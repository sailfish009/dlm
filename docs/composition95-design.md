# 0095: 같은 DLM 안의 관계·수치·복합 기저 형성

기준 제안: `/research/design_20261104.md`. 이 문서는 **구현된 작은 실험의 계약과 한계**를 설명한다. 자유로운 의미 추출이나 일반적인 기저 공리 이론을 완성했다는 뜻이 아니다.

## 1. 소유자는 기존 Basis91

`basis-state91` / `execution-core91`, 기존 `basis91` API, 라이브러리, audit, replay, checkpoint, native lock을 확장했다. `*c95-state*`, 두 번째 숫자 모델, 별도의 95 checkpoint 소유자는 없다. 기존 독립 `eml93` 경로는 호환성을 위해 남아 있으나 이 실험은 그것의 state/session/learner를 호출하지 않는다. 재사용하는 것은 **native 산술·문법 생성·식 탐색·원시 전개 검사 함수**다.

한 라이브러리 안에 전역적으로 증가하는 prefix ID를 부여한다.

```lisp
(basis91 ID RELATIONAL-PATTERN RELATIONAL-BODY)
(numeric95 ID ARITY BODY EXPANSION BRANCH ORIGIN)
(composite95 ID REL-ID NUM-ID INPUT-PORTS ORIGIN-CHANNEL)
```

- 관계 기저는 기존의 역할 보존, 양의 연결된 이항 관계 패턴이다. 논리 본문과 `encoded91 eml94` 본문을 모두 유지한다.
- 수치 기저는 `one93`, `x93`, `eml93`, 이전 **수치** 기저의 `call93`로 구성되는 부분 함수의 정의다. 저장한 원시 전개와 실제 prefix 전개가 같아야 한다.
- 복합 기저는 관계 결합에 속하는 객체의 관측값 또는 이전 복합 기저의 출력을 수치 기저의 입력에 연결한다.

관계 planner/Attention92는 관계 정의만 후보로 삼는다. 따라서 `call91`로 숫자 정의를 호출하거나 `call93`로 관계 정의를 호출할 수 없다. 서로 다른 이름 공간을 사후에 붙이는 것이 아니라, **공통 ID와 prefix 검사 안에서 타입별 허용 간선을 검사**한다. 이후 관계 해석·형성도 같은 라이브러리에 새 관계 기저를 추가할 수 있다.

## 2. 타입과 역할 인터페이스

```lisp
(measure95 OBJECT-ROLE)
(output95 PRIOR-COMPOSITE-ID)
```

`measure95`의 인자는 수치가 아니라 관계 패턴의 **객체 역할 인덱스**다. 그 역할에 결합된 객체를 찾고 다음 관측에서 숫자를 읽는다.

```lisp
(measure95 OBJECT (z93 REAL-MICROUNITS IMAG-MICROUNITS))
```

객체 ID를 수치로 변환하지 않는다. 같은 객체에 역할 두 개가 결합되는 alias는 허용하며, 숫자 계산에 쓰이지 않는 중간 객체 역할도 결과에서 없애지 않는다. `output95`는 같은 관계 인터페이스를 가진 이전 복합 정의의 **실제 계산 출력**을 전달한다. 숫자 역할에 객체를 넣거나, 수치 정의를 복합 출력처럼 참조하거나, 미결합/범위 밖 역할을 참조하면 채택되지 않는다.

이번 타입 체계는 객체와 complex fixed-point scalar의 구분이다. **물리 단위·속성 이름·차원 분석·자연어 의미는 학습하거나 검증하지 않는다.** 객체마다 한 scalar 관측을 가진다는 구조화된 입력 규약과 관측 tuple의 역할 순서는 실험에 주어진다.

## 3. 상태와 실행 코어

기존 8-field state / 6-field core는 그대로 허용한다. `basis91 'types BRANCH`를 실행하면 같은 소유자를 확장한다.

```text
(basis-state91 2 SIGNATURE EPISODES LIBRARY READINGS AUDIT EPOCH
  (typed95 BRANCH CALIBRATIONS CHANNELS SCOPES))

(execution-core91 SIGNATURE EPISODES LIBRARY VIEWS EPOCH
  (typed-core95 BRANCH SCOPES))
```

- scalar epoch는 **모든 타입의 정의 개수**다. joint admission으로 정의 두 개를 추가하면 2 증가한다.
- 관찰/적용 범위 수정과 의미 보존 인코딩은 정의를 추가하지 않는다. 정확한 모델 식별에는 전체 core/audit가 필요하다.
- 실행 코어에는 숫자 학습 정답, target table, candidate pool, formation history가 없다. scope에는 source ID/version, basis ID, 현재 허용 sign cell만 들어간다.
- 동일한 기존 `basis-session91`은 audit를 재생하여 core와 관계 지지 자료를 비교한다. 숫자/복합 형성의 원본 자료와 채택 주장은 audit에 남는다.
- 실행 코어의 형태 검사는 인증된 학습 출처를 증명하지 않는다. 외부에서 받은 임의의 well-formed core에 암호학적 출처 인증을 제공하지 않는다. session replay 검사는 기록과 현재 모델의 일치를 추가로 검사한다.

## 4. 입력 관찰과 형성

직접 수치 관찰:

```lisp
(calibration95 SOURCE VERSION ARITY ROWS)
(row93 ID (NUMERIC-INPUTS ...) NUMERIC-TARGET)
```

관계로 묶을 관찰:

```lisp
(channel95 CHANNEL VERSION FACT-EPISODE FACT-VERSION MEASURES TARGETS)
(observed95 ID (ALL-OBJECT-ROLE-VALUES ...) NUMERIC-TARGET)
```

최소 3개의 서로 다른 수치 입력을 가진 원본 target record가 필요하다. 한 source 안의 중복 target ID와 객체 tuple, 중복 수치 입력, 중복 객체 측정은 허용하지 않는다. `derived95` 등을 원본 `observed95`로 받지 않는다. 다만 임의 사용자가 계산한 값을 외부 관측인 것처럼 재입력하는 행위를 암호학적으로 알아내지는 못한다. 보장하는 것은 **제품 내부에서 파생 출력을 원본 지지로 자동 재기록하지 않는 것**이다.

### A. 기존 수치 구성자 형성

`calibrate`는 관찰을 추가하고 `learn-numeric`은 기존 numeric prefix를 재사용해 EML 문법을 native CPU에서 탐색한다. 별도 EML93 state를 만들지 않는다.

### B. 관계가 수치 자료의 결합을 결정

현재 라이브러리의 관계 기저를 실제 실행해 원본 fact witness를 얻는다. 제공된 target의 객체 tuple이 그 결합에 속하는지 검사한다. 가능한 역할 연결을 열거하여 객체 관측값을 수치 입력으로 묶는다.

기존 수치 정의로 설명할 수 있으면 그것을 사용한다. 없으면 **관계로 묶은 관찰에서** EML 프로그램을 탐색한다. 새 숫자 정의와 그것을 쓰는 복합 정의를 하나의 `compose95` event로 함께 검사·채택한다. 사람이 원하는 EML 식이나 역할 연결 `(0,2)`를 입력에 주지 않는다.

### C. 출력이 후속 형성의 입력

다음 channel에서 먼저 현재 복합 기저들을 적용하여 얻은 `output95`를 입력 후보로 둔다. 이 값을 기존 수치 구성자에 연결할 수 있으면 새 복합 정의를 형성한다. 이는 단순 query log 저장이 아니라 **이전 복합 정의를 호출하는 새 실행 구조**다.

형성용 자료에는 기존 복합 출력의 source/version/cell 가정과 실제 관측값 근거가 함께 들어간다. 채택 시 원시 관계 join과 원시 EML 전개로 다시 검사한다. D의 지지는 D channel의 원본 target record다. 입력에 사용한 C 출력이나 C의 지지 자료를 추가적인 D 관측으로 세지 않는다. 한 원본 자료가 수치 정의와 복합 정의를 함께 지지해도 두 배의 독립 관찰이 되지 않는다.

## 5. 실제 주 실험의 그래프

입력 source 이름은 함수 이름을 주지 않는 `nalpha`, `nbeta`다. 실험용 외부 생성기는 정답을 알지만 제품은 숫자 관찰만 받는다. native 탐색 결과를 외부 oracle로 해석하면 다음과 같다.

```text
R1(a,b,c) := r(a,b) & s(b,c)
N2(x)     := E(x,1)                       # 시험 범위에서 exp
N3(x)     := E(1,N2(E(1,x)))               # 시험 범위에서 log
N4(u,v)   := E(N3(u),N2(v))                # 시험 범위에서 u-v
C5(a,b,c) := N4(measure(a),measure(c))
D6(a,b,c) := N2(output(C5(a,b,c)))
```

R1의 실제 실행 본문은 주 arm에서는 기존 EML94 코덱이다. `N4`와 `C5`는 같은 관계-수치 관찰에서 함께 생긴다. D의 데이터는 C와 **다른 객체 및 다른 관측값**을 가진다. 따라서 D 형성 시 사용하는 C 출력은 학습 때 저장해 둔 C 정답의 재조회가 아니다.

이 표기의 exp/log/차이는 외부에서 관찰한 동작 설명이다. 내부 정의는 EML 식이다. 구조적 전개 동일성, fixed-point 계산의 일치, 실제 관측 현상에 대한 경험적 대응은 서로 다른 계약이다.

## 6. 적용 범위와 수정

```lisp
(scope95 numeric95 SOURCE VERSION NUM-ID CELLS)
(scope95 composite95 CHANNEL VERSION COMPOSITE-ID CELLS)
```

sign cell은 EML93에서 가져온 고정 구분이다. 일반적인 적용 조건을 발명하는 학습기는 아니다. 각 현재 source의 cell에 충분한 서로 다른 원본 자료가 있고 **그 cell의 모든 관측**이 허용 오차에 맞을 때만 활성화한다. 반례를 버리고 나머지 일부만 골라 같은 cell을 유지하지 않는다.

- channel의 사실 episode/version이 현재 사실과 맞지 않으면 결합 지지가 비활성화된다.
- 관계 사실은 기존 API대로 `retract` 후 `observe`하여 새 version을 만든다. 기존 ID를 `observe`만으로 덮어쓰지 않는다.
- `observe-values` / `calibrate`는 새 관측 버전을 추가한다. 과거 자료는 audit와 frozen snapshot에 남는다.
- C의 적용 범위가 철회되면 C를 입력으로 적용하는 D의 범위도 재검사되어 비활성화된다.
- 정의와 적용 가정을 구별한다. N4 안의 N2/N3 호출은 명시적 프로그램 구성이다. C의 직접 관찰이 N4 프로그램의 대응을 독립적으로 지지하는 경우, 과거 exp calibration 철회가 계산 정의 자체를 삭제하지는 않는다. 그러나 D가 exp correspondence를 직접 적용하려면 N2의 현재 적용 범위도 필요하다.
- 현재 source snapshot에 없는 cell은 비활성일 수 있다. 과거의 모든 관측을 자동으로 합쳐 무조건 적용 범위를 넓히지 않는다.
- 이전 frozen core는 역사적 모델로 남는다. 실행 중인 query를 수정하지 않는다.

이것은 정의 재작성 전반이나 일반 조건 발명의 구현이 아니라 **의존성에 따른 경험적 적용 범위의 철회·재활성화**다.

## 7. 독립 검사와 unknown

실행은 Attention92의 기존 관계 경로를 사용한다. scalar worker는 저장된 numeric prefix 호출을 실제 실행한다. 검사자는 primitive relation join과 numeric primitive expansion으로 별도의 제어 경로를 실행하여 전체 결과, 숫자, 원본 fact ID, 관측 근거, 가정을 비교한다. 두 경로는 타입/일부 결합 도구와 EML 산술 primitive를 공유한다. 따라서 완전히 독립적인 두 산술 구현이나 형식적 전역 증명이라고 부르지 않는다. Python assignment/math oracle가 유한 실험의 추가 독립 검사를 한다.

누락·틀린 값·위조된 근거는 **거부**한다. reference 값을 worker 출력에 채워 넣지 않는다. 순서만 다른 같은 결과 집합은 허용한다.

측정 누락, 미지원 cell, 숫자 정의역 실패, 예산 부족은 `unknown`이다. 완료되지 않은 query의 일부 행은 complete 결과로 공개하지 않는다. 현재 공개 unknown 진단은 coarse하다. 풍부한 누락 전제 설명이나 일반 부분 결론 API를 완성한 것은 아니다. 완전한 유한 사실 문맥에 관계 결합이 없는 경우의 빈 표는 세계 전체에서의 부정 명제가 아니다.

## 8. 상한과 고정 요소

- 기존 signature≤4, fact episodes≤4, facts/nodes≤8, relational atoms≤3, object roles≤4, library 전체≤8, audit≤32, query fuel≤200000을 유지한다.
- scalar arity 1–2, expansion≤96 EML nodes, body grammar cost≤3, 생성 level당≤5000 후보, source rows≤12.
- 직접 calibration sources≤4, 관계-수치 channels≤3, 객체 측정≤8, runtime 결과≤512.
- prefix-only graph라 순환·미래 참조는 허용하지 않는다.
- formation은 재사용을 먼저 시도하고 출력 port를 측정 port보다 먼저 고려하는 **고정 정책**이다. 이것을 학습된 정책으로 부르지 않는다.
- fuel은 일부 검증·할당·candidate generation·숫자 급수 내부 작업·scope rebuild·replay 비용을 포함하지 않는다. 전체 CPU 비용이나 시간 보장이 아니다.

## 9. 구현 파일과 API

| 파일 | 역할 |
|---|---|
| `composition95-ir.l` | 공통 라이브러리의 typed 정의/간선/관측/core 검사 |
| `composition95-execution.l` | scalar dataflow, scope/provenance, worker와 no-repair 검사 |
| `composition95-evidence.l` | 관계로 묶은 관찰, 현재 scope 재구성, 숫자 채택 |
| `composition95-formation.l` | 기존 출력/수치 재사용, joint 수치·복합 후보와 검사 |
| `composition95-session.l` | 같은 Basis91 transition/audit/commit에 추가하는 사건 |

```lisp
(basis91 'types 'principal93)
(basis91 'calibrate SOURCE ARITY ROWS)
(basis91 'number-proposal SOURCE COST FUEL)
(basis91 'learn-numeric SOURCE COST FUEL)
(basis91 'observe-values CHANNEL EPISODE MEASURES TARGETS)
(basis91 'typed-proposal CHANNEL COST FUEL)
(basis91 'compose CHANNEL COST FUEL)
(basis91 'typed-query CHANNEL CONTEXT FUEL)
(basis91 'typed-infer MODEL CHANNEL CONTEXT FUEL)
(basis91 'typed-profile)
(basis91 'typed-evidence)
(basis91 'retract-values 'channel95 CHANNEL)
(basis91 'retract-values 'calibration95 SOURCE)
(basis91 'restore SNAPSHOT)
(basis91 'reset)
```

마지막 두 명령은 같은 기존 session의 메모리 restore/reset이다. 파일에 붙어 있을 때는 허용하지 않는다. `restore`는 data를 평가하지 않고 검사된 audit를 재생한다. 일반 관계 API, Attention92, 숫자 독립 실험 등의 기존 명령도 유지한다.

재현 및 실제 결과는 [release-0095.md](release-0095.md)를 참조한다.
