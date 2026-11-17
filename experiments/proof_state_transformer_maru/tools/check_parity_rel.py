#!/usr/bin/env python3
"""Independent oracle for the 0.0270 relational fixture (RELATOM=1).

Rebuilds the rule table from the SCHEMA SPEC (not from the C code), recomputes
closure as a set fixpoint (not bitmasks), recomputes S0 features/utility from
their formulas, verifies per-goal witness + reachability by independent subset
enumeration, and checks the DP labels by memo-free enumeration.

Usage:
  check_parity_rel.py --rules out/rel_rules.txt --worlds out/rel_worlds.txt \
      [--dp out/rel_dp.txt] [--label-rem 4] [--maxerr 2e-5]
Prints PARITY-REL-PASS / PARITY-REL-FAIL with counts.
"""
import argparse, itertools, sys
from itertools import combinations

E, PU, PB = 3, 3, 3
NA = PU*E + PB*E*E
OFF = PU*E

def atom_pred(a): return a//E if a < OFF else (a-OFF)//(E*E)
def atom_e1(a): return a%E if a < OFF else ((a-OFF)%(E*E))//E
def atom_e2(a): return a%E if a < OFF else (a-OFF)%E
def goal_atom(gp, ge): return OFF + gp*E*E + ge

def spec_rules():
    """Independent construction from the schema description."""
    rules = []
    for h in range(PU):
        for b in range(PU):
            if h == b: continue
            for e in range(E):
                rules.append((h*E+e, (b*E+e,)))
    for e1 in range(E):
        for e2 in range(E):
            for e3 in range(E):
                rules.append((OFF+2*E*E+e1*E+e3, (OFF+0*E*E+e1*E+e2, OFF+1*E*E+e2*E+e3)))
    for p, q in ((0,1),(1,2)):
        for e1 in range(E):
            for e2 in range(E):
                rules.append((OFF+e1*E+e2, (p*E+e1, q*E+e2)))
    return rules

def closure(facts, rules, ids):
    known = set(facts)
    while True:
        added = False
        for i in ids:
            head, body = rules[i]
            if head not in known and all(b in known for b in body):
                known.add(head); added = True
        if not added: return known

def rule_cost(r): return 0.5 + 0.75*len(r[1])

def support(r, known): return sum(1 for b in r[1] if b in known)

def utility(w, rules, committed, cand):
    before = closure(w['facts'], rules, w['theory']+committed)
    after = closure(w['facts'], rules, w['theory']+committed+[cand])
    gnew = sum(1 for ga in w['gatoms'] if ga in after and ga not in before)
    return 5.0*gnew + 0.15*len(after-before) - rule_cost(rules[cand])

def state_feats(w, rules, committed, live):
    known = closure(w['facts'], rules, w['theory']+committed)
    gk = sum(1 for ga in w['gatoms'] if ga in known)
    sups = [support(rules[c], known)/len(rules[c][1]) for c in live] or [0.0]
    ng = max(w['ngoals'], 1)
    out = [len(known)/NA, gk/ng, 1-len(known)/NA, len(live)/24,
           sum(sups)/len(sups), max(sups), min(sups), (2+len(committed))/8.0]
    for g in range(3):
        if g < w['ngoals']:
            gp, ge = w['goals'][g]
            out += [1.0 if p == gp else 0.0 for p in range(PB)]
            out += [1.0 if e == ge else 0.0 for e in range(E*E)]
        else:
            out += [0.0]*(PB+E*E)
    return out

def cand_feats(w, rules, committed, cand):
    known = closure(w['facts'], rules, w['theory']+committed)
    r = rules[cand]
    sup = support(r, known); fully = sup == len(r[1])
    hk = 1 if r[0] in known else 0
    gpc = sum(1 for gp, ge in w['goals'] if atom_pred(r[0]) == gp)
    gam = 1 if any(r[0] == goal_atom(gp, ge) for gp, ge in w['goals']) else 0
    wp = 1 if (fully and gam) else 0
    ng = max(w['ngoals'], 1)
    out = [len(r[1])/2.0, rule_cost(r)/2.0, sup/len(r[1]), float(fully), float(hk),
           gpc/ng, float(wp), float(gam)]
    out += [1.0 if atom_pred(r[0]) == p else 0.0 for p in range(PB)]
    for s in range(2):
        out += [1.0 if (s < len(r[1]) and atom_pred(r[1][s]) == p) else 0.0 for p in range(PB)]
    for g in range(3):
        if g < w['ngoals']:
            gp, ge = w['goals'][g]; g1, g2 = ge//E, ge%E
            h1, h2 = atom_e1(r[0]), atom_e2(r[0])
            bo = any(atom_e1(b) in (g1,g2) or atom_e2(b) in (g1,g2) for b in r[1])
            out += [1.0 if r[0] == goal_atom(gp,ge) else 0.0,
                    1.0 if atom_pred(r[0]) == gp else 0.0,
                    1.0 if (h1 in (g1,g2) or h2 in (g1,g2)) else 0.0,
                    1.0 if bo else 0.0]
        else:
            out += [0.0]*4
    return out

def proved_count(w, rules, ids):
    known = closure(w['facts'], rules, ids)
    return sum(1 for ga in w['gatoms'] if ga in known)

def dp_value_brute(w, rules, mask_indices, rem):
    """Max goals proved by theory + mask + up to rem extra candidates (no memo)."""
    base = w['theory'] + list(mask_indices)
    best = proved_count(w, rules, base)
    avail = [c for c in w['cands'] if c not in mask_indices]
    for k in range(1, rem+1):
        for sub in combinations(avail, k):
            v = proved_count(w, rules, base+list(sub))
            if v > best: best = v
    return best

def parse_worlds(path):
    worlds = []; cur = None
    for line in open(path):
        f = line.split()
        if not f: continue
        if f[0] == 'W':
            cur = {'split': int(f[1]), 'idx': int(f[2]), 'ngoals': int(f[3]),
                   'fallback': int(f[4]) if len(f) > 4 else 0,
                   'depth': int(f[5]) if len(f) > 5 else 2, 'steps': []}
            worlds.append(cur)
        elif f[0] == 'F': cur['facts'] = [int(x) for x in f[1:]]
        elif f[0] == 'T': cur['theory'] = [int(x) for x in f[1:]]
        elif f[0] == 'C': cur['cands'] = [int(x) for x in f[1:]]
        elif f[0] == 'G':
            cur['goals'] = [tuple(int(v) for v in x.split(':')) for x in f[1:]]
        elif f[0] == 'STEP':
            cur['steps'].append({'st': int(f[1]), 'nlive': int(f[2]), 'best': int(f[3]),
                                 'live': [int(x) for x in f[4:]], 'cf': [], 'util': []})
        elif f[0] == 'S':
            cur['steps'].append({'st': int(f[1]), 'nlive': int(f[2]), 'best': int(f[3]),
                                 'live': [int(x) for x in f[4:]], 'cf': [], 'util': []})
        elif f[0] == 'L': cur['steps'][-1]['util'] = [float(x) for x in f[1:]]
        elif f[0] == 'STATE': cur['steps'][-1]['state'] = [float(x) for x in f[1:]]
        elif f[0] == 'CF':
            u = f.index('U')
            cur['steps'][-1]['cf'].append((int(f[1]), [float(x) for x in f[2:u]], float(f[u+1])))
    for w in worlds:
        fm = 0
        for i, b in enumerate(w['facts']): fm |= b << (8*i)
        w['facts'] = [a for a in range(NA) if (fm >> a) & 1]
        w['gatoms'] = [goal_atom(gp, ge) for gp, ge in w['goals']]
    return worlds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rules', required=True)
    ap.add_argument('--worlds', required=True)
    ap.add_argument('--dp')
    ap.add_argument('--label-rem', type=int, default=4)
    ap.add_argument('--maxerr', type=float, default=2e-5)
    a = ap.parse_args()

    # 1. rule table vs independent schema construction
    hdr = open(a.rules).readline().split()
    assert hdr[0] == 'RELATOM' and hdr[1] == '1', 'rules dump must be RELATOM=1'
    dumped = {}
    for line in open(a.rules):
        f = line.split()
        if f[0] == 'R':
            body = tuple(int(x) for x in f[3:3+int(f[5])])
            dumped[int(f[1])] = (int(f[2]), body)
    spec = spec_rules()
    assert len(spec) == len(dumped), f'rule count {len(spec)} != {len(dumped)}'
    for i, r in enumerate(spec):
        assert dumped[i] == r, f'rule {i}: spec {r} != dumped {dumped[i]}'
    rules = spec
    print(f'RULES-PASS {len(rules)} ground rules match the independent schema construction')

    worlds = parse_worlds(a.worlds)
    maxerr = 0.0; nfeat = 0; nutil = 0; nwit = 0; nreach = 0; bad = 0
    for w in worlds:
        # 2. witness + reachability: goal derivable with ALL candidates, and not
        #    with any subset of size <= depth-1 (independent enumeration)
        allids = w['theory'] + w['cands']
        k_all = closure(w['facts'], rules, allids)
        depth = w['depth']
        shallow = set()
        for k in range(0, depth):
            for sub in combinations(w['cands'], k):
                shallow |= closure(w['facts'], rules, w['theory']+list(sub))
        for ga in w['gatoms']:
            nreach += 1
            if ga not in k_all:
                print(f"REACH-FAIL world {w['idx']} goal {ga} unreachable even with all candidates"); bad += 1
            nwit += 1
            if ga in shallow:
                print(f"WITNESS-FAIL world {w['idx']} goal {ga} derivable with <{depth} candidates"); bad += 1
        # 3. per-step features / utility / best
        committed = []
        for st in w['steps']:
            live = st['live']
            sf = state_feats(w, rules, committed, live)
            for x, y in zip(sf, st['state']):
                maxerr = max(maxerr, abs(x-y)); nfeat += 1
                if abs(x-y) > a.maxerr:
                    print(f"STATE-FAIL world {w['idx']} step {st['st']}: {x} vs {y}"); bad += 1
            for rid, cf, u in st['cf']:
                cfx = cand_feats(w, rules, committed, rid)
                for x, y in zip(cfx, cf):
                    maxerr = max(maxerr, abs(x-y)); nfeat += 1
                    if abs(x-y) > a.maxerr:
                        print(f"CF-FAIL world {w['idx']} step {st['st']} cand {rid}: {x} vs {y}"); bad += 1
                ux = utility(w, rules, committed, rid)
                nutil += 1
                if abs(ux-u) > a.maxerr:
                    print(f"UTIL-FAIL world {w['idx']} step {st['st']} cand {rid}: {ux} vs {u}"); bad += 1
            if live[st['best']] != max(live, key=lambda c: utility(w, rules, committed, c)):
                print(f"BEST-FAIL world {w['idx']} step {st['st']}"); bad += 1
            committed.append(live[st['best']])
    print(f'FEATURES checked={nfeat} utility={nutil} maxerr={maxerr:.2e}')
    print(f'WITNESS-REACH goals={nwit} reachability={nreach} violations={bad}')

    # 4. DP labels (cross-language, memo-free enumeration)
    if a.dp:
        dpw = parse_worlds(a.dp)
        ndp = 0; dpbad = 0; dperr = 0.0
        for w in dpw:
            committed = []
            for st in w['steps']:
                rem = max(a.label_rem - st['st'], 0)
                mask_ids = committed
                for k, rid in enumerate(st['live']):
                    v = dp_value_brute(w, rules, mask_ids+[rid], max(rem-1, 0))
                    lab = 5.0*v/max(w['ngoals'], 1)
                    got = st['util'][k]
                    ndp += 1; dperr = max(dperr, abs(lab-got))
                    if abs(lab-got) > a.maxerr:
                        print(f"DP-FAIL world {w['idx']} step {st['st']} cand {rid}: oracle {lab} vs C {got}"); dpbad += 1
                committed.append(st['live'][st['best']])
        print(f'DP-LABELS checked={ndp} mismatches={dpbad} maxerr={dperr:.2e}')
        bad += dpbad

    if bad:
        print(f'PARITY-REL-FAIL violations={bad}')
        sys.exit(1)
    print('PARITY-REL-PASS')

if __name__ == '__main__':
    main()