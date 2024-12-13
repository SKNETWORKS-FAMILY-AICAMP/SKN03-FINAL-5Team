'use client';
import Container from '@/app/common/components/container';
import Header from '@/app/common/components/header';
import { Box, Flex } from '@chakra-ui/react';
import SideNavigation from './navigation';
import DetailLog from './detailLog';
import React from 'react';
import UserGuard from '@/app/common/utils/userGuard';
import { GetInterviewLog } from '../hook/useGetInterviewLog';
import { GetInterviewReport } from '../hook/useGetInterviewReport';

const InterviewDetail = ({ params }) => {
  const { interviewId } = params;

  const { interviewLogList } = GetInterviewLog(interviewId);
  const { reportData } = GetInterviewReport(interviewId);

  return (
    <UserGuard>
      <Container>
        <Header />
        <Flex mt={'50px'} gap={'30px'}>
          <SideNavigation />
          <Box w={'70%'}>
            <DetailLog interviewLogList={interviewLogList} />
          </Box>
        </Flex>
      </Container>
    </UserGuard>
  );
};
export default InterviewDetail;