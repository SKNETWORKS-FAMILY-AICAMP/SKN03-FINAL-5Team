import Container from '../common/components/Container';
import Header from '../common/components/header';
import SideNavigation from '../myPage/components/navigation';
import BoardList from './components/boardList';
import { Flex } from '@chakra-ui/react';

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
