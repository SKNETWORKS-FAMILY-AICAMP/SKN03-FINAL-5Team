from sqlalchemy.orm import Session
from models import User

def get_user_by_id(db: Session, id: str):
    return db.query(User).filter(User.id == id).first()


def create_user(db: Session, name: str, email: str, id: str):
    db_user = User(
        name=name,
        email=email,
        id=id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, update_data: dict):
    db.query(User).filter(User.id == user_id).update(update_data)
    db.commit()