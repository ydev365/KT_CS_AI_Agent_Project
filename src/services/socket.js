import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect() {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(SOCKET_URL, {
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket.id);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });

    this.socket.on('connection_success', (data) => {
      console.log('Connection success:', data);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // 상담 세션 참가
  joinConsultation(consultationId) {
    if (this.socket?.connected) {
      this.socket.emit('join_consultation', { consultationId });
    }
  }

  // 상담 세션 떠나기
  leaveConsultation(consultationId) {
    if (this.socket?.connected) {
      this.socket.emit('leave_consultation', { consultationId });
    }
  }

  // 상담 업데이트 리스너
  onConsultationUpdate(callback) {
    if (this.socket) {
      this.socket.on('consultation:updated', callback);
    }
  }

  // 새 메시지 리스너
  onNewMessage(callback) {
    if (this.socket) {
      this.socket.on('consultation:message-added', callback);
    }
  }

  // 상태 변경 리스너
  onStatusChange(callback) {
    if (this.socket) {
      this.socket.on('consultation:status-change', callback);
    }
  }

  // 리스너 제거
  removeListener(event) {
    if (this.socket) {
      this.socket.off(event);
    }
  }

  // 모든 리스너 제거
  removeAllListeners() {
    if (this.socket) {
      this.socket.removeAllListeners();
    }
  }
}

// 싱글톤 인스턴스
const socketService = new SocketService();

export default socketService;
