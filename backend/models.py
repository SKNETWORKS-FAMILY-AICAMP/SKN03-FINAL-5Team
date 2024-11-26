from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "user_tb"  # 테이블 이름

    id = Column(String(45), primary_key=True, index=True) 
    user_name = Column(String(45))  
    user_email = Column(String(45)) 
    terms_check = Column(String(45))
    user_joined = Column(String(45))