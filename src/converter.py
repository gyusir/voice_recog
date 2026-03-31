"""오디오 파일 유틸리티 모듈.

오디오 파일 검증, 메타데이터 조회 등을 담당한다.
VibeVoice가 m4a를 네이티브 지원하므로 포맷 변환은 불필요.
"""

import os
import shutil
import subprocess


SUPPORTED_EXTENSIONS = {".m4a", ".mp3", ".wav", ".mp4", ".aac", ".ogg", ".flac", ".webm"}


def ensure_ffmpeg() -> bool:
    """ffmpeg가 시스템에 설치되어 있는지 확인한다."""
    return shutil.which("ffmpeg") is not None


def validate_audio_file(filepath: str) -> tuple[bool, str]:
    """오디오 파일이 유효한지 검증한다.

    Returns:
        (is_valid, error_message) 튜플
    """
    if not os.path.exists(filepath):
        return False, f"파일이 존재하지 않습니다: {filepath}"

    size = os.path.getsize(filepath)
    if size < 1024:
        return False, f"파일이 너무 작습니다 ({size} bytes): {filepath}"

    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"지원하지 않는 형식입니다 ({ext}): {filepath}"

    return True, ""


def get_audio_duration(filepath: str) -> float:
    """ffprobe를 사용하여 오디오 파일의 길이(초)를 반환한다.

    ffprobe가 없으면 -1.0을 반환한다.
    """
    if not shutil.which("ffprobe"):
        return -1.0

    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                filepath,
            ],
            capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired):
        return -1.0
