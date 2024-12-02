import { useQuery, useMutation } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useGetBoardQuery() {
  return useQuery({
    queryKey: [`board/read`],
    queryFn: () =>
      httpClient({
        method: 'get',
        url: `board/read`,
      }),
  });
}

export function usePostBardMutation() {
  return useMutation({
    mutationFn: (data) =>
      httpClient({
        method: 'post',
        url: '/board/create',
        data,
      }),
  });
}
