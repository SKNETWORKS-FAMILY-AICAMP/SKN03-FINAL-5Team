'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

const KakaoCallbackPage = () => {
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
        console.log(res.data);
        router.replace('/register');
      }
    } catch (error) {
      console.error('Login failed:', error);
      router.replace('/');
    }
  };

  return null;
};

export default KakaoCallbackPage;
