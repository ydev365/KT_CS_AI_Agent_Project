import socketio
import base64
from typing import Optional, Dict
from datetime import datetime

# Socket.IO 서버 인스턴스 생성
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=False
)

# 음성 세션 관리
voice_sessions: Dict[str, dict] = {}


@sio.event
async def connect(sid, environ, auth):
    """클라이언트 연결 이벤트"""
    print(f"Client connected: {sid}")
    await sio.emit('connection_success', {'message': '연결되었습니다', 'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    """클라이언트 연결 해제 이벤트"""
    print(f"Client disconnected: {sid}")
    # 음성 세션 정리
    sessions_to_remove = [k for k, v in voice_sessions.items() if v.get('sid') == sid]
    for session_id in sessions_to_remove:
        del voice_sessions[session_id]


@sio.event
async def join_consultation(sid, data):
    """상담 세션 참가 (상담사 대시보드용)"""
    consultation_id = data.get('consultationId')
    if consultation_id:
        await sio.enter_room(sid, f"consultation_{consultation_id}")
        await sio.emit('joined_consultation', {
            'consultationId': consultation_id,
            'message': f'상담 {consultation_id}에 참가했습니다'
        }, room=sid)


@sio.event
async def leave_consultation(sid, data):
    """상담 세션 떠나기"""
    consultation_id = data.get('consultationId')
    if consultation_id:
        await sio.leave_room(sid, f"consultation_{consultation_id}")


# ==================== 음성 상담 세션 이벤트 ====================

@sio.event
async def start_voice_session(sid, data):
    """음성 상담 세션 시작"""
    session_id = data.get('sessionId')
    customer_info = data.get('customerInfo')

    if not session_id:
        await sio.emit('session_error', {'error': 'sessionId가 필요합니다'}, room=sid)
        return

    # 세션 저장
    voice_sessions[session_id] = {
        'sid': sid,
        'customer_info': customer_info,
        'started_at': datetime.now().isoformat()
    }

    # 상담 룸 참가
    await sio.enter_room(sid, f"voice_{session_id}")

    await sio.emit('voice_session_started', {
        'sessionId': session_id,
        'message': '음성 상담 세션이 시작되었습니다'
    }, room=sid)


@sio.event
async def voice_input(sid, data):
    """음성 입력 처리 (STT → AI → TTS)"""
    session_id = data.get('sessionId')
    audio_base64 = data.get('audio')

    if not session_id or session_id not in voice_sessions:
        await sio.emit('session_error', {'error': '유효하지 않은 세션입니다'}, room=sid)
        return

    try:
        from .services.voice_service import voice_service
        from .services.session_service import session_service
        from .routers.chat import active_agents

        # Base64 디코딩
        audio_data = base64.b64decode(audio_base64)

        # STT 변환
        text = await voice_service.speech_to_text(audio_data)

        # 고객 메시지 저장
        session_service.add_message(session_id, {
            'speaker': 'customer',
            'content': text,
            'timestamp': datetime.now().isoformat()
        })

        # 고객 메시지 브로드캐스트
        await sio.emit('customer_message', {
            'sessionId': session_id,
            'text': text,
            'timestamp': datetime.now().isoformat()
        }, room=f"voice_{session_id}")

        # AI 에이전트 응답 생성
        agent = active_agents.get(session_id)
        if not agent:
            await sio.emit('session_error', {'error': 'AI 에이전트가 초기화되지 않았습니다'}, room=sid)
            return

        response = await agent.process_message(text)
        print(f"[VOICE INPUT] AI response - text: '{response.text[:50]}...', should_end: {response.should_end}")

        # AI 응답 저장
        session_service.add_message(session_id, {
            'speaker': 'ai',
            'content': response.text,
            'timestamp': datetime.now().isoformat()
        })

        # TTS 변환
        response_audio = await voice_service.text_to_speech_base64(response.text)

        # AI 응답 전송
        await sio.emit('voice_response', {
            'sessionId': session_id,
            'text': response.text,
            'audio': response_audio,
            'shouldEnd': response.should_end,
            'timestamp': datetime.now().isoformat()
        }, room=f"voice_{session_id}")

        # 상담 종료 시
        if response.should_end:
            print(f"[VOICE INPUT] Session ending, calling handle_session_end for {session_id}")
            await handle_session_end(session_id)

    except Exception as e:
        print(f"Voice input error: {e}")
        import traceback
        traceback.print_exc()
        await sio.emit('session_error', {
            'error': f'음성 처리 중 오류: {str(e)}'
        }, room=sid)


@sio.event
async def text_input(sid, data):
    """텍스트 입력 처리 (음성 없이 텍스트만)"""
    session_id = data.get('sessionId')
    text = data.get('text')

    if not session_id or session_id not in voice_sessions:
        await sio.emit('session_error', {'error': '유효하지 않은 세션입니다'}, room=sid)
        return

    try:
        from .services.voice_service import voice_service
        from .services.session_service import session_service
        from .routers.chat import active_agents

        # 고객 메시지 저장
        session_service.add_message(session_id, {
            'speaker': 'customer',
            'content': text,
            'timestamp': datetime.now().isoformat()
        })

        # AI 에이전트 응답 생성
        agent = active_agents.get(session_id)
        if not agent:
            await sio.emit('session_error', {'error': 'AI 에이전트가 초기화되지 않았습니다'}, room=sid)
            return

        response = await agent.process_message(text)

        # AI 응답 저장
        session_service.add_message(session_id, {
            'speaker': 'ai',
            'content': response.text,
            'timestamp': datetime.now().isoformat()
        })

        # TTS 변환
        response_audio = await voice_service.text_to_speech_base64(response.text)

        # AI 응답 전송
        await sio.emit('voice_response', {
            'sessionId': session_id,
            'text': response.text,
            'audio': response_audio,
            'shouldEnd': response.should_end,
            'timestamp': datetime.now().isoformat()
        }, room=f"voice_{session_id}")

        # 상담 종료 시
        if response.should_end:
            await handle_session_end(session_id)

    except Exception as e:
        print(f"Text input error: {e}")
        await sio.emit('session_error', {
            'error': f'처리 중 오류: {str(e)}'
        }, room=sid)


@sio.event
async def end_voice_session(sid, data):
    """음성 상담 세션 종료"""
    session_id = data.get('sessionId')

    if session_id:
        await handle_session_end(session_id)


async def handle_session_end(session_id: str):
    """상담 세션 종료 처리"""
    print(f"[SESSION END] Starting session end for: {session_id}")
    try:
        from .services.session_service import session_service
        from .services.summary_service import summary_service
        from .services.recommendation_service import recommendation_service
        from .routers.chat import active_agents

        # 세션 정보 조회
        session = session_service.get_session(session_id)
        if not session:
            print(f"[SESSION END] Session not found: {session_id}")
            return

        # 대화 기록 조회
        conversation = session_service.get_conversation(session_id)

        # 요약 및 추천 생성
        customer_info = session.customer_info.model_dump()

        summary = await summary_service.summarize_conversation(
            conversation=conversation,
            customer_info=customer_info
        )

        # 대화 기록을 스코어링용 형식으로 변환
        conversation_for_scoring = []
        for msg in conversation:
            speaker = 'customer' if msg.get('role') == 'user' else 'agent'
            conversation_for_scoring.append({
                'speaker': speaker,
                'content': msg.get('content', '')
            })

        recommendations = await recommendation_service.generate_recommendations(
            summary=summary,
            customer_info=customer_info,
            target_categories=session.customer_info.target_categories,
            conversation_history=conversation_for_scoring
        )

        # 상담 완료 이벤트 브로드캐스트 (음성 상담 클라이언트로)
        completion_data = {
            'sessionId': session_id,
            'customerInfo': customer_info,
            'conversation': conversation,
            'summary': summary.model_dump(),
            'recommendations': [r.model_dump() for r in recommendations],
            'completedAt': datetime.now().isoformat()
        }

        # 음성 세션 룸으로 전송 (VoiceConsultationPage가 수신)
        await sio.emit('consultation:completed', completion_data, room=f"voice_{session_id}")

        # 전체 브로드캐스트도 (대시보드가 수신)
        await sio.emit('consultation:completed', completion_data)

        print(f"Consultation completed event sent for session: {session_id}")

        # 세션 정리
        session_service.update_session_status(session_id, "ended")
        if session_id in active_agents:
            del active_agents[session_id]
        if session_id in voice_sessions:
            del voice_sessions[session_id]

    except Exception as e:
        import traceback
        print(f"[SESSION END] Error: {e}")
        traceback.print_exc()


# ==================== 브로드캐스트 함수 ====================

async def emit_consultation_update(consultation_id: str, data: dict):
    """상담 업데이트 브로드캐스트"""
    await sio.emit('consultation:updated', data, room=f"consultation_{consultation_id}")


async def emit_new_message(consultation_id: str, message: dict):
    """새 메시지 브로드캐스트"""
    await sio.emit('consultation:message-added', message, room=f"consultation_{consultation_id}")


async def emit_status_change(consultation_id: str, status: str):
    """상담 상태 변경 브로드캐스트"""
    await sio.emit('consultation:status-change', {
        'consultationId': consultation_id,
        'status': status
    }, room=f"consultation_{consultation_id}")
