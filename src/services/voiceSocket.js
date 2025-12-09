import { io } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class VoiceSocketService {
  constructor() {
    this.socket = null;
    this.sessionId = null;
    this.pendingListeners = [];
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

    // 대기 중인 리스너 등록
    this.pendingListeners.forEach(({ event, callback }) => {
      this.socket.on(event, callback);
    });
    this.pendingListeners = [];

    this.socket.on('connect', () => {
      console.log('Voice socket connected:', this.socket.id);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Voice socket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Voice socket connection error:', error);
    });

    return this.socket;
  }

  // 리스너 등록 헬퍼 (연결 전에도 등록 가능)
  _addListener(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    } else {
      this.pendingListeners.push({ event, callback });
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.sessionId = null;
    }
  }

  // 음성 세션 시작
  startVoiceSession(sessionId, customerInfo) {
    if (!this.socket?.connected) {
      this.connect();
    }

    this.sessionId = sessionId;
    this.socket.emit('start_voice_session', {
      sessionId,
      customerInfo
    });
  }

  // 음성 입력 전송 (Base64 인코딩된 오디오)
  sendVoiceInput(audioBase64) {
    if (this.socket?.connected && this.sessionId) {
      this.socket.emit('voice_input', {
        sessionId: this.sessionId,
        audio: audioBase64
      });
    }
  }

  // 텍스트 입력 전송
  sendTextInput(text) {
    if (this.socket?.connected && this.sessionId) {
      this.socket.emit('text_input', {
        sessionId: this.sessionId,
        text
      });
    }
  }

  // 음성 세션 종료
  endVoiceSession() {
    if (this.socket?.connected && this.sessionId) {
      this.socket.emit('end_voice_session', {
        sessionId: this.sessionId
      });
    }
  }

  // 세션 시작 리스너
  onSessionStarted(callback) {
    this._addListener('voice_session_started', callback);
  }

  // 고객 메시지 리스너
  onCustomerMessage(callback) {
    this._addListener('customer_message', callback);
  }

  // AI 응답 리스너 (기존 호환용)
  onVoiceResponse(callback) {
    this._addListener('voice_response', callback);
  }

  // AI 텍스트 응답 리스너 (스트리밍용 - 텍스트 먼저 수신)
  onAITextResponse(callback) {
    this._addListener('ai_text_response', callback);
  }

  // TTS 스트리밍 시작 리스너
  onTTSStreamStart(callback) {
    this._addListener('tts_stream_start', callback);
  }

  // TTS 스트리밍 청크 리스너
  onTTSStreamChunk(callback) {
    this._addListener('tts_stream_chunk', callback);
  }

  // TTS 스트리밍 종료 리스너
  onTTSStreamEnd(callback) {
    this._addListener('tts_stream_end', callback);
  }

  // 세션 에러 리스너
  onSessionError(callback) {
    this._addListener('session_error', callback);
  }

  // 상담 완료 리스너
  onConsultationCompleted(callback) {
    this._addListener('consultation:completed', callback);
  }

  // 연결 성공 리스너
  onConnectionSuccess(callback) {
    this._addListener('connection_success', callback);
  }

  // 리스너 제거
  removeListener(event) {
    if (this.socket) {
      this.socket.off(event);
    }
  }

  // 모든 리스너 제거
  removeAllListeners() {
    this.pendingListeners = [];
    if (this.socket) {
      this.socket.removeAllListeners();
    }
  }
}

// 싱글톤 인스턴스
const voiceSocket = new VoiceSocketService();

export default voiceSocket;
