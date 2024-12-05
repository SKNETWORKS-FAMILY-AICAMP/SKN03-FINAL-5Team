from fastapi import APIRouter, File, UploadFile, HTTPException
from google.cloud import speech
import subprocess
from util.get_parameter import get_parameter
router = APIRouter()





def convert_webm_to_flac(webm_content):
    process = subprocess.Popen(['ffmpeg', '-i', 'pipe:0', '-f', 'flac', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    flac_content, stderr = process.communicate(input=webm_content)
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode()}")
    return flac_content

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    account_key = get_parameter("/gcp/service-account-key")

        # JSON 문자열을 Python dict로 변환
    service_account_info = json.loads(account_key)

    # Google Cloud Speech-to-Text 클라이언트 생성
    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    client = speech.SpeechClient(credentials=credentials)
    webm_content = await audio.read()
    flac_content = convert_webm_to_flac(webm_content)

    audio = speech.RecognitionAudio(content=flac_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=48000,
        language_code="ko-KR",
    )

    response = client.recognize(config=config, audio=audio)
    transcript = "".join(result.alternatives[0].transcript for result in response.results)

    return {"transcript": transcript}