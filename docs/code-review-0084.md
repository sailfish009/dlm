# DLM v0.0084 코드 리뷰·평가

검토 대상: `/research/dlm_v0.0084` 현재 작업 트리.
운영 소스·기존 테스트·런타임은 수정하지 않았다. 이 리뷰와 별도 재현 증거만 추가했다.
이전 구현 작업이 최종 릴리스 절차 전 중단된 상태도 함께 평가했다.

## 발견 사항 — 우선순위 순

### 1. [P2] 정의 한도 도달 상태는 재시작 후 동일하게 복원되지 않음

위치: `src/dlm/search-session.l:33-44`, `:56-71`,
`src/dlm/search-control.l:69-76`, `src/dlm/repl.l:57-61`.

`s84-step`은 `saturated`와 `capacity` 모두 `*dlm-saturated*=true`로 처리한다.
하지만 `s84-sync`은 현재 모델과 키가 같고 pool이 비어 있는 경우에만 이 플래그를
복원한다. 정의 수12에 따른 capacity는 pool에 후보가 남아 있어도 발생할 수 있다.
따라서 저장된 controller/model이 동일해도 재시작 후 다음 전이가 달라진다.

재현: r/s 두 관계, a/b/c 세 개체의 모든 쌍18개를 관측하고 cache 모드로13회 step.

```
(before (capacity pair-checks 0) saturated true definitions 12 pool 10)
(uninterrupted-next (round 14 (waiting pair-checks 0)))
(restored-saturated () next (round 14 (capacity pair-checks 0)))
```

별도 새 프로세스에서 `dlm open`으로 검증·복원한 결과다. 증명 진위가 바뀌지는 않지만,
이미 자원 한도에 도달한 세션이 재시작마다 불필요한 search84-run 이벤트와 checkpoint를
추가할 수 있다. 기존 saturated-wait 복원 테스트는 빈 pool만 검사하여 이 경우를 놓친다.

권고: 마지막 검색 상태/중단 원인을 replay 결과에 명시하거나, 정의 한도와 pool 생성
한도를 포함해 정지 상태를 정확히 유도할 것. capacity는 논리적 포화와 구별해야 한다.
12개 정의 + nonempty pool의 실제 새 프로세스 복원 회귀 테스트가 필요하다.

### 2. [P2] 로그/누적 요청 한도 거부가 idle 학습을 멈추지 않음

위치: `src/dlm/repl.l:62-73`, `:104-120`,
`src/dlm/search-session.l:56-78`.

이벤트 한도와 누적 예산 한도는 commit 시점에 검사한다. 그러나 `s84-step`은 그 전에
`a84-run`을 실행한다. 한도 거부 후에는 모델/controller를 publish하지 않는 점은
올바르지만, checkpoint 실패와 달리 `d77-pause`하지 않으며 다음 tick에서도 같은
controller에서 같은 작업을 반복한다. 거부된 탐색에 대한 진행 상태는 저장되지 않는다.

실제 API만 사용한 간단한 재현:

```
(times-do 256 (dlm 'search 'cache))
(dlm 'start 20)
(dlm 'step)
(dlm 'step)
```

결과:

```
first  = (round 1 (rejected invalid-transition-or-event-limit))
second = (round 2 (rejected invalid-transition-or-event-limit))
running true, saturated (), events 256
```

이 재현은 수동 step으로 반복 가능한 상태를 보여준다. idle callback도 같은 step을
호출하므로 이후에도 동일한 거부를 반복한다. 데이터 손상은 아니지만, 한도 도달 시
자동 학습이 생산적 진행 없이 CPU·출력을 계속 사용할 수 있다.

권고: 탐색 전에 로그/누적 요청 용량을 preflight하고, 회복 불가능한 세션 자원 거부는
명시적 `paused/resource-limit`로 바꿀 것. 원인별 거부와 source/reset/reopen 복구 정책을
정하고 idle 동작을 검사할 것. 실패를 논리적 반증으로 바꾸어서는 안 된다.

### 3. [P2 / 릴리스 차단] 현재 소스와 릴리스 검증 자료가 일치하지 않음

위치: `README.md:97-104`, `docs/release.txt`,
`docs/release.tests.sha256`, `maru-compiler` symlink.

README가 가리키는 `docs/release-0084.md`가 없고, active runtime/release 기록은
v0.0083의 `20261022T050940Z-18663`이다. 기존 test manifest 검사에서 다음이 실패한다.

```
scripts/run.sh: FAILED
src/dlm/axiom-space.l: FAILED
src/dlm/repl.l: FAILED
src/dlm/session-store.l: FAILED
VERSION: FAILED
```

이는 새 소스를 이전 버전의 완료된 검증 자료와 구별해야 한다는 뜻이지, 기존 Maru
실행 파일이 잘못됐다는 뜻은 아니다. DLM 모듈은 외부 로드되며 compiler/platform은
변경되지 않았다. 다만 현재 v0.0084 소스 전체에 대해 최종 reproduce/verify/promote와
manifest 갱신이 완료됐다고 볼 수 없다. 이번 리뷰에서는 릴리스 절차를 실행하지 않았다.

권고: 경계 수정 후 최종 소스로 3세대 LLVM/stripped 비교 및 전체 검증을 실행하고,
matching manifests·릴리스 노트·로그를 갱신할 것. 현재 76개 테스트 통과와 이전 릴리스의
self-host 검증을 혼동하지 말 것.

## 테스트 재실행

- Python: **76개 통과**, 94.968초.
- Native `./scripts/run.sh test`: 통과.
- 독립 오라클 출력 유지: 3392 sequents, SPACE79 417 sequents,
  interpolation100 pairs/Beth6 theories 등 기존 비교 통과.
- 신규 별도 probe에서 위 두 상태/자원 경계 문제를 재현.

증거: `docs/review84-evidence/python-tests.log`, `native-tests.log`,
`results.json`, `log-limit.l`, `capacity-save.l`, `capacity-restore.l`.
capacity probe는 `/tmp/review84-capacity.sexp`를 사용한다. 재실행 시 전용 임시 경로로
바꾸고 save/restore를 서로 다른 프로세스에서 실행할 것.

## 설계상 긍정적인 점

1. **선택과 증명 승인을 분리했다.** UCB 점수가 높아도 `a77-certify`를 거쳐야 하며,
   성공 결과는 cache로 승인하지 않는다.
2. **부정 cache 의미가 제한적이다.** complete insufficient-reuse만 저장하며,
   검증 실패/미완료는 retry 후보로 남긴다. 이를 논리적 불가능으로 오인하지 않는다.
3. **캐시 키가 보수적이다.** 전체 모델 변경 시 frontier/부정 cache를 무효화한다.
   미세 의존성 무효화보다 비싸지만 stale rejection 위험을 줄인다.
4. **실제 루프에 연결돼 있다.** 기존 step/start, 새 프로세스 controller 복원,
   checkpoint 실패 rollback이 테스트된다. 독립 데모만 만든 것은 아니다.
5. **통계는 기호적이며 재현 가능하다.** 정수 log/sqrt 기반 family UCB이고 LLM/신경망이
   없다. 일반 UCB1의 이론적 보장을 주장하지 않는 점도 적절하다.

현재 검토/검사에서는 새로운 커널 승인 우회나 허위 증명 수용을 확인하지 못했다.
이것은 전체 soundness의 형식적 증명을 뜻하지 않는다.

## 실험 평가 — 얻은 증거와 아직 부족한 증거

### 확인된 범위

- rare-path에서 동일한 정의2개를 얻으면서 certification 호출을 `4/3/5 → 3/3/4`로
  줄였다. cache mode의 split 간 부정 재사용도 실제로 발생한다.
- distractors에서6라운드 후 legacy는 정의1개, indexed 모드들은3개를 발견했다.
- 같은 목표(정의2개)에 도달하는 시간은 cache mode가 약 `0.3863 → 0.3431초`였다.
  단,6라운드 전체 실행은 `0.3519 → 0.4720초`로 더 오래 걸렸다.
- 문서는 이런 부정 결과·예산 단위 차이·추가 저장 비용을 공개하고 있어 정직하다.

### 추가 평가가 필요한 부분

**A. UCB의 독립 기여를 입증하지 못함.**
`cache` arm에도 endpoint index, 후보 중복 제거, persistent frontier가 함께 들어간다.
따라서 legacy 대비 개선을 transposition이나 UCB 하나의 효과로 분해할 수 없다.
현재 workload는 유효 primitive 관계가 사실상 edge 하나라 선택 다양성이 작다.
indexed-only/no-negative-cache arm과 여러 성과·비용 family가 경쟁하는 입력이 필요하다.

**B. persistent REPL의 실제 비용이 benchmark에서 빠져 있음.**
`adapters/search_experiment.py:35-70`은 store를 열지 않는 in-memory 실행이다.
반면 attached REPL은 `d77-checkpoint`에서 새 snapshot, 기존 파일, 다시 읽은 임시 파일을
각각 검증하여 history replay를 반복한다(`session-store.l:55-67`).
새 모드는 unsuccessful/partial step도 기록하므로 이 비용이 사용자 환경에서 중요하다.
현재 toy in-memory 결과를 저장 중인 REPL의 속도 개선으로 확대 해석해서는 안 된다.

**C. distractor seed는 구조적으로 다른 문제를 만들지 않음.**
`search_experiment.py:21-24`는 서로 연결되지 않는 noise의 순서만 바꾸고,
유효 edge chain과 noise-first 배치를 고정한다. 세 seed는 새로운 reasoning structure
세 개라기보다 동일 구조의 nuisance-order 변형이다. 고정 순서의 arm 실행과
startup/진단 출력 포함 측정도 작은 시간 차이의 해석에 제약을 준다.
다양한 그래프·관계·증거 밀도, 무작위 arm 순서, 더 긴 workload를 추가할 것.

**D. 목적함수는 아직 '후속 유용성'이 아님.**
reward는 source-instance coverage, cost는 일부 closure-proof entry 계수다.
이후 목표에서 실제로 절감한 작업이나 wall time, 후보 생성·checkpoint 비용은
policy score에 직접 들어가지 않는다. 이는 문서화된 근사지만, 학습된 탐색 가치나
범용 탐색 가속이 검증됐다고 부를 수는 없다.

## 종합 판정

**연구용 탐색 제어 프로토타입으로는 적절하고, indexed frontier/cache는 계속 발전시킬
가치가 있다. 그러나 현 상태를 최종 검증된 릴리스나 UCB의 효율 우위가 입증된 모델로
평가하기는 이르다.**

우선순위:

1. capacity 재시작 동등성과 resource-limit idle 동작 수정.
2. v0.0084 최종 릴리스 검증 자료 정합성 확보.
3. persistent-store time-to-target와 indexed-only ablation 추가.
4. 그 결과를 본 뒤 cost model/UCB를 개선. 지금 MCTS 전체를 추가하는 것은 우선순위가 낮다.
