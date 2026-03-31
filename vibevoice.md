# VibeVoice

> Microsoft의 오픈소스 음성 AI 모델 패밀리 (TTS + ASR)

- **GitHub**: https://github.com/microsoft/VibeVoice
- **Project Page**: https://microsoft.github.io/VibeVoice
- **HuggingFace**: `microsoft/vibevoice`
- **라이선스**: MIT

## 핵심 기술

- **연속 음성 토크나이저**: 7.5 Hz 초저 프레임레이트로 동작 (Acoustic + Semantic)
- **Next-Token Diffusion**: LLM의 자기회귀 토큰 예측 + Diffusion 기반 음향 생성을 결합

## 모델 구성

| 모델 | 파라미터 | 용도 | 주요 특징 |
|---|---|---|---|
| **VibeVoice-ASR-7B** | 7B | 장문 음성 인식 | 60분 오디오 단일 패스 처리, 64K 토큰, 화자 ID/타임스탬프, 핫워드 지원, 50+ 언어 |
| **VibeVoice-TTS-1.5B** | 1.5B | 장문 다화자 TTS | 최대 90분, 4명 화자, 영어/중국어/크로스링구얼, 노래 가능 |
| **VibeVoice-Realtime-0.5B** | 0.5B | 실시간 스트리밍 TTS | ~300ms 첫 음성 지연, 스트리밍 텍스트 입력, ~10분 생성 |

## 지원 언어

- **ASR**: 50+ 언어 (한국어 포함)
- **TTS**: 영어, 독일어, 프랑스어, 이탈리아어, 일본어, 한국어, 네덜란드어, 폴란드어, 포르투갈어, 스페인어 등
- **크로스링구얼**: 영어-중국어 TTS

## 설치 요구사항

- **Python**: 3.9+
- **설치**: `pip install -e .`
- **ASR 파인튜닝 시**: `pip install peft` 추가

### 주요 의존성

- `torch`, `transformers>=4.51.3`, `diffusers`, `accelerate`
- `librosa` (오디오 처리)
- `fastapi`, `uvicorn` (서빙)
- `aiortc` (실시간 통신)
- `gradio` (웹 UI)

## 파이프라인

### ASR
```
오디오 입력 → 7.5Hz 연속 토크나이징 → 7B LLM (64K 토큰) → 화자 ID + 타임스탬프 + 텍스트
```

### TTS
```
텍스트 입력 → LLM 토큰 생성 → Diffusion 음향 디코딩 → 파형 출력
```

## ASR 파인튜닝 (LoRA)

- **데이터 형식**: MP3 오디오 + JSON 어노테이션 (audio_duration, audio_path, segments)
- **기본 하이퍼파라미터**: rank=16, alpha=32, dropout=0.05, lr=5e-5
- Gradient checkpointing 지원, PEFT `merge_and_unload()`로 LoRA 가중치 병합 가능

## 데모 및 실행

- `vibevoice_asr_gradio_demo.py` — Gradio 기반 ASR 데모
- `vibevoice_asr_inference_from_file.py` — 파일 기반 ASR 추론
- `vibevoice_realtime_demo.py` — 실시간 TTS 데모
- `vibevoice_realtime_colab.ipynb` — Google Colab 노트북
- 온라인 플레이그라운드: `aka.ms/vibevoice-asr`

## 관련 논문

- TTS Report: `arxiv.org/pdf/2508.19205`
- ASR Report: `arxiv.org/pdf/2601.18184`

## 참고사항

- vLLM 플러그인을 통한 최적화된 추론 서빙 지원
- 멀티 GPU 학습 지원 (`torchrun`, 최대 4 GPU)
- 2026-03-06 기준 HuggingFace Transformers에 통합
- Responsible AI 정책에 따라 독립 TTS 코드는 제거됨 (2025-09)
