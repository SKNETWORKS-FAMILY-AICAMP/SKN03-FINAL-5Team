import { usePostEvaluationMutation } from '@/app/api/useInterviewClient';
import { useEffect, useState } from 'react';

export const useFetchAnswer = () => {
  const [isLoading, setLoading] = useState(false);
  const {
    mutate: getAnswer,
    data: answer,
    isError: answerError,
    isPending: getAnswerLoading,
  } = usePostEvaluationMutation();

  const getAnswerFunction = (data) => {
    getAnswer(data);
  };

  useEffect(() => {
    if (getAnswerLoading == true) {
      setLoading(true);
    } else {
      setLoading(false);
    }
  }, [getAnswerLoading]);

  return { getAnswerFunction, isLoading };
};
