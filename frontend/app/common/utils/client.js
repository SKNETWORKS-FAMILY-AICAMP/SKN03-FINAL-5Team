import { HttpError } from '@lio/shared/utils/http-client';
import axios, { AxiosResponse } from 'axios';

const developmentApiUrl =
  process.env['API_URL_DEVELOPMENT'] ?? 'https://localhost:3000/api';
const productionApiUrl =
  process.env['API_URL_PRODUCTION'] ?? 'https://unaitit/api';

export const instance = axios.create({
  baseURL:
    process.env['NEXT_PUBLIC_MODE'] === 'development'
      ? developmentApiUrl
      : productionApiUrl,
});

export function httpClient(...args) {
  return instance(...args)
    .then((res) => {
      return res.data;
    })
    .catch((err) => {
      throw new HttpError(
        err?.response?.data?.message ?? '알 수 없는 오류가 발생했습니다.',
        err.response?.status ?? 400
      );
    });
}

export function setBearerAuthorizationAtHttpClient(token) {
  instance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}
