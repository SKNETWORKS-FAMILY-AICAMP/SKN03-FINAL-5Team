from fastapi import APIRouter, HTTPException
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

kakao_client_id = os.getenv('KAKAO_CLIENT_ID')
kakao_redirect_uri = os.environ.get('KAKAO_REDIRECT_URI')


@router.get("/login/oauth2/code/kakao")
async def kakao_callback(code: str):
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
    
    return {"user_info": user_info}