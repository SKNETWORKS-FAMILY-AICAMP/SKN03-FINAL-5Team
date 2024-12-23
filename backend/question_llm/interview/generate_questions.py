import random
import pandas as pd
from typing import List, Dict
import time
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
import uuid 
from util.get_parameter import get_parameter
import boto3

load_dotenv()



def fetch_openai_api_key(parameter_name="/TEST/CICD/STREAMLIT/OPENAI_API_KEY"):
    try:
        ssm_client = boto3.client("ssm", region_name="ap-northeast-2")
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        api_key = response["Parameter"]["Value"]
        os.environ["OPENAI_API_KEY"] = api_key
        return api_key
    except Exception as e:
        raise RuntimeError(f"Error fetching parameter: {str(e)}")

# Fetch and set the API key
openai_api_key = os.environ.get("OPENAI_API_KEY") or fetch_openai_api_key()

def get_client():
    return ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True,
        openai_api_key=openai_api_key
        )

# ChatOpenAI 인스턴스 생성
chat = get_client()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)


# 현재 파일의 디렉토리 경로를 가져옴
current_dir = os.path.dirname(os.path.abspath(__file__))

# 상위 디렉토리로 이동 (필요한 만큼 반복).
parent_dir = os.path.dirname(current_dir)

vector_db_high = FAISS.load_local(
    folder_path=os.path.join(parent_dir, "high_db"),
    index_name="python_high_chunk700",
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)

vector_db_low = FAISS.load_local(
    folder_path=os.path.join(parent_dir, "low_db"),
    index_name="python_low_chunk700",
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)

# 검색기 함수
def cross_encoder_reranker(query, db_level="low", top_k=5):

    # DB 선택
    vector_db = vector_db_high if db_level == "high" else vector_db_low

    # Retriever 설정
    retriever = vector_db.as_retriever()

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
    result_string = " ".join(query)
    compressed_docs = compression_retriever.invoke(result_string)
    

    return compressed_docs


# 질문생성함수
def generate_questions(keywords: List[str], USER_JOB: str, interview_id: int, db_session) -> pd.DataFrame:
    questions = []
    """
    주어진 키워드를 바탕으로 질문을 생성하고, DB에 저장 후 DataFrame으로 반환.
    Args:
        keywords (List[str]): 기술 키워드 목록
        interview_id (int): 인터뷰 ID
        db_session: 데이터베이스 세션
    Returns:
        pd.DataFrame: 생성된 질문과 관련 데이터
    """
    db_allocation = ["low"] * 3 + ["high"] * 2
    random.shuffle(db_allocation)

    # 키워드 리스트를 하나의 문자열로 결합
    for db_level in db_allocation:
        # 검색
        search_results = cross_encoder_reranker(query=keywords, db_level=db_level, top_k=5)
        if not search_results:
            # 검색 결과가 없으면 반대 레벨에서도 검색
            alternate_level = "high" if db_level == "low" else "low"
            search_results = cross_encoder_reranker(query=keywords, db_level=alternate_level, top_k=5)
            if not search_results:
                print("검색 결과가 없습니다.")
                continue
        # 검색된 각 문서를 순회하며 질문 생성

        for i, doc in enumerate(search_results):
            retrieved_content = doc.page_content
            reference_docs = doc.metadata.get("source", "출처를 알 수 없음")

            # 한글 질문 생성
            prompt = question_prompt() + (
                f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
                f"다음 면접자의 희망직무를 반영하여 질문을 생성해주세요:\n{USER_JOB}\n"
                f"기술 스택: {keywords}\n"
                f"하나의 질문만 반환해주시기 바랍니다."
            )
            question_response = chat.invoke([SystemMessage(content=prompt)])
            korean_job_question = question_response.content.strip()

            print(korean_job_question)
            # 한글 모범답안 생성
            model_prompt = model_answer(korean_job_question, retrieved_content)
            model_response = chat.invoke([SystemMessage(content=model_prompt)])

            korean_job_solution = model_response.content.strip()


            # 영어 번역 생성 (질문과 모범답안 동일성 유지)
            translation_prompt = (
                f"Translate the following question and its answer into English:\n\n"
                f"Question:\n{korean_job_question}\n\n"
                f"Answer:\n{korean_job_solution}\n"
            )
            translation_response = chat.invoke([SystemMessage(content=translation_prompt)])
            translated_text = translation_response.content.strip()

            # 번역된 질문 및 답변 파싱
            english_job_question, english_job_solution = translated_text.split("\nAnswer:")
            print(english_job_question)


            # 결과 추가
            questions.append({
                "interview_id": interview_id,
                "job_question_kor": korean_job_question.strip(),
                "job_question_eng": english_job_question.strip(),
                "job_answer_kor": "",
                "job_answer_eng": "",
                "job_solution_kor": korean_job_solution.strip(),
                "job_solution_eng": english_job_solution.strip(),
                "job_context": retrieved_content,
                "job_score": 0,
            })

            # 질문이 5개가 되면 종료
            if len(questions) >= 2:
                break

        # 질문이 5개가 되면 외부 루프도 종료
        if len(questions) >= 2:
            break


    return questions
