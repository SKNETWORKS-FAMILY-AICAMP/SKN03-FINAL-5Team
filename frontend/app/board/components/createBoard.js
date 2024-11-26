'use client';
import {
  Box,
  Text,
  VStack,
  Flex,
  Input,
  Textarea,
  Button,
  Link,
} from '@chakra-ui/react';
import React, { useState } from 'react';

const CreateBoard = () => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const onChngeTitle = (e) => {
    setTitle(e.target.value);
  };

  const onChangeContent = (e) => {
    setContent(e.target.value);
  };

  const onClickSubmit = () => {
    const data = {
      title: title,
      content: content,
    };
  };

  return (
    <Box>
      <Box borderBottom={'4px solid black'} pb={'10px'} w={'100%'}>
        <Text fontSize={['24px', '26px', '30px']}>문의 게시판</Text>
      </Box>
      <Box fontSize={'x-large'} mt={5} mb={10}>
        글쓰기
      </Box>
      <VStack
        w={'100%'}
        ml={'20px'}
        pb={'40px'}
        borderBottom={'1px solid black'}
      >
        <Flex w={'100%'}>
          <Text p={'5px 10px'} w={'auto'}>
            제목
          </Text>
          <Input
            value={title}
            onChange={(e) => onChngeTitle(e)}
            bg={'white'}
            w={'80%'}
          />
        </Flex>
        <Flex w={'100%'}>
          <Text p={'5px 10px'} w={'auto'}>
            내용
          </Text>
          <Textarea
            onChange={(e) => onChangeContent(e)}
            value={content}
            bg={'white'}
            w={'80%'}
            h={'300px'}
          />
        </Flex>
      </VStack>
      <Flex justifyContent={'flex-end'} gap={'10px'} mt={'10px'}>
        <Button onClick={onClickSubmit}>확인</Button>
        <Button>
          <Link href='/board'>취소</Link>
        </Button>
      </Flex>
    </Box>
  );
};

export default CreateBoard;