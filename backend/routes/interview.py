from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from .crud import get_interviews_by_user_id
from utils import upload_to_s3
from datetime import datetime
from models import Interview

from pydantic import BaseModel
from typing import Optional
from .prompt import evaluation_prompt, question_prompt, model_answer, generate_final_evaluation_prompt
from langchain_openai import ChatOpenAI
import os
import random
from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain.schema import SystemMessage
from .db_utils import save_question_to_db , save_report_to_db, update_question_in_db
from utils.get_parameter import get_parameter





load_dotenv()




router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BUCKET_NAME = "sk-unailit"

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    user_job: str = Form(...),
    job_talent: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    사용자가 업로드한 이력서를 S3에 저장하고, 데이터베이스에 해당 경로를 기록하는 API
    """
    try:
        # S3에 파일 업로드
        s3_path = upload_to_s3(file.file, BUCKET_NAME, f"resume/{file.filename}")

        # 데이터베이스에 사용자 정보 및 경로 저장
        # interview = save_to_database(db, s3_path, user_id, user_job,job_talent)
        interview = Interview(
            user_id=user_id,
            user_job=user_job,
            job_talent=job_talent,

            resume_path=s3_path,
            interview_time = datetime.utcnow(),  # 현재 시간 설정
            interview_created = datetime.utcnow()
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)

        return {
            "message": "이력서가 성공적으로 업로드되었습니다.",
            "data": {
                "interview_id": interview.interview_id,
                "resume_path": interview.resume_path,
                "user_id": interview.user_id,
                "user_job": interview.user_job,
                "interview_time": interview.interview_time,
                "interview_created": interview.interview_created,
                "job_talent" : interview.job_talent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
    
@router.get("/interview/{user_id}")
async def read_interviews(user_id: int, db: Session = Depends(get_db)):
    interviews = get_interviews_by_user_id(db=db, user_id=user_id)
    if not interviews:
        raise HTTPException(status_code=404, detail="No interviews found for this user")
    
    return [{"interview_id": interview.interview_id, "interview_created": interview.interview_created} for interview in interviews]




# State 데이터 구조 정의
class State(BaseModel):
    tech_keywords: str
    question_count: int = 0
    max_questions: int = 5
    selected_keyword: Optional[str] = None
    question: Optional[str] = None
    reference_docs: Optional[str] = None
    ideal_answer: Optional[str] = None

# 초기 상태
initial_state = State(
    tech_keywords="python, java, react",  # 기본 키워드
    question_count=0,
    max_questions=5
)


vector_db_high = FAISS.load_local(
    folder_path="/Users/gim-woncheol/Desktop/finalproject/backend/high_db",
    index_name="python_high_chunk700",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)


vector_db_low = FAISS.load_local(
    folder_path="/Users/gim-woncheol/Desktop/finalproject/backend/low_db",
    index_name="python_low_chunk700",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)



# ChatOpenAI 클라이언트 생성 함수
def get_client():
    return ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        # openai_api_key=os.getenv("OPENAI_API_KEY")
        openai_api_key=get_parameter('/TEST/CICD/STREAMLIT/OPENAI_API_KEY')
    ) 


# ChatOpenAI 인스턴스 생성
chat = get_client()


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






def generate_question(state: State, interview_id: int) -> State:
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
    save_question_to_db(
        interview_id=interview_id,
        job_question=question_text,
        job_answer="N/A",
        job_solution="N/A",
        job_score=0,
        question_vector="0.0, 0.0, 0.0"
    )

    # 새로운 상태 반환
    return {
        **state,
        "question": question_text,
        "reference_docs": reference_docs,
        "ideal_answer": retrieved_content.strip(),
        "question_count": question_count + 1,
    }


# 질문 생성 API 엔드포인트
@router.post("/generate_question")
async def generate_question_endpoint(state: State):
    """
    기술 키워드를 바탕으로 질문을 생성합니다.
    """
    try:
        # 질문 생성 함수 호출
        updated_state = generate_question(state.dict(), interview_id=1)  # 예제 interview_id 사용
        return [{
            "question": updated_state["question"],
            "reference_docs": updated_state["reference_docs"],
            "ideal_answer": updated_state["ideal_answer"]
        }]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")

