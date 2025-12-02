from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
import base64

from ..schemas.voice import TTSRequest, TTSResponse, STTResponse
from ..services.voice_service import voice_service

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(audio: UploadFile = File(...)):
    """
    음성을 텍스트로 변환 (STT)

    - 지원 포맷: webm, mp3, wav, m4a, ogg
    - 한국어 자동 인식
    """
    try:
        # 파일 읽기
        audio_data = await audio.read()

        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="오디오 파일이 비어있습니다")

        # STT 변환
        text = await voice_service.speech_to_text(
            audio_data,
            filename=audio.filename or "audio.webm"
        )

        return STTResponse(text=text, language="ko")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"음성 인식 중 오류 발생: {str(e)}")


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    텍스트를 음성으로 변환 (TTS)

    - Base64 인코딩된 MP3 오디오 반환
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다")

        audio_base64 = await voice_service.text_to_speech_base64(
            request.text,
            request.voice
        )

        return TTSResponse(
            audio_base64=audio_base64,
            content_type="audio/mpeg"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"음성 합성 중 오류 발생: {str(e)}")


@router.post("/tts/audio")
async def text_to_speech_audio(request: TTSRequest):
    """
    텍스트를 음성으로 변환 (TTS) - 직접 오디오 파일 반환

    - MP3 오디오 파일로 응답
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다")

        audio_data = await voice_service.text_to_speech(
            request.text,
            request.voice
        )

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"음성 합성 중 오류 발생: {str(e)}")
