'use client';

import { Box } from '@chakra-ui/react';
import WebcamComponent from './components/webcam';
import Header from '../common/components/header';

function InterviewPage() {
  return (
    <Box>
      <Header />
      <WebcamComponent />
    </Box>
  );
}

export default InterviewPage;
