# from sqlalchemy.orm import Session
# from sqlalchemy import and_
# from models import Board
# from routes.board_schema import NewPost, BoardResponse, PostList, UpdatePost, Post


# def insert_post(new_post: NewPost, db: Session):
#     post = Board(
#         writer = new_post.writer,
#         title = new_post.title,
#         content = new_post.content
#     )
#     db.add(post)
#     db.commit()
#     db.refresh(post)
    
#     return BoardResponse.from_orm(post)  # SQLAlchemy 모델을 Pydantic 모델로 변환

# def list_all_post(db: Session):
#     lists =db.query(Board).filter(Board.del_yn == 'Y').all()
#     return [PostList(idx=row.idx, writer=row.writer, title=row.title, post_date=row.post_date) for row in lists]

# def get_post(post_idx:int, db:Session):
#     try:
#         post = db.query(Board).filter(and_(Board.idx, Board.del_yn == 'Y')).first()
#         return Post(idx=post.inx, writer=post.writer, title=post.title, content=post.content, post_date=post.post_date)
#     except Exception as e:
#         return {'error': str(e), 'msg' : '존재하지 않는 게시글 번호입니다.'}
    
# def update_post(update_post: UpdatePost, db:Session):
#     post = db.query(Board).filter(and_(Board.idx == update_post.idx, Board.del_yn == 'Y')).first()
#     try:
#         if not post:
#             raise Exception("존재하지 않는 게시글 번호입니다.")

#         post.title = update_post.title
#         post.content = update_post.content
#         db.commit()
#         db.refresh(post)
#         return get_post(post.idx, db)
    
#     except Exception as e:
#         return str(e)
        
        
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models import Board
from routes.board_schema import NewPost, PostList, Post, UpdatePost

def insert_post(new_post: NewPost, db: Session):
    post = Board(
        writer = new_post.writer,
        title = new_post.title,
        content = new_post.content
    ) 
    db.add(post)
    db.commit()

    return post.idx


def list_all_post(db: Session):
    lists = db.query(Board).filter(Board.del_yn == 'Y').all()
    return [PostList(idx=row.idx, writer=row.writer, title=row.title, post_date=row.post_date) for row in lists]


def get_post(post_idx: int, db: Session):
    try:
        post = db.query(Board).filter(and_(Board.idx == post_idx, Board.del_yn == 'Y')).first()
        return Post(idx=post.idx, writer=post.writer, title=post.title, content=post.content, post_date=post.post_date)
    except Exception as e:
        return {'error': str(e), 'msg': '존재하지 않는 게시글 번호입니다.'}


def update_post(update_post: UpdatePost, db: Session):
    post = db.query(Board).filter(and_(Board.idx == update_post.idx, Board.del_yn == 'Y')).first()
    try:
        if not post:
            raise Exception("존재하지 않는 게시글 번호입니다.")
    
        post.title = update_post.title
        post.content = update_post.content
        db.commit()
        db.refresh(post)
        return get_post(post.idx, db)
    except Exception as e:
        return str(e)

def alter_del_yn(post_idx: int, db: Session):
    post = db.query(Board).filter(and_(Board.idx == post_idx, Board.del_yn == 'Y')).first()
    try:
        if not post:
            raise Exception("존재하지 않는 게시글 번호입니다")
    
        post.del_yn = 'N'
        db.commit()
        db.refresh(post)  
        return {'msg':'삭제가 완료되었습니다.'}
    except Exception as e:
        return str(e)

def delete_post(post_idx: int, db: Session):
    post = db.query(Board).filter(and_(Board.idx == post_idx, Board.del_yn == 'Y')).first()
    try:
        if not post:
            raise Exception("존재하지 않는 게시글 번호입니다")
        db.delete(post)
        db.commit()
        return {'msg':'삭제가 완료되었습니다.'}
    
    except Exception as e:
        return str(e)