import React, { useState, useEffect } from 'react';
import { Box, Flex, Text, VStack, Select } from '@chakra-ui/react';
import {
  selectedAudioAtom,
  selectedVideoAtom,
  selectedSpeakerAtom,
} from '../atom/atom';
import { useAtom } from 'jotai';

function StepComponent() {
  const [audioDevices, setAudioDevices] = useState([]);
  const [videoDevices, setVideoDevices] = useState([]);
  const [selectedAudio, setSelectedAudio] = useAtom(selectedAudioAtom);
  const [selectedVideo, setSelectedVideo] = useAtom(selectedVideoAtom);
  const [selectedSpeaker, setSelectedSpeaker] = useAtom(selectedSpeakerAtom);

  useEffect(() => {
    const getDevices = async () => {
      const devices = await navigator.mediaDevices.enumerateDevices();
      setAudioDevices(devices.filter((device) => device.kind === 'audioinput'));
      setVideoDevices(devices.filter((device) => device.kind === 'videoinput'));
    };
    getDevices();
  }, []);

  return (
    <Box
      w={'400px'}
      h={'450px'}
      borderRadius={'40px'}
      background={'#DFE2FB'}
      p={'30px 34px 0 30px'}
      fontFamily={'inter'}
    >
      <VStack gap={'30px'} alignItems={'flex-start'}>
        <Flex alignItems={'center'} gap={'30px'}>
          <Flex flexWrap={'nowrap'}>스피커</Flex>
          <Select
            minW={'150px'}
            maxW={'200px'}
            borderRadius={'20px'}
            background={'#ffffff'}
            value={selectedSpeaker}
            onChange={(e) => setSelectedSpeaker(e.target.value)}
          >
            <option value=''>선택</option>
            {audioDevices.map((device) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || '스피커'}
              </option>
            ))}
          </Select>
        </Flex>
        <Flex alignItems={'center'} gap={'30px'}>
          <Text>카메라</Text>
          <Select
            minW={'150px'}
            maxW={'200px'}
            borderRadius={'20px'}
            background={'#ffffff'}
            value={selectedVideo}
            onChange={(e) => setSelectedVideo(e.target.value)}
          >
            <option value=''>선택</option>
            {videoDevices.map((device) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || '카메라'}
              </option>
            ))}
          </Select>
        </Flex>
        <Flex alignItems={'center'} gap={'30px'}>
          <Text>마이크</Text>
          <Select
            minW={'150px'}
            maxW={'200px'}
            borderRadius={'20px'}
            background={'#ffffff'}
            value={selectedAudio}
            onChange={(e) => setSelectedAudio(e.target.value)}
          >
            <option value=''>선택</option>
            {audioDevices.map((device) => (
              <option key={device.deviceId} value={device.deviceId}>
                {device.label || '마이크'}
              </option>
            ))}
          </Select>
        </Flex>
        <Box>
          <Text mb={'30px'}>주의사항</Text>
          <Box
            minW={'150px'}
            borderRadius={'20px'}
            background={'#ffffff'}
            p={'10px 20px'}
          >
            <Text>• 선택된 기기가 PC에 연결되어 있는지 확인해주세요.</Text>
            <Text>
              • 상단 팝업의 카메라와 마이크 권한을 “허용”으로 바꿔주세요
            </Text>
          </Box>
        </Box>
      </VStack>
    </Box>
  );
}

export default StepComponent;
