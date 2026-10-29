# 0.0089 작업본 리뷰 — 웹 데이터 기반 재귀적 자기지도 학습

## 0. 대상과 결론

- 작업 디렉터리: `/research/dlm_v0.0089`.
- 기준: `/research/dlm_v0.0088` 전체를 복사한 `88a4551c3c978ce27b28a83935444f27d319da44` 코드.
- 이번 작업: 소스 리뷰, 네트워크 없는 로컬 재현, 리뷰/증거 추가. **학습 기능 구현이나 결함 수정은 하지 않았다.**
- `src/`, `adapters/`, `scripts/`, `tests/`, `experiments/`, `VERSION`, 기존 README는 복사한 그대로다. `VERSION`은 `0.0088`이며, 이 디렉터리는 아직 검증·승격된 0.0089 릴리스가 아니다.
- 공개 인터넷, DNS, 로컬 HTTP 서버를 사용하지 않았다. 수집 검사는 사전 생성 캐시 + `--offline`, HTTP 오류 검사는 가짜 응답을 사용했다.

**판정: 웹 수집 기반과 검증된 재귀 연산자 학습 기반은 있지만, 둘을 연결한 웹 자기지도 학습 실험은 아직 없다. 네트워크만 허용한다고 이 실험이 동작하지 않는다.**

첫 0089 실험은 일반 웹 자연어의 자율 이해보다 **고정 스키마 웹 자료에서 추출한 작은 그래프에 대한 다중 홉 질의와 검증된 연산자 재사용**으로 한정하는 것이 현실적이다. 원문을 임의의 세계 공리로 바꾸지 않는 현재 경계는 보존해야 한다.

우선순위의 의미:

- **P1 / 현재 결함**: 정상적인 저장·입력 거절 계약을 깨거나, 외부 입력 경계에서 프로세스를 종료시킨다.
- **P1 / 실험 선행조건**: 0088의 약속 위반은 아니지만, 목표로 하는 0089 실험의 유효성을 위해 먼저 구현·명세해야 한다.
- **P2**: 온라인 운영·규모 확장 전에 보완할 신뢰성/재현성 항목.

## 1. 현재 연결 관계

### 실제 존재하는 경로

```text
URL / GitHub·Wikipedia 검색
  → adapters/web.py
  → URL 키 JSON 캐시 + 원문 bytes / SHA-256 / URL / 취득 시각
  → acquisition74 S-expression
  → scripts/web.sh + web-ingest
  → web-state74 + 별도의 experiments/web/store
  → web-report: interpretation unresolved, admitted-facts 0
```

```text
명시적으로 공급한 이항 사실 / demo
  → dlm observe → axiom-space77
  → 후보 관계 합성 → space79 choose/certify86/accept
  → checked feedback → 정책 통계 / 검증된 definition
  → 다음 라운드가 기존 definition 재사용
  → dlm-session86 또는 joint dlm-session88
```

`contracts88`도 같은 native scheduler를 쓰지만, 명시적인 Boolean goal과 유한 검증 모델이다. 웹 문서에서 contract goal을 만드는 경로는 없다.

### 빠진 연결

```text
웹 원문
  -X→ 스키마별 해석 / 정규화 / 출처가 연결된 관측
  -X→ 자기지도 과제 / 분할 / 숨겨진 평가 목표
  -X→ native 학습 상태에 대한 트랜잭션 입력
  -X→ 이전 라이브러리를 이용하는 다음 웹 학습 라운드
  -X→ 학습 전후 전이 성능 / 비용 / 실패의 통합 평가
```

`run.sh`가 모든 모듈을 로드한다는 사실은 이 연결을 구현했다는 뜻이 아니다. `web-state`, `axiom-space77`, `graph75`, `ground82`, `space79`는 이름이 비슷해도 서로 다른 데이터 모델·저장 경로다.

## 2. 발견 사항

### R1. [P1 / 실험 선행조건] 수집 결과가 학습기의 관측이나 과제로 전달되지 않음

위치:

- `scripts/web.sh:13–24`
- `src/dlm/web.l:41–47,65–72`
- `src/dlm/repl.l:166–187`
- `src/dlm/contracts88-curriculum.l:36–44,145–164`

수집 스크립트는 별도 프로세스에서 웹 상태를 병합하고 보고한다. 재귀 학습 launcher에는 웹 bundle/import 옵션이나 웹 과제 큐가 없다. joint curriculum은 relations/contracts만 선택한다.

동일 Maru 프로세스에서 웹 문서 하나를 ingest한 뒤 `dlm step`을 두 번 실행해도 결과는 다음과 같다.

```text
(documents 1 native-episodes 0 native-definitions 0 contract-goals 0)
```

`admitted-facts 0`은 안전한 현재 동작이며, 이를 단순히 자동 `observe`로 바꾸는 것은 해결책이 아니다.

필요한 연결은 **버전이 지정된 해석기 → 출처 registry → 제한된 관측/과제 import → native commit**이다. 추출 불가 자료는 `unsupported`로 남기고, 수집 실패·미해석 상태를 학습 성공으로 집계하지 않아야 한다.

### R2. [P1 / 현재 결함] 비정상 웹 데이터가 명시적 거절 대신 SIGSEGV를 유발

위치: `src/dlm/web.l:7–18,29–32,41–43,49–62`.

`web-document?`는 proper-list 검사 전에 `dlm-length`를 호출한다. `web-ingest`도 incoming 문서 목록의 타입을 검증하지 않고 순회한다.

로컬 child process 재현:

```lisp
(web-document? (cons 'document 42))
(web-ingest (web-new) '(acquisition 74 42 ()))
```

두 경우 모두 **return code -11 / SIGSEGV**였다. assertion으로 거절한 것이 아니다. 정상 Python adapter 출력은 이런 형태를 생성하지 않지만, 손상된 캐시 이후의 bundle/저장 파일이나 미래 extractor/import 경로를 안전하게 처리하지 못한다.

수정 방향:

1. `sq-shape?` / bounded proper-list 검사를 `car`, 길이, 순회보다 먼저 수행한다.
2. 문서 필드의 개수·중복·필수 필드·타입과 hex 표현을 검사한다.
3. 문서 수, raw 길이, 이벤트 수, 전체 snapshot 크기를 제한한다.
4. malformed 입력은 오류 값을 반환하고 기존 상태를 보존한다.
5. CLI ingest뿐 아니라 `web-replay`/`web-verify-state`에도 같은 입력 계약을 적용한다.

### R3. [P2 / 현재 경계 부족, 관측 승인 연결 전 필수] replay 일관성은 원문 무결성이나 출처 검증이 아님

위치:

- `adapters/web.py:70–87,161–170`
- `src/dlm/web.l:7–25,59–62`
- `src/dlm/graph.l:110–134`
- `src/dlm/ground-space.l:28–46`

Python 캐시는 원문 digest를 다시 계산하므로 캐시의 hash만 변경하면 `invalid-cache`로 거절한다. 반면 native 웹 검증은 필드가 symbol인지와 이벤트 replay 일치만 검사한다.

서로 일관된 새 이벤트·상태로 전달하면 다음 세 경우 모두 `web-verify-state`가 받아들였다.

```text
(raw-hash-mismatch true)
(source-group-mismatch true)
(document-id-mismatch true)
```

이것은 현재 바로 가짜 Horn 사실이 승인된다는 뜻은 아니다. 현재는 문서를 미해석 상태로만 저장하기 때문이다. 그러나 이 상태를 향후 trusted evidence로 바로 연결하면 문제가 된다.

또한 Graph75의 provenance span은 숫자 범위 형태만 검사한다. Ground82의 evidence digest도 caller가 준 값이다. 어느 쪽도 웹 문서의 실제 bytes와 claim을 자동 대조하지 않는다.

필요한 계약:

```text
claim-id
  → document-id / raw-sha256 / 원문 byte 위치 또는 구조화 selector
  → extractor 이름·버전 / 정규화 버전
  → 추출된 typed relation
  → episode-id / task-id / train-validation-test 배정
```

- raw bytes와 hash, URL+hash 기반 document ID, source-group의 일치를 admission 경계에서 재검증해야 한다.
- span을 쓴다면 원문 byte offset인지 정규화 문자열 offset인지 명시해야 한다.
- UTF-8 외 인코딩·HTML 정제·JSON 경로 해석을 원문과 구별해야 한다.
- 해시 일치는 bytes의 일치이지 저자 인증이나 내용의 진실성 증명이 아니다.
- 같은 내용을 복제한 URL들은 독립 근거가 아니다. 현재 exact-byte SHA 그룹만으로 근접 복제·동일 원저작물 의존성을 구분할 수 없다.
- 원문 갱신·철회 시 영향을 받는 관측/과제를 찾아 무효화해야 한다. web-state에는 retract 이벤트가 없고 native episode와의 매핑도 없다.
- A77의 보존적 definition은 원문이 철회되어도 언어 정의로 남을 수 있다. 이를 유지하는 것과 해당 원문에 의존한 empirical claim/평가 결과를 유지하는 것은 구분해야 한다.

### R4. [P1 / 현재 결함, 0088에서 상속] ground 라우팅을 사용하는 joint checkpoint가 재시작에서 거부됨

위치:

- `src/dlm/contracts88-curriculum.l:97–104,132–133`
- `src/dlm/contracts88-session.l:19–27`
- `src/dlm/ground-bridge.l:91–99`

0088 리뷰의 결함을 복사한 0089에서도 재현했다. plain relation replay가 `g83-order`의 live 전역 캐시를 참조해 이벤트만으로 결정되지 않는다.

```lisp
(dlm 'open "/tmp/fresh-review89.sexp")
(dlm 'demo)
(dlm 'ground 'on)
(dlm 'curriculum 'relations)
(dlm 'relation-budget 1)
(dlm 'step)
(dlm 'step)
(dlm 'save)
```

```text
(round 1 (incomplete 1))
(round 2 (learned ...))
(rejected checkpoint)
```

새 프로세스의 open은 `(rejected snapshot)`이다. 문서 근거까지 저장하려는 웹 실험에서는 반드시 수정해야 한다. 수정 전 제한된 탐색에서는 `ground off`로 고정하고 이를 manifest에 기록해야 한다. 이 우회가 전체 저장 경로의 정당성을 증명하지는 않는다.

### R5. [P1 / 실험 선행조건] 현재 학습 의미와 용량으로는 일반적인 웹 자기지도 실험을 정의할 수 없음

위치:

- `src/dlm/axiom-space.l:28–34,77–109,119–145`
- `src/dlm/recursive86.l:30–44,49–68`
- `src/dlm/contracts88-curriculum.l:145–167`
- `src/dlm/learning.l:8–25`

현재 A77은 다음 제한을 갖는다.

| 항목 | 제한 |
|---|---:|
| 활성 episode | 8 |
| episode별 입력 사실 | 24 |
| 사실 형태 | ground 이항 atom |
| 학습 definition | 12 |
| primitive path 길이 | 최대 4 |
| indexed candidate pool | 512 |
| native 이벤트 | 256 |
| cumulative relation request | 100000 |

아홉 번째 episode 입력은 실제로 `(rejected schema-or-limit)`였다. 웹 adapter의 `--limit` 최대 20과 learner 수용량도 일치하지 않는다. 추출·보관·학습 window를 별도로 설계하지 않으면 작은 웹 수집부터 import가 중단된다. 단순히 모든 상수를 늘리면 proof closure와 전체 replay 비용도 커진다.

더 중요한 의미론적 구분:

```text
학습 전: edge(a,b), edge(b,c), ...
학습 후: 새로운 이름으로 compose(edge,edge), 더 긴 compose 재사용
```

이는 **보존적인 관계 정의와 프로그램 재사용**이다. 누락된 primitive `edge(a,c)`가 현실에서 참이라는 empirical rule을 발견한 것이 아니다.

재현 결과:

```text
(definitions 3 primitive-edge not-derived composed-path proved)
```

따라서 첫 실험을 "문서의 누락 링크를 자동 예측한다"로 설계하면 현재 learner와 목표가 맞지 않는다. "소스 그래프에서 확인 가능한 경로 질의를 예산 내 해결하고 이전 연산자를 재사용한다"가 적합하다.

`hits >= 2`도 독립적인 두 출처의 확인이 아니다. 한 episode의 여러 경로 인스턴스도 hits에 포함된다. 이를 세계 지식의 신뢰도로 보고하면 안 된다.

기존 `sl-*` 학습기에는 confirmed/contradicted partition이 있지만, 그것이 새 native recursive loop에 연결되어 있는 것도 아니다. 같은 저장소에 있다는 이유로 각 학습 모델의 보장을 합쳐서는 안 된다.

필요 사항:

- 사전 고정된 shard/window 선택과 용량 초과의 명시적 기록.
- 포화·불완전·용량 초과와 진짜 반례의 구분.
- task 유형에 맞는 learner 선택.
- primitive 사실, inductive hypothesis, 보존적 definition, finite contract theorem의 분리.

### R6. [P2 / 현재 결함] 중간에 끊긴 HTTP 응답이 failure record가 아니라 예외로 전파됨

위치: `adapters/web.py:92–110`.

가짜 opener의 `response.read()`에서 `http.client.IncompleteRead`를 발생시키면 `get_record`는 오류 tuple을 반환하지 않고 예외를 전파한다. 이 타입은 현재의 `URLError/OSError/ValueError` catch에 포함되지 않는다.

```json
{"uncaught_exception": "IncompleteRead"}
```

온라인 배치에서 이런 오류가 나면 해당 URL만 실패로 격리하지 못하고 실행 전체가 중단된다. 이번 재현은 실제 연결을 사용하지 않았다.

필요 사항:

- 예상 가능한 HTTP framing/connection 오류를 명시적으로 분류한다.
- per-URL outcome을 남기고 부분 성공을 보존한다.
- 429/503, Retry-After, 제한된 재시도·backoff·host별 요청 간격을 설계한다.
- 시도 수·전체 byte·전체 elapsed deadline을 별도로 제한한다. 현재 `timeout`은 전체 실험의 hard wall-time 상한이 아니다.
- 실패 때문에 synthetic observation을 생성하지 않는다.

### R7. [P2 / 온라인 운영 전] URL 검사는 scheme 검사이지 접근 정책이 아님

위치: `adapters/web.py:40–54,124–153`.

현재 `valid_url`은 다음 주소를 모두 허용한다. 실제 요청은 하지 않고 predicate만 평가했다.

```text
http://127.0.0.1/private
http://169.254.169.254/latest/meta-data/
http://[::1]/private
```

현재는 명시적인 로컬 CLI이므로 이것만으로 외부 공격에 노출된 SSRF 서비스라고 단정할 수 없다. 그러나 향후 문서·검색 결과·학습 결과가 새 URL을 제안하는 루프에서는 네트워크 경계가 필요하다.

권장:

- 첫 실험은 고정 provider/host allowlist와 명시적 URL manifest만 사용.
- redirect의 각 hop에도 같은 정책 적용.
- 자동 URL 모드에서는 private/link-local/loopback/내부망 대상 제한. 로컬 테스트 예외는 명시적인 별도 설정으로 격리.
- DNS rebinding 등은 문자열 검사만으로 해결되지 않으므로 실제 접속 대상 및 proxy 정책도 검토.
- robots, 이용약관, 라이선스, 요청 속도 및 민감 데이터 보관 정책을 온라인 단계에서 확인.

### R8. [P2 / 현재 저장 설계 한계] 동일 문서를 반복 취득해도 원문이 이벤트·스냅샷에 중복됨

위치: `src/dlm/web.l:41–47,49–62`, `scripts/web.sh:20–23`.

문서 목록은 ID로 dedup하지만 `acquire` 이벤트에는 raw를 포함한 전체 bundle이 남는다. `web.sh`는 매번 전체 상태를 별도 파일로 복사한다.

같은 작은 문서 하나를 반복 ingest한 실측:

| 취득 횟수 | 최신 snapshot bytes | 동일 raw 필드 출현 수 |
|---:|---:|---:|
| 1 | 1596 | 2 |
| 8 | 7245 | 9 |
| 16 | 13701 | 17 |

단일 문서의 중복 취득에 대해서도 최신 snapshot 크기는 횟수에 비례해 증가한다. 모든 과거 전체 snapshot을 보관하면 이 반복 사례의 누적 파일량은 횟수의 제곱에 비례해 증가한다. 다수의 서로 다른 문서에서는 dedup lookup과 replay 비용도 추가된다.

필요 사항:

- 원문을 내용 주소 기반 immutable blob으로 보관하고 이벤트는 digest/reference 위주로 저장.
- 이벤트/블롭 manifest 검증과 snapshot retention 정책.
- 성공적으로 처리된 batch fingerprint와 resume cursor 저장.
- 반복 재생이 문서·과제·학습 피드백을 중복 집계하지 않는 idempotency 계약.
- `web-state`와 `dlm-session88`을 반드시 거대한 하나의 파일로 합칠 필요는 없다. 대신 학습 checkpoint가 참조하는 불변 corpus/extraction/task manifest를 정확히 고정해야 한다.

### R9. [P1 / 실험 선행조건] 웹 전이 평가 및 누수 방지 프로토콜이 없음

위치: `adapters/recursive86_experiment.py`, `adapters/recursive_fld.py`, `experiments/fld/learn.l`, `adapters/web.py:161–170`.

기존 FLD 실험의 input/gold 분리와 cold/learned 비교는 재사용할 좋은 패턴이다. 하지만 웹 수집 경로에는 다음이 없다.

- train/validation/test의 source-family 단위 고정 분할.
- mirror·재수집·동일 문서 revision·근접 복제의 교차 split 방지.
- self-supervised task spec과 정답 oracle의 분리.
- 학습 라이브러리·정책을 동결한 평가 전용 실행.
- source→task→feedback→새 연산자→후속 과제의 연결 기록.

원문 하나를 그대로 질문과 정답에 넣거나, 모델의 예측을 다시 독립 관측으로 넣으면 학습 향상을 측정한 것이 아니다. 현재 문서 수·definition 수·계속 증가하는 round는 성능 지표가 아니다.

## 3. 0089의 권장 최소 실험

아래는 **구현 제안**이지 현재 제공되는 실행 명령이나 완료된 기능이 아니다.

### 3.1 첫 과제: 구조화된 웹 그래프의 검증 가능한 경로 질의

1. 원격 JSON/목록 등 하나의 고정 스키마만 지원한다. GitHub README나 Wikipedia 요약의 자유 문장 해석은 첫 실험 범위에서 제외한다.
2. 자료를 bytes 그대로 취득·보관하고 revision 또는 content hash를 고정한다.
3. 버전 지정 extractor가 허용된 typed binary relation만 만든다. 중간 claim registry에는 원문/selector와 출처를 남긴다.
4. A77 episode에는 이항 atom만 전달한다. 출처를 억지로 세 번째 argument로 넣지 말고 episode/claim registry에 연결한다.
5. 학습은 path2→path3→path4 정의를 만들고 후속 라운드에서 이전 연산자를 실제 사용한다.
6. 평가 대상은 보관된 소스 그래프에 대한 명시적인 경로 질의다. 외부 세계의 일반적 사실성이나 누락 primitive edge 예측을 주장하지 않는다.

정답은 별도 reference interpreter의 원시 edge/predicate-sequence join으로 계산한다. Native `a77-path`를 그대로 호출한 값을 독립 oracle이라고 부르지 않는다. 질의 endpoint는 문제 입력일 수 있으나, 숨겨진 정답/증명/평가 피드백은 learner 입력으로 전달하지 않는다.

### 3.2 상태 소유권과 저장

```text
선택적 Python acquisition adapter: HTTP와 캐시만 담당
  → immutable corpus manifest
선택적 schema adapter: 결정적 해석과 스키마 검증
  → claim registry + extraction manifest
고정 task protocol
  → train 입력 manifest / 평가 입력·정답 manifest 분리
하나의 native learner
  → observe/import → generate → execute → verify → admit
  → library + search frontier + manifest digest + processed-task cursor checkpoint
평가 driver
  → frozen library / policy, 별도 상태, 독립 oracle와 대조
```

수집/해석을 전처리로 분리해도 "하나의 native 학습기" 원칙을 훼손하지 않는다. Python이 승인·정책 업데이트를 대신하는 두 번째 learner가 되지 않도록 경계를 명시하면 된다. Native idle task 안에서 HTTP를 직접 기다리도록 만드는 것은 첫 단계에 권장하지 않는다.

학습 checkpoint에는 적어도 다음을 연결해야 한다.

- corpus/extraction/task/split manifest digest.
- extractor와 task generator 버전.
- 사용한 문서 revision·hash 및 processed batch/task ID.
- native source/runtime 식별자와 학습 설정, seed, 라이브러리 상태.
- 다음 작업 cursor와 실패/차단 상태.

restart 시 네트워크나 최신 검색 결과를 다시 조회해 과거 상태를 재구성해서는 안 된다. frozen 데이터로 같은 다음 작업을 재현해야 한다.

### 3.3 평가 프로토콜

- source family/revision grouping 및 분할을 학습 전에 확정한다.
- train-derived curricula만 학습기에 전달한다. 평가 결과를 검색 query 선택이나 재시도 우선순위에 되먹이지 않는다.
- eval 자료를 학습 session에 평범한 `dlm observe`로 추가한 뒤 idle 학습을 계속하지 않는다. 평가 전용 상태에서 frozen library/policy를 사용한다.
- cold, primitive-only grammar, recursive-reuse arm을 분리한다. 단순 `nd-cache` 대 `nd-ucb` 비교만으로 재귀 재사용 효과를 입증할 수 없다.
- 동일 자료·예산·질의 집합을 사용하고 실행 순서를 무작위화한다. 복수 source group/seed로 분산도 보고한다.
- proof만 맞는 trivial skip 질의와 실제 이전 연산자가 필요한 질의를 구분한다.
- 반복 라운드만 늘려 포화된 정의 수를 학습 진전으로 보고하지 않는다.

필수 지표:

| 범주 | 기록할 값 |
|---|---|
| 자료 | 발견/취득/실패/캐시 hit, raw bytes, 문서·독립 group 수 |
| 해석 | supported/unsupported/invalid, 추출 coverage, source-span 검증 실패 |
| 학습 | 실제 승인·재사용 수, 부모 연산자 dependency, checked feedback, unknown/blocked/capacity |
| 평가 | 전체 질의 대비 supported coverage, solved@budget, oracle 정답 일치, 잘못된 승인 수 |
| 비용 | wall/CPU/RSS, proof-check 비용, replay/checkpoint 비용, 저장 bytes |
| 복원 | 새 프로세스의 동일 다음 작업, 중복 피드백 방지, source 변경 영향 |

정확도는 supported subset만 조용히 선택하지 말고 원래 선정 자료 대비 coverage와 함께 보고한다. HTTP 수집 비용, 학습 비용, 평가 비용은 분리하되 전체 end-to-end 비용도 남긴다.

## 4. 네트워크가 막힌 지금 할 일과 나중에 할 일

### 지금: 오프라인 준비

1. R2/R4를 먼저 수정하고 malformed/restart 회귀 테스트 추가.
2. 단일 스키마 extractor와 claim registry, source binding 검증 구현.
3. 캐시 fixture로 문서→관측→과제→연산자→다음 라운드 재사용의 end-to-end 테스트 구현.
4. frozen corpus/split/task manifests 및 idempotent import/resume 구현.
5. 8×24 제한 안의 사전 고정 micro-shard로 파일 기반 리허설.
6. 가짜 응답으로 truncated body, 429/503, redirect 거절, oversize, timeout, mixed success/partial failure 검증.
7. cold/recursive arm과 독립 oracle을 네트워크 없이 검증.

### 이후: 온라인 실행

1. provider·schema·라이선스·접근 정책 확정.
2. 승인된 URL/revision manifest를 작은 규모로 취득.
3. 네트워크를 끊어도 동일 frozen corpus로 재실행되는지 확인.
4. 사전 확정한 평가 프로토콜로 대조 실험.
5. 실제 취득 성공률/실패 원인과 학습 효과를 별도로 보고.

### 실험 시작 gate

- [ ] 웹 문서가 실제로 train 관측/과제에 연결되고 출처를 역추적할 수 있음.
- [ ] 손상 입력이 SIGSEGV 없이 거절됨.
- [ ] 원문 hash/ID/group/selector 검증이 admission 경계에서 수행됨.
- [ ] source update/retract가 관련 과제·평가 근거에 반영됨.
- [ ] 동일 batch 재처리와 restart가 학습 피드백을 중복시키지 않음.
- [ ] partial frontier + library + manifest가 새 프로세스에서 동일하게 복원됨.
- [ ] 학습과 평가 사이 source-family 누수가 없음.
- [ ] cold/recursive arm이 동일 oracle과 예산으로 비교됨.
- [ ] unknown/실패/포화를 정답·학습 성공으로 집계하지 않음.
- [ ] 용량 상한과 데이터 보관·retention 정책이 명시됨.

## 5. 실행 증거와 범위

새 증거 디렉터리: `docs/review89-evidence/`.

| 항목 | 결과 |
|---|---|
| `offline_probe.py` | 네트워크 없는 수집/오류/출처/용량/restart 재현 완료 |
| `./scripts/run.sh test` | 통과, `native-tests.log` |
| `test_recursive86.py` | 8개 통과, 12.213초 |
| `test_contracts88.py` | 15개 통과, 25.218초 |
| packaging 단일 회귀 테스트 | 실패 — 기존 `.gitignore` 누락 상속 |
| source manifest | 일치 |
| test manifest | `.gitignore` 불일치 |

기존 전체 Python 115개 테스트를 이 작업에서 다시 모두 실행하지 않았다. `test_web.py`는 로컬 HTTP 서버를 사용하므로 이번 무네트워크 점검에서는 실행하지 않았다. 그 대신 실제 adapter/shell/native bridge를 seed된 cache의 `--offline` 모드로 검사했다. 기존 0088 전체 테스트 결과를 이번 0089 실행 결과로 대체해서 표기하지 않는다.

재현 명령:

```sh
cd /research/dlm_v0.0089
python3 -B docs/review89-evidence/offline_probe.py
./scripts/run.sh test
python3 -B -m unittest discover -s tests -p 'test_recursive86.py' -v
python3 -B -m unittest discover -s tests -p 'test_contracts88.py' -v
```

`offline_probe.py`는 수정 후에도 전부 통과해야 하는 regression suite가 아니라 **현재 관찰을 JSON으로 출력하는 리뷰 도구**다. 예를 들어 `raw-hash-mismatch true`와 return code `-11`은 결함 재현 결과이며 제품 테스트 통과를 뜻하지 않는다. mutable 실험 상태는 임시 디렉터리에만 생성한다.

현재 잘된 점도 유지해야 한다: 원문 bytes의 data-only 전달, Python 캐시의 hash 재검증, 실패를 가짜 사실로 채우지 않음, search와 admission의 분리, 기존 연산자를 다음 후보 생성에 실제 재사용하는 native 루프. **다음 작업의 핵심은 새 탐색 기법보다, 이 루프에 출처가 검증된 웹 과제와 누수 없는 평가를 연결하는 것**이다.
