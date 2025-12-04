import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import VoiceRecorder from '../components/voice/VoiceRecorder';
import ConversationDisplay from '../components/voice/ConversationDisplay';
import voiceSocket from '../services/voiceSocket';
import api from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  display: flex;
  flex-direction: column;
`;

const Header = styled.header`
  background: white;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.h1`
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const CustomerInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #666;
`;

const CustomerBadge = styled.span`
  background: #f0f4ff;
  color: #667eea;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  padding: 24px;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;

  @media (max-width: 900px) {
    flex-direction: column;
  }
`;

const ConversationSection = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 500px;
`;

const ControlSection = styled.div`
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 20px;

  @media (max-width: 900px) {
    width: 100%;
  }
`;

const ControlCard = styled.div`
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
`;

const CardTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
`;

const TextInputContainer = styled.div`
  display: flex;
  gap: 8px;
`;

const TextInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SendButton = styled.button`
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const EndButton = styled(motion.button)`
  width: 100%;
  padding: 16px;
  background: #fff;
  color: #ef4444;
  border: 2px solid #ef4444;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #fef2f2;
  }
`;

const StatusBadge = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: ${props => {
    switch(props.$status) {
      case 'connected': return '#ecfdf5';
      case 'error': return '#fef2f2';
      default: return '#fffbeb';
    }
  }};
  color: ${props => {
    switch(props.$status) {
      case 'connected': return '#059669';
      case 'error': return '#dc2626';
      default: return '#d97706';
    }
  }};
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
`;

const StatusDot = styled.span`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
`;

const Modal = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 24px;
  padding: 32px;
  max-width: 400px;
  width: 90%;
  text-align: center;
`;

const ModalTitle = styled.h2`
  margin: 0 0 12px 0;
  font-size: 22px;
  color: #333;
`;

const ModalText = styled.p`
  color: #666;
  margin-bottom: 24px;
  line-height: 1.6;
`;

const ModalButtons = styled.div`
  display: flex;
  gap: 12px;
  justify-content: center;
`;

const ModalButton = styled.button`
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  ${props => props.$primary ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
  ` : `
    background: white;
    color: #666;
    border: 1px solid #e0e0e0;
  `}

  &:hover {
    transform: translateY(-1px);
  }
`;

const VoiceConsultationPage = () => {
  const navigate = useNavigate();

  // 상태
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [messages, setMessages] = useState([]);
  const [isAITyping, setIsAITyping] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [showEndModal, setShowEndModal] = useState(false);
  const [customerInfo, setCustomerInfo] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [pendingEndSession, setPendingEndSession] = useState(false); // TTS 재생 완료 대기용
  const [consultationComplete, setConsultationComplete] = useState(false); // 상담 완료 대기

  // 초기화
  useEffect(() => {
    // 인증 정보 확인
    const authData = sessionStorage.getItem('authResult');
    const storedSessionId = sessionStorage.getItem('sessionId');

    if (!authData || !storedSessionId) {
      navigate('/auth');
      return;
    }

    const auth = JSON.parse(authData);
    setCustomerInfo(auth.customer);
    setSessionId(storedSessionId);

    // 이벤트 리스너를 먼저 설정한 후 연결
    voiceSocket.onConnectionSuccess(() => {
      console.log('Connection success received');
      setConnectionStatus('connected');
      // 세션 시작 - API 호출 후 WebSocket 연결
      initializeSession(storedSessionId, auth.customer);
    });

    voiceSocket.onSessionStarted(async (data) => {
      console.log('Voice session started:', data);
      // 초기 인사 메시지 + TTS
      const greetingText = '안녕하세요! KT AI 상담사입니다. 어떤 요금제에 관심이 있으신가요?';
      try {
        const ttsResponse = await api.post('/api/voice/tts', { text: greetingText });
        console.log('TTS response:', ttsResponse.data);
        addAIMessage(greetingText, ttsResponse.data.audio_base64);
      } catch (error) {
        console.error('TTS error:', error);
        addAIMessage(greetingText);
      }
    });

    // 리스너 설정 후 연결
    voiceSocket.connect();

    voiceSocket.onCustomerMessage((data) => {
      addCustomerMessage(data.text, data.timestamp);
      setIsAITyping(true);
    });

    voiceSocket.onVoiceResponse((data) => {
      setIsProcessing(false);
      setIsAITyping(false);
      addAIMessage(data.text, data.audio, data.timestamp);

      if (data.shouldEnd) {
        // TTS 재생 완료 후 종료 처리하도록 플래그 설정
        setPendingEndSession(true);
      }
    });

    voiceSocket.onSessionError((data) => {
      console.error('Session error:', data.error);
      setIsProcessing(false);
      setIsAITyping(false);
    });

    voiceSocket.onConsultationCompleted((data) => {
      console.log('Consultation completed:', data);
      // 상담 결과를 저장
      sessionStorage.setItem('consultationResult', JSON.stringify(data));
      // 상담 완료 플래그 설정 (TTS 완료 후 네비게이션)
      setConsultationComplete(true);
    });

    // 클린업
    return () => {
      voiceSocket.removeAllListeners();
      voiceSocket.disconnect();
    };
  }, [navigate]);

  const initializeSession = async (sessId, customer) => {
    try {
      // 채팅 세션 생성 API 호출
      await api.post('/api/chat/session', {
        session_id: sessId
      });

      // WebSocket으로 음성 세션 시작
      voiceSocket.startVoiceSession(sessId, customer);
    } catch (error) {
      console.error('Session init error:', error);
      setConnectionStatus('error');
    }
  };

  const addCustomerMessage = useCallback((text, timestamp) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      speaker: 'customer',
      text,
      timestamp: timestamp || new Date().toISOString()
    }]);
  }, []);

  const addAIMessage = useCallback((text, audio, timestamp) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      speaker: 'ai',
      text,
      audio,
      timestamp: timestamp || new Date().toISOString()
    }]);
  }, []);

  // 음성 녹음 완료 처리
  const handleRecordingComplete = useCallback(async (audioBase64) => {
    setIsProcessing(true);

    try {
      // WebSocket으로 음성 전송
      voiceSocket.sendVoiceInput(audioBase64);
    } catch (error) {
      console.error('Voice send error:', error);
      setIsProcessing(false);
    }
  }, []);

  // 텍스트 전송
  const handleSendText = useCallback(async () => {
    if (!textInput.trim() || isProcessing) return;

    const text = textInput.trim();
    setTextInput('');
    addCustomerMessage(text);
    setIsAITyping(true);

    try {
      // WebSocket으로 텍스트 전송
      voiceSocket.sendTextInput(text);
    } catch (error) {
      console.error('Text send error:', error);
      setIsAITyping(false);
    }
  }, [textInput, isProcessing, addCustomerMessage]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  // 상담 종료
  const handleEndConsultation = () => {
    setShowEndModal(true);
  };

  const confirmEndConsultation = () => {
    setShowEndModal(false);
    voiceSocket.endVoiceSession();
  };

  const handleConsultationEnd = () => {
    // AI가 상담 종료 판단 → 자동으로 세션 종료 호출
    setIsProcessing(true);
    voiceSocket.endVoiceSession();
  };

  // TTS 재생 완료 콜백
  const handleAudioPlayComplete = useCallback(() => {
    console.log('TTS playback complete', { pendingEndSession, consultationComplete });

    // 상담이 완료되었으면 대시보드로 이동
    if (consultationComplete) {
      console.log('Navigating to dashboard after TTS complete...');
      // 약간의 딜레이를 주어 자연스럽게 전환
      setTimeout(() => {
        navigate('/dashboard');
      }, 500);
      return;
    }

    // should_end가 true였던 경우 세션 종료 호출
    if (pendingEndSession) {
      console.log('Ending session after TTS...');
      setPendingEndSession(false);
      handleConsultationEnd();
    }
  }, [pendingEndSession, consultationComplete, navigate]);

  return (
    <PageContainer>
      <Header>
        <Logo>KT AI 상담</Logo>
        <CustomerInfo>
          {customerInfo && (
            <>
              <span>{customerInfo.name}님</span>
              <CustomerBadge>
                {customerInfo.current_plan || '신규 고객'}
              </CustomerBadge>
            </>
          )}
          <StatusBadge $status={connectionStatus}>
            <StatusDot />
            {connectionStatus === 'connected' ? '연결됨' :
             connectionStatus === 'error' ? '연결 오류' : '연결 중...'}
          </StatusBadge>
        </CustomerInfo>
      </Header>

      <MainContent>
        <ConversationSection>
          <ConversationDisplay
            messages={messages}
            isAITyping={isAITyping}
            autoPlayAudio={true}
            onAudioPlayComplete={handleAudioPlayComplete}
          />
        </ConversationSection>

        <ControlSection>
          <ControlCard>
            <CardTitle>음성 입력</CardTitle>
            <VoiceRecorder
              onRecordingComplete={handleRecordingComplete}
              disabled={connectionStatus !== 'connected'}
              isProcessing={isProcessing || isAITyping}
            />
          </ControlCard>

          <ControlCard>
            <CardTitle>텍스트 입력</CardTitle>
            <TextInputContainer>
              <TextInput
                type="text"
                placeholder="메시지를 입력하세요..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={connectionStatus !== 'connected' || isAITyping}
              />
              <SendButton
                onClick={handleSendText}
                disabled={!textInput.trim() || isAITyping}
              >
                전송
              </SendButton>
            </TextInputContainer>
          </ControlCard>

          <EndButton
            onClick={handleEndConsultation}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            상담 종료
          </EndButton>
        </ControlSection>
      </MainContent>

      {/* 종료 확인 모달 */}
      <AnimatePresence>
        {showEndModal && (
          <Modal
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowEndModal(false)}
          >
            <ModalContent
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ModalTitle>상담을 종료하시겠습니까?</ModalTitle>
              <ModalText>
                상담을 종료하면 AI가 대화 내용을 분석하여<br/>
                요약 및 요금제 추천을 생성합니다.
              </ModalText>
              <ModalButtons>
                <ModalButton onClick={() => setShowEndModal(false)}>
                  계속 상담
                </ModalButton>
                <ModalButton $primary onClick={confirmEndConsultation}>
                  상담 종료
                </ModalButton>
              </ModalButtons>
            </ModalContent>
          </Modal>
        )}
      </AnimatePresence>
    </PageContainer>
  );
};

export default VoiceConsultationPage;
