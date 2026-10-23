# Silicon 분석: Maru DLM에 가져올 구조

## 범위와 결론

대상: `/research/silicon` 로컬 소스, HEAD `ff386aec`.
비교 대상: `/research/dlm_v0.0086`.
README뿐 아니라 상태, 실행, 계약 호출, 분기/병합, 경로 조건, consume/produce,
실패 후 재시도, solver 경계와 일부 회귀 fixture를 직접 읽었다.
Scala/sbt·Z3 실행 환경은 PATH에서 확인되지 않아 빌드·실행 테스트는 하지 않았다.
이는 정적 설계 분석이며 Silicon 전체의 정확성/성능 감사가 아니다.
운영 소스·테스트·런타임은 변경하지 않았다.

**핵심 결론:** Silicon 전체를 Maru에 이식하기보다, 계약 기반 기호 실행의 작은
부분집합을 기존 생성/비결정 실행/커널 루프에 넣는 것이 유용하다. Silicon은 생성기나
학습기가 아니다. 기존 DLM이 생성하고, Silicon에서 배운 구조로 절차의 의미를 검사한다.

## 실제 소스에서 확인한 구조

| 파일 (Silicon 경로 `src/main/scala/`) | 확인 내용 | DLM 적용 |
|---|---|---|
| `state/State.scala:29-87` | store g, heap h, oldHeaps, invariant contexts, retry/permission/cache 상태 분리 | 지식·작업 상태·자원·경로 조건·이전 상태 분리 |
| `supporters/MethodSupporter.scala:47-126` | 사전조건을 가정한 상태에서 본문을 실행하고 사후조건을 검사 | 생성 절차 자체의 계약 검증 |
| `rules/Executor.scala:564-654` | 호출 시 사전조건 consume, 반환 fresh 기호, 사후조건 produce | 검증된 모듈 계약 재사용 |
| `rules/Brancher.scala:35-75, 185-244` | 증명된 불가능 경로만 제외하고 결과 결합 | 실행 분기를 모두 검증하되 불가능성 증명으로 가지치기 |
| `decider/PathConditions.scala:27-84` | 분기 조건, 가정, 정의, mark/push/pop/after | 가정의 scope와 증분 증명 문맥 |
| `rules/ExecutionFlowController.scala:53-99` | 로컬 solver scope 진입/복구, 결과만 전달 | 분기 가정/임시 결과의 누출 방지 |
| `rules/Consumer.scala:27-114` | assertion/resource 소비와 snapshot 전달 | 전제 검사와 변경 권한 관리 |
| `rules/Producer.scala:24-120` | assertion/resource 생산 | 검증된 계약 적용 후 작업 상태 갱신 |
| `rules/Executor.scala:256-350` | 수정 변수 havoc, invariant 초기 성립/보존 검사 | 반복 절차의 검증, 단순 실행 횟수와 구별 |
| `rules/Joiner.scala:46-115` | branch-local 결과 수집, 조건을 보존하여 합류 | 중복 후속 실행 절감 후보 |
| `state/State.scala:430-597` | 상호 배타 조건 아래 Ite store와 조건부 heap 병합 | 무조건 union 대신 조건부 결과 유지 |
| `rules/ExecutionFlowController.scala:103-169`, `rules/StateConsolidator.scala:63-143` | 실패 시 문맥 복구·상태 정규화·더 완전한 재검사 | 즉시 실패/재시작 대신 제한적 의미 보존 재시도 |
| `decider/Decider.scala:377-434`, `decider/ProverStdIO.scala:247-284` | SMT 증명 결과와 timeout/unknown 관련 경계 | 명시적인 proved/counterexample/unknown 인터페이스 필요 |
| `interfaces/Verification.scala:31-151` | Success/Unreachable/Failure 및 실패 문맥·unknown 원인 | 실행 불가와 해결 성공을 다른 데이터로 기록 |

`src/test/resources/errorMessageTests/methodInlining/withArgsNRes.vpr`에는 본문과
사후조건이 어긋나는 예제가 있고, `whileToIfGoto/simple.vpr`에는 유지되지 않는 invariant
예제가 있다. `conditionalizePermissions/silicon_0008.vpr`에는 greedy 검사에서 증명하지
못하는 권한 예제가 예상 실패로 명시된다. 이들을 실행해 확인한 것은 아니며,
DLM의 실패/미완료 회귀 테스트를 설계할 소재로 참고했다.

## 1. 최우선: 생성한 프로그램을 계약으로 검사

현재 `recursive86.l:3-16`의 n86-certify는 a77-certify에 위임하여 관계 합성 정의를
검사한다. `n86-program`이 만드는 것은 주로 certify86/accept 후보 프로그램이다.
임의의 변수 변경·상태 변화·절차의 사후조건을 검사하는 일반 프로그램 검증기는 아니다.

가져올 개념은 Hoare 형태의 계약이다.

```
{Pre} Program {Post}
```

추가할 계약 정보:

```
preconditions
postconditions
read/write footprint
resource requirements
frame (보존할 상태)
body identity / dependency revisions
proof or checked verification obligations
scope / domain / version
```

실제 프로그램 검증에서는 Pre를 가정하고 본문을 기호적으로 실행한 뒤 Post를 검사한다.
호출자는 Pre를 충족해야 하며, 호출 후에는 검증된 Post만 사용할 수 있다.
일부 실행 예제에서 통과한 것을 모든 입력에 대한 계약 증명으로 일반화해서는 안 된다.
처음에는 유한 Boolean/상수 상태 공간에 범위를 명시하고 검사하는 것이 현실적이다.

### 계약 검증과 계약 호출의 구별

MethodSupporter는 본문과 계약을 검증한다. Executor의 MethodCall은 매번 본문을
펼치는 대신 계약을 적용한다. 이것을 DLM에 옮기면:

```
처음: 본문 검증 -> 검증된 모듈 요약 보관
재사용: 현재 상태에서 Pre 증명 -> 요약의 Post/effect 적용
```

단, 외부 추상 메서드/신뢰 계약은 별도 전제다. 문서에서 추출한 Post를 검증된 본문
효과처럼 자동 승인하면 안 된다. 본문 hash뿐 아니라 공리/조건/버전/검사기와 의존성의
일치가 필요하다. 이 재사용이 실제로 재검사 비용을 줄이는지는 별도 실험해야 한다.

## 2. 가장 중요한 의미 구분: 생성의 OR와 실행 검증의 AND

현재 DLM의 choose는 대체로 후보 프로그램/정의 중 하나를 찾는 existential 선택이다.
Silicon Brancher는 프로그램의 if에 대해 실행 가능한 true/false 경로를 처리하고
검증 결과를 결합한다. 둘은 같은 연산이 아니다.

```
search-choice:    Program A 또는 Program B 중 유효한 하나를 찾음
runtime-branch:   선택한 프로그램에서 가능한 모든 환경 경로가 계약을 만족해야 함
```

예: `if has_permission then write else skip`가 무조건 written을 보장한다고 주장할 때,
then 경로만 성공해도 된다고 처리하면 잘못된 검증이다. Pre에서 has_permission을
증명하거나, else 경로도 계약을 만족하도록 만들어야 한다.

DLM에는 서로 다른 opcode/의무를 권한다.

- 후보 탐색 OR: 하나의 유효한 계획을 찾기.
- 프로그램 조건 분기 AND: 모든 feasible 경로의 계약 검사.
- 환경의 비결정성과 에이전트가 선택하는 행동도 별도 의미로 지정.

불가능 경로는 그 불가능성이 증명됐을 때만 제외한다. 검사 시간 초과/전제 부족은
불가능성이 아니므로 계속 검사하거나 unknown으로 남겨야 한다.

### 공허한 성공을 학습 성공으로 세지 말 것

Silicon은 도달 불가능 경로를 정상적으로 종료할 수 있다(Joiner의 entries.empty,
Executor의 inhale false 등). 검증에서 이는 타당한 제어 처리지만, DLM 문제 해결에서
"불가능한 Pre를 가정했으므로 모든 Post가 성립"을 해결책 발견으로 세면 안 된다.
계획/답변 승인에는 적용 가능한 전제·도달 가능한 witness가 따로 필요하다.

## 3. 상태를 분리: 지식과 자원은 같지 않음

Silicon State의 g/h/oldHeaps와 permission chunk 구분을 그대로 복사할 필요는 없지만,
DLM이 상태 변경 절차를 생성하려면 아래 분리가 필요하다.

```
persistent knowledge + provenance   반복해서 사용할 수 있는 지식
symbolic store                     변수/작업 값
path conditions                    현재 분기에만 유효한 조건
linear resources / capabilities    소비·이전될 수 있는 권한
old-state snapshot                 변경 전 값의 논리적 참조
pending proof obligations          미해결 검증 과제
```

권한 chunk는 자원ID, 인자, 값 snapshot, permission을 가진다(`state/Chunks.scala:32-69`).
초기 DLM에서는 복잡한 fractional permission 대신 단순 소유/읽기/쓰기 토큰부터
시작할 수 있다. 하지만 읽기 권한의 복제와 쓰기 권한의 독점 규칙은 명세해야 한다.

**일반 지식은 사용했다고 삭제하지 않는다.** consume은 모든 사실을 지우는 기능이
아니라 필요한 assertion/권한을 검사·이전하는 의미다. 출처 철회도 권한 소비와는 다르다.
Silicon의 heap snapshot은 논리적 이전 메모리 값이지 파일 checkpoint가 아니다.
이를 그대로 가져와 DLM의 디스크 replay 비용이 해결된다고 볼 수 없다.

## 4. 효율에 참고할 부분: 조건부 검사와 검증된 요약

### 로컬 scope

ExecutionFlowController는 pushScope/popScope로 임시 가정을 제한한다. DLM도 전체
지식 재구성 대신 기반 문맥 + 분기 delta로 로컬 검사를 구성할 수 있다. 다만 이것은
논리 실행의 증분화다. crash-safe persistence나 checkpoint 인증은 별도 설계다.

### 실패 시 정규화 후 제한적 재시도

현재 DLM은 verification 미완료를 defer한다. Silicon은 특정 실패에 한해 이전 mark로
복구하고 동일한 의미의 상태를 consolidate한 후 재시도한다. DLM에서는 정규화·동일식
정리·증명 인덱스 확장 등을 한 차례 시도할 수 있다. 실패를 없애려고 임의의 새 전제를
추가해서는 안 된다.

### 분기 병합은 후순위

State.merge는 상호 배타 조건을 전제로 Ite 값을 만들고 heap 권한을 조건화한다.
단순 union이 아니다. 독립적인 생성 후보들은 자동으로 상호 배타인 실행 경로가
아니므로 같은 방식으로 섞어서는 안 된다.
초기에는 의미가 같은 상태/증명 문맥의 공유부터 도입하고, 일반 병합은 나중에 검증할 것.
소스 자체도 merge 직후 무조건 consolidation하는 것이 성능을 낮췄다는 주석을 둔다.
"매번 정규화/합류하면 빠르다"는 가정은 피해야 한다.

## 5. 반복 절차는 invariant로 검사

Executor의 루프 처리는 수정되는 변수를 fresh 값으로 바꾸고(havoc), 다음을 검사한다.

1. 진입 시 invariant 성립.
2. invariant와 guard 아래 본문 실행.
3. back edge에서 invariant 보존.
4. 종료 경로에서 invariant와 negated guard로 목표 검사.

DLM에 적용하면 생성기가 invariant 후보를 제안하고 커널이 검증하는 학습 문제로
만들 수 있다. 초기에는 유한 상태/작은 수치 범위로 제한할 것. 이 분석 경로만으로
절차 종료성까지 보장한다고 주장할 수는 없으며, 종료 증명/variant 또는 명시적 실행
예산은 별도로 필요하다. 이것은 DLM 학습 라운드를 반복하는 것과도 다른 기능이다.

## 6. 그대로 가져오면 안 되는 경계

### SMT boolean 결과를 자체 증명서로 간주하지 않기

Silicon의 decider/prover 경로는 SMT에 `not goal`을 추가해 unsat 여부를 묻는다.
고수준 check/assert는 Boolean이지만 실패 문맥에 model/reasonUnknown 정보를 보존한다.
False 반환이 곧 검증된 반례라는 뜻은 아니다. 이 소스 경로가 DLM용 독립 증명 검사기
형태의 certificate를 자동 제공한다고 볼 수도 없다.

Maru에서는 `proved + checked proof`, `counterexample + checked model`,
`unknown + reason`을 구분해야 한다. 초기엔 기존 Horn/G3c·유한 상태 검사 범위로
시작하고, 수치/배열/양화 때문에 SMT가 필요해질 때만 명시적인 backend로 분리한다.
독립 검사 가능한 certificate가 없으면 SMT 신뢰 의존성 확대를 분명히 표시해야 한다.
SMT 설치를 Maru self-host/bootstrap의 필수 조건으로 만들 필요는 없다.

### 무조건 inhale/assume 금지

계약 검증 내부에서 Pre를 가정하는 것과 외부 세계 주장을 승인하는 것은 다르다.
Wikipedia/GitHub/고득점 SO에서 얻은 문장도 출처·버전·조건을 지닌 접지 공리 후보로
처리하고, 생성기가 만든 주장을 임의로 전역 가정에 추가해서는 안 된다.

### 복잡한 기능의 일괄 이식 금지

quantified permissions, magic wand, 병렬 verifier pool, trigger 설계, 전체 mutable
heap 및 fractional permission을 첫 버전에 넣지 않는다. Scala/Silver/sbt/Z3 전체를
native DLM에 감싸는 것도 사용자의 non-LLM/native 방향과 별도 의존성 결정이다.
소스는 MPL-2.0 표기다. 직접 복사/수정 배포는 해당 파일의 고지·조건 검토가 필요하며,
초기엔 원리를 이해하고 Maru로 재구현하는 편이 적절하다.

## 권장 최소 구현 순서 (아직 구현하지 않은 제안)

### 단계 A: 작은 계약 IR와 기호 실행기

기존 IR/S-expression을 사용해 순수 Boolean·상수·유한 상태의 assign/assert/if/call만
지원한다. 지식 문맥, 작업 상태, path condition, effect footprint, obligations를 분리한다.
임의의 Maru 프로그램 전체를 검증하려 하지 않는다. 새 MLIR dialect도 선행 조건이 아니다.

### 단계 B: 생성기와 검증기 연결

```
question/goal IR
 -> 규칙 기반 프로그램 후보
 -> Screamer형 후보 선택 (OR)
 -> 계약 기반 기호 실행/실행 분기 검사 (AND)
 -> 독립 검증
 -> 적용 범위가 붙은 해결 절차 저장
 -> 이후 목표에서 재사용
```

질문 자연어 해석과 웹 공리 추출은 여전히 별도 작업이다. 이번에 Silicon 분석만으로
이 기능들이 생긴 것은 아니다.

### 단계 C: 요약 재사용과 실패 피드백

검증된 계약·효과·의존성의 조합을 재사용 단위로 저장한다. 실패의 사전조건/사후조건/
권한 부족/unknown을 구분해 생성기에 돌려준다. 실제 후속 목표에서 절감된 검사 비용을
측정한 뒤에야 학습 가치로 삼는다. 몇 개 실행 예제의 성공을 보편적 정리로 승격하지 않는다.

### 필수 반증 테스트

- then만 성공하고 feasible else는 실패하는 프로그램 거부.
- 모순된 Pre만으로 목표 달성을 주장하는 후보 거부/적용 불가 표시.
- 분기에서 추가한 가정·권한·임시 변수가 형제/부모로 누출되지 않음.
- source/contract/body 버전 변경 시 부적합 요약 재사용 차단.
- 같은 지식의 반복 읽기는 허용하되 독점 쓰기 권한의 이중 소비 거부.
- invariant 초기 성립·보존·종료 목표 각각의 실패를 구분.
- timeout/unknown을 반례·불가능 경로로 오인하지 않음.
- 로컬 검사/요약 재사용 전후 검증 결과 같고, 관리 비용 포함 시간 측정.
- 새로운 검증 상태/미해결 과제도 native 저장/새 프로세스 복원에서 보존.

## 최종 추천

**먼저 "작은 계약 기반 기호 실행 검증기"를 기존 Maru 생성 루프에 붙이는 것이
가장 가치 있다.** 이는 현재의 제한된 관계 정의 학습을 검증 가능한 해결 절차 생성으로
확장하는 연결점이다. 그다음 검증된 모듈 요약을 재사용하고, 필요한 경우에만 자원·루프·
수치 이론을 늘린다. Silicon 전체 포팅, MCTS·병렬화·복잡한 heap 이론 추가보다 우선한다.
