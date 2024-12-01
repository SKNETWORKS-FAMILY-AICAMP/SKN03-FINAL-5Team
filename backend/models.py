from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from database import Base
from datetime import date, datetime
from pydantic import BaseModel
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

    interview_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer) 
    interview_created = Column(DateTime)  

    
class Board(Base):
    __tablename__ = "board_tb"

    idx = Column(Integer, primary_key=True, autoincrement=True)  # 게시판 아이디
    id = Column(String(45), nullable=False)  # 사용자 아이디 (ERD의 id 컬럼)
    title = Column(String(255), nullable=False)  # 제목
    content = Column(String(255), nullable=False)  # 내용
    post_date = Column(DateTime, nullable=False, default=func.now())  # 게시판 업로드 날짜
    del_yn = Column(String(1), nullable=False, default='Y')