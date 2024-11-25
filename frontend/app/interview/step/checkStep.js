'use client';

import { Box, Flex, Button } from '@chakra-ui/react';
import WebcamComponent from '../components/webcam';
import StepComponent from '../components/stepComponent';
import 'regenerator-runtime/runtime';
import React, { useState } from 'react';

const CheckStep = ({ setCurrentStep }) => {
  const nextStep = () => {
    setCurrentStep((prevSteps) => prevSteps + 1);
  };

  return (
    <Box>
      <Flex justify={'space-around'} mb={'20px'}>
        <Box>
          <WebcamComponent />
          <Box
            background={'#DFE2FB'}
            h={'100px'}
            minW={'100%'}
            mt={'30px'}
          ></Box>
        </Box>
        <Box>
          <StepComponent />
          <Button
            w={'100%'}
            h={'100px'}
            background={'#DFE2FB'}
            fontFamily={'inter'}
            mt={'30px'}
            onClick={nextStep}
          >
            다음으로
          </Button>
        </Box>
      </Flex>
    </Box>
  );
};

export default CheckStep;
