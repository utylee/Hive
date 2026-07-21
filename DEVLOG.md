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

- source와 workflow를 job_dir 내부에 함께 복사
- 원격 worker에서 job_dir/input/..., job_dir/workflow.json 사용 가능
- dispatcher 테스트 통과

- ComfyExecutor가 manifest의 source, workflow, comfy_url, comfy_input_batches 사용
- 단위 테스트에서 DummyClient로 실행 흐름 검증
- WorkerRunner 테스트는 DummyComfyExecutor로 executor 선택만 검증
- 전체 테스트 33개 통과

- result["outputs"]가 있을 때만 원격 output/ 디렉터리 rsync
- 출력 없는 작업은 기존처럼 정상 종료
- 전체 테스트 통과

- 초기 실행은 원격 Stub 코드로 즉시 종료
- 원격 소스 동기화 후 requests 누락 오류 확인
- 의존성 설치 후 실제 GPU 처리 및 결과 MP4 회수 성공

- Dispatcher 성공 후 원본 이동 추가
- 단위 테스트에서 001.mp4, 002.mp4의 done/ 이동 검증
- 전체 테스트 통과

- 원격 실행 예외와 ok: false 결과 처리 추가
- 실패한 입력을 재스캔하지 않도록 분리
- 성공/실패 Dispatcher 테스트 통과

- 실패 작업 수동 재시도 명령 추가
- broken.mp4가 failed/에서 jobs/로 정상 복구됨

- 실패 메타데이터에 retry_count, last_job_id, last_error 기록
- --retry-failed가 MP4와 retry JSON을 함께 복구
- 두 번째 실패 시 retry_count: 2 단위 테스트 통과

- retry_count >= 3 작업 복구 차단
- broken.mp4가 failed/에 유지되는 수동 검증 성공

- 한도 초과 작업 격리 로직 추가
- broken.mp4와 retry 메타데이터가 quarantine으로 이동하는 수동 검증 성공

- quarantine 수동 복구 옵션 추가
- MP4는 jobs/로 복귀하고 \*.retry.json은 삭제되는 흐름 검증

- pick_server(..., excluded=...) 지원
- 실패 시 현재 서버 이름을 failed_servers에 누적
- 테스트 더미 서버에 name 필드 추가
- 전체 테스트 통과

- pick_server()가 (server, index) 반환
- start_index, excluded 지원
- 다중 서버 순환 및 제외 서버 테스트 추가

- 작업 하나 처리 흐름을 \_process_source()로 분리
- 두 작업이 서로 다른 서버에서 동시에 실행되는 테스트 추가

- 서버 하나에 작업 두 개를 배정해도 max_active == 1 확인
- 서버당 동시 작업 수 1개 보장

- API workflow에 남아 있던 m5 전용 /data/... 출력 경로 문제 수정
- 입력 경로뿐 아니라 전처리 출력 경로도 서버별 설정으로 관리
- 관련 단위 테스트 전체 통과

- m5: 001_00005-audio.mp4
- ccy2: 002_00001-audio.mp4
- 두 작업이 서로 다른 서버에서 실제 동시 처리됨
- 서버별 절대경로 차이 문제 해결 완료

## 2026-07-20 Dynamic Queue E2E

- 공용 작업 큐 기반 동적 서버 분배 검증
- 5개 서버에서 10개 세그먼트 처리
- 전체 10개 성공, 실패 0개
- 빠른 서버가 완료 즉시 다음 작업을 가져가는 동작 확인

결과:

- wsl12: 5 jobs, avg 420.29s
- m5: 2 jobs, avg 1553.13s
- mac: 1 job, avg 2143.78s
- ccy2: 1 job, avg 2981.11s
- legion: 1 job, avg 3286.79s

정적 균등 배분이 아니라 서버 처리 속도에 따라 작업 수가 자연스럽게 배분됨.

## 2026-07-20 Remote Reliability Improvements

- 서버별 `hive_root` 설정 추가
- 서버별 Hive 소스 자동 동기화
- 원격 명령의 일시적 `returncode=255` 오류 재시도
- 서버 preflight 검사 추가
  - SSH 접속
  - 원격 Python 실행
  - `import hive`
  - ComfyUI 응답
- 5개 서버 모두 preflight 통과

## 2026-07-21 Automatic Cross-Server Retry E2E

- 실패 작업을 같은 실행 안에서 다른 서버로 자동 재투입
- m5의 Python 경로를 의도적으로 잘못 설정해 실패 유도
- m5 실패 후 ccy2가 자동으로 작업을 이어받아 완료
- 수동 `--retry-failed` 실행 없이 복구되는 흐름 검증

결과:

- m5: failed, 1.385s
- ccy2: completed, 2886.519s
