from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from datetime import datetime
import os
from database_utils import save_report_to_db
def get_client():
    return ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

# ChatOpenAI 인스턴스 생성
chat = get_client()

def generate_report(evaluation_results: List[Dict], db_session) -> Dict:
    """
    총평을 생성하고 보고서 데이터를 반환합니다.

    Args:
        evaluation_results (List[Dict]): 평가 결과 데이터.

    Returns:
        Dict: 보고서 데이터.
    """
    # 평가 데이터 정리
    detail_feedback = [{"question": result["question"], "answer":result["answer"], "feedback": result["feedback"]} for result in evaluation_results]
    average_score = round(sum(result["score"] for result in evaluation_results) / len(evaluation_results), 2)

    # GPT 모델 프롬프트 생성
    prompt = (
        "다음은 면접 결과입니다.\n"
        "질문과 피드백을 기반으로 강점, 약점, 한줄평을 작성해 주세요.\n\n"
        "면접 결과:\n"
    )
    for result in evaluation_results:
        prompt += f"질문: {result['question']}\n답변: {result['answer']}\n피드백: {result['feedback']}\n\n"
    prompt += (
        "강점:\n- 주요 강점 3가지를 작성해 주세요.\n\n"
        "약점:\n- 주요 약점 3가지를 작성해 주세요.\n\n"
        "한줄평:\n- 사용자를 위한 한줄평을 작성해 주세요."
    )

    # GPT 모델 요청
    try:
        response = chat.invoke([SystemMessage(content=prompt)])
        feedback = response.content.strip()
    except Exception as e:
        print(f"Error generating final feedback: {e}")
        feedback = "오류 발생"

    # 보고서 데이터 구성
    report_data = {
        "interview_id": evaluation_results[0]["interview_id"],  # 동일 인터뷰 ID 사용
        "strength": "강점 없음" if "강점" not in feedback else feedback.split("약점")[0].strip(),
        "weakness": "약점 없음" if "약점" not in feedback else feedback.split("한줄평")[0].split("약점")[1].strip(),
        "ai_summary": "한줄평 없음" if "한줄평" not in feedback else feedback.split("한줄평")[1].strip(),
        "report_score": average_score,
        "detail_feedback": detail_feedback,
        "report_created": datetime.now(),
        "attitude_feedback": "개발중"
    }

    save_report_to_db(report_data, db_session)

    return report_data
