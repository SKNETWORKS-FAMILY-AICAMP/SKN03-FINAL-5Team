import { Box, Flex, Button, Text, Spinner } from '@chakra-ui/react';
import React, { useState, useEffect } from 'react';
import WebcamComponent from '../components/webcam';
import ChatComponent from '../components/chatComponent';
import SpeechToText from '../components/getaudio';
import { useFetchQuestion } from './hook/getQuestion';

const InterviewStep = React.memo(() => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [timers, setTimers] = useState({ countdown: 20, recording: 10 });
  const [questions, setQuestions] = useState([]);
  const [isInterviewComplete, setIsInterviewComplete] = useState(false);
  const [interviewData, setInterviewData] = useState([]);
  const [loading, setLoading] = useState(true);

  const { questionList } = useFetchQuestion();

  useEffect(() => {
    if (questionList.length > 0) {
      const questionsArray = questionList.map((item) => item.question);
      setQuestions(questionsArray);
      setLoading(false);
      startTimers();
    }
  }, [questionList]);

  useEffect(() => {
    console.log(questionList);
  }, [questionList]);

  const startTimers = () => {
    setTimers({ countdown: 20, recording: 10 });
    setIsRecording(false);
  };

  const handleTranscriptUpdate = (newTranscript) => {
    setInterviewData((prev) => [
      ...prev,
      { question: questions[currentQuestionIndex], answer: newTranscript },
    ]);
  };

  // 타이머 및 인터뷰 로직
  useEffect(() => {
    if (loading || isInterviewComplete) return;

    if (timers.countdown > 0 && !isRecording) {
      const countdownInterval = setInterval(() => {
        setTimers((prev) => ({ ...prev, countdown: prev.countdown - 1 }));
      }, 1000);
      return () => clearInterval(countdownInterval);
    } else if (timers.countdown === 0 && !isRecording) {
      setIsRecording(true);
      setTimers((prev) => ({ ...prev, recording: 10 }));
    }
  }, [timers.countdown, isRecording, isInterviewComplete, loading]);

  useEffect(() => {
    if (loading || isInterviewComplete) return;

    if (timers.recording > 0 && isRecording) {
      const recordingInterval = setInterval(() => {
        setTimers((prev) => ({ ...prev, recording: prev.recording - 1 }));
      }, 1000);
      return () => clearInterval(recordingInterval);
    } else if (timers.recording === 0 && isRecording) {
      setIsRecording(false);
      nextQuestion();
    }
  }, [timers.recording, isRecording, isInterviewComplete, loading]);

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
      setTimers({ countdown: 10, recording: 10 });
    } else {
      setIsInterviewComplete(true);
    }
  };

  const onSubmitAnswer = () => {
    console.log(interviewData);
  };

  return (
    <Box>
      <Flex justify={'space-around'} mb={'20px'}>
        <Box>
          <WebcamComponent />
          <Box background={'#DFE2FB'} h={'100px'} minW={'100%'} mt={'30px'}>
            <SpeechToText
              isRecording={isRecording}
              onTranscriptUpdate={handleTranscriptUpdate}
            />
          </Box>
        </Box>
        <Box minW={'40%'} w={'40%'}>
          <Box
            background={'#DFE2FB'}
            h={'450px'}
            p={'40px 0'}
            overflowY={'scroll'}
          >
            {loading ? (
              <Flex justify="center" align="center" h="100%">
                <Spinner size="xl" color="blue.500" thickness="4px" />
                <Text ml={3}>로딩 중...</Text>
              </Flex>
            ) : (
              <>
                <Text ml={'20px'} fontSize="lg" color="gray.600">
                  {isInterviewComplete
                    ? '모든 질문이 완료되었습니다.'
                    : isRecording
                      ? `녹음 중: ${timers.recording}초 남음`
                      : `답변 준비 시간: ${timers.countdown}초`}
                </Text>
                <Box m={'20px'}>
                  <Flex alignItems={'center'} ml={'5px'}>
                    <ChatComponent
                      index={currentQuestionIndex}
                      question={questions[currentQuestionIndex]}
                    />
                  </Flex>
                </Box>
              </>
            )}
          </Box>
          <Button
            w={'100%'}
            h={'100px'}
            background={'#DFE2FB'}
            fontFamily={'inter'}
            mt={'30px'}
            onClick={onSubmitAnswer}
            isDisabled={
              !isInterviewComplete && (isRecording || timers.countdown > 0)
            }
          >
            {isInterviewComplete && interviewData.length === questions.length
              ? '면접 완료'
              : '진행중'}
          </Button>
        </Box>
      </Flex>
    </Box>
  );
});

export default InterviewStep;
