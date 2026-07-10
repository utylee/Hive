# Hive Dev Log

## 2026-07

### Runtime

- Worker / Transport 인터페이스 정리.
- upload/download API 통일.

---

### LocalTransport

workspace 개념 추가.

upload()

execute()

download()

완료.

---

### SSHTransport

workspace 지원.

upload()

execute()

download()

완료.

초기에는

bash -lc

사용.

원격 ffmpeg가 movie.mp4를 찾지 못하는 문제 발생.

조사 결과

bash -lc 제거.

ssh remote command 직접 실행으로 변경.

E2E 성공.

---

### Example

examples/hd_remaster.py 작성.

Local 성공.

SSH 성공.

segment 생성.

outputs 다운로드 성공.

---

### Test

pytest 수정.

LocalTransport 테스트 업데이트.

SSHTransport 테스트 업데이트.

모든 테스트 통과.

---

### Comfy

ComfyClient 구현.

submit()

wait()

history()

outputs()

download()

완료.

Prompt 객체 구현.

Outputs 구현.

ImageOutput 구현.

---

### 현재 진행

examples/comfy_client.py 작성 중.

현재 UI Workflow JSON을 제출하여

500 Internal Server Error 확인.

원인 확인.

UI Workflow JSON.

↓

API Workflow JSON 필요.

다음 커밋에서 API Workflow 제출 예정.
