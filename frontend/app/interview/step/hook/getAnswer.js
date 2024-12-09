import { usePostEvaluationMutation } from '@/app/api/useInterviewClient';
import { useEffect } from 'react';

export const useFetchAnswer = () => {
  const {
    mutate: getAnswer,
    data: answer,
    isError: answerError,
  } = usePostEvaluationMutation();

  const getAnswerFunction = (data) => {
    console.log(data);
    getAnswer(data);
  };

  return { getAnswerFunction };
};
