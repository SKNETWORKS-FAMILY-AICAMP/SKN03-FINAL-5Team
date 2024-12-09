from sqlalchemy.exc import SQLAlchemyError
<<<<<<< HEAD
from datetime import  datetime
import sys
from typing import List, Dict
import os
from sqlalchemy.orm import Session
=======
import sys
import os
>>>>>>> origin/main

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.database import SessionLocal
<<<<<<< HEAD
from backend.models import QuestionTb, ReportTb,InterviewTb
=======
from backend.models import QuestionTb, ReportTb
>>>>>>> origin/main


# 데이터베이스 세션 생성
db_session = SessionLocal()

<<<<<<< HEAD

def create_new_interview(user_id: str, user_job: str, job_talent: str, resume_path: str, interview_time: datetime = None) -> int:
    if interview_time is None:
        interview_time = datetime.now()

    new_interview = InterviewTb(
        user_id=user_id,
        user_job=user_job,
        job_talent=job_talent,
        resume_path=resume_path,
        interview_time=interview_time,
        interview_created=datetime.now()
    )

    try:
        db_session.add(new_interview)
        db_session.commit()
        print(f"Interview created with ID: {new_interview.interview_id}")
        return new_interview.interview_id
    except Exception as e:
        db_session.rollback()
        print(f"Error creating interview: {e}")
        raise

# 초기 질문 ID 생성
def initialize_questions(interview_id, max_questions):
    question_ids = []
    for i in range(max_questions):
        question_id = save_question_to_db(
            interview_id=interview_id,
            job_question="N/A",
            job_answer="N/A",
            job_solution="N/A",
            job_score=0,
            question_vector_path=f"default/path/question_{i}.json"
        )
        question_ids.append(question_id)
    return question_ids


def create_new_question(interview_id: int) -> int:
    """
    새 질문을 생성하고 데이터베이스에 기본 정보를 저장합니다.
    """
    try:
        # 질문 데이터 생성
        new_question = QuestionTb(
            interview_id=interview_id,
            job_question="N/A",
            job_answer="N/A",
            job_solution="N/A",
            job_score=0,
            
        )

        # 데이터베이스에 추가 및 커밋
        db_session.add(new_question)
        db_session.commit()

        print(f"New question created with ID: {new_question.id}")
        return new_question.id  # 생성된 question_id 반환
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error creating new question: {e}")
        raise
=======
def save_question_to_db(interview_id, job_question, job_answer, job_solution, job_score, question_vector):
    """
    QuestionTb 테이블에 데이터를 저장합니다.
    """
    try:
        question = QuestionTb(
            interview_id=interview_id,
            job_question=job_question,
            job_answer=job_answer,
            job_solution=job_solution,
            job_score=job_score,
            question_vector_path=question_vector,
        )
        
        db_session.add(question)
        db_session.commit()
        print("Question saved successfully!")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error saving question to DB: {e}")
>>>>>>> origin/main
    finally:
        db_session.close()


<<<<<<< HEAD

def save_question_to_db(interview_id, job_question, job_answer, job_solution, job_score, question_vector_path):
    new_question = QuestionTb(
        interview_id=interview_id,
        job_question=job_question,
        job_answer=job_answer,
        job_solution=job_solution,
        job_score=job_score,
        question_vector_path=question_vector_path
    )
    db_session.add(new_question)
    db_session.commit()
    return new_question.question_id  # question_id를 반환





def update_question_in_db(question_id, interview_id, job_question, job_answer, job_solution, job_score):
    question = db_session.query(QuestionTb).filter_by(question_id=question_id).first()
    if question is None:
        raise ValueError(f"No question found with question_id {question_id}")
    question.job_question = job_question
    question.job_answer = job_answer
    question.job_solution = job_solution
    question.job_score = job_score
    db_session.commit()
=======
def update_question_in_db(
    question_id: int,
    interview_id: int,
    job_question: str,
    job_answer: str,
    job_solution: str,
    job_answer_score: float
):
    """
    QuestionTb에 데이터를 업데이트하는 함수.
    """
    try:
        question = db_session.query(QuestionTb).filter_by(id=question_id, interview_id=interview_id).first()
        if not question:
            raise ValueError(f"Question with ID {question_id} and interview_id {interview_id} not found.")

        # 필드 업데이트
        question.job_question = job_question
        question.job_answer = job_answer
        question.job_solution = job_solution
        question.job_answer_score = job_answer_score

        db_session.commit()
        print(f"Question {question_id} updated successfully.")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error updating QuestionTb: {e}")
    finally:
        db_session.close()
>>>>>>> origin/main




def save_report_to_db(interview_id, strength, weakness, ai_summary, detail_feedback, attitude, report_score):
    """
    ReportTb 테이블에 데이터를 저장합니다.
    """
    try:
        report = ReportTb(
            interview_id=interview_id,
            strength=strength,
            weakness=weakness,
            ai_summary=ai_summary,
            detail_feedback=detail_feedback,
            attitude_feedback=attitude,
            report_score=report_score,
        )
        db_session.add(report)
        db_session.commit()
        print("Report saved successfully!")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error saving report to DB: {e}")
    finally:
        db_session.close()
<<<<<<< HEAD

=======
>>>>>>> origin/main
