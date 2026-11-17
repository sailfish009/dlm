# DLM 0.0270 — 관계형 fixture와 타입 구조: 의무 분해가 작동하는 원리

0.0269의 구성요소 분해(design-components-0269.md)가 예측한 순서대로 진행했습니다:
**관계형 fixture 먼저, 그 위에 구조 실험.** 단항 fixture에서 S1/S2는 null일 것이라는
사전예측 아래, 바인딩이 자명하지 않은 세계에서 판별력을 확보한 뒤 측정했습니다.

## 1. 관계형 fixture (RELATOM)

- 엔티티 3개, 단항 술어 3 + 이항 술어 3 → **36개 ground 원자** (uint64 마스크,
  기존 WENT=6 바이트에 패킹 — 랩의 모든 시그니처 보존).
- 규칙 63개 = 단항사슬 18 + **관계합성 27** + 브리지 18. 핵심 스키마:
  `B(r2,e1,e3) ← B(r0,e1,e2), B(r1,e2,e3)` — 중간 엔티티 e2가 바인딩입니다.
  커널은 여전히 작은 명제 Horn 검사기(변수/통일 없음; 바인딩은 ground 인스턴스에 내장).
- 목표: 이항 원자만, depth-파라미터 풀(전체 후보로 도출 가능하지만 ≤depth−1 부분집합으로는
  불가능). per-goal witness 내장, 독립 도달성 감사.
- S0 특징: 엔티티-블라인드 수치(술어 one-hot + support + **goal-상대** 바인딩 중복).
  절대 엔티티 identity는 통제 arm(S0e)과 S1 토큰에만 존재합니다.

### 독립 검증 (tools/check_parity_rel.py)

```text
RULES-PASS      63 ground rules == 독립 스키마 재구성
FEATURES        66,600 특징값 + 2,160 utility, maxerr 4.4e-7
WITNESS-REACH   181 목표, 도달성/위반 0
DP-LABELS       1,080 라벨, Python 무메모 열거와 mismatch 0
PARITY-REL-PASS
```

C 내부 DP-AUDIT 24/0, BOUND-ASSERT ok. 단항 회귀: EPTRAIN=1 B-arm 가중치가
0269와 byte-identical (헤더에 relatom/typed/oblread/entfeat/typedshuf 필드 추가).

### 판별력: 바인딩 앨리어스 census (tools/alias_census.c)

동일 특징행을 가진 후보 그룹 안에서 커널 DP 라벨이 갈리는 경우를 셌습니다:

```text
depth 2 (훈련):  16/240 상태 top-mixed (6.7%)
depth 4 (평가):  95/240 train, 99/240 test (~40%)
```

**평가 깊도에서 상태의 ~40%가 S0 특징만으로는 최선 순위를 매길 수 없습니다.**
fixture가 판별력을 가진다는 정량적 증거입니다. (훈련은 depth 2, 평가는 depth 4 —
0260 이래의 프로토콜; 앨리어스 분포가 깊도에 따라 다름을 명시합니다.)

## 2. 구조 실험 (같은 라벨·같은 에피소드 트레이너·같은 탐색, 계약 없음)

branch 5, 예산 4, 5시드 71–75, goaldepth 4 평가. 계약 축은 격리했습니다
(구조 질문만; 계약 이득은 0268에서 확립).

- **S0**: set transformer, 관계형 S0 특징.
- **S0e**: + 절대 엔티티/역할 one-hot 18차원 (토큰 없이 바인딩 정보 — T1 통제).
- **S1**: 타입 토큰 `[state, candidates, facts(known 원자), obligations(미증명 목표)]`,
  타입쌍별 어텐션 scale/bias, 원자 임베딩 = 술어 + 엔티티 + 역할 (T2/T3).
- **S2**: S1 + 의무 조건부 readout (score += Wobl·mean(oblig LN)) (T6).
- **S1shuf**: 사실 토큰 원자 identity를 고정 derangement로 치환 (내용 파괴,
  개수·타입 구조 보존, 후보/의무는 진실 유지 — 훈련·평가 일관).
- **S0_focus / S1_focus**: 의무 포커스(FOCUS) — 미증명 목표에서 역방향으로 닿는
  후보만 남김 (Rocq 의무 분해, T3 마스크).

파라미터: S0 ~19.7k, S1 26,660, S2 26,692 (예산 ~2만 유지). gradcheck 전 파라미터
유한차분 rel 1.5e-10 + TYPED-GRAD 생생성 게이트. 순열 등변은 후보 **그리고 사실 토큰
순서** 치환에서 ~1e-15.

### 결과

```text
arm         greedy   beam     dfs      dfs_full   nodes
S0          0.2397   0.3504   0.7438   0.7420     6474
S0e         0.2314   0.3239   0.7438   0.7340     6639
S1          0.1835   0.2843   0.7620   0.7600     7237
S2          0.2050   0.3124   0.7537   0.7400     6048
S1shuf      0.2000   0.2876   0.7504   0.7440     7209
S0_focus    0.4165   0.5141   0.8050   0.7980     3514
S1_focus    0.4297   0.4992   0.8033   0.7960     3659

천장(무계약 완전탐색 branch 24, 시드 무관): 0.8182
```

```text
S1 − S0        +1.82pp  2se 4.39  ns
S2 − S1        −0.83pp  2se 5.04  ns
S0e − S0       +0.00pp  2se 4.85  ns
S1 − S1shuf    +1.16pp  2se 4.42  ns
S2 − S0        +0.99pp  2se 2.24  ns
S0_focus − S0  +6.12pp  2se 1.93  SIGNIFICANT
S1_focus − S1  +4.13pp  2se 3.05  SIGNIFICANT
```

## 3. 판정

1. **의무 분해(FOCUS, T3)가 이 fixture에서 작동하는 연역 원리입니다.**
   5시드 +6.1pp / 15시드 +5.3pp 유의, 천장의 **98.8%**, 노드는 오히려 54%
   (3514 vs 6474) — 효율 이득입니다.
   단항 d4/b4에서 공허였던(0 제거) 그部件이 관계형에서는 상태당 평균 ~16개 후보를
   제거합니다(49,745 상태에서 807,491 제거). 설계 교차표의 예측대로입니다.
2. **타입 어텐션(S1)과 의무 readout(S2)은 null입니다** (15시드 S1−S0 −0.27pp ns;
   5시드 +1.8pp 점추정은 노이즈였습니다). 엔티티 수치 특징(S0e)도 0.0pp — 바인딩 identity를
   특징으로 주는 것만으로는 부족하고, 토큰화도 이 규모에서는 유의한 이득을 내지 못합니다.
   사실 내용 셔플(S1shuf) 대비 +1.2pp ns — 사실 토큰 내용의 기여도 미확정.
3. S1_focus ≈ S0_focus (0.8033 vs 0.8050) — 포커스 위에 타입 토큰을 얹어도 추가 이득 없음.
4. greedy/beam이 DFS보다 훨씬 낮습니다(0.24/0.35 vs 0.74) — 이 fixture는 탐색 의존도가
   높고, 포커스는 greedy도 0.24→0.42로 올립니다. 후보 가지치기가 순위보다 먼저 작동합니다.

**해석**: 바인딩 정보가 부족해서가 아니라(앨리어스 40%), 그 정보를 활용하는 방식이
순위 학습(T2)보다 **의무 directed 가지치기(T3)**라는 것입니다. Rocq의 전술 분해에
해당하는 원리가 이득을 냈고, 어텐션 점수 구조 변경은 내지 못했습니다.

## 3b. 15시드 확인 (71–85, run_confirm0270.sh)

```text
평균: S0 0.7554  S0e 0.7372  S1 0.7526  S1shuf 0.7433
      S0_focus 0.8083  S1_focus 0.8077

S1 − S0          −0.27pp  2se 3.38  ns   ← 타입 어텐션 null 확정
S0e − S0         −1.82pp  2se 3.43  ns   ← 엔티티 수치 특징 null
S1 − S1shuf      +0.94pp  2se 2.98  ns   ← 사실 내용 기여 미확정
S0_focus − S0    +5.29pp  2se 2.01  SIGNIFICANT
S1_focus − S1    +5.51pp  2se 2.04  SIGNIFICANT
S1_focus − S0_focus −0.06pp 2se 0.34 ns   ← 포커스 위 타입 토큰 무가치
```

5시드의 S1 양의 점추정(+1.8pp)은 노이즈였습니다. 15시드에서 S1−S0은 −0.27pp로
**타입 어텐션/엔티티 임베딩/의무 readout은 이 규모에서 null**입니다. 포커스 이득은
+5.3pp로 견고하며, S0_focus 0.8083은 천장 0.8182의 **98.8%**입니다.

## 3c. assert 발명 (Rocq assert/cut, T7) — 커널 채택/거부율

설계: 제안 헤드(state token LN → 36 atom logits)가 중간 원자(보조정리)를 제안하면
**커널이 채택을 결정**합니다: 미지 ∧ 목표관련(역방향 도달) ∧ 전체 live후보 폐포 도달
∧ AND-OR 깊이 하한 ≤ 잔여예산. 모델은 제안만, 판정은 커널만. BCE 보조손실(ASSERTW 0.5)로
채택 타깃을 학습하고, 추론에서는 채택된 제안을 서브골로 하는 역방향 포커스를 적용합니다
(Rocq: 보조정리를 먼저 증명). 통제: 무훈련 헤드(ASSERTW 0, 메커니즘 분리),
소프트 변형(제안 ∪ 목표 포커스, ASSERTUNION).

```text
학습 곡선(커널 판정 top-1 채택률): 0.168 → 0.308 → 0.556 → 0.600 → 0.647 (epoch 0–39)
기회수준 ~0.07. 체크포인트(val top1 선택)의 채택률 0.264, 평가 런 무조건 top-1 채택률 3–4%
— 다중과제 체크포인트 긴장: 후보 순위가 제안 품질보다 먼저 선택됩니다.

arm               dfs      nodes    15시드 평균
S1_assert         0.6413   2207     0.6512   (하드 서브골 포커스)
S1_assert_rand    0.6529   1782     0.6573   (무훈련 헤드)
S1_assert_union   0.8099   3278     0.8099   (제안 ∪ 목표)
S1_focus          0.8033   3659     0.8077

15시드 대조:
S1_assert − S1_focus       −15.65pp  2se 3.00  SIGNIFICANT (훼손)
S1_assert − S1_assert_rand  −0.61pp  2se 2.97  ns (제안 학습 무관)
S1_assert_union − S1_focus  +0.22pp  2se 0.34  ns (소프트 힌트 무가치)
S1_assert_union − S1        +5.73pp  2se 1.91  SIGNIFICANT (포커스 자체의 이득)
```

판정:
1. **커널 채택 신호는 학습 가능**합니다(채택률 17%→65%, 기회수준 7%). 거부율 지표가
   학습 방향을 정직하게 보여줍니다.
2. **하드 단일 서브골 분해는 정책을 훼손**합니다(−15.7pp). 제안이 최적 경로 위에 있다는
   보장이 없고, 틀린 보조정리로의 하드 포커스는 최적 행동을 잘라냅니다. 학습된 제안과
   무작위 제안의 차이가 없으므로 문제는 제안 품질이 아니라 메커니즘입니다.
3. **소프트 힌트(∪ 목표)는 무가치**(+0.22pp ns; 5시드 +0.66pp 경계선은 15시드에서 소멸).
4. 작동하는 원리는 여전히 의무 포커스(T3) 단독입니다. assert 발명은 이 fixture에서
   학습 가능한 신호이지만 정책 이득으로 전이되지 않습니다 — Rocq assert가 성립하려면
   보조정리가 실제 증명 경로 위에 있어야 하며, 모델은 그 위치를 신뢰성 있게 찾지 못합니다.

## 4. 정직한 경계

- 매트릭스 게이트는 5시드, 주장 확인은 15시드(run_confirm0270.sh, out/confirm0270.txt, 9 arm).
- assert 평가 채택률(3–4%)은 체크포인트 선택(val top1)의 다중과제 긴장을 반영합니다;
  최종 epoch 가중치의 채택률(65%)과 다릅니다. 둘 다 보고합니다.
- 계약 없음 — 계약+포커스 결합은 후속 측정 대상입니다.
- 훈련 depth 2 / 평가 depth 4 프로토콜: 앨리어스 분포가 다릅니다(6.7% vs 40%).
- RELATOM은 CERT/BINDTOK/LIFTED/INTEGRAL/SYMGATE와 동시 사용 불가(후속 포팅),
  Maru Q16 export는 관계형에서 명시 거부(단항 base에서 parity 게이트 수행).
- TYPED는 EPTRAIN 필수, LOOPCELL과 상호배제(0269: 마르코프 충분 상태 재귀 null).

## 5. 게이트 (`verify_rel0270.sh` → `V0270-RELATIONAL-PASS`)

```text
REL-GRADCHECK   5빌드 전 파라미터 + TYPED-GRAD 생생성
PARITY-REL      독립 오라클: 규칙/특징/utility/witness/DP 라벨
ALIAS           판별력: depth-4 top-mixed 앨리어스 > 0
PERM            후보 + 사실 토큰 순서 등변
LABEL-INDEPENDENT  b4/b6 pchk 동일 (타입 arm)
HEADER          typed/oblread/entfeat/typedshuf cross-load 거부
CONTRASTS       대조 보고 (방향은 발견이지 게이트 요구사항 아님)
CEILING         시드별 무계약 완전탐색, 전 arm 상한 검사
FOCUS           제거 카운트 보고 (비공허 확인)
ASSERT-LEARN    커널 판정 채택률 학습 곡선 (0.168 → 0.647)
ASSERT-GRAD     제안 헤드 생생성 (훈련 nonzero, 무훈련 0)
AGG/LLVM/UNARY  표 재계산 + 변이 10건, O0/O2/O3 + ASan(S2), 단항 gradcheck 회귀
CONFIRM-TABLE   15시드 확인 표 == 시드별 재계산
V0270-RELATIONAL-PASS
```

## 6. 재현

```bash
cd experiments/proof_state_transformer_maru
bash run_rel0270.sh        # 10-arm 매트릭스 + 천장
bash run_confirm0270.sh    # 15시드 확인 (9 arm)
bash verify_rel0270.sh     # 게이트
python3 tools/check_parity_rel.py --rules out/rel_rules.txt \
  --worlds out/rel_worlds_gate.txt --dp out/rel_dp_gate.txt
```