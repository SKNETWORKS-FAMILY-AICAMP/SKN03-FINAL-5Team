from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import speech
import io
import subprocess

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import get_user_by_kakao_id, create_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    client = speech.SpeechClient()

    # WebM을 FLAC으로 변환
    webm_content = await audio.read()
    flac_content = convert_webm_to_flac(webm_content)

    audio = speech.RecognitionAudio(content=flac_content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=48000,
        language_code="ko-KR",
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return {"transcript": transcript}

def convert_webm_to_flac(webm_content):
    # FFmpeg를 사용하여 WebM을 FLAC으로 변환
    ffmpeg_path = "/opt/homebrew/bin/ffmpeg"
    process = subprocess.Popen(['ffmpeg', '-i', 'pipe:0', '-f', 'flac', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    flac_content, stderr = process.communicate(input=webm_content)
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode()}")
    return flac_content

# 로그인 기능 추가
## 데이터베이스 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/login")
async def login():
    auth_url = f"{settings.KAKAO_AUTHORIZATION_URL}?client_id={settings.KAKAO_REST_API_KEY}&redirect_uri={settings.KAKAO_REDIRECT_URI}&response_type=code"
    return RedirectResponse(auth_url)

@app.get("/kakao/callback")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    # 카카오에서 토큰을 받아옴
    response = requests.post(
        settings.KAKAO_TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_REST_API_KEY,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'code': code
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="카카오 로그인에 실패했습니다.")

    # 카카오 API에서 사용자 정보 요청
    user_info_response = requests.get(
        settings.KAKAO_USER_INFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_response.json()

    kakao_id = user_info["id"]
    nickname = user_info["properties"]["nickname"]
    email = user_info.get("kakao_account", {}).get("email", None)

    # 사용자 정보가 데이터베이스에 있는지 확인
    db_user = get_user_by_kakao_id(db, kakao_id)
    if db_user:
        # 이미 존재하는 사용자 로그인
        return {"message": "로그인 성공", "user": db_user}
    else:
        # 새로운 사용자 등록
        new_user = create_user(db, kakao_id, nickname, email)
        return {"message": "회원가입 성공", "user": new_user}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



