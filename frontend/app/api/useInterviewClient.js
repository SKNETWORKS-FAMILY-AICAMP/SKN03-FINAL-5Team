import { useQuery, useMutation } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useGetQuestionMutation() {
  return useMutation({
    mutationFn: () =>
      httpClient({
        method: 'post',
        url: '/generate_question',
        data: ['python', 'java', 'react'],
      }),
  });
}

export function usePostEvaluationMutation() {
  return useMutation({
    mutationFn: (data) =>
      httpClient({
        method: 'post',
        url: '/evaluate_answers',
        data: data,
      }),
  });
}
