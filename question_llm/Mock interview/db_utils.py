from .models import Question, Report

def save_question(job_question, job_solution):
    """
    질문과 모범 답안을 저장합니다.
    """
    question = Question.objects.create(
        job_question=job_question,
        job_solution=job_solution
    )
    return question.id

def save_answer(question_id, job_answer, job_answer_score):
    """
    답변과 점수를 저장합니다.
    """
    question = Question.objects.get(id=question_id)
    question.job_answer = job_answer
    question.job_answer_score = job_answer_score
    question.save()

def save_report(strength, weakness, ai_summary, detail_feedback, report_score):
    """
    최종 보고서를 저장합니다.
    """
    Report.objects.create(
        strength=strength,
        weakness=weakness,
        ai_summary=ai_summary,
        detail_feedback=detail_feedback,
        report_score=report_score
    )
