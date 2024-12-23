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
import random

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
    folder_path=os.path.join(parent_dir, "low_local_db"),
    index_name="python_new_low_chunk700",
    embeddings=embeddings,
    allow_dangerous_deserialization=True,
)




# 검색기 함수
def cross_encoder_reranker(query, db_level="low", top_k=10):


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
def generate_questions(keywords: List[str], interview_id: int, db_session):
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

        selected_keywords = random.sample(keywords, min(len(keywords), 15))
        combined_keywords = ", ".join(selected_keywords)
        # 키워드 리스트를 하나의 문자열로 결합
        # combined_keywords = ", ".join(keywords)
        print(f"Combined Keywords: {combined_keywords}")

        for db_level in db_allocation:
            # 검색
            search_results = cross_encoder_reranker(query=combined_keywords, db_level=db_level, top_k=10)
            if not search_results:
                # 검색 결과가 없으면 반대 레벨에서도 검색
                alternate_level = "high" if db_level == "low" else "low"
                search_results = cross_encoder_reranker(query=combined_keywords, db_level=alternate_level, top_k=10)

            if not search_results:
                print("검색 결과가 없습니다.")
                continue

            search_results = random.sample(search_results, min(len(search_results), 5))
            
            # 검색된 각 문서를 순회하며 질문 생성
            for i, doc in enumerate(search_results):
                retrieved_content = doc.page_content

                # 한글 질문 생성
                prompt = question_prompt() + (
                    f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
                    f"다음의 키워드가 공식문서의 데이터와 연관이 있다면 키워드와 공식문서를 함께 활용해서 다채로운 질문을 생성해주세요:\n{combined_keywords}\n"
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

    new_df = pd.DataFrame(questions, columns=[
        "job_question_kor", "selected_keyword","job_question_eng", "job_solution_kor", 
        "job_solution_eng", "job_context"
    ])

    output_folder = "c:/dev/SKN03-Final-5Team-git/backend/question_llm/interview/csv_folder"
    output_csv_path = os.path.join(output_folder, f"Question_prompt_Project_data.csv")


    # 기존 파일이 존재하는 경우 데이터를 읽어와 병합
    if os.path.exists(output_csv_path):
        existing_df = pd.read_csv(output_csv_path, encoding="utf-8-sig")
        combined_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates()
    else:
        combined_df = new_df

    # 병합된 데이터 저장
    combined_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print(f"결과가 {output_csv_path}에 업데이트되었습니다.")

    return questions


# # 1. 키워드 확장 함수
# def expand_keywords(query: str) -> List[str]:
#     keyword_mapping = {
#         "AWS": ["Amazon Web Services", "Cloud Computing", "EC2", "S3", "AWS Lambda"],
#         "C++": ["STL", "Boost", "Embedded Systems", "Object-Oriented Programming"],
#         "CSS": ["Cascading Style Sheets", "Frontend Styling", "CSS3", "Responsive Design"],
#         "Data Analyst": ["Data Analysis", "Business Intelligence", "Data Visualization", "Excel", "Tableau"],
#         "DBMS": ["Database Management Systems", "SQL", "Relational Database", "Oracle DB", "PostgreSQL"],
#         "Deep Learning": ["Neural Networks", "TensorFlow", "PyTorch", "AI Models", "Keras"],
#         "Django": ["Python Django", "Web Framework", "REST API", "ORM", "Model-View-Template"],
#         "Docker": ["Containerization", "Docker Compose", "Kubernetes", "DevOps", "CI/CD"],
#         "Frontend": ["Frontend Development", "React", "Vue.js", "Angular", "HTML", "CSS", "JavaScript"],
#         "Hadoop": ["Big Data", "MapReduce", "HDFS", "Apache Hive", "Spark Integration"],
#         "Java": ["Java SE", "Spring Framework", "Hibernate", "J2EE", "Android Development"],
#         "JavaScript": ["JS", "Node.js", "Frontend Development", "ES6", "React"],
#         "Kubernetes": ["K8s", "Container Orchestration", "Helm", "Service Mesh", "DevOps"],
#         "Linux": ["Unix", "Shell Scripting", "System Administration", "Red Hat", "Ubuntu"],
#         "Machine Learning": ["ML", "Supervised Learning", "Unsupervised Learning", "Scikit-Learn", "Pandas"],
#         "MongoDB": ["NoSQL", "Document Database", "Replica Sets", "Atlas", "Aggregation Pipeline"],
#         "MySQL": ["Relational Database", "SQL", "InnoDB", "Database Indexing", "Stored Procedures"],
#         "Node.js": ["Backend Development", "Express.js", "Asynchronous Programming", "JavaScript Runtime"],
#         "Project": ["Project Management", "Agile", "Scrum", "JIRA", "PMO"],
#         "Spark": ["Apache Spark", "Distributed Computing", "Big Data", "MLlib", "Stream Processing"],
#         "SQL": ["Structured Query Language", "Database Querying", "T-SQL", "PL/SQL", "Joins"]
#     }
#     return keyword_mapping.get(query, [query])  # 매칭되지 않으면 원래 키워드 유지


# # 2. 쿼리 전처리 함수
# def preprocess_query_with_backup(raw_query: List[str]):
#     """
#     입력된 쿼리에서 유효 키워드를 추출하고, 유효하지 않은 키워드를 별도로 반환.
#     확장된 키워드를 유효 키워드에 포함.
#     """
#     # 1. 유효 키워드 정의 (기본 키워드 리스트)
#     base_keywords = [
#         "Python","AWS", "C++","CSS","Data Analyst",
#     "DBMS","Deep Learning","Django","Docker","Frontend","Hadoop","Java","JavaScript","Kubernetes","Linux",
#     "Machine Learning","MongoDB","MySQL","Node.js","Project","Spark","SQL"
#     ]

#     # 2. 확장 키워드 생성 (기본 키워드의 확장 형태 포함)
#     expanded_keywords = set(base_keywords)  # 기본 키워드 포함
#     for keyword in base_keywords:
#         expanded_keywords.update(expand_keywords(keyword))  # 확장된 키워드 추가

#     # 3. 입력된 키워드를 리스트로 처리
#     valid_filtered_keywords = [word for word in raw_query if word in expanded_keywords]
#     invalid_keywords = [word for word in raw_query if word not in expanded_keywords]

#     # 4. 유효 키워드를 확장하여 반환
#     expanded_valid_keywords = []
#     for keyword in valid_filtered_keywords:
#         expanded_valid_keywords.extend(expand_keywords(keyword))

#     invalid_keywords = []
#     for keyword in invalid_keywords:
#         invalid_keywords.extend(invalid_keywords(keyword))

#     return expanded_valid_keywords, invalid_keywords

# # 3. 검색기
# def high_performance_search(query: List[str], db_level="low", top_k=5):
#     # 1. 쿼리 전처리 및 유효성 검증
#     expanded_keywords, invalid_keywords = preprocess_query_with_backup(query)

#     # 유효 키워드가 없는 경우: 원본 키워드로 검색
#     if not expanded_keywords:
#         expanded_keywords = invalid_keywords

#     # 랜덤 셔플 및 샘플링 (최대 10개 키워드 선택)
#     random.shuffle(expanded_keywords)
#     sampled_keywords = random.sample(expanded_keywords, min(len(expanded_keywords), 10))

#     combined_keywords = ", ".join(sampled_keywords)
#     print(f"Combined Keywords for Search: {combined_keywords}")

#     # 2. 다중 저장소 검색


#     # DB 선택
#     vector_db = vector_db_high if db_level == "high" else vector_db_low

#     # Retriever 설정
#     retriever = vector_db.as_retriever(
#     )

#     # MultiQueryRetriever 생성
#     llm = ChatOpenAI(temperature=0, model="gpt-4o")
#     multi_query_retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)

#     # Cross Encoder Reranker 초기화
#     model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
#     reranker = CrossEncoderReranker(model=model, top_n=top_k)

#     # ContextualCompressionRetriever 생성
#     compression_retriever = ContextualCompressionRetriever(
#         base_compressor=reranker,
#         base_retriever=multi_query_retriever
#     )

#     # 쿼리에 대한 문서 검색 및 압축
#     compressed_docs = compression_retriever.invoke(combined_keywords)

#     return {
#         "reranked_results": compressed_docs,
#         "combined_keywords": combined_keywords
#     }

# # 4. 질문 생성 함수
# def generate_questions(keywords: List[str], interview_id: int, db_session):
#     """
#     원본 쿼리를 기반으로 질문을 생성. 키워드가 없는 경우 기본 질문을 생성.
#     """
#     questions = []
#     # 1. 입력된 키워드 리스트를 확인
#     if not isinstance(keywords, list):
#         raise ValueError("Expected 'keywords' to be a list of strings.")
    
#     if not keywords:
#         # 키워드가 비어 있는 경우 처리
#         print("No keywords provided. Generating default questions.")
#         keywords = ["General"]  # 기본 키워드 추가

#     # 2. 키워드 리스트를 문자열로 변환
#     original_keywords = ", ".join(keywords)
#     print(f"Original Keywords: {original_keywords}")


#     # 쿼리 전처리 및 확장
#     valid_keywords, invalid_keywords = preprocess_query_with_backup(keywords)
#     if not valid_keywords and not invalid_keywords:
#         # 1. 키워드가 없는 경우 기본 질문 생성
#         chat = ChatOpenAI(temperature=0, model="gpt-4o")
#         for i in range(5):
#             korean_job_question, korean_job_solution = question_similarity_main(i + 1)
#             translation_prompt = (
#                 f"Translate the following question and its answer into English:\n\n"
#                 f"Question:\n{korean_job_question}\n\n"
#                 f"Answer:\n{korean_job_solution}\n"
#             )
#             try:
#                 translation_response = chat.invoke([{"role": "system", "content": translation_prompt}])
#                 translated_text = translation_response["choices"][0]["message"]["content"].strip()
#                 english_job_question, english_job_solution = translated_text.split("\nAnswer:")
#             except Exception as e:
#                 print(f"Error during translation: {e}")
#                 english_job_question = "Translation Error"
#                 english_job_solution = "Translation Error"

#             question_id = create_new_question_in_db(
#                 interview_id=interview_id,
#                 job_question_kor=korean_job_question.strip(),
#                 job_solution_kor=korean_job_solution.strip(),
#                 job_question_eng=english_job_question.strip(),
#                 job_solution_eng=english_job_solution.strip(),
#             )

#             questions.append({
#                 "question_id": question_id,
#                 "interview_id": interview_id,
#                 "job_question_kor": korean_job_question.strip(),
#                 "job_question_eng": english_job_question.strip(),
#                 "job_answer_kor": "N/A",
#                 "job_answer_eng": "N/A",
#                 "job_solution_kor": korean_job_solution.strip(),
#                 "job_solution_eng": english_job_solution.strip(),
#                 "job_score": 0,
#                 "selected_keyword": ", ".join(original_keywords),  # 원본 키워드
#                 "job_context": "None_context"
#             })
#     else:
#         # 2. 키워드가 있는 경우 검색 후 질문 생성
#         search_results = high_performance_search(query=keywords, db_level="low", top_k=5)
#         documents = search_results["reranked_results"][:5]  # 최대 5개 문서만 사용

#         for doc in enumerate(documents, start=1):  # 문서 순서와 함께 루프
#             retrieved_content = doc.page_content

#             # 질문 생성
#             chat = ChatOpenAI(temperature=0, model="gpt-4o")
#             prompt = question_prompt() + (
#                 f"다음 공식 문서를 참조하여 기술 면접 질문을 생성해 주세요:\n{retrieved_content}\n"
#                 f"하나의 질문만 반환해주시기 바랍니다."
#             )

#             question_response = chat.invoke([SystemMessage(content=prompt)])
#             korean_job_question = question_response.content.strip()

#             # 한글 모범답안 생성
#             model_prompt = model_answer(korean_job_question, retrieved_content)
#             model_response = chat.invoke([SystemMessage(content=model_prompt)])
#             korean_job_solution = model_response.content.strip()

#             # 영어 번역 생성 (질문과 모범답안 동일성 유지)
#             translation_prompt = (
#                 f"Translate the following question and its answer into English:\n\n"
#                 f"Question:\n{korean_job_question}\n\n"
#                 f"Answer:\n{korean_job_solution}\n"
#                 )
#             translation_response = chat.invoke([SystemMessage(content=translation_prompt)])
#             translated_text = translation_response.content.strip()

#             # 번역된 질문 및 답변 파싱
#             english_job_question, english_job_solution = translated_text.split("\nAnswer:")

#             question_id = create_new_question_in_db(
#                     interview_id=interview_id,
#                     job_question_kor=korean_job_question.strip(),
#                     job_solution_kor=korean_job_solution.strip(),
#                     job_question_eng=english_job_question.strip(),
#                     job_solution_eng=english_job_solution.strip(),
#                 )

#                 # 결과 추가
#             questions.append({
#                     "interview_id": interview_id,
#                     "question_id":question_id,
#                     "job_question_kor": korean_job_question.strip(),
#                     "job_question_eng": english_job_question.strip(),
#                     "job_answer_kor": "N/A",
#                     "job_answer_eng": "N/A",
#                     "job_solution_kor": korean_job_solution.strip(),
#                     "job_solution_eng": english_job_solution.strip(),
#                     "job_score": 0,
#                     "selected_keyword": search_results.get("combined_keywords"),
#                     "job_context": retrieved_content,
#                 })

#                 # 질문이 5개가 되면 종료

#     # 데이터 저장
#     save_questions_to_csv(questions)
#     return questions

# # 5. CSV 저장 함수
# def save_questions_to_csv(questions):
#     output_folder = "c:/dev/SKN03-Final-5Team-git/backend/question_llm/interview/csv_folder"
#     output_csv_path = os.path.join(output_folder, "Project_data.csv")
#     new_df = pd.DataFrame(questions, columns=[
#         "job_question_kor", "selected_keyword","job_question_eng", "job_solution_kor", 
#         "job_solution_eng", "job_context"
#     ])
#     if os.path.exists(output_csv_path):
#         existing_df = pd.read_csv(output_csv_path, encoding="utf-8-sig")
#         combined_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates()
#     else:
#         combined_df = new_df
#     combined_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
#     print(f"결과가 {output_csv_path}에 저장되었습니다.")
