import React from 'react';
import Webcam from 'react-webcam';

const videoConstraints = {
  width: 200,
  height: 300,
  facingMode: 'user',
};

const WebcamComponent = () => (
  <Webcam
    audio={false}
    height={200}
    screenshotFormat='image/jpeg'
    width={300}
    videoConstraints={videoConstraints}
  >
    {({ getScreenshot }) => (
      <button
        onClick={() => {
          const imageSrc = getScreenshot();
          print(imageSrc);
        }}
      >
        사진 캡쳐
      </button>
    )}
  </Webcam>
);

export default WebcamComponent;
