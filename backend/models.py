from sqlalchemy import Column, Integer, String, Date  
from database import Base
from datetime import date  
from pydantic import BaseModel

class User(Base):
    __tablename__ = "user_tb"  

    id = Column(String(45), primary_key=True, index=True) 
    user_name = Column(String(45))  
    user_email = Column(String(45)) 
    terms_check = Column(String(45))
    user_joined = Column(Date)  



class UserRegister(BaseModel):
    name: str
    email: str
    id: int
    terms_check: str
    user_joined: date