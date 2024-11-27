'use client';

import { useEffect, useState } from 'react';
import { useCookies } from 'react-cookie';
import { useRouter, usePathname } from 'next/navigation';
import { Spinner, Flex } from '@chakra-ui/react';

const UserGuard = ({ children }) => {
  const [cookies] = useCookies(['unailit_refresh-token']);
  const router = useRouter();
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const accessToken = cookies['unailit_refresh-token'];
    const unprotectedRoutes = ['/', '/about', '/login'];

    if (!accessToken && !unprotectedRoutes.includes(pathname)) {
      router.push('/login');
    } else {
      setIsLoading(false);
    }
  }, [cookies, router, pathname]);

  // 홈페이지와 about 페이지는 항상 children을 렌더링
  if (pathname === '/' || pathname === '/about') {
    return <>{children}</>;
  }

  if (isLoading && pathname !== '/login') {
    return (
      <Flex
        width="100vw"
        height="100vh"
        justifyContent="center"
        alignItems="center"
      >
        <Spinner
          thickness="4px"
          speed="0.65s"
          emptyColor="gray.200"
          color="blue.500"
          size="xl"
        />
      </Flex>
    );
  }

  return <>{children}</>;
};

export default UserGuard;
