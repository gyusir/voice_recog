"""회의 녹취록 생성 파이프라인.

Google Colab 환경에서 VibeVoice-ASR-7B를 사용하여
m4a 오디오 파일을 텍스트 녹취록으로 변환한다.
"""

import os
import shutil
import time

import torch
from tqdm import tqdm

from converter import validate_audio_file, get_audio_duration
from formatter import format_segments


def find_unprocessed_files(input_dir: str, processed_file: str) -> list[str]:
    """input_dir에서 아직 처리되지 않은 오디오 파일 목록을 반환한다."""
    processed = set()
    if os.path.exists(processed_file):
        with open(processed_file, "r", encoding="utf-8") as f:
            processed = {line.strip() for line in f if line.strip()}

    files = []
    for fname in sorted(os.listdir(input_dir)):
        if fname.lower().endswith(".m4a") and fname not in processed:
            files.append(os.path.join(input_dir, fname))
    return files


def load_model(cache_dir: str):
    """VibeVoice-ASR 모델과 프로세서를 로드한다.

    cache_dir에 모델이 캐시되어 있으면 바로 로드하고,
    없으면 HuggingFace에서 다운로드 후 캐시한다.

    Returns:
        (model, processor) 튜플
    """
    from vibevoice.modular.modeling_vibevoice_asr import (
        VibeVoiceASRForConditionalGeneration,
    )
    from vibevoice.processor.vibevoice_asr_processor import VibeVoiceASRProcessor

    model_id = "microsoft/VibeVoice-ASR"

    cached = os.path.exists(os.path.join(cache_dir, "config.json"))
    if cached:
        print("캐시된 모델을 로드합니다...")
        load_path = cache_dir
    else:
        print("모델을 처음 다운로드합니다. 약 10분 소요됩니다...")
        load_path = model_id

    processor = VibeVoiceASRProcessor.from_pretrained(
        load_path, cache_dir=cache_dir, trust_remote_code=True
    )
    model = VibeVoiceASRForConditionalGeneration.from_pretrained(
        load_path,
        cache_dir=cache_dir,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation="sdpa",
        trust_remote_code=True,
    )
    model.eval()

    # 최초 다운로드 시 캐시 디렉토리에 저장
    if not cached:
        print("모델을 Drive에 캐시합니다...")
        model.save_pretrained(cache_dir)
        processor.save_pretrained(cache_dir)

    print(f"모델 로드 완료! (VRAM 사용: {torch.cuda.memory_allocated() / 1e9:.1f} GB)")
    return model, processor


def transcribe_file(model, processor, audio_path: str) -> list[dict]:
    """단일 오디오 파일을 텍스트로 변환한다.

    Returns:
        세그먼트 리스트: [{"start_time", "end_time", "speaker_id", "text"}]
    """
    inputs = processor(
        audio=audio_path,
        sampling_rate=None,
        return_tensors="pt",
        add_generation_prompt=True,
        context_info="Korean and English mixed conversation",
    )
    inputs = {
        k: v.to("cuda") if isinstance(v, torch.Tensor) else v
        for k, v in inputs.items()
    }

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=32768,
            temperature=0.0,
            pad_token_id=processor.pad_id,
            eos_token_id=processor.tokenizer.eos_token_id,
        )

    generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]
    generated_text = processor.decode(generated_ids, skip_special_tokens=True)
    segments = processor.post_process_transcription(generated_text)
    return segments


def mark_as_processed(filename: str, processed_file: str) -> None:
    """처리 완료된 파일명을 .processed 파일에 추가한다."""
    with open(processed_file, "a", encoding="utf-8") as f:
        f.write(filename + "\n")
        f.flush()


def run_pipeline(
    input_dir: str,
    output_dir: str,
    cache_dir: str,
    processed_file: str,
) -> None:
    """전체 파이프라인을 실행한다.

    1. 미처리 파일 탐색
    2. 모델 로드
    3. 파일별 순차 처리
    4. 결과 저장
    """
    files = find_unprocessed_files(input_dir, processed_file)

    if not files:
        print("처리할 새로운 파일이 없습니다.")
        return

    print(f"\n{len(files)}개의 파일을 처리합니다.\n")

    model, processor = load_model(cache_dir)

    results = []
    temp_dir = "/content/temp"
    os.makedirs(temp_dir, exist_ok=True)

    for i, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)
        print(f"\n[{i}/{len(files)}] 처리 중: {filename}")

        # 파일 검증
        is_valid, error_msg = validate_audio_file(filepath)
        if not is_valid:
            print(f"  건너뜀: {error_msg}")
            _write_error_file(output_dir, filename, error_msg)
            continue

        # 오디오 길이 확인
        duration = get_audio_duration(filepath)
        if duration > 0:
            print(f"  오디오 길이: {duration / 60:.1f}분")
            if duration > 3600:
                print("  경고: 60분 초과 파일입니다. 처리가 불안정할 수 있습니다.")

        try:
            # Drive I/O 병목 방지: 로컬에 복사 후 처리
            local_path = os.path.join(temp_dir, filename)
            shutil.copy2(filepath, local_path)

            start_time = time.time()
            segments = transcribe_file(model, processor, local_path)
            elapsed = time.time() - start_time

            # 결과 포맷팅 및 저장
            output_text = format_segments(segments, filename)
            output_name = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_dir, output_name)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_text)

            mark_as_processed(filename, processed_file)

            speaker_count = len(set(s.get("speaker_id", "") for s in segments))
            results.append({
                "파일": filename,
                "길이": f"{duration / 60:.1f}분" if duration > 0 else "?",
                "화자 수": speaker_count,
                "발화 수": len(segments),
                "처리 시간": f"{elapsed:.0f}초",
                "결과": output_name,
            })
            print(f"  완료! ({elapsed:.0f}초, 화자 {speaker_count}명, 발화 {len(segments)}건)")

            # 임시 파일 정리 및 GPU 메모리 해제
            os.remove(local_path)
            torch.cuda.empty_cache()

        except Exception as e:
            print(f"  오류 발생: {e}")
            _write_error_file(output_dir, filename, str(e))
            torch.cuda.empty_cache()

    # 최종 요약
    print("\n" + "=" * 50)
    print("처리 완료 요약")
    print("=" * 50)
    for r in results:
        print(f"  {r['파일']} → {r['결과']} ({r['처리 시간']}, 화자 {r['화자 수']}명)")
    print(f"\n총 {len(results)}/{len(files)}개 파일 처리 완료")


def _write_error_file(output_dir: str, filename: str, error: str) -> None:
    """에러 정보를 파일로 저장한다."""
    error_name = os.path.splitext(filename)[0] + "_ERROR.txt"
    error_path = os.path.join(output_dir, error_name)
    with open(error_path, "w", encoding="utf-8") as f:
        f.write(f"파일: {filename}\n")
        f.write(f"오류: {error}\n")
