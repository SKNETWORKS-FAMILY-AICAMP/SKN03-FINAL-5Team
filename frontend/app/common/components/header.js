import { Box, Image, Flex, Link } from '@chakra-ui/react';
import React from 'react';

const Header = () => {
  return (
    <Box
      display={'flex'}
      w={'100%'}
      p={'10px 30px'}
      color={'#0066FF'}
      justifyContent="space-between"
      fontSize={'28px'}
    >
      <Flex alignItems={'center'} gap={'40px'}>
        <Link href="/">
          <Box cursor={'pointer'}>
            <Image w={'80px'} mb={'5px'} src="/logo.png" />
          </Box>
        </Link>
        <Link href="/about">
          <Box w={'100%'}>About</Box>
        </Link>
        <Link href="/interview">
          <Box w={'100%'}>AI Mock Interview</Box>
        </Link>
        <Link href="/myPage">
          <Box w={'100%'}>My Page</Box>
        </Link>
      </Flex>

      <Flex alignItems={'center'} gap={'40px'}>
        <Link href="/login">
          <Box w={'120px'}>Login</Box>
        </Link>
        <Link href="/signup">
          <Box w={'120px'}>Sign up</Box>
        </Link>
      </Flex>
    </Box>
  );
};

export default Header;
