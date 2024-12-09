import pandas as pd
from database_utils import save_answers_to_db
from typing import List

def process_answers(answers: List[str], questions_df: pd.DataFrame) -> pd.DataFrame:
    if len(answers) != len(questions_df):
        raise ValueError("답변의 개수가 질문 개수와 일치하지 않습니다.")

    # 답변 저장
    questions_df["job_answer"] = answers
    save_answers_to_db(questions_df)
    return questions_df
