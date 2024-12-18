# 레포트를 pdf로 설계
# generate_report는 다음과 같은 정보를 반환
# report_data = {
#             "interview_id": evaluation_results[0].get("interview_id"),
#             "strength": clean_text("강점 없음" if "강점" not in feedback else feedback.split("약점")[0].strip()),
#             "weakness": clean_text("약점 없음" if "약점" not in feedback else feedback.split("한줄평")[0].split("약점")[1].strip()),
#             "ai_summary": clean_text("한줄평 없음" if "한줄평" not in feedback else feedback.split("한줄평")[1].strip()),
#             "report_score": average_score,
#             "detail_feedback": str(detail_feedback),
# 
# 추가로 필요한정보
# interview tb의 interview_create
# interview_id에 대응되는 user id를 가져옴
# user_tb에서 user_id에 대응되는 user_name을 끌고옴
# 
# 결론
# 실제 report에 표시될 내용 
# = 이름(user_name), 인터뷰 시작시간(interview create), 강점(strength), 약점(weakness), 한줄평(ai_summary), 총점(report_score), 피드백(detail_feedback) 