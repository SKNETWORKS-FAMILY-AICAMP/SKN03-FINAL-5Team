from typing import Dict, List
import sys
import os

from typing import Dict, List

def collect_answers(
    answers_from_frontend: List[Dict],
    questions: List[Dict]
) -> List[Dict]:
    """
    질문과 프론트엔드에서 전달된 답변을 매핑 (DB 저장 없이).
    
    Args:
        answers_from_frontend (List[Dict]): 프론트에서 받은 답변 리스트
        questions (List[Dict]): 생성된 질문 리스트
        
    Returns:
        List[Dict]: 질문과 답변이 매핑된 데이터 리스트
    """
    print(f"answers_from_frontend: {answers_from_frontend}")
    print(f"questions: {questions}")

    if not isinstance(answers_from_frontend, list):
        raise ValueError("answers_from_frontend must be a list of dictionaries.")

    if not all(isinstance(q, dict) for q in questions):
        raise ValueError("questions must be a list of dictionaries.")

    mapped_answers = []

    for question in questions:
        # `job_question`을 기준으로 답변 매핑
        question_text = question.get("job_question", "Unknown question")
        model_answer = question.get("job_solution", "No ideal answer provided")
        interview_id = question.get("interview_id", 00)
        # 프론트엔드에서 전달된 답변 매핑
        answer = next(
            (a["answer"] for a in answers_from_frontend if a.get("question") == question_text),
            None
        )

        # 답변이 없을 경우 샘플 답변 생성
        if not answer:
            print(f"Warning: No answer found for question: {question_text}. Generating sample answer.")
            answer = f"Sample answer for question: {question_text[:30]}..."

        # 매핑된 데이터 저장
        mapped_data = {
            "interview_id" : interview_id,
            "question": question_text,
            "answer": answer,
            "model_answer": model_answer,
        }
        mapped_answers.append(mapped_data)

    print("Answers successfully mapped (DB storage deferred).")
    return mapped_answers
