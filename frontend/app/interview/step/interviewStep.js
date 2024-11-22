import { Box, Flex, Button, Text } from '@chakra-ui/react';
import React, { useState, useEffect } from 'react';
import WebcamComponent from '../components/webcam';
import ChatComponent from '../components/chatComponent';

const InterviewStep = ({ setCurrentStep }) => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [timers, setTimers] = useState([]); // 각 질문에 대한 타이머 배열

  const allQuestions = [
    '파이썬에서 매직매소드를 로직에 구현한 경험에 대해 말해보세요',
    '파이썬에서 데이터 분석을 위해 주로 쓰는 모듈에 대해 설명해보세요.',
    '파이썬에서 가장 큰 값을 리턴하는 함수를 설명해주세요',
  ];

  const nextStep = () => {
    setCurrentStep((prevSteps) => prevSteps + 1);
  };

  useEffect(() => {
    setTimers(Array(allQuestions.length).fill(10));
    const questionInterval = setInterval(() => {
      if (currentQuestionIndex < allQuestions.length) {
        setQuestions((prevQuestions) => [
          ...prevQuestions,
          allQuestions[currentQuestionIndex],
        ]);
        setCurrentQuestionIndex((prevIndex) => prevIndex + 1);
      } else {
        clearInterval(questionInterval); // 모든 질문이 추가되면 인터벌 종료
      }
    }, 10000);

    return () => clearInterval(questionInterval); // 컴포넌트 언마운트 시 인터벌 정리
  }, [currentQuestionIndex]);

  useEffect(() => {
    if (currentQuestionIndex < allQuestions.length) {
      const countdownInterval = setInterval(() => {
        setTimers((prevTimers) => {
          const newTimers = [...prevTimers];
          if (newTimers[currentQuestionIndex] > 0) {
            newTimers[currentQuestionIndex] -= 1;
          } else {
            clearInterval(countdownInterval);
            if (currentQuestionIndex < allQuestions.length - 1) {
              setCurrentQuestionIndex((prevIndex) => prevIndex + 1);
              newTimers[currentQuestionIndex + 1] = 10;
            }
          }
          return newTimers;
        });
      }, 1000);

      return () => clearInterval(countdownInterval);
    }
  }, [currentQuestionIndex]);

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
        <Box minW={'40%'}>
          <Box
            background={'#DFE2FB'}
            h={'450px'}
            p={'40px 0'}
            overflowY={'scroll'}
          >
            <Text ml={'20px'} fontSize='lg' color='gray.600'>
              {timers[currentQuestionIndex] > 0
                ? `다음 질문까지 남은 시간: ${Math.floor(timers[currentQuestionIndex] / 60)}:${(timers[currentQuestionIndex] % 60).toString().padStart(2, '0')}`
                : '끝!'}
            </Text>
            {questions.map((item, index) => (
              <Box m={'20px 0'} key={index}>
                <Flex alignItems={'center'} ml={'5px'}>
                  <ChatComponent index={index} question={item} />
                </Flex>
              </Box>
            ))}
          </Box>
          <Button
            w={'100%'}
            h={'100px'}
            background={'#DFE2FB'}
            fontFamily={'inter'}
            mt={'30px'}
            onClick={nextStep}
          >
            면접 완료
          </Button>
        </Box>
      </Flex>
    </Box>
  );
};

export default InterviewStep;
