import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import VoiceInput from './VoiceInput';
import { sendMessage, endChat } from '../services/api';

function ChatRoom({ sessionId, initialMessage, customer, onEnd }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showEndModal, setShowEndModal] = useState(false);
  const [requiresHumanAgent, setRequiresHumanAgent] = useState(false);

  useEffect(() => {
    if (initialMessage) {
      setMessages([{ role: 'assistant', content: initialMessage }]);
    }
  }, [initialMessage]);

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage = inputText.trim();
    setInputText('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await sendMessage(sessionId, userMessage);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.assistant_message },
      ]);

      if (response.requires_human_agent) {
        setRequiresHumanAgent(true);
      }
    } catch (err) {
      console.error('메시지 전송 오류:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceInput = (text) => {
    setInputText(text);
  };

  const handleEndChat = async () => {
    try {
      const result = await endChat(sessionId);
      onEnd(result);
    } catch (err) {
      console.error('상담 종료 오류:', err);
      onEnd(null);
    }
  };

  return (
    <div className="chat-room">
      <div className="chat-header">
        <div className="title">
          {customer?.name ? `${customer.name}님` : 'KT AI 상담'}
        </div>
        <button className="end-btn" onClick={() => setShowEndModal(true)}>
          상담 종료
        </button>
      </div>

      {requiresHumanAgent && (
        <div className="human-agent-notice">
          <h4>상담원 연결 안내</h4>
          <p>
            전문 상담원 연결을 요청하셨습니다.
            <br />
            잠시 후 상담원이 연결됩니다.
          </p>
        </div>
      )}

      <MessageList messages={messages} isLoading={isLoading} />

      <div className="chat-input">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="메시지를 입력하세요..."
          rows={1}
          disabled={isLoading}
        />
        <VoiceInput onTranscribed={handleVoiceInput} disabled={isLoading} />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={!inputText.trim() || isLoading}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>

      {showEndModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>상담을 종료하시겠습니까?</h3>
            <p>상담 내용이 요약되어 저장됩니다.</p>
            <div className="buttons">
              <button
                className="cancel-btn"
                onClick={() => setShowEndModal(false)}
              >
                계속 상담
              </button>
              <button className="confirm-btn" onClick={handleEndChat}>
                종료하기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatRoom;
