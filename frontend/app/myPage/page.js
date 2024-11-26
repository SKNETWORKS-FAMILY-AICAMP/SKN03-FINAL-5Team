// 'use client'; // 클라이언트 컴포넌트 선언 필요

// import Container from '@/app/common/components/container';
// import Header from '@/common/components/header';
// import InterviewHistory from './components/interviewHistory';
// import SideNavigation from './components/navigation';
// import { Flex, Box } from '@chakra-ui/react';

import Container from '../common/components/container';
import Header from '../common/components/header';
import InterviewHistory from './components/interviewHistory';
import SideNavigation from './components/navigation';
import { Flex, Box } from '@chakra-ui/react';
import React from 'react';

function MyPages() {
  return (
    <Container>
      <Header />
      <Flex mt={'50px'} gap={'30px'}>
        <SideNavigation />
        <Box w={'70%'}>
          <InterviewHistory />
        </Box>
      </Flex>
    </Container>
  );
}

export default MyPages;
