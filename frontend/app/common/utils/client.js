import { HttpError } from './HttpError';
import axios from 'axios';
import { getCookie, setCookie } from 'cookies-next';
import { useRouter } from 'next/navigation';

const developmentApiUrl =
  process.env['API_URL_DEVELOPMENT'] || 'http://127.0.0.1:8000';
const productionApiUrl =
  process.env['API_URL_PRODUCTION'] || 'https://unaitit.com';

const refreshTokenCookieName = 'unailit_refresh-token';
const accessTokenCookieName = 'unailit_access-token';

export const instance = axios.create({
  baseURL:
    process.env.NODE_ENV === 'production'
      ? productionApiUrl
      : developmentApiUrl,
});

let refreshTokenFailedCallback = () => {
  console.log('Refresh token failed. Please set a callback function.');
};

export const setRefreshTokenFailedCallback = (callback) => {
  refreshTokenFailedCallback = callback;
};

instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = getCookie(refreshTokenCookieName);
        const response = await axios.post(
          `${instance.defaults.baseURL}/refresh`,
          null,
          {
            params: { refresh_token: refreshToken },
          }
        );
        const { access_token, refresh_token } = response.data;

        setCookie(refreshTokenCookieName, refresh_token, {
          maxAge: 60 * 60 * 24 * 1,
          sameSite: 'lax',
        });
        setCookie(accessTokenCookieName, access_token, {
          maxAge: 1 * 60,
          sameSite: 'lax',
        });
        setBearerAuthorizationAtHttpClient(access_token);
        return instance(originalRequest);
      } catch (refreshError) {
        console.log('err');
        refreshTokenFailedCallback();
        throw new HttpError('세션이 만료되었습니다. 다시 로그인해주세요.', 401);
      }
    }
    return Promise.reject(error);
  }
);

export function httpClient(config) {
  return instance(config)
    .then((res) => {
      return res.data;
    })
    .catch((err) => {
      if (err instanceof HttpError) {
        throw err;
      }
      throw new HttpError(
        err?.response?.data?.message || '알 수 없는 오류가 발생했습니다.',
        err.response?.status || 400
      );
    });
}

export function setBearerAuthorizationAtHttpClient(token) {
  instance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}
