# routes/kakao.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import httpx
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from .crud import get_user_by_id, update_user
from models import User
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

kakao_client_id = os.getenv('KAKAO_CLIENT_ID')
kakao_redirect_uri = os.getenv('KAKAO_REDIRECT_URI')

ACCESS_TOKEN_EXPIRE_DAYS = 1  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days

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
        refresh_token = token_data.get("refresh_token")

        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        user_response = await client.get(user_info_url, headers=headers)
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        user_info = user_response.json()
        kakao_id = user_info['id'] 
        existing_user = get_user_by_id(db=db, id=str(kakao_id))
        
    if existing_user:
        # 기존 사용자 로그인 처리
        access_token_expiry = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        refresh_token_expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        update_user(db, existing_user.id, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_token_expiry": access_token_expiry,
            "refresh_token_expiry": refresh_token_expiry
        })
        
        response = JSONResponse(content={
            "message": "로그인 성공", 
            "user": {
                "name": existing_user.user_name, 
                "email": existing_user.user_email,
                "access_token": access_token,
                "refresh_token": refresh_token
            },
        })
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite='lax', expires=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 3600)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite='lax', expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
        return response
    
    # 회원가입이 필요한 경우
    return JSONResponse(content={
        "message": "회원가입 필요",
        "kakao_id": kakao_id,
        "name": user_info['properties']['nickname'],
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    })

@router.post("/refresh")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    body = await request.json()  # 요청의 바디를 JSON으로 파싱
    refresh_token = body.get("refresh_token")  # 바디에서 리프레시 토큰 가져오기

    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token not found")

    user = db.query(User).filter(User.refresh_token == refresh_token).first()
    if not user or user.refresh_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": kakao_client_id,
        "refresh_token": refresh_token,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to refresh token")

        token_data = response.json()
        new_access_token = token_data.get("access_token")
        new_refresh_token = token_data.get("refresh_token", refresh_token)

    # Update user with new tokens and expiry
    access_token_expiry = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    refresh_token_expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    update_user(db, user.id, {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "access_token_expiry": access_token_expiry,
        "refresh_token_expiry": refresh_token_expiry
    })

    response = JSONResponse(content={
        "message": "Token refreshed successfully", 
        "user": {
            "name": user.user_name, 
            "email": user.user_email,
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        },
    })
    
    # Set cookies for the new tokens
    response.set_cookie(key="access_token", value=new_access_token, httponly=True, secure=True, samesite='lax', expires=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 3600)
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, secure=True, samesite='lax', expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    
    return response