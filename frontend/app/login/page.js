import { Box } from '@chakra-ui/react';
import Container from '../common/components/container';
import Header from '../common/components/header';
import Login from './components/login';

function LoginPage() {
  return (
    <Container>
      <Header />
      <Box
        height='calc(100vh - 300px)' // 64px: Header의 높이
        display='flex'
        alignItems='center'
        justifyContent='center'
      >
        <Login />
      </Box>
    </Container>
  );
}

export default LoginPage;
