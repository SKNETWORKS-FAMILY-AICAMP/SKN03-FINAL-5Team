from sqlalchemy import Column, Integer, String, Date,DateTime
from database import Base
from datetime import date  
from pydantic import BaseModel
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "user_tb"  

    id = Column(String(45), primary_key=True, index=True) 
    user_name = Column(String(45))  
    user_email = Column(String(45)) 
    user_joined = Column(Date)  
    access_token = Column(String)
    refresh_token = Column(String)
    access_token_expiry = Column(DateTime)
    refresh_token_expiry = Column(DateTime)



class UserRegister(BaseModel):
    name: str
    email: str
    id: int
    user_joined: date
    
class Board(Base):
    __tablename__ = "board_tb"
    
    idx = Column(Integer, primary_key=True, autoincrement=True)
    writer = Column(String(30), nullable=False)
    title = Column(String(30), nullable=False)
    content = Column(String(100), nullable=False)
    post_date = Column(DateTime, nullable=False, default=func.now())
    del_yn = Column(String(1), nullable=False, default='Y')