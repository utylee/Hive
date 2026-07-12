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

---

다음

- [ ] ComfyExecutor 실제 구현

---

그 다음

- [ ] Runtime과 ComfyExecutor 연결
- [ ] 여러 Worker에 segment 분산 실행
- [ ] 결과 segment 병합
