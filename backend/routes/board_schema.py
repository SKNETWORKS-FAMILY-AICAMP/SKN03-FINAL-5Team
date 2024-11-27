from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewPost(BaseModel):
    writer : str
    title : str
    content : Optional[str] = None
    
class PostList(BaseModel):
    idx: int
    writer: str
    title: str
    post_date: datetime
    
class Post(BaseModel):
    idx: int
    writer: str
    title: str
    post_date: datetime
    
class UpdatePost(BaseModel):
    idx: int
    title : str
    content : str
    
# 게시글 응답을 위한 Pydantic 모델 추가
class BoardResponse(BaseModel):
    idx: int
    writer: str
    title: str
    content: Optional[str] = None
    post_date: datetime
    del_yn: str

    class Config:
        from_attributes = True  # SQLAlchemy 모델을 Pydantic 모델로 변환