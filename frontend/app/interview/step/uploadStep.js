import {
  Box,
  Button,
  Flex,
  HStack,
  Input,
  VStack,
  InputGroup,
  InputRightElement,
  Spinner,
} from '@chakra-ui/react';
import { FaUpload } from 'react-icons/fa';
import React, { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import {
  fileNameAtom,
  jobInterestAtom,
  desiredTraitsAtom,
  fileAtom,
} from '../atom/atom';
import { useFetchQuestion } from './hook/getQuestion';

const UploadStep = ({ setCurrentStep }) => {
  const [file, setFile] = useAtom(fileAtom);
  const [fileName, setFileName] = useAtom(fileNameAtom);
  const [jobInterest, setJobInterest] = useAtom(jobInterestAtom);
  const [desiredTraits, setDesiredTraits] = useAtom(desiredTraitsAtom);

  const [kakaoId, setKakaoId] = useState();
  const [requestData, setRequestData] = useState();

  useEffect(() => {
    const storedKakaoId = localStorage.getItem('id');
    if (storedKakaoId) {
      setKakaoId(storedKakaoId);
    }
  }, []);

  const {
    questionList,
    questionAnswerList,
    interviewId,
    isPending,
    getQuestionList,
  } = useFetchQuestion();

  useEffect(() => {
    if (requestData) {
      getQuestionList(requestData);
    }
  }, [requestData]);

  const nextStep = async () => {
    console.log(file, jobInterest, kakaoId);
    if (file && jobInterest !== '' && kakaoId) {
      setRequestData({
        resume: file,
        user_job: jobInterest,
        user_id: kakaoId,
      });
    }
    if (isPending === false && questionList.length !== 0) {
      setCurrentStep((prevSteps) => prevSteps + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep((prevStep) => prevStep - 1);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFileName(file.name);
      setFile(file);
    }
  };

  return (
    <Box w={'100%'}>
      {isPending === true ? (
        <Flex
          width="100vw"
          height="100vh"
          justifyContent="center"
          alignItems="center"
        >
          <Spinner
            thickness="4px"
            speed="0.65s"
            emptyColor="gray.200"
            color="blue.500"
            size="xl"
          />
        </Flex>
      ) : (
        <></>
      )}
      <Box m={'0 auto'} maxW={'1000px'}>
        <VStack alignItems={'flex-start'} gap={'30px'}>
          <Box w={'100%'}>
            <Box fontSize={'30px'}>관심 직무</Box>
            <Input
              w={'100%'}
              h={'80px'}
              placeholder="관심 직무를 입력하세요"
              value={jobInterest}
              onChange={(e) => setJobInterest(e.target.value)}
              border={'0'}
              borderRadius={'0'}
              background={'white'}
              sx={{
                '::placeholder': {
                  color: 'gray.500',
                  fontSize: '20px',
                },
              }}
            />
          </Box>
          <Box w={'100%'}>
            <Box fontSize={'30px'}>직무 인재상</Box>
            <Input
              w={'100%'}
              h={'80px'}
              placeholder="원하는 기업의 인재상을 모두 입력하세요 ex) 협업능력, 사고력·실행력, 패기"
              border={'0'}
              borderRadius={'0'}
              value={desiredTraits}
              onChange={(e) => setDesiredTraits(e.target.value)}
              background={'white'}
              sx={{
                '::placeholder': {
                  color: 'gray.500',
                  fontSize: '20px',
                },
              }}
            />
          </Box>
          <Box w={'100%'}>
            <Box fontSize={'30px'}>이력서</Box>
            <InputGroup>
              <Input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                display="none"
              />
              <Input
                w={'100%'}
                h={'80px'}
                value={fileName}
                placeholder="프로젝트 경험이 포함된 자기소개서를 업로드해주세요 (pdf 파일만 가능)"
                border={'0'}
                borderRadius={'0'}
                background={'white'}
                readOnly
                sx={{
                  '::placeholder': {
                    color: 'gray.500',
                    fontSize: '20px',
                  },
                }}
              />
              <InputRightElement width="80px" height="100%">
                <Button
                  onClick={() =>
                    document.querySelector('input[type="file"]').click()
                  }
                  variant="ghost"
                  aria-label="Upload file"
                  fontSize="28px"
                  paddingRight="10px"
                >
                  <FaUpload />
                </Button>
              </InputRightElement>
            </InputGroup>
          </Box>
        </VStack>
        <Flex justifyContent={'space-around'}>
          <Button
            w={'300px'}
            h={'100px'}
            background={'#DFE2FB'}
            fontFamily={'inter'}
            mt={'30px'}
            onClick={prevStep}
            bg={'#0066FF'}
            color={'#ffffff'}
            borderRadius={'40px'}
            fontSize={'xl'}
          >
            이전으로
          </Button>
          <Button
            w={'300px'}
            h={'100px'}
            background={'#DFE2FB'}
            fontFamily={'inter'}
            mt={'30px'}
            onClick={nextStep}
            bg={'#0066FF'}
            color={'#ffffff'}
            fontSize={'xl'}
            borderRadius={'40px'}
          >
            다음으로
          </Button>
        </Flex>
      </Box>
    </Box>
  );
};

export default UploadStep;
