import React from 'react';
import Webcam from 'react-webcam';
import { Box, Button } from '@chakra-ui/react';

const WebcamComponent = () => {
  const webcamRef = React.useRef(null);
  const mediaRecorderRef = React.useRef(null);
  const [capturing, setCapturing] = React.useState(false);
  const [recordedChunks, setRecordedChunks] = React.useState([]);

  const handleStartCaptureClick = React.useCallback(() => {
    setCapturing(true);
    const stream = webcamRef.current.video.srcObject;

    const canvas = document.createElement('canvas');
    canvas.width = webcamRef.current.video.videoWidth;
    canvas.height = webcamRef.current.video.videoHeight;
    const context = canvas.getContext('2d');

    mediaRecorderRef.current = new MediaRecorder(canvas.captureStream(), {
      mimeType: 'video/webm',
    });

    const drawFrame = () => {
      if (capturing) {
        // 좌우 반전을 적용하여 캔버스에 그립니다.
        context.save();
        context.scale(-1, 1);
        context.drawImage(
          webcamRef.current.video,
          -canvas.width,
          0,
          canvas.width,
          canvas.height
        );
        context.restore();
        requestAnimationFrame(drawFrame);
      }
    };
    drawFrame();

    mediaRecorderRef.current.addEventListener(
      'dataavailable',
      handleDataAvailable
    );
    mediaRecorderRef.current.start();
  }, [webcamRef, setCapturing, mediaRecorderRef]);

  const handleDataAvailable = React.useCallback(
    ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks((prev) => prev.concat(data));
      }
    },
    [setRecordedChunks]
  );

  const handleStopCaptureClick = React.useCallback(() => {
    mediaRecorderRef.current.stop();
    setCapturing(false);
  }, [mediaRecorderRef, webcamRef, setCapturing]);

  const handleDownload = React.useCallback(() => {
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

  return (
    <Box w={'auto'} textAlign={'center'}>
      <Box w={'100%'} overflow='hidden' borderRadius='16px'>
        <Webcam
          width='100%'
          audio={false}
          ref={webcamRef}
          style={{
            borderRadius: '16px', // 비디오 자체에도 radius 적용
            transform: 'scaleX(-1)', // 좌우 반전
          }}
        />
      </Box>
      <Box mt='10px' mb={'20px'}>
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
      </Box>
      <Box background={'#DFE2FB'} h={'100px'}></Box>
    </Box>
  );
};

export default WebcamComponent;
