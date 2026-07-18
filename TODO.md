# Next Commit

## 목표

Comfy 작업 진행률을 Hive 콘솔에서 확인할 수 있게 한다.

---

순서

- [x] 현재 실행 중인 worker 표시
- [x] 현재 처리 중인 segment 표시
- [x] VHS meta batch 진행률 표시
- [x] elapsed time 표시
- [x] 완료/실패 상태 표시
- [x] 테스트
- [x] 커밋

---

다음 목표: ComfyExecutor가 manifest의 comfy_url, source, workflow 설정을 읽어 실제 실행
다음 목표: ComfyExecutor에서 workflow JSON 로드 → patch → submit → wait → video download 연결
다음 목표: Dispatcher가 선택된 server의 comfy_input_batches를 manifest parameters에 넣기
다음 목표: 실제 Dispatcher → remote worker → ComfyExecutor E2E 실행
다음 목표: 실제 Dispatcher → 원격 Worker → ComfyUI → 결과 영상 회수 E2E 실행

완료된 입력 파일 재처리 방지
실패 작업 상태와 재시도
다중 서버 병렬 분배
원격 코드 배포 방식 자동화

실패한 입력을 failed/로 이동
실패 사유 기록 및 재시도 정책 추가

실패 작업 재시도 명령
최대 재시도 횟수와 서버 변경 정책
여러 작업 병렬 분배

재시도 횟수 기록
최대 재시도 초과 시 격리
실패 시 다른 서버로 재배정

최대 재시도 횟수 제한
한도 초과 작업 격리
재시도 시 다른 서버 선택 정책

한도 초과 작업을 quarantine/으로 이동
서버별 실패 이력 기록
재시도 시 다른 서버 우선 선택

quarantine 작업 수동 복구 명령
서버별 실패 이력 기록
재시도 시 다른 서버 우선 선택

서버별 실패 이력 기록
재시도 시 이전에 실패한 서버 제외
여러 작업 병렬 분배

서버별 실패 횟수 기록
동일 서버 연속 실패 제한
다중 작업 병렬 분배

실제 여러 입력을 여러 서버에 병렬 실행
서버별 동시 작업 수 제한
서버 상태/Comfy queue 기반 선택

동일 서버에 동시에 여러 작업이 배정되지 않도록 슬롯 관리
실제 다중 서버 E2E
서버 queue 상태 기반 동시성 조절

---

다음

- [ ] ComfyExecutor 실제 구현

---

그 다음

- [ ] Runtime과 ComfyExecutor 연결
- [ ] 여러 Worker에 segment 분산 실행
- [ ] 결과 segment 병합
