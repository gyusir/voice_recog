# CLAUDE.md

## 프로젝트 개요

- **레포지토리**: `gyusir/voice_recog`
- **목적**: [Microsoft VibeVoice](https://github.com/microsoft/VibeVoice) 관련 실험 및 연구
- VibeVoice 기반 음성 인식 실험, 성능 테스트, 커스터마이징 등을 진행

## 브랜치 전략

- **`main`**: 배포용 브랜치. 직접 커밋 금지. `dev`에서 검증 완료된 코드만 머지.
- **`dev`**: 작업용 브랜치. 모든 개발은 이 브랜치에서 진행.
- **별도 브랜치 생성 금지**: `main`, `dev` 외 추가 브랜치를 만들지 않는다.

## 개발 규칙

- 모든 작업은 `dev` 브랜치에서 수행
- `main`에는 PR 또는 머지를 통해서만 반영
- 커밋 메시지는 한국어 또는 영어로 명확하게 작성
