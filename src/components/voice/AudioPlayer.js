import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const PlayerContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8f9ff;
  border-radius: 12px;
  max-width: 300px;
`;

const PlayButton = styled(motion.button)`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &:hover {
    opacity: 0.9;
  }

  svg {
    width: 18px;
    height: 18px;
  }
`;

const ProgressContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  cursor: pointer;
`;

const Progress = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  transition: width 0.1s linear;
`;

const TimeDisplay = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 11px;
  color: #999;
  font-family: monospace;
  width: 100%;
  gap: 4px;
`;

const PlayIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M8 5v14l11-7z"/>
  </svg>
);

const PauseIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
  </svg>
);

const AudioPlayer = ({ audioBase64, autoPlay = false, onPlayComplete }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef(null);
  const hasAutoPlayedRef = useRef(false);

  // 오디오 로드 및 자동 재생 처리
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !audioBase64) return;

    // 새 오디오일 때 autoPlay 플래그 리셋
    hasAutoPlayedRef.current = false;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      // autoPlay이고 아직 재생 안 했으면 재생
      if (autoPlay && !hasAutoPlayedRef.current) {
        hasAutoPlayedRef.current = true;
        audio.play().catch(console.error);
      }
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handlePlay = () => {
      setIsPlaying(true);
    };

    const handlePause = () => {
      setIsPlaying(false);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      if (onPlayComplete) {
        onPlayComplete();
      }
    };

    // 이벤트 리스너 먼저 등록
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    // 그 다음 오디오 소스 설정 및 로드
    const audioSrc = `data:audio/mp3;base64,${audioBase64}`;
    audio.src = audioSrc;
    audio.load();

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [audioBase64, autoPlay, onPlayComplete]);

  const togglePlayPause = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play().catch(console.error);
    }
  }, [isPlaying]);

  const handleProgressClick = useCallback((e) => {
    const audio = audioRef.current;
    if (!audio || !duration) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const clickPosition = (e.clientX - rect.left) / rect.width;
    audio.currentTime = clickPosition * duration;
  }, [duration]);

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <PlayerContainer>
      <audio ref={audioRef} preload="metadata" />

      <PlayButton
        onClick={togglePlayPause}
        whileTap={{ scale: 0.95 }}
      >
        {isPlaying ? <PauseIcon /> : <PlayIcon />}
      </PlayButton>

      <ProgressContainer>
        <ProgressBar onClick={handleProgressClick}>
          <Progress style={{ width: `${progressPercent}%` }} />
        </ProgressBar>
        <TimeDisplay>
          <span>{formatTime(currentTime)}</span>
          <span>/</span>
          <span>{formatTime(duration)}</span>
        </TimeDisplay>
      </ProgressContainer>
    </PlayerContainer>
  );
};

export default AudioPlayer;
