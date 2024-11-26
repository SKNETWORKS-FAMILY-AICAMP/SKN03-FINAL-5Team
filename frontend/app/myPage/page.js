import Container from '../common/components/containers';
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
