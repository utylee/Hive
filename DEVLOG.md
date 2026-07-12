# Hive Dev Log

## 2026-07

### Runtime

- Worker / Transport 인터페이스 정리.
- upload/download API 통일.

---

### LocalTransport

- workspace 개념 추가.
- upload(), execute(), download() 구현 완료.
- 로컬 ffmpeg split E2E 성공.

---

### SSHTransport

- workspace 지원 추가.
- upload(), execute(), download() 완료.
- rsync를 통한 업로드/다운로드 적용.
- 초기에는 `bash -lc`를 사용했으나 원격 ffmpeg가 `movie.mp4`를 찾지 못하는 문제 발생.
- `bash -lc`를 제거하고 ssh remote command를 직접 실행하도록 변경.
- 원격 ffmpeg split E2E 성공.

---

### Example

- `examples/hd_remaster.py` 작성.
- LocalTransport 실행 성공.
- SSHTransport 실행 성공.
- segment 생성 및 outputs 다운로드 성공.

---

### Test

- LocalTransport 테스트를 현재 upload/download 시그니처에 맞게 수정.
- SSHTransport 테스트에 workspace 인자 반영.
- Comfy submit 테스트의 DummyResponse를 현재 응답 인터페이스에 맞게 수정.
- Comfy wait 테스트에 실제 history의 `prompt`, `create_time` 구조 반영.
- `/queue` 응답에 `queue_running`, `queue_pending` 구조 반영.
- 전체 unit test 31개 통과.

---

### Comfy SDK

- `ComfyClient.submit()` 구현.
- `ComfyClient.wait()` 구현.
- `ComfyClient.history()` 구현.
- 이미지 및 영상 output 다운로드 구현.
- `Prompt.wait()` 구현.
- `Prompt.outputs()` 구현.
- `ImageOutput` 구현.
- `VideoOutput` 구현.
- `Outputs.images`, `Outputs.videos` 구현.

---

### Comfy E2E

- UI workflow JSON이 아니라 API workflow JSON이 필요함을 확인.
- API workflow JSON 제출 성공.
- `prompt_id` 수신 성공.
- VHS meta batch 재큐잉 전체 완료까지 기다리도록 `wait()` 수정.
- 영상 결과가 history의 `gifs` 키로 반환되는 것을 확인.
- `VideoOutput` 추가.
- `/view`를 통해 최종 MP4 다운로드 성공.
- `queue_nonce`를 매 실행 변경해 캐시 실행 방지.
- `queue_nonce` 최대값이 `999999999`임을 확인하고 범위 내 랜덤값 사용.

---

### Single Segment E2E

- 로컬 `segment_0000.mp4`를 SSHTransport로 원격 ComfyUI의 `input/batches/hive_test/`에 업로드.
- API workflow의 `batch_folder`를 `hive_test`로 주입.
- `queue_nonce`를 실행마다 범위 내 랜덤값으로 변경.
- Comfy HTTP API로 workflow 제출.
- VHS meta batch 재큐잉이 모두 끝날 때까지 대기.
- 최종 MP4를 `/view`를 통해 로컬 `outputs/comfy/`로 다운로드.
- 입력 파일명 기반으로 출력 파일명이 자동 결정되는 구조 확인.
- 원격 ComfyUI 브라우저에서는 API 제출 작업의 meta batch 진행 표시가 보이지 않을 수 있음을 확인.
- 향후 Hive 콘솔에서 worker, segment, meta batch 진행률, elapsed time, 완료/실패 상태를 표시할 필요가 있음.

---

### continued Segment E2E

- ComfyClient.wait()에 on_progress 콜백 추가
- VHS BatchManager의 count, frames_per_batch, requeue로 진행률 계산
- 콘솔 한 줄 갱신 방식으로 진행률 표시 성공

---

### continued Segment E2E

- create_manifest()에 optional parameters 추가
- Dispatcher가 parameters를 manifest에 전달
- 관련 테스트 통과

---

- 원본 source를 job_dir 안으로 복사하도록 수정
- 원격 worker에서도 동일 상대경로 사용 가능
- dispatcher/manifest 테스트 통과

---

- Dispatcher가 server 선택 후 comfy_url을 manifest에 주입
- dispatcher/manifest 테스트 통과

---

- VHSBatchPrecleanPro와 VHS_BatchManager 입력 대상 수정
- 잘못된 cleanup_threshold 제거
- workflow patch 단위 테스트 추가 및 통과

---

- servers.yaml에서 comfy_input_batches 로드
- 기본값 /data/temp/ComfyUI/input/batches
- 관련 테스트 통과

- 선택된 서버의 Comfy URL과 input batch 경로를 job manifest에 주입
- dispatcher 테스트 통과
