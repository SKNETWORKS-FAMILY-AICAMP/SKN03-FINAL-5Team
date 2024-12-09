import pandas as pd
from typing import Dict, List
import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from datetime import  datetime
from sqlalchemy.orm import Session


from database import SessionLocal
from models import QuestionTb, ReportTb, Interview

def update_question_in_db(
    question_id: int,
    interview_id: int,
    job_question: str,
    job_answer: str,
    job_solution: str,
    job_score: float,
) -> bool:

    # DB 세션 생성
    session: Session = SessionLocal()
    try:
        # 업데이트할 질문 가져오기
        question = session.query(QuestionTb).filter(QuestionTb.question_id == question_id).first()
        if not question:
            print(f"[DB 오류] question_id={question_id}가 존재하지 않습니다.")
            return False

        # 질문 업데이트
        question.interview_id = interview_id
        question.job_question = job_question
        question.job_answer = job_answer
        question.job_solution = job_solution
        question.job_score = job_score

        # 변경 사항 커밋
        session.commit()
        print(f"[DB 업데이트 성공] question_id={question_id}, interview_id={interview_id}")
        return True

    except Exception as e:
        session.rollback()  # 트랜잭션 롤백
        print(f"[DB 업데이트 오류] question_id={question_id}, Error: {e}")
        return False

    finally:
        session.close()  # 세션 닫기


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def save_questions_to_db(interview_id: int, questions: List[Dict], db_session):
    for question in questions:
        question_entry = QuestionTb(
            interview_id=interview_id,
            job_question=question["job_question"],
            job_answer=question["job_answer"],
            job_solution=question["job_solution"],
            job_score=question["job_score"],
            question_vector_path=question["question_vector_path"]
        )
        db_session.add(question_entry)
    db_session.commit()



def save_report_to_db(report_data: Dict, db_session):
    """
    보고서 데이터를 DB에 저장합니다.

    Args:
        report_data (Dict): 보고서 데이터.
        db_session: SQLAlchemy DB 세션.
    """
    try:
        report = ReportTb(
            interview_id=report_data["interview_id"],
            strength=report_data["strength"],
            weakness=report_data["weakness"],
            ai_summary=report_data["ai_summary"],
            report_score=report_data["report_score"],
            detail_feedback=str(report_data["detail_feedback"]),  # JSON 문자열로 저장
            report_created=report_data["report_created"],
            attitude_feedback=report_data["attitude_feedback"]
        )
        db_session.add(report)
        db_session.commit()
        print("Report saved successfully in DB.")
    except Exception as e:
        db_session.rollback()
        print(f"Error saving report to DB: {e}")



def create_new_interview(user_id: int, user_job: str, job_talent: str, resume_path: str, interview_time: datetime, db_session: Session) -> int:
    """
    새로운 인터뷰를 생성하고 인터뷰 ID를 반환합니다.
    """
    try:
        # 인터뷰 데이터 생성
        new_interview = Interview(
            user_id=user_id,
            user_job=user_job,
            job_talent=job_talent,
            resume_path=resume_path,
            interview_time=interview_time,
            interview_created=datetime.now(),
        )

        # DB 세션을 사용하여 데이터 추가 및 커밋
        db_session.add(new_interview)
        db_session.commit()
        db_session.refresh(new_interview)

        # 생성된 인터뷰 ID 반환
        return new_interview.interview_id
    except Exception as e:
        print(f"Error creating interview: {e}")
        db_session.rollback()  # 에러 발생 시 롤백
        return None
    
def save_answers_to_db(answers: List[Dict]):
    """
    매핑된 질문-답변 데이터를 DB에 저장합니다.

    Args:
        answers (List[Dict]): 질문-답변 매핑 데이터 리스트
    """
    with SessionLocal() as session:
        for answer in answers:
            db_record = QuestionTb(
                question_id=answer["question_id"],
                job_question=answer["question"],
                job_answer=answer["answer"],
                job_solution=answer["ideal_answer"],
                job_score=0,  # 초기 점수 설정
                question_vector_path="default/path/vector.json",
            )
            session.add(db_record)
        session.commit()
    print("Answers successfully saved to the database.")

def save_evaluated_answers_to_db(
    interview_id: int,
    evaluated_answers: List[Dict],
    db_session: Session
):
    """
    평가된 답변을 DB에 저장합니다.

    Args:
        interview_id (int): 인터뷰 ID
        evaluated_answers (List[Dict]): 평가된 답변 리스트
        db_session (Session): SQLAlchemy DB 세션
    """
    try:
        for answer in evaluated_answers:
            db_record = QuestionTb(
                interview_id=interview_id,
                job_question=answer["question"],
                job_answer=answer["answer"],
                job_solution=answer["model_answer"],
                # job_score=answer["score"],  # 평가 점수 저장
                job_score=0,  # 평가 점수 저장
                question_vector_path="default/path/vector.json",
            )
            db_session.add(db_record)
        db_session.commit()
        print("Evaluated answers stored in DB successfully.")
    except Exception as e:
        db_session.rollback()
        print(f"Error during DB storage: {e}")
        raise
