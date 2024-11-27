from sqlalchemy.orm import Session
from .auth import get_db
from fastapi import APIRouter

router = APIRouter(
    prefix = "/board"
)

@router.get("/test")
async def board_test():
    return "test"