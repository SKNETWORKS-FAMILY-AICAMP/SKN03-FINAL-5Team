from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from database import Base
from datetime import date, datetime
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Date
from sqlalchemy.dialects.mysql import DATETIME, LONGTEXT, SMALLINT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.orm import configure_mappers
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
<<<<<<< HEAD
Base = declarative_base()
metadata = Base.metadata
=======
from sqlalchemy.sql import func

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey

>>>>>>> origin/main


<<<<<<< HEAD
    id = Column(String(45), primary_key=True)
    user_name = Column(String(45), nullable=False)
    user_email = Column(String(45), nullable=False)
    user_joined = Column(DateTime, nullable=False)
    access_token = Column(String(255))
    refresh_token = Column(String(255))
    access_token_expiry = Column(DateTime)
    refresh_token_expiry = Column(DateTime)
=======
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


>>>>>>> origin/main

    # BoardTb와의 관계 설정
    boards = relationship("BoardTb", back_populates="user")


class UserRegister(BaseModel):
    name: str
    email: str
    id: int
    user_joined: date

<<<<<<< HEAD
=======
class Interview(Base):
    __tablename__ = "interview_tb"

    interview_id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(String(45), nullable=False)                 
    user_job = Column(String(255), nullable=True)                
    job_talent = Column(String(255), nullable=True)              
    interview_time = Column(DateTime, nullable=True)             
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

>>>>>>> origin/main


class BoardTb(Base):
    __tablename__ = 'board_tb'
    __table_args__ = (
        CheckConstraint("(`del_yn` in ('Y', 'N'))"),
    )

    idx = Column(Integer, primary_key=True)
    id = Column(ForeignKey('user_tb.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    title = Column(String(50), nullable=False)
    content = Column(String(255), nullable=False)
    post_date = Column(DateTime, nullable=False)
    del_yn = Column(String(1), nullable=False)

    # UserTb와의 관계 설정
    user = relationship("UserTb", back_populates="boards")

# 모든 클래스 정의 후 관계 설정
UserTb.boards = relationship("BoardTb", back_populates="user")
BoardTb.user = relationship("UserTb", back_populates="boards")

# 매퍼 초기화
configure_mappers()

class AuthGroup(Base):
    __tablename__ = 'auth_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DATETIME(fsp=6))
    is_superuser = Column(TINYINT(1), nullable=False)
    username = Column(String(150), nullable=False, unique=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False)
    is_staff = Column(TINYINT(1), nullable=False)
    is_active = Column(TINYINT(1), nullable=False)
    date_joined = Column(DATETIME(fsp=6), nullable=False)


class DjangoContentType(Base):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        Index('django_content_type_app_label_model_76bd3d3b_uniq', 'app_label', 'model', unique=True),
    )

    id = Column(Integer, primary_key=True)
    app_label = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)


class DjangoMigration(Base):
    __tablename__ = 'django_migrations'

    id = Column(BigInteger, primary_key=True)
    app = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    applied = Column(DATETIME(fsp=6), nullable=False)


class DjangoSession(Base):
    __tablename__ = 'django_session'

    session_key = Column(String(40), primary_key=True)
    session_data = Column(LONGTEXT, nullable=False)
    expire_date = Column(DATETIME(fsp=6), nullable=False, index=True)


class AuthPermission(Base):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        Index('auth_permission_content_type_id_codename_01ab375a_uniq', 'content_type_id', 'codename', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id'), nullable=False)
    codename = Column(String(100), nullable=False)

    content_type = relationship('DjangoContentType')


class AuthUserGroup(Base):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        Index('auth_user_groups_user_id_group_id_94350c0c_uniq', 'user_id', 'group_id', unique=True),
    )

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False)
    group_id = Column(ForeignKey('auth_group.id'), nullable=False, index=True)

    group = relationship('AuthGroup')
    user = relationship('AuthUser')




class DjangoAdminLog(Base):
    __tablename__ = 'django_admin_log'
    __table_args__ = (
        CheckConstraint('(`action_flag` >= 0)'),
    )

    id = Column(Integer, primary_key=True)
    action_time = Column(DATETIME(fsp=6), nullable=False)
    object_id = Column(LONGTEXT)
    object_repr = Column(String(200), nullable=False)
    action_flag = Column(SMALLINT, nullable=False)
    change_message = Column(LONGTEXT, nullable=False)
    content_type_id = Column(ForeignKey('django_content_type.id'), index=True)
    user_id = Column(ForeignKey('auth_user.id'), nullable=False, index=True)

    content_type = relationship('DjangoContentType')
    user = relationship('AuthUser')


<<<<<<< HEAD
class InterviewTb(Base):
    __tablename__ = 'interview_tb'

    interview_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user_tb.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    user_job = Column(String(255), nullable=False)
    job_talent = Column(String(255), nullable=False)
    interview_time = Column(DateTime, nullable=False)
    interview_created = Column(DateTime, nullable=False)
    resume_path = Column(VARCHAR(255), nullable=False)

    user = relationship('UserTb')
    questions = relationship("QuestionTb", back_populates="interview")
    report = relationship("ReportTb", back_populates="interview")
=======

>>>>>>> origin/main

class ReportTb(Interview):
    __tablename__ = 'report_tb'

    interview_id = Column(ForeignKey('interview_tb.interview_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    strength = Column(String(255), nullable=False)
    weakness = Column(String(255), nullable=False)
    ai_summary = Column(DateTime, nullable=False)
    detail_feedback = Column(DateTime, nullable=False)
    attitude_feedback = Column(VARCHAR(255), nullable=False)
    report_score = Column(Integer, nullable=False)
    report_created = Column(DateTime, nullable=False)

    interview = relationship("InterviewTb", back_populates="report")
    
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

    question_id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(ForeignKey('interview_tb.interview_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    job_question = Column(String(255), nullable=False)
    job_answer = Column(String(255), nullable=False)
    job_solution = Column(String(255), nullable=False)
    job_score = Column(Integer, nullable=False)
    question_vector_path = Column(VARCHAR(255), nullable=False)

    interview = relationship('Interview')
