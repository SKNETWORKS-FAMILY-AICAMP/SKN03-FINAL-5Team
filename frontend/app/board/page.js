import Container from '@/app/common/components/containers';
import Header from '../common/components/header';
import SideNavigation from '../myPage/components/navigation';
import BoardList from './components/boardList';
import { Flex } from '@chakra-ui/react';
import React from 'react';

function Board() {
  return (
    <Container>
      <Header />
      <Flex w={'90%'} justifyContent={'center'}>
        <SideNavigation />
        <BoardList />
      </Flex>
    </Container>
  );
}

export default Board;
