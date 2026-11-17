/* ---------------- stage 3: data, training, evaluation, policies ---------------- */
#ifndef MAXBUDGET
#define MAXBUDGET 6
#endif
#define NW_TRAIN 180
#define NW_VAL 40
#define NW_TEST 40
#define EPOCHS 40
#define BATCH 32

#define W_MAGIC 0x444C4D5730323532ULL
typedef struct {
  uint64_t magic;
  int state_dim, cand_dim, variant, hard, relob, bindtok, goaldepth, eval_budget;
  int integral, lifted, prior_shuf, holdout;
  int attmode, symgate, cert, focus, lemma;   /* 0260 hybrid-layer tag */
  int pairmode, pair_keep;                   /* 0261 contract proposer */
  int valmode;                               /* 0262 value label */
  int label_ncost, label_steps, label_rem;   /* 0268 label definition */
  int branchtok, readmax, regshuf;           /* 0263 multi-register structure */
  int md, mnl, phaseuntie;                   /* 0264 capacity */
  int loopcell, celldetach, cellshuf, remfeat, eptrain;  /* 0269 loop cell */
  int relatom;                                           /* 0270 relational fixture */
  int typed, oblread;                                    /* 0270 S1/S2 */
  int entfeat, typedshuf;                                /* 0270 controls */
  int assertf;                                           /* 0270 assert invention */
  int assertunion;
  double lift_rho, path_gamma;
  double predw;                              /* 0269 world-model auxiliary weight */
  double assertw;                            /* 0270 assert auxiliary weight */
  double pchk;
} WHeader;

typedef struct {
  int nlive;
  int live[POOL];
  double state[STATE_DIM];
  double cf[POOL][CAND_DIM];
  double util[POOL];
  int best;
  int reward_pos;      /* best utility > 0 (goal reward present) */
#if TYPED
  int fatoms[NA], nfact;          /* known atoms at this state (fact tokens) */
  int oatoms[GOAL_COUNT], nobl;   /* unproved goals (obligation tokens) */
#endif
} RStep;

typedef struct {
  World w;
  int nsteps;
  RStep st[NSTEPS];
} WSteps;

#if ASSERT
static long g_assert_states = 0, g_assert_adopt = 0, g_assert_fallback = 0;
static long g_assert_raw_adopt = 0;   /* unconditional top-1 proposal accepted by kernel */
#endif
#if ASSERT
static void assert_report(const Params *p, int split, const char *tag);
#endif
static int g_collect = 0;       /* 0 = stop when best utility <= 0 (0245), 1 = full budget */
static int g_sample = 0;        /* 0 = all collected states, 1 = root only, 2 = root + subsample */
static int g_balance = 0;       /* 1 = reward-bearing states first, then fill to the same count */
static int g_regret = 0;
static int g_dfs = 0;        /* 1 = native DFS search metrics */
static int g_onecommit_audit = 0;  /* 1 = scan test split for single-commit multi-goal proofs */
static long g_ds_worlds[3], g_ds_steps[3], g_ds_hist[3][NSTEPS+1], g_ds_reward[3], g_ds_labels[3];

static WSteps *g_data[3];
static int g_nw[3] = {NW_TRAIN, NW_VAL, NW_TEST};
static int g_beam = 3;                 /* beam width for the beam policy */
static int g_branch = 3;               /* children kept per node in the DFS search */
static int g_subsume = 1;              /* state-subsumption pruning (Silicon port) */
static int g_prop = 1;                 /* admissible propagation (Screamer port) */
static int g_focus = FOCUS;            /* 1 = obligation-directed candidate focus (Rocq tactic) */
static int g_lemmas = LEMMA;           /* 1 = verified 2-rule lemma (contract) actions */
static int g_lemma_max = 64;
static int g_lemma_cost = 1;           /* action slots charged for a lemma (contract use) */
typedef struct { int r1, r2; int body; int uses; } Lemma;  /* pre: body atom holds at an entity */
static Lemma g_lem[128];
static int g_nlem = 0;
/* 0.0261: how the contract set is proposed.
 *   PAIRMODE 1 = mined from teacher rollouts (0.0257/0.0260, hand-designed)
 *   PAIRMODE 2 = learned pair scorer over the world's own candidate rules
 *   PAIRMODE 3 = random structurally-valid pairs (matched-count control) */
static int g_pairmode = PAIRMODE;
static int g_pair_keep = 16;           /* contracts offered per state */
static int g_pair_uses = 0, g_pair_viol = 0;   /* applied / kernel-mismatch */
#define PAIRF 8
static double g_pairw[PAIRF];
static int g_pair_learned = 0;
static int g_valmode = VALMODE;   /* 0 utility, 1 DP value, 2 shuffled DP (control) */
/* g_label_rem_max moved to pst.c (0.0269: the stage-1 rollout needs it too) */
static long g_dp_store_fail = 0, g_dp_states = 0, g_dp_masks = 0, g_onpath_cands = 0, g_onpath_states = 0, g_onpath_distinct = 0;
static long g_lab_states[3], g_lab_top[3], g_lab_nlive[3];
static int g_lab_split = 0;
static int g_cert_on = CERT;           /* independent certificate check on the DFS proof */
static int g_cert_selftest = 0;        /* 1 = corrupt one parent (checker must fail) */
static long g_dfs_nodes = 0, g_dfs_cands = 0, g_dfs_leafs = 0, g_dfs_pruned = 0;
static long g_nsteps[3];

static void pc_filter(const uint8_t *known, int *live, int *nlive);
static int focus_filter(const World *w, const uint8_t *known, int *live, int nlive);
static void lemma_mine(void);
static void pair_learn(void);

/* ---- 0.0262 budget-exact DP value labels ----------------------------------
 * The single-step utility target cannot express "this rule enables the next
 * step". The DP label is the exact value of committing a candidate and then
 * playing optimally within the REMAINING budget:
 *
 *   P(mask)      = goals proved by closure(theory + mask)
 *   V(mask, rem) = max(P(mask), max_{c not in mask} V(mask | 1<<c, rem-1))
 *   label(c)     = V(mask | 1<<c, rem-1)
 *
 * The recursion is memoised over (mask, rem); the state space is every candidate
 * subset reachable within the remaining budget (C(22,<=4) = 9109 at the root), and
 * every leaf is a kernel closure. This is an oracle label, not a rollout label:
 * verify_value.sh compares it against an independent brute-force enumeration.
 * VALMODE=2 keeps the same label multiset with the correspondence to candidates
 * destroyed, so any gain from VALMODE=1 can be attributed to the labels. */
#define DPMEMO (1<<20)    /* 0.0267: C(22,<=6)=110,056 keys; 32k overflowed at eval budget 6 */
#define DPPROBE 256
typedef struct { uint32_t mask; int8_t rem; int8_t used; int val; int8_t steps; } DpCell;
static DpCell g_dp[DPMEMO];

static int proved_mask(const World *w, uint32_t mask){
  int rules[MAXRULE];
  int n = SEED_RULES;
  for (int k = 0; k < SEED_RULES; k++) rules[k] = w->theory[k];
  for (int c = 0; c < POOL; c++)
    if (mask & (1u << c)){ if (n < MAXRULE) rules[n++] = w->cands[c]; }
  uint8_t known[WENT];
  closure(w->facts, rules, n, known);
  int gp = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (GOAL_KNOWN(w,g,known)) gp++;
  return gp;
}

static uint32_t dp_hash(uint32_t mask, int rem){
  uint64_t h = (uint64_t)mask*0x9E3779B97F4A7C15ULL ^ (uint64_t)(rem+1)*0xBF58476D1CE4E5B9ULL;
  return (uint32_t)(h >> 40) & (DPMEMO-1);
}

static int dp_value(const World *w, uint32_t mask, int rem);
static int dp_value_s(const World *w, uint32_t mask, int rem);  /* returns steps via *out */

static int dp_lookup(uint32_t mask, int rem, int *val, int *steps){
  uint32_t h = dp_hash(mask, rem);
  for (int i = 0; i < DPPROBE; i++){
    DpCell *e = &g_dp[(h+i) & (DPMEMO-1)];
    if (!e->used) return 0;
    if (e->mask == mask && e->rem == rem){ *val = e->val; if (steps) *steps = e->steps; return 1; }
  }
  return 0;
}
static void dp_store(uint32_t mask, int rem, int val){
  /* steps are stored by dp_store2 below when needed */
  uint32_t h = dp_hash(mask, rem);
  for (int i = 0; i < DPPROBE; i++){
    DpCell *e = &g_dp[(h+i) & (DPMEMO-1)];
    if (!e->used || (e->mask == mask && e->rem == rem)){
      e->used = 1; e->mask = mask; e->rem = (int8_t)rem; e->val = val; return;
    }
  }
  g_dp_store_fail++;   /* table full: the recursion would recompute exponentially */
}

static int dp_value(const World *w, uint32_t mask, int rem){
  int memo;
  if (dp_lookup(mask, rem, &memo, 0)) return memo;
  g_dp_masks++;
  int best = proved_mask(w, mask);
  if (rem > 0){
    for (int c = 0; c < POOL; c++){
      if (mask & (1u << c)) continue;
      int v = dp_value(w, mask | (1u << c), rem-1);
      if (v > best) best = v;
    }
  }
  dp_store(mask, rem, best);
  return best;
}

/* value with a proof-cost tie-break (0.0265): the same recursion, but the memo
 * also carries the MINIMUM number of commits needed to reach that value, so two
 * candidates with equal value are ordered by the length of the derivation they
 * lead to (MDL / justification signal). */
static int dp2[STATE_DIM];   /* scratch unused */
static int dp_value_sx(const World *w, uint32_t mask, int rem, int *steps){
  int memo, ms;
  if (dp_lookup(mask, rem, &memo, &ms)){ if (steps) *steps = ms; return memo; }
  g_dp_masks++;
  int best = proved_mask(w, mask), bstep = 0;
  if (rem > 0){
    for (int c = 0; c < POOL; c++){
      if (mask & (1u << c)) continue;
      int s2 = 0;
      int v = dp_value_sx(w, mask | (1u << c), rem-1, &s2);
      int step = s2 + 1;
      if (v > best || (v == best && (bstep == 0 || step < bstep))){ best = v; bstep = step; }
    }
  }
  /* store both fields */
  uint32_t h = dp_hash(mask, rem);
  for (int i = 0; i < DPPROBE; i++){
    DpCell *e = &g_dp[(h+i) & (DPMEMO-1)];
    if (!e->used || (e->mask == mask && e->rem == rem)){
      e->used = 1; e->mask = mask; e->rem = (int8_t)rem; e->val = best; e->steps = (int8_t)bstep; break;
    }
  }
  if (steps) *steps = bstep;
  return best;
}

/* independent brute force (no memo, no recursion sharing) for the gate */
static int dp_bruteforce(const World *w, uint32_t mask, int rem){
  int best = proved_mask(w, mask);
  if (rem <= 0) return best;
  for (int c = 0; c < POOL; c++){
    if (mask & (1u << c)) continue;
    int v = dp_bruteforce(w, mask | (1u << c), rem-1);
    if (v > best) best = v;
  }
  return best;
}

/* candidate-mask of the committed rules at this state */
static uint32_t committed_mask(const World *w, const int *live, int nlive,
                               const int *rules, int nrules){
  uint32_t mask = 0;
  (void)live; (void)nlive;
  for (int k = 0; k < nrules; k++)
    for (int c = 0; c < POOL; c++)
      if (w->cands[c] == rules[k]) mask |= (1u << c);
  return mask;
}

static void dp_labels(const World *w, const int *rules, int nrules, const int *live,
                      int nlive, int rem, double *util){
  uint32_t mask = committed_mask(w, live, nlive, rules, nrules);
  memset(g_dp, 0, sizeof g_dp);
  g_dp_states++;
  int vals[POOL];
  /* NOTE (review N1/N2): compute the value WITH its derivation length from one
   * call. Mixing dp_value() and dp_value_sx() on the same memo cell returned
   * steps=0 for every candidate, which silently made the steps term constant and
   * reduced the 0.0265 label to "exact value, cost term dropped". */
  for (int k = 0; k < nlive; k++){
    uint32_t bit = 0;
    for (int c = 0; c < POOL; c++) if (w->cands[c] == live[k]) bit = (1u << c);
    int s2 = 0;
    vals[k] = dp_value_sx(w, mask | bit, rem > 0 ? rem-1 : 0, &s2);
    util[k] = 5.0*(double)vals[k]/(double)(w->ngoals > 0 ? w->ngoals : 1)
              - rule_cost(&all_rules[live[k]]);
  }
  if (g_valmode >= 1){
    /* label = value term (+ optional derivation-length term, + optional cost),
     * 2x2 decomposition of the 0.0265 label (review N2). */
    int st[POOL];
    for (int k = 0; k < nlive; k++){
      uint32_t bit = 0;
      for (int c = 0; c < POOL; c++) if (w->cands[c] == live[k]) bit = (1u << c);
      int s2 = 0;
      dp_value_sx(w, mask | bit, rem > 0 ? rem-1 : 0, &s2);   /* memo hit: steps */
      st[k] = s2;
    }
    for (int k = 0; k < nlive; k++){
      double u = 5.0*(double)vals[k]/(double)(w->ngoals > 0 ? w->ngoals : 1);
      if (LABEL_STEPS || g_valmode >= 3)
        u += 0.5*(1.0 - (double)st[k]/(double)(g_eval_budget > 0 ? g_eval_budget : 1));
      if (!(LABEL_NCOST || g_valmode >= 3)) u -= rule_cost(&all_rules[live[k]]);
      util[k] = u;
    }
    /* census of the label actually used for training (review N1): how many
     * candidates share the TOP label, per state and split */
    double mxu = -1e30;
    for (int k = 0; k < nlive; k++) if (util[k] > mxu) mxu = util[k];
    int non = 0;
    for (int k = 0; k < nlive; k++) if (util[k] >= mxu - 1e-9) non++;
    g_lab_states[g_lab_split]++; g_lab_top[g_lab_split] += non;
    g_lab_nlive[g_lab_split] += nlive;
  }
  if (g_valmode == 2 || g_valmode == 4){   /* control: same multiset, shuffled */
    for (int k = nlive-1; k > 0; k--){
      int j = (int)randbelow((uint64_t)k+1);
      double t = util[k]; util[k] = util[j]; util[j] = t;
    }
  }
}


/* DP vs independent brute force (gate helper). Runs on the first few train
 * states at remaining budgets 1..3, where brute force is affordable. */
static void dp_audit(void){
  long checks = 0, bad = 0;
  for (int i = 0; i < g_nw[0] && i < 4; i++){
    const World *w = &g_data[0][i].w;
    for (int st = 0; st < g_data[0][i].nsteps && st < 2; st++){
      const RStep *rs = &g_data[0][i].st[st];
      int rules[MAXRULE];
      int nrules = SEED_RULES;
      for (int k = 0; k < SEED_RULES; k++) rules[k] = w->theory[k];
      for (int q = 0; q < st; q++) rules[nrules++] = g_data[0][i].st[q].live[g_data[0][i].st[q].best];
      uint32_t mask = committed_mask(w, rs->live, rs->nlive, rules, nrules);
      for (int rem = 1; rem <= 3; rem++){
        memset(g_dp, 0, sizeof g_dp);
        int a = dp_value(w, mask, rem);
        int b = dp_bruteforce(w, mask, rem);
        checks++;
        if (a != b) bad++;
        printf("DP-AUDIT world=%d state=%d rem=%d memo=%d brute=%d %s\n",
               i, st, rem, a, b, a == b ? "ok" : "MISMATCH");
      }
    }
  }
  printf("DP-AUDIT-SUMMARY checks=%ld mismatches=%ld\n", checks, bad);
}

static void build_dataset(void){
  for (int s = 0; s < 3; s++){
    g_lab_split = s;
    g_data[s] = (WSteps*)calloc((size_t)g_nw[s], sizeof(WSteps));
    if (!g_data[s]){ fprintf(stderr, "alloc\n"); exit(2); }
    rng_state = (uint64_t)(11 + s);
    for (int i = 0; i < g_nw[s]; i++){
      WSteps *ws = &g_data[s][i];
      int ok = 0;
      if (g_goal_scan){
        static int src[3] = {0,0,0};
        int guard = 0;
        while (!ok && guard++ < 20000){ ok = make_world(&ws->w, s, src[s]++) && holdout_ok(&ws->w, s); }
        if (!ok){ fprintf(stderr, "SCAN-FAIL split=%d world=%d depth=%d\n", s, i, g_goaldepth); exit(3); }
      } else {
        while (!ok) ok = make_world(&ws->w, s, i);
      }
      int rules[MAXRULE];
      int nrules = SEED_RULES;
      for (int k = 0; k < SEED_RULES; k++) rules[k] = ws->w.theory[k];
      int used[POOL] = {0};
      int ns = 0;
      for (int st = 0; st < NSTEPS; st++){
        int live[POOL], nlive = 0;
        for (int c = 0; c < POOL; c++){
          int r = ws->w.cands[c], u = 0;
          for (int k = 0; k < nrules; k++) if (rules[k] == r) u = 1;
          if (!u) live[nlive++] = r;
        }
        if (!nlive) break;
        RStep *rs = &ws->st[ns++];
        rs->nlive = nlive;
        for (int k = 0; k < nlive; k++) rs->live[k] = live[k];
        state_features(&ws->w, rules, nrules, live, nlive, rs->state,
                       g_label_rem_max - st > 0 ? g_label_rem_max - st : 0);
#if TYPED
        {
          uint8_t kn[WENT];
          closure(ws->w.facts, rules, nrules, kn);
          rs->nfact = atoms_from_known(kn, rs->fatoms);
          rs->nobl = obligs_from_goals(&ws->w, kn, rs->oatoms);
        }
#endif
        int best = 0;
        for (int k = 0; k < nlive; k++){
          cand_features(&ws->w, rules, nrules, live[k], rs->cf[k]);
          rs->util[k] = utility(&ws->w, rules, nrules, live[k]);
          if (rs->util[k] > rs->util[best]) best = k;
        }
        if (g_valmode != 0){
          /* 0.0268 (review F1): the label budget is a function of the STEP only.
           * Using min(eval_budget - st, 4) still coupled the training labels to
           * the evaluation budget for every non-root state. */
          int rem = g_label_rem_max - st;
          if (rem < 0) rem = 0;
          dp_labels(&ws->w, rules, nrules, live, nlive, rem, rs->util);
        }
        for (int k = 0; k < nlive; k++)
          if (rs->util[k] > rs->util[best]) best = k;
        fill_path_features(&ws->w, rules, nrules, live, nlive, rs->cf);
        rs->best = best;
        rs->reward_pos = (rs->util[best] > 0) ? 1 : 0;
        (void)used;
        if (rs->util[best] <= 0 && !g_collect) break;
        if (rs->util[best] <= 0 && g_collect){
          /* full-budget collection: commit the best candidate anyway and keep
           * collecting states so the teacher exposes intermediate states */
          rules[nrules++] = live[best];
          continue;
        }
        rules[nrules++] = live[best];
      }
      ws->nsteps = ns;
      g_nsteps[s] += ns;
      g_ds_worlds[s]++;
      g_ds_steps[s] += ns;
      g_ds_hist[s][ns < NSTEPS ? ns : NSTEPS]++;
      for (int q = 0; q < ns; q++){
        if (ws->st[q].reward_pos) g_ds_reward[s]++;
        g_ds_labels[s] += ws->st[q].nlive;
      }
    }
  }
}

static void onpath_report(void){
  if (g_valmode == 0) return;
  printf("LABELMEMO cells=%ld store_fail=%ld probe=%d cap=%d label_rem_max=%d\n",
         g_dp_masks, g_dp_store_fail, DPPROBE, DPMEMO, g_label_rem_max);
  if (g_dp_store_fail) printf("LABELMEMO-WARN table overflow: labels stay correct but the DP recomputes without memo\n");
  /* one line per split: this is the label the weights are trained on (review N1) */
  for (int s = 0; s < 3; s++){
    if (!g_lab_states[s]) continue;
    const char *nm = (s == 0) ? "train" : (s == 1) ? "val" : "test";
    printf("LABELCENSUS valmode=%d labelset=%d split=%s states=%ld top_label_cands=%ld "
           "mean_top=%.2f mean_nlive=%.2f top_share=%.3f\n",
           g_valmode, VALMODE, nm, g_lab_states[s], g_lab_top[s],
           (double)g_lab_top[s]/(double)g_lab_states[s],
           (double)g_lab_nlive[s]/(double)g_lab_states[s],
           g_lab_nlive[s] ? (double)g_lab_top[s]/(double)g_lab_nlive[s] : 0.0);
  }
}
static void dataset_stats(void){
  for (int s = 0; s < 3; s++){
    const char *nm = (s == 0) ? "train" : (s == 1) ? "val" : "test";
    printf("DATASET fixture=%s collect=%s split=%d(%s) worlds=%ld steps=%ld hist1=%ld hist2=%ld hist3=%ld hist4=%ld label_reward_steps=%ld candidate_labels=%ld\n",
           (HARD_GOALS ? "hard" : "ref"), g_collect ? "full" : "rootstop", s, nm,
           g_ds_worlds[s], g_ds_steps[s], g_ds_hist[s][1], g_ds_hist[s][2],
           g_ds_hist[s][3], g_ds_hist[s][4], g_ds_reward[s], g_ds_labels[s]);
  }
}

/* per-step loss of a fixed candidate set (used by the gradient check) */
static double loss_eval(const Params *p, const double *state,
                        const double (*cf)[CAND_DIM], const double *util,
                        int best, int nlive){
  Cache *c = g_c;
  model_forward(p, state, cf, nlive, c);
  return loss_from_cache(c, util, best, nlive, (double*)0);
}

/* ---- 0.0269 episode-level training: BPTT through the loop cell ------------
 * One scalar per episode: sum of the per-step listwise+pairwise losses on the
 * kernel DP labels, plus PREDW * MSE of the next-state value predicted from
 * (z_t, emb(a_t)) alone. The trainer and the finite-difference checker share
 * episode_forward, so the checked scalar IS the trained scalar. */
#if EPTRAIN || LOOPCELL || TYPED
static Cache g_epc[NSTEPS];
static double g_epds[NSTEPS][POOL];
#if LOOPCELL
static CellCache g_epcell[NSTEPS];
static int g_epcsrc[NSTEPS];
static double g_epea[NSTEPS][D];
static double g_epth[NSTEPS][D], g_eppx[NSTEPS][2*D], g_eppred[NSTEPS];
static CellCache g_evalcell;
#endif

static double ep_maxutil(const RStep *rs){
  double mx = rs->util[0];
  for (int j = 1; j < rs->nlive; j++) if (rs->util[j] > mx) mx = rs->util[j];
  return mx;
}

static double episode_forward(const Params *p, const WSteps *ws, int grad){
  double z[D];
  for (int d = 0; d < D; d++) z[d] = p->z0[d];
  double total = 0;
  for (int t = 0; t < ws->nsteps; t++){
    const RStep *rs = &ws->st[t];
#if TYPED
    model_forward_typed(p, rs->state, rs->cf, rs->nlive, rs->live,
                        rs->fatoms, rs->nfact, rs->oatoms, rs->nobl, (const double*)0, &g_epc[t]);
#else
    model_forward_z(p, rs->state, rs->cf, rs->nlive, LOOPCELL ? z : (const double*)0, &g_epc[t]);
#endif
    total += loss_from_cache(&g_epc[t], rs->util, rs->best, rs->nlive, grad ? g_epds[t] : (double*)0);
#if ASSERT
    if (ASSERTW > 0){
      /* kernel adoption targets: the model proposes, the kernel decides */
      int rules[MAXRULE];
      int nr = 0;
      for (int q = 0; q < SEED_RULES; q++) rules[nr++] = ws->w.theory[q];
      for (int q = 0; q < t; q++) rules[nr++] = ws->st[q].live[ws->st[q].best];
      uint8_t kn[WENT];
      closure(ws->w.facts, rules, nr, kn);
      AssertCtx ax;
      assert_ctx(&ws->w, rules, nr, rs->live, rs->nlive, kn, &ax);
      int rem = g_label_rem_max - t; if (rem < 0) rem = 0;
      double bce = 0;
      for (int a = 0; a < NA; a++){
        int why;
        double y = assert_adopt(&ax, a, rem, &why) ? 1.0 : 0.0;
        double x = g_epc[t].prop[a];
        bce += y*softplus(-x) + (1.0-y)*softplus(x);
        if (grad) g_epc[t].dprop[a] = ASSERTW*(sigmoid(x) - y)/(double)NA;
      }
      total += ASSERTW*bce/(double)NA;
    }
#endif
#if LOOPCELL
    g_epcsrc[t] = CELLSHUF ? (t+1) % ws->nsteps : t;
    action_embed(p, rs->cf[rs->best], g_epea[t]);
    if (PREDW > 0 && t+1 < ws->nsteps){
      double tgt = ep_maxutil(&ws->st[t+1]);
      g_eppred[t] = pred_fwd(p, z, g_epea[t], g_epth[t], g_eppx[t]);
      double e = g_eppred[t]-tgt;
      total += PREDW*e*e;
    }
    if (!CELLDETACH){
      double ea_cell[D];
      if (g_epcsrc[t] == t){ for (int d = 0; d < D; d++) ea_cell[d] = g_epea[t][d]; }
      else action_embed(p, ws->st[g_epcsrc[t]].cf[ws->st[g_epcsrc[t]].best], ea_cell);
      cell_fwd(p, z, ea_cell, z, &g_epcell[t]);
    }
#endif
  }
  return total;
}

#if LOOPCELL
static void episode_backward(const WSteps *ws){
  Params *g = g_g;
  const Params *p = g_p;
  double dz_rec[D];
  for (int d = 0; d < D; d++) dz_rec[d] = 0;
  for (int t = ws->nsteps-1; t >= 0; t--){
    const RStep *rs = &ws->st[t];
    model_backward_ds(&g_epc[t], rs->state, rs->cf, rs->nlive, g_epds[t]);
    double dz[D], dea_pred[D];
    for (int d = 0; d < D; d++){ dz[d] = g_dh[0][d]; dea_pred[d] = 0; }
    if (PREDW > 0 && t+1 < ws->nsteps){
      double tgt = ep_maxutil(&ws->st[t+1]);
      pred_bwd(p, g, g_epth[t], g_eppx[t], 2.0*PREDW*(g_eppred[t]-tgt), dz, dea_pred);
      action_embed_bwd(g, rs->cf[rs->best], dea_pred);
    }
    if (CELLDETACH){
      /* static token: every step's z IS z0; accumulate its gradient directly */
      for (int d = 0; d < D; d++) g->z0[d] += dz[d];
      continue;
    }
    double dz_prev[D], dea_cell[D];
    for (int d = 0; d < D; d++){ dz_prev[d] = 0; dea_cell[d] = 0; }
    cell_bwd(p, g, &g_epcell[t], dz_rec, dz_prev, dea_cell);
    action_embed_bwd(g, ws->st[g_epcsrc[t]].cf[ws->st[g_epcsrc[t]].best], dea_cell);
    if (t == 0){ for (int d = 0; d < D; d++) g->z0[d] += dz[d] + dz_prev[d]; }
    else for (int d = 0; d < D; d++) dz_rec[d] = dz[d] + dz_prev[d];
  }
}
#else
static void episode_backward(const WSteps *ws){
  for (int t = ws->nsteps-1; t >= 0; t--){
    const RStep *rs = &ws->st[t];
    model_backward_ds(&g_epc[t], rs->state, rs->cf, rs->nlive, g_epds[t]);
  }
}
#endif

/* world-model quality on the val split: MSE of the (z_t, a_t) prediction vs
 * the kernel's next-state optimal value, against a constant-train-mean baseline */
#if LOOPCELL
static void pred_val_report(const Params *p){
  double ssum = 0; long sn = 0;
  for (int i = 0; i < g_nw[0]; i++){
    const WSteps *ws = &g_data[0][i];
    for (int t = 0; t+1 < ws->nsteps; t++){ ssum += ep_maxutil(&ws->st[t+1]); sn++; }
  }
  double tmean = sn ? ssum/(double)sn : 0;
  double mse = 0, bse = 0; long n = 0;
  for (int i = 0; i < g_nw[1]; i++){
    const WSteps *ws = &g_data[1][i];
    double z[D];
    for (int d = 0; d < D; d++) z[d] = p->z0[d];
    for (int t = 0; t < ws->nsteps; t++){
      const RStep *rs = &ws->st[t];
      double ea[D], th[D], x[2*D];
      action_embed(p, rs->cf[rs->best], ea);
      if (t+1 < ws->nsteps){
        double tgt = ep_maxutil(&ws->st[t+1]);
        double v = pred_fwd(p, z, ea, th, x);
        mse += (v-tgt)*(v-tgt); bse += (tmean-tgt)*(tmean-tgt); n++;
      }
      if (!CELLDETACH) cell_fwd(p, z, ea, z, &g_evalcell);
    }
  }
  printf("LOOPCELL-VAL predw=%.3f detach=%d shuf=%d mse=%.4f base_mse=%.4f n=%ld\n",
         (double)PREDW, CELLDETACH, CELLSHUF, n ? mse/(double)n : 0, n ? bse/(double)n : 0, n);
}
#endif
#endif

static void adam_update(Params *p, Params *g, Params *m, Params *v, int t){
  long n = param_count();
  double *pp = pv(p), *gg = pv(g), *mm = pv(m), *vv = pv(v);
  double norm = 0;
  for (long i = 0; i < n; i++) norm += gg[i]*gg[i];
  norm = sqrt(norm);
  double clip = (norm > 1.0) ? 1.0/norm : 1.0;
  double bc1 = 1.0 - pow(BETA1, t), bc2 = 1.0 - pow(BETA2, t);
  for (long i = 0; i < n; i++){
    double gi = gg[i]*clip;
    mm[i] = BETA1*mm[i] + (1.0-BETA1)*gi;
    vv[i] = BETA2*vv[i] + (1.0-BETA2)*gi*gi;
    double mh = mm[i]/bc1, vh = vv[i]/bc2;
    pp[i] -= LR*(mh/(sqrt(vh)+ADAM_EPS) + WD*pp[i]);
  }
}

/* ---- evaluation ---- */
typedef struct { double top1, hit, regret; } Metrics;

static void eval_steps(const Params *p, int split, Metrics *out){
  double u = 0, h = 0, r = 0;
  long n = 0;
  for (int i = 0; i < g_nw[split]; i++){
    const WSteps *ws = &g_data[split][i];
    double z[D];
#if LOOPCELL
    for (int d = 0; d < D; d++) z[d] = p->z0[d];
#endif
    for (int s = 0; s < ws->nsteps; s++){
      const RStep *rs = &ws->st[s];
#if TYPED
      model_forward_typed(p, rs->state, rs->cf, rs->nlive, rs->live,
                          rs->fatoms, rs->nfact, rs->oatoms, rs->nobl, (const double*)0, g_c);
#else
      model_forward_z(p, rs->state, rs->cf, rs->nlive, LOOPCELL ? z : (const double*)0, g_c);
#endif
      int arg = 0;
      for (int j = 1; j < rs->nlive; j++) if (g_c->score[j] > g_c->score[arg]) arg = j;
      u += rs->util[arg];
      h += (arg == rs->best) ? 1.0 : 0.0;
      double mx = rs->util[0];
      for (int j = 1; j < rs->nlive; j++) if (rs->util[j] > mx) mx = rs->util[j];
      r += mx - rs->util[arg];
      n++;
#if LOOPCELL
      if (!CELLDETACH){
        double ea[D];
        action_embed(p, rs->cf[rs->best], ea);
        cell_fwd(p, z, ea, z, &g_evalcell);
      }
#endif
    }
  }
  if (n == 0){ out->top1 = out->hit = out->regret = 0; return; }
  out->top1 = u/n; out->hit = h/n; out->regret = r/n;
}

static double g_head_prior[P];

/* ---- baseline rankers on the same per-step features ---- */
static void eval_steps_base(int split, int mode, Metrics *out){
  double u = 0, h = 0, r = 0;
  long n = 0;
  for (int i = 0; i < g_nw[split]; i++){
    const WSteps *ws = &g_data[split][i];
    for (int s = 0; s < ws->nsteps; s++){
      const RStep *rs = &ws->st[s];
      int arg = 0;
      double scr[POOL];
      for (int j = 0; j < rs->nlive; j++){
        if (mode == 1) scr[j] = rs->cf[j][3] + 0.5*rs->cf[j][5];
        else if (mode == 2){
          int head = 0;
          for (int q = 0; q < HP; q++) if (rs->cf[j][8+q] > 0.5) head = q;
          scr[j] = g_head_prior[head] - 0.2*2.0*rs->cf[j][1];
        } else if (mode == 3) scr[j] = (double)((j*2654435761u) % 1000) / 1000.0;
        else scr[j] = 0.0;
        if (scr[j] > scr[arg]) arg = j;
      }
      u += rs->util[arg];
      h += (arg == rs->best) ? 1.0 : 0.0;
      double mx = rs->util[0];
      for (int j = 1; j < rs->nlive; j++) if (rs->util[j] > mx) mx = rs->util[j];
      r += mx - rs->util[arg];
      n++;
    }
  }
  if (!n){ out->top1 = out->hit = out->regret = 0; return; }
  out->top1 = u/n; out->hit = h/n; out->regret = r/n;
}

/* ---- proof policy on a whole world (recomputes features for its own state) ---- */
static Params *g_untrained;

static void step_features(const World *w, const int *rules, int nrules,
                          const int *live, int nlive, double *state,
                          double (*cf)[CAND_DIM], double *util, int rem){
  state_features(w, rules, nrules, live, nlive, state, rem);
  for (int k = 0; k < nlive; k++){
    cand_features(w, rules, nrules, live[k], cf[k]);
    util[k] = utility(w, rules, nrules, live[k]);
  }
  fill_path_features(w, rules, nrules, live, nlive, cf);
  fill_prior_features(live, nlive, cf);
}

/* mode: 0 model, 1 support, 2 prior, 3 random, 4 untrained, 5 shuffled, 6 oracle */
static void policy_world(const World *w, const Params *p, int mode, uint64_t seed,
                         int *goals_proved, int *steps_used, int *full_success){
  int rules[MAXRULE];
  int nrules = SEED_RULES;
  for (int k = 0; k < SEED_RULES; k++) rules[k] = w->theory[k];
  rng_state = seed | 1ULL;
  static double state[STATE_DIM];
  static double cf2[POOL][CAND_DIM];
  static double util[POOL];
#if LOOPCELL
  double z[D];
  for (int d = 0; d < D; d++) z[d] = p->z0[d];
#endif
  int used_steps = 0;
  for (int st = 0; st < g_eval_budget; st++){
    int live[POOL], nlive = 0;
    for (int c = 0; c < POOL; c++){
      int r = w->cands[c], u = 0;
      for (int k = 0; k < nrules; k++) if (rules[k] == r) u = 1;
      if (!u) live[nlive++] = r;
    }
    if (!nlive) break;
    uint8_t known[WENT];
    {
      closure(w->facts, rules, nrules, known);
      nlive = focus_filter(w, known, live, nlive);   /* Rocq obligation focus */
      pc_filter(known, live, &nlive);                /* Silicon path condition */
    }
    if (!nlive) break;
    step_features(w, rules, nrules, live, nlive, state, cf2, util, g_eval_budget - st);
    int pick = 0;
    if (mode == 0 || mode == 4 || mode == 5){
      const Params *mp = (mode == 4) ? g_untrained : p;
      int perm[POOL];
      for (int k = 0; k < nlive; k++) perm[k] = k;
      if (mode == 5){   /* break feature/label correspondence */
        for (int k = nlive-1; k > 0; k--){
          int j = randbelow(k+1);
          int t = perm[k]; perm[k] = perm[j]; perm[j] = t;
        }
      }
      static double cfp[POOL][CAND_DIM];
      for (int k = 0; k < nlive; k++)
        for (int d = 0; d < CAND_DIM; d++) cfp[k][d] = cf2[perm[k]][d];
#if TYPED
      {
        int livep[POOL], fa[NA], oa[GOAL_COUNT];
        for (int k = 0; k < nlive; k++) livep[k] = live[perm[k]];
        int nf = atoms_from_known(known, fa);
        int no = obligs_from_goals(w, known, oa);
        model_forward_typed(mp, state, (const double (*)[CAND_DIM])cfp, nlive, livep,
                            fa, nf, oa, no, (const double*)0, g_c);
      }
#else
      model_forward_z(mp, state, (const double (*)[CAND_DIM])cfp, nlive,
#if LOOPCELL
                      z,
#else
                      (const double*)0,
#endif
                      g_c);
#endif
      for (int k = 1; k < nlive; k++) if (g_c->score[k] > g_c->score[pick]) pick = k;
#if ASSERT
      {
        AssertCtx ax;
        assert_ctx(w, rules, nrules, live, nlive, known, &ax);
        int a_star = assert_top(&ax, g_c->prop, g_eval_budget - st);
        int focal[POOL], nf = assert_focus_filter(w, &ax, a_star, live, nlive, focal);
        g_assert_states++;
        if (a_star >= 0) g_assert_adopt++; else g_assert_fallback++;
        { int rb = 0, why;
          for (int a = 1; a < NA; a++) if (g_c->prop[a] > g_c->prop[rb]) rb = a;
          if (assert_adopt(&ax, rb, g_eval_budget - st, &why)) g_assert_raw_adopt++; }
        if (nf > 0){
          int pk = -1;
          for (int k = 0; k < nlive; k++){
            int inf = 0;
            for (int q = 0; q < nf; q++) if (focal[q] == live[k]) inf = 1;
            if (!inf) continue;
            if (pk < 0 || g_c->score[k] > g_c->score[pk]) pk = k;
          }
          if (pk >= 0) pick = pk;
        }
      }
#endif
#if SYMGATE >= 1
      /* path-condition census at the actual selection point: the soft residual
       * gate can still select an inadmissible candidate, the hard gate cannot. */
      if (!g_c->sym[1+pick]) g_pc_picks++;
#endif
    } else if (mode == 1){
      for (int k = 1; k < nlive; k++)
        if (cf2[k][3] + 0.5*cf2[k][5] > cf2[pick][3] + 0.5*cf2[pick][5]) pick = k;
    } else if (mode == 2){
      double sb = -1e30;
      for (int k = 0; k < nlive; k++){
        int head = 0;
        for (int q = 0; q < HP; q++) if (cf2[k][8+q] > 0.5) head = q;
        double s = g_head_prior[head] - 0.2*2.0*cf2[k][1];
        if (s > sb){ sb = s; pick = k; }
      }
    } else if (mode == 3){
      pick = randbelow(nlive);
    } else { /* 6: oracle */
      for (int k = 1; k < nlive; k++) if (util[k] > util[pick]) pick = k;
    }
    rules[nrules++] = live[pick];
    used_steps++;
#if LOOPCELL
    if (mode == 0 || mode == 4 || mode == 5){
      const Params *mp = (mode == 4) ? g_untrained : p;
      double ea[D];
      action_embed(mp, cf2[pick], ea);
      if (!CELLDETACH){ CellCache cc; cell_fwd(mp, z, ea, z, &cc); }
    }
#endif
  }
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  int gp = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (GOAL_KNOWN(w,g,known)) gp++;
  *goals_proved = gp;
  *steps_used = used_steps;
  *full_success = (gp == w->ngoals) ? 1 : 0;
}

/* ---- native nondeterministic search -------------------------------------
 * Port of the Screamer core (choice points + backtracking + propagation) and of
 * the Silicon state-subsumption idea into the C/LLVM line, with the transformer
 * supplying the child order. The trail is the applied-rule list (budget is the
 * only other state), so undo is O(1).
 * Propagation: an admissible bound prunes a subtree when the best continuation
 * cannot beat the incumbent. Subsumption: a fact set that is a subset of an
 * already-visited state at the same or smaller depth is dominated (it cannot
 * derive more with the same remaining budget). */
#define SUBS_MAX 4096
static uint64_t subs_key[SUBS_MAX];
static int subs_depth[SUBS_MAX];
static int subs_n = 0;

static uint64_t pack_facts_u64(const uint8_t m[WENT]){
  uint64_t s = 0;
#if RELATOM
  for (int e = 0; e < WENT; e++) s |= (uint64_t)m[e] << (8*e);
#else
  for (int e = 0; e < WENT; e++) s |= (uint64_t)m[e] << (6*e);
#endif
  return s;
}
static int is_subset_mask(uint64_t a, uint64_t b){   /* a subset of b */
#if RELATOM
  return (a & ~b) == 0;
#else
  for (int e = 0; e < WENT; e++){
    uint64_t am = (a >> (6*e)) & 0x3f, bm = (b >> (6*e)) & 0x3f;
    if ((am & ~bm) != 0) return 0;
  }
  return 1;
#endif
}
static int dominated(uint64_t mask, int depth){
  for (int i = 0; i < subs_n; i++)
    if (subs_depth[i] <= depth && is_subset_mask(mask, subs_key[i])) return 1;
  return 0;
}
static void subs_add(uint64_t mask, int depth){
  if (subs_n < SUBS_MAX){ subs_key[subs_n] = mask; subs_depth[subs_n] = depth; subs_n++; }
}

static int g_best_seen;
static int g_best_rules[MAXRULE];
static int g_best_nrules = 0;
static int g_leaf_best = -1;

/* ---- Rocq-style independent proof certificate -----------------------------
 * The search records WHICH rule derived each atom (a parent map). The checker
 * then re-derives every goal from base facts using ONLY the parent map: leaves
 * must be base facts, and every used rule must have the head it claims. The
 * checker never trusts the closure that the search used.
 * g_cert_selftest=1 corrupts one parent after recording, so the gate can show a
 * mutated certificate is rejected (the checker is not vacuous). */
static int cert_check(const World *w, const int *rules, int nrules){
  uint8_t base[WENT];
  closure(w->facts, w->theory, SEED_RULES, base);
  uint8_t known[WENT];
  for (int e = 0; e < WENT; e++) known[e] = base[e];
  int parent[WENT][P];
  for (int e = 0; e < WENT; e++) for (int p = 0; p < P; p++) parent[e][p] = -1;
  int changed = 1;
  while (changed){
    changed = 0;
    for (int k = 0; k < nrules; k++){
      const Rule *r = &all_rules[rules[k]];
      uint8_t bm = 0;
      for (int q = 0; q < r->blen; q++) bm |= (uint8_t)(1u << r->body[q]);
      uint8_t hm = (uint8_t)(1u << r->head);
      for (int e = 0; e < WENT; e++)
        if ((known[e] & bm) == bm && !(known[e] & hm)){
          known[e] |= hm; parent[e][r->head] = rules[k]; changed = 1;
        }
    }
  }
  if (g_cert_selftest){
    /* negative control: drop the parent of a goal atom that is not a base fact.
     * The walk cannot reach a base fact for it, so the checker MUST fail. */
    for (int g = 0; g < w->ngoals; g++){
      int e = w->goal_ent[g], p = w->goal_pred[g];
      if (!(base[e] & (uint8_t)(1u << p)) && parent[e][p] >= 0){ parent[e][p] = -1; }
    }
  }
  for (int g = 0; g < w->ngoals; g++){
    int e = w->goal_ent[g], p = w->goal_pred[g];
    if (!(known[e] & (uint8_t)(1u << p))) continue;   /* not derived: nothing to certify */
    g_cert_checked++;
    int stack_e[64], stack_p[64], sp = 0, ok = 1, guard = 0;
    stack_e[sp] = e; stack_p[sp] = p; sp++;
    while (sp > 0 && ok){
      if (++guard > 256){ ok = 0; break; }
      int ce = stack_e[--sp], cp = stack_p[sp];
      if (base[ce] & (uint8_t)(1u << cp)) continue;   /* justified by a base fact */
      int r = parent[ce][cp];
      if (r < 0){ ok = 0; break; }
      const Rule *rr = &all_rules[r];
      if (rr->head != cp){ ok = 0; break; }
      for (int q = 0; q < rr->blen; q++){
        if (sp >= 60){ ok = 0; break; }
        stack_e[sp] = ce; stack_p[sp] = rr->body[q]; sp++;
      }
    }
    if (g_cert_selftest){ if (!ok) g_cert_mutfail++; else g_cert_ok++; }
    else if (ok) g_cert_ok++;
    else g_cert_fail++;
  }
  return (int)g_cert_fail;
}

/* ---- Silicon-style path condition (admissibility) in search ---------------
 * A candidate whose body is not supported by the current closure violates the
 * path condition: under SYMGATE>=2 it is removed from the action set. The DFS
 * has no transformer mask, so the condition is applied on the explicit set. */
static int pc_admissible(const double *cfrow){ return cfrow[6] > 0.5; }
static void pc_filter(const uint8_t *known, int *live, int *nlive){
#if SYMGATE >= 2
  int m = 0;
  for (int k = 0; k < *nlive; k++){
    const Rule *r = &all_rules[live[k]];
    if ((int)support(r, known) > 0) live[m++] = live[k];
    else g_pc_dropped++;
  }
  if (m == 0) g_pc_fallback++;   /* no admissible action: keep the set, count it */
  else *nlive = m;
#else
  (void)known; (void)live; (void)nlive;
#endif
}

/* obligation-directed focus (Rocq tactic focus / obligation closure): keep only
 * candidates whose head predicate can contribute to an unproved goal. The
 * relevance set is the fixpoint "heads of candidates whose head is relevant add
 * their body predicates", starting from the unproved goal predicates. Forward
 * chaining only derives atoms with the head predicate of an applied rule, so a
 * candidate whose head never reaches a goal cannot contribute. Gate: exhaustive
 * DFS agreement with the unfiltered search (completeness). */
static long g_focus_states = 0, g_focus_removed = 0;
static int focus_filter(const World *w, const uint8_t *known, int *live, int nlive){
  if (!g_focus) return nlive;
#if RELATOM
  /* obligation focus over ATOMS: seed the unproved goal atoms, propagate
   * backwards through candidate bodies, keep candidates whose head is focal.
   * Binding-sensitive: unlike the unary fixture this can remove candidates. */
  int rel[NA];
  for (int i = 0; i < NA; i++) rel[i] = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (!GOAL_KNOWN(w,g,known)) rel[GOAL_ATOM(w,g)] = 1;
#else
  int rel[P];
  for (int p = 0; p < P; p++) rel[p] = 0;
  for (int g = 0; g < w->ngoals; g++){
    int e = w->goal_ent[g], p = w->goal_pred[g];
    if (!(known[e] & (uint8_t)(1u << p))) rel[p] = 1;
  }
#endif
  int changed = 1;
  while (changed){
    changed = 0;
    for (int c = 0; c < POOL; c++){
      const Rule *r = &all_rules[w->cands[c]];
      if (!rel[r->head]) continue;
      for (int q = 0; q < r->blen; q++)
        if (!rel[r->body[q]]){ rel[r->body[q]] = 1; changed = 1; }
    }
  }
  int focal[POOL], nf = 0;
  for (int k = 0; k < nlive; k++)
    if (rel[all_rules[live[k]].head]) focal[nf++] = live[k];
  g_focus_states++;
  g_focus_removed += (nlive - nf);
  if (!nf) return nlive;
  for (int k = 0; k < nf; k++) live[k] = focal[k];
  return nf;
}

/* ---- verified 2-rule lemma (contract) mining --------------------------------
 * A lemma (r1,r2) is admitted only when the kernel confirms the chain: r1's body
 * is a single atom and r2's body equals r1's head, so applying the pair derives
 * r2's head at r1's body entity. Applying a lemma charges one action slot
 * instead of two (Silicon method-summary / Rocq lemma reuse). */
static void lemma_mine(void){
  g_nlem = 0;
  for (int i = 0; i < g_nw[0] && g_nlem < g_lemma_max; i++){
    const WSteps *ws = &g_data[0][i];
    int seq[MAXRULE];
    int m = SEED_RULES;
    for (int k = 0; k < SEED_RULES; k++) seq[k] = ws->w.theory[k];
    for (int st = 0; st < ws->nsteps; st++){
      const RStep *rs = &ws->st[st];
      if (rs->nlive <= 0) break;
      seq[m++] = rs->live[rs->best];
    }
    for (int k = SEED_RULES; k + 1 < m && g_nlem < g_lemma_max; k++){
      int r1 = seq[k], r2 = seq[k+1];
      const Rule *a = &all_rules[r1], *b = &all_rules[r2];
      if (a->blen != 1 || b->blen != 1 || b->body[0] != a->head) continue;
      /* kernel check of the contract on every train world that has both rules */
      uint8_t kn[WENT];
      closure(ws->w.facts, ws->w.theory, SEED_RULES, kn);
      int ok = 0;
#if RELATOM
      ok = ATOM_KNOWN(kn, a->body[0]) ? 1 : 0;
#else
      for (int e = 0; e < WENT; e++) if (kn[e] & (uint8_t)(1u << a->body[0])) ok = 1;
#endif
      if (!ok) continue;
      int dup = 0;
      for (int q = 0; q < g_nlem; q++) if (g_lem[q].r1 == r1 && g_lem[q].r2 == r2) dup = 1;
      if (dup) continue;
      g_lem[g_nlem].r1 = r1; g_lem[g_nlem].r2 = r2;
      g_lem[g_nlem].body = a->body[0];
      g_lem[g_nlem].uses = 0;
      g_nlem++;
    }
  }
  printf("LEMMA-MINE unique=%d cap=%d kernel_checked=1\n", g_nlem, g_lemma_max);
}

/* ---- 0.0261 learned contract proposal --------------------------------------
 * The 0.0257/0.0260 contract set is HAND-DESIGNED: pairs are read off teacher
 * rollouts, so the "proposal" step carries no learning. Here the candidate spaces
 * are enumerated from each world's own ruleset (structural chain body(r2)=head(r1))
 * and three proposers are compared at matched contract count:
 *   mined   teacher-rollout pairs (PAIRMODE 1)
 *   learned linear pair scorer trained on KERNEL labels (PAIRMODE 2)
 *   random  structurally valid pairs (PAIRMODE 3, matched count, no learning)
 * Labels come from the kernel, never from the teacher: for a train-world root the
 * label of a pair is the change in proved goals when the pair is committed
 * (two closures). The scorer is fitted by normal equations (deterministic, 8x8). */
static void pair_features(const World *w, const uint8_t *known, int r1, int r2,
                          double *f){
  const Rule *a = &all_rules[r1], *b = &all_rules[r2];
  int sup_body = 0, sup_head = 0, goal1 = 0, goal2 = 0;
#if RELATOM
  sup_body = (a->blen && ATOM_KNOWN(known, a->body[0])) ? 1 : 0;
  sup_head = ATOM_KNOWN(known, a->head) ? 1 : 0;
  for (int g = 0; g < w->ngoals; g++){
    if (w->goal_pred[g] == atom_pred(a->head)) goal1 = 1;
    if (w->goal_pred[g] == atom_pred(b->head)) goal2 = 1;
  }
  f[0] = (double)sup_body;
  f[1] = (double)sup_head;
#else
  for (int e = 0; e < WENT; e++){
    if (a->blen && (known[e] & (uint8_t)(1u << a->body[0]))) sup_body++;
    if (known[e] & (uint8_t)(1u << a->head)) sup_head++;
  }
  for (int g = 0; g < w->ngoals; g++){
    if (w->goal_pred[g] == a->head) goal1 = 1;
    if (w->goal_pred[g] == b->head) goal2 = 1;
  }
  f[0] = (double)sup_body / (double)WENT;
  f[1] = (double)sup_head / (double)WENT;
#endif
  f[2] = (double)goal1;
  f[3] = (double)goal2;
  f[4] = rule_cost(a) / 2.0;
  f[5] = rule_cost(b) / 2.0;
#if RELATOM
  f[6] = g_head_prior[atom_pred(b->head)];
#else
  f[6] = g_head_prior[b->head];
#endif
  f[7] = 1.0;                       /* bias */
}

static int pair_structurally_valid(const World *w, int r1, int r2){
  const Rule *a = &all_rules[r1], *b = &all_rules[r2];
  if (a->blen != 1 || b->blen != 1) return 0;
  if (b->body[0] != a->head) return 0;
  for (int c = 0; c < POOL; c++){
    if (w->cands[c] == r1 || w->cands[c] == r2) return 1;
  }
  return 0;
}

/* kernel label: committing (r1,r2) at this state -> goal delta + atom delta.
 * Both terms come from the kernel closure; the teacher never supplies the label. */
static double pair_label(const World *w, const int *rules, int nrules, int r1, int r2){
  int rr[MAXRULE];
  int n = nrules;
  for (int k = 0; k < nrules; k++) rr[k] = rules[k];
  if (n + 2 > MAXRULE) return 0.0;
  rr[n++] = r1; rr[n++] = r2;
  uint8_t kn[WENT], k0[WENT];
  closure(w->facts, rules, nrules, k0);
  closure(w->facts, rr, n, kn);
#if RELATOM
  int rel[NA];
  for (int i = 0; i < NA; i++) rel[i] = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (!GOAL_KNOWN(w,g,k0)) rel[GOAL_ATOM(w,g)] = 1;
#else
  int rel[P];
  for (int p = 0; p < P; p++) rel[p] = 0;
  for (int g = 0; g < w->ngoals; g++){
    int e = w->goal_ent[g], p = w->goal_pred[g];
    if (!(k0[e] & (uint8_t)(1u << p))) rel[p] = 1;
  }
#endif
  for (int it = 0; it < 4; it++)
    for (int c = 0; c < POOL; c++){
      const Rule *r = &all_rules[w->cands[c]];
      if (!rel[r->head]) continue;
      for (int q = 0; q < r->blen; q++) rel[r->body[q]] = 1;
    }
  int g0 = 0, g1 = 0, a0 = 0, a1 = 0;
  for (int g = 0; g < w->ngoals; g++){
    if (GOAL_KNOWN(w,g,k0)) g0++;
    if (GOAL_KNOWN(w,g,kn)) g1++;
  }
#if RELATOM
  {
    uint64_t m0 = fs_load(k0), m1 = fs_load(kn);
    for (int id = 0; id < NA; id++){
      if (!rel[id]) continue;                /* goal-reachable atoms only */
      if ((m0 >> id) & 1ULL) a0++;
      if ((m1 >> id) & 1ULL) a1++;
    }
    return 4.0*(double)(g1 - g0) + (double)(a1 - a0)/(double)NA;
  }
#else
  for (int e = 0; e < WENT; e++){
    for (int p = 0; p < P; p++){
      if (!rel[p]) continue;                 /* goal-reachable predicates only */
      if (k0[e] & (uint8_t)(1u << p)) a0++;
      if (kn[e] & (uint8_t)(1u << p)) a1++;
    }
  }
  return 4.0*(double)(g1 - g0) + (double)(a1 - a0)/(double)(WENT*P);
#endif
}

static void pair_learn(void){
  /* normal equations over kernel-labelled pairs sampled from RANDOM rollouts
   * (model-independent state distribution; the label is always kernel-derived) */
  double A[PAIRF][PAIRF], bb[PAIRF], f[PAIRF];
  for (int i = 0; i < PAIRF; i++){ bb[i] = 0; for (int j = 0; j < PAIRF; j++) A[i][j] = 0; }
  long rows = 0, pos = 0;
  uint64_t saved = rng_state;
  for (int i = 0; i < g_nw[0]; i++){
    const World *w = &g_data[0][i].w;
    int used[POOL];
    for (int c = 0; c < POOL; c++) used[c] = 0;
    int rules[MAXRULE];
    int nrules = SEED_RULES;
    for (int k = 0; k < SEED_RULES; k++) rules[k] = w->theory[k];
    int depth = 0;
    while (depth < g_eval_budget){
      uint8_t known[WENT];
      closure(w->facts, rules, nrules, known);
      for (int c1 = 0; c1 < POOL; c1++){
        if (used[c1]) continue;
        for (int c2 = 0; c2 < POOL; c2++){
          if (used[c2] || c1 == c2) continue;
          int r1 = w->cands[c1], r2 = w->cands[c2];
          if (!pair_structurally_valid(w, r1, r2)) continue;
          const Rule *ar = &all_rules[r1];
          int ok = 0;
          for (int e = 0; e < WENT; e++) if (known[e] & (uint8_t)(1u << ar->body[0])) ok = 1;
          if (!ok) continue;
          double lab = pair_label(w, rules, nrules, r1, r2);
          if (lab < 0) lab = 0;
          if (lab >= 1.0) pos++;
          pair_features(w, known, r1, r2, f);
          for (int p = 0; p < PAIRF; p++){
            bb[p] += f[p]*lab;
            for (int q = 0; q < PAIRF; q++) A[p][q] += f[p]*f[q];
          }
          rows++;
        }
      }
      /* advance the rollout with a uniformly random admissible single rule */
      int pick = -1, nfree = 0;
      for (int c = 0; c < POOL; c++) if (!used[c]) nfree++;
      if (!nfree) break;
      int want = (int)(randbelow((uint64_t)nfree));
      for (int c = 0, k2 = 0; c < POOL; c++) if (!used[c]){ if (k2 == want){ pick = c; break; } k2++; }
      if (pick < 0) break;
      used[pick] = 1;
      if (nrules + 1 > MAXRULE) break;
      rules[nrules++] = w->cands[pick];
      depth++;
    }
  }
  rng_state = saved;
  for (int i = 0; i < PAIRF; i++) A[i][i] += 1e-3;
  for (int i = 0; i < PAIRF; i++){
    int piv = i;
    for (int r = i+1; r < PAIRF; r++) if (fabs(A[r][i]) > fabs(A[piv][i])) piv = r;
    if (piv != i){
      for (int c = 0; c < PAIRF; c++){ double t = A[i][c]; A[i][c] = A[piv][c]; A[piv][c] = t; }
      double t = bb[i]; bb[i] = bb[piv]; bb[piv] = t;
    }
    double d = A[i][i];
    if (fabs(d) < 1e-12){ g_pairw[i] = 0; continue; }
    for (int c = i; c < PAIRF; c++) A[i][c] /= d;
    bb[i] /= d;
    for (int r = 0; r < PAIRF; r++){
      if (r == i) continue;
      double m = A[r][i];
      if (m == 0) continue;
      for (int c = i; c < PAIRF; c++) A[r][c] -= m*A[i][c];
      bb[r] -= m*bb[i];
    }
  }
  for (int i = 0; i < PAIRF; i++) g_pairw[i] = bb[i];
  g_pair_learned = 1;
  printf("PAIR-LEARN rows=%ld positives=%ld w=[", rows, pos);
  for (int i = 0; i < PAIRF; i++) printf("%.4f%s", g_pairw[i], i+1<PAIRF ? "," : "");
  printf("]\n");
}

static double pair_score(const World *w, const uint8_t *known, int r1, int r2){
  double f[PAIRF], s = 0;
  pair_features(w, known, r1, r2, f);
  for (int i = 0; i < PAIRF; i++) s += g_pairw[i]*f[i];
  return s;
}

/* Build the contract set for the CURRENT state under the active proposer.
 * Learned/random propose from the world's own ruleset (not from rollouts), and
 * the set is capped at g_pair_keep so every proposer gets the same budget. */
typedef struct { int r1, r2; } PairAct;
static int pair_candidates(const World *w, const uint8_t *known, const int *rules,
                           int nrules, PairAct *out, int max){
  PairAct all[POOL*POOL];
  double sc[POOL*POOL];
  int nall = 0;
  for (int c1 = 0; c1 < POOL; c1++){
    int r1 = w->cands[c1], used1 = 0;
    for (int k = 0; k < nrules; k++) if (rules[k] == r1) used1 = 1;
    if (used1) continue;
    for (int c2 = 0; c2 < POOL; c2++){
      int r2 = w->cands[c2], used2 = 0;
      for (int k = 0; k < nrules; k++) if (rules[k] == r2) used2 = 1;
      if (used2) continue;
      if (!pair_structurally_valid(w, r1, r2)) continue;
      /* kernel applicability at this state: r1's body must hold somewhere */
      const Rule *a = &all_rules[r1];
      int ok = 0;
      for (int e = 0; e < WENT; e++) if (known[e] & (uint8_t)(1u << a->body[0])) ok = 1;
      if (!ok) continue;
      all[nall].r1 = r1; all[nall].r2 = r2;
      if (g_pairmode == 2) sc[nall] = pair_score(w, known, r1, r2);
      else sc[nall] = (double)randbelow(1000000);   /* matched-count control */
      nall++;
    }
  }
  for (int i = 0; i < nall; i++)
    for (int j = i+1; j < nall; j++)
      if (sc[j] > sc[i]){
        double t = sc[i]; sc[i] = sc[j]; sc[j] = t;
        PairAct tp = all[i]; all[i] = all[j]; all[j] = tp;
      }
  int m = (max < nall) ? max : nall;
  for (int i = 0; i < m; i++) out[i] = all[i];
  return m;
}

static void dfs_world_z(const World *w, int *rules, int nrules, int depth, int budget,
                        const double *z){
  g_dfs_nodes++;
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  int proven = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (GOAL_KNOWN(w,g,known)) proven++;
  if (proven > g_best_seen) g_best_seen = proven;
  if (depth >= budget){
    g_dfs_leafs++;
    if (proven >= g_leaf_best){
      g_leaf_best = proven; g_best_nrules = nrules;
      for (int k = 0; k < nrules; k++) g_best_rules[k] = rules[k];
    }
    return;
  }
  if (proven == w->ngoals){
    g_dfs_leafs++;
    if (proven >= g_leaf_best){
      g_leaf_best = proven; g_best_nrules = nrules;
      for (int k = 0; k < nrules; k++) g_best_rules[k] = rules[k];
    }
    return;
  }
  if (g_prop && proven + (budget - depth) <= g_best_seen) { g_dfs_pruned++; return; }
  uint64_t mask = 0;
  if (g_subsume){
    mask = pack_facts_u64(known);
    if (dominated(mask, depth)){ g_dfs_pruned++; return; }
  }
  int live[POOL], nlive = 0;
  for (int c = 0; c < POOL; c++){
    int used = 0;
    for (int k = 0; k < nrules; k++) if (rules[k] == w->cands[c]) used = 1;
    if (!used) live[nlive++] = w->cands[c];
  }
  if (!nlive) { g_dfs_leafs++; return; }
  nlive = focus_filter(w, known, live, nlive);   /* Rocq obligation focus */
  pc_filter(known, live, &nlive);                /* Silicon path condition (hard) */
  if (!nlive) { g_dfs_leafs++; return; }
  static double state[STATE_DIM];
  static double cf2[POOL][CAND_DIM];
  static double util[POOL];
  step_features(w, rules, nrules, live, nlive, state, cf2, util, budget - depth);
#if TYPED
  {
    int fa[NA], oa[GOAL_COUNT];
    int nf = atoms_from_known(known, fa);
    int no = obligs_from_goals(w, known, oa);
    model_forward_typed(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, live,
                        fa, nf, oa, no, (const double*)0, g_c);
  }
#else
  model_forward_z(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, z, g_c);
#endif
  g_dfs_cands += nlive;
  int order[POOL];
  for (int a = 0; a < nlive; a++) order[a] = a;
  for (int a = 0; a < nlive; a++)
    for (int b = a+1; b < nlive; b++)
      if (g_c->score[order[b]] > g_c->score[order[a]]){ int t = order[a]; order[a] = order[b]; order[b] = t; }
  /* combined action set: single rules + proposed 2-rule contracts.
   * PAIRMODE 1 uses the mined set; PAIRMODE 2/3 propose from the world's own
   * ruleset at this state (learned scorer / matched-count random control), each
   * capped at g_pair_keep. Contracts are ranked by the same transformer score of
   * their first rule, so only the *selection* differs between proposers. */
  int act_kind[POOL+128], act_val[POOL+128];
  double act_score[POOL+128];
  PairAct pact[POOL*POOL];
  int npact = 0;
  int nact = 0;
  for (int a = 0; a < nlive; a++){
    act_kind[nact] = 0; act_val[nact] = live[order[a]]; act_score[nact] = g_c->score[order[a]]; nact++;
  }
  if (g_pairmode == 1){
    for (int L = 0; L < g_nlem; L++){
      int r1 = g_lem[L].r1, r2 = g_lem[L].r2, i1 = -1, i2 = -1;
      for (int c = 0; c < POOL; c++){ if (w->cands[c] == r1) i1 = c; if (w->cands[c] == r2) i2 = c; }
      if (i1 < 0 || i2 < 0) continue;
      int used = 0;
      for (int k = 0; k < nrules; k++) if (rules[k] == r1 || rules[k] == r2) used = 1;
      if (used) continue;
      int pre_ok = 0;
      for (int e = 0; e < WENT; e++) if (known[e] & (uint8_t)(1u << g_lem[L].body)) pre_ok = 1;
      if (!pre_ok) continue;
      double sc = -1e30;
      for (int a = 0; a < nlive; a++) if (live[a] == r1) sc = g_c->score[a];
      if (sc <= -1e29) continue;
      pact[npact].r1 = r1; pact[npact].r2 = r2;
      act_kind[nact] = 1; act_val[nact] = npact; act_score[nact] = sc; npact++; nact++;
    }
  } else if (g_pairmode >= 2 && nrules + 2 <= MAXRULE){
    PairAct cand[POOL*POOL];
    int np = pair_candidates(w, known, rules, nrules, cand, g_pair_keep);
    for (int i = 0; i < np; i++){
      double sc = -1e30;
      for (int a = 0; a < nlive; a++) if (live[a] == cand[i].r1) sc = g_c->score[a];
      if (sc <= -1e29) continue;
      pact[npact] = cand[i];
      act_kind[nact] = 1; act_val[nact] = npact; act_score[nact] = sc; npact++; nact++;
    }
  }
  for (int a = 0; a < nact; a++)
    for (int b2 = a+1; b2 < nact; b2++)
      if (act_score[b2] > act_score[a]){
        double t = act_score[a]; act_score[a] = act_score[b2]; act_score[b2] = t;
        int tk = act_kind[a]; act_kind[a] = act_kind[b2]; act_kind[b2] = tk;
        int tv = act_val[a]; act_val[a] = act_val[b2]; act_val[b2] = tv;
      }
#if SYMGATE >= 1
  if (nact > 0 && act_kind[0] == 0){
    int top = act_val[0], ti = -1;
    for (int a = 0; a < nlive; a++) if (live[a] == top) ti = a;
    if (ti >= 0 && !g_c->sym[1+ti]) g_pc_picks++;
  }
#endif
#if ASSERT
  {
    AssertCtx ax;
    assert_ctx(w, rules, nrules, live, nlive, known, &ax);
    int a_star = assert_top(&ax, g_c->prop, budget - depth);
    int focal[POOL], nf = assert_focus_filter(w, &ax, a_star, live, nlive, focal);
    g_assert_states++;
    if (a_star >= 0) g_assert_adopt++; else g_assert_fallback++;
    { int rb = 0, why;
      for (int a = 1; a < NA; a++) if (g_c->prop[a] > g_c->prop[rb]) rb = a;
      if (assert_adopt(&ax, rb, budget - depth, &why)) g_assert_raw_adopt++; }
    if (nf > 0){
      int nn = 0;
      for (int a = 0; a < nact; a++){
        int keep_a = 1;
        if (act_kind[a] == 0){
          keep_a = 0;
          for (int q = 0; q < nf; q++) if (focal[q] == act_val[a]) keep_a = 1;
        }
        if (keep_a){
          act_kind[nn] = act_kind[a]; act_val[nn] = act_val[a]; act_score[nn] = act_score[a];
          nn++;
        }
      }
      nact = nn;
    }
  }
#endif
  int keep = (g_branch < nact) ? g_branch : nact;
  for (int a = 0; a < keep; a++){
    if (act_kind[a] == 0){
      rules[nrules] = act_val[a];
#if LOOPCELL
      { /* latent transition on the committed rule (cf row copied BEFORE the
         * recursive call: cf2 is a static buffer the child overwrites) */
        double znext[D], ea[D]; CellCache cc;
        int ri = act_val[a], li = -1;
        for (int q = 0; q < nlive; q++) if (live[q] == ri) li = q;
        action_embed(g_p, cf2[li], ea);
        cell_fwd(g_p, z, ea, znext, &cc);
        dfs_world_z(w, rules, nrules+1, depth+1, budget, znext);
      }
#else
      dfs_world_z(w, rules, nrules+1, depth+1, budget, (const double*)0);
#endif
    } else {
      int pi = act_val[a];
      if (nrules + 2 > MAXRULE) continue;      /* capacity guard (0260 fix) */
      int r1 = pact[pi].r1, r2 = pact[pi].r2;
      /* kernel re-check at application time (Silicon-style contract check): the
       * committed pair must derive r2's head where r1's body held, else the
       * contract is not admissible and the action is counted as a violation. */
      const Rule *ar = &all_rules[r1], *br = &all_rules[r2];
      int rr[MAXRULE];
      int n = nrules;
      for (int k = 0; k < nrules; k++) rr[k] = rules[k];
      rr[n++] = r1; rr[n++] = r2;
      uint8_t kn[WENT];
      closure(w->facts, rr, n, kn);
      int held = 0, derived = 0;
#if RELATOM
      held = (ar->blen && ATOM_KNOWN(kn, ar->body[0])) ? 1 : 0;
      derived = ATOM_KNOWN(kn, br->head) ? 1 : 0;
#else
      for (int e = 0; e < WENT; e++){
        if (ar->blen && (kn[e] & (uint8_t)(1u << ar->body[0]))) held = 1;
        if (kn[e] & (uint8_t)(1u << br->head)) derived = 1;
      }
#endif
      if (!held || !derived){ g_pair_viol++; continue; }
      rules[nrules] = r1; rules[nrules+1] = r2;
      g_pair_uses++; g_lemma_uses++;
#if LOOPCELL
      { /* a contract commits two rules: apply the cell once per rule, in order */
        double zmid[D], znext[D], ea[D]; CellCache cc;
        int li1 = -1, li2 = -1;
        for (int q = 0; q < nlive; q++){ if (live[q] == r1) li1 = q; if (live[q] == r2) li2 = q; }
        action_embed(g_p, cf2[li1], ea);
        cell_fwd(g_p, z, ea, zmid, &cc);
        if (li2 >= 0){ action_embed(g_p, cf2[li2], ea); cell_fwd(g_p, zmid, ea, znext, &cc); }
        else for (int d = 0; d < D; d++) znext[d] = zmid[d];
        dfs_world_z(w, rules, nrules+2, depth+g_lemma_cost, budget, znext);
      }
#else
      dfs_world_z(w, rules, nrules+2, depth+g_lemma_cost, budget, (const double*)0);
#endif
    }
    if (proven > g_best_seen) g_best_seen = proven;
  }
  /* R255-3: register only fully-explored states (postorder). Preorder registration
   * let an ancestor on the current path dominate its own descendants, which is
   * unsound even for exhaustive search (review 0255 F3). */
  if (g_subsume) subs_add(mask, depth);
}
static void dfs_world(const World *w, int *rules, int nrules, int depth, int budget){
  dfs_world_z(w, rules, nrules, depth, budget, LOOPCELL ? g_p->z0 : (const double*)0);
}

/* native DFS policy over the test split (returns goal fraction) */
static double policy_metrics_dfs(int split, double *full){
  subs_n = 0;
  g_dfs_nodes = g_dfs_cands = g_dfs_leafs = g_dfs_pruned = 0;
  long gp = 0, gt = 0, fs = 0, nw = 0;
  for (int i = 0; i < g_nw[split]; i++){
    const World *w = &g_data[split][i].w;
    int rules[MAXRULE];
    for (int k = 0; k < SEED_RULES; k++) rules[k] = w->theory[k];
    g_best_seen = 0; g_best_nrules = 0; g_leaf_best = -1;
    subs_n = 0;   /* R255-2: dominance is per-world; worlds share no facts/goals */
    dfs_world(w, rules, SEED_RULES, 0, g_eval_budget);
#if CERT
    if (g_cert_on && g_best_nrules > 0) cert_check(w, g_best_rules, g_best_nrules);
#endif
    gp += g_best_seen; gt += w->ngoals; if (g_best_seen == w->ngoals) fs++;
    nw++;
  }
  *full = nw ? (double)fs/(double)nw : 0.0;
  return gt ? (double)gp/(double)gt : 0.0;
}

/* Beam search over rule sequences scored by the model (width g_beam, depth NSTEPS).
 * Returns goals proved by the best complete sequence. */
/* ---- budget-exact proof bound -------------------------------------------
 * The policy commits at most NSTEPS distinct rules and the closure then runs to
 * fixpoint, so a committed rule keeps firing as other rules add atoms. The
 * exact bound is therefore a maximum over rule SUBSETS of size <= NSTEPS
 * (C(24,4)+C(24,3)+C(24,2)+C(24,1)+1 = 12,950 per world), not a DP over fact
 * sets (the committed set is part of the state). */
static int bnd_best;
static void bound_rec(const World *w, const uint8_t base[WENT], const int *pick,
                      int depth, int start, int k){
  if (depth == k){
    int rules[SEED_RULES+MAXBUDGET];
    for (int i = 0; i < SEED_RULES; i++) rules[i] = w->theory[i];
    for (int i = 0; i < k; i++) rules[SEED_RULES+i] = w->cands[pick[i]];
    uint8_t known[WENT];
    closure(w->facts, rules, SEED_RULES+k, known);
    int gp = 0;
    for (int g = 0; g < w->ngoals; g++)
      if (GOAL_KNOWN(w,g,known)) gp++;
    if (gp > bnd_best) bnd_best = gp;
    return;
  }
  for (int i = start; i < POOL; i++){
    ((int*)pick)[depth] = i;
    bound_rec(w, base, pick, depth+1, i+1, k);
  }
}
static int bound_world(const World *w){
  uint8_t base[WENT];
  closure(w->facts, w->theory, SEED_RULES, base);
  bnd_best = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (GOAL_KNOWN(w,g,base)) bnd_best++;
  int pick[MAXBUDGET];
  for (int i = 0; i < MAXBUDGET; i++) pick[i] = 0;
  int bmax = g_eval_budget < MAXBUDGET ? g_eval_budget : MAXBUDGET;
  for (int k = 1; k <= bmax; k++) bound_rec(w, base, pick, 0, 0, k);
  return bnd_best;
}

/* ---- matched-search beam: same controller, different scorer ---- */
typedef struct { long states, cands, closes, forwards; } Counters;

#define SC_MODEL_RAW 0
#define SC_MODEL_LOGP 1
#define SC_SUPPORT 2
#define SC_PRIOR 3
#define SC_RANDOM 4
#define SC_UNTRAINED 5
#define NSCORE 6
static const char *g_scorer_name[NSCORE] = {
  "model_raw", "model_logp", "support", "prior", "random", "untrained"
};

/* score nlive candidates under a scorer; returns 1 if scores came from a net */
static int score_candidates(int scorer, const Params *p, const double *state,
                            const double (*cf)[CAND_DIM], int nlive, double *out,
                            Counters *ctr, const double *z,
                            const int *live, const uint8_t *known, const World *w){
#if TYPED
  int fa[NA], oa[GOAL_COUNT];
  int nf = known ? atoms_from_known(known, fa) : 0;
  int no = (w && known) ? obligs_from_goals(w, known, oa) : 0;
#else
  (void)w;
#endif
  if (scorer == SC_MODEL_RAW || scorer == SC_UNTRAINED){
    const Params *mp = (scorer == SC_UNTRAINED) ? g_untrained : p;
#if TYPED
    model_forward_typed(mp, state, cf, nlive, live, fa, nf, oa, no, (const double*)0, g_c);
#else
    (void)live; (void)known; (void)w;
    model_forward_z(mp, state, cf, nlive, z, g_c);
#endif
    ctr->forwards++;
    for (int j = 0; j < nlive; j++) out[j] = g_c->score[j];
    return 1;
  }
  if (scorer == SC_MODEL_LOGP){
#if TYPED
    model_forward_typed(p, state, cf, nlive, live, fa, nf, oa, no, (const double*)0, g_c);
#else
    model_forward_z(p, state, cf, nlive, z, g_c);
#endif
    ctr->forwards++;
    double mx = -1e30;
    for (int j = 0; j < nlive; j++) if (g_c->score[j] > mx) mx = g_c->score[j];
    double z = 0;
    for (int j = 0; j < nlive; j++) z += exp(g_c->score[j] - mx);
    for (int j = 0; j < nlive; j++)
      out[j] = (g_c->score[j] - mx) - log(z);
    return 1;
  }
  for (int j = 0; j < nlive; j++){
    if (scorer == SC_SUPPORT) out[j] = cf[j][3] + 0.5*cf[j][5];
    else if (scorer == SC_PRIOR){
      int head = 0;
      for (int q = 0; q < HP; q++) if (cf[j][8+q] > 0.5) head = q;
      out[j] = g_head_prior[head] - 0.2*2.0*cf[j][1];
    } else out[j] = (double)randbelow(1000);
  }
  return 0;
}

static void policy_world_beam(const World *w, const Params *p, int scorer, uint64_t seed,
                              int *goals_proved, int *full_success, Counters *ctr){
  enum { BW = 32, MAXSEQ = SEED_RULES + MAXBUDGET, MAXC = BW*BW };
  int W = g_beam; if (W > BW) W = BW;
  static double state[STATE_DIM];
  static double cf2[POOL][CAND_DIM];
  static double util[POOL];
  int seq[BW][MAXSEQ];
  int seqn[BW];
  double score[BW];
#if LOOPCELL
  static double bz[BW][D], bz2[MAXC][D];
  for (int d = 0; d < D; d++) bz[0][d] = p->z0[d];
#endif
  int nW = 1;
  seqn[0] = SEED_RULES;
  for (int k = 0; k < SEED_RULES; k++) seq[0][k] = w->theory[k];
  score[0] = 0.0;
  rng_state = seed | 1ULL;
  for (int d = 0; d < g_eval_budget; d++){
    int nseq[MAXC]; int ns2[MAXC][MAXSEQ]; double sc2[MAXC];
    int n2 = 0;
    for (int bi = 0; bi < nW; bi++){
      int nrules = seqn[bi];
      int live[POOL], nlive = 0;
      for (int c = 0; c < POOL; c++){
        int r = w->cands[c], u = 0;
        for (int k = 0; k < nrules; k++) if (seq[bi][k] == r) u = 1;
        if (!u) live[nlive++] = r;
      }
      if (!nlive) continue;
      uint8_t known[WENT];
      {
        closure(w->facts, seq[bi], nrules, known);
        nlive = focus_filter(w, known, live, nlive);  /* Rocq obligation focus */
        pc_filter(known, live, &nlive);               /* Silicon path condition */
      }
      if (!nlive) continue;
      step_features(w, seq[bi], nrules, live, nlive, state, cf2, util, g_eval_budget - d);
      double sc[POOL];
      score_candidates(scorer, p, state, (const double (*)[CAND_DIM])cf2, nlive, sc, ctr,
#if LOOPCELL
                       bz[bi],
#else
                       (const double*)0,
#endif
                       live, known, w);
      ctr->states++;
      ctr->cands += nlive;
#if ASSERT
      {
        AssertCtx ax;
        assert_ctx(w, seq[bi], nrules, live, nlive, known, &ax);
        int a_star = assert_top(&ax, g_c->prop, g_eval_budget - d);
        int focal[POOL], nf = assert_focus_filter(w, &ax, a_star, live, nlive, focal);
        g_assert_states++;
        if (a_star >= 0) g_assert_adopt++; else g_assert_fallback++;
        if (nf > 0){
          int nn = 0;
          for (int k = 0; k < nlive; k++){
            int inf = 0;
            for (int q = 0; q < nf; q++) if (focal[q] == live[k]) inf = 1;
            if (inf) live[nn++] = live[k];
          }
          nlive = nn;
        }
      }
#endif
      int order[POOL];
      for (int k = 0; k < nlive; k++) order[k] = k;
      for (int k = 0; k < nlive; k++)
        for (int j = k+1; j < nlive; j++)
          if (sc[order[j]] > sc[order[k]]){ int t = order[k]; order[k] = order[j]; order[j] = t; }
      for (int e = 0; e < nlive && e < W; e++){
        int k = order[e];
        for (int q = 0; q < nrules; q++) ns2[n2][q] = seq[bi][q];
        ns2[n2][nrules] = live[k];
        nseq[n2] = nrules + 1;
        sc2[n2] = score[bi] + sc[k];
#if LOOPCELL
        { double ea[D]; CellCache cc;
          action_embed(p, cf2[k], ea);
          if (CELLDETACH) for (int q = 0; q < D; q++) bz2[n2][q] = p->z0[q];
          else cell_fwd(p, bz[bi], ea, bz2[n2], &cc); }
#endif
        n2++;
      }
    }
    if (!n2) break;
    for (int i = 0; i < n2; i++)
      for (int j = i+1; j < n2; j++)
        if (sc2[j] > sc2[i]){
          double t = sc2[i]; sc2[i] = sc2[j]; sc2[j] = t;
          int tn = nseq[i]; nseq[i] = nseq[j]; nseq[j] = tn;
          for (int q = 0; q < MAXSEQ; q++){ int x = ns2[i][q]; ns2[i][q] = ns2[j][q]; ns2[j][q] = x; }
#if LOOPCELL
          for (int q = 0; q < D; q++){ double x = bz2[i][q]; bz2[i][q] = bz2[j][q]; bz2[j][q] = x; }
#endif
        }
    nW = (n2 < W) ? n2 : W;
    for (int i = 0; i < nW; i++){
      score[i] = sc2[i];
      seqn[i] = nseq[i];
      for (int q = 0; q < MAXSEQ; q++) seq[i][q] = ns2[i][q];
#if LOOPCELL
      for (int q = 0; q < D; q++) bz[i][q] = bz2[i][q];
#endif
    }
  }
  int bestgp = -1, bestfull = 0;
  for (int i = 0; i < nW; i++){
    uint8_t known[WENT];
    closure(w->facts, seq[i], seqn[i], known);
    ctr->closes++;
    int gp = 0;
    for (int g = 0; g < w->ngoals; g++)
      if (GOAL_KNOWN(w,g,known)) gp++;
    int full = (gp == w->ngoals) ? 1 : 0;
    if (full > bestfull || (full == bestfull && gp > bestgp)){ bestfull = full; bestgp = gp; }
  }
  if (bestgp < 0){ bestgp = 0; }
  *goals_proved = bestgp;
  *full_success = bestfull;
}

/* per-world outcomes for the matched-search comparison (paired bootstrap) */
#define MAXSEEDS 16
static int g_wgoals[MAXSEEDS][NSCORE][512];
static int g_wfull[MAXSEEDS][NSCORE][512];
/* ---- permutation invariance check ---- */
static double permutation_invariance(void){
  const WSteps *ws = &g_data[2][0];
  if (ws->nsteps == 0) return 1e9;
  const RStep *rs = &ws->st[0];
  static double s1[POOL], s2[POOL];
  static double cf[POOL][CAND_DIM];
  for (int k = 0; k < rs->nlive; k++) for (int d = 0; d < CAND_DIM; d++) cf[k][d] = rs->cf[k][d];
#if TYPED
  {
    int lv[POOL], fa[NA], oa[GOAL_COUNT], fb[NA];
    for (int k = 0; k < rs->nlive; k++) lv[k] = rs->live[k];
    for (int f = 0; f < rs->nfact; f++) fa[f] = rs->fatoms[f];
    for (int o = 0; o < rs->nobl; o++) oa[o] = rs->oatoms[o];
    model_forward_typed(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, lv,
                        fa, rs->nfact, oa, rs->nobl, (const double*)0, g_c);
    for (int k = 0; k < rs->nlive; k++) s1[k] = g_c->score[k];
    for (int k = 0; k < rs->nlive; k++)
      for (int d = 0; d < CAND_DIM; d++) cf[k][d] = rs->cf[rs->nlive-1-k][d];
    for (int k = 0; k < rs->nlive; k++) lv[k] = rs->live[rs->nlive-1-k];
    for (int f = 0; f < rs->nfact; f++) fb[f] = rs->fatoms[rs->nfact-1-f];  /* fact order too */
    model_forward_typed(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, lv,
                        fb, rs->nfact, oa, rs->nobl, (const double*)0, g_c);
    for (int k = 0; k < rs->nlive; k++) s2[k] = g_c->score[rs->nlive-1-k];
  }
#else
#if TYPED
  model_forward_typed(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, rs->live,
                      rs->fatoms, rs->nfact, rs->oatoms, rs->nobl, (const double*)0, g_c);
#else
  model_forward(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, g_c);
#endif
  for (int k = 0; k < rs->nlive; k++) s1[k] = g_c->score[k];
  for (int k = 0; k < rs->nlive; k++)
    for (int d = 0; d < CAND_DIM; d++) cf[k][d] = rs->cf[rs->nlive-1-k][d];
#if TYPED
  model_forward_typed(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, rs->live,
                      rs->fatoms, rs->nfact, rs->oatoms, rs->nobl, (const double*)0, g_c);
#else
  model_forward(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, g_c);
#endif
  for (int k = 0; k < rs->nlive; k++) s2[k] = g_c->score[rs->nlive-1-k];
#endif
  double mx = 0;
  for (int k = 0; k < rs->nlive; k++){
    double d = fabs(s1[k] - s2[k]);
    if (d > mx) mx = d;
  }
#if LOOPCELL
  { /* episode-level equivariance: permute candidates consistently at EVERY
     * step (live/cf/util/best remapped); the latent chain and the episode
     * scalar must be invariant, not just the root-state scores */
    static WSteps wp;
    static double es1[NSTEPS][POOL];
    wp.w = ws->w; wp.nsteps = ws->nsteps;
    for (int t = 0; t < ws->nsteps; t++){
      const RStep *r0 = &ws->st[t]; RStep *rp = &wp.st[t];
      rp->nlive = r0->nlive; rp->reward_pos = r0->reward_pos;
#if TYPED
      rp->nfact = r0->nfact; rp->nobl = r0->nobl;
      for (int f = 0; f < r0->nfact; f++) rp->fatoms[f] = r0->fatoms[f];
      for (int o = 0; o < r0->nobl; o++) rp->oatoms[o] = r0->oatoms[o];
#endif
      for (int d = 0; d < STATE_DIM; d++) rp->state[d] = r0->state[d];
      for (int k = 0; k < r0->nlive; k++){
        int rk = r0->nlive-1-k;
        rp->live[k] = r0->live[rk];
        for (int d = 0; d < CAND_DIM; d++) rp->cf[k][d] = r0->cf[rk][d];
        rp->util[k] = r0->util[rk];
      }
      rp->best = r0->nlive-1-r0->best;
    }
    double l1 = episode_forward(g_p, ws, 0);
    for (int t = 0; t < ws->nsteps; t++)
      for (int k = 0; k < ws->st[t].nlive; k++) es1[t][k] = g_epc[t].score[k];
    double l2 = episode_forward(g_p, &wp, 0);
    if (fabs(l1-l2) > mx) mx = fabs(l1-l2);
    for (int t = 0; t < ws->nsteps; t++)
      for (int k = 0; k < ws->st[t].nlive; k++){
        double d = fabs(es1[t][k] - g_epc[t].score[ws->st[t].nlive-1-k]);
        if (d > mx) mx = d;
      }
  }
#endif
  return mx;
}

/* ---- training ---- */
static void train_seed(int seed, int epochs){
#if TYPEDSHUF
  factperm_init();
#endif
  init_params(g_p, (uint64_t)seed);
  Params *best = (Params*)calloc(1, sizeof(Params));
  if (!best){ fprintf(stderr, "alloc\n"); exit(2); }
  memset(g_g, 0, sizeof(Params));
  memset(g_m, 0, sizeof(Params));
  memset(g_v, 0, sizeof(Params));
  *best = *g_p;
  Metrics vm;
  eval_steps(best, 1, &vm);
  double best_val = vm.top1;
  /* sample selection: 0 = every collected state, 1 = root state only,
   * 2 = root-count subsample of every collected state (exposure-matched). */
  long n_all = g_nsteps[0];
  long n_root = 0;
  for (int i = 0; i < g_nw[0]; i++) if (g_data[0][i].nsteps > 0) n_root++;
  long ntr = (g_sample == 0) ? n_all : n_root;
  int *idx = (int*)calloc((size_t)n_all, sizeof(int));
  int *idx_root = (int*)calloc((size_t)(n_root > 0 ? n_root : 1), sizeof(int));
  if (!idx || !idx_root){ fprintf(stderr, "alloc\n"); exit(2); }
  long flat = 0, fr = 0;
  for (int i = 0; i < g_nw[0]; i++){
    for (int s = 0; s < g_data[0][i].nsteps; s++){
      idx[flat++] = i * 1000 + s;
      if (s == 0 && fr < n_root) idx_root[fr++] = i * 1000;
    }
  }
  if (g_sample == 1) for (long i = 0; i < ntr; i++) idx[i] = idx_root[i];
  if (g_balance){
    /* keep every reward-bearing state, then fill the rest deterministically so
     * that the number of training samples (and therefore updates) is unchanged.
     * This equalises goal-reward label exposure across collection modes. */
    int *bal = (int*)calloc((size_t)n_all, sizeof(int));
    if (!bal){ fprintf(stderr, "alloc\n"); exit(2); }
    long nb = 0, npos = 0;
    for (long i = 0; i < n_all; i++){
      int wi = idx[i] / 1000, si = idx[i] % 1000;
      if (g_data[0][wi].st[si].reward_pos){ bal[nb++] = idx[i]; npos++; }
    }
    for (long i = 0; i < n_all && nb < ntr; i++){
      int wi = idx[i] / 1000, si = idx[i] % 1000;
      if (!g_data[0][wi].st[si].reward_pos) bal[nb++] = idx[i];
    }
    for (long i = 0; i < ntr && i < nb; i++) idx[i] = bal[i];
    fprintf(stderr, "BALANCE train_samples=%ld reward_states=%ld total_states=%ld\n", ntr, npos, n_all);
    free(bal);
  }
#if EPTRAIN || LOOPCELL || TYPED
  /* episode-batched protocol (0.0269): shuffle WORLDS, batch EPB worlds per
   * update, average the gradient over the states in the batch. Every 0269 arm
   * uses this schedule so cell-vs-baseline contrasts are protocol-matched.
   * --balance-reward is a no-op here: every collected state is already used. */
  {
    enum { EPB = 8 };
    int nw = (int)g_nw[0];
    int *widx = (int*)calloc((size_t)(nw > 0 ? nw : 1), sizeof(int));
    if (!widx){ fprintf(stderr, "alloc\n"); exit(2); }
    for (int i = 0; i < nw; i++) widx[i] = i;
    printf("EPTRAIN episodes=%d epbatch=%d updates_per_epoch=%ld balance_noop=%d\n",
           nw, EPB, (long)((nw + EPB - 1)/EPB), g_balance ? 1 : 0);
    int t = 0;
    for (int ep = 0; ep < epochs; ep++){
      for (int i = nw-1; i > 0; i--){
        int j = randbelow(i+1);
        int tmp = widx[i]; widx[i] = widx[j]; widx[j] = tmp;
      }
      for (int b = 0; b < nw; b += EPB){
        memset(g_g, 0, sizeof(Params));
        long nst = 0;
        for (int k = b; k < b + EPB && k < nw; k++){
          const WSteps *ws = &g_data[0][widx[k]];
          episode_forward(g_p, ws, 1);
          episode_backward(ws);
          nst += ws->nsteps;
        }
        if (nst){
          double inv = 1.0/(double)nst;
          double *gg = pv(g_g);
          long np = param_count();
          for (long q = 0; q < np; q++) gg[q] *= inv;
          t++;
          adam_update(g_p, g_g, g_m, g_v, t);
        }
      }
      eval_steps(g_p, 1, &vm);
      if (vm.top1 > best_val){ best_val = vm.top1; *best = *g_p; }
#if ASSERT
      if (ASSERTW > 0 && (ep % 10 == 0 || ep == epochs-1))
        assert_report(g_p, 0, "TRAIN");
#endif
#if LOOPCELL
      if (PREDW > 0 && (ep % 10 == 0 || ep == epochs-1)){
        /* world-model learning curve on TRAIN episodes (directional evidence
         * that the auxiliary objective is actually being optimised) */
        double mse = 0; long n = 0;
        for (int i = 0; i < g_nw[0] && i < 40; i++){
          const WSteps *ws = &g_data[0][i];
          double z[D];
          for (int d = 0; d < D; d++) z[d] = g_p->z0[d];
          for (int t = 0; t < ws->nsteps; t++){
            const RStep *rs = &ws->st[t];
            double ea[D], th[D], x[2*D];
            action_embed(g_p, rs->cf[rs->best], ea);
            if (t+1 < ws->nsteps){
              double tgt = ep_maxutil(&ws->st[t+1]);
              double v = pred_fwd(g_p, z, ea, th, x);
              mse += (v-tgt)*(v-tgt); n++;
            }
            if (!CELLDETACH) cell_fwd(g_p, z, ea, z, &g_evalcell);
          }
        }
        printf("PRED-TRAIN ep=%d mse=%.4f n=%ld val_top1=%.4f\n", ep, n ? mse/(double)n : 0, n, vm.top1);
      }
#endif
    }
    free(widx);
  }
#else
  int t = 0;
  for (int ep = 0; ep < epochs; ep++){
    /* deterministic shuffle; the exposure-matched arm shuffles every collected
     * state and uses the first ntr, so update count stays identical */
    long shuf_n = (g_sample == 2) ? n_all : ntr;
    for (long i = shuf_n-1; i > 0; i--){
      int j = randbelow((int)(i+1));
      int tmp = idx[i]; idx[i] = idx[j]; idx[j] = tmp;
    }
    double ep_loss = 0;
    for (long b = 0; b < ntr; b += BATCH){
      memset(g_g, 0, sizeof(Params));
      int nb = 0;
      for (long k = b; k < b + BATCH && k < ntr; k++){
        int wi = idx[k] / 1000, si = idx[k] % 1000;
        const RStep *rs = &g_data[0][wi].st[si];
        ep_loss += model_step(rs->state, (const double (*)[CAND_DIM])rs->cf,
                              (const int*)0, rs->best, rs->util, rs->nlive);
        nb++;
      }
      if (nb){
        double inv = 1.0/(double)nb;      /* batch-mean gradient (M1 objective) */
        double *gg = pv(g_g);
        long np = param_count();
        for (long k = 0; k < np; k++) gg[k] *= inv;
        t++;
        adam_update(g_p, g_g, g_m, g_v, t);
      }
    }
    eval_steps(g_p, 1, &vm);
    if (vm.top1 > best_val){ best_val = vm.top1; *best = *g_p; }
  }
#endif
  *g_p = *best;
#if LOOPCELL
  pred_val_report(g_p);
#endif
#if ASSERT
  assert_report(g_p, 0, "FINAL-TRAIN");
  assert_report(g_p, 1, "VAL");
#endif
  free(best);
  free(idx);
  free(idx_root);
}

#if ASSERT
/* kernel-judged proposal quality: top-1 adoption rate + rejection reasons */
static void assert_report(const Params *p, int split, const char *tag){
  long n = 0, adopt = 0, r_known = 0, r_irrel = 0, r_unreach = 0, r_deep = 0;
  for (int i = 0; i < g_nw[split]; i++){
    const WSteps *ws = &g_data[split][i];
    int rules[MAXRULE];
    int nr = 0;
    for (int q = 0; q < SEED_RULES; q++) rules[nr++] = ws->w.theory[q];
    for (int t = 0; t < ws->nsteps; t++){
      const RStep *rs = &ws->st[t];
      uint8_t kn[WENT];
      closure(ws->w.facts, rules, nr, kn);
      model_forward_typed(p, rs->state, rs->cf, rs->nlive, rs->live,
                          rs->fatoms, rs->nfact, rs->oatoms, rs->nobl, (const double*)0, g_c);
      AssertCtx ax;
      assert_ctx(&ws->w, rules, nr, rs->live, rs->nlive, kn, &ax);
      int rem = g_label_rem_max - t; if (rem < 0) rem = 0;
      /* the model proposes UNCONDITIONALLY (argmax over all atoms); the
       * kernel then accepts or rejects — that verdict is the learning signal */
      int best = 0;
      for (int a = 1; a < NA; a++) if (g_c->prop[a] > g_c->prop[best]) best = a;
      int why;
      int ok = assert_adopt(&ax, best, rem, &why);
      for (int a = 0; a < NA; a++){
        int w2;
        if (!assert_adopt(&ax, a, rem, &w2)){
          if (w2 == 0) r_known++; else if (w2 == 1) r_irrel++;
          else if (w2 == 2) r_unreach++; else r_deep++;
        }
      }
      n++;
      if (ok) adopt++;
      rules[nr++] = rs->live[rs->best];
    }
  }
  printf("ASSERT-%s states=%ld top1_adopt=%.4f reject_known=%ld reject_irrel=%ld reject_unreach=%ld reject_deep=%ld\n",
         tag, n, n ? (double)adopt/(double)n : 0, r_known, r_irrel, r_unreach, r_deep);
}
#endif

/* ---- reporting ---- */
static void head_prior_from_train(void){
  double sums[P] = {0}, counts[P] = {0};
  for (int i = 0; i < g_nw[0]; i++)
    for (int s = 0; s < g_data[0][i].nsteps; s++){
      const RStep *rs = &g_data[0][i].st[s];
      for (int k = 0; k < rs->nlive; k++){
        int head = 0;
        for (int q = 0; q < HP; q++) if (rs->cf[k][8+q] > 0.5) head = q;
        sums[head] += rs->util[k];
        counts[head] += 1;
      }
    }
  for (int q = 0; q < P; q++) g_head_prior[q] = counts[q] ? sums[q]/counts[q] : 0.0;
}

/* per-rule prior = mean utility over TRAIN states where the rule was live
 * (0243-style empirical prior, finer than the per-head prior). Train split only:
 * no val/test leakage. PRIOR_SHUF deranges the assignment (offset 37, coprime
 * with 90) to destroy rule identity while preserving the value distribution. */
static void rule_prior_from_train(void){
  double sums[NRULES_ALL] = {0}, counts[NRULES_ALL] = {0};
  for (int i = 0; i < g_nw[0]; i++)
    for (int s = 0; s < g_data[0][i].nsteps; s++){
      const RStep *rs = &g_data[0][i].st[s];
      for (int k = 0; k < rs->nlive; k++){
        int rid = rs->live[k];
        sums[rid] += rs->util[k];
        counts[rid] += 1;
      }
    }
  for (int r = 0; r < NRULES_ALL; r++) g_rule_prior[r] = counts[r] ? sums[r]/counts[r] : 0.0;
#if PRIOR_SHUF
  { double tmp[NRULES_ALL];
    for (int r = 0; r < NRULES_ALL; r++) tmp[r] = g_rule_prior[(r+37)%NRULES_ALL];
    for (int r = 0; r < NRULES_ALL; r++) g_rule_prior[r] = tmp[r]; }
#endif
#if INTEGRAL
  /* patch the stored dataset prior column now that the prior exists (utilities
   * are prior-independent, so this is a clean two-pass fill, no circularity) */
  for (int s = 0; s < 3; s++)
    for (int i = 0; i < g_nw[s]; i++)
      for (int q = 0; q < g_data[s][i].nsteps; q++){
        RStep *rs = &g_data[s][i].st[q];
        for (int k = 0; k < rs->nlive; k++) rs->cf[k][PATH_OFF+2] = g_rule_prior[rs->live[k]];
      }
#endif
}

/* ---- exact first-step regret (discovery criterion) ------------------------
 * For every live candidate at the root state, Q(a) = max goals reachable with
 * the remaining budget (a plus up to budget-1 further rules). The exact optimum
 * is available because the fixture is finite (<=24 candidates, budget <=4).
 * regret = max_a Q(a) - Q(chosen); optimal = Q(chosen) == max_a Q(a).
 * This separates action quality from state reachability: a policy can reach few
 * goals because it chose badly (high regret) or because the state is bad. */
static int q_closure_goals(const World *w, const int *rules, int nrules, const int *extra, int nx){
  int all[SEED_RULES + MAXBUDGET + 4];
  int m = 0;
  for (int i = 0; i < nrules; i++) all[m++] = rules[i];
  for (int i = 0; i < nx; i++) all[m++] = extra[i];
  uint8_t known[WENT];
  closure(w->facts, all, m, known);
  int gp = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (GOAL_KNOWN(w,g,known)) gp++;
  return gp;
}

/* Q for every live candidate; budget = total actions available from here */
static void q_actions(const World *w, const int *rules, int nrules,
                      const int *live, int nlive, int budget, int *q){
  int extra[MAXBUDGET + 4];
  for (int a = 0; a < nlive; a++){
    int best = q_closure_goals(w, rules, nrules, &live[a], 1);
    int rem = budget - 1;
    if (rem >= 1){
      for (int b = 0; b < nlive; b++){
        if (b == a) continue;
        extra[0] = live[a]; extra[1] = live[b];
        int v = q_closure_goals(w, rules, nrules, extra, 2);
        if (v > best) best = v;
      }
    }
    if (rem >= 2){
      for (int b = 0; b < nlive; b++){
        if (b == a) continue;
        for (int c = b+1; c < nlive; c++){
          if (c == a) continue;
          extra[0] = live[a]; extra[1] = live[b]; extra[2] = live[c];
          int v = q_closure_goals(w, rules, nrules, extra, 3);
          if (v > best) best = v;
        }
      }
    }
    if (rem >= 3){
      for (int b = 0; b < nlive; b++){
        if (b == a) continue;
        for (int c = b+1; c < nlive; c++){
          if (c == a) continue;
          for (int d = c+1; d < nlive; d++){
            if (d == a) continue;
            extra[0] = live[a]; extra[1] = live[b]; extra[2] = live[c]; extra[3] = live[d];
            int v = q_closure_goals(w, rules, nrules, extra, 4);
            if (v > best) best = v;
          }
        }
      }
    }
    q[a] = best;
  }
}

/* Step-indexed optimality along the model's OWN greedy trajectory: at each step
 * the exact Q (remaining budget) is computed over live candidates, so we can see
 * whether the failure starts at step 1 (scorer) or later (compounding). */
static void traj_profile(int seed){
  int nstep = g_eval_budget;
  long opt[MAXBUDGET], tot[MAXBUDGET], setsz[MAXBUDGET];
  double reg[MAXBUDGET];
  for (int i = 0; i < MAXBUDGET; i++){ opt[i]=0; tot[i]=0; setsz[i]=0; reg[i]=0; }
  static double state[STATE_DIM];
  static double cf2[POOL][CAND_DIM];
  static double util[POOL];
  int q[POOL];
  for (int w = 0; w < g_nw[2]; w++){
    const World *wd = &g_data[2][w].w;
    int rules[MAXRULE];
    int nrules = SEED_RULES;
    for (int k = 0; k < SEED_RULES; k++) rules[k] = wd->theory[k];
    for (int st = 0; st < nstep; st++){
      int live[POOL], nlive = 0;
      for (int c = 0; c < POOL; c++){
        int r = wd->cands[c], used = 0;
        for (int k = 0; k < nrules; k++) if (rules[k] == r) used = 1;
        if (!used) live[nlive++] = r;
      }
      if (!nlive) break;
      step_features(wd, rules, nrules, live, nlive, state, cf2, util, nstep - st);
#if TYPED
      { uint8_t kn[WENT]; int fa[NA], oa[GOAL_COUNT];
        closure(wd->facts, rules, nrules, kn);
        model_forward_typed(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, live,
                            fa, atoms_from_known(kn, fa), oa, obligs_from_goals(wd, kn, oa),
                            (const double*)0, g_c); }
#else
      model_forward(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, g_c);
#endif
      int pick = 0;
      for (int a = 1; a < nlive; a++) if (g_c->score[a] > g_c->score[pick]) pick = a;
      int rem = nstep - st;
      q_actions(wd, rules, nrules, live, nlive, rem, q);
      int qmax = q[0], nopt = 0;
      for (int a = 1; a < nlive; a++) if (q[a] > qmax) qmax = q[a];
      for (int a = 0; a < nlive; a++) if (q[a] == qmax) nopt++;
      tot[st]++;
      if (q[pick] == qmax) opt[st]++;
      setsz[st] += nopt;
      reg[st] += (double)(qmax - q[pick]);
      rules[nrules++] = live[pick];
    }
  }
  for (int st = 0; st < nstep; st++){
    if (!tot[st]) continue;
    printf("TRAJ seed=%d step=%d opt=%.4f optset=%.2f regret=%.4f worlds=%ld depth=%d budget=%d\n",
           seed, st+1, (double)opt[st]/(double)tot[st], (double)setsz[st]/(double)tot[st],
           reg[st]/(double)tot[st], tot[st],
           (g_goaldepth > 0 ? g_goaldepth : 2), g_eval_budget);
  }
}

/* first-action regret for the model, the support heuristic and utility_greedy */
static void first_step_regret(double *r_model, double *h_model,
                              double *r_sup, double *h_sup,
                              double *r_ug, double *h_ug){
  double rm = 0, hm = 0, rs = 0, hs = 0, ru = 0, hu = 0;
  long n = 0;
  static double state[STATE_DIM];
  static double cf2[POOL][CAND_DIM];
  static double util[POOL];
  int q[POOL];
  for (int i = 0; i < g_nw[2]; i++){
    const World *w = &g_data[2][i].w;
    int rules[SEED_RULES];
    for (int k = 0; k < SEED_RULES; k++) rules[k] = w->theory[k];
    int live[POOL], nlive = 0;
    for (int c = 0; c < POOL; c++){
      int used = 0;
      for (int k = 0; k < SEED_RULES; k++) if (rules[k] == w->cands[c]) used = 1;
      if (!used) live[nlive++] = w->cands[c];
    }
    if (!nlive) continue;
    step_features(w, rules, SEED_RULES, live, nlive, state, cf2, util, g_eval_budget);
#if TYPED
    { uint8_t kn[WENT]; int fa[NA], oa[GOAL_COUNT];
      closure(w->facts, rules, SEED_RULES, kn);
      model_forward_typed(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, live,
                          fa, atoms_from_known(kn, fa), oa, obligs_from_goals(w, kn, oa),
                          (const double*)0, g_c); }
#else
    model_forward(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, g_c);
#endif
    int am = 0, asup = 0, aug = 0;
    for (int a = 1; a < nlive; a++){
      if (g_c->score[a] > g_c->score[am]) am = a;
      if (cf2[a][3] + 0.5*cf2[a][5] > cf2[asup][3] + 0.5*cf2[asup][5]) asup = a;
      if (util[a] > util[aug]) aug = a;
    }
    q_actions(w, rules, SEED_RULES, live, nlive, g_eval_budget, q);
    int qmax = q[0];
    for (int a = 1; a < nlive; a++) if (q[a] > qmax) qmax = q[a];
    rm += qmax - q[am]; hm += (q[am] == qmax) ? 1 : 0;
    rs += qmax - q[asup]; hs += (q[asup] == qmax) ? 1 : 0;
    ru += qmax - q[aug]; hu += (q[aug] == qmax) ? 1 : 0;
    n++;
  }
  *r_model = n ? rm/n : 0; *h_model = n ? hm/n : 0;
  *r_sup = n ? rs/n : 0;   *h_sup = n ? hs/n : 0;
  *r_ug = n ? ru/n : 0;    *h_ug = n ? hu/n : 0;
}

/* ---- query server: the C model scores a proof state on demand ----------
 * One line per query on stdin:   <world> <nrules> <r1> ... <rn>
 * One line per reply on stdout:  <nlive> <id> <score> <id> <score> ...
 * Used to drive an external (Common Lisp / Screamer) backtracking search with
 * the native transformer as the ordering heuristic. */
static void serve(void){
  static double state[STATE_DIM];
  static double cf2[POOL][CAND_DIM];
  static double util[POOL];
  char line[8192];
  while (fgets(line, sizeof line, stdin)){
    int w = 0, n = 0, rules[SEED_RULES + MAXBUDGET + 8];
    char *p = line;
    w = (int)strtol(p, &p, 10);
    n = (int)strtol(p, &p, 10);
    if (w < 0 || w >= g_nw[2] || n < 0 || n > SEED_RULES + MAXBUDGET){ printf("0\n"); fflush(stdout); continue; }
    for (int i = 0; i < n; i++) rules[i] = (int)strtol(p, &p, 10);
    const World *wd = &g_data[2][w].w;
    int live[POOL], nlive = 0;
    for (int c = 0; c < POOL; c++){
      int used = 0;
      for (int k = 0; k < n; k++) if (rules[k] == wd->cands[c]) used = 1;
      if (!used) live[nlive++] = wd->cands[c];
    }
    if (!nlive){ printf("0\n"); fflush(stdout); continue; }
    step_features(wd, rules, n, live, nlive, state, cf2, util,
                  g_eval_budget - (n - SEED_RULES) > 0 ? g_eval_budget - (n - SEED_RULES) : 0);
#if TYPED
    { uint8_t kn[WENT]; int fa[NA], oa[GOAL_COUNT];
      closure(wd->facts, rules, n, kn);
      model_forward_typed(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, live,
                          fa, atoms_from_known(kn, fa), oa, obligs_from_goals(wd, kn, oa),
                          (const double*)0, g_c); }
#else
    model_forward(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, g_c);
#endif
    printf("%d", nlive);
    for (int a = 0; a < nlive; a++) printf(" %d %.9f", live[a], g_c->score[a]);
    printf("\n");
    fflush(stdout);
  }
}

static int g_emit_worlds = 0;

static void policy_metrics(const Params *p, int split, int mode,
                           double *proved, double *full){
  long gp = 0, gt = 0, fs = 0, nw = 0;
  for (int i = 0; i < g_nw[split]; i++){
    const World *w = &g_data[split][i].w;
    int g1 = 0, st1 = 0, f1 = 0;
    policy_world(w, p, mode, (uint64_t)(1000+i), &g1, &st1, &f1);
    gp += g1; gt += w->ngoals; fs += f1; nw++;
  }
  *proved = gt ? (double)gp/(double)gt : 0.0;
  *full = nw ? (double)fs/(double)nw : 0.0;
}

/* paired world bootstrap, two labelled estimators (R245-5):
 *   ratio = total goals of a / total goals available (the headline coverage),
 *   macro = mean over worlds of the per-world goal fraction.
 * Full-success differences are the world mean. */
static void bootstrap_beam_diff(int seeds, int a, int b,
                                double *rlo, double *rhi, double *mlo, double *mhi,
                                double *flo, double *fhi){
  enum { NB = 3000 };
  int nw = g_nw[2];
  static double dg[512], df[512], rt[512], bs[3][NB];
  for (int i = 0; i < nw; i++){
    double ga = 0, gb = 0, fa = 0, fb = 0;
    for (int si = 0; si < seeds; si++){
      int gt = g_data[2][i].w.ngoals;
      ga += gt ? (double)g_wgoals[si][a][i]/(double)gt : 0.0;
      gb += gt ? (double)g_wgoals[si][b][i]/(double)gt : 0.0;
      fa += g_wfull[si][a][i];
      fb += g_wfull[si][b][i];
    }
    dg[i] = (ga - gb)/(double)seeds;
    df[i] = (fa - fb)/(double)seeds;
    rt[i] = (double)g_data[2][i].w.ngoals;
  }
  uint64_t st = 0xB0075EEDULL ^ (uint64_t)(a*97 + b);
  for (int r = 0; r < NB; r++){
    double sg = 0, sf = 0, ra = 0, rb = 0, tt = 0;
    for (int i = 0; i < nw; i++){
      st = mix64(st);
      int j = (int)(st % (uint64_t)nw);
      sg += dg[j]; sf += df[j];
      for (int si = 0; si < seeds; si++){
        ra += g_wgoals[si][a][j]; rb += g_wgoals[si][b][j];
      }
      tt += rt[j]*(double)seeds;
    }
    bs[0][r] = tt > 0 ? (ra - rb)/tt : 0.0;   /* total-goal ratio */
    bs[1][r] = sg/(double)nw;                 /* world-mean macro */
    bs[2][r] = sf/(double)nw;
  }
  for (int c = 0; c < 3; c++)
    for (int i = 0; i < NB; i++)
      for (int j = i+1; j < NB; j++)
        if (bs[c][j] < bs[c][i]){ double t = bs[c][i]; bs[c][i] = bs[c][j]; bs[c][j] = t; }
  *rlo = bs[0][(NB*25)/1000]; *rhi = bs[0][(NB*975)/1000];
  *mlo = bs[1][(NB*25)/1000]; *mhi = bs[1][(NB*975)/1000];
  *flo = bs[2][(NB*25)/1000]; *fhi = bs[2][(NB*975)/1000];
}



static void run_variant(int seeds, int epochs, int verbose){
  build_dataset();
  onpath_report();
  head_prior_from_train();
  rule_prior_from_train();
  if (g_dp_check){ dp_audit(); return; }
  g_untrained = (Params*)calloc(1, sizeof(Params));
  if (!g_untrained){ fprintf(stderr, "alloc\n"); exit(2); }
  init_params(g_untrained, 999);

  /* fixture-level budget-exact bound (seed independent) */
  double bound_goal = 0, bound_full = 0;
  long bound_gt = 0, bound_w = 0, bound_states = 0;
  static int bw_goals[512];
  if (g_no_bound){
    for (int i = 0; i < g_nw[2]; i++) bw_goals[i] = 99;   /* assertion disabled */
    bound_goal = -1.0; bound_full = -1.0;
  } else {
    for (int i = 0; i < g_nw[2]; i++){
      const World *w = &g_data[2][i].w;
      int bg = bound_world(w);
      bw_goals[i] = bg;
      bound_goal += bg; bound_gt += w->ngoals;
      if (bg == w->ngoals) bound_full += 1;
      bound_w++;
    }
    bound_goal = bound_gt ? bound_goal/(double)bound_gt : 0.0;
    bound_full = bound_w ? bound_full/(double)bound_w : 0.0;
  }

  if (g_onecommit_audit){
    int viol = 0, mx = 0;
    for (int i = 0; i < g_nw[2]; i++){
      const World *w = &g_data[2][i].w;
      int wmax = 0;
      for (int c = 0; c < POOL; c++){
        int rr[SEED_RULES+1];
        for (int k = 0; k < SEED_RULES; k++) rr[k] = w->theory[k];
        rr[SEED_RULES] = w->cands[c];
        uint8_t kn[WENT]; closure(w->facts, rr, SEED_RULES+1, kn);
        int gp1 = 0;
        for (int g = 0; g < w->ngoals; g++)
          if (GOAL_KNOWN(w,g,kn)) gp1++;
        if (gp1 > wmax) wmax = gp1;
      }
      if (wmax >= 2) viol++;
      if (wmax > mx) mx = wmax;
    }
    printf("ONECOMMIT-AUDIT worlds=%d max=%d violations=%d\n", g_nw[2], mx, viol);
  }

  enum { NAGG = 35 };
  double agg[NAGG];
  for (int i = 0; i < NAGG; i++) agg[i] = 0;
  Counters cinfo = {0,0,0,0};
  int bound_assert_ok = 1;
  long bound_pairs = 0, bound_viol = 0;

  for (int si = 0; si < seeds; si++){
    int seed = g_seed_base + si;
    rng_state = (uint64_t)(seed*7 + 1);
    /* R250-8: weights carry a config header so a stale .bin from a different
     * build (dims/flags/data protocol) is rejected instead of silently reused. */
    if (g_load_weights){
      FILE *lf = fopen(g_load_weights, "rb");
      if (!lf){ fprintf(stderr, "cannot open weights %s\n", g_load_weights); exit(2); }
      WHeader h;
      if (fread(&h, sizeof h, 1, lf) != 1){ fprintf(stderr, "short header\n"); exit(2); }
      if (h.magic != W_MAGIC || h.state_dim != STATE_DIM || h.cand_dim != CAND_DIM ||
          h.variant != NOUT || h.hard != HARD_GOALS || h.relob != RELOB || h.bindtok != BINDTOK ||
          h.integral != INTEGRAL || h.lifted != LIFTED || h.prior_shuf != PRIOR_SHUF ||
          h.holdout != g_holdout_mask || h.lift_rho != LIFT_RHO || h.path_gamma != PATH_GAMMA ||
          h.attmode != ATTMODE || h.symgate != SYMGATE || h.cert != CERT ||
          h.focus != FOCUS || h.lemma != LEMMA ||
          h.pairmode != PAIRMODE || h.pair_keep != g_pair_keep || h.valmode != VALMODE ||
          h.branchtok != BRANCHTOK || h.readmax != READMAX || h.regshuf != REGSHUF ||
          h.label_ncost != LABEL_NCOST || h.label_steps != LABEL_STEPS || h.label_rem != g_label_rem_max ||
          h.loopcell != LOOPCELL || h.celldetach != CELLDETACH || h.cellshuf != CELLSHUF ||
          h.remfeat != REMFEAT || h.eptrain != EPTRAIN || h.predw != (double)PREDW ||
          h.relatom != RELATOM || h.typed != TYPED || h.oblread != OBLREAD ||
          h.entfeat != ENTFEAT || h.typedshuf != TYPEDSHUF ||
          h.assertf != ASSERT || h.assertw != (double)ASSERTW || h.assertunion != ASSERTUNION ||
          h.md != D || h.mnl != NL || h.phaseuntie != PHASEUNTIE){
        fprintf(stderr, "WEIGHTS-MISMATCH %s\n", g_load_weights);
        fprintf(stderr, "  weights: dims %d/%d variant %d hard %d relob %d bindtok %d integral %d lifted %d holdout %d "
                        "attmode %d symgate %d cert %d focus %d lemma %d pairmode %d keep %d valmode %d "
                        "ncost %d steps %d label_rem %d branchtok %d readmax %d regshuf %d md %d nl %d untie %d "
                        "cell %d detach %d shuf %d remfeat %d eptrain %d predw %.3f assert %d assertw %.3f\n",
                h.state_dim, h.cand_dim, h.variant, h.hard, h.relob, h.bindtok,
                h.integral, h.lifted, h.holdout, h.attmode, h.symgate, h.cert, h.focus, h.lemma,
                h.pairmode, h.pair_keep, h.valmode,
                h.label_ncost, h.label_steps, h.label_rem,
                h.branchtok, h.readmax, h.regshuf, h.md, h.mnl, h.phaseuntie,
                h.loopcell, h.celldetach, h.cellshuf, h.remfeat, h.eptrain, h.predw, h.assertf, h.assertw);
        fprintf(stderr, "  binary : dims %d/%d variant %d hard %d relob %d bindtok %d integral %d lifted %d holdout %d "
                        "attmode %d symgate %d cert %d focus %d lemma %d pairmode %d keep %d valmode %d "
                        "ncost %d steps %d label_rem %d branchtok %d readmax %d regshuf %d md %d nl %d untie %d "
                        "cell %d detach %d shuf %d remfeat %d eptrain %d predw %.3f assert %d assertw %.3f\n",
                STATE_DIM, CAND_DIM, NOUT, HARD_GOALS, RELOB, BINDTOK,
                INTEGRAL, LIFTED, g_holdout_mask, ATTMODE, SYMGATE, CERT, FOCUS, LEMMA,
                PAIRMODE, g_pair_keep, VALMODE, LABEL_NCOST, LABEL_STEPS, g_label_rem_max,
                BRANCHTOK, READMAX, REGSHUF, D, NL, PHASEUNTIE,
                LOOPCELL, CELLDETACH, CELLSHUF, REMFEAT, EPTRAIN, (double)PREDW, ASSERT, (double)ASSERTW);
        exit(4);
      }
      if (fread(g_p, sizeof(Params), 1, lf) != 1){ fprintf(stderr, "short weights\n"); exit(2); }
      fclose(lf);
    } else {
      train_seed(seed, epochs);
      if (g_save_weights){
        FILE *sf = fopen(g_save_weights, "wb");
        if (!sf){ fprintf(stderr, "cannot write %s\n", g_save_weights); exit(2); }
        double pchk = 0;
        { double *pp = pv(g_p); long np = param_count(); for (long i = 0; i < np; i++) pchk += pp[i]*(double)(i % 97); }
        WHeader h = { W_MAGIC, STATE_DIM, CAND_DIM, NOUT, HARD_GOALS, RELOB, BINDTOK, g_goaldepth, g_eval_budget,
                      INTEGRAL, LIFTED, PRIOR_SHUF, g_holdout_mask,
                      ATTMODE, SYMGATE, CERT, FOCUS, LEMMA, PAIRMODE, g_pair_keep, VALMODE,
                      LABEL_NCOST, LABEL_STEPS, g_label_rem_max,
                      BRANCHTOK, READMAX, REGSHUF, D, NL, PHASEUNTIE,
                      LOOPCELL, CELLDETACH, CELLSHUF, REMFEAT, EPTRAIN, RELATOM, TYPED, OBLREAD, ENTFEAT, TYPEDSHUF, ASSERT, ASSERTUNION,
                      LIFT_RHO, PATH_GAMMA, (double)PREDW, (double)ASSERTW, pchk };
        fwrite(&h, sizeof h, 1, sf);
        fwrite(g_p, sizeof(Params), 1, sf);
        fclose(sf);
      }
    }
#if TYPEDSHUF
    factperm_init();
#endif
    if (g_pairmode == 1 && g_lemmas) lemma_mine();   /* hand-designed: teacher-rollout pairs */
    if (g_pairmode == 2) pair_learn();               /* learned: kernel-labelled pair scorer */
    g_pc_tokens = g_pc_dropped = g_pc_fallback = g_pc_picks = 0;
    g_cert_ok = g_cert_fail = g_cert_checked = g_cert_mutfail = 0;
    g_focus_states = g_focus_removed = 0;
#if ASSERT
    g_assert_states = g_assert_adopt = g_assert_fallback = g_assert_raw_adopt = 0;
#endif
    g_pair_uses = g_pair_viol = 0;
    Metrics m;
    eval_steps(g_p, 2, &m);

    double pm = 0, fm = 0, po = 0, fo = 0, ps = 0, fs = 0, pp = 0, fp = 0,
           pr = 0, fr = 0, pu = 0, fu = 0, psh = 0, fsh = 0;
    policy_metrics(g_p, 2, 0, &pm, &fm);
    policy_metrics(g_p, 2, 6, &po, &fo);   /* utility_greedy comparator */
    policy_metrics(g_p, 2, 1, &ps, &fs);
    policy_metrics(g_p, 2, 2, &pp, &fp);
    policy_metrics(g_p, 2, 3, &pr, &fr);
    policy_metrics(g_p, 2, 4, &pu, &fu);
    policy_metrics(g_p, 2, 5, &psh, &fsh);

    /* matched-search beam arms (same controller, same budget) */
    double bg[NSCORE] = {0}, bf[NSCORE] = {0};
    Counters arm_ctr[NSCORE];
    for (int sc = 0; sc < NSCORE; sc++) arm_ctr[sc].states = arm_ctr[sc].cands =
      arm_ctr[sc].closes = arm_ctr[sc].forwards = 0;
    for (int wi = 0; wi < g_nw[2]; wi++){
      const World *w = &g_data[2][wi].w;
      for (int sc = 0; sc < NSCORE; sc++){
        int g1 = 0, f1 = 0;
        Counters c = {0,0,0,0};
        policy_world_beam(w, g_p, sc, (uint64_t)(1000+wi), &g1, &f1, &c);
        g_wgoals[si][sc][wi] = g1;
        g_wfull[si][sc][wi] = f1;
        bg[sc] += g1; bf[sc] += f1;
        arm_ctr[sc].states += c.states; arm_ctr[sc].cands += c.cands;
        arm_ctr[sc].closes += c.closes; arm_ctr[sc].forwards += c.forwards;
      }
      /* budget-exact upper bound must dominate every arm and the greedy model */
      int model_g = 0, st1 = 0, full1 = 0;
      policy_world(w, g_p, 0, (uint64_t)(1000+wi), &model_g, &st1, &full1);
      if (model_g > bw_goals[wi]){
        bound_assert_ok = 0;
        bound_viol++;
        if (bound_viol <= 5)
          printf("BOUND-VIOLATION world=%ld model=%d bound=%d goals_total=%d\n",
                 (long)wi, model_g, bw_goals[wi], w->ngoals);
      }
      bound_pairs++;
    }
    long tt = 0;
    for (int wi = 0; wi < g_nw[2]; wi++) tt += g_data[2][wi].w.ngoals;
    for (int sc = 0; sc < NSCORE; sc++){ bg[sc] = tt ? bg[sc]/(double)tt : 0.0; bf[sc] /= (double)g_nw[2]; }

    if (g_emit_worlds){
      for (int wi = 0; wi < g_nw[2]; wi++){
        const World *w = &g_data[2][wi].w;
        int g1 = 0, st1 = 0, f1 = 0, g3 = 0, s3 = 0, f3 = 0;
        policy_world(w, g_p, 0, (uint64_t)(1000+wi), &g1, &st1, &f1);
        policy_world(w, g_p, 1, (uint64_t)(1000+wi), &g3, &s3, &f3);
        printf("SUCCESS %s seed=%d world=%d model=%d beam=%d support=%d goals=%d/%d beam_goals=%d/%d bound=%d\n",
               VNAME, seed, wi, f1, g_wfull[si][SC_MODEL_RAW][wi], f3, g1, w->ngoals,
               g_wgoals[si][SC_MODEL_RAW][wi], w->ngoals, bw_goals[wi]);
      }
    }
    double rg_m = 0, ht_m = 0, rg_s = 0, ht_s = 0, rg_u = 0, ht_u = 0;
    if (g_regret) first_step_regret(&rg_m, &ht_m, &rg_s, &ht_s, &rg_u, &ht_u);
    if (g_regret) traj_profile(seed);
    if (g_dfs){
      double dv_full = 0;
      double dv = policy_metrics_dfs(2, &dv_full);
      printf("DFS seed=%d variant=%s d=%d b=%d branch=%d subsume=%d prop=%d goal=%.4f full=%.4f "
             "nodes=%ld cands=%ld leafs=%ld pruned=%ld\n",
             seed, VNAME, (g_goaldepth > 0 ? g_goaldepth : 2), g_eval_budget,
             g_branch, g_subsume, g_prop, dv, dv_full,
             g_dfs_nodes, g_dfs_cands, g_dfs_leafs, g_dfs_pruned);
      /* 0260 hybrid layers: kernel path condition (Silicon), certificate (Rocq),
       * verified lemma contracts, obligation focus. One line per seed. */
      printf("HYBRID seed=%d variant=%s attmode=%d symgate=%d cert=%d focus=%d lemma=%d "
             "gate_viol=%ld pc_fallback=%ld pc_tokens=%ld pc_dropped=%ld "
             "cert_ok=%ld cert_fail=%ld cert_checked=%ld cert_mutfail=%ld lemma_uses=%ld lemmas=%d "
             "focus_states=%ld focus_removed=%ld pairmode=%d pair_uses=%d pair_viol=%d "
             "pair_keep=%d lemma_uses_all=%ld\n",
             seed, VNAME, ATTMODE, SYMGATE, CERT, FOCUS, LEMMA,
             g_pc_picks, g_pc_fallback, g_pc_tokens, g_pc_dropped,
             g_cert_ok, g_cert_fail, g_cert_checked, g_cert_mutfail, g_lemma_uses, g_nlem,
             g_focus_states, g_focus_removed, g_pairmode, g_pair_uses, g_pair_viol,
             g_pair_keep, g_lemma_uses);
#if ASSERT
      printf("ASSERT seed=%d states=%ld adopt=%ld fallback=%ld raw_adopt=%ld raw_rate=%.4f\n",
             seed, g_assert_states, g_assert_adopt, g_assert_fallback,
             g_assert_raw_adopt, g_assert_states ? (double)g_assert_raw_adopt/(double)g_assert_states : 0);
#endif
    }
    double perm = permutation_invariance();
    Metrics vt, bs, bp, br; eval_steps(g_p, 1, &vt);
    eval_steps_base(2, 1, &bs); eval_steps_base(2, 2, &bp); eval_steps_base(2, 3, &br);
    double pchk = 0;
    { double *pp = pv(g_p); long n = param_count(); for (long i = 0; i < n; i++) pchk += pp[i]*(double)(i % 97); }
    printf("SEED %d variant=%s fixture=%s d=%d b=%d top1=%.4f hit=%.4f regret=%.4f "
           "proof_model=%.4f full_model=%.4f proof_utility_greedy=%.4f proof_support=%.4f "
           "proof_prior=%.4f proof_random=%.4f proof_untrained=%.4f proof_shuffled=%.4f "
           "proof_beam=%.4f full_beam=%.4f beam_logp=%.4f beam_support=%.4f beam_prior=%.4f "
           "beam_random=%.4f beam_untrained=%.4f beam_full_support=%.4f bound_goal=%.4f bound_full=%.4f "
           "perm_maxdiff=%.3e val_top1=%.4f pchk=%.6f base_support=%.4f base_prior=%.4f "
           "base_random=%.4f search_states=%ld search_cands=%ld search_closes=%ld forwards_model=%ld\n",
           seed, VNAME, (HARD_GOALS ? "hard" : "ref"),
           (g_goaldepth > 0 ? g_goaldepth : 2), g_eval_budget, m.top1, m.hit, m.regret,
           pm, fm, po, ps, pp, pr, pu, psh, bg[SC_MODEL_RAW], bf[SC_MODEL_RAW],
           bg[SC_MODEL_LOGP], bg[SC_SUPPORT], bg[SC_PRIOR], bg[SC_RANDOM], bg[SC_UNTRAINED],
           bf[SC_SUPPORT], bound_goal, bound_full, perm, vt.top1, pchk, bs.top1, bp.top1, br.top1,
           arm_ctr[SC_MODEL_RAW].states, arm_ctr[SC_MODEL_RAW].cands,
           arm_ctr[SC_MODEL_RAW].closes, arm_ctr[SC_MODEL_RAW].forwards);

    double v[NAGG] = {m.top1, m.hit, pm, fm, po, ps, pp, pr, pu, psh,
                      bg[SC_MODEL_RAW], bf[SC_MODEL_RAW], bg[SC_MODEL_LOGP],
                      bg[SC_SUPPORT], bg[SC_PRIOR], bg[SC_RANDOM], bg[SC_UNTRAINED],
                      bf[SC_SUPPORT], bound_goal, bound_full, perm,
                      (double)arm_ctr[SC_MODEL_RAW].states, (double)arm_ctr[SC_MODEL_RAW].cands,
                      (double)arm_ctr[SC_MODEL_RAW].closes, vt.top1, pchk,
                      bs.top1, bp.top1, br.top1,
                      rg_m, ht_m, rg_s, ht_s, rg_u, ht_u};
    for (int i = 0; i < NAGG; i++) agg[i] += v[i];
    cinfo.states += arm_ctr[SC_MODEL_RAW].states;
    cinfo.cands += arm_ctr[SC_MODEL_RAW].cands;
    cinfo.closes += arm_ctr[SC_MODEL_RAW].closes;
    cinfo.forwards += arm_ctr[SC_MODEL_RAW].forwards;
  }
  printf("MEAN variant=%s fixture=%s d=%d b=%d seeds=%d top1=%.4f hit=%.4f proof_model=%.4f full_model=%.4f "
         "proof_utility_greedy=%.4f proof_support=%.4f proof_prior=%.4f proof_random=%.4f "
         "proof_untrained=%.4f proof_shuffled=%.4f proof_beam=%.4f full_beam=%.4f "
         "beam_logp=%.4f beam_support=%.4f beam_prior=%.4f beam_random=%.4f beam_untrained=%.4f "
         "beam_full_support=%.4f bound_goal=%.4f bound_full=%.4f perm_maxdiff=%.3e "
         "search_states=%.0f search_cands=%.0f search_closes=%.0f forwards_model=%.0f "
         "val_top1=%.4f pchk=%.6f base_support=%.4f base_prior=%.4f base_random=%.4f\n",
         VNAME, (HARD_GOALS ? "hard" : "ref"),
         (g_goaldepth > 0 ? g_goaldepth : 2), g_eval_budget, seeds,
         agg[0]/seeds, agg[1]/seeds, agg[2]/seeds, agg[3]/seeds, agg[4]/seeds, agg[5]/seeds,
         agg[6]/seeds, agg[7]/seeds, agg[8]/seeds, agg[9]/seeds, agg[10]/seeds, agg[11]/seeds,
         agg[12]/seeds, agg[13]/seeds, agg[14]/seeds, agg[15]/seeds, agg[16]/seeds,
         agg[17]/seeds, agg[18]/seeds, agg[19]/seeds, agg[20]/seeds,
         agg[21]/seeds, agg[22]/seeds, agg[23]/seeds, (double)cinfo.forwards/(double)seeds,
         agg[24]/seeds, agg[25]/seeds, agg[26]/seeds, agg[27]/seeds, agg[28]/seeds);
  {
    double rlo, rhi, mlo, mhi, flo, fhi;
    bootstrap_beam_diff(seeds, SC_MODEL_RAW, SC_SUPPORT, &rlo, &rhi, &mlo, &mhi, &flo, &fhi);
    printf("BOOT beam_model_raw_minus_support goal_ratio_lo=%.4f goal_ratio_hi=%.4f "
           "goal_macro_lo=%.4f goal_macro_hi=%.4f full_lo=%.4f full_hi=%.4f\n",
           rlo, rhi, mlo, mhi, flo, fhi);
    bootstrap_beam_diff(seeds, SC_MODEL_RAW, SC_MODEL_LOGP, &rlo, &rhi, &mlo, &mhi, &flo, &fhi);
    printf("BOOT beam_model_raw_minus_logp goal_ratio_lo=%.4f goal_ratio_hi=%.4f "
           "goal_macro_lo=%.4f goal_macro_hi=%.4f full_lo=%.4f full_hi=%.4f\n",
           rlo, rhi, mlo, mhi, flo, fhi);
  }
  if (g_regret)
    printf("REGRET-MEAN variant=%s d=%d b=%d model_regret=%.4f model_opt=%.4f "
           "support_regret=%.4f support_opt=%.4f ug_regret=%.4f ug_opt=%.4f\n",
           VNAME, (g_goaldepth > 0 ? g_goaldepth : 2), g_eval_budget,
           agg[29]/seeds, agg[30]/seeds, agg[31]/seeds, agg[32]/seeds,
           agg[33]/seeds, agg[34]/seeds);
  printf("BOUND-ASSERT ok=%d pairs=%ld violations=%ld bound_goal=%.4f bound_full=%.4f\n",
         bound_assert_ok, bound_pairs, bound_viol, bound_goal, bound_full);
  printf("SEARCH-BUDGET states=%ld cands=%ld closes=%ld forwards_model=%ld (identical across the six beam arms)\n",
         cinfo.states, cinfo.cands, cinfo.closes, cinfo.forwards);
  if (verbose) printf("PARAMS %ld\n", param_count());
}

/* ---- Maru export: Q16 weights + evaluation cases (inference parity) ---- */
static void emit_matrix(FILE *f, const char *name, const double *w, int rows, int cols){
  fprintf(f, "(define %s (list\n", name);
  for (int r = 0; r < rows; r++){
    fprintf(f, "  (list");
    for (int c = 0; c < cols; c++){
      long q = lround(w[r*cols + c] * 65536.0);
      fprintf(f, " %ld", q);
    }
    fprintf(f, ")\n");
  }
  fprintf(f, "))\n");
}
static void emit_vec(FILE *f, const char *name, const double *w, int n){
  fprintf(f, "(define %s (list", name);
  for (int i = 0; i < n; i++) fprintf(f, " %ld", lround(w[i]*65536.0));
  fprintf(f, "))\n");
}

static void export_maru(const char *path, int seed, int epochs, int ncases){
#if RELATOM
  fprintf(stderr, "EXPORT-FAIL: RELATOM Maru Q16 export is not implemented yet "
                  "(relational fixture port is a follow-up); gate Maru parity on the unary base build\n");
  exit(2);
#elif LOOPCELL
  fprintf(stderr, "EXPORT-FAIL: LOOPCELL Maru Q16 export is not implemented yet "
                  "(the latent chain needs a multi-step pst_infer port); "
                  "gate Maru parity on the base build\n");
  exit(2);
#else
  build_dataset();
  head_prior_from_train();
  rule_prior_from_train();
  rng_state = (uint64_t)(seed*7 + 1);
  train_seed(seed, epochs);
  FILE *f = fopen(path, "w");
  if (!f){ fprintf(stderr, "cannot open %s\n", path); exit(2); }
  fprintf(f, ";;; generated by pst --export-maru (variant %s, fixture %s) — do not edit\n",
          VNAME, (HARD_GOALS ? "hard" : "ref"));
  fprintf(f, "(define pst-D %d)\n(define pst-FE %d)\n(define pst-NH %d)\n(define pst-NL %d)\n",
          D, FE, NH, NL);
  emit_matrix(f, "pst-Ws", g_p->Ws, D, STATE_DIM);
  emit_vec(f, "pst-bs", g_p->bs, D);
  emit_matrix(f, "pst-Wc", g_p->Wc, D, CAND_DIM);
  emit_vec(f, "pst-bc", g_p->bc, D);
  emit_vec(f, "pst-ts", g_p->ts, D);
  emit_vec(f, "pst-tc", g_p->tc, D);
  for (int l = 0; l < NL; l++){
    char nm[64];
    snprintf(nm, sizeof nm, "pst-Wqkv%d", l); emit_matrix(f, nm, g_p->Wqkv[l], 3*D, D);
    snprintf(nm, sizeof nm, "pst-bqkv%d", l); emit_vec(f, nm, g_p->bqkv[l], 3*D);
    snprintf(nm, sizeof nm, "pst-Wo%d", l); emit_matrix(f, nm, g_p->Wo[l], D, D);
    snprintf(nm, sizeof nm, "pst-bo%d", l); emit_vec(f, nm, g_p->bo[l], D);
    snprintf(nm, sizeof nm, "pst-g1_%d", l); emit_vec(f, nm, g_p->g1[l], D);
    snprintf(nm, sizeof nm, "pst-be1_%d", l); emit_vec(f, nm, g_p->be1[l], D);
    snprintf(nm, sizeof nm, "pst-W1_%d", l); emit_matrix(f, nm, g_p->W1[l], FE, D);
    snprintf(nm, sizeof nm, "pst-b1_%d", l); emit_vec(f, nm, g_p->b1[l], FE);
    snprintf(nm, sizeof nm, "pst-W2_%d", l); emit_matrix(f, nm, g_p->W2[l], D, FE);
    snprintf(nm, sizeof nm, "pst-b2_%d", l); emit_vec(f, nm, g_p->b2[l], D);
    snprintf(nm, sizeof nm, "pst-g2_%d", l); emit_vec(f, nm, g_p->g2[l], D);
    snprintf(nm, sizeof nm, "pst-be2_%d", l); emit_vec(f, nm, g_p->be2[l], D);
  }
  emit_vec(f, "pst-gf", g_p->gf, D);
  emit_vec(f, "pst-bef", g_p->bef, D);
  emit_matrix(f, "pst-Wout", g_p->Wout, NOUT, D);
  emit_vec(f, "pst-bout", g_p->bout, NOUT);

  /* evaluation cases: first ncases steps of the test split */
  int emitted = 0;
  fprintf(f, "(define pst-cases (list\n");
  for (int i = 0; i < g_nw[2] && emitted < ncases; i++){
    const WSteps *ws = &g_data[2][i];
    if (ws->nsteps == 0) continue;
    const RStep *rs = &ws->st[0];
    model_forward(g_p, rs->state, rs->cf, rs->nlive, g_c);
    int arg = 0;
    for (int j = 1; j < rs->nlive; j++) if (g_c->score[j] > g_c->score[arg]) arg = j;
    fprintf(f, "  (list %d\n    (list", rs->nlive);
    for (int k = 0; k < STATE_DIM; k++) fprintf(f, " %ld", lround(rs->state[k]*65536.0));
    fprintf(f, ")\n    (list\n");
    for (int j = 0; j < rs->nlive; j++){
      fprintf(f, "      (list");
      for (int k = 0; k < CAND_DIM; k++) fprintf(f, " %ld", lround(rs->cf[j][k]*65536.0));
      fprintf(f, ")\n");
    }
    fprintf(f, "    )\n    %d\n    (list", arg);
    for (int j = 0; j < rs->nlive; j++) fprintf(f, " %ld", lround(g_c->score[j]*65536.0));
    fprintf(f, "))\n");
    emitted++;
  }
  fprintf(f, "))\n");
  fclose(f);
  double pchk = 0;
  { double *pp = pv(g_p); long np = param_count(); for (long i = 0; i < np; i++) pchk += pp[i]*(double)(i % 97); }
  printf("EXPORT-CONFIG variant=%s fixture=%s seed=%d epochs=%d train=%d val=%d test=%d cases=%d params=%ld weights_checksum=%.6f\n",
         VNAME, (HARD_GOALS ? "hard" : "ref"), seed, epochs, g_nw[0], g_nw[1], g_nw[2],
         emitted, param_count(), pchk);
  printf("EXPORT-MARU cases=%d path=%s params=%ld\n", emitted, path, param_count());
#endif
}

/* debug: dump stage-by-stage Q16 values for one exported case */
static void dump_forward(const char *path, int seed, int epochs, int case_idx){
  build_dataset();
  head_prior_from_train();
  rule_prior_from_train();
  rng_state = (uint64_t)(seed*7 + 1);
  train_seed(seed, epochs);
  FILE *f = fopen(path, "w");
  if (!f){ fprintf(stderr, "cannot open %s\n", path); exit(2); }
  int idx = 0, emitted = 0;
  for (int i = 0; i < g_nw[2] && emitted <= case_idx; i++){
    const WSteps *ws = &g_data[2][i];
    if (ws->nsteps == 0) continue;
    if (idx++ != case_idx) continue;
    const RStep *rs = &ws->st[0];
    model_forward(g_p, rs->state, rs->cf, rs->nlive, g_c);
    fprintf(f, "ETH0");
    for (int d = 0; d < D; d++) fprintf(f, " %ld", lround(g_c->h[0][d]*65536.0));
    fprintf(f, "\n");
    LayerCache *lc = &g_c->lc[0];
    fprintf(f, "LN1_0");
    for (int d = 0; d < D; d++) fprintf(f, " %ld", lround(lc->ln1[0][d]*65536.0));
    fprintf(f, "\nQKV0");
    for (int r = 0; r < 3*D; r++) fprintf(f, " %ld", lround(lc->qkv[0][r]*65536.0));
    fprintf(f, "\nATT0H0");
    for (int j = 0; j < rs->nlive + 1; j++) fprintf(f, " %ld", lround(lc->att[0][0][j]*65536.0));
    fprintf(f, "\nAO0");
    for (int d = 0; d < D; d++) fprintf(f, " %ld", lround(lc->ao[0][d]*65536.0));
    fprintf(f, "\nH1_0");
    for (int d = 0; d < D; d++) fprintf(f, " %ld", lround(lc->h1[0][d]*65536.0));
    fprintf(f, "\nACT0");
    for (int d = 0; d < FE; d++) fprintf(f, " %ld", lround(lc->act[0][d]*65536.0));
    fprintf(f, "\nH2_0");
    for (int d = 0; d < D; d++) fprintf(f, " %ld", lround(g_c->h[0][d]*65536.0));
    fprintf(f, "\nSCORE");
    for (int j = 0; j < rs->nlive; j++) fprintf(f, " %ld", lround(g_c->score[j]*65536.0));
    fprintf(f, "\n");
    emitted++;
  }
  fclose(f);
  printf("DUMP-FORWARD case=%d path=%s\n", case_idx, path);
}

/* ---- finite-difference gradient check ---- */
static double gradcheck(void){
  build_dataset();
  rule_prior_from_train();
  if (g_dp_check) dp_audit();
  init_params(g_p, 1234);
  memset(g_g, 0, sizeof(Params));
#if EPTRAIN || LOOPCELL || TYPED
  /* the checked scalar is the EPISODE objective (BPTT through the cell),
   * exactly what the episode trainer optimises */
  const WSteps *ws = &g_data[0][0];
  double base = episode_forward(g_p, ws, 1);
  episode_backward(ws);
  long n = param_count();
  double *pp = pv(g_p), *gg = pv(g_g);
  double eps = 1e-5, max_rel = 0, max_abs = 0, max_grad = 0;
  long worst = -1; double worst_num = 0, worst_ana = 0;
  int checked = 0;
  for (long i = 0; i < n; i++){
    double orig = pp[i];
    pp[i] = orig + eps;
    double lp = episode_forward(g_p, ws, 0);
    pp[i] = orig - eps;
    double lm = episode_forward(g_p, ws, 0);
    pp[i] = orig;
    double num = (lp - lm)/(2*eps);
    double ana = gg[i];
    double denom = fabs(num) + fabs(ana) + 1e-8;
    double rel = fabs(num - ana)/denom;
    if (fabs(num - ana) > max_abs){ max_abs = fabs(num - ana); worst = i; worst_num = num; worst_ana = ana; }
    if (fabs(ana) > max_grad) max_grad = fabs(ana);
    if (rel > max_rel && fabs(num) + fabs(ana) > 1e-7) max_rel = rel;
    checked++;
  }
#else
  const RStep *rs = &g_data[0][0].st[0];
  double base = model_step(rs->state, (const double (*)[CAND_DIM])rs->cf,
                           (const int*)0, rs->best, rs->util, rs->nlive);
  long n = param_count();
  double *pp = pv(g_p), *gg = pv(g_g);
  double eps = 1e-5, max_rel = 0, max_abs = 0, max_grad = 0;
  long worst = -1; double worst_num = 0, worst_ana = 0;
  int checked = 0;
  for (long i = 0; i < n; i++){
    double orig = pp[i];
    pp[i] = orig + eps;
    double lp = loss_eval(g_p, rs->state, (const double (*)[CAND_DIM])rs->cf, rs->util, rs->best, rs->nlive);
    pp[i] = orig - eps;
    double lm = loss_eval(g_p, rs->state, (const double (*)[CAND_DIM])rs->cf, rs->util, rs->best, rs->nlive);
    pp[i] = orig;
    double num = (lp - lm)/(2*eps);
    double ana = gg[i];
    double denom = fabs(num) + fabs(ana) + 1e-8;
    double rel = fabs(num - ana)/denom;
    if (fabs(num - ana) > max_abs){ max_abs = fabs(num - ana); worst = i; worst_num = num; worst_ana = ana; }
    if (fabs(ana) > max_grad) max_grad = fabs(ana);
    if (rel > max_rel && fabs(num) + fabs(ana) > 1e-7) max_rel = rel;
    checked++;
  }
#endif
  double rel_to_max = max_abs / (max_grad > 0 ? max_grad : 1.0);
  printf("GRADCHECK params=%d loss=%.6f max_abs=%.3e max_grad=%.3e rel_to_max_grad=%.3e max_rel_small=%.3e\n",
         checked, base, max_abs, max_grad, rel_to_max, max_rel);
#if TYPED
  { /* typed-structure liveness: embeddings/typed-attention must carry gradient,
     * else a dead typed path would pass the finite-difference check vacuously */
    double tmax = 0;
    long off = (long)(offsetof(Params, Pemb)/sizeof(double));
    long end = (long)(offsetof(Params, abias)/sizeof(double)) + NH*16;
    for (long i = off; i < end; i++) if (fabs(gg[i]) > tmax) tmax = fabs(gg[i]);
    printf("TYPED-GRAD max=%.3e %s\n", tmax, tmax > 1e-8 ? "OK" : "DEAD");
    if (tmax <= 1e-8) return 1e9;
  }
#endif
#if ASSERT
  { /* proposal-head liveness: trained head must carry gradient; the ASSERTW=0
     * mechanism control must carry NONE (untrained by construction) */
    double amax = 0;
    long off = (long)(offsetof(Params, Wprop)/sizeof(double));
    long end = (long)(sizeof(Params)/sizeof(double));
    for (long i = off; i < end; i++) if (fabs(gg[i]) > amax) amax = fabs(gg[i]);
    int ok = (ASSERTW > 0) ? (amax > 1e-8) : (amax < 1e-12);
    printf("ASSERT-GRAD max=%.3e assertw=%.3f %s\n", amax, (double)ASSERTW, ok ? "OK" : "DEAD");
    if (!ok) return 1e9;
  }
#endif
#if LOOPCELL
  { /* BPTT liveness: the transition matrices must carry nonzero gradient,
     * otherwise a dead recurrence would pass the finite-difference check
     * vacuously (0 = 0). CELLDETACH expects zero cell gradients by design. */
    double cmax = 0;
    long off = (long)(offsetof(Params, Wu)/sizeof(double));
    long cnt = (long)((offsetof(Params, Wv) - offsetof(Params, Wu))/sizeof(double));
    for (long i = off; i < off+cnt; i++) if (fabs(gg[i]) > cmax) cmax = fabs(gg[i]);
    int ok = CELLDETACH ? (cmax < 1e-12) : (cmax > 1e-8);
    printf("CELL-GRAD max=%.3e detach=%d %s\n", cmax, CELLDETACH, ok ? "OK" : "DEAD");
    if (!ok) return 1e9;
  }
#endif
  if (getenv("PST_GRADDEBUG"))
    printf("GRADDEBUG worst_idx=%ld num=%.6e ana=%.6e\n", worst, worst_num, worst_ana);
  (void)gg;
  return rel_to_max;
}

/* ---- path-integral consistency self-check (INTEGRAL) ----------------------
 * Independently recomputes the path integral with an INCREMENTAL accumulator
 * (different code path from fill_path_features's prefix replay) and compares to
 * the stored training features. Guards the replay off-by-one. Also checks the
 * prior column equals g_rule_prior (which is computed from split 0 only). */
static int path_check(void){
#if INTEGRAL
  build_dataset();
  rule_prior_from_train();
  double maxdiff = 0, priordiff = 0;
  int nchecked = 0;
  for (int i = 0; i < g_nw[0] && i < 30; i++){
    const WSteps *ws = &g_data[0][i];
    double acc[NRULES_ALL] = {0}, root[NRULES_ALL] = {0}, wsum = 0;
    int t = 0;
    int rules[MAXRULE];
    int nrules = SEED_RULES;
    for (int k = 0; k < SEED_RULES; k++) rules[k] = ws->w.theory[k];
    for (int s = 0; s < ws->nsteps; s++){
      const RStep *rs = &ws->st[s];
      uint8_t kn[WENT];
      closure(ws->w.facts, rules, nrules, kn);
      wsum = PATH_GAMMA*wsum + 1.0;
      for (int c = 0; c < POOL; c++){
        int rid = ws->w.cands[c];
        double sup = (double)support(&all_rules[rid], kn)/(double)WENT;
        if (t == 0) root[rid] = sup;
        acc[rid] = PATH_GAMMA*acc[rid] + sup;
      }
      t++;
      for (int k = 0; k < rs->nlive; k++){
        int rid = rs->live[k];
        double s_now = (double)support(&all_rules[rid], kn)/(double)WENT;
        double d0 = fabs(acc[rid]/wsum - rs->cf[k][PATH_OFF+0]);
        double d1 = fabs((s_now - root[rid]) - rs->cf[k][PATH_OFF+1]);
        double d2 = fabs(g_rule_prior[rid] - rs->cf[k][PATH_OFF+2]);
        if (d0 > maxdiff) maxdiff = d0;
        if (d1 > maxdiff) maxdiff = d1;
        if (d2 > priordiff) priordiff = d2;
        nchecked++;
      }
      rules[nrules++] = rs->live[rs->best];
    }
  }
  int ok = (maxdiff < 1e-12 && priordiff < 1e-12);
  printf("PATH-CHECK checked=%d path_maxdiff=%.3e prior_maxdiff=%.3e %s\n",
         nchecked, maxdiff, priordiff, ok ? "PASS" : "FAIL");
  return ok ? 0 : 1;
#else
  printf("PATH-CHECK-SKIP (INTEGRAL=0)\n");
  return 0;
#endif
}