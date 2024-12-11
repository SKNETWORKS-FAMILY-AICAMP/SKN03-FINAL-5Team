import UserGuard from '@/app/common/utils/userGuard';
import Container from '@/app/common/components/container';
import Header from '@/app/common/components/header';
import { Flex } from '@chakra-ui/react';
import SideNavigation from '@/app/myPage/components/navigation';
import DetailComponent from './detailComponent';

function BoardDetail({ params }) {
  return (
    <UserGuard>
      <Container>
        <Header />
        <Flex w={'90%'} justifyContent={'center'}>
          <SideNavigation />
          <DetailComponent params={params} />
        </Flex>
      </Container>
    </UserGuard>
  );
}

export default BoardDetail;
