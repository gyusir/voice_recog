# TODO

## 우선순위 높음

- [ ] Colab에서 실제 m4a 파일로 전체 파이프라인 테스트
- [ ] T4 GPU에서 bf16 모델 로드 시 OOM 여부 확인

## 검토 필요

- [ ] **4-bit 양자화 적용 검토**
  - HuggingFace Transformers 통합 버전 (`microsoft/VibeVoice-ASR-HF`) 사용 시 `BitsAndBytesConfig`로 4-bit NF4 양자화 가능
  - VRAM 사용량: bf16 ~14GB → 4-bit ~6-8GB (T4 15.4GB 기준 훨씬 여유)
  - 장점: VibeVoice 레포 클론 불필요, `pip install transformers`만으로 설치, API 더 깔끔
  - 단점: 양자화에 의한 인식 품질 저하 가능성 (테스트 필요)
  - 참고: `DevParker/VibeVoice7b-low-vram` 사전 양자화 모델도 존재
  - **판단 기준**: bf16으로 OOM 발생 시 전환, 또는 품질 비교 후 결정

## 향후 개선

- [ ] 한국어 인식 품질 평가 (짧은 샘플로 테스트)
- [ ] 핫워드(고유명사) 기능 활용 테스트
- [ ] m4a 외 다른 형식(mp3, wav) 자동 감지 지원
- [ ] 회의록 요약 기능 추가 (LLM 활용)
