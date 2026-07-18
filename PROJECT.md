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

아직 남은 문제:

- ComfyExecutor는 아직 Stub
- 여러 segment를 여러 Worker에 분산 실행하지 않음
- manifest가 parameters를 전달할 수 있음
- 선택된 server의 comfy_url을 manifest parameters에 저장

---

# Next Goal

그 후 ComfyExecutor를 실제 구현한다.
