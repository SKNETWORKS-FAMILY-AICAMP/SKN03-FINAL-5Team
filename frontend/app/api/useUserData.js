import { useCallback } from 'react';
import { deleteCookie, setCookie } from 'cookies-next';
import { useAtom } from 'jotai';
import { setBearerAuthorizationAtHttpClient } from '../common/utils/client';

import { accessTokenAtom, userProfileAtom } from '../atom/useUserAtom';

export const refreshTokenCookieName = 'unailit_refresh-token';

export function useUserData() {
  const [accessToken, setAccessToken] = useAtom(accessTokenAtom);
  const [userProfileData, setUserProfileData] = useAtom(userProfileAtom);

  const userLogin = useCallback(
    ({ accessToken }) => {
      setAccessToken(accessToken);
      setCookie(refreshTokenCookieName, accessToken, {
        maxAge: 60 * 60 * 24,
        sameSite: 'lax',
      });
      setBearerAuthorizationAtHttpClient(accessToken);
    },
    [setAccessToken]
  );

  const resetUser = useCallback(() => {
    setUserProfileData({
      userInfo: {
        name: '',
        email: '',
      },
    });
  }, [setUserProfileData]);

  const userLogout = useCallback(() => {
    setAccessToken('');
    deleteCookie(refreshTokenCookieName);
    resetUser();
  }, [setAccessToken]);

  return {
    isLoggedIn: accessToken && accessToken !== '' ? true : false,
    accessToken,
    userLogin,
    userLogout,
    setUserProfileData,
    userProfileData,
  };
}
