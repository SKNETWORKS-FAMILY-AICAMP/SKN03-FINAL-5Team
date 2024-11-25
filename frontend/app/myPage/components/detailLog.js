import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Divider,
  Flex,
  Image,
} from '@chakra-ui/react';
import { FaQuestion, FaComment } from 'react-icons/fa';

const DetailLog = () => {
  const interviewData = [
    {
      question:
        '면접 질문 이력이 들어갈 곳입니다. 면접 질문 이력이 들어갈 곳입니다. 면접 질문 이력이 들어갈 곳입니다. 면접 질문 이력이 들어갈 곳입니다. 면접 질문 이력이 들어갈 곳입니다.',
      answer: '사용자의 대답 이력이 들어갈 곳입니다.',
    },
    {
      question: '면접 질문 이력이 들어갈 곳입니다.',
      answer: '사용자의 대답 이력이 들어갈 곳입니다.',
    },
    {
      question: '면접 질문 이력이 들어갈 곳입니다.',
      answer: '사용자의 대답 이력이 들어갈 곳입니다.',
    },
    {
      question: '면접 질문 이력이 들어갈 곳입니다.',
      answer: '사용자의 대답 이력이 들어갈 곳입니다.',
    },
  ];

  return (
    <Box maxWidth='800px' margin='auto' p={5} overflowX={'scroll'}>
      <Box borderBottom={'4px solid black'} pb={'10px'} w={'100%'}>
        <Text fontSize={['24px', '26px', '30px']}>면접 세부 내용</Text>
      </Box>
      <VStack spacing={4} align='stretch'>
        <Flex justifyContent={'space-between'} alignItems={'center'}>
          <Heading as='h2' size='md' mb={2} mt={10}>
            면접1
          </Heading>
          <Box cursor={'pointer'} textDecor={'underline'}>
            면접 결과 보고서.pdf 다운받기
          </Box>
        </Flex>
        {interviewData.map((item, index) => (
          <Box key={index} borderBottom={'1px solid black'} p={'10px 0 10px 0'}>
            <Flex align='center' mb={4}>
              <Image w={'30px'} mb={'5px'} mr={'8px'} src='/logo.png' />
              <Box p={'5px 30px'} background={'white'} borderRadius={'16px'}>
                <Text fontWeight='bold'>질문: {item.question}</Text>
              </Box>
            </Flex>
            <Flex align='center' mb={4}>
              <FaComment
                style={{
                  marginLeft: '5px',
                  fontSize: '20px',
                  marginRight: '13px',
                  color: 'green.500',
                }}
              />
              <Box p={'5px 30px'} background={'white'} borderRadius={'16px'}>
                <Text>대답: {item.answer}</Text>
              </Box>
            </Flex>
          </Box>
        ))}
      </VStack>
    </Box>
  );
};

export default DetailLog;
