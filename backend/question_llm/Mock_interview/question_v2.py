import os
from typing import List, Dict
import pandas as pd
import numpy as np
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import openai
import time
from google.cloud import speech  
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import SystemMessage
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness, context_recall, context_precision
from datasets import Dataset
import ast
from audio import real_time_transcription
from video import start_video_recording, stop_video_recording
from prompt import evaluation_prompt, question_prompt, model_answer, generate_final_evaluation_prompt
from typing_extensions import Annotated
import pdfplumber
import random
import json
from langchain_core.runnables import RunnableConfig
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from bert_score import score as bert_score
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from db_utils import create_new_interview, save_question_to_db , save_report_to_db, update_question_in_db, initialize_questions
from datetime import datetime
from util.get_parameter import get_parameter



config = RunnableConfig(recursion_limit=70, configurable={"thread_id": "THREAD_ID"}) 


openai_api_key = get_parameter('/TEST/CICD/STREAMLIT/OPENAI_API_KEY')
# openai_api_key = os.getenv("OPENAI_API_KEY")

# "gpt-4" "gpt-4o-mini"
# ChatOpenAI 클라이언트 생성 함수
def get_client():
    return ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        openai_api_key=openai_api_key
    ) 


# ChatOpenAI 인스턴스 생성
chat = get_client()

# State 정의
class State(TypedDict):
    # resume_text: Optional[str] = None
    # project_text: Optional[str] = None
    tech_keywords: Optional[str]
    ideal_answer: Optional[str] = None # 참고자료
    model_answer: Optional[str] = None # 모범답안
    question: Optional[str] = None
    answer_text: Optional[str] = None
    evaluation: Optional[str] = None
    reference_docs: Optional[str] = None
    feedback : Optional[str] = None 
    is_stop: Optional[bool] = False
    question_count: Optional[int] = 0
    max_questions: Optional[int] = 5
    selected_keyword: Optional[str] = None
    evaluation_results: Optional[List[Dict]]
    cosine_scores: Optional[List[float]]
    interview_id: Optional[int] = None  # 추가
    question_id: Optional[int] = None   # 추가
    final_feedback: Optional[Dict] = None  # 추가
# FAISS 데이터베이스 로드

vector_db_high = FAISS.load_local(
    folder_path="C:/dev/SKN03-FINAL-5Team-git/question_llm/high_db/",
    index_name="python_high_chunk700",
    embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key),
    allow_dangerous_deserialization=True,
)


vector_db_low = FAISS.load_local(
    folder_path="C:/dev/SKN03-FINAL-5Team-git/question_llm/low_db",
    index_name="python_low_chunk700",
    embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key),
    allow_dangerous_deserialization=True,
)

# SBERT 모델 초기화
sbert_model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')  # 한국어 지원 모델 사용

example_tech_terms = ["python", "파이썬", "javascript", "자바스크립트", "java", "자바", "react", "리액트", "css", "씨에스에스",
                        "html", "에이치티엠엘", "node.js", "노드제이에스", "binary file", "argument", "context", "lambda", "parameter" ]


# cross_encoder_reranker 검색기
def cross_encoder_reranker(query, db_level="low", top_k=3):
    """
    Cross Encoder Reranker를 ContextualCompressionRetriever와 통합하여 문서를 검색하고 압축.
    Args:
        query (str): 검색 쿼리
        db_level (str): 사용할 DB 레벨 ("high" 또는 "low")
        top_k (int): 최종적으로 반환할 문서 개수
        score_threshold (float): 유사도 점수 임계값
    Returns:
        List[Document]: 적합도가 높은 문서 리스트
    """
    # DB 선택
    vector_db = vector_db_high if db_level == "high" else vector_db_low

    # Retriever 설정
    retriever = vector_db.as_retriever(
    )

    # MultiQueryRetriever 생성
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    multi_query_retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)

    # Cross Encoder Reranker 초기화
    model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
    reranker = CrossEncoderReranker(model=model, top_n=top_k)

    # ContextualCompressionRetriever 생성
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=multi_query_retriever
    )

    # 쿼리에 대한 문서 검색 및 압축
    compressed_docs = compression_retriever.invoke(query)

    return compressed_docs



pdf_path = 'c:/dev/SKN03-Final_Project/이력서_20240508.pdf'

def resume_loader(pdf_path):
    resume_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            resume_text += page.extract_text() + "\n"  # 각 페이지의 텍스트를 추가
    return resume_text

# 키워드 추출 노드(이력서 키워드와 에시 키워드간 맞는 것만 추출)
def extract_keywords(state: State) -> State:
    resume_text = state["resume_text"]
    tech_keywords = ", ".join(term for term in example_tech_terms if term.lower() in resume_text.lower())
    return {**state, "tech_keywords": tech_keywords}

# 질문 키워드 추출 노드(open ai를 바탕으로 추출)
def extract_keywords_from_resume(resume_text: str) -> str:
    # 이력서 텍스트에서 키워드를 추출하는 프롬프트
    prompt = f"이력서에서 주요 기술 키워드를 추출해 주세요:\n이력서: {resume_text}"

    # OpenAI API 호출 (키워드를 한 번만 추출)
    response = chat.invoke([
        SystemMessage(content=prompt)
    ])
    
    return response.content.strip()

#==========================질문생성===============================

# 질문 생성 노드

def generate_question(state: State, interview_id: int) -> State:
    print(state)

    tech_keywords = state["tech_keywords"]
    
    question_count = state["question_count"]

    # 기본 변수 초기화
    selected_level = "low"
    search_results = []

    # 기술 키워드 리스트 생성
    keywords_list = tech_keywords.split(", ")

    # 랜덤으로 키워드 선택
    selected_keyword = random.choice(keywords_list)
    # selected_keyword = keywords_list
    state["selected_keyword"] = selected_keyword

    if question_count > 3: 
        # 1. 상위 DB 우선 검색 ,3개 넘는 질문을 했을 때
        search_results = cross_encoder_reranker(
            query=selected_keyword,
            db_level="high",  # 상위 DB
            top_k=5
        )

        # 2. 상위 DB 검색 실패 시 하위 DB로 fallback
        if search_results:
            selected_level = "high"
        else:
            search_results = cross_encoder_reranker(
                query=selected_keyword,
                db_level="low",  # 하위 DB
                top_k=5
            )
            selected_level = "low"
    else:
        # 3. 질문이 3개 이하일 경우 하위 DB만 검색
        search_results = cross_encoder_reranker(
            query=selected_keyword,
            db_level="low",  # 하위 DB
            top_k=5
        )
        selected_level = "low"

    # 검색된 문서 처리
    if search_results:
        retrieved_content = search_results[0].page_content
        reference_docs = search_results[0].metadata.get("source", "출처를 알 수 없음")
    else:
        # 검색 결과가 없을 경우 기본 메시지 설정
        retrieved_content = "관련 문서를 찾을 수 없습니다."
        reference_docs = "출처를 알 수 없음"

    # 질문 프롬프트 작성
    query_prompt = question_prompt() + (
        f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
        f"기술 스택: {selected_keyword}\n"
        f"하나의 질문만 반환해주시기 바랍니다."
    )

    # ChatGPT를 사용하여 질문 생성
    response = chat.invoke([SystemMessage(content=query_prompt)])
    question_text = response.content.strip()

    # 데이터베이스에 저장
    question_id = save_question_to_db(
        interview_id=interview_id,
        job_question=question_text,
        job_answer="N/A",
        job_solution="N/A",
        job_score=0,
        question_vector_path="default/path/vector.json"
    )
    if question_id is None:
        raise ValueError("Failed to obtain question_id from database.")

    print(f"Generated question_id: {question_id}")

    # 상태 변경 사항 반환
    return {
        "selected_keyword": selected_keyword,
        "question": question_text,
        "reference_docs": reference_docs,
        "ideal_answer": retrieved_content.strip(),
        "question_count": state["question_count"] + 1,
        "question_id": question_id,
    }

#=====================모범답안 생성===============================
def generate_model_answer(state: State) -> Dict:
    question = state["question"]
    retrieved_content = state["ideal_answer"]
    prompt = model_answer(question, retrieved_content)
    
    response = chat.invoke([SystemMessage(content=prompt)])
    
    # 상태 전체를 반환하지 않고, 변경된 부분만 반환
    return {"model_answer": response.content.strip()}


#====================답변녹음=====================================

# 답변 녹음 및 변환 노드
def record_and_transcribe(state: State, interview_id: int = None, question_id: int = None) -> Dict:
    if interview_id is None:
        interview_id = state.get("interview_id")
    if question_id is None:
        question_id = state.get("question_id")

    if interview_id is None or question_id is None:
        raise ValueError("interview_id 또는 question_id가 상태에 없습니다.")
    
    print(f"Debug: Entering record_and_transcribe with state: {state}")
    print(f"Debug: interview_id={interview_id}, question_id={question_id}")

    # 답변 녹음 및 변환
    answer_text = real_time_transcription()
    print(f"Debug: Transcribed answer_text={answer_text}")

    # 데이터베이스 업데이트
    update_question_in_db(
        question_id=question_id,
        interview_id=interview_id,
        job_question=state.get("question", "N/A"),
        job_answer=answer_text,
        job_solution=state.get("model_answer", "N/A"),
        job_score=0
    )

    # 상태 변경 사항 반환
    return {
        "answer_text": answer_text
    }

#=============================피드백====================================
# 피드백 생성 함수
def generate_feedback(state: State, interview_id: int = None, question_id: int = None) -> Dict:
    # 인터뷰 ID와 질문 ID 가져오기
    if interview_id is None:
        interview_id = state.get("interview_id")
    if question_id is None:
        question_id = state.get("question_id")
    if interview_id is None or question_id is None:
        raise ValueError("interview_id 또는 question_id가 상태에 없습니다.")
    
    answer = state["answer_text"]
    ideal_answer = state["ideal_answer"]
    prompt = evaluation_prompt(answer, ideal_answer)
    
    response = chat.invoke([SystemMessage(content=prompt)])
    feedback = response.content.strip()
    
    # 데이터베이스 업데이트
    update_question_in_db(
        question_id=question_id,
        interview_id=interview_id,
        job_question=state["question"],
        job_answer=answer,
        job_solution=state["model_answer"],
        job_score=0
    )
    
    # 변경된 부분만 반환
    return {"feedback": feedback}

#========================================================================

# 평가지표용 번역 함수
def translate_text(text: str, target_language: str = "en") -> str:
    prompt = f"Translate the following text to {target_language}: {text}"
    response = chat.invoke([SystemMessage(content=prompt)])
    return response.content.strip()


# RAGAS 평가 로직을 integrate하여 answer 평가하는 노드
#============================= 면접자의 답변 평가 노드==============================

def evaluate_answer(state: State, interview_id: int = None, question_id: int = None) -> Dict:
    # 인터뷰 ID와 질문 ID 가져오기
    if interview_id is None:
        interview_id = state.get("interview_id")
    if question_id is None:
        question_id = state.get("question_id")
    if interview_id is None or question_id is None:
        raise ValueError("interview_id 또는 question_id가 상태에 없습니다.")
    
    answer_text = state["answer_text"]
    model_answer = state["model_answer"]
    feedback = state["feedback"]
    
    # answer_text가 없을 경우 처리
    if not answer_text:
        print("면접자가 답변을 제공하지 않았습니다. 평가를 건너뜁니다.")
        # 평가 결과에 '무응답'으로 표시하거나 적절한 조치를 취합니다.
        evaluation_data = {
            "Question": state["question"],
            "Answer": "무응답",
            "Ideal_Answer": model_answer,
            "Feedback": feedback,
            "SBERT_Cosine_Similarity": 0.0,
            "job_score": 0.0,
        }
        
        # 기존의 evaluation_results에 추가
        evaluation_results = state.get("evaluation_results", [])
        evaluation_results.append(evaluation_data)
        
        # 상태 업데이트
        return {
            "evaluation_results": evaluation_results,
        }
    
    # model_answer가 없는 경우 처리
    if not model_answer:
        print("Error: model_answer가 없습니다.")
        raise ValueError("model_answer가 없습니다.")
    
    # 정상적인 경우 평가 수행
    answer_embedding = sbert_model.encode(answer_text)
    model_answer_embedding = sbert_model.encode(model_answer)
    cosine_sim = cosine_similarity([answer_embedding], [model_answer_embedding])[0][0]
    job_score = round(cosine_sim * 100, 2)
    
    # 코사인 유사도 저장
    cosine_scores = state.get("cosine_scores", [])
    cosine_scores.append(cosine_sim)
    
    # 데이터베이스 업데이트
    update_question_in_db(
        question_id=state["question_id"],
        interview_id=state["interview_id"],
        job_question=state["question"],
        job_answer=answer_text,
        job_solution=model_answer,
        job_score=job_score,
    )
    
    # 평가 결과 저장
    evaluation_data = {
        "Question": state["question"],
        "Answer": answer_text,
        "Ideal_Answer": model_answer,
        "Feedback": feedback,
        "SBERT_Cosine_Similarity": cosine_sim,
        "job_score": job_score,
    }
    evaluation_results = state.get("evaluation_results", [])
    evaluation_results.append(evaluation_data)
    
    # 상태 업데이트
    return {
        "cosine_scores": cosine_scores,
        "evaluation_results": evaluation_results,
        "evaluation": evaluation_data,  # update_evaluation_results에서 참조
    }



#=========================질문 평가=============================

def evaluate_question(state: State) -> State:
    # 모델이 생성한 질문과 참조 청크를 사용하여 질문의 적절성 평가
    generated_question = state["question"]
    reference_context = state["ideal_answer"]  # 질문 생성 시 참조한 청크를 사용

    if not generated_question or not reference_context:
        print("Error: Missing generated_question or reference_context for evaluation.")
        return {**state, "question_evaluation": {"question_relevancy": 0.0, "faithfulness": 0.0, "context_precision": 0.0, "context_recall": 0.0}}
    
    translated_reference_context = translate_text(reference_context, target_language="ko")

    # 평가용 데이터셋 생성
    df = pd.DataFrame([{
        "question": translated_reference_context,  # 참조 청크 (질문의 컨텍스트)
        "answer": generated_question,   # 모델이 생성한 질문
        "ground_truth": translated_reference_context,  # 평가에 필요한 정답
        "contexts": json.dumps([translated_reference_context])  # 평가에 사용할 컨텍스트 (참조 청크를 컨텍스트로 사용)
    }])
    
    # 데이터셋 변환
    test_dataset = Dataset.from_pandas(df)
    test_dataset = test_dataset.map(lambda example: {"contexts": ast.literal_eval(example["contexts"])})
    
    # RAGAS 평가 적용
    result = evaluate(
        dataset=test_dataset,
        metrics=[answer_relevancy, faithfulness, context_precision, context_recall],
    )
    
    # 결과를 데이터프레임으로 변환
    result_df = result.to_pandas()
    
    # 평가 결과에 모델이 생성한 질문을 추가
    additional_data = pd.DataFrame({
        "Generated_Question": [generated_question],
        "Reference_Context": [reference_context]
    })
    
    # 최종 결과 데이터프레임 생성
    final_df = pd.concat([additional_data, result_df], axis=1)
    
    # 평가 결과 저장

    # 새로운 상태 반환
    return {**state, "question_evaluation": result_df.iloc[0].to_dict()}

#=======================평가데이터 누적=========================

def update_evaluation_results(state: State) -> State:
    if "evaluation" not in state or not state["evaluation"]:
        state["evaluation"] = {}  # 기본값으로 초기화

    # 새 데이터를 준비
    evaluation = state["evaluation"]
    
    # 새 데이터를 준비
    new_data = {
        "Question": evaluation.get("Question", "질문 없음"),
        "Answer": evaluation.get("Answer", "답변 없음"),
        "Ideal_Answer": evaluation.get("Ideal_Answer", ""),
        "Feedback": evaluation.get("Feedback", ""),
        "SBERT_Cosine_Similarity": evaluation.get("SBERT_Cosine_Similarity", 0.0),
        "job_score": evaluation.get("job_score", 0.0),
        "Question_Relevancy": evaluation.get("question_relevancy", 0.0),
        "Faithfulness": evaluation.get("faithfulness", 0.0),
        "Context_Precision": evaluation.get("context_precision", 0.0),
        "Context_Recall": evaluation.get("context_recall", 0.0)
    }

    # 기존 데이터 가져오기
    if "evaluation_results" not in state or not state["evaluation_results"]:
        state["evaluation_results"] = []

    # 새 데이터를 추가
    state["evaluation_results"].append(new_data)
    return state


#=============float32를 Python의 기본 float 타입으로 변환========
def convert_to_serializable(obj):
    if isinstance(obj, np.float32):
        return float(obj)  # Python float으로 변환
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


#==========================면접최종평가=======================
def generate_final_evaluation(state: State, interview_id: int) -> State:
    print(f"Before update, state['final_feedback']: {state.get('final_feedback')}")
    evaluation_results = state.get("evaluation_results", [])
    evaluation_df = pd.DataFrame(evaluation_results)

    # GPT를 사용하여 최종 평가 생성
    prompt = generate_final_evaluation_prompt(evaluation_df)
    try:
        response = chat.invoke([SystemMessage(content=prompt)])
        final_feedback = json.loads(
            json.dumps(response.content.strip(), default=convert_to_serializable)
        )
    except Exception as e:
        print(f"Error generating final_feedback: {e}")
        # 빈 피드백 생성
        final_feedback = {
            "strength": "",
            "weakness": "",
            "ai_summary": "",
            "detail_feedback": "",
            "attitude": ""
        }

        # 상태의 final_feedback이 딕셔너리가 아닐 경우 초기화
    if not isinstance(state.get("final_feedback"), dict):
        state["final_feedback"] = {}

    state["final_feedback"] = final_feedback

    # 평균 점수 계산
    cosine_scores = state.get("cosine_scores", [])
    if cosine_scores:
        # NumPy 배열 또는 float32로 인해 문제가 발생하지 않도록 변환
        average_score = sum(map(float, cosine_scores)) / len(cosine_scores)
    else:
        average_score = 0.0
    report_score = round(average_score * 100, 2)

    # 상태에 총점 저장
    state["final_feedback"]["report_score"] = report_score

    # 최종 보고서 저장
    save_report_to_db(
        interview_id=state["interview_id"],
        strength=state["final_feedback"].get("strength", ""),
        weakness=state["final_feedback"].get("weakness", ""),
        ai_summary=state["final_feedback"].get("ai_summary", ""),
        detail_feedback=state["final_feedback"].get("detail_feedback", ""),
        attitude=state["final_feedback"].get("attitude", ""),
        report_score=report_score,
    )
    print(f"After update, state['final_feedback']: {state.get('final_feedback')}")  # 디버깅 추가
    return state


#==============================종료조건================================
    
# 종료 조건 확인 함수
def check_stop_condition(state: State) -> str:
    if state["question_count"] >= state["max_questions"]:
        return "stop_interview"
    else:
        return "continue_interview"

#========================랭그래프 노드 엣지 =============================
# 그래프 생성
mock_interview_graph = StateGraph(State)

# 노드 추가 (raw_output=True 설정)
# 노드 추가 (raw_output=True 제거)
mock_interview_graph.add_node("generate_question", lambda state: generate_question(state, state.get("interview_id")))
mock_interview_graph.add_node("generate_model_answer", generate_model_answer)
mock_interview_graph.add_node("record_and_transcribe", lambda state: record_and_transcribe(state, state.get("interview_id"), state.get("question_id")))
mock_interview_graph.add_node("generate_feedback", lambda state: generate_feedback(state, state.get("interview_id"), state.get("question_id")))
mock_interview_graph.add_node("evaluate_question", evaluate_question)
mock_interview_graph.add_node("evaluate_answer", lambda state: evaluate_answer(state, state.get("interview_id"), state.get("question_id")))
mock_interview_graph.add_node("generate_final_evaluation", lambda state: generate_final_evaluation(state, state.get("interview_id")))
mock_interview_graph.add_node("update_evaluation_results", update_evaluation_results)




# 엣지 추가
mock_interview_graph.add_edge(START, "generate_question")
mock_interview_graph.add_edge("generate_question", "generate_model_answer")
mock_interview_graph.add_edge("generate_model_answer", "record_and_transcribe")
mock_interview_graph.add_edge("record_and_transcribe", "generate_feedback")
mock_interview_graph.add_edge("generate_feedback", "evaluate_question")
mock_interview_graph.add_edge("evaluate_question", "evaluate_answer")
mock_interview_graph.add_edge("evaluate_answer", "update_evaluation_results")

# 조건부 엣지 추가 (종료 조건에 따라 인터뷰를 반복하거나 종료)
mock_interview_graph.add_conditional_edges(
    "update_evaluation_results",
    check_stop_condition,
    {
        "continue_interview": "generate_question",
        "stop_interview": "generate_final_evaluation"
    }
)
mock_interview_graph.add_edge("generate_final_evaluation", END)

# 그래프 컴파일 및 실행
compiled_graph = mock_interview_graph.compile()

#=============================================================================
# 이력서 텍스트 로딩 및 키워드 추출
# pdf_path = 'c:/dev/SKN03-Final_Project/이력서_20240508.pdf'
# resume_text = resume_loader(pdf_path)
# extracted_keywords = extract_keywords_from_resume(resume_text)
#==========================================================================


# 그래프 실행 예시
# resume_text = 이력서 정보
# project_text = 프로젝트 정보

    # "resume_text": resume_text,
    # "python, binary file, argument, context, lambda, parameter",
    # "project_text": "사용자의 프로젝트 정보",

USER_ID = 1  # 사용자 ID
USER_JOB = "백엔드 개발자"  # 지원 직무
JOB_TALENT = "Python, Django, IDLE"  # 기술 능력
RESUME_PATH = "c:/path/to/resume.pdf"  # 이력서 경로 (없을 경우 None)

interview_id = create_new_interview(user_id=USER_ID, user_job=USER_JOB, job_talent=JOB_TALENT, resume_path=RESUME_PATH, interview_time=datetime.now() )

if not interview_id:
    print("Error: Failed to create new interview. Exiting...")
    exit()

print(f"Interview created with ID: {interview_id}")

# 초기 상태 설정
initial_state = {
    "tech_keywords": JOB_TALENT,  # 기술 키워드
    "is_stop": False,
    "question_count": 0,
    "max_questions": 5,
    "final_feedback": {},
    "interview_id": interview_id,
    "user_id": USER_ID,          # 현재 사용자 ID
    "user_job": USER_JOB,        # 사용자가 지원하는 직무
    "job_talent": JOB_TALENT,    # 직무 관련 기술 또는 역량
    "interview_time": datetime.now(),    # 면접 시간
    "interview_created": datetime.now(), # 면접 생성 시간
    "resume_path": RESUME_PATH,  # 이력서 경로
}

#=====================================면접실행==============================================
# 모의면접 실행 함수
# initialize_questions 함수와 question_ids 리스트 제거
# question_ids = initialize_questions(interview_id, max_questions=5)
def run_mock_interview(compiled_graph, initial_state, interview_id: int):
    start_video_recording()
    current_state = initial_state.copy()

    # 재귀 한도 설정을 포함한 config 정의
    config = RunnableConfig(recursion_limit=1000)

    try:
        for index, chunk in enumerate(compiled_graph.stream(current_state, config=config)):
            # 노드 출력 추출
            node_name, node_output = next(iter(chunk.items()))
            current_state.update(node_output)

            # 디버깅 정보 출력
            print(f"Step {index} 후의 상태: {current_state}")
            print(f"Step {index}에서의 interview_id: {current_state.get('interview_id')}")
            print(f"Step {index}에서의 question_id: {current_state.get('question_id')}")

            # 추가 로직
            if node_name == "record_and_transcribe":
                question_id = current_state.get("question_id")
                if question_id is None:
                    raise ValueError("녹음 및 변환 단계에서 question_id가 없습니다.")

        print("모의 면접이 성공적으로 완료되었습니다.")

    except Exception as e:
        print(f"모의 면접 중 오류 발생: {e}")
    finally:
        stop_video_recording()



run_mock_interview(compiled_graph, initial_state, interview_id)


