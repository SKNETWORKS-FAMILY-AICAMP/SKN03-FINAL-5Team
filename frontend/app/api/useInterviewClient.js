import { useQuery, useMutation } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useGetQuestionMutation() {
  return useMutation({
    mutationFn: () =>
      httpClient({
        method: 'post',
        url: '/generate_question',
        data: {
          tech_keywords: 'python, java, react',
          question_count: 0,
          max_questions: 5,
        },
      }),
  });
}
