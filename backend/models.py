from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Date, Text, DECIMAL
from sqlalchemy.dialects.mysql import DATETIME, LONGTEXT, SMALLINT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.orm import configure_mappers
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from pydantic import BaseModel
from datetime import date, datetime
from sqlalchemy.sql import func
from typing import List






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
    user_id = Column(String(45), nullable=False)                 
    user_job = Column(String(255), nullable=True)                
    job_talent = Column(String(255), nullable=True)              
    interview_created = Column(DateTime, nullable=False)         
    resume_path = Column(String(255), nullable=True) 

    
class Board(Base):
    __tablename__ = "board_tb"

    idx = Column(Integer, primary_key=True, autoincrement=True)  
    id = Column(String(45), nullable=False)  
    title = Column(String(255), nullable=False)  
    content = Column(String(255), nullable=False)  
    post_date = Column(DateTime, nullable=False, default=func.now())  
    del_yn = Column(String(1), nullable=False, default='Y')






class ReportTb(Base):
    __tablename__ = 'report_tb'

    interview_id = Column(ForeignKey('interview_tb.interview_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    strength = Column(String(255), nullable=False)
    weakness = Column(String(255), nullable=False)
    ai_summary = Column(DateTime, nullable=False)
    detail_feedback = Column(Text, nullable=False)
    report_score = Column(Integer, nullable=False)
    report_created = Column(DateTime, nullable=False)


class AuthGroupPermission(Base):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        Index('auth_group_permissions_group_id_permission_id_0cd325b0_uniq', 'group_id', 'permission_id', unique=True),
    )

    id = Column(BigInteger, primary_key=True)
    group_id = Column(ForeignKey('auth_group.id'), nullable=False)
    permission_id = Column(ForeignKey('auth_permission.id'), nullable=False, index=True)

    group = relationship('AuthGroup')
    permission = relationship('AuthPermission')


class AuthUserUserPermission(Base):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        Index('auth_user_user_permissions_user_id_permission_id_14a6b632_uniq', 'user_id', 'permission_id', unique=True),
    )

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False)
    permission_id = Column(ForeignKey('auth_permission.id'), nullable=False, index=True)

    permission = relationship('AuthPermission')
    user = relationship('AuthUser')


class QuestionTb(Base):
    __tablename__ = 'question_tb'

    question_id = Column(Integer, primary_key=True)
    interview_id = Column(ForeignKey('interview_tb.interview_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    job_question_kor = Column(String(255), nullable=True)
    job_question_eng = Column(String(255), nullable=True)
    job_answer_kor = Column(String(255), nullable=True)
    job_answer_eng = Column(String(255), nullable=True)
    job_solution_kor = Column(String(255), nullable=True)
    job_solution_eng = Column(String(255), nullable=True)
    job_context = Column(String(255), nullable=True)
    job_score = Column(DECIMAL, nullable=True)
    interview = relationship('Interview')

class Answer(BaseModel):
    interview_id: int
    question: str
    answer: str
    solution: str

class EvaluateAnswersRequest(BaseModel):
    interview_id: int
    answers: List[Answer]
