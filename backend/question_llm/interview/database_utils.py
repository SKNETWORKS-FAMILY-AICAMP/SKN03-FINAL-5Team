import pandas as pd
from typing import Dict, List
import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from datetime import  datetime
from sqlalchemy.orm import Session
from sqlalchemy import update

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
        question.job_question_kor = job_question
        question.job_answer_kor = job_answer
        question.job_solution_kor = job_solution
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
    print(questions)
    for question in questions:
        question_entry = QuestionTb(
            interview_id=interview_id,
            job_question_kor=question["job_question_kor"],
            job_question_eng=question['job_question_eng'],
            job_answer_kor=question["job_answer_kor"],
            job_answer_eng=question['job_answer_eng'],
            job_solution_kor=question["job_solution_kor"],
            job_solution_eng=question['job_solution_eng'],
            job_context=question['job_context'],
            job_score=question["job_score"],
            
        )
    db_session.add(question_entry)
    db_session.commit()


def save_report_to_db(db_session, **kwargs):

    try:
        # ReportTb의 컬럼과 매칭되는 데이터만 필터링
        filtered_data = {key: value for key, value in kwargs.items() if hasattr(ReportTb, key)}
        report = ReportTb(**filtered_data)
        db_session.add(report)
        db_session.commit()
        print("Report saved successfully in DB.")
    except Exception as e:
        db_session.rollback()
        print(f"Error saving report to DB: {e}")
        raise



def create_new_interview(user_id: int, user_job: str, resume_path: str, interview_created: datetime, db_session: Session) -> int:

    try:
        # 인터뷰 데이터 생성
        new_interview = Interview(
            user_id=user_id,
            user_job=user_job,
            resume_path=resume_path,
            interview_created=interview_created,
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

    with SessionLocal() as session:
        for answer in answers:
            db_record = QuestionTb(
                question_id=answer["question_id"],
                job_question_kor=answer["question"],
                job_answer_kor=answer["answer"],
                job_solution_kor=answer["ideal_answer"],
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

    try:
        for answer in evaluated_answers:
            stmt = update(QuestionTb).where(
                (QuestionTb.interview_id == interview_id) &
                (QuestionTb.job_question == answer["question"])
            ).values(
                job_answer_kor=answer["answer"],
                job_solution_kor=answer["model_answer"],
                job_score=answer["score"],
            )
            db_session.execute(stmt)
        
        db_session.commit()
        print("Evaluated answers updated in DB successfully.")
    except Exception as e:
        db_session.rollback()
        print(f"Error during DB update: {e}")
        raise


def save_report_to_db(
    interview_id: int,
    strength: str,
    weakness: str,
    ai_summary: str,
    detail_feedback: str,
    report_score: int,
    db_session: Session
):

    try:
        report = ReportTb(
            interview_id=interview_id,
            strength=strength,
            weakness=weakness,
            ai_summary=ai_summary,
            detail_feedback=detail_feedback,
            report_score=report_score,
            report_created=datetime.now(),  # 생성 시간 추가
        )
        db_session.add(report)
        db_session.commit()
        print("Report saved successfully!")
    except SQLAlchemyError as e:
        db_session.rollback()
        print(f"Error saving report to DB: {e}")
        raise e
    


def get_job_questions_by_interview_id(db: Session, interview_id: int):
    return (
        db.query(QuestionTb.job_question_eng)
        .join(Interview, QuestionTb.interview_id == Interview.interview_id)
        .filter(Interview.interview_id == interview_id)
        .all()
    )