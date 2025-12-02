import React, { useState } from 'react';
import styled from 'styled-components';
import { FiClock, FiMessageSquare, FiChevronRight, FiX, FiUser, FiZap } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';

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
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
`;

const Title = styled.h3`
  font-size: 1.1rem;
  color: #333;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const HistoryList = styled.div`
  flex: 1;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
  }

  &::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 10px;
  }
`;

const HistoryItem = styled(motion.div)`
  background: #f9f9f9;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 10px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;

  &:hover {
    background: white;
    border-color: #667eea;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
`;

const HistoryDate = styled.div`
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const HistorySummary = styled.div`
  font-size: 0.9rem;
  color: #333;
  font-weight: 500;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const HistoryTags = styled.div`
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
`;

const HistoryTag = styled.span`
  background: ${props => props.$type === 'resolved' ? '#dcfce7' : '#fef3c7'};
  color: ${props => props.$type === 'resolved' ? '#166534' : '#92400e'};
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #999;

  svg {
    font-size: 2rem;
    margin-bottom: 12px;
    opacity: 0.3;
  }

  p {
    font-size: 0.85rem;
  }
`;

// 모달 스타일
const ModalOverlay = styled(motion.div)`
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
  border-radius: 20px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const ModalHeader = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ModalTitle = styled.h2`
  font-size: 1.2rem;
  color: #333;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: #666;
  transition: all 0.2s;

  &:hover {
    background: #f0f0f0;
    color: #333;
  }
`;

const ModalBody = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
`;

const Tab = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.$active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f0f0f0'};
  color: ${props => props.$active ? 'white' : '#666'};

  &:hover {
    transform: translateY(-1px);
  }
`;

const SummarySection = styled.div`
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
`;

const SummaryTitle = styled.h3`
  font-size: 1rem;
  color: #0369a1;
  margin-bottom: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const SummaryItem = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
`;

const SummaryLabel = styled.span`
  font-weight: 600;
  color: #1e40af;
  font-size: 0.85rem;
  min-width: 80px;
`;

const SummaryValue = styled.span`
  color: #475569;
  font-size: 0.85rem;
`;

const ConversationContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.$isAI ? 'flex-start' : 'flex-end'};
`;

const MessageBubble = styled.div`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: ${props => props.$isAI ? '4px 16px 16px 16px' : '16px 4px 16px 16px'};
  background: ${props => props.$isAI ? '#f0f4ff' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: ${props => props.$isAI ? '#333' : 'white'};
  font-size: 0.9rem;
  line-height: 1.5;
`;

const MessageSpeaker = styled.span`
  font-size: 0.75rem;
  color: #999;
  margin-bottom: 4px;
`;

const MessageTime = styled.span`
  font-size: 0.7rem;
  color: #bbb;
  margin-top: 4px;
`;

const ConsultationHistory = ({ customerId, history, onSelectHistory }) => {
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  // 샘플 이전 상담 내역
  const sampleHistory = history || [
    {
      id: 'H001',
      date: '2024-11-15 14:30',
      summary: '데이터 요금제 변경 문의',
      status: 'resolved',
      tags: ['요금제 변경', '5G'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, KT 고객센터입니다.', timestamp: '14:30:10' },
        { speaker: 'customer', content: '요금제 변경하고 싶어요', timestamp: '14:30:25' },
        { speaker: 'ai', content: '네, 어떤 요금제를 원하시나요?', timestamp: '14:30:35' },
        { speaker: 'customer', content: '데이터 많은 걸로요', timestamp: '14:30:50' },
        { speaker: 'ai', content: '5G 슈퍼플랜 추천드립니다.', timestamp: '14:31:05' },
      ],
      aiSummary: {
        currentPlan: '5G 베이직',
        requestedFeature: '데이터 증량',
        mainConcern: '데이터 부족',
        result: '5G 슈퍼플랜 안내 완료'
      }
    },
    {
      id: 'H002',
      date: '2024-11-10 10:15',
      summary: '인터넷 결합 할인 문의',
      status: 'resolved',
      tags: ['결합할인', '인터넷'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, 무엇을 도와드릴까요?', timestamp: '10:15:10' },
        { speaker: 'customer', content: '인터넷이랑 결합하면 할인되나요?', timestamp: '10:15:30' },
        { speaker: 'ai', content: '네, 결합 시 최대 25% 할인됩니다.', timestamp: '10:15:45' },
      ],
      aiSummary: {
        currentPlan: '5G 베이직',
        requestedFeature: '결합 할인',
        mainConcern: '요금 절감',
        result: '결합 할인 안내 완료'
      }
    },
    {
      id: 'H003',
      date: '2024-10-28 16:45',
      summary: '해외 로밍 서비스 문의',
      status: 'resolved',
      tags: ['로밍', '해외'],
      conversation: [
        { speaker: 'ai', content: '안녕하세요, KT입니다.', timestamp: '16:45:10' },
        { speaker: 'customer', content: '일본 여행가는데 로밍 어떻게 해요?', timestamp: '16:45:30' },
        { speaker: 'ai', content: '데이터로밍 무제한 상품 추천드립니다.', timestamp: '16:45:50' },
      ],
      aiSummary: {
        currentPlan: '5G 베이직',
        requestedFeature: '해외 로밍',
        mainConcern: '해외 데이터 사용',
        result: '로밍 상품 안내 완료'
      }
    }
  ];

  const handleItemClick = (item) => {
    setSelectedHistory(item);
    setActiveTab('summary');
  };

  const closeModal = () => {
    setSelectedHistory(null);
  };

  const formatTime = (timestamp) => {
    return timestamp;
  };

  return (
    <>
      <PanelContainer>
        <PanelHeader>
          <Title>
            <FiClock style={{ color: '#667eea' }} />
            이전 상담 내역
          </Title>
        </PanelHeader>

        <HistoryList>
          {sampleHistory.length === 0 ? (
            <EmptyState>
              <FiMessageSquare />
              <p>이전 상담 내역이 없습니다</p>
            </EmptyState>
          ) : (
            sampleHistory.map((item, index) => (
              <HistoryItem
                key={item.id}
                onClick={() => handleItemClick(item)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <HistoryDate>
                  <FiClock size={12} />
                  {item.date}
                </HistoryDate>
                <HistorySummary>
                  {item.summary}
                  <FiChevronRight size={16} color="#999" />
                </HistorySummary>
                <HistoryTags>
                  <HistoryTag $type={item.status}>
                    {item.status === 'resolved' ? '해결됨' : '진행중'}
                  </HistoryTag>
                  {item.tags.map((tag, idx) => (
                    <HistoryTag key={idx}>{tag}</HistoryTag>
                  ))}
                </HistoryTags>
              </HistoryItem>
            ))
          )}
        </HistoryList>
      </PanelContainer>

      {/* 상담 상세 모달 */}
      <AnimatePresence>
        {selectedHistory && (
          <ModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeModal}
          >
            <ModalContent
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ModalHeader>
                <ModalTitle>
                  <FiMessageSquare />
                  상담 상세 내역
                </ModalTitle>
                <CloseButton onClick={closeModal}>
                  <FiX size={20} />
                </CloseButton>
              </ModalHeader>

              <ModalBody>
                <TabContainer>
                  <Tab
                    $active={activeTab === 'summary'}
                    onClick={() => setActiveTab('summary')}
                  >
                    <FiZap style={{ marginRight: 4 }} />
                    AI 요약
                  </Tab>
                  <Tab
                    $active={activeTab === 'conversation'}
                    onClick={() => setActiveTab('conversation')}
                  >
                    <FiMessageSquare style={{ marginRight: 4 }} />
                    대화 내역
                  </Tab>
                </TabContainer>

                {activeTab === 'summary' ? (
                  <SummarySection>
                    <SummaryTitle>
                      <FiZap />
                      AI 상담 요약
                    </SummaryTitle>
                    <SummaryItem>
                      <SummaryLabel>상담일시:</SummaryLabel>
                      <SummaryValue>{selectedHistory.date}</SummaryValue>
                    </SummaryItem>
                    <SummaryItem>
                      <SummaryLabel>현재 요금제:</SummaryLabel>
                      <SummaryValue>{selectedHistory.aiSummary.currentPlan}</SummaryValue>
                    </SummaryItem>
                    <SummaryItem>
                      <SummaryLabel>요청 사항:</SummaryLabel>
                      <SummaryValue>{selectedHistory.aiSummary.requestedFeature}</SummaryValue>
                    </SummaryItem>
                    <SummaryItem>
                      <SummaryLabel>주요 관심:</SummaryLabel>
                      <SummaryValue>{selectedHistory.aiSummary.mainConcern}</SummaryValue>
                    </SummaryItem>
                    <SummaryItem>
                      <SummaryLabel>처리 결과:</SummaryLabel>
                      <SummaryValue>{selectedHistory.aiSummary.result}</SummaryValue>
                    </SummaryItem>
                  </SummarySection>
                ) : (
                  <ConversationContainer>
                    {selectedHistory.conversation.map((msg, idx) => (
                      <Message key={idx} $isAI={msg.speaker === 'ai'}>
                        <MessageSpeaker>
                          {msg.speaker === 'ai' ? 'AI 상담사' : '고객'}
                        </MessageSpeaker>
                        <MessageBubble $isAI={msg.speaker === 'ai'}>
                          {msg.content}
                        </MessageBubble>
                        <MessageTime>{formatTime(msg.timestamp)}</MessageTime>
                      </Message>
                    ))}
                  </ConversationContainer>
                )}
              </ModalBody>
            </ModalContent>
          </ModalOverlay>
        )}
      </AnimatePresence>
    </>
  );
};

export default ConsultationHistory;
