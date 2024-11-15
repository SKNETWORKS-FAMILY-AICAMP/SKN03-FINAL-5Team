import os
import pyaudio
import time
import soundfile as sf
import numpy as np
from google.cloud import speech
from dotenv import load_dotenv

# .env 파일의 환경 변수 로드
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# 오디오 설정
SAMPLE_RATE = 16000  # 샘플링 속도 (Hz)
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms 동안 수집할 오디오 데이터 크기
SILENCE_THRESHOLD = 4 * 1000  # 4초 (밀리초 단위)
INITIAL_SILENCE_GRACE_PERIOD = 10 * 1000  # 최초 10초간 무음 허용 (밀리초 단위)

def get_next_filename(prefix="recorded_audio", ext="flac"):
    """순차적으로 증가하는 파일명을 생성합니다."""
    i = 1
    while os.path.exists(f"{prefix}_{i}.{ext}"):
        i += 1
    return f"{prefix}_{i}.{ext}"

def real_time_transcription():
    # Google Speech-to-Text API 클라이언트 생성
    client = speech.SpeechClient()

    # 오디오 스트림 설정
    audio_interface = pyaudio.PyAudio()
    stream = audio_interface.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=SAMPLE_RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK_SIZE)

    # 녹음 데이터를 저장할 배열
    audio_data_frames = []

    # 초기화
    start_time = time.time() * 1000  # 스트리밍 시작 시간 기록
    last_sound_time = start_time  # 마지막 소리가 감지된 시간
    final_result = ""  # 최종 결과를 저장할 변수
    last_interim = ""  # 중간 결과를 저장할 변수 (중복 방지)

    # 스트리밍 요청 생성 함수
    def request_stream():
        nonlocal last_sound_time
        while True:
            data = stream.read(CHUNK_SIZE)
            audio_data = np.frombuffer(data, dtype=np.int16)
            audio_data_frames.append(audio_data)  # 녹음 데이터 누적

            # 소리가 감지되는지 확인 (무음 기준)
            if np.max(np.abs(audio_data)) > 500:  # 임계값 이상인 경우 소리 감지
                last_sound_time = time.time() * 1000
            
            # 스트리밍 시작 후 10초가 지난 경우에만 무음 상태를 체크
            if (time.time() * 1000) - start_time > INITIAL_SILENCE_GRACE_PERIOD:
                # 4초 이상 무음일 경우 스트리밍 종료
                if (time.time() * 1000) - last_sound_time > SILENCE_THRESHOLD:
                    print("4초 동안 무음 상태입니다. 스트리밍을 종료합니다.")
                    break
            
            yield speech.StreamingRecognizeRequest(audio_content=data)

    # Google STT 스트리밍 설정
    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            language_code="ko-KR",
        ),
        interim_results=True
    )

    # STT 결과를 순회하며 최종 텍스트 반환
    responses = client.streaming_recognize(streaming_config, request_stream())
    for response in responses:
        for result in response.results:
            transcript = result.alternatives[0].transcript

            # 중간(interim) 결과가 업데이트될 때마다 확인
            if not result.is_final:
                if transcript != last_interim:  # 중복 방지
                    print("Transcript (interim):", transcript)
                    last_interim = transcript  # 마지막 중간 결과 업데이트
            else:
                # 최종 텍스트 변환 결과가 발생한 시점에서 스트리밍 종료
                final_result = transcript
                print("Final Transcript (confirmed):", final_result)  # 각 최종 결과 확인

                # 스트림 종료
                stream.stop_stream()
                stream.close()
                audio_interface.terminate()

                # FLAC 파일로 녹음 데이터 저장
                output_filename = get_next_filename()
                sf.write(output_filename, np.concatenate(audio_data_frames), SAMPLE_RATE, format='FLAC')
                print(f"Recording saved as {output_filename}")
                
                return final_result  # 최종 결과 반환

    # 스트림 종료 시 예외 대비
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()




# 인터뷰 함수에서 이 함수를 여러 번 호출하면, 
# for 루프에 의해 매번 재실행될 수 있습니다.

# 함수 실행


# import os
# import pyaudio
# import time
# from google.cloud import speech
# import numpy as np
# from dotenv import load_dotenv

# # .env 파일의 환경 변수 로드
# load_dotenv()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
# # 오디오 설정
# SAMPLE_RATE = 16000  # 샘플링 속도 (Hz)
# CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms 동안 수집할 오디오 데이터 크기
# SILENCE_THRESHOLD = 4 * 1000  # 4초 (밀리초 단위)

# def real_time_transcription():
#     # Google Speech-to-Text API 클라이언트 생성
#     client = speech.SpeechClient()

#     # 오디오 스트림 설정
#     audio_interface = pyaudio.PyAudio()
#     stream = audio_interface.open(format=pyaudio.paInt16,
#                                 channels=1,
#                                 rate=SAMPLE_RATE,
#                                 input=True,
#                                 frames_per_buffer=CHUNK_SIZE)

#     # 마지막으로 소리가 감지된 시간을 초기화
#     last_sound_time = time.time() * 1000
#     final_result = ""  # 최종 결과를 저장할 변수
#     last_interim = ""  # 중간 결과를 저장할 변수 (중복 방지)

#     # 스트리밍 요청 생성 함수
#     def request_stream():
#         nonlocal last_sound_time
#         while True:
#             data = stream.read(CHUNK_SIZE)
#             audio_data = np.frombuffer(data, dtype=np.int16)
            
#             # 소리가 감지되는지 확인 (무음 기준)
#             if np.max(np.abs(audio_data)) > 500:  # 임계값 이상인 경우 소리 감지
#                 last_sound_time = time.time() * 1000
            
#             # 4초 이상 무음일 경우 스트리밍 종료
#             if (time.time() * 1000) - last_sound_time > SILENCE_THRESHOLD:
#                 print("4초 동안 무음 상태입니다. 스트리밍을 종료합니다.")
#                 break
            
#             yield speech.StreamingRecognizeRequest(audio_content=data)

#     # Google STT 스트리밍 설정
#     streaming_config = speech.StreamingRecognitionConfig(
#         config=speech.RecognitionConfig(
#             encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#             sample_rate_hertz=SAMPLE_RATE,
#             language_code="ko-KR",
#         ),
#         interim_results=True
#     )

#     # STT 결과를 순회하며 최종 텍스트 축적
#     responses = client.streaming_recognize(streaming_config, request_stream())
#     for response in responses:
#         for result in response.results:
#             transcript = result.alternatives[0].transcript

#             # 중간(interim) 결과가 업데이트될 때마다 확인
#             if not result.is_final:
#                 if transcript != last_interim:  # 중복 방지
#                     print("Transcript (interim):", transcript)
#                     last_interim = transcript  # 마지막 중간 결과 업데이트
#             else:
#                 # 최종 텍스트 변환 결과를 final_result에 누적
#                 final_result += transcript + " "
#                 print("Final Transcript (confirmed):", transcript)  # 각 최종 결과 확인

#     # 스트림 종료
#     stream.stop_stream()
#     stream.close()
#     audio_interface.terminate()

#     print("\nComplete Final Transcript:", final_result.strip())  # 전체 최종 결과 확인
#     return final_result.strip()  # 전체 결과를 반환

# real_time_transcription()


