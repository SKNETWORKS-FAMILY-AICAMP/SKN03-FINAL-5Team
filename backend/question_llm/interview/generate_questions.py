import random
import pandas as pd
from typing import List, Dict
import time
from .prompt import question_prompt, model_answer
from datetime import datetime
from langchain_openai import ChatOpenAI
from .database_utils import create_new_question_in_db
from .question_similarity import question_similarity_main
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


# openai_api_key = get_parameter('/TEST/CICD/STREAMLIT/OPENAI_API_KEY')

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
print(openai_api_key)

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
async def cross_encoder_reranker(query, db_level="low", top_k=5):
    
    embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key),
    allow_dangerous_deserialization=True,


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




# 질문생성함수
async def generate_questions(keywords: List[str], interview_id: int, db_session):
    questions = []
    if not keywords:  # 키워드가 없는 경우
        for i in range(5):
            korean_job_question, korean_job_solution = question_similarity_main(i + 1)
            translation_prompt = (
                f"Translate the following question and its answer into English:\n\n"
                f"Question:\n{korean_job_question}\n\n"
                f"Answer:\n{korean_job_solution}\n"
            )
            try:
                translation_response = chat.invoke([SystemMessage(content=translation_prompt)])
                translated_text = translation_response.content.strip()
                english_job_question, english_job_solution = translated_text.split("\nAnswer:")
            except Exception as e:
                print(f"Error during translation: {e}")
                english_job_question = "Translation Error"
                english_job_solution = "Translation Error"
            
            question_id = create_new_question_in_db(
                    interview_id=interview_id,
                    job_question_kor=korean_job_question.strip(),
                    job_solution_kor=korean_job_solution.strip(),
                    job_question_eng=english_job_question.strip(),
                    job_solution_eng=english_job_solution.strip(),
                )

            questions.append({
                "question_id":question_id,
                "interview_id": interview_id,
                "job_question": korean_job_question.strip(),
                "job_question_english": english_job_question.strip(),
                "job_answer": "N/A",
                "job_solution": korean_job_solution.strip(),
                "job_solution_english": english_job_solution.strip(),
                "job_score": 0,
                "question_vector_path": "default/path/vector.json",
                "selected_keyword": "None_keyword",
                "job_context": "None_context"
            })
    else: 
        questions = []
        db_allocation = ["low"] * 5 + ["high"] * 0
        random.shuffle(db_allocation)

        # 키워드 리스트를 하나의 문자열로 결합
        combined_keywords = ", ".join(keywords)
        print(f"Combined Keywords: {combined_keywords}")

        for db_level in db_allocation:
            # 검색
            search_results = cross_encoder_reranker(query=combined_keywords, db_level=db_level, top_k=5)
            if not search_results:
                # 검색 결과가 없으면 반대 레벨에서도 검색
                alternate_level = "high" if db_level == "low" else "low"
                search_results = cross_encoder_reranker(query=combined_keywords, db_level=alternate_level, top_k=5)

            if not search_results:
                print("검색 결과가 없습니다.")
                continue

            # 검색된 각 문서를 순회하며 질문 생성
            for i, doc in enumerate(search_results):
                retrieved_content = doc.page_content

                # 한글 질문 생성
                prompt = question_prompt() + (
                    f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
                    f"기술 스택: {combined_keywords}\n"
                    f"하나의 질문만 반환해주시기 바랍니다."
                )
                question_response = chat.invoke([SystemMessage(content=prompt)])
                korean_job_question = question_response.content.strip()

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

                question_id = create_new_question_in_db(
                    interview_id=interview_id,
                    job_question_kor=korean_job_question.strip(),
                    job_solution_kor=korean_job_solution.strip(),
                    job_question_eng=english_job_question.strip(),
                    job_solution_eng=english_job_solution.strip(),
                )

                # 결과 추가
                questions.append({
                    "interview_id": interview_id,
                    "question_id":question_id,
                    "job_question_kor": korean_job_question.strip(),
                    "job_question_eng": english_job_question.strip(),
                    "job_answer_kor": "N/A",
                    "job_answer_eng": "N/A",
                    "job_solution_kor": korean_job_solution.strip(),
                    "job_solution_eng": english_job_solution.strip(),
                    "job_score": 0,
                    "selected_keyword": combined_keywords,
                    "job_context": retrieved_content,
                })

                # 질문이 5개가 되면 종료
                if len(questions) >= 5:
                    break

            # 질문이 5개가 되면 외부 루프도 종료
            if len(questions) >= 5:
                break

    # # 데이터를 DataFrame으로 변환
    # df = pd.DataFrame(questions, columns=[
    #     "job_question", "selected_keyword","job_question_english", "job_solution", 
    #     "job_solution_english", "retrieved_content"
    # ])
    # output_folder = "c:/dev/SKN03-Final-5Team-git/backend/question_llm/interview/csv_folder"

    # timestamp = time.strftime("%Y%m%d_%H%M%S")
    # output_csv_path = os.path.join(output_folder, f"Python_file_question_data{timestamp}.csv")

    # df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    # print(f"결과가 {output_csv_path}에 저장되었습니다.")

    return questions
