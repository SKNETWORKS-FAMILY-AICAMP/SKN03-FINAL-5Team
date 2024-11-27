from sqlalchemy.orm import Session
from .auth import get_db
from fastapi import APIRouter, Depends

from routes import board_crud, board_schema

router = APIRouter(
    prefix = "/board"
)

@router.post("/create", description="기본 게시판 - 게시글 생성")
async def create_new_post(new_post : board_schema.NewPost, db : Session):
    return board_crud.insert_post(new_post, db)