import base64
import tempfile
import os
from io import BytesIO
from typing import Optional
from openai import OpenAI

from ..core.config import settings


class VoiceService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _detect_audio_format(self, audio_data: bytes) -> str:
        """오디오 데이터의 형식 감지"""
        # WebM 시그니처: 0x1A 0x45 0xDF 0xA3
        if audio_data[:4] == b'\x1a\x45\xdf\xa3':
            return 'webm'
        # OGG 시그니처: OggS
        if audio_data[:4] == b'OggS':
            return 'ogg'
        # MP3 시그니처: ID3 또는 0xFF 0xFB
        if audio_data[:3] == b'ID3' or audio_data[:2] == b'\xff\xfb':
            return 'mp3'
        # WAV 시그니처: RIFF
        if audio_data[:4] == b'RIFF':
            return 'wav'
        # FLAC 시그니처: fLaC
        if audio_data[:4] == b'fLaC':
            return 'flac'
        # M4A/MP4 시그니처: ftyp (offset 4)
        if len(audio_data) > 8 and audio_data[4:8] == b'ftyp':
            return 'm4a'
        # 기본값
        return 'webm'

    async def speech_to_text(
        self,
        audio_data: bytes,
        filename: str = None
    ) -> str:
        """
        음성을 텍스트로 변환 (Whisper API)

        Args:
            audio_data: 오디오 바이너리 데이터
            filename: 파일명 (확장자로 포맷 결정)

        Returns:
            인식된 텍스트
        """
        # 오디오 데이터 검증
        audio_size = len(audio_data)
        print(f"[STT] Audio data size: {audio_size} bytes")

        if audio_size < 1000:
            print(f"[STT] Warning: Audio data too small ({audio_size} bytes)")
            return ""

        # 오디오 형식 감지
        detected_format = self._detect_audio_format(audio_data)

        if filename is None:
            filename = f"audio.{detected_format}"

        print(f"[STT] Detected format: {detected_format}, filename: {filename}")
        print(f"[STT] First 20 bytes: {audio_data[:20].hex()}")

        # 임시 파일로 저장하여 처리 (더 안정적)
        with tempfile.NamedTemporaryFile(suffix=f".{detected_format}", delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name

        print(f"[STT] Temp file saved: {tmp_file_path}")

        try:
            # 파일로 열어서 Whisper API 호출
            with open(tmp_file_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=settings.WHISPER_MODEL,
                    file=audio_file,
                    language="ko",
                    response_format="text"
                )

            result = response.strip()
            print(f"[STT] Transcription result: '{result}'")
            return result
        except Exception as e:
            print(f"[STT] Error: {e}")
            raise
        finally:
            # 임시 파일 삭제
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    def _normalize_for_tts(self, text: str) -> str:
        """TTS 발음 교정"""
        import re

        # 순서 중요: 먼저 5G/4G 네트워크 명칭 처리 (숫자+G 패턴)
        text = re.sub(r'5G', '파이브지', text)
        text = re.sub(r'4G', '포지', text)

        # 숫자+GB 패턴 (예: 14GB → 14기가바이트)
        def replace_gb(match):
            num = match.group(1)
            return f"{num}기가바이트"
        text = re.sub(r'(\d+)GB', replace_gb, text)

        # 숫자+MB 패턴
        def replace_mb(match):
            num = match.group(1)
            return f"{num}메가바이트"
        text = re.sub(r'(\d+)MB', replace_mb, text)

        # 숫자+Mbps 패턴 (예: 5Mbps → 5엠비피에스)
        def replace_mbps(match):
            num = match.group(1)
            return f"{num}엠비피에스"
        text = re.sub(r'(\d+)Mbps', replace_mbps, text)

        # 숫자+Kbps 패턴 (예: 400Kbps → 400케이비피에스)
        def replace_kbps(match):
            num = match.group(1)
            return f"{num}케이비피에스"
        text = re.sub(r'(\d+)Kbps', replace_kbps, text)

        # 금액 패턴 처리 (예: 37,000원 → 삼만칠천원)
        def number_to_korean(num_str):
            """숫자를 한글로 변환"""
            num = int(num_str.replace(',', ''))
            if num == 0:
                return "영"

            units = ['', '만', '억', '조']
            small_units = ['', '십', '백', '천']
            digits = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']

            result = []
            unit_idx = 0

            while num > 0:
                part = num % 10000
                if part > 0:
                    part_str = ''
                    for i in range(4):
                        digit = part % 10
                        if digit > 0:
                            # 일십, 일백, 일천에서 '일' 생략
                            if digit == 1 and i > 0:
                                part_str = small_units[i] + part_str
                            else:
                                part_str = digits[digit] + small_units[i] + part_str
                        part = part // 10
                    result.append(part_str + units[unit_idx])
                num = num // 10000
                unit_idx += 1

            return ''.join(reversed(result))

        def replace_price(match):
            num_str = match.group(1)
            return number_to_korean(num_str) + "원"

        # 쉼표 있는 금액 (예: 37,000원)
        text = re.sub(r'([\d,]+)원', replace_price, text)

        # 단순 치환
        simple_replacements = {
            "LTE": "엘티이",
            "KT": "케이티",
            "OTT": "오티티",
            "IPTV": "아이피티비",
            "VIP": "브이아이피",
            "VVIP": "브이브이아이피",
        }
        for key, value in simple_replacements.items():
            text = text.replace(key, value)

        return text

    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """
        텍스트를 음성으로 변환 (OpenAI TTS)

        Args:
            text: 변환할 텍스트
            voice: 음성 종류 (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            MP3 오디오 바이너리 데이터
        """
        voice = voice or settings.TTS_VOICE

        # 발음 교정
        normalized_text = self._normalize_for_tts(text)

        response = self.client.audio.speech.create(
            model=settings.TTS_MODEL,
            voice=voice,
            input=normalized_text,
            response_format="mp3"
        )

        return response.content

    async def text_to_speech_base64(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> str:
        """
        텍스트를 음성으로 변환하고 Base64로 인코딩

        Args:
            text: 변환할 텍스트
            voice: 음성 종류

        Returns:
            Base64 인코딩된 오디오 문자열
        """
        audio_data = await self.text_to_speech(text, voice)
        return base64.b64encode(audio_data).decode('utf-8')


# 싱글톤 인스턴스
voice_service = VoiceService()
