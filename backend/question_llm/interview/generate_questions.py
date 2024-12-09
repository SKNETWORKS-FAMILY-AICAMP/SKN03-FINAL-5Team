import random
import pandas as pd
from typing import List, Dict
from .database_utils import save_questions_to_db
from .prompt import question_prompt, model_answer
from datetime import datetime
from langchain_openai import ChatOpenAI
from .database_utils import create_new_interview
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.schema import SystemMessage
from dotenv import load_dotenv
import uuid  # 고유 ID 생성에 사용

load_dotenv()


def get_client():
    return ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY")
        )

# ChatOpenAI 인스턴스 생성
chat = get_client()

embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))


# 현재 파일의 디렉토리 경로를 가져옵니다.
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리로 이동합니다 (필요한 만큼 반복).
parent_dir = os.path.dirname(current_dir)

vector_db_high = FAISS.load_local(
    folder_path=os.path.join(parent_dir, "high_db"),
    index_name="python_high_chunk700",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)

vector_db_low = FAISS.load_local(
    folder_path=os.path.join(parent_dir, "low_db"),
    index_name="python_low_chunk700",
    embeddings=OpenAIEmbeddings(),
    allow_dangerous_deserialization=True,
)


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


def generate_questions(keywords: List[str], interview_id: int, db_session) -> pd.DataFrame:
    """
    주어진 키워드를 바탕으로 질문을 생성하고, DB에 저장 후 DataFrame으로 반환.
    Args:
        keywords (List[str]): 기술 키워드 목록
        interview_id (int): 인터뷰 ID
        db_session: 데이터베이스 세션
    Returns:
        pd.DataFrame: 생성된 질문과 관련 데이터
    """
    questions = []
    db_allocation = ["low"] * 1 + ["high"] * 1  # 3개는 low, 2개는 high
    random.shuffle(db_allocation)  # 랜덤 순서로 DB 검색 레벨 결정

    for db_level in db_allocation:
        # 키워드 선택
        keyword = random.choice(keywords)
        print('db_allow')

        # 검색
        search_results = cross_encoder_reranker(query=keyword, db_level=db_level, top_k=1)
        if not search_results:
            # 검색 결과가 없으면 반대 레벨에서도 검색
            alternate_level = "high" if db_level == "low" else "low"
            search_results = cross_encoder_reranker(query=keyword, db_level=alternate_level, top_k=1)

        # 검색된 결과 처리
        if search_results:
            retrieved_content = search_results[0].page_content
            reference_docs = search_results[0].metadata.get("source", "출처를 알 수 없음")
            print('결과 처리')
        else:
            # 결과가 없으면 기본 메시지 설정
            retrieved_content = "관련 문서를 찾을 수 없습니다."
            reference_docs = "출처를 알 수 없음"

        # 질문 생성
        prompt = question_prompt() + (
                f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
                f"기술 스택: {keyword}\n"
                f"하나의 질문만 반환해주시기 바랍니다."
                )  # 질문 생성 프롬프트
        question_response = chat.invoke([SystemMessage(content=prompt)])
        job_question = question_response.content.strip()

        # 모범답안 생성
        model_prompt = model_answer(job_question, retrieved_content)  # 모범답안 생성 프롬프트
        model_response = chat.invoke([SystemMessage(content=model_prompt)])
        job_solution = model_response.content.strip()


        # 결과 추가
        questions.append({
            "interview_id": interview_id,             # 인터뷰 ID
            "job_question": job_question,             # 생성된 질문
            "job_answer": "N/A",                      # 답변 (초기값)
            "job_solution": job_solution,             # 생성된 모범답안
            "job_score": 0,                           # 초기 점수
            "question_vector_path": "default/path/vector.json",  # 기본 벡터 경로
        })
    
    # DataFrame으로 변환 후 반환
    return questions


    # return pd.DataFrame(questions)


    