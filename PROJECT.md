# Hive

분산 GPU/ComfyUI 오케스트레이터.

목표

- 여러 GPU 서버(Local/SSH)를 하나의 Runtime으로 관리
- 영상을 segment 단위로 분산 처리
- ComfyUI Workflow를 HTTP API로 실행
- 결과를 자동 수집 및 병합

---

# Current Status

## Runtime

- [x] Task
- [x] Worker
- [x] WorkerPool
- [x] Executor
- [x] Executor.submit()
- [x] Executor.map()

Runtime은 당분간 변경하지 않는다.

---

## Transport

### LocalTransport

- [x] upload(source, destination)
- [x] execute(command)
- [x] download(source, destination)
- [x] workspace 지원

### SSHTransport

- [x] upload(source, destination)
- [x] execute(command)
- [x] download(source, destination)
- [x] workspace 지원
- [x] rsync 사용
- [x] ssh remote command 실행

### 완료

LocalTransport와 SSHTransport가 동일한 의미론으로 동작한다.

Worker는 Transport 종류를 알 필요가 없다.

---

## Media

### MovieProbe

- [x] ffprobe duration

### MovieSplitter

- [x] duration
- [x] Segment 생성

---

## Workflow

### HDRemasterWorkflow

- [x] workflow.plan()
- [x] Task 생성
- [x] ffmpeg split command 생성

---

## Comfy SDK

### 완료

- [x] submit()
- [x] wait()
- [x] history()
- [x] outputs()
- [x] download()
- [x] API workflow submit
- [x] meta batch 전체 완료 대기
- [x] image outputs
- [x] video outputs (`gifs`)
- [x] video download
- [x] Comfy E2E 성공

### Prompt

- [x] wait()
- [x] outputs()

### ImageOutput

- [x] download()

### VideoOutput

- [x] download()

### Outputs

- [x] images
- [x] videos

---

## Executor

### ComfyExecutor

현재 Stub.

구현 예정.

---

# Example

## hd_remaster.py

완료.

동작 흐름:

```text
movie.mp4
  ↓
Workflow.plan()
  ↓
Task 생성
  ↓
Executor.map()
  ↓
Worker
  ↓
Transport
  ↓
ffmpeg split
  ↓
segment 다운로드
  ↓
outputs/
```

Local, SSH 모두 성공.

## comfy_client.py

완료.

동작 흐름:

```text
API workflow JSON 로드
  ↓
queue_nonce 변경
  ↓
ComfyClient.submit()
  ↓
meta batch 전체 완료까지 wait()
  ↓
Prompt.outputs()
  ↓
VideoOutput.download()
  ↓
outputs/comfy/
```

---

## Repository Structure

```text
hive/
├── comfy/
│   ├── client.py
│   ├── models.py
│   └── outputs.py
├── executors/
│   └── comfy.py
├── runtime/
│   ├── executor.py
│   ├── task.py
│   ├── worker.py
│   └── worker_pool.py
├── transport/
│   ├── local.py
│   └── ssh.py
├── workflows/
│   └── hd_remaster/
└── examples/
    ├── hd_remaster.py
    ├── comfy_client.py
    └── workflows/
```

## Important APIs

```python
LocalTransport(workspace: Path)
SSHTransport(host: str, workspace: Path)

upload(source: Path, destination: str) -> None
execute(command: list[str], *, cwd=None, timeout=None) -> None
download(source: str, destination: Path) -> None
```

```python
ComfyClient.submit(workflow) -> Prompt
Prompt.wait() -> Prompt
Prompt.outputs() -> Outputs
ImageOutput.download() -> bytes
VideoOutput.download() -> bytes
```

---

# Architecture

```text
Dispatcher
├── Runtime
├── SSH
│   ├── upload
│   └── download
└── HTTP
    ├── submit
    ├── wait
    ├── history
    └── outputs
```

SSH는 파일 전송에 사용한다.

HTTP는 Comfy 실행에 사용한다.

둘은 분리한다.

---

# Design Rules

- Runtime은 당분간 수정하지 않는다.
- 작은 커밋으로 진행한다.
- 현재 코드 기준으로만 수정한다.
- 없는 API를 만들지 않는다.
- YAGNI
- 실제 동작 우선
- 테스트 후 커밋
- Runtime보다 Example을 먼저 만든다.

---

# Current Issue

단일 segment 기준으로 다음 흐름은 동작 확인이 끝났다.

- 로컬 segment를 원격 Comfy input batch 폴더로 업로드
- API workflow에 `batch_folder` 주입
- `queue_nonce` 자동 변경
- Comfy submit
- VHS meta batch 전체 완료 대기
- 결과 MP4 다운로드
- Hive 콘솔에서 worker, segment, meta batch 진행률, elapsed time 표시 성공
- comfy_client.py가 실행 위치와 무관하게 workflow 경로를 찾도록 수정
- Dispatcher가 source를 job_dir/input/에 staging
- manifest에는 input/<filename> 상대경로 저장
- build_comfy_workflow()가 batch_folder, queue_nonce, frames_per_batch를 실제 노드에 주입
- 원본 workflow는 deepcopy로 보존
- Server에 comfy_input_batches 추가
- 서버별 Comfy input batch 경로 설정 가능
- manifest parameters에 comfy_url, comfy_input_batches 저장
- Dispatcher가 API workflow JSON을 job_dir/workflow.json으로 staging
- manifest의 workflow 경로를 원격에서도 유효한 상대경로로 저장
- ComfyExecutor 실제 구현 완료
- source staging → workflow patch → submit → wait → video download 지원
- 원격 작업 완료 후 result.json뿐 아니라 output/ 결과물도 로컬 job 디렉터리로 회수
- 실제 Dispatcher → m5 Worker → ComfyUI → 결과 영상 회수 E2E 성공
- 원격 Worker 가상환경에 requests 필요
- 결과는 로컬 work/<job-id>/output/에 저장
- 성공한 입력 파일은 jobs/done/으로 이동
- 완료된 파일은 다음 스캔에서 제외
- 성공 입력은 jobs/done/
- 실패 입력은 jobs/failed/
- 실패 원인은 work/<job-id>/error.txt에 기록
- --retry-failed로 jobs/failed/\*.mp4를 다시 입력 큐로 복구
- 동일 파일명이 이미 있으면 덮어쓰지 않고 오류 처리
- 실패 파일 옆에 \*.retry.json 저장
- 재시도 후 다시 실패하면 retry_count 증가
- 재시도 성공 시 retry 메타데이터 삭제
- MAX_RETRIES = 3
- 재시도 한도에 도달한 실패 작업은 failed/에 유지
- --retry-failed 실행 시 건너뛴 이유와 횟수 출력
- retry_count >= 3 작업은 jobs/quarantine/으로 이동
- MP4와 \*.retry.json을 함께 격리
- --restore-quarantine으로 격리 작업을 입력 큐로 복구
- 복구 시 기존 retry 메타데이터 삭제 및 횟수 초기화
- retry 메타데이터에 failed_servers 기록
- 재시도 시 이전에 실패한 서버를 우선 제외
- 모든 서버가 제외된 경우 다시 첫 enabled 서버부터 선택
- Dispatcher가 서버 인덱스를 기억하고 작업마다 라운드로빈 분배
- 재시도 작업은 failed_servers를 우선 제외
- 모든 서버가 제외되면 현재 라운드로빈 위치부터 다시 선택
- ThreadPoolExecutor 기반 병렬 원격 dispatch
- 기본 동시 작업 수는 enabled 서버 수
- 작업 할당은 라운드로빈 유지
- 서버별 Lock으로 동일 서버 동시 실행 방지
- 서로 다른 서버는 병렬 실행 유지
- 서버별 comfy_output_dir 설정 지원
- VHSBatchPrecleanPro.output_folder를 제출 직전에 서버 경로로 패치
- 동일 API workflow를 m5, ccy2 등 서로 다른 경로 구조에서 공용 사용
- m5와 ccy2 실제 병렬 E2E 성공
- 서버별 comfy_input_batches, comfy_output_dir 사용
- 동일 API workflow를 서버별 경로에 맞게 런타임 패치
- 두 결과 MP4 모두 로컬로 정상 회수
- 정적 라운드로빈 사전 할당 제거
- 서버별 worker가 공용 Queue에서 작업을 가져가도록 변경
- 빠른 서버가 작업 완료 즉시 다음 작업 처리
- manifest에 server_name, started_at, finished_at,
  elapsed_seconds, status 기록
- pytest 및 pyright 통과
- manifest에 server_name 기록
- started_at / finished_at 기록
- elapsed_seconds 기록
- running / failed / completed 상태 기록
- 성공과 실패 경로 분리 저장
- Shared dynamic job queue
- One worker thread per enabled server
- Fast servers automatically consume more jobs
- Manifest execution metadata:
  - server_name
  - started_at
  - finished_at
  - elapsed_seconds
  - status
- 10-job / 5-server real E2E test completed successfully
- Server-specific Hive roots
- Automatic Hive package sync before remote dispatch
- Retry transient SSH/rsync failures
- Server preflight command for SSH, Python, Hive, and ComfyUI
- Automatic retry on another server within the same dispatcher run
- Failed server exclusion per job
- Real E2E verified: m5 failure → ccy2 completion
- Retry transient Comfy preflight failures
- Real E2E verified: HTTP 502 → retry → HTTP 200
- In-memory server failure tracking
- Automatic server cooldown after repeated failures
- Server recovery after a successful job
- Thread-safe server event logging to `server_events.jsonl`
- Server status summary via `--server-status`
- Active cooldown and remaining time display
- Recent event inspection via `--server-events N`
- 성공 및 실패 경로별 manifest 상태 저장
- 공용 동적 작업 큐
- 활성화된 서버마다 하나의 워커 스레드 실행
- 빠른 서버가 더 많은 작업을 자동으로 가져가는 구조
- Manifest 실행 메타데이터 기록
  server_name
  started_at
  finished_at
  elapsed_seconds
  status
- 10개 작업과 5개 서버를 이용한 실제 E2E 테스트 성공
- 서버별 Hive 루트 경로 지원
- 원격 작업 실행 전 Hive 패키지 자동 동기화
- 일시적인 SSH/rsync 오류 자동 재시도
- SSH, Python, Hive, ComfyUI 상태를 확인하는 서버 preflight 명령
- 같은 dispatcher 실행 안에서 실패한 작업을 다른 서버로 자동 재시도
- 작업별 실패 서버 재배정 제외
- 실제 E2E 검증 완료: m5 실패 → ccy2 완료
- 일시적인 Comfy preflight 오류 자동 재시도
- 실제 E2E 검증 완료: HTTP 502 → 재시도 → HTTP 200
- 메모리 기반 서버 실패 횟수 추적
- 반복 실패 서버 자동 cooldown 처리
- 작업 성공 시 서버 실패 상태 초기화 및 복구
- server_events.jsonl에 스레드 안전 방식으로 서버 이벤트 기록
- --server-status를 통한 서버 상태 요약
- 현재 cooldown 활성 여부와 남은 시간 표시
- --server-events N을 통한 최근 서버 이벤트 조회

- 서버별 연속 실패 횟수와 cooldown 상태 영속화
- 서버 상태 파일의 원자적·스레드 안전 저장
- dispatcher 재시작 후 서버 상태 자동 복원
- cooldown 종료 후 서버 자동 재참여
- `--server-status`에서 저장된 현재 상태 표시
- `--reset-server-state`를 통한 서버 상태 수동 초기화

아직 남은 문제:

- ComfyExecutor는 아직 Stub
- 여러 segment를 여러 Worker에 분산 실행하지 않음
- manifest가 parameters를 전달할 수 있음
- 선택된 server의 comfy_url을 manifest parameters에 저장

---

# Next Goal

그 후 ComfyExecutor를 실제 구현한다.
