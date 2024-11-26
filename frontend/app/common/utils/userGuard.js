'use client';
import { useEffect } from 'react';
import { useUserData } from '@/app/api/useUserData';
import { usePathname, useRouter } from 'next/navigation';

const UserGuard = ({ children }) => {
  const { isLoggedIn } = useUserData();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    console.log(pathname);
    if (!isLoggedIn && pathname !== '/' && pathname !== '/about') {
      router.replace('/login');
    }
  }, [isLoggedIn, pathname, router]);

  return <>{children}</>;
};

export default UserGuard;
