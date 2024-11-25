import {
  Box,
  Button,
  Input,
  InputGroup,
  InputRightElement,
  Text,
} from '@chakra-ui/react';
const UserComponent = () => {
  return (
    <Box>
      <Box maxWidth='800px' margin='auto' p={5} overflowX={'scroll'}>
        <Box borderBottom={'4px solid black'} pb={'10px'} w={'100%'}>
          <Text fontSize={['24px', '26px', '30px']}>회원 정보</Text>
        </Box>
        <Box p={'20px 0 20px 0'}>
          <Box fontSize={'20px'} mb={1}>
            이름
          </Box>
          <Box borderRadius={'15px'} p={'5px 10px'} w={'100%'} bg={'white'}>
            김원철
          </Box>
        </Box>
        <Box p={'20px 0 20px 0'}>
          <Box fontSize={'20px'} mb={1}>
            이메일
          </Box>
          <InputGroup>
            <Input type='file' accept='.pdf' display='none' />
            <Input
              w={'100%'}
              h={'40px'}
              placeholder='test@naver.com'
              border={'0'}
              borderRadius={'15px'}
              background={'white'}
              readOnly
              sx={{
                '::placeholder': {
                  color: 'gray.500',
                },
              }}
            />
            <InputRightElement width='80px' height='100%'>
              <Button
                // onClick={() =>
                //   document.querySelector('input[type="file"]').click()
                // }
                variant='ghost'
                aria-label='Upload file'
                fontSize='28px'
                paddingRight='10px'
              >
                <Box fontSize={'md'} color={'gray.500'}>
                  수정하기
                </Box>
              </Button>
            </InputRightElement>
          </InputGroup>
        </Box>
        <Box p={'20px 0 20px 0'}>
          <Box fontSize={'20px'} mb={1}>
            회원탈퇴
          </Box>
          <Button
            fontSize={'md'}
            color={'red'}
            borderRadius={'15px'}
            p={'5px 20px'}
            bg={'white'}
          >
            회원탈퇴
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default UserComponent;
