from sqlalchemy.orm import Session
from models import User

def get_user_by_kakao_id(db: Session, kakao_id: int):
    return db.query(User).filter(User.kakao_id == kakao_id).first()

def create_user(db: Session, user_id: str, user_name: str, user_pw: str, user_email: str, terms_check: str):
    db_user = User(
        user_id=user_id,
        user_name=user_name,
        user_pw=user_pw,
        user_email=user_email,
        terms_check=terms_check
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user