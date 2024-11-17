import os
from dotenv import load_dotenv
from typing import List, Dict
import pandas as pd
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import openai
import time
from google.cloud import speech  # Google STT 사용을 위한 라이브러리
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import SystemMessage
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness, context_recall, context_precision
from datasets import Dataset
import ast
from audio import real_time_transcription
from video import start_video_recording, stop_video_recording
import pdfplumber
import random


load_dotenv()

# ChatOpenAI 클라이언트 생성 함수
def get_client():
    return ChatOpenAI(
        model="gpt-4",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

# ChatOpenAI 인스턴스 생성
chat = get_client()

# State 정의
class State(TypedDict):
    # resume_text: Optional[str] = None
    # project_text: Optional[str] = None
    tech_keywords: Optional[str] = None
    question: Optional[str] = None
    answer_text: Optional[str] = None
    evaluation: Optional[str] = None
    reference_docs: Optional[str] = None
    is_stop: Optional[bool] = False
    question_count: Optional[int] = 0
    max_questions: Optional[int] = 5


# FAISS 데이터베이스 로드

vector_db = FAISS.load_local(
    folder_path="faiss_db",
    index_name="python_csv01",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)

retriever = vector_db.as_retriever()


example_tech_terms = ["python", "파이썬", "javascript", "자바스크립트", "java", "자바", "react", "리액트", "css", "씨에스에스",
                        "html", "에이치티엠엘", "node.js", "노드제이에스", "binary file", "argument", "context", "lambda", "parameter" ]

# RAGAS 평가를 위한 데이터 프레임 정의
qa_data = pd.DataFrame(columns=["Question", "Answer", "Reference_Docs", "Evaluation"])


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

# 질문 생성 노드
fix_question = ["자기소개를 부탁드립니다", "자신의 성격의 장단점을 말씀해주세요", "갈등이나 문제를 해결한 경험이 있다면 이야기 해주세요"]

def generate_question(state: State) -> State:
    tech_keywords = state["tech_keywords"]
    prev_answer = state.get("answer_text", None)
    retrieval_index = state.get("retrieval_index", 0)  # 기본적으로 0에서 시작

        # 추출된 기술 키워드를 리스트로 분리
    keywords_list = tech_keywords.split(", ")
    
    # 랜덤으로 키워드를 선택 (각 질문마다 새로운 키워드로 변경)
    selected_keyword = random.choice(keywords_list)

    # retriever를 사용하여 기술 관련 자료 검색
    search_results = retriever.get_relevant_documents(tech_keywords)

    # 검색된 문서 내용과 참조 정보 (순차적으로 선택)
    if search_results:
        retrieved_content = search_results[retrieval_index % len(search_results)].page_content
        reference_docs = search_results[retrieval_index % len(search_results)].metadata.get("source", "출처를 알 수 없음")
    else:
        retrieved_content = "관련 문서를 찾을 수 없습니다."
        reference_docs = "출처를 알 수 없음"

    # 질문 프롬프트 작성 다음 공식 문서:\n{retrieved_content}\n
    if prev_answer is None:
        query_prompt = (
            f"당신은 현재 지원자를 평가하는 면접관입니다. "
            f"지원자의 기술 스택을 기반으로 질문을 하나만 생성하세요. "
            f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
            f"기술 스택: {selected_keyword}\n"
            f"하나의 질문만 반환해주시기 바랍니다."
        )
    else:
        query_prompt = (
            f"당신은 현재 지원자를 평가하는 면접관입니다. "
            f"지원자의 기술 스택을 기반으로 질문을 하나만 생성하세요. "
            f"이전 질문과는 다른 관점에서 질문을 생성해 주세요.\n"
            f"이전 답변: {prev_answer}\n과 기술 스택: {selected_keyword}\n,다음 공식 문서:\n{retrieved_content}\n를 참조하여 후속 면접질문을 생성해주세요"
            f"하나의 질문만 반환해주시기 바랍니다."
        )

    # ChatGPT를 사용하여 질문 생성
    response = chat.invoke([
        SystemMessage(content=str(query_prompt))
    ])
    
    return {
        **state,
        "question": response.content.strip(),
        "reference_docs": reference_docs,
        "question_count": state["question_count"] + 1,
        "retrieval_index": retrieval_index + 1  # 다음 질문 시 다음 문서로 넘어가도록 인덱스 증가
    }
# 답변 녹음 및 변환 노드
def record_and_transcribe(state: State) -> State:
    # Google STT를 통해 텍스트화 된 답변을 변수로 저장
    
    answer_text = real_time_transcription()
    return {
        **state,
        "answer_text": answer_text
    }

# 답변 평가 노드

# RAGAS 평가 로직을 integrate하여 answer 평가하는 노드
def evaluate_answer(state: State) -> State:
    answer_text = state["answer_text"]
    reference_docs = state["reference_docs"]

    # RAGAS 평가용 데이터셋 생성
    df = pd.DataFrame([{
        "user_input": answer_text,
        "reference": reference_docs,
        "contexts": f"['{reference_docs}']",
        "response": answer_text
    }])
    test_dataset = Dataset.from_pandas(df)
    test_dataset = test_dataset.map(lambda example: {"contexts": ast.literal_eval(example["contexts"])})

    # RAGAS 평가 적용
    result = evaluate(
        dataset=test_dataset,
        metrics=[context_precision, faithfulness, answer_relevancy, context_recall],
    )

    # 결과를 DataFrame으로 변환
    result_df = result.to_pandas()
    
    # 추가 데이터프레임 생성 (질문, 답변, 참조 문서 추가)
    additional_data = pd.DataFrame({
        "Question": [state["question"]],
        "Answer": [answer_text],
        "Reference_Docs": [reference_docs]
    })

    # 결과와 추가 정보를 합쳐 최종 데이터프레임 생성
    final_df = pd.concat([additional_data, result_df], axis=1)
    
    # 결과 CSV 저장
    final_df.to_csv("mock_interview_results.csv", mode='a', index=False, header=not pd.io.common.file_exists("mock_interview_results.csv"))
    
    print("Results saved to 'mock_interview_results.csv'")
    
    return {**state, "evaluation": result_df.iloc[0].to_dict()}

# 종료 조건 확인 함수
def check_stop_condition(state: State) -> str:
    if state["question_count"] >= state["max_questions"]:
        return "stop_interview"
    else:
        return "continue_interview"

# 그래프 생성
mock_interview_graph = StateGraph(State)

# 노드 추가
mock_interview_graph.add_node("generate_question", generate_question)
mock_interview_graph.add_node("record_and_transcribe", record_and_transcribe)
mock_interview_graph.add_node("evaluate_answer", evaluate_answer)

# 엣지 추가
mock_interview_graph.add_edge(START, "generate_question")
mock_interview_graph.add_edge("generate_question", "record_and_transcribe")
mock_interview_graph.add_edge("record_and_transcribe", "evaluate_answer")

# 조건부 엣지 추가 (종료 조건에 따라 인터뷰를 반복하거나 종료)
mock_interview_graph.add_conditional_edges(
    "evaluate_answer",
    check_stop_condition,
    {
        "continue_interview": "generate_question",
        "stop_interview": END
    }
)

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
initial_state = {
    # "resume_text": resume_text,
    # "python, binary file, argument, context, lambda, parameter",
    # "project_text": "사용자의 프로젝트 정보",
    "tech_keywords": "python, binary file, argument, context, lambda, parameter",
    "is_stop": False,
    "question_count": 0,
    "max_questions": 5
}

# 모의면접 실행 함수
def run_mock_interview(compiled_graph, initial_state):
    # 녹화 시작
    start_video_recording()

    # LangGraph 실행
    try:
        for chunk in compiled_graph.stream(initial_state):
            print("Current chunk state:", chunk)
    finally:
        # 녹화 종료
        stop_video_recording()


run_mock_interview(compiled_graph, initial_state)

# for chunk in compiled_graph.stream(initial_state):
#     print("Current chunk state:", chunk)

# 최종 질의응답 데이터 출력
print("질의응답 데이터:\n", qa_data)

# qa_data.to_csv("mock_interview_results.csv", index=False)
# print("Results saved to 'mock_interview_results.csv'")