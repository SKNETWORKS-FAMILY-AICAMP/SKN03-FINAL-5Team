from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal
from .crud import get_interviews_by_user_id
from utils import upload_to_s3, save_to_database
from datetime import datetime
from models import Interview

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

BUCKET_NAME = "sk-unailit"

@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    user_job: str = Form(...),
    job_talent: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    사용자가 업로드한 이력서를 S3에 저장하고, 데이터베이스에 해당 경로를 기록하는 API
    """
    try:
        # S3에 파일 업로드
        s3_path = upload_to_s3(file.file, BUCKET_NAME, f"resume/{file.filename}")

        # 데이터베이스에 사용자 정보 및 경로 저장
        # interview = save_to_database(db, s3_path, user_id, user_job,job_talent)
        interview = Interview(
            user_id=user_id,
            user_job=user_job,
            job_talent=job_talent,

            resume_path=s3_path,
            interview_time = datetime.utcnow(),  # 현재 시간 설정
            interview_created = datetime.utcnow()
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)

        return {
            "message": "이력서가 성공적으로 업로드되었습니다.",
            "data": {
                "interview_id": interview.interview_id,
                "resume_path": interview.resume_path,
                "user_id": interview.user_id,
                "user_job": interview.user_job,
                "interview_time": interview.interview_time,
                "interview_created": interview.interview_created,
                "job_talent" : interview.job_talent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
    
@router.get("/interview/{user_id}")
async def read_interviews(user_id: int, db: Session = Depends(get_db)):
    interviews = get_interviews_by_user_id(db=db, user_id=user_id)
    if not interviews:
        raise HTTPException(status_code=404, detail="No interviews found for this user")
    
    return [{"interview_id": interview.interview_id, "interview_created": interview.interview_created} for interview in interviews]