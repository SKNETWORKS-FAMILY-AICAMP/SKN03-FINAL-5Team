import React, { useEffect, useState } from 'react';
import { useRefresh } from '@/app/api/useRefresh'; // 리프레시 뮤테이션 훅
import { hasCookie, getCookie } from 'cookies-next';
import { useUserData } from '@/app/api/useUserData';
import { Center, Spinner, VStack } from '@chakra-ui/react';

const refreshTokenCookieName = 'unailit_refresh-token';

export function UserProvider({ children }) {
  const { userLogin } = useUserData();

  const [isUserLoaded, setIsUserLoaded] = useState(false);
  const {
    mutate: refresh,
    data: refreshData,
    error: refreshError,
  } = useRefresh();

  const initializeUserSession = () => {
    if (hasCookie(refreshTokenCookieName)) {
      const refreshTokenFromCookie = getCookie(refreshTokenCookieName);
      if (typeof refreshTokenFromCookie !== 'string') {
        throw new Error('유저 세션 초기화 도중 문제가 발생했습니다.');
      }
      refresh({ refresh_token: refreshTokenFromCookie });
    } else {
      setIsUserLoaded(true);
    }
  };

  useEffect(() => {
    initializeUserSession();
  }, []);

  useEffect(() => {
    if (refreshData) {
      userLogin({
        accessToken: refreshData.user.access_token,
        refreshToken: refreshData.user.refresh_token,
      });
      setIsUserLoaded(true);
    }
  }, [refreshData]);

  return (
    <>
      {isUserLoaded ? (
        children
      ) : (
        <Center height="100vh">
          <VStack spacing={4}>
            <Spinner size="xl" color="blue.500" thickness="4px" />
          </VStack>
        </Center>
      )}
    </>
  );
}
