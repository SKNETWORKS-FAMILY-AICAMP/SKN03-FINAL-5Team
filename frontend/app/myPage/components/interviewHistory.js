import { Box, Text, VStack, Grid, GridItem, Link } from '@chakra-ui/react';
import React from 'react';

const InterviewLog = ({ title, date, id }) => {
  return (
    <Box
      display={'grid'}
      p={'20px'}
      fontSize={'20px'}
      bg={'white'}
      w={'300px'}
      borderRadius={'16px'}
      cursor={'pointer'}
      transition="transform 0.2s ease-in-out"
      _hover={{ transform: 'translateY(-5px)' }}
    >
      <Link href={`/myPage/${id}`}>
        <Text>{title}</Text>
        <Text>{date}</Text>
      </Link>
    </Box>
  );
};

const InterviewHistory = () => {
  const interviewData = [
    { id: 1, title: '직무 면접[이력서]', date: '2024.11.14' },
    { id: 2, title: '기술 면접[프론트엔드]', date: '2024.11.15' },
    { id: 3, title: 'AI 면접[인성]', date: '2024.11.16' },
    { id: 4, title: '최종 면접[임원]', date: '2024.11.17' },
    { id: 5, title: '신입 공채 면접', date: '2024.11.18' },
  ];

  return (
    <Box>
      <Box borderBottom={'4px solid black'} pb={'10px'} w={'100%'}>
        <Text fontSize={['24px', '26px', '30px']}>면접 이력</Text>
      </Box>
      <Grid w={'100%'} pt={'30px'} templateColumns="repeat(3, 1fr)" gap={6}>
        {interviewData.map((interview) => (
          <GridItem key={interview.id}>
            <InterviewLog
              title={interview.title}
              date={interview.date}
              id={interview.id}
            />
          </GridItem>
        ))}
      </Grid>
    </Box>
  );
};

export default InterviewHistory;
