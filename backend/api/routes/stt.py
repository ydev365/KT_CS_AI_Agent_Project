from fastapi import APIRouter, UploadFile, File, HTTPException
from services.stt_service import STTService
from schemas.models import STTResponse

router = APIRouter(prefix="/api/stt", tags=["STT"])


@router.post("/transcribe", response_model=STTResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    음성 파일을 텍스트로 변환 (Whisper API)

    지원 형식: mp3, mp4, mpeg, mpga, m4a, wav, webm
    """
    # 파일 형식 검증
    allowed_extensions = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"
        )

    # 파일 크기 제한 (25MB - Whisper API 제한)
    max_size = 25 * 1024 * 1024
    content = await file.read()

    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="파일 크기가 25MB를 초과했습니다."
        )

    # STT 처리
    stt_service = STTService()
    success, result = stt_service.transcribe_audio(content, file.filename)

    if success:
        return STTResponse(
            success=True,
            transcribed_text=result
        )
    else:
        return STTResponse(
            success=False,
            transcribed_text="",
            error=result
        )
