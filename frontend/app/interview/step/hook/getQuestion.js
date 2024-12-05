import { useState, useEffect } from 'react';
import { useGetQuestionMutation } from '@/app/api/useInterviewClient';
import { useAtom } from 'jotai';
import { questionListAtom } from '../atom/interviewAtom';

export const useFetchQuestion = () => {
  const [questionList, setQuestionList] = useAtom(questionListAtom);

  const {
    mutate: getQuestion,
    data: question,
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
    if (question && question.length > 0) {
      setQuestionList(question);
    }
  }, [question]);

  return { questionList };
};
