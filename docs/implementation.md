# v0.0076 구현 기록 — design.md P0/P1

## 범위와 변경

- 0075 소스·컴파일러·모델 store는 그대로 두고 별도 0076 디렉터리를 생성.
  초기 컴파일러만 복사하였고, symbolic/web/graph 사용자 store는 복사하지 않음.
- Maru 코어·컴파일러 소스는 0075와 `diff -rq` 일치. 새 구현은 DLM 응용 계층.
- `formula.l`: 유한 스키마·술어 arity·상수항 검사, 명제 원자 수집.
- `sequent.l`: 프로파일·서명·발생 순서를 보존하는 시퀀트/문제.
- `sequent-check.l`: 탐색기와 독립적인 G3c 규칙 재구성 및 인증서 DAG 검사.
- `sequent-search.l`: cut 없는 결정적 기준 탐색, 두 방향 판정.
- `countermodel.l`: 총 할당과 원 문제의 독립 의미 검사.
- `proof-store.l`, `scripts/proof*.sh`, `experiments/proof/`: 명시적 버전 저장,
  이전 상태 검사·잠금·dump 왕복·입력 해시 검사·과거 snapshot·원자적 교체.
- `adapters/fld.py`, `adapters/sexp.py`, `scripts/fld.sh`: 실제 FLD 문법 파서,
  전체 지원 범위 감사, gold 격리, data-only 배치 실행·평가.
- 새 파일·어댑터·스크립트·fixture를 compiler verify manifest에 포함.

## 원 설계의 구체화

1. P1에서는 binder를 도입하지 않았다. ground predicate tuple을 명제 원자로
   취급하며 자유변수·양화식·함수항·eq는 런타임 스키마 밖이다. 따라서 알파 동치,
   포획 없는 치환을 구현했다고 주장하지 않는다. 어댑터는 양화 범위를 파싱하되
   해당 문제를 unsupported로 분리한다.
2. 인증서는 전제가 먼저 나오는 위상 순서 DAG다. 임의 순서 DAG의 위상 정렬은
   하지 않으며 전방 참조를 명시적으로 거절한다. 동일 전제를 둘 이상 참조하는
   AND 노드는 허용한다. 탐색기는 현재 tree-shaped DAG를 생성하고 공유 최적화나
   시퀀트 캐시는 사용하지 않는다. 문맥이 다른 목표를 캐시 공유할 여지가 없다.
3. top은 명시적 top-right/top-left, bottom-right를 선택했다. cut/weakening/
   contraction을 별도 입력 규칙으로 허용하지 않는다. 중복식은 제거하지 않는다.
4. 모든 가역 규칙의 child가 필요한 AND 분기다. 열린 원자 leaf의 할당을 만들고
   반드시 원 문제에서 검사한다. 두 방향 모두 반모델이 있을 때만 UNKNOWN이다.
5. proof-store-v1은 단일 문제 및 `(search fixed budget)` 이벤트를 저장한다.
   기존 graph/web/symbolic 저장 형식과 통합하지 않았다. 저장된 인증서/반모델은
   매번 재검사한다. primitive 실행 비용을 재현하거나 학습 경험을 저장하는
   이벤트 저널은 아니다. 파일 rename은 원자적이나 fsync crash durability는 없다.
6. canonical problem SHA256는 외부 `sha256sum`으로 재계산한다. `sq-store?`는
   논리 증거를 검사하며, 전체 입력 해시 검사는 `scripts/proof-verify.sh`가 맡는다.
   원 파일 SHA256는 출처 메타데이터이고 canonical hash와 별개이다. 서명은 아니다.
7. 파싱 오류/지원 제한/예산 소진을 정답 UNKNOWN으로 바꾸지 않는다. runtime의
   P1 스키마 밖 입력은 invalid-input; adapter가 인식한 양화식/미해석 placeholder는
   unsupported. 고전 FOL 프로파일 자체는 아직 제공하지 않는다.

## FLD 자료 감사

검토한 원본: `FLD-generator/FLD_generator/formula.py`,
`formula_checkers/z3_logic_checkers/intermediates.py`, `datasets.py`.

- 생성기 binary chain은 같은 우선순위의 좌결합이며 보통 괄호로 중첩을 지정.
  부정은 다음 단위식, 양화 접두사는 현재 group 나머지 전체에 범위가 걸린다.
- negative_hypothesis_formula는 별도 negative 예제라 단순 부정으로 사용할 수 없다.
  실제 train row1의 목표는 not A, negative는 not DB이다.
- DISPROVED 행의 proofs_formula의 `hypothesis` 표지는 원 목표의 반대 방향 증명일
  수 있다. 이를 입력/인증서로 재사용하지 않고 실제 목표와 명시적 not 목표를 푼다.
- CWA world_assump_label은 UNKNOWN을 DISPROVED로 바꿀 수 있다. 평가에는
  실제 연역 상태 proof_label만 쓴다.
- `fake_formula`는 빈 NL 문맥에 임의 문장을 넣는 생성기 placeholder다. 원자처럼
  수입하거나 자연어 의미를 추정하지 않고 unsupported로 유지한다. 빈 형식 문맥
  자체는 유효한 빈 전제로 처리한다.
- 원자료 110000행을 수정하지 않았고 train/validation/test별 전행 사유와 원문,
  파일 해시, row, 버전을 export했다. `docs/fld-audit.json`은 간략 보고서.
  test split은 문법 지원 범위만 감사했으며 추론 성능/정책 선택에 사용하지 않았다.

전체 지원: train 38446/100000, validation 1938/5000, test 1935/5000.
각 split 미지원 분모/사유는 README와 audit.json 참조. 파싱 오류 0.
파싱 성공은 연역 가능성이나 해답을 보장하지 않는다.

## 검증과 정직한 한계

- 변경 전 0075의 명시된 회귀 명령 모두 성공: `baseline75.log`.
- 모든 G3c 규칙의 양성/규칙 위조/문맥 변조/참조 손상/분기 누락 검사를 실행.
- 독립 Python 진리표의 3392 시퀀트 × 4 할당 비교: 불일치 0.
- 총 18 Python 테스트, inherited graph20/Horn20 차등, store/source-free 회귀 통과.
- validation 첫100행, 지원44, 일치31, incomplete13 (각 방향 budget1000).
  전체 선택 행 기준31/100, 지원 행 기준31/44. 해결된31행만의 일치율100%를
  전체 정확도로 포장하지 않는다. 약21.4초/26004 탐색 의무; 확인기 비용 포함
  wall time이며 의무 수는 primitive 연산량이 아니다. 정책 업데이트/학습 없음.
- source-built release는 `release.txt`; candidate/next/third LLVM 및 stripped
  binary 동일성과 source-free 테스트를 compiler verify에서 확인한 뒤 promote.
- 자기호스팅 고정점은 재현성만 검증한다. FOL·등식·학습 개선 증거가 아니다.
- P2~P5, MLIR, 전체 모델 저장 migration, 자연어 의미 추출은 미구현이다.
  구현하지 않은 기능의 빈 파일이나 완료 표시를 만들지 않았다.

자료 라이선스: 로컬 FLD-corpus는 CC BY 4.0, FLD-generator는 Apache-2.0.
FLDx2 로컬 카드에는 별도 license 필드가 없으므로 재배포 시 upstream 조건과
attribution을 확인해야 한다. 원 Parquet를 소스 번들에 포함하지 않는다.
