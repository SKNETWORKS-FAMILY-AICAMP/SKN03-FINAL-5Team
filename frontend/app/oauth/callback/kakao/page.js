'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useUserData } from '@/app/api/useUserData';

const KakaoCallbackPage = () => {
  const { userLogin } = useUserData();

  const [code, setCode] = useState(null);
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URL(window.location.href).searchParams;
      const codeParam = urlParams.get('code');
      if (codeParam) {
        setCode(codeParam);
      }
    }
  }, []);

  useEffect(() => {
    if (code !== null) {
      kakaoLogin();
    }
  }, [code]);

  const kakaoLogin = async () => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/login/oauth/code/kakao?code=${code}`
      );
      if (res.status === 200 && res.data.message === '회원가입 필요') {
        router.replace('/register');
      }
      if (res.status === 200 && res.data.message === '로그인 성공') {
        userLogin({ accessToken: res.data.user.access_token });
        router.replace('/');
      }
    } catch (error) {
      console.error('Login failed:', error);
      router.replace('/');
    }
  };

  return null;
};

export default KakaoCallbackPage;
