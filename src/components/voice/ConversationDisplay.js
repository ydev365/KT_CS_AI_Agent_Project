import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import AudioPlayer from './AudioPlayer';

const Container = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
`;

const Header = styled.div`
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
`;

const HeaderTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const MessageWrapper = styled(motion.div)`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.$isAI ? 'flex-start' : 'flex-end'};
  gap: 8px;
`;

const SpeakerLabel = styled.span`
  font-size: 12px;
  color: #999;
  margin-left: ${props => props.$isAI ? '12px' : '0'};
  margin-right: ${props => props.$isAI ? '0' : '12px'};
`;

const MessageBubble = styled.div`
  max-width: 75%;
  padding: 14px 18px;
  border-radius: ${props => props.$isAI
    ? '4px 18px 18px 18px'
    : '18px 4px 18px 18px'};
  background: ${props => props.$isAI
    ? '#f0f4ff'
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: ${props => props.$isAI ? '#333' : 'white'};
  font-size: 15px;
  line-height: 1.5;
  word-break: keep-all;
`;

const Timestamp = styled.span`
  font-size: 11px;
  color: #bbb;
  margin-left: ${props => props.$isAI ? '12px' : '0'};
  margin-right: ${props => props.$isAI ? '0' : '12px'};
`;

const EmptyState = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  gap: 12px;

  svg {
    width: 64px;
    height: 64px;
    opacity: 0.5;
  }
`;

const TypingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 14px 18px;
  background: #f0f4ff;
  border-radius: 4px 18px 18px 18px;
  width: fit-content;
`;

const TypingDot = styled(motion.span)`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
`;

const ChatIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
  </svg>
);

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return '';

  const hours = date.getHours();
  const minutes = date.getMinutes();
  const period = hours < 12 ? '오전' : '오후';
  const displayHours = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;
  const displayMinutes = minutes.toString().padStart(2, '0');

  return `${period} ${displayHours}:${displayMinutes}`;
};

const ConversationDisplay = ({ messages, isAITyping, autoPlayAudio = true, onAudioPlayComplete }) => {
  const messagesEndRef = useRef(null);

  // 새 메시지가 오면 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isAITyping]);

  return (
    <Container>
      <Header>
        <HeaderTitle>상담 대화</HeaderTitle>
      </Header>

      <MessagesContainer>
        {messages.length === 0 ? (
          <EmptyState>
            <ChatIcon />
            <p>대화가 시작되면 여기에 표시됩니다</p>
          </EmptyState>
        ) : (
          <AnimatePresence>
            {messages.map((message, index) => {
              const isAI = message.speaker === 'ai';
              return (
                <MessageWrapper
                  key={message.id || index}
                  $isAI={isAI}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <SpeakerLabel $isAI={isAI}>
                    {isAI ? 'AI 상담사' : '고객'}
                  </SpeakerLabel>

                  <MessageBubble $isAI={isAI}>
                    {message.text || message.content}
                  </MessageBubble>

                  {isAI && message.audio && (
                    <AudioPlayer
                      audioBase64={message.audio}
                      autoPlay={autoPlayAudio && index === messages.length - 1}
                      onPlayComplete={index === messages.length - 1 ? onAudioPlayComplete : undefined}
                    />
                  )}

                  <Timestamp $isAI={isAI}>
                    {formatTime(message.timestamp)}
                  </Timestamp>
                </MessageWrapper>
              );
            })}
          </AnimatePresence>
        )}

        {/* AI 타이핑 표시 */}
        <AnimatePresence>
          {isAITyping && (
            <MessageWrapper
              $isAI={true}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              <SpeakerLabel $isAI={true}>AI 상담사</SpeakerLabel>
              <TypingIndicator>
                {[0, 1, 2].map((i) => (
                  <TypingDot
                    key={i}
                    animate={{ y: [0, -6, 0] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.15
                    }}
                  />
                ))}
              </TypingIndicator>
            </MessageWrapper>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </MessagesContainer>
    </Container>
  );
};

export default ConversationDisplay;
