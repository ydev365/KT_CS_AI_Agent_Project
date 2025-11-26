from openai import OpenAI
from typing import Tuple
import tempfile
import os
from config import get_settings

settings = get_settings()


class STTService:
    """Whisper 기반 STT 서비스"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def transcribe_audio(self, audio_data: bytes, filename: str = "audio.webm") -> Tuple[bool, str]:
        """
        음성 데이터를 텍스트로 변환

        Args:
            audio_data: 오디오 파일 바이트 데이터
            filename: 원본 파일명 (확장자 추출용)

        Returns:
            (success, transcribed_text or error_message)
        """
        try:
            # 임시 파일로 저장
            ext = os.path.splitext(filename)[1] or ".webm"
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name

            try:
                # Whisper API 호출
                with open(tmp_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ko",  # 한국어
                        response_format="text"
                    )

                return True, transcript.strip()

            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        except Exception as e:
            return False, f"음성 인식 중 오류가 발생했습니다: {str(e)}"

    def transcribe_file(self, file_path: str) -> Tuple[bool, str]:
        """
        파일 경로로부터 음성을 텍스트로 변환

        Args:
            file_path: 오디오 파일 경로

        Returns:
            (success, transcribed_text or error_message)
        """
        try:
            with open(file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ko",
                    response_format="text"
                )

            return True, transcript.strip()

        except FileNotFoundError:
            return False, f"파일을 찾을 수 없습니다: {file_path}"
        except Exception as e:
            return False, f"음성 인식 중 오류가 발생했습니다: {str(e)}"
