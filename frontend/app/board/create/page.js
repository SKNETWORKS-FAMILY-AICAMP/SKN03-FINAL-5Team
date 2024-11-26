import Container from '@/app/common/components/containers';
import Header from '@/app/common/components/header';
import SideNavigation from '@/app/myPage/components/navigation';
import { Box, Flex } from '@chakra-ui/react';
import CreateBoard from '../components/createBoard';
import React from 'react';

const BoardCreate = () => {
  return (
    <Container>
      <Header />
      <Flex w={'90%'} justifyContent={'space-between'}>
        <SideNavigation />
        <Box w={'70%'}>
          <CreateBoard />
        </Box>
      </Flex>
    </Container>
  );
};

export default BoardCreate;
