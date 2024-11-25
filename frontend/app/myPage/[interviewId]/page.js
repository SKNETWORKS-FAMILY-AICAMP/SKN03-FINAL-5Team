import Container from '@/app/common/components/Container';
import Header from '@/app/common/components/header';
import { Box, Flex } from '@chakra-ui/react';
import SideNavigation from '../components/navigation';
import DetailLog from '../components/detailLog';

const InterviewDetail = () => {
  return (
    <Container>
      <Header />
      <Flex mt={'50px'} gap={'30px'}>
        <SideNavigation />
        <Box w={'70%'}>
          <DetailLog />
        </Box>
      </Flex>
    </Container>
  );
};

export default InterviewDetail;
