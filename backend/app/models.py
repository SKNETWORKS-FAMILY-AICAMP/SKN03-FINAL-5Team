from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "user_tb"  # 테이블 이름

    # 기본 키(primary key)로 설정
    user_id = Column(String(45), primary_key=True, index=True)  # 사용자 아이디 (primary key 설정)
    user_name = Column(String(45))  # 사용자 이름
    user_pw = Column(String(45))  # 사용자 비밀번호
    user_email = Column(String(45))  # 사용자 이메일
    terms_check = Column(String(45))  # 약관 동의 여부