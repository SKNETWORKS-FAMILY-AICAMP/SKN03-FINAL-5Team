import { Box } from '@chakra-ui/react';
import Container from '../common/components/container';
import Header from '../common/components/header';
import Login from './components/login';
import React from 'react';
import { getParameterStore } from '../common/utils/getParameterStore';

async function LoginPage() {
  const KAKAO_REST_API_KEY = await getParameterStore(
    '/interviewdb-info/kakao/RESTAPI'
  );
  const KAKAO_REDIRECT_URI = await getParameterStore(
    '/interviewdb-info/kakao/KAKAO_REDIRECT_URI'
  );

  return (
    <Container>
      <Header />
      <Box
        height="calc(100vh - 300px)"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Login
          KAKAO_REST_API_KEY={KAKAO_REST_API_KEY}
          KAKAO_REDIRECT_URI={KAKAO_REDIRECT_URI}
        />
      </Box>
    </Container>
  );
}

export default LoginPage;
