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

Prompt

- [x] wait()
- [x] outputs()

ImageOutput

- [x] download()

Outputs

- [x] images

---

## Executor

### ComfyExecutor

현재 Stub.

구현 예정.

---

# Example

## hd_remaster.py

완료.

동작

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

동작 확인 완료.

Local

SSH

모두 성공.

---

## Repository Structure

hive/
├── comfy/
│ ├── client.py
│ ├── models.py
│ └── outputs.py
├── executors/
│ └── comfy.py
├── runtime/
│ ├── executor.py
│ ├── task.py
│ ├── worker.py
│ └── worker_pool.py
├── transport/
│ ├── local.py
│ └── ssh.py
├── workflows/
│ └── hd_remaster/
└── examples/
├── hd_remaster.py
├── comfy_client.py
└── workflows/

LocalTransport(workspace: Path)
SSHTransport(host: str, workspace: Path)

upload(source: Path, destination: str) -> None
execute(command: list[str], \*, cwd=None, timeout=None) -> None
download(source: str, destination: Path) -> None

---

# Architecture

Dispatcher

├── Runtime
│
├── SSH
│ ├── upload
│ └── download
│
└── HTTP
├── submit
├── wait
├── history
└── outputs

SSH는

파일 전송

HTTP는

Comfy 실행

둘은 분리한다.

---

# Design Rules

반드시 지킨다.

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

Comfy API Workflow 제출 진행 중.

현재 UI Workflow JSON은 확인.

API Workflow JSON으로 전환 필요.

---

# Next Goal

Comfy API Workflow submit 성공.

prompt_id 수신.

wait()

outputs()

다운로드.

E2E 성공.

그 후

ComfyExecutor 구현.
