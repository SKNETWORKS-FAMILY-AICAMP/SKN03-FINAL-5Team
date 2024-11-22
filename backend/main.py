from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import speech
import io
import subprocess

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
