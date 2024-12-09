from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from question_llm.interview.generate_questions import generate_questions, create_new_interview
from models import Interview
from database import SessionLocal
from .crud import get_interviews_by_user_id
from sqlalchemy.exc import SQLAlchemyError
from datetime import  datetime
from question_llm.interview.database_utils import save_questions_to_db, save_evaluated_answers_to_db
from question_llm.interview.collect_answer import collect_answers
from question_llm.interview.generate_report import generate_report
from question_llm.interview.evaluate_answers import evaluate_answer
from models import EvaluateAnswersRequest
from sentence_transformers import SentenceTransformer


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

def makequestion(keywords: List[str],db_session: Session):  # db_session을 인자로 받도록 수정
    """
    모의 면접 프로세스 관리.
    """
    USER_ID = 3808083867
    USER_JOB = "백엔드 개발자"
    JOB_TALENT = "Python, Django"
    RESUME_PATH = "path/to/resume.pdf"

    try:
        # Step 1: 인터뷰 생성 및 ID 확보
        interview_id = create_new_interview(
            user_id=USER_ID,
            user_job=USER_JOB,
            job_talent=JOB_TALENT,
            resume_path=RESUME_PATH,
            interview_time=datetime.now(),
            db_session=db_session  # 전달된 db_session 사용
        )
        if not interview_id:
            raise ValueError("Failed to create new interview.")
        print(f"Interview created with ID: {interview_id}")

        questions = generate_questions(keywords, interview_id, db_session)
        for question in questions:
            save_questions_to_db(interview_id, questions, db_session)
        
        return questions, interview_id
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        raise
    except Exception as e:
        print(f"An error occurred during the mock interview process: {e}")
        raise

@router.post("/generate_question")
async def generate_interview_questions(keywords: List[str], db: Session = Depends(get_db)):
    try:
        questions, interview_id = makequestion(keywords, db)  # db를 인자로 전달
        print(keywords)
        
        return {"message": "Questions generated successfully", "interview_id": interview_id, "questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/evaluate_answers")
async def evaluate_answers(request: EvaluateAnswersRequest, db: Session = Depends(get_db)):
    try:
        print(request)
        interview_id = request.interview_id
        answers_from_frontend = request.answers  

        # Step 4: 질문과 답변 매핑 
        mapped_answers = []
        evaluated_answers  = []
        for answer_data in answers_from_frontend:
            mapped_data = {
                "interview_id": interview_id,
                "question": answer_data.question,
                "answer": answer_data.answer,
                "model_answer": answer_data.solution,  # solution을 model_answer로 사용
            }
            mapped_answers.append(mapped_data)

        for answer_data in mapped_answers:
                evaluation_result = evaluate_answer(
                    interview_id = interview_id,
                    model = model,
                    question=answer_data["question"],
                    answer=answer_data["answer"],
                    model_answer=answer_data["model_answer"],
                )
                evaluated_answers.append(evaluation_result)
                print(f"Evaluation Results: {evaluated_answers}")

        save_evaluated_answers_to_db(interview_id, evaluated_answers, db)

        print(f"Mapped Answers: {mapped_answers}")


        # Step 6: 총평 생성
        try:
            report = generate_report(
                evaluation_results=evaluated_answers,  # 모든 평가 결과 전달
                db_session=db,
            )
            print("Final Report Generated:")
            print(report)
            return {"message": "Evaluation completed successfully", "report": report}
        except Exception as e:
            print(f"Error during report generation: {e}")
            raise HTTPException(status_code=500, detail="Error during report generation")
        
    except Exception as e:
        print(f"An error occurred during the evaluation process: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the evaluation process")


@router.get("/interview/{user_id}")
async def read_interviews(user_id: int, db: Session = Depends(get_db)):
    interviews = get_interviews_by_user_id(db=db, user_id=user_id)
    if not interviews:
        raise HTTPException(status_code=404, detail="No interviews found for this user")
    
    return [{"interview_id": interview.interview_id, "interview_created": interview.interview_created} for interview in interviews]


