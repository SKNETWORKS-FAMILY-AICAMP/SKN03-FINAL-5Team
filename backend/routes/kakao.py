# routes/kakao.py
from fastapi import APIRouter, HTTPException, Depends
import httpx
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from .crud import get_user_by_id 
from models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

kakao_client_id = os.getenv('KAKAO_CLIENT_ID')
kakao_redirect_uri = os.getenv('KAKAO_REDIRECT_URI')

@router.get("/login/oauth/code/kakao")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    try:
        user_count = db.query(User).count()  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 연결 실패: {str(e)}")

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": kakao_client_id,
        "redirect_uri": kakao_redirect_uri,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        token_data = response.json()
        access_token = token_data.get("access_token")

        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        user_response = await client.get(user_info_url, headers=headers)
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        user_info = user_response.json()
        kakao_id = user_info['id'] 
        existing_user = get_user_by_id(db=db, id=str(kakao_id))
        
        if existing_user:
            return {"message": "로그인 성공", "user": {"name": existing_user.user_name, "email": existing_user.user_email, "access_token": access_token}}
        
        return {
            "message": "회원가입 필요",
            "kakao_id": kakao_id,
            "name": user_info['properties']['nickname'],  
        }