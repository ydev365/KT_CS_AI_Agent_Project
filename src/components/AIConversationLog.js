import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import { FiUser, FiCpu, FiClock, FiPhone, FiAlertCircle } from 'react-icons/fi';
import { motion } from 'framer-motion';

const PanelContainer = styled.div`
  background: white;
  border-radius: 15px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`;

const PanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
`;

const Title = styled.h2`
  font-size: 1.3rem;
  color: #333;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ConversationInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.85rem;
  color: #666;
`;

const InfoBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: ${props => props.type === 'duration' ? '#e0f2fe' : '#f0fdf4'};
  color: ${props => props.type === 'duration' ? '#0369a1' : '#15803d'};
  border-radius: 20px;
  font-weight: 500;
`;

const ConversationArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f9fafb;
  border-radius: 10px;
  font-family: 'Courier New', monospace;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
  }
`;

const LogEntry = styled(motion.div)`
  margin-bottom: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid ${props => props.speaker === 'customer' ? '#667eea' : '#10b981'};
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
`;

const LogHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.85rem;
`;

const Timestamp = styled.span`
  color: #999;
  font-weight: 400;
`;

const Speaker = styled.span`
  color: ${props => props.type === 'customer' ? '#667eea' : '#10b981'};
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const LogContent = styled.div`
  color: #333;
  font-size: 0.95rem;
  line-height: 1.5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding-left: 20px;
`;

const SummaryBox = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
`;

const SummaryTitle = styled.h4`
  font-size: 0.9rem;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const SummaryContent = styled.p`
  font-size: 0.85rem;
  line-height: 1.4;
  opacity: 0.95;
`;

const HandoffAlert = styled.div`
  margin-top: 12px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AIConversationLog = ({ conversationLog }) => {
  const scrollRef = useRef(null);
  const [duration, setDuration] = useState('');
  
  useEffect(() => {
    // 대화 지속 시간 계산
    if (conversationLog && conversationLog.length > 0) {
      const start = new Date(conversationLog[0].timestamp);
      const end = new Date(conversationLog[conversationLog.length - 1].timestamp);
      const diff = Math.floor((end - start) / 1000);
      const minutes = Math.floor(diff / 60);
      const seconds = diff % 60;
      setDuration(`${minutes}분 ${seconds}초`);
    }
  }, [conversationLog]);

  const formatDateTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // 샘플 대화 로그 (실제로는 props로 받아옴)
  const sampleLog = conversationLog || [
    {
      timestamp: '2024-11-19T03:50:10',
      speaker: 'ai',
      speakerId: 'AI 상담사',
      content: '안녕하세요, KT 고객센터입니다. 무엇을 도와드릴까요?'
    },
    {
      timestamp: '2024-11-19T03:50:15',
      speaker: 'customer',
      speakerId: '고객_010-1234-5678',
      content: '안녕하세요, 요금제 변경하고 싶은데요.'
    },
    {
      timestamp: '2024-11-19T03:50:25',
      speaker: 'ai',
      speakerId: 'AI 상담사',
      content: '네, 요금제 변경을 도와드리겠습니다. 현재 사용 중이신 요금제는 5G 베이직 플랜이시며, 월 55,000원입니다. 어떤 요금제를 찾고 계신가요?'
    },
    {
      timestamp: '2024-11-19T03:50:35',
      speaker: 'customer',
      speakerId: '고객_010-1234-5678',
      content: '데이터를 더 많이 쓸 수 있는 요금제로 바꾸고 싶어요. 한 달에 100GB 정도는 필요할 것 같아요.'
    },
    {
      timestamp: '2024-11-19T03:50:50',
      speaker: 'ai',
      speakerId: 'AI 상담사',
      content: '100GB 이상의 데이터를 제공하는 요금제를 추천해드리겠습니다. 5G 프리미엄 언리미티드 요금제는 월 79,000원으로 데이터 무제한이며, 5G 슈퍼플랜은 월 69,000원으로 150GB를 제공합니다. 어떤 것이 더 적합하실까요?'
    },
    {
      timestamp: '2024-11-19T03:51:05',
      speaker: 'customer',
      speakerId: '고객_010-1234-5678',
      content: '5G 슈퍼플랜이 좋을 것 같네요. 그런데 가족 결합 할인도 되나요?'
    },
    {
      timestamp: '2024-11-19T03:51:20',
      speaker: 'ai',
      speakerId: 'AI 상담사',
      content: '네, 5G 슈퍼플랜도 가족 결합 할인이 가능합니다. 가족 2명 결합 시 10%, 3명 이상은 20% 할인이 적용됩니다. 현재 가족 결합이 가능한 분이 계신가요?'
    },
    {
      timestamp: '2024-11-19T03:51:30',
      speaker: 'customer',
      speakerId: '고객_010-1234-5678',
      content: '아내랑 아들이 있는데, 둘 다 KT 쓰고 있어요.'
    },
    {
      timestamp: '2024-11-19T03:51:45',
      speaker: 'ai',
      speakerId: 'AI 상담사',
      content: '3명 가족 결합 시 20% 할인이 적용되어 월 55,200원에 이용 가능하십니다. 상담원을 연결하여 자세한 변경 절차를 안내해드리겠습니다.'
    }
  ];

  return (
    <PanelContainer>
      <PanelHeader>
        <Title>
          <FiCpu style={{ color: '#10b981' }} />
          AI 상담 대화록
        </Title>
        <ConversationInfo>
          <InfoBadge type="duration">
            <FiClock />
            {duration || '2분 35초'}
          </InfoBadge>
          <InfoBadge type="messages">
            <FiPhone />
            {sampleLog.length}개 메시지
          </InfoBadge>
        </ConversationInfo>
      </PanelHeader>
      
      <ConversationArea ref={scrollRef}>
        {sampleLog.map((log, index) => (
          <LogEntry
            key={index}
            speaker={log.speaker}
            initial={{ opacity: 0, x: log.speaker === 'customer' ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <LogHeader>
              <Timestamp>{formatDateTime(log.timestamp)}</Timestamp>
              <Speaker type={log.speaker}>
                {log.speaker === 'customer' ? <FiUser /> : <FiCpu />}
                [{log.speakerId}]:
              </Speaker>
            </LogHeader>
            <LogContent>{log.content}</LogContent>
          </LogEntry>
        ))}
        
        <SummaryBox>
          <SummaryTitle>
            <FiAlertCircle />
            AI 상담 요약
          </SummaryTitle>
          <SummaryContent>
            고객이 현재 5G 베이직(55,000원)에서 더 많은 데이터 요금제로 변경 희망. 
            5G 슈퍼플랜(69,000원/150GB) 선택, 가족 3명 결합 시 20% 할인 적용하여 
            월 55,200원 이용 가능. 상담원 연결 필요.
          </SummaryContent>
        </SummaryBox>

        <HandoffAlert>
          <FiAlertCircle />
          AI 상담이 완료되어 상담원에게 전달되었습니다. 요금제 변경 처리를 진행해주세요.
        </HandoffAlert>
      </ConversationArea>
    </PanelContainer>
  );
};

export default AIConversationLog;
