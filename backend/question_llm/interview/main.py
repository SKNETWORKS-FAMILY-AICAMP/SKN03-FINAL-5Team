from .generate_questions import generate_questions
from .process_answers import process_answers
from .evaluate_answers import evaluate_answer
from .generate_report import generate_report
from .database_utils import create_new_interview, save_evaluated_answers_to_db, save_mapped_answers_to_db
from .keyword_s3 import keyword_main, ResumePathManager
from database import SessionLocal
from .collect_answer import collect_answers
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
import os
import pandas as pd
from datetime import datetime


model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

def get_client():
    return ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY")
        )

# ChatOpenAI 인스턴스 생성
chat = get_client()


from sqlalchemy.exc import SQLAlchemyError

# RESUME_PATH 긁어오는 함수
def use_resume_path():

    resume_path = ResumePathManager.get_path()
    return resume_path
    # 추가 작업 수행 가능



def main():
    """
    모의 면접 프로세스 관리.
    """
    make_keywords = keyword_main()
    pdf_path = use_resume_path()

    USER_ID = 1
    USER_JOB = "풀스텍 개발자"
    RESUME_PATH = pdf_path

    try:
        # Step 1: 인터뷰 생성 및 ID 확보
        with SessionLocal() as db_session:
            interview_id = create_new_interview(
                user_id=USER_ID,
                user_job=USER_JOB,
                resume_path=RESUME_PATH,   
                db_session=db_session
            )
            if not interview_id:
                raise ValueError("Failed to create new interview.")
            print(f"Interview created with ID: {interview_id}")

            # Step 2: 질문 생성 .split(", ")
            keywords = make_keywords.split(", ")
            keyjob = USER_JOB
            print(keyjob)
            print(type(keyjob))
            questions = generate_questions(keywords, interview_id, keyjob, db_session)
            print(f"Generated Questions: {questions}")

            # Step 3: 프론트에서 답변 받기 (샘플 답변 생성)
            answers_from_frontend = [
                {"question": q["job_question_kor"], "answer": f"Sample answer for {q['job_question_kor'][:10]}..."}
                for q in questions
            ]


            # Step 4: 질문과 답변 매핑 
            mapped_answers = collect_answers(answers_from_frontend, questions)
            print(f"Mapped Answers: {mapped_answers}")

            save_mapped_answers_to_db(mapped_answers ,db_session)

            # Step 5: 답변 평가 (평가 결과는 리스트로 저장)
            evaluated_answers  = []
            for answer_data in mapped_answers:
                evaluation_result = evaluate_answer(
                    interview_id = answer_data["interview_id"],
                    question_id = answer_data["question_id"],
                    model = model,
                    question=answer_data["job_question_kor"],
                    answer=answer_data["job_answer_kor"],
                    model_answer=answer_data["job_solution_kor"],
                    job_context=answer_data["job_context"],
                )
                evaluated_answers .append(evaluation_result)
            print(f"Evaluation Results: {evaluated_answers }")

            save_evaluated_answers_to_db(evaluated_answers, db_session)

            # Step 6: 총평 생성
            # try:
            #     report = generate_report(
            #         evaluation_results=evaluated_answers,  # 모든 평가 결과 전달
            #         db_session = db_session,
            #         interview_id = interview_id
            #     )
            #     print("Final Report Generated:")
            #     print(report)
            # except Exception as e:
            #     print(f"Error during report generation: {e}")
            #     return
            
            # print("Mock interview process completed successfully.")

    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An error occurred during the mock interview process: {e}")

    
if __name__ == "__main__":
    main()
