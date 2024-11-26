'use client';
import { Box, VStack, Link, Text, Image, Flex, Spacer } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import React from 'react';

const MotionBox = motion(Box);

const KakaoLoginButton = () => {
  const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=${process.env.NEXT_PUBLIC_KAKAO_REST_API_KEY}&redirect_uri=${process.env.NEXT_PUBLIC_KAKAO_REDIRECT_URI}&scope=profile_nickname`;

  return (
    <Link href={KAKAO_AUTH_URL} _hover={{ opacity: 0.8 }}>
      <Box
        as="button"
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg="transparent"
        border="none"
        w={'300px'}
      >
        <Image src="/kakao_login.png" alt="카카오 로그인" />
      </Box>
    </Link>
  );
};

const Login = () => {
  return (
    <Flex direction="column" minHeight="100vh">
      <Spacer />
      <VStack spacing={8} align="center" mb={10}>
        <Text fontSize="4xl" fontWeight="bold">
          로그인
        </Text>
        <Text fontSize="xl" color="#0066FF">
          당신을 더욱 빛나게 성장시킬 Unail,IT
        </Text>
        <KakaoLoginButton />
        <Text fontSize="sm" color="gray.500">
          로그인하여 다양한 기능을 이용해보세요
        </Text>
      </VStack>
      <Spacer />
      <Flex
        as="footer"
        justifyContent="center"
        p={5}
        borderTop="1px"
        borderColor="gray.200"
      >
        <Link href="/terms" mr={4} color="gray.500">
          이용약관
        </Link>
        <Link href="/privacy" color="gray.500">
          개인정보처리방침
        </Link>
      </Flex>
    </Flex>
  );
};

export default Login;
