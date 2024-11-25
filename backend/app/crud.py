from sqlalchemy.orm import Session
from models import User

def get_user_by_kakao_id(db: Session, kakao_id: int):
    return db.query(User).filter(User.kakao_id == kakao_id).first()

def create_user(db: Session, kakao_id: int, nickname: str, email: str = None):
    db_user = User(
        kakao_id=kakao_id,
        nickname=nickname,
        email=email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user