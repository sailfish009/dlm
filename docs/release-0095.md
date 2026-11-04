# DLM 0.0095 — 구현 및 CPU 실험 보고

## 요약

`/research/design_20261104.md`의 첫 작은 교차 구성 실험을 구현했다. 기존 Basis91 모델 안에서 **관계가 수치 관찰의 짝과 역할을 정하고, 그 자료에서 수치 기저와 복합 기저를 함께 형성하며, 복합 출력이 다음 형성의 입력이 되는 경로**다.

새 독립 95 모델, 별도의 EML93 학습 state, 공통 launcher 아래의 두 학습기 dispatcher는 만들지 않았다. 기존 라이브러리·전역 prefix ID·모델 projection·채택·audit·replay·checkpoint·native lock을 확장했다.

**새 테스트 26개 및 전체 오프라인 264개가 통과했다.** 순차 40-process 대조 실험에서는 complete query 288개에 포함된 **2,592개 전체 binding/숫자/원본 witness 행**에서 불일치가 없었다. 의도적으로 필요한 기저를 제거한 192개 unknown query는 정답으로 세지 않았다.

이것은 구조화된 작은 자료에서의 누적 교차 형성 결과이지, 일반적인 의미 학습·기저 공리 이론·보편적 EML 우위를 입증한 결과가 아니다.

## 1. 버전 경계와 보존

- 0093 실제 532 files, 0094 실제 562 files 및 Git status/compiler를 기록했다.
- 0094의 실제 작업 트리를 `cp -a --reflink=auto`로 0095에 복사하고 562 file hash가 일치함을 **구현 전** 확인했다.
- 루트 README는 `README-0094.md`로 보관하고 `VERSION=0.0095`로 올렸다.
- 원본의 dirty/untracked 상태를 포함해 보존했다. reset/commit은 하지 않았다.
- compiler/runtime는 변경하지 않았다. Compiler SHA256:
  `2cbe804829509f5386933d832cbba2fef1bad367b7510a543b5d3f5818136fc9`.

0094 복사본 대비 수정한 상속 파일은 정확히 다음 10개다. Git 기준 diff에는 0094에서 상속한 과거 변경도 표시되므로, 이번 경계 비교는 actual copy-time hash를 사용한다.

```text
README.md
VERSION
scripts/run.sh
src/dlm/attention92-control.l
src/dlm/attention92-ir.l
src/dlm/basis91-check.l
src/dlm/basis91-formation.l
src/dlm/basis91-ir.l
src/dlm/basis91-plan.l
src/dlm/basis91-session.l
```

[초기 inventory](composition95-evidence/predecessors.json), [복사 경계](composition95-evidence/version-boundary.json), [최종 보존 검사](composition95-evidence/preservation.json)를 함께 남겼다.

## 2. 실제 형성 경로

관계 학습은 기존 Basis91/Attention92 경로를 그대로 사용한다. 숫자 기본 구성자 두 개도 원하는 본문 없이 native EML 문법 탐색으로 관찰에서 형성한다. source 이름 `nalpha`, `nbeta`는 함수 이름이 아니다.

주 arm의 전역 라이브러리는 다음 6개 정의다.

| ID | 종류 | 실제 역할 |
|---:|---|---|
| 1 | `basis91` | `r(a,b) ∧ s(b,c)`, 기존 EML94 본문으로 실제 관계 후보 검사 |
| 2 | `numeric95` | EML 식, 시험 범위에서 exp처럼 동작 |
| 3 | `numeric95` | 2를 prefix로 쓰는 EML 식, 시험 범위에서 log처럼 동작 |
| 4 | `numeric95` | 관계가 묶은 관찰에서 형성한 EML 식, 시험 범위에서 차이 계산 |
| 5 | `composite95` | R1의 역할 0/2 관측값을 N4 입력에 결합 |
| 6 | `composite95` | 새 문맥에 C5를 적용한 출력을 N2에 전달 |

새 숫자 본문과 복합 배선의 예는 실제 출력 그대로 다음과 같다.

```lisp
(numeric95 4 2
  (eml93 (call93 3 ((x93 0))) (call93 2 ((x93 1))))
  (eml93
    (eml93 one93 (eml93 (eml93 one93 (x93 0)) one93))
    (eml93 (x93 1) one93))
  principal93
  (paired95 "channel-c-0" 1 ((measure95 0) (measure95 2))))

(composite95 5 1 4 ((measure95 0) (measure95 2)) "channel-c-0")
(composite95 6 1 2 ((output95 5)) "channel-d-0")
```

`(0,2)` 배선이나 이 본문을 학습 입력으로 주지 않았다. 원본 target tuple의 역할 순서와 객체당 scalar 측정이라는 관찰 schema는 주어진다. 자동 자연어 해석 실험은 아니다.

C5 형성에는 **새 N4와 C5가 원자적으로 함께** 채택된다. D6 형성은 새 숫자 프로그램 탐색 없이 실제 C5 출력을 입력으로 재사용한다. 주 fixture에서 C proposal은 11개 pair 후보/1회 숫자 search를 거치고, D proposal은 첫 후보/숫자 search 0회로 기존 output port를 택했다. 이는 고정된 reuse-first 후보 순서의 결과이지 학습된 선택 정책이 아니다.

관계·숫자·복합 정의가 한 라이브러리에 있다는 사실만이 아니라, 이전 관계와 numeric prefix가 **새 숫자 형성에**, C의 실제 계산값이 **다음 복합 형성에** 참여한다. typed 학습 후에도 기존 관계 해석과 새 계층 관계 형성이 같은 라이브러리에 계속 추가되는 테스트를 통과했다.

## 3. 데이터와 실험 조건

- 관계 초기 관찰: 독립된 두 r–s 연결, 4 facts.
- 직접 scalar 관찰: opaque source 두 개, 각각 서로 다른 입력 4개.
- C와 D: 각 6개 외부 합성 target record, 6 facts/7 objects의 관계 문맥과 객체 측정.
- 각 관계 문맥은 9개의 전체 역할 결합을 가진다. target은 그중 6개에 주어지며 다른 조합/새 문맥으로 적용한다.
- D는 C와 다른 객체 및 다른 측정값을 쓴다. D의 정답은 외부 합성 생성기가 만들며 모델의 C 예측을 정답으로 다시 저장하지 않는다.
- 서로 다른 raw record라는 의미이지 통계적으로 독립인 표본이라고 주장하지 않는다. 같은 객체/관계가 여러 record에서 공유된다.
- 2개 fact-order/entity-renaming/query seed × 2개 branch context × 5 arms × 2 repeats = **40개 순차 fresh process**.
- process마다 새 관계·객체·측정 문맥 6개 × C/D channel 2개 = 12 queries.
- seed는 같은 함수 가족의 순서·이름·질의 변형이며 독립적인 새 함수/세계 가족이 아니다.
- 두 branch에서 실제 시험 입력은 positive-real scope다. 복소 전역 동일성이나 음의 축 안전성을 검증한 실험이 아니다.
- GPU, 외부 LLM/API, gradient 학습, network 실행 없이 native Maru와 Python 표준 라이브러리 생성기/oracle만 사용했다.

학습 시 원본 target과 모델 파생 입력의 근거를 분리한다. scope는 source/version/sign cell에 연결된다. primitive expansion 동일성과 외부 관찰에 대한 empirical applicability를 혼동하지 않는다. 제품이 원본 자료 자체의 진위를 인증한다는 뜻도 아니다.

## 4. 대조 실험 결과

| Arm | Runs | 최종 정의 수 | Complete queries | Unknown | 검사한 complete 행 | 불일치 |
|---|---:|---:|---:|---:|---:|---:|
| `shared95` | 8 | 6 | 96 | 0 | 864 | 0 |
| `logical95` | 8 | 6 | 96 | 0 | 864 | 0 |
| `no-relational95` | 8 | 2 | 0 | 96 | 0 | — |
| `no-numeric95` | 8 | 1 | 0 | 96 | 0 | — |
| `no-output95` | 8 | 7 | 96 | 0 | 864 | 0 |
| **합계** | **40** | — | **288** | **192** | **2,592** | **0** |

480 attempted queries에서 complete+unknown이 모두 설명되며 pending은 없다. 192 unknown은 필요한 구성자를 없앤 대조군 결과로서, 정답이나 complete empty answer로 바꾸지 않았다. Complete query의 모든 행을 독립적인 Python 관계 조합/`math` oracle와 비교했다. 최대 complex absolute error는 **0.00010814496703215326**, 검사 허용치는 0.002였다. native fit 허용치는 component별 0.001이다. 전역 수치 오차 정리는 아니다.

동일 seed의 모든 arm/branch/repeat에서 data SHA256이 같았다. `shared95`와 `logical95`의 numeric/composite 정의는 같고 R1의 실행 표현만 다르다.

### 대조군에서 알 수 있는 것

1. **관계 기저 제거:** C/D 후보를 만들 관계 결합 인터페이스가 없어 N4/C/D가 생기지 않았다. 이 형성기는 현재 학습된 관계 기저에서 출발한다는 한정된 메커니즘의 인과 확인이다.
2. **숫자 prefix 제거:** 같은 constructor cost≤3에서 primitive-only 탐색은 C/D 대응을 찾지 못했다. 더 큰 식/다른 탐색에서도 불가능하다는 뜻이 아니다. Prefix를 한 constructor로 세므로 두 arm의 전체 primitive 계산 비용이 같다는 주장도 하지 않는다.
3. **복합 출력 재사용 제거:** D는 여전히 형성된다. 다만 `output95 5` 대신 `N6(u,v)=N2(N4(u,v))`라는 새 숫자 정의와 이를 사용하는 새 복합 정의를 만든다. 최종 정의가 6→7개로 달라졌다. **출력 재사용 없이는 학습 자체가 불가능하다고 주장하지 않는다.**
4. **논리 R1 표현:** 같은 numeric/composite 그래프와 답을 얻었다. 교차 형성에는 typed 연결과 실제 재사용이 중요하며, 모든 관계를 EML로 바꿀 필요는 없다.

## 5. 비용

전체 fresh process 중앙값에는 boot, 관계/숫자/복합 형성, admission, scope rebuild, snapshot replay 검사, 12 queries 및 출력이 들어간다. Python oracle와 뒤의 JSON artifact write 및 attached checkpoint I/O는 포함하지 않는다. 단일 query kernel만의 시간 비교가 아니다.

| Arm | process 중앙값(s) | standalone core JSON bytes |
|---|---:|---:|
| `shared95` | 7.1076 | 1,811–1,831 |
| `logical95` | 3.8009 | 1,116–1,132 |
| `no-output95` | 9.9430 | 2,175–2,199 |
| `no-relational95` | 1.0978 | 450–462 |
| `no-numeric95` | 5.1507 | 845–853 |

두 unknown 대조군의 짧은 시간은 유용한 문제 해결의 속도 우위가 아니다. 주 EML arm은 논리 R1보다 **느리고 크다**. 출력 재사용은 이번 workload에서 추가 숫자 정의/탐색을 피했지만 일반적인 최적 구성/속도 우위는 증명하지 않는다.

- 주 EML process 범위: **6.9853–7.2402 s**.
- 순차 batch의 peak child RSS: **26,860 KiB**. arm별 learned memory가 아니라 child process high-water의 최댓값이다.
- 작은 기본 demo: **5.103293350999593 s**, child RSS **19,536 KiB**. Python `perf_counter`로 fresh native subprocess를 측정했으며 Python startup/artifact write는 제외한다.
- `/usr/bin/time`이 없어 최초 timing launcher 호출이 실패했다. [기록](composition95-evidence/demo-time-unavailable.log)을 남기고 Python 표준 라이브러리로 다시 측정했다. 모델 실행 실패와 혼동하지 않는다.
- JSON bytes는 parameter 개수/heap 크기가 아니다. Fuel/diagnostic counters는 전체 CPU instruction/time이 아니다.

## 6. 테스트와 개입

| Suite | 결과 |
|---|---|
| 새 `test_composition95.py` | **26 passed**, 108.530 s |
| 전체 offline Python | **264 passed**, 1063.108 s |
| native `run.sh test` | passed |
| store/runtime/graph-store | 모두 passed |

기존 local HTTP Python 6개는 오프라인 suite에서 제외했다. Python socket guard이지 OS-wide network sandbox는 아니다. 기존 native integrity/HTTP 문제를 이번에 해결했다고 주장하지 않는다.

새 유한 oracle 테스트는 **64 fact subsets × C/D × 두 branches = 256 complete queries**, **576 complete binding/숫자/원본 witness 행**을 별도로 검사했다. 이 수는 위 40-process 결과에 포함시키지 않았다.

추가 검사는 다음을 포함한다.

- 400 malformed trees, 잘못된 타입 간선, 미래/순환 참조, 잘못된 branch와 primitive expansion.
- forged numeric value/support/claim/scope, 누락된 결과/잘못된 근거에 대한 no-repair rejection, 순서만 바뀐 같은 결과 집합의 허용.
- duplicate 원본 ID/tuple 및 파생 target 재입력 거절, alias object roles 보존, 빈 유한 관계 결과.
- 측정 누락, tiny numeric domain 실패, unsupported 음수 intermediate, budget exhaustion→unknown.
- source counterexample/철회, facts의 retract→observe version 변경, dependent application withdrawal, restoration, historical frozen core.
- standalone core에서 training episodes/views를 제거하고 discovery/replay/learner/live owner를 없앤 뒤 새 입력 inference.
- typed 형성 후 기존 관계 해석/새 관계 기저 형성, 세 단계 복합 output 재사용.
- 같은 owner의 snapshot replay, fresh-process 파일 복원, native lock, 실패한 checkpoint에서 상태 미공개.

[개입 출력](composition95-interventions.sexp)은 실제로 다음을 확인한다.

```text
D 적용: 9 complete rows; composite calls 18; numeric calls 45
사용한 정의 IDs: (2 3 4 5 6), 원본 사실/측정과 source/version/cell 가정 유지
worker 결과 누락: rejected95 independent-check
C 반례: C/D unknown, 정의 6개 유지, historical core는 complete
C 관찰 복원: D complete, 같은 definition count, 다른 정확한 core
exp calibration 철회: 독립 지지된 C 프로그램은 complete, exp 대응을 적용하는 D는 unknown
replay: true
```

측정 counter는 worker 일부 작업을 뜻한다. 검사자 비용/series 내부 비용 등이 포함된 총 연산량으로 해석하지 않는다.

## 7. 남은 한계

- 주 실험은 작은 한 r–s 관계 가족과 실수 함수 가족의 합성이다. 자유 텍스트/web 의미 추출, physical units, 임의 관계 interface 사이의 role remapping, 일반 predicate/조건 발명은 없다.
- observation schema, sign cells, constructor/admission 규칙, reuse-first 후보 순서는 고정된다. 유한 자료로 프로그램/배선을 고르는 형성은 귀납적·가설적 요소를 가진다. gradient가 없다는 이유로 순수 연역 학습이라고 부르지 않는다.
- library 전체≤8, episodes≤4, channels≤3 등 작은 상한을 유지한다. noisy 대규모/장기 성장이나 일반 completeness/scalability는 보이지 않았다.
- 반례 대응은 주로 적용 범위 철회/재활성화다. 일반적인 정의 수정과 의미 조건 발명을 완성한 것은 아니다.
- worker/checker는 일부 도구와 산술 primitive를 공유한다. 외부 oracle도 유한 입력의 증거다. 복합 수치 오차가 임의 깊이에서 보장되는 것은 아니다.
- well-formed core는 인증된 학습 원본의 증명이 아니다. session replay도 외부 관찰의 실제 진위를 인증하지 않는다.
- 공개 unknown 사유는 아직 coarse하며, 풍부한 누락 전제/부분 결론 인터페이스를 완성하지 않았다.
- **EML만의 학습력·압축·속도 우위나 새로운 세계 법칙의 발견은 확립되지 않았다.** 이번 진전은 같은 DLM의 형성·실행·근거·후속 형성 경로가 실제로 교차 연결됐다는 점이다.

## 8. 재현과 증거

```sh
cd /research/dlm_v0.0095
./scripts/run.sh compose95
./scripts/run.sh compose95-input < experiments/composition95/input-example.sexp
./scripts/run.sh proof experiments/composition95/interventions.l
python3 -B -m unittest discover -s tests -p 'test_composition95.py' -v
python3 -B tests/run_offline.py
./scripts/run.sh test
bash tests/store-tests.sh
bash tests/runtime-tests.sh
bash tests/graph-store-tests.sh
python3 -B adapters/composition95_experiment.py \
  --seeds 2 --queries 6 --repeats 2 --output /tmp/composition95.json
python3 -B docs/composition95-evidence/final_check.py
sha256sum -c docs/composition95-evidence/source.sha256
sha256sum -c docs/composition95-evidence/SHA256SUMS
```

- [설계/입력/상태/API 계약](composition95-design.md)
- [40-run raw report](composition95-experiment.json)
- [native demo](composition95-demo.sexp), [stdin demo](composition95-input-demo.sexp) — byte-identical
- [새 테스트 log](composition95-evidence/typed-tests.log), [전체 offline log](composition95-evidence/offline-tests.log)
- [native log](composition95-evidence/native-tests.log), [store/runtime log](composition95-evidence/store-runtime-tests.log)
- [실험 log](composition95-evidence/experiment.log), [환경](composition95-evidence/environment.json), [demo 측정](composition95-evidence/demo-metrics.json)
- [최종 checker](composition95-evidence/final_check.py), [최종 검사 결과](composition95-evidence/final-checks.json)

최종 검사는 **500 product hashes, 18 artifact hashes, 23 local links**, Python AST, shell syntax, whitespace 및 `git diff --check`를 확인했다. 원본 0093/0094의 실제 files/status/compiler와 README archive도 다시 확인했다.

Manifest는 제품/산출물의 일관성을 검사하는 것이며 결과의 과학적 진리나 외부 관측 원본을 인증하지 않는다.
