from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from models import QuestionTb, ReportTb


# 데이터베이스 세션 생성
db_session = SessionLocal()

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
    finally:
        db_session.close()


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


