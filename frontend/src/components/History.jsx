import React, { useState, useEffect } from 'react';
import { getHistory, getSessionDetail } from '../services/api';

function History({ phoneNumber, onBack }) {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchHistory = async () => {
      if (!phoneNumber) {
        setLoading(false);
        return;
      }

      try {
        const data = await getHistory(phoneNumber.replace(/-/g, ''));
        setSessions(data);
      } catch (err) {
        setError('상담 이력을 불러오는데 실패했습니다.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [phoneNumber]);

  const handleSessionClick = async (sessionId) => {
    try {
      const detail = await getSessionDetail(sessionId);
      setSelectedSession(detail);
    } catch (err) {
      console.error('세션 상세 조회 실패:', err);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!phoneNumber) {
    return (
      <div className="history">
        <div className="history-header">
          <button className="back-btn" onClick={onBack}>
            ←
          </button>
          <h2>상담 이력</h2>
        </div>
        <div className="history-content">
          <p style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
            전화번호를 먼저 입력해주세요.
          </p>
        </div>
      </div>
    );
  }

  if (selectedSession) {
    return (
      <div className="history">
        <div className="history-header">
          <button className="back-btn" onClick={() => setSelectedSession(null)}>
            ←
          </button>
          <h2>상담 상세</h2>
        </div>
        <div className="history-content">
          <div className="history-item" style={{ cursor: 'default' }}>
            <div className="date">{formatDate(selectedSession.session_start)}</div>
            {selectedSession.summary && (
              <div className="summary">
                <strong>요약:</strong> {selectedSession.summary}
              </div>
            )}
          </div>

          <div style={{ marginTop: '16px' }}>
            {selectedSession.messages?.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                {msg.role === 'assistant' && <div className="avatar">KT</div>}
                <div className="message-bubble">{msg.content}</div>
                {msg.role === 'user' && <div className="avatar">나</div>}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="history">
      <div className="history-header">
        <button className="back-btn" onClick={onBack}>
          ←
        </button>
        <h2>상담 이력</h2>
      </div>
      <div className="history-content">
        {loading ? (
          <div className="loading">
            <div className="loading-spinner"></div>
          </div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : sessions.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
            이전 상담 내역이 없습니다.
          </p>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className="history-item"
              onClick={() => handleSessionClick(session.id)}
            >
              <div className="date">{formatDate(session.session_start)}</div>
              <div className={session.summary ? 'summary' : 'summary no-summary'}>
                {session.summary || '요약 없음'}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default History;
