from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from .database_utils import update_question_in_db
from .prompt import evaluation_prompt
import os
import pandas as pd
from typing import List, Dict


model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

def get_client():
    return ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY")
        )

# ChatOpenAI 인스턴스 생성
chat = get_client()

def evaluate_answer(interview_id, question, answer, model_answer, model):
    if not answer:
        return {
            "interview_id": interview_id,
            "question": question,
            "answer": "",
            "model_answer": model_answer,
            "feedback": "무응답",
            "score": 0.0,
            "cosine_similarity": 0.0,
        }

    
    question_embedding = model.encode(question)
    answer_embedding = model.encode(answer)
    model_answer_embedding = model.encode(model_answer)

    cosine_sim = cosine_similarity([answer_embedding], [model_answer_embedding])[0][0]
    score = round(cosine_sim * 100, 2)


    feedback_prompt = evaluation_prompt(answer, model_answer)
    feedback_response = chat.invoke([SystemMessage(content=feedback_prompt)])
    feedback_full = feedback_response.content.strip()

    # "피드백"으로 시작하는 부분만 추출
    feedback = ""
    for line in feedback_full.splitlines():
        if line.startswith("피드백"):
            feedback = line.replace("피드백:", "", 1).strip()  # "피드백:" 제거 및 양쪽 공백 제거
            break

    if not feedback:
        feedback = "피드백을 위한 데이터가 부족합니다."


    return {
        "question":question,
        "answer":answer,
        "model_answer":model_answer,
        "interview_id":interview_id,
        "feedback": feedback,
        "score": score,
        "cosine_similarity": cosine_sim,
    }





