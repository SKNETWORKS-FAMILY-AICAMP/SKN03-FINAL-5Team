from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from .crud import get_interviews_by_user_id

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/interview/{user_id}")
async def read_interviews(user_id: int, db: Session = Depends(get_db)):
    interviews = get_interviews_by_user_id(db=db, user_id=user_id)
    if not interviews:
        raise HTTPException(status_code=404, detail="No interviews found for this user")
    
    return [{"interview_id": interview.interview_id, "interview_created": interview.interview_created} for interview in interviews]