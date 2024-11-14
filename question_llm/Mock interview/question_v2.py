import os
from dotenv import load_dotenv
from typing import List, Dict
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import openai
import time
from google.cloud import speech  # Google STT 사용을 위한 라이브러리
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import SystemMessage
from audio import real_time_transcription

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
    resume_text: Optional[str] = None
    project_text: Optional[str] = None
    tech_keywords: Optional[str] = None
    question: Optional[str] = None
    answer_text: Optional[str] = None
    evaluation: Optional[str] = None
    reference_docs: Optional[str] = None
    is_stop: Optional[bool] = False
    question_count: Optional[int] = 0
    max_questions: Optional[int] = 5


# FAISS 벡터 데이터베이스 초기화 및 retriever 할당
# faiss_index_path = "C:/dev/SKN03-Final_Project/faiss_db/python01.faiss"  # 인덱스 파일 경로
# faiss_metadata_path = "C:/dev/SKN03-Final_Project/faiss_db/python01.pkl"  # 메타데이터 파일 경로

# FAISS 데이터베이스 로드

vector_db = FAISS.load_local(
    folder_path="faiss_db",
    index_name="python01",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)

retriever = vector_db.as_retriever()


example_tech_terms = ["python", "파이썬", "javascript", "자바스크립트", "java", "자바", "react", "리액트", "css", "씨에스에스",
                        "html", "에이치티엠엘", "node.js", "노드제이에스" ]

# 이력서 텍스트에서 사전 정의된 기술 용어와 일치하는 키워드를 추출하는 함수
def extract_keywords_from_resume(resume_text, tech_terms):
    resume_text = resume_text.lower()  # 대소문자 구분을 없앰
    matched_keywords = [term for term in tech_terms if term.lower() in resume_text]
    return matched_keywords

# 키워드 추출 노드
def extract_keywords(state: State) -> State:
    resume_text = state["resume_text"]
    tech_keywords = extract_keywords_from_resume(resume_text, example_tech_terms)
    
    return {
        **state,
        "tech_keywords": ", ".join(tech_keywords)  # 키워드를 쉼표로 구분하여 저장
    }

# 질문 키워드 추출 노드(open ai를 바탕으로 추출)
def extract_keywords(state: State) -> State:
    resume_text = state["resume_text"]
    # 필요시 추가 = project_text = state["project_text"]   \n프로젝트 설명: {project_text}
    prompt=f"이력서와 프로젝트 설명에서 주요 기술 키워드를 추출해 주세요:\n이력서: {resume_text}",

    response = chat.invoke([
        SystemMessage(content=str(prompt))
    ])
    
    return {
        **state,
        "tech_keywords": response.content.strip(),
    }

# 질문 생성 노드
fix_question = ["자기소개를 부탁드립니다", "자신의 성격의 장단점을 말씀해주세요", "갈등이나 문제를 해결한 경험이 있다면 이야기 해주세요"]

def generate_question(state: State) -> State:
    tech_keywords = state["tech_keywords"]
    # project_context = state["project_text"]
    prev_answer = state.get("answer_text", None)

    # retriever를 사용하여 기술 관련 자료 검색
    search_results = retriever.get_relevant_documents(tech_keywords)
    
    # 검색된 문서 내용과 참조 정보
    # source는 페이지 링크일 듯
    retrieved_content = search_results[0].page_content if search_results else "관련 문서를 찾을 수 없습니다."
    reference_docs = search_results[0].metadata.get("source", "출처를 알 수 없음") if search_results else "출처를 알 수 없음"
    
    # 질문 프롬프트 작성   필요시 추가 = 프로젝트 내용: {project_context}\n 프로젝트 내용: {project_context}\n

    if prev_answer is None:
        query_prompt = (
            f"당신은 현재 지원자를 평가하는 면접관입니다. "
            f"지원자의 자기소개서와 기술 스택을 기반으로 질문을 하나만 생성하세요. "
            f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
            f"기술 스택: {tech_keywords}\n"
            f"하나의 질문만 반환해주시기 바랍니다."
        )
    else:
        query_prompt = (
            f"당신은 현재 지원자를 평가하는 면접관입니다. "
            f"지원자의 자기소개서와 기술 스택을 기반으로 질문을 하나만 생성하세요. "
            f"다음 공식 문서의 키워드를 참조하여 후속 면접 질문을 생성해 주세요 다만 이전 질문과는 다른 키워드를 선택해주세요. :\n{retrieved_content}\n"
            f"이전 답변: {prev_answer}\n기술 스택: {tech_keywords}\n"
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
        "question_count": state["question_count"] + 1
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
def evaluate_answer(state: State) -> State:
    answer_text = state["answer_text"]
    evaluation_prompt = f"Evaluate the following answer:\n{answer_text}"
    
    response = chat.invoke([
        SystemMessage(content=str(evaluation_prompt))
    ])
    
    return {
        **state,
        "evaluation": response.content.strip()
    }

# 종료 조건 확인 함수
def check_stop_condition(state: State) -> str:
    if state["question_count"] >= state["max_questions"]:
        return "stop_interview"
    else:
        return "continue_interview"

# 그래프 생성
mock_interview_graph = StateGraph(State)

# 노드 추가
mock_interview_graph.add_node("extract_keywords", extract_keywords)
mock_interview_graph.add_node("generate_question", generate_question)
mock_interview_graph.add_node("record_and_transcribe", record_and_transcribe)
mock_interview_graph.add_node("evaluate_answer", evaluate_answer)

# 엣지 추가
mock_interview_graph.add_edge(START, "extract_keywords")
mock_interview_graph.add_edge("extract_keywords", "generate_question")
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

# 그래프 실행 예시
initial_state = {
    "resume_text": "python",
    # "project_text": "사용자의 프로젝트 정보",
    "is_stop": False,
    "question_count": 0,
    "max_questions": 5
}

for chunk in compiled_graph.stream(initial_state):
    print(chunk)
