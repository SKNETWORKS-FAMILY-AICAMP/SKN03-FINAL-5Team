from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from database import Base
from datetime import date, datetime
from pydantic import BaseModel
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "user_tb"  

    id = Column(String(45), primary_key=True, index=True) 
    user_name = Column(String(45))  
    user_email = Column(String(45)) 
    user_joined = Column(Date)  


class UserToken(Base):
    __tablename__ = "token_tb"

    id = Column(String(45), ForeignKey("user_tb.id"), primary_key=True)  
    refresh_token = Column(String(255), nullable=True)
    refresh_token_created = Column(DateTime(timezone=True), server_default=func.now())


class UserRegister(BaseModel):
    name: str
    email: str
    id: int
    user_joined: date

class Interview(Base):
    __tablename__ = "interview_tb"

    interview_id = Column(Integer, primary_key=True, index=True)  # 인터뷰 ID
    user_id = Column(Integer)  # 사용자 ID (외래 키)
    interview_created = Column(DateTime)  # 인터뷰 생성 시간