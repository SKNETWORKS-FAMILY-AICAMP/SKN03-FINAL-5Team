# from sqlalchemy.orm import Session
# from .auth import get_db
# from fastapi import APIRouter, Depends

# from routes import board_crud, board_schema

# router = APIRouter(
#     prefix = "/board"
# )

# # @router.post("/create", description="기본 게시판 - 게시글 생성")
# # async def create_new_post(new_post : board_schema.NewPost, db : Session):
# #     return board_crud.insert_post(new_post, db)

# @router.post("/create", description="기본 게시판 - 게시글 생성", response_model=board_schema.BoardResponse)
# async def create_new_post(new_post: board_schema.NewPost, db: Session = Depends(get_db)):
#     return board_crud.insert_post(new_post, db)

# @router.get("/read", description="기본 게시판 - 게시글 조회", response_model=board_schema.BoardResponse)
# async def read_all_post(db: Session = Depends(get_db)):
#     return board_crud.list_all_post(db)

# @router.get("/read/{post_idx}", description="기본 게시판 - 특정 게시글 상세 조회", response_model=board_schema.BoardResponse)
# async def read_post(post_idx : int, db: Session = Depends(get_db)):
#     return board_crud.get_post(post_idx, db)

# @router.put("/update/{post_idx}", description="기본 게시판 - 특정 게시글 수정", response_model=board_schema.BoardResponse)
# async def update_post(update_post : board_schema.UpdatePost, db: Session = Depends(get_db)):
#     return board_crud.get_post(UpdatePost, db)

from sqlalchemy.orm import Session
from .auth import get_db

from fastapi import APIRouter, Depends

from routes import board_crud, board_schema

router = APIRouter(
    prefix="/board",
)

@router.post(path="/create", description="기본 게시판 - 게시글 생성")
async def create_new_post(new_post: board_schema.NewPost, db: Session = Depends(get_db)):
    return board_crud.insert_post(new_post, db)


@router.get(path="/read", description="기본 게시판 - 게시글 조회")
async def read_all_post(db: Session = Depends(get_db)):
    return board_crud.list_all_post(db)


@router.get(path="/read/{post_idx}", description="기본 게시판 - 특정 게시글 상세 조회")
async def read_post(post_idx: int, db: Session = Depends(get_db)):
    return board_crud.get_post(post_idx, db)


@router.put(path="/update/{post_idx}", description="기본 게시판 - 특정 게시글 수정")
async def update_post(update_post: board_schema.UpdatePost, db: Session = Depends(get_db)):
    return board_crud.update_post(update_post, db)


@router.patch(path="/delete/{post_idx}", description="기본 게시판 - 특정 게시글 삭제")
async def delete_post_yn(post_idx: int, db: Session = Depends(get_db)):
    return board_crud.alter_del_yn(post_idx, db)


@router.delete(path="/delete/{post_idx}", description="기본 게시판 - 특정 게시글 삭제")
async def delete_post(post_idx: int, db: Session = Depends(get_db)):
    return board_crud.delete_post(post_idx, db)