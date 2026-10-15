# Abstraction-level comparison — DLM v0.0041 vs a human reading `main.py`

> **v0.0042 status update.** This document defined the ladder and measured
> v0.0041 at L3–L4. v0.0042 now implements **L5–L9** (`dlm/compose.py`,
> `experiments/abstraction/`): L5 composition (`calls(X,Y),calls(Y,Z)`), L6
> architecture (role motifs, transfers + discriminates a new shape), L7 intent
> (hypotheses, never certified), L8 causal (certified from acquired API facts),
> L9 transfer. The `abstraction_score` is now reported. The ladder below is the
> measuring stick; the “what we don’t have yet” column reflects v0.0041 at the
> time of writing and is kept for the audit trail.

> **결론 먼저.** DLM이 내놓는 것은 **평면적 관계 이해(L3–L4)** 다. 같은 파일을
> 읽은 사람은 **계층적·의도적·인과적 이해(L6–L9)** 를 만든다. 추상화 축에서
> DLM은 시작 단계다 — 사용자 평가가 맞다. DLM이 사람에게 없는 것은 **건전성**이다:
> 모든 문장이 커널에 의해 entail되고, 지지가 없으면 abstain한다. 과제는 이 차이를
> 부정하는 것이 아니라 정확히 이름 붙이고 올라가는 것이다.

---

## 1. 사람(또는 LLM) 기준선 — 이 파일을 읽고 하는 말

아래는 `main.py`를 읽은 유능한 독자가 실제로 만들어내는 이해다. 층위(L*)는 §4의
사다리를 따른다.

**목적·의도 (L7)** — *코드 텍스트에 직접 없음, 맥락에서 추론*
> 이것은 MNIST 손글씨 숫자를 분류하는 작은 CNN의 **완전한 학습 스크립트**이자
> **참조 구현(reference example)** 이다. 14 epoch 동안 Adadelta로 학습하고, 매
> epoch마다 테스트 정확도를 재고, 학습률을 0.7배씩 감쇠하며, 선택적으로 모델을
> 저장한다. 목적은 **일반화 성능을 측정**하는 것(테스트 정확도)이다.

**구조·계층 (L5)** — *함수 호출 구조 + 데이터 흐름*
> 4개의 최상위 단위: `main`(설정+오케스트레이션) → epoch 루프 `{train; test;
> scheduler.step}`; `train`(한 epoch의 SGD); `test`(평가); `Net`(모델).
> `train`은 main이 epoch마다 부르는 **하나의 추상 작업("한 epoch 학습")** 이고,
> 그 안은 **SGD 한 스텝**의 정형 순서다.

**알고리즘·아키텍처 (L6)** — *관계를 넘어서는 패턴*
> `Net`은 소형 VGG류 CNN이다: `[conv→relu]×2 → maxpool → dropout → flatten →
> [fc→relu→dropout] → fc → log_softmax`. 즉 **conv 블록 2개 + 분류기 헤드**.
> 채널: conv1 1→32(k3), conv2 32→64(k3), fc1 9216→128, fc2 128→10.
> `log_softmax + nll_loss = cross-entropy`(수치 안정형). 정규화 (0.1307, 0.3081)은
> **MNIST 데이터셋의 평균/표준편차**다.

**인과·이유 (L8)** — *"왜"*
> `zero_grad()`인 이유: PyTorch는 gradient를 누적하므로 스텝 전에 비워야 한다.
> `model.train()/eval()`인 이유: dropout(BatchNorm)의 동작을 토글한다.
> `no_grad()`인 이유: 추론 시 그래프를 만들지 않아 메모리/연산을 아낀다.
> `StepLR(step_size=1, gamma=0.7)`인 이유: epoch마다 LR을 지수 감쇠.
> `--dry-run`인 이유: 한 배치만 돌리는 스모크 테스트(`if args.dry_run: break`).

**전이·유추 (L9)** — *다른 코드로 옮기기*
> "이건 PyTorch의 표준 MNIST CNN 예제다. CIFAR 예제와 같은 골격이고, 데이터셋만
> 바꾸면 재사용된다. `test()`는 정확도 계산을 포함한다: `pred.eq(target).sum()/
> dataset`." → 새 데이터·새 태스크로 **적응/수정** 가능.

---

## 2. DLM v0.0041 기준선 — 실제로 내놓는 것

출처: `reports/mnist/20261015-101113/result.json`(32문장), `reports/generalize/*`(8개념).

- **관계 어휘 8개**: `imports, defines, method_of, inherits, creates, calls,
  step_of, before`. 모두 **엔티티 간 평면 관계**.
- **문장 6종**: import / is-a(`is_module`) / has-a(`has_layer`) / 행위 플래그
  (`trains, optimizes, …`) / 근접 도달(`calls+`) / 순서 파이프라인(`before` 목록).
- **개념 8개**: 전부 **한 subject의 특징 원자 2–3개의 논리곱**
  (`backpropagates(X) ∧ optimizes(X)` 등). 즉 **명제적(propositional) 결합**이지,
  구조 위의 규칙이 아니다.

핵심 관찰:
1. `trains`라는 **의미 이름**은 손으로 준 **다리(BRIDGE_FORMS)** 에서 온다. 개념
   `concept0 = backpropagates ∧ optimizes`는 이미 다리로 만든 두 사실의 **논리곱**이다.
2. DLM은 `training_step`을 **코드 구조**(`zero_grad→forward→loss→backward→step`)에서
   유도하지 않는다. 그 구조는 `before` 파이프라인 문장 하나(평면 순서 목록)로만 나온다.
3. `test()`의 **정확도 계산**(`pred.eq(target).sum()/dataset`)이나 채널/shape
   데이터플로는 **전혀 표현되지 않는다**.
4. 전이(`transfer`)는 "같은 특징 조합이 다른 프로그램 subject에서도 성립"을
   증명할 뿐, **다른 코드 모양으로의 유추**가 아니다.

---

## 3. 나란히 비교

| 물음 | 사람 (L6–L9) | DLM v0.0041 | 격차 |
|---|---|---|---|
| 이건 뭐야? | "MNIST 분류 CNN 학습 스크립트" | "main이 train/test를 부르고 torch를 import" | **의도 없음** |
| train()은? | "한 epoch SGD" | "main이 train을 호출, 순서 나열" | **합성 없음** |
| Net은? | "conv×2 + 분류기, cross-entropy" | "conv2d/linear/dropout 레이어를 가짐" | **토폴로지·의미 없음** |
| 왜 zero_grad? | "gradient 누적 방지" | (없음) | **인과 없음** |
| 정확도는? | "correct/total 계산" | (없음) | **값·산술 없음** |
| 다른 데 쓸 수 있나? | "CIFAR로 바꿀 수 있음" | (없음) | **유추 없음** |
| 이 문장 믿을 수 있나? | 사람 판단(검증 안 됨) | **커널 증명됨 + abstain** | ← DLM 우위 |

---

## 4. 추상화 사다리와 현재 위치

```
L0 바이트          │
L1 구문 (AST)      │  extract.py
L2 관계 사실       │  imports/calls/defines/before ...        ← DLM 감소
L3 엔티티 의미     │  is_module/has_layer (웹 획득)           ← v0.0040  ✅
L4 국소 관용구     │  backpropagates ∧ optimizes = "step"     ← v0.0041  ◑ (명제적)
L5 합성·계층       │  "SGD 스텝" = 순서 있는 부분그래프, epoch 루프  ← 없음 ❌
L6 알고리즘·구조   │  CNN = conv블록+헤드, cross-entropy          ← 없음 ❌
L7 목적·의도       │  "숫자 분류 참조 구현"                      ← 없음 ❌
L8 인과·전제조건   │  "누적 방지 → zero_grad"                    ← 없음 ❌
L9 전이·유추       │  "CIFAR 골격과 동형"                        ← 없음 ❌
```

**측정된 위치: L3 확고, L4 부분적(그것도 명제적 수준). L5 이상 전무.**
따라서 "매우 초기 단계"라는 평가는 추상화 축에서 **정확하다**.

---

## 5. 과소평가하지 말 것 — 실제로 있는 것

- **건전성 보장**: 32문장 전부 커널 closure에 entail됨(`all_sentences_verified`),
  87쌍 `calls` closure에 대해 `false_final=0`. LLM/사람은 더 풍부하지만 **환각
  위험**이 있고 검증되지 않는다. DLM은 "얕지만 틀리지 않는다".
- **abstain**: 지지가 없으면 문장을 **내지 않는다**. 의미를 지어내지 않는다.
- **전이의 실재**: `concept0`는 학습에 안 쓴 `main.py`의 `main`·`train`에서 커널이
  **재도출**했고, `p11`(conv만)은 `conv2d∧linear` 개념을 **거부**했다. 이건
  장식이 아니라 반증 가능한 주장이다.
- **획득 vs 부여의 분리**: 의미는 웹에서 `meaning(symbol,concept)` 사실로 들어온다.

즉 관계는 "사람 = 깊지만 미검증", "DLM = 얕지만 검증됨"의 **상보**다.

---

## 6. 격차 목록과 구체적 다음 단계

가장 중요한 **구조적 결함**부터:

1. **L5 — 합성 개념 (최우선).** 지금 `dlm/generalize.py`는 *특징 논리곱*만 만든다.
   다음은 **관계 구조 위의 패턴**을 코퍼스에서 채굴해야 한다:
   `training_step(T) :- step_of(T,g0), calls(T,m), calls(T,b), step_of(T,s), before(g0,b)…`.
   `dlm/abstract.abstract_theory`가 이미 *규칙 몸체*를 접는다 — 코퍼스가 규칙 몸체를
   공유하게 만들면(여러 프로그램의 `train`을 같은 구조로 감소) 여기서 발화한다.
   검증은 `closure_preserved` + 홀드아웃 전이.
2. **L6 — 데이터플로·아키텍처.** `forward`를 **shape 붙은 데이터플로 그래프**로
   감소시키고, 서브그래프 패턴("conv 블록", "분류 헤드", "log_softmax+nll=cross-entropy")을
   그래프 마이닝으로 발굴·커널 검증.
3. **L7 — 의도.** 의도는 closure에 **없다**. 정직한 답: docstring/README/웹에서
   **획득**하고(`meaning`처럼) **가설로만** 진술한다. "의도 문장"은 절대 certify하지
   않는다 — 신뢰 경계 유지.
4. **L8 — 인과·전제조건.** API 전제(`zero_grad`는 `backward` 전에 필요, 추론엔
   `eval/no_grad`)를 **사실로 획득**하면 `requires` 규칙이 "왜" 문장을 도출할 수 있다.
   이것도 커널 검증 가능.
5. **L9 — 유추·전이.** 코퍼스/교차 저장소 전이를 구조적 유추(LGG/`galois`)로 확장.

그리고 메타 결함:

6. **평가 지표 부재.** 현재 verdict는 **건전성**(false_final=0, verified)만 검사하고
   **이해의 풍부함**은 측정하지 않는다. `main.py`에 대해 사람이 기대하는 추상화
   체크리스트(관용구/아키텍처/의도/인과)를 만들고, 시스템이 **지지와 함께** 산출하는
   비율을 `abstraction_score`로 보고해야 "초기 단계"가 **수치로** 보인다.
   지금의 PASS는 깊이가 아니라 건전성의 PASS다.

---

## 7. 정직한 메모

DLM은 "증명 가능한 최소 핵"으로는 이미 성립한다. 그러나 **사람이 코드를 이해한다**는
것의 대부분(L5–L9)은 아직 없다. v0.0041은 그 첫 칸(L4)을, 그것도 명제적 논리곱으로
채웠을 뿐이다. 다음 버전은 **합성(L5)** 부터 시작하는 것이 옳다 — 그것이 나머지
층위의 토대이기 때문이다.