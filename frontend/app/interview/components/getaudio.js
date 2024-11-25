import React, { useState, useRef } from 'react';

const SpeechToText = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = sendAudioToServer;

      mediaRecorder.current.start();
      setIsRecording(true);

      // 10초 후 녹음 중지
      setTimeout(() => {
        stopRecording();
      }, 10000);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudioToServer = async () => {
    const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await fetch('http://localhost:8000/transcribe', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setTranscript(data.transcript);
    } catch (error) {
      console.error('Error sending audio to server:', error);
    }

    audioChunks.current = [];
  };

  return (
    <div>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
      <div>
        <h3>Transcript:</h3>
        <p>{transcript}</p>
      </div>
    </div>
  );
};

export default SpeechToText;
