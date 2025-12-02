import React, { useState, useRef, useCallback, useEffect } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

const pulse = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  }
  70% {
    box-shadow: 0 0 0 20px rgba(239, 68, 68, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
`;

const RecorderContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
`;

const RecordButton = styled(motion.button)`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: none;
  background: ${props => props.$isRecording
    ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  ${props => props.$isRecording && css`
    animation: ${pulse} 1.5s infinite;
  `}

  &:hover:not(:disabled) {
    transform: scale(1.05);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  svg {
    width: 32px;
    height: 32px;
  }
`;

const StatusText = styled.p`
  font-size: 14px;
  color: ${props => props.$isRecording ? '#ef4444' : '#666'};
  margin: 0;
  font-weight: 500;
`;

const RecordingTime = styled.span`
  font-family: monospace;
  font-size: 16px;
  color: #ef4444;
  font-weight: 600;
`;

const WaveformContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  height: 40px;
`;

const WaveBar = styled(motion.div)`
  width: 4px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
`;

const MicIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
  </svg>
);

const StopIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <rect x="6" y="6" width="12" height="12" rx="2"/>
  </svg>
);

const VoiceRecorder = ({ onRecordingComplete, disabled, isProcessing }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(new Array(10).fill(5));

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const analyzeAudio = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    // 10개의 바로 시각화
    const barCount = 10;
    const step = Math.floor(dataArray.length / barCount);
    const levels = [];

    for (let i = 0; i < barCount; i++) {
      const value = dataArray[i * step];
      // 5~40 사이로 정규화
      levels.push(Math.max(5, Math.min(40, (value / 255) * 40)));
    }

    setAudioLevel(levels);
    animationFrameRef.current = requestAnimationFrame(analyzeAudio);
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });

      // 오디오 분석 설정
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      // 브라우저 호환성을 위한 MIME 타입 선택
      const getSupportedMimeType = () => {
        const mimeTypes = [
          'audio/webm;codecs=opus',
          'audio/webm',
          'audio/ogg;codecs=opus',
          'audio/ogg',
          'audio/mp4',
          'audio/mpeg'
        ];
        for (const mimeType of mimeTypes) {
          if (MediaRecorder.isTypeSupported(mimeType)) {
            console.log('Using MIME type:', mimeType);
            return mimeType;
          }
        }
        console.log('Using default MIME type');
        return undefined; // 브라우저 기본값 사용
      };

      const mimeType = getSupportedMimeType();
      const recorderOptions = mimeType ? { mimeType } : {};

      const mediaRecorder = new MediaRecorder(stream, recorderOptions);
      const actualMimeType = mediaRecorder.mimeType || 'audio/webm';
      console.log('MediaRecorder using MIME type:', actualMimeType);

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // 스트림 정리
        stream.getTracks().forEach(track => track.stop());
        audioContext.close();

        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }

        // 청크 데이터 확인
        console.log('Audio chunks count:', audioChunksRef.current.length);
        const totalSize = audioChunksRef.current.reduce((acc, chunk) => acc + chunk.size, 0);
        console.log('Total audio size:', totalSize, 'bytes');

        if (audioChunksRef.current.length === 0 || totalSize < 1000) {
          console.warn('Audio data too small or empty, skipping...');
          setAudioLevel(new Array(10).fill(5));
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: actualMimeType });
        console.log('Final blob size:', audioBlob.size, 'bytes');

        // Blob을 Base64로 변환
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64Audio = reader.result.split(',')[1];
          console.log('Base64 length:', base64Audio.length);
          onRecordingComplete(base64Audio, audioBlob);
        };
        reader.readAsDataURL(audioBlob);

        setAudioLevel(new Array(10).fill(5));
      };

      mediaRecorder.start(100); // 100ms마다 데이터 수집
      setIsRecording(true);
      setRecordingTime(0);

      // 타이머 시작
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      // 오디오 분석 시작
      analyzeAudio();

    } catch (error) {
      console.error('Error starting recording:', error);
      alert('마이크 접근 권한이 필요합니다.');
    }
  }, [onRecordingComplete, analyzeAudio]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      // 최소 녹음 시간 체크 (1초 미만이면 무시)
      if (recordingTime < 1) {
        console.log('Recording too short, ignoring...');
        mediaRecorderRef.current.stop();
        setIsRecording(false);
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
        // 짧은 녹음은 전송하지 않음
        audioChunksRef.current = [];
        return;
      }

      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  }, [isRecording, recordingTime]);

  const handleClick = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <RecorderContainer>
      <AnimatePresence>
        {isRecording && (
          <WaveformContainer>
            {audioLevel.map((level, index) => (
              <WaveBar
                key={index}
                initial={{ height: 5 }}
                animate={{ height: level }}
                exit={{ height: 5 }}
                transition={{ duration: 0.1 }}
              />
            ))}
          </WaveformContainer>
        )}
      </AnimatePresence>

      <RecordButton
        $isRecording={isRecording}
        onClick={handleClick}
        disabled={disabled || isProcessing}
        whileTap={{ scale: 0.95 }}
      >
        {isRecording ? <StopIcon /> : <MicIcon />}
      </RecordButton>

      <StatusText $isRecording={isRecording}>
        {isProcessing ? '처리 중...' : isRecording ? (
          <>녹음 중 <RecordingTime>{formatTime(recordingTime)}</RecordingTime></>
        ) : (
          '버튼을 눌러 말씀해주세요'
        )}
      </StatusText>
    </RecorderContainer>
  );
};

export default VoiceRecorder;
