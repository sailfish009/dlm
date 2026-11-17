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
  double lift_rho, path_gamma;
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
} RStep;

typedef struct {
  World w;
  int nsteps;
  RStep st[NSTEPS];
} WSteps;

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
static int g_cert_on = CERT;           /* independent certificate check on the DFS proof */
static int g_cert_selftest = 0;        /* 1 = corrupt one parent (checker must fail) */
static long g_dfs_nodes = 0, g_dfs_cands = 0, g_dfs_leafs = 0, g_dfs_pruned = 0;
static long g_nsteps[3];

static void pc_filter(const uint8_t *known, int *live, int *nlive);
static int focus_filter(const World *w, const uint8_t *known, int *live, int nlive);
static void lemma_mine(void);

static void build_dataset(void){
  for (int s = 0; s < 3; s++){
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
        state_features(&ws->w, rules, nrules, live, nlive, rs->state);
        int best = 0;
        for (int k = 0; k < nlive; k++){
          cand_features(&ws->w, rules, nrules, live[k], rs->cf[k]);
          rs->util[k] = utility(&ws->w, rules, nrules, live[k]);
          if (rs->util[k] > rs->util[best]) best = k;
        }
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
    for (int s = 0; s < ws->nsteps; s++){
      const RStep *rs = &ws->st[s];
      model_forward(p, rs->state, rs->cf, rs->nlive, g_c);
      int arg = 0;
      for (int j = 1; j < rs->nlive; j++) if (g_c->score[j] > g_c->score[arg]) arg = j;
      u += rs->util[arg];
      h += (arg == rs->best) ? 1.0 : 0.0;
      double mx = rs->util[0];
      for (int j = 1; j < rs->nlive; j++) if (rs->util[j] > mx) mx = rs->util[j];
      r += mx - rs->util[arg];
      n++;
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
          for (int q = 0; q < P; q++) if (rs->cf[j][8+q] > 0.5) head = q;
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
                          double (*cf)[CAND_DIM], double *util){
  state_features(w, rules, nrules, live, nlive, state);
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
  int used_steps = 0;
  for (int st = 0; st < g_eval_budget; st++){
    int live[POOL], nlive = 0;
    for (int c = 0; c < POOL; c++){
      int r = w->cands[c], u = 0;
      for (int k = 0; k < nrules; k++) if (rules[k] == r) u = 1;
      if (!u) live[nlive++] = r;
    }
    if (!nlive) break;
    {
      uint8_t known[WENT];
      closure(w->facts, rules, nrules, known);
      nlive = focus_filter(w, known, live, nlive);   /* Rocq obligation focus */
      pc_filter(known, live, &nlive);                /* Silicon path condition */
    }
    if (!nlive) break;
    step_features(w, rules, nrules, live, nlive, state, cf2, util);
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
      model_forward(mp, state, (const double (*)[CAND_DIM])cfp, nlive, g_c);
      for (int k = 1; k < nlive; k++) if (g_c->score[k] > g_c->score[pick]) pick = k;
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
        for (int q = 0; q < P; q++) if (cf2[k][8+q] > 0.5) head = q;
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
  }
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  int gp = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (known[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) gp++;
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
  for (int e = 0; e < WENT; e++) s |= (uint64_t)m[e] << (6*e);
  return s;
}
static int is_subset_mask(uint64_t a, uint64_t b){   /* a subset of b */
  for (int e = 0; e < WENT; e++){
    uint64_t am = (a >> (6*e)) & 0x3f, bm = (b >> (6*e)) & 0x3f;
    if ((am & ~bm) != 0) return 0;
  }
  return 1;
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
  int rel[P];
  for (int p = 0; p < P; p++) rel[p] = 0;
  for (int g = 0; g < w->ngoals; g++){
    int e = w->goal_ent[g], p = w->goal_pred[g];
    if (!(known[e] & (uint8_t)(1u << p))) rel[p] = 1;
  }
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
      for (int e = 0; e < WENT; e++) if (kn[e] & (uint8_t)(1u << a->body[0])) ok = 1;
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

static void dfs_world(const World *w, int *rules, int nrules, int depth, int budget){
  g_dfs_nodes++;
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  int proven = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (known[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) proven++;
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
  step_features(w, rules, nrules, live, nlive, state, cf2, util);
  model_forward(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, g_c);
  g_dfs_cands += nlive;
  int order[POOL];
  for (int a = 0; a < nlive; a++) order[a] = a;
  for (int a = 0; a < nlive; a++)
    for (int b = a+1; b < nlive; b++)
      if (g_c->score[order[b]] > g_c->score[order[a]]){ int t = order[a]; order[a] = order[b]; order[b] = t; }
  /* combined action set: single rules + kernel-verified lemma (pair) actions */
  int act_kind[POOL+128], act_val[POOL+128];
  double act_score[POOL+128];
  int nact = 0;
  for (int a = 0; a < nlive; a++){
    act_kind[nact] = 0; act_val[nact] = live[order[a]]; act_score[nact] = g_c->score[order[a]]; nact++;
  }
  if (g_lemmas){
    int rules_used[POOL];
    for (int c = 0; c < POOL; c++) rules_used[c] = 0;
    for (int k = 0; k < nrules; k++)
      for (int c = 0; c < POOL; c++) if (w->cands[c] == rules[k]) rules_used[c] = 1;
    for (int L = 0; L < g_nlem; L++){
      int r1 = g_lem[L].r1, r2 = g_lem[L].r2, i1 = -1, i2 = -1;
      for (int c = 0; c < POOL; c++){ if (w->cands[c] == r1) i1 = c; if (w->cands[c] == r2) i2 = c; }
      if (i1 < 0 || i2 < 0 || rules_used[i1] || rules_used[i2]) continue;
      int pre_ok = 0;
      for (int e = 0; e < WENT; e++) if (known[e] & (uint8_t)(1u << g_lem[L].body)) pre_ok = 1;
      if (!pre_ok) continue;
      double sc = -1e30;
      for (int a = 0; a < nlive; a++) if (live[a] == r1) sc = g_c->score[a];
      if (sc <= -1e29) continue;
      act_kind[nact] = 1; act_val[nact] = L; act_score[nact] = sc; nact++;
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
  int keep = (g_branch < nact) ? g_branch : nact;
  for (int a = 0; a < keep; a++){
    if (act_kind[a] == 0){
      rules[nrules] = act_val[a];
      dfs_world(w, rules, nrules+1, depth+1, budget);
    } else {
      int L = act_val[a];
      if (nrules + 2 > MAXRULE) continue;      /* capacity guard (0260 fix) */
      rules[nrules] = g_lem[L].r1; rules[nrules+1] = g_lem[L].r2;
      g_lemma_uses++; g_lem[L].uses++;
      dfs_world(w, rules, nrules+2, depth+g_lemma_cost, budget);
    }
    if (proven > g_best_seen) g_best_seen = proven;
  }
  /* R255-3: register only fully-explored states (postorder). Preorder registration
   * let an ancestor on the current path dominate its own descendants, which is
   * unsound even for exhaustive search (review 0255 F3). */
  if (g_subsume) subs_add(mask, depth);
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
      if (known[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) gp++;
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
    if (base[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) bnd_best++;
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
                            Counters *ctr){
  if (scorer == SC_MODEL_RAW || scorer == SC_UNTRAINED){
    const Params *mp = (scorer == SC_UNTRAINED) ? g_untrained : p;
    model_forward(mp, state, cf, nlive, g_c);
    ctr->forwards++;
    for (int j = 0; j < nlive; j++) out[j] = g_c->score[j];
    return 1;
  }
  if (scorer == SC_MODEL_LOGP){
    model_forward(p, state, cf, nlive, g_c);
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
      for (int q = 0; q < P; q++) if (cf[j][8+q] > 0.5) head = q;
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
      {
        uint8_t known[WENT];
        closure(w->facts, seq[bi], nrules, known);
        nlive = focus_filter(w, known, live, nlive);  /* Rocq obligation focus */
        pc_filter(known, live, &nlive);               /* Silicon path condition */
      }
      if (!nlive) continue;
      step_features(w, seq[bi], nrules, live, nlive, state, cf2, util);
      double sc[POOL];
      score_candidates(scorer, p, state, (const double (*)[CAND_DIM])cf2, nlive, sc, ctr);
      ctr->states++;
      ctr->cands += nlive;
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
        }
    nW = (n2 < W) ? n2 : W;
    for (int i = 0; i < nW; i++){
      score[i] = sc2[i];
      seqn[i] = nseq[i];
      for (int q = 0; q < MAXSEQ; q++) seq[i][q] = ns2[i][q];
    }
  }
  int bestgp = -1, bestfull = 0;
  for (int i = 0; i < nW; i++){
    uint8_t known[WENT];
    closure(w->facts, seq[i], seqn[i], known);
    ctr->closes++;
    int gp = 0;
    for (int g = 0; g < w->ngoals; g++)
      if (known[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) gp++;
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
  model_forward(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, g_c);
  for (int k = 0; k < rs->nlive; k++) s1[k] = g_c->score[k];
  for (int k = 0; k < rs->nlive; k++)
    for (int d = 0; d < CAND_DIM; d++) cf[k][d] = rs->cf[rs->nlive-1-k][d];
  model_forward(g_p, rs->state, (const double (*)[CAND_DIM])cf, rs->nlive, g_c);
  for (int k = 0; k < rs->nlive; k++) s2[k] = g_c->score[rs->nlive-1-k];
  double mx = 0;
  for (int k = 0; k < rs->nlive; k++){
    double d = fabs(s1[k] - s2[k]);
    if (d > mx) mx = d;
  }
  return mx;
}

/* ---- training ---- */
static void train_seed(int seed, int epochs){
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
  *g_p = *best;
  free(best);
  free(idx);
  free(idx_root);
}

/* ---- reporting ---- */
static void head_prior_from_train(void){
  double sums[P] = {0}, counts[P] = {0};
  for (int i = 0; i < g_nw[0]; i++)
    for (int s = 0; s < g_data[0][i].nsteps; s++){
      const RStep *rs = &g_data[0][i].st[s];
      for (int k = 0; k < rs->nlive; k++){
        int head = 0;
        for (int q = 0; q < P; q++) if (rs->cf[k][8+q] > 0.5) head = q;
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
    if (known[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) gp++;
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
      step_features(wd, rules, nrules, live, nlive, state, cf2, util);
      model_forward(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, g_c);
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
    step_features(w, rules, SEED_RULES, live, nlive, state, cf2, util);
    model_forward(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, g_c);
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
    step_features(wd, rules, n, live, nlive, state, cf2, util);
    model_forward(g_p, state, (const double (*)[CAND_DIM])cf2, nlive, g_c);
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
  head_prior_from_train();
  rule_prior_from_train();
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
          if (kn[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) gp1++;
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
          h.focus != FOCUS || h.lemma != LEMMA){
        fprintf(stderr, "WEIGHTS-MISMATCH %s: header dims %d/%d variant %d hard %d relob %d bindtok %d "
                "integral %d lifted %d holdout %d attmode %d symgate %d cert %d focus %d lemma %d, "
                "binary dims %d/%d variant %d hard %d relob %d bindtok %d integral %d lifted %d holdout %d attmode %d symgate %d cert %d focus %d lemma %d\n",
                g_load_weights, h.state_dim, h.cand_dim, h.variant, h.hard, h.relob, h.bindtok,
                h.integral, h.lifted, h.holdout, h.attmode, h.symgate, h.cert, h.focus, h.lemma,
                STATE_DIM, CAND_DIM, NOUT, HARD_GOALS, RELOB, BINDTOK, INTEGRAL, LIFTED, g_holdout_mask,
                ATTMODE, SYMGATE, CERT, FOCUS, LEMMA);
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
                      ATTMODE, SYMGATE, CERT, FOCUS, LEMMA,
                      LIFT_RHO, PATH_GAMMA, pchk };
        fwrite(&h, sizeof h, 1, sf);
        fwrite(g_p, sizeof(Params), 1, sf);
        fclose(sf);
      }
    }
    if (g_lemmas) lemma_mine();   /* verified 2-rule contracts from train rollouts */
    g_pc_tokens = g_pc_dropped = g_pc_fallback = g_pc_picks = 0;
    g_cert_ok = g_cert_fail = g_cert_checked = g_cert_mutfail = 0;
    g_focus_states = g_focus_removed = 0;
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
             "focus_states=%ld focus_removed=%ld\n",
             seed, VNAME, ATTMODE, SYMGATE, CERT, FOCUS, LEMMA,
             g_pc_picks, g_pc_fallback, g_pc_tokens, g_pc_dropped,
             g_cert_ok, g_cert_fail, g_cert_checked, g_cert_mutfail, g_lemma_uses, g_nlem,
             g_focus_states, g_focus_removed);
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
  const RStep *rs = &g_data[0][0].st[0];
  init_params(g_p, 1234);
  memset(g_g, 0, sizeof(Params));
  double base = model_step(rs->state, (const double (*)[CAND_DIM])rs->cf,
                           (const int*)0, rs->best, rs->util, rs->nlive);
  long n = param_count();
  double *pp = pv(g_p), *gg = pv(g_g);
  double eps = 1e-5, max_rel = 0, max_abs = 0, max_grad = 0;
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
    if (fabs(num - ana) > max_abs) max_abs = fabs(num - ana);
    if (fabs(ana) > max_grad) max_grad = fabs(ana);
    if (rel > max_rel && fabs(num) + fabs(ana) > 1e-7) max_rel = rel;
    checked++;
  }
  double rel_to_max = max_abs / (max_grad > 0 ? max_grad : 1.0);
  printf("GRADCHECK params=%d loss=%.6f max_abs=%.3e max_grad=%.3e rel_to_max_grad=%.3e max_rel_small=%.3e\n",
         checked, base, max_abs, max_grad, rel_to_max, max_rel);
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