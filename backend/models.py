from sqlalchemy import Column, Integer, String, Date,DateTime
from database import Base
from datetime import date  
from pydantic import BaseModel

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