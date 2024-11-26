import React, { useState, useEffect, useCallback, useRef } from 'react';
import Webcam from 'react-webcam';
import { Box, Button, Skeleton } from '@chakra-ui/react';
import StepProgress from '@/app/common/components/progress';

const WebcamComponent = () => {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [capturing, setCapturing] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [hasWebcamPermission, setHasWebcamPermission] = useState(false);

  useEffect(() => {
    // 웹캠 권한 확인
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then(() => setHasWebcamPermission(true))
      .catch(() => setHasWebcamPermission(false));
  }, []);

  const handleStartCaptureClick = useCallback(() => {
    setCapturing(true);

    const stream = webcamRef.current.video.srcObject;

    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType: 'video/webm',
    });

    mediaRecorderRef.current.addEventListener(
      'dataavailable',
      handleDataAvailable
    );
    mediaRecorderRef.current.start(); // 스트림 녹화 시작
  }, [webcamRef, setCapturing, mediaRecorderRef]);

  const handleDataAvailable = useCallback(
    ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks((prev) => prev.concat(data));
      }
    },
    [setRecordedChunks]
  );

  const handleStopCaptureClick = useCallback(() => {
    mediaRecorderRef.current.stop();
    setCapturing(false);
  }, [mediaRecorderRef, webcamRef, setCapturing]);

  const handleDownload = useCallback(() => {
    if (recordedChunks.length) {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      document.body.appendChild(a);
      a.style = 'display: none';
      a.href = url;
      a.download = 'mirrored-video.webm';
      a.click();
      window.URL.revokeObjectURL(url);
      setRecordedChunks([]);
    }
  }, [recordedChunks]);

  const containerSize = { width: '100%', height: '450px' };

  return (
    <Box textAlign={'center'}>
      <Box
        w={containerSize.width}
        h={containerSize.height}
        minW={'700px'}
        overflow='hidden'
        borderRadius='16px'
        position='relative'
      >
        {hasWebcamPermission ? (
          <Webcam
            audio={false}
            ref={webcamRef}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              borderRadius: '16px',
              transform: 'scaleX(-1)',
            }}
          />
        ) : (
          <Skeleton width='100%' height='100%' borderRadius='16px' />
        )}
      </Box>
      {/* <Box mt='10px' mb={'20px'}>
        {hasWebcamPermission ? (
          <>
            {capturing ? (
              <Button onClick={handleStopCaptureClick} colorScheme='red'>
                Stop Capture
              </Button>
            ) : (
              <Button onClick={handleStartCaptureClick} colorScheme='green'>
                Start Capture
              </Button>
            )}
            {recordedChunks.length > 0 && (
              <Button onClick={handleDownload} colorScheme='blue' ml='10px'>
                Download
              </Button>
            )}
          </>
        ) : (
          <Button
            onClick={() => alert('웹캠 권한이 필요합니다.')}
            colorScheme='yellow'
          >
            웹캠 권한 요청
          </Button>
        )}
      </Box> */}
    </Box>
  );
};

export default WebcamComponent;
