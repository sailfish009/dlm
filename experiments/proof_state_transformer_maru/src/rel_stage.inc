/* ---------------- 0.0270 relational stage 1 (RELATOM=1) --------------------
 * Ground binary atoms over EREL=3 entities; the join lives in the composition
 * schema B(r2,e1,e3) <- B(r0,e1,e2), B(r1,e2,e3): the intermediate entity e2
 * is the binding the model must recover. The kernel is still propositional
 * Horn over atom ids (uint64 mask packed into the WENT=6 fact bytes), so every
 * downstream signature (closure/support/utility/features/DP/bound/DFS) is
 * unchanged. S0 features are entity-blind except goal-relative comparisons;
 * absolute entity/role identity enters only via S0e/S1 (the discriminative
 * contrast the design doc pre-registers). */

static void build_all_rules(void){
  int k = 0;
  /* unary chains U(h,e) <- U(b,e), h != b  (18) */
  for (int h = 0; h < PU; h++)
    for (int b = 0; b < PU; b++) if (h != b)
      for (int e = 0; e < EREL; e++){
        all_rules[k].head = h*EREL+e;
        all_rules[k].body[0] = b*EREL+e;
        all_rules[k].blen = 1; k++;
      }
  /* composition B(r2,e1,e3) <- B(r0,e1,e2), B(r1,e2,e3)  (27 joins) */
  for (int e1 = 0; e1 < EREL; e1++)
    for (int e2 = 0; e2 < EREL; e2++)
      for (int e3 = 0; e3 < EREL; e3++){
        int off = PU*EREL;
        all_rules[k].head = off + 2*EREL*EREL + e1*EREL+e3;
        all_rules[k].body[0] = off + 0*EREL*EREL + e1*EREL+e2;
        all_rules[k].body[1] = off + 1*EREL*EREL + e2*EREL+e3;
        all_rules[k].blen = 2; k++;
      }
  /* bridges B(r0,e1,e2) <- U(p,e1), U(q,e2), (p,q) in {(0,1),(1,2)}  (18) */
  for (int pq = 0; pq < 2; pq++){
    int p = pq, q = pq+1;
    for (int e1 = 0; e1 < EREL; e1++)
      for (int e2 = 0; e2 < EREL; e2++){
        all_rules[k].head = PU*EREL + e1*EREL+e2;
        all_rules[k].body[0] = p*EREL+e1;
        all_rules[k].body[1] = q*EREL+e2;
        all_rules[k].blen = 2; k++;
      }
  }
  if (k != NRULES_ALL){ fprintf(stderr, "rel rule table %d\n", k); exit(2); }
}

static void closure(const uint8_t facts[WENT], const int *rules, int nrules, uint8_t out[WENT]){
  uint64_t m = fs_load(facts);
  int changed = 1;
  while (changed){
    changed = 0;
    for (int k = 0; k < nrules; k++){
      const Rule *r = &all_rules[rules[k]];
      uint64_t bm = 0;
      for (int s = 0; s < r->blen; s++) bm |= 1ULL << r->body[s];
      uint64_t hm = 1ULL << r->head;
      if ((m & bm) == bm && !(m & hm)){ m |= hm; changed = 1; }
    }
  }
  fs_store(m, out);
}

/* number of body atoms known (0..blen); relational callers normalise by blen */
static int support(const Rule *r, const uint8_t known[WENT]){
  uint64_t m = fs_load(known);
  int c = 0;
  for (int s = 0; s < r->blen; s++) if ((m >> r->body[s]) & 1ULL) c++;
  return c;
}

static double utility(const World *w, const int *rules, int nrules, int cand){
  uint8_t before[WENT], after[WENT];
  closure(w->facts, rules, nrules, before);
  int tmp[SEED_RULES + MAXBUDGET + 1];
  for (int i = 0; i < nrules; i++) tmp[i] = rules[i];
  tmp[nrules] = cand;
  closure(w->facts, tmp, nrules + 1, after);
  uint64_t b = fs_load(before), a = fs_load(after);
  int goal_new = 0;
  for (int g = 0; g < w->ngoals; g++){
    uint64_t bit = 1ULL << GOAL_ATOM(w,g);
    if ((a & bit) && !(b & bit)) goal_new++;
  }
  int new_atoms = __builtin_popcountll(a & ~b);
  return 5.0*goal_new + 0.15*(double)new_atoms - rule_cost(&all_rules[cand]);
}

static void state_features(const World *w, const int *rules, int nrules,
                           const int *live, int nlive, double out[STATE_DIM], int rem){
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  uint64_t km = fs_load(known);
  int known_n = __builtin_popcountll(km);
  int goal_known = 0;
  for (int g = 0; g < w->ngoals; g++) if (GOAL_KNOWN(w,g,known)) goal_known++;
  double smin = 1e9, smax = -1e9, ssum = 0;
  for (int i = 0; i < nlive; i++){
    const Rule *r = &all_rules[live[i]];
    double s = r->blen ? (double)support(r, known)/(double)r->blen : 0.0;
    if (s < smin) smin = s;
    if (s > smax) smax = s;
    ssum += s;
  }
  out[0] = (double)known_n / (double)NA;
  out[1] = (double)goal_known / (double)(w->ngoals > 0 ? w->ngoals : 1);
  out[2] = 1.0 - (double)known_n / (double)NA;
  out[3] = (double)nlive / (double)POOL;
  out[4] = nlive ? ssum / (double)nlive : 0.0;
  out[5] = nlive ? smax : 0.0;
  out[6] = nlive ? smin : 0.0;
  out[7] = (double)nrules / 8.0;
#if RELOB
  {
    int k = STATE_BASE;
    for (int i = 0; i < GOAL_COUNT*GOAL_FEAT; i++) out[i + STATE_BASE] = 0.0;
    for (int g = 0; g < w->ngoals; g++){
      for (int p = 0; p < GPRED; p++) out[k++] = (w->goal_pred[g] == p) ? 1.0 : 0.0;
      for (int e = 0; e < GENT; e++) out[k++] = (w->goal_ent[g] == e) ? 1.0 : 0.0;
    }
  }
#endif
#if REMFEAT
  out[STATE_DIM-1] = (double)rem / (double)MAXBUDGET;
#endif
}

static void cand_features(const World *w, const int *rules, int nrules,
                          int cand, double out[CAND_DIM]){
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  uint64_t km = fs_load(known);
  const Rule *r = &all_rules[cand];
  int sup = support(r, known);
  int fully = (sup == r->blen);
  int head_known = (int)((km >> r->head) & 1ULL);
  int goal_pred_count = 0, goal_atom_match = 0, would_prove = 0;
  for (int g = 0; g < w->ngoals; g++){
    if (atom_pred(r->head) == w->goal_pred[g]) goal_pred_count++;
    if (r->head == GOAL_ATOM(w,g)){ goal_atom_match = 1; if (fully) would_prove = 1; }
  }
  out[0] = (double)r->blen / 2.0;
  out[1] = rule_cost(r) / 2.0;
  out[2] = r->blen ? (double)sup / (double)r->blen : 0.0;
  out[3] = (double)fully;
  out[4] = (double)head_known;
  out[5] = (double)goal_pred_count / (double)(w->ngoals > 0 ? w->ngoals : 1);
  out[6] = (double)would_prove;
  out[7] = (double)goal_atom_match;
  for (int p = 0; p < PB; p++) out[8+p] = (atom_pred(r->head) == p) ? 1.0 : 0.0;
  for (int s = 0; s < NSLOT; s++)
    for (int p = 0; p < PB; p++)
      out[8+PB + s*PB + p] = (s < r->blen && atom_pred(r->body[s]) == p) ? 1.0 : 0.0;
#if RELOB
  {
    /* goal-RELATIVE binding comparisons: no absolute entity identity enters
     * the S0 features (entity-held-out), but overlap with the goal binding is
     * visible. Absolute entity/role features are the S0e/S1 contrast. */
    int k = CAND_BASE;
    for (int g = 0; g < GOAL_COUNT; g++){
      if (g >= w->ngoals){ for (int z = 0; z < CAND_GOAL_FEAT; z++) out[k++] = 0.0; continue; }
      int gb = w->goal_ent[g], g1 = gb/EREL, g2 = gb%EREL;
      int h1 = atom_e1(r->head), h2 = atom_e2(r->head);
      int bind_overlap = (h1==g1 || h1==g2 || h2==g1 || h2==g2);
      int body_overlap = 0;
      for (int s = 0; s < r->blen; s++){
        int b1 = atom_e1(r->body[s]), b2 = atom_e2(r->body[s]);
        if (b1==g1 || b1==g2 || b2==g1 || b2==g2) body_overlap = 1;
      }
      out[k++] = (r->head == GOAL_ATOM(w,g)) ? 1.0 : 0.0;
      out[k++] = (atom_pred(r->head) == w->goal_pred[g]) ? 1.0 : 0.0;
      out[k++] = (double)bind_overlap;
      out[k++] = (double)body_overlap;
    }
  }
#endif
#if INTEGRAL
  for (int z = 0; z < 3; z++) out[PATH_OFF+z] = 0.0;   /* path integral: unary-only, inert here */
#endif
#if ENTFEAT
  {
    /* S0e: absolute entity identity per argument slot (the information S1
     * carries in tokens, here as plain numeric features) */
    int k = ENT_OFF;
    int slots[3][2];
    slots[0][0] = atom_e1(r->head); slots[0][1] = atom_e2(r->head);
    for (int s = 0; s < 2; s++){
      if (s < r->blen){ slots[s+1][0] = atom_e1(r->body[s]); slots[s+1][1] = atom_e2(r->body[s]); }
      else { slots[s+1][0] = -1; slots[s+1][1] = -1; }
    }
    for (int sl = 0; sl < 3; sl++)
      for (int q = 0; q < 2; q++)
        for (int e = 0; e < EREL; e++)
          out[k++] = (slots[sl][q] == e) ? 1.0 : 0.0;
  }
#endif
}

/* union of closure(seed + subset) over candidate subsets of size <= maxk */
static uint64_t rel_union_upto(const World *w, const uint8_t base[WENT], int maxk){
  uint64_t u = fs_load(base);
  int comb[4];
  for (int k = 1; k <= maxk && k <= 3; k++){
    for (int i = 0; i < k; i++) comb[i] = i;
    while (1){
      uint8_t tmp[WENT];
      int rules2[SEED_RULES+3];
      for (int t = 0; t < SEED_RULES; t++) rules2[t] = w->theory[t];
      for (int q = 0; q < k; q++) rules2[SEED_RULES+q] = w->cands[comb[q]];
      closure(w->facts, rules2, SEED_RULES+k, tmp);
      u |= fs_load(tmp);
      int pos = k-1;
      while (pos >= 0 && comb[pos] == POOL - k + pos) pos--;
      if (pos < 0) break;
      comb[pos]++;
      for (int q = pos+1; q < k; q++) comb[q] = comb[q-1]+1;
    }
  }
  return u;
}
#if TYPED
/* typed-token context builders: fact tokens = known atoms, obligation tokens =
 * unproved goals. Both are SETS: token order must not affect scores (gate). */
static int g_factperm[NA];
static void factperm_init(void){
  /* fixed derangement of the atom universe (seed 999, independent of training) */
  for (int a = 0; a < NA; a++) g_factperm[a] = a;
  uint64_t st = mix64(999ULL);
  for (int a = NA-1; a > 0; a--){
    st = mix64(st);
    int j = (int)(st % (uint64_t)(a+1));
    int t = g_factperm[a]; g_factperm[a] = g_factperm[j]; g_factperm[j] = t;
  }
  for (int a = 0; a < NA; a++)
    if (g_factperm[a] == a) g_factperm[a] = (a+1) % NA;   /* no fixed points */
}
static int atoms_from_known(const uint8_t *known, int *list){
  uint64_t m = fs_load(known);
  int n = 0;
  for (int a = 0; a < NA; a++) if ((m >> a) & 1ULL) list[n++] = a;
#if TYPEDSHUF
  for (int f = 0; f < n; f++) list[f] = g_factperm[list[f]];
#endif
  return n;
}
static int obligs_from_goals(const World *w, const uint8_t *known, int *list){
  int n = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (!GOAL_KNOWN(w,g,known)) list[n++] = GOAL_ATOM(w,g);
  return n;
}
#endif

#if ASSERT
/* ---- kernel adoption gate for invented assertions (Rocq assert/cut) --------
 * A proposed atom is ADOPTABLE iff, purely by kernel computation:
 *   (1) it is not already known,
 *   (2) it is goal-relevant (backward-reachable from an unproved goal through
 *       the world's candidate rules),
 *   (3) it is derivable with the live candidates (closure of theory+committed+
 *       ALL live candidates contains it),
 *   (4) its AND-OR derivation depth lower bound <= remaining budget.
 * The model never decides adoption; it only proposes. Rejection reasons are
 * counted so the rejection rate is an honest learning indicator. */
typedef struct {
  uint64_t known, reachable;
  int rel[NA];          /* goal-relevant atoms */
  int depth[NA];        /* AND-OR depth lower bound (NA = unreachable) */
} AssertCtx;

static void assert_ctx(const World *w, const int *rules, int nrules,
                       const int *live, int nlive, const uint8_t *known, AssertCtx *ax){
  ax->known = fs_load(known);
  int all[SEED_RULES + MAXBUDGET + POOL];
  int m = 0;
  for (int i = 0; i < nrules; i++) all[m++] = rules[i];
  for (int i = 0; i < nlive; i++) all[m++] = live[i];
  uint8_t kk[WENT];
  closure(w->facts, all, m, kk);
  ax->reachable = fs_load(kk);
  for (int a = 0; a < NA; a++) ax->rel[a] = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (!GOAL_KNOWN(w,g,known)) ax->rel[GOAL_ATOM(w,g)] = 1;
  for (int it = 0; it < NA; it++){
    int changed = 0;
    for (int c = 0; c < POOL; c++){
      const Rule *r = &all_rules[w->cands[c]];
      if (!ax->rel[r->head]) continue;
      for (int q = 0; q < r->blen; q++)
        if (!ax->rel[r->body[q]]){ ax->rel[r->body[q]] = 1; changed = 1; }
    }
    if (!changed) break;
  }
  /* AND-OR depth: known = 0; head of rule = 1 + max(body depths); fixpoint.
   * Lower bound on sequential commits (shared subderivations only make the
   * true cost larger), so depth <= rem is a necessary derivability condition. */
  for (int a = 0; a < NA; a++) ax->depth[a] = ((ax->known >> a) & 1ULL) ? 0 : NA;
  for (int it = 0; it < NA; it++){
    int changed = 0;
    for (int i = 0; i < m; i++){
      const Rule *r = &all_rules[all[i]];
      int mx = 0, ok = 1;
      for (int q = 0; q < r->blen; q++){
        int db = ax->depth[r->body[q]];
        if (db >= NA){ ok = 0; break; }
        if (db > mx) mx = db;
      }
      if (!ok) continue;
      int nd = mx + 1;
      if (nd < ax->depth[r->head]){ ax->depth[r->head] = nd; changed = 1; }
    }
    if (!changed) break;
  }
}

/* returns 1 if adoptable; else *why = rejection reason code
 * 0 known, 1 irrelevant, 2 unreachable, 3 too deep */
static int assert_adopt(const AssertCtx *ax, int a, int rem, int *why){
  if ((ax->known >> a) & 1ULL){ *why = 0; return 0; }
  if (!ax->rel[a]){ *why = 1; return 0; }
  if (!((ax->reachable >> a) & 1ULL)){ *why = 2; return 0; }
  if (ax->depth[a] > rem){ *why = 3; return 0; }
  *why = -1; return 1;
}

/* top adoptable proposal under the model's logits; -1 if none adoptable */
static int assert_top(const AssertCtx *ax, const double *prop, int rem){
  int best = -1;
  for (int a = 0; a < NA; a++){
    int why;
    if (!assert_adopt(ax, a, rem, &why)) continue;
    if (best < 0 || prop[a] > prop[best]) best = a;
  }
  return best;
}

/* assert-guided focus: keep candidates backward-reachable from the asserted
 * subgoal atom (Rocq: prove the assert first). Falls back to goal focus when
 * no atom is adoptable. */
static int assert_focus_filter(const World *w, const AssertCtx *ax, int a_star,
                               const int *live, int nlive, int *out){
  int rel[NA];
  for (int a = 0; a < NA; a++) rel[a] = 0;
  if (a_star >= 0){
    rel[a_star] = 1;
#if ASSERTUNION
    for (int a = 0; a < NA; a++) if (ax->rel[a]) rel[a] = 1;   /* soft: union goals */
#endif
  } else for (int a = 0; a < NA; a++) rel[a] = ax->rel[a];
  for (int it = 0; it < NA; it++){
    int changed = 0;
    for (int c = 0; c < POOL; c++){
      const Rule *r = &all_rules[w->cands[c]];
      if (!rel[r->head]) continue;
      for (int q = 0; q < r->blen; q++)
        if (!rel[r->body[q]]){ rel[r->body[q]] = 1; changed = 1; }
    }
    if (!changed) break;
  }
  int nf = 0;
  for (int k = 0; k < nlive; k++)
    if (rel[all_rules[live[k]].head]) out[nf++] = live[k];
  return nf;
}
#endif
