import { useMutation } from '@tanstack/react-query';
import { httpClient } from '../common/utils/client';

export function useRefresh() {
  return useMutation({
    mutationFn: (data) =>
      httpClient({
        method: 'post',
        url: '/refresh',
        data,
      }),
  });
}