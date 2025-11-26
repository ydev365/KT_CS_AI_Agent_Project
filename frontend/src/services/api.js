import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 고객 인증
export const verifyCustomer = async (phoneNumber) => {
  const response = await api.post('/api/auth/verify', {
    phone_number: phoneNumber,
  });
  return response.data;
};

// 채팅 메시지 전송
export const sendMessage = async (sessionId, message) => {
  const response = await api.post('/api/chat/message', {
    session_id: sessionId,
    message: message,
  });
  return response.data;
};

// 상담 종료
export const endChat = async (sessionId) => {
  const response = await api.post('/api/chat/end', {
    session_id: sessionId,
  });
  return response.data;
};

// 음성 파일 전사
export const transcribeAudio = async (audioBlob) => {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.webm');

  const response = await api.post('/api/stt/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// 상담 이력 조회
export const getHistory = async (phoneNumber) => {
  const response = await api.get(`/api/history/${phoneNumber}`);
  return response.data;
};

// 세션 상세 조회
export const getSessionDetail = async (sessionId) => {
  const response = await api.get(`/api/history/session/${sessionId}`);
  return response.data;
};

export default api;
