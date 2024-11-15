'use client';

import { Box, Flex } from '@chakra-ui/react';
import WebcamComponent from './components/webcam';
import Header from '../common/components/header';
import StepComponent from './components/stepComponent';

function InterviewPage() {
  return (
    <Box>
      <Header />
      <Flex justify={'space-around'}>
        <WebcamComponent />
        <StepComponent />
      </Flex>
    </Box>
  );
}

export default InterviewPage;
