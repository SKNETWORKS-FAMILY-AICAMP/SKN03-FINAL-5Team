'use client';
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Input,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Flex,
  InputGroup,
  InputRightElement,
  Stack,
  Text,
  Link,
} from '@chakra-ui/react';
import { FaSearch } from 'react-icons/fa';

const BoardList = () => {
  const [posts, setPosts] = useState([
    {
      id: 1,
      title: '첫 번째 게시글: 환영합니다!',
      author: '관리자',
      createdAt: '2024-11-21 09:00',
    },
    {
      id: 2,
      title: '사이트 이용 가이드',
      author: '홍길동',
      createdAt: '2024-11-21 10:15',
    },
    {
      id: 3,
      title: '자주 묻는 질문 (FAQ)',
      author: '김철수',
      createdAt: '2024-11-21 11:30',
    },
    {
      id: 4,
      title: '새로운 기능 업데이트 안내',
      author: '이영희',
      createdAt: '2024-11-21 13:45',
    },
    {
      id: 5,
      title: '커뮤니티 규칙 안내',
      author: '박지성',
      createdAt: '2024-11-21 15:00',
    },
    {
      id: 6,
      title: '이벤트: 겨울 맞이 특별 프로모션',
      author: '정소연',
      createdAt: '2024-11-22 09:30',
    },
    {
      id: 7,
      title: '서비스 점검 예정 안내',
      author: '관리자',
      createdAt: '2024-11-22 11:00',
    },
    {
      id: 8,
      title: '사용자 경험 개선을 위한 설문조사',
      author: '김태희',
      createdAt: '2024-11-22 14:20',
    },
    {
      id: 9,
      title: '신규 회원 가입 혜택 안내',
      author: '이승기',
      createdAt: '2024-11-23 10:00',
    },
    {
      id: 10,
      title: '모바일 앱 출시 안내',
      author: '최동욱',
      createdAt: '2024-11-23 13:15',
    },
    {
      id: 11,
      title: '개인정보 처리방침 개정 안내',
      author: '관리자',
      createdAt: '2024-11-24 09:45',
    },
    {
      id: 12,
      title: '연말 결산 이벤트 안내',
      author: '박서준',
      createdAt: '2024-11-24 11:30',
    },
    {
      id: 13,
      title: '고객 지원 센터 운영 시간 변경',
      author: '김민지',
      createdAt: '2024-11-24 14:00',
    },
    {
      id: 14,
      title: '신규 파트너사 협력 안내',
      author: '이하늬',
      createdAt: '2024-11-25 10:30',
    },
    {
      id: 15,
      title: '서비스 이용 팁: 초보자 가이드',
      author: '정우성',
      createdAt: '2024-11-25 13:45',
    },
    {
      id: 16,
      title: '긴급: 시스템 오류 해결 완료',
      author: '관리자',
      createdAt: '2024-11-26 08:00',
    },
    {
      id: 17,
      title: '2025년 서비스 로드맵 공개',
      author: '송혜교',
      createdAt: '2024-11-26 11:20',
    },
    {
      id: 18,
      title: '사용자 후기 이벤트 시작',
      author: '강동원',
      createdAt: '2024-11-26 15:30',
    },
    {
      id: 19,
      title: '베타 테스터 모집 안내',
      author: '이지은',
      createdAt: '2024-11-27 09:50',
    },
    {
      id: 20,
      title: '연말 감사 인사: 2024년을 마무리하며',
      author: '관리자',
      createdAt: '2024-11-27 17:00',
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [filteredPosts, setFilteredPosts] = useState([]);
  const postsPerPage = 10;

  useEffect(() => {
    const results = posts.filter(
      (post) =>
        post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.author.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredPosts(results);
    setCurrentPage(1);
  }, [searchTerm, posts]);

  // 현재 페이지의 게시글
  const indexOfLastPost = currentPage * postsPerPage;
  const indexOfFirstPost = indexOfLastPost - postsPerPage;
  const currentPosts = filteredPosts.slice(indexOfFirstPost, indexOfLastPost);

  // 페이지 변경 함수
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <Box p={5} w={'100%'}>
      <Flex justifyContent='space-between' alignItems='center' mb={5}>
        <Flex
          fontSize={'xl'}
          borderBottom={'4px solid black'}
          pb={'10px'}
          w={'100%'}
          justifyContent={'space-between'}
        >
          <Text fontSize={['24px', '26px', '30px']}>문의 게시판</Text>
          <InputGroup width='300px'>
            <Input
              placeholder='게시글 검색'
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <InputRightElement>
              <FaSearch color='gray.500' />
            </InputRightElement>
          </InputGroup>
        </Flex>
      </Flex>

      <Table variant='simple'>
        <Thead>
          <Tr>
            <Th>번호</Th>
            <Th>제목</Th>
            <Th>글쓴이</Th>
            <Th>작성시간</Th>
          </Tr>
        </Thead>
        <Tbody>
          {currentPosts.map((post) => (
            <Tr key={post.id}>
              <Td>{post.id}</Td>
              <Td>{post.title}</Td>
              <Td>{post.author}</Td>
              <Td>{post.createdAt}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>

      <Flex justifyContent='space-between' alignItems='center' mt={5}>
        <Box flex={1}></Box>

        <Flex justifyContent='center' flex={1}>
          <Stack direction='row' spacing={2}>
            {Array.from(
              { length: Math.ceil(filteredPosts.length / postsPerPage) },
              (_, i) => (
                <Button
                  key={i}
                  onClick={() => paginate(i + 1)}
                  bg={'none'}
                  color={currentPage === i + 1 ? 'gray.500' : 'black'}
                >
                  {i + 1}
                </Button>
              )
            )}
          </Stack>
        </Flex>

        <Flex justifyContent='flex-end' flex={1}>
          <Button colorScheme='blue'>
            <Link href='/board/create'>글쓰기</Link>
          </Button>
        </Flex>
      </Flex>
    </Box>
  );
};

export default BoardList;
