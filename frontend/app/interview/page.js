'use client';

import { Box, Flex, Button } from '@chakra-ui/react';
import WebcamComponent from './components/webcam';
import Header from '../common/components/header';
import StepComponent from './components/stepComponent';
import 'regenerator-runtime/runtime';
import React, { useState } from 'react';
import Dictaphone from './components/dictaphone';
import StepProgress from '../common/components/progress';
import UploadStep from './step/uploadStep';
import Container from '../common/components/Container';
import CheckStep from './step/checkStep';
import InterviewStep from './step/interviewStep';

const StepRenderer = ({ steps, setCurrentStep }) => {
  switch (steps) {
    case 1:
      return <CheckStep setCurrentStep={setCurrentStep} />;
    case 2:
      return <UploadStep setCurrentStep={setCurrentStep} />;
    case 3:
      return <InterviewStep setCurrentStep={setCurrentStep} />;
    default:
      return null; // 또는 기본 컴포넌트를 렌더링할 수 있습니다
  }
};

function InterviewPage() {
  const [steps, setSteps] = useState([1, 2, 3]);
  const [currentStep, setCurrentStep] = useState(1);

  return (
    <Box>
      <Container>
        <Header />
        <StepProgress steps={steps} currentStep={currentStep} />
        <StepRenderer steps={currentStep} setCurrentStep={setCurrentStep} />
      </Container>
    </Box>
  );
}

export default InterviewPage;
