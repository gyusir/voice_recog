"""회의 녹취록 포맷팅 모듈.

VibeVoice-ASR 출력 세그먼트를 사람이 읽기 쉬운 텍스트 형식으로 변환한다.
"""

from datetime import datetime


def normalize_timestamp(ts: str) -> str:
    """타임스탬프를 HH:MM:SS 형식으로 정규화한다.

    Args:
        ts: "0:00:05", "1:23:45" 등의 타임스탬프 문자열

    Returns:
        "[HH:MM:SS]" 형식의 문자열
    """
    parts = ts.strip().split(":")
    if len(parts) == 2:
        parts = ["00"] + parts
    return ":".join(p.zfill(2) for p in parts)


def map_speaker_ids(segments: list[dict]) -> dict[str, str]:
    """세그먼트에서 등장하는 화자 ID를 화자A, 화자B, ... 순서로 매핑한다."""
    seen = {}
    labels = "ABCDEFGHIJ"
    for seg in segments:
        sid = seg.get("speaker_id", "Unknown")
        if sid not in seen and len(seen) < len(labels):
            seen[sid] = f"화자{labels[len(seen)]}"
    return seen


def format_segments(segments: list[dict], filename: str) -> str:
    """ASR 출력 세그먼트를 포맷된 녹취록 텍스트로 변환한다.

    Args:
        segments: post_process_transcription() 결과 리스트
            [{"start_time": "0:00:00", "end_time": "0:00:05",
              "speaker_id": "Speaker 1", "text": "..."}]
        filename: 원본 오디오 파일명

    Returns:
        포맷된 녹취록 문자열
    """
    speaker_map = map_speaker_ids(segments)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("=" * 50)
    lines.append("회의 녹취록")
    lines.append(f"파일: {filename}")
    lines.append(f"생성일시: {now}")
    lines.append("=" * 50)
    lines.append("")

    for seg in segments:
        ts = normalize_timestamp(seg.get("start_time", "0:00:00"))
        speaker = speaker_map.get(seg.get("speaker_id", "Unknown"), "화자?")
        text = seg.get("text", "").strip()
        lines.append(f"[{ts}] {speaker}: {text}")

    lines.append("")
    lines.append("=" * 50)

    speakers = ", ".join(sorted(set(speaker_map.values())))
    lines.append(f"화자 목록: {speakers}")
    lines.append(f"총 발화 수: {len(segments)}")
    lines.append("=" * 50)

    return "\n".join(lines)
