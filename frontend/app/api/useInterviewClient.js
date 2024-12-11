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

export function useGetInterviewLogQuery(interview_id) {
  return useQuery({
    queryKey: [`/interviews/${interview_id}/questions`],
    queryFn: () =>
      httpClient({
        method: 'get',
        url: `/interviews/${interview_id}/questions`,
      }),
    enabled: !!interview_id,
  });
}

export function useGetInterviewReport(interview_id) {
  return useQuery({
    queryKey: [`/interviews/${interview_id}/report`],
    queryFn: () =>
      httpClient({
        method: 'get',
        url: `/interviews/${interview_id}/report`,
      }),
    enabled: !!interview_id,
  });
}
