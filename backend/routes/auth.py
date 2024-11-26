# routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
async def register(name: str, email: str, id: str, db: Session = Depends(get_db)):
    # 고유 아이디가 이미 존재하는지 확인
    existing_user = db.query(User).filter(User.id == id).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="해당 고유 아이디는 이미 존재합니다.")
    
    # 새 사용자 추가
    new_user = User(name=name, email=email, id=id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입이 완료되었습니다."}
