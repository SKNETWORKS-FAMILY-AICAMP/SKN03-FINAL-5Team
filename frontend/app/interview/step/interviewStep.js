import { Box, Flex, Button, Text } from '@chakra-ui/react';
import React, { useState, useEffect } from 'react';
import WebcamComponent from '../components/webcam';
import ChatComponent from '../components/chatComponent';
import SpeechToText from '../components/getaudio';

const InterviewStep = ({ setCurrentStep }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [timers, setTimers] = useState({ countdown: 10, recording: 10 });
  const [questions, setQuestions] = useState([]);
  const [isInterviewComplete, setIsInterviewComplete] = useState(false);

  const allQuestions = [
    '파이썬에서 매직매소드를 로직에 구현한 경험에 대해 말해보세요',
    '파이썬에서 데이터 분석을 위해 주로 쓰는 모듈에 대해 설명해보세요.',
    '파이썬에서 가장 큰 값을 리턴하는 함수를 설명해주세요',
  ];

  useEffect(() => {
    setQuestions([allQuestions[currentQuestionIndex]]);
  }, []);

  useEffect(() => {
    if (isInterviewComplete) return; 

    if (timers.countdown > 0 && !isRecording) {
      const countdownInterval = setInterval(() => {
        setTimers((prev) => ({ ...prev, countdown: prev.countdown - 1 }));
      }, 1000);
      return () => clearInterval(countdownInterval);
    } else if (timers.countdown === 0 && !isRecording) {
      setIsRecording(true);
      setTimers((prev) => ({ ...prev, recording: 10 }));
    }
  }, [timers.countdown, isRecording, isInterviewComplete]);

  useEffect(() => {
    if (isInterviewComplete) return; 

    if (timers.recording > 0 && isRecording) {
      const recordingInterval = setInterval(() => {
        setTimers((prev) => ({ ...prev, recording: prev.recording - 1 }));
      }, 1000);
      return () => clearInterval(recordingInterval);
    } else if (timers.recording === 0 && isRecording) {
      setIsRecording(false);
      nextQuestion();
    }
  }, [timers.recording, isRecording, isInterviewComplete]);

  const nextQuestion = () => {
    if (currentQuestionIndex < allQuestions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
      setQuestions((prev) => [...prev, allQuestions[currentQuestionIndex + 1]]);
      setTimers({ countdown: 10, recording: 10 });
    } else {
      setIsInterviewComplete(true);
      console.log('모든 질문 완료');
    }
  };

  return (
    <Box>
      <Flex justify={'space-around'} mb={'20px'}>
        <Box>
          <WebcamComponent />
          <Box background={'#DFE2FB'} h={'100px'} minW={'100%'} mt={'30px'}>
            <SpeechToText isRecording={isRecording} />
          </Box>
        </Box>
        <Box minW={'40%'}>
          <Box
            background={'#DFE2FB'}
            h={'450px'}
            p={'40px 0'}
            overflowY={'scroll'}
          >
            <Text ml={'20px'} fontSize="lg" color="gray.600">
              {isInterviewComplete
                ? '모든 질문이 완료되었습니다.'
                : isRecording
                  ? `녹음 중: ${timers.recording}초 남음`
                  : `답변 준비 시간: ${timers.countdown}초`}
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
            onClick={
              isInterviewComplete
                ? () => setCurrentStep((prev) => prev + 1)
                : nextQuestion
            }
            isDisabled={
              !isInterviewComplete && (isRecording || timers.countdown > 0)
            }
          >
            {isInterviewComplete ? '면접 완료' : '다음 질문으로 이동'}
          </Button>
        </Box>
      </Flex>
    </Box>
  );
};

export default InterviewStep;
