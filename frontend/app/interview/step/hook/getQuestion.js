import { useState, useEffect } from 'react';
import { useGetQuestionMutation } from '@/app/api/useInterviewClient';
import { useAtom } from 'jotai';
import {
  questionListAtom,
  questionAnswerListAtom,
  interviewIdAtom,
} from '../atom/interviewAtom';

export const useFetchQuestion = () => {
  const [questionList, setQuestionList] = useAtom(questionListAtom);
  const [questionAnswerList, setQuestionAnswerList] = useAtom(
    questionAnswerListAtom
  );
  const [interviewId, setInterviewId] = useAtom(interviewIdAtom);

  const {
    mutate: getQuestion,
    data: questionData,
    isError: QuestionError,
  } = useGetQuestionMutation();
  const [hasCalledGetQuestion, setHasCalledGetQuestion] = useState(false);

  useEffect(() => {
    if (!hasCalledGetQuestion) {
      getQuestion();
      setHasCalledGetQuestion(true);
    }
  }, [hasCalledGetQuestion, getQuestion]);

  useEffect(() => {
    if (questionData && questionData.questions) {
      console.log(questionData);
      const jobQuestions = questionData.questions.map((q) => q.job_question);
      const jobSolutions = questionData.questions.map((q) => q.job_solution);
      const interviewId = questionData.interview_id;
      setQuestionList(jobQuestions);
      setQuestionAnswerList(jobSolutions);
      setInterviewId(interviewId);
    }
  }, [questionData]);

  return { questionList, questionAnswerList, interviewId };
};
