#!/usr/bin/env python3
"""Offline CPU experiment generator/oracle. No Python model learner/executor.

Same native Basis91 owner, observations and Attention92 controller across arms.
EML is a checked body representation, not an independent numeric training state.
"""
import argparse
import cmath
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import time

from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {
    'chain': ([('r',0,1),('s',1,2)], [('r',0,1),('s',1,2),('t',2,3)]),
    'fork': ([('r',0,1),('s',0,2)], [('r',0,1),('s',0,2),('t',2,3)]),
    'target': ([('r',0,1),('s',2,1)], [('r',0,1),('s',2,1),('t',1,3)]),
    'cycle': ([('r',0,1),('s',1,0)], [('r',0,1),('s',1,0),('t',0,2)]),
}


def reference(pattern, facts):
    """Exhaustive assignments; independent of native routing, joins and circuits."""
    nodes = sorted({v for f in facts for v in f[2]}, key=str)
    n = 1 + max(v for p,a,b in pattern for v in (a,b))
    available = {(f[1], *f[2]) for f in facts}
    return {values for values in itertools.product(nodes, repeat=n)
            if all((p,values[a],values[b]) in available for p,a,b in pattern)}


def fixture(family='chain', seed=0, arm='eml94', branch='principal93', policy='adaptive92'):
    rng = random.Random(9400 + seed)
    names = {p:S(f'{p}_opaque_{seed}') for p in 'rst'}
    two, three = FAMILIES[family]
    two = [[names[p],a,b] for p,a,b in two]
    three = [[names[p],a,b] for p,a,b in three]

    def episode(pattern, stem):
        facts = []
        arity = 1+max(v for p,a,b in pattern for v in (a,b))
        for group in range(2):
            values = [S(f'{stem}_{seed}_{group}_{i}') for i in range(arity)]
            facts += [[S('atom'),p,[values[a],values[b]]] for p,a,b in pattern]
        rng.shuffle(facts)
        return facts

    queries = []
    nodes = [S(f'held_{seed}_{i}') for i in range(4)]
    universe = [[S('atom'),p,[a,b]] for p,a,b in itertools.product(names.values(),nodes,nodes)]
    for i in range(24):
        p = copy_pattern = [list(atom) for atom in (two if i<12 else three)]
        facts = []
        if i % 2 == 0:
            arity = 1+max(v for _,a,b in p for v in (a,b))
            values = [rng.choice(nodes) for _ in range(arity)]
            for rel,a,b in p:
                fact = [S('atom'),rel,[values[a],values[b]]]
                if fact not in facts: facts.append(fact)
        candidates = list(universe)
        rng.shuffle(candidates)
        for fact in candidates:
            if len(facts) == 8: break
            if fact not in facts: facts.append(fact)
        rng.shuffle(facts)
        arity = 1+max(v for _,a,b in p for v in (a,b))
        perm = list(range(arity))
        rng.shuffle(perm)
        p = [[rel,perm[a],perm[b]] for rel,a,b in copy_pattern]
        rng.shuffle(p)
        queries.append([S('query94'),S(f'q{i}'),facts,p])
    return [S('integration-input94'),1,list(names.values()),episode(two,'initial'),
            episode(three,'subsequent'),queries,S(arm),S(branch),S(policy),200000]


def native(data):
    start = time.perf_counter()
    child = subprocess.run([str(ROOT/'scripts/run.sh'),'integrate94-input'],
                           input=dumps(data),text=True,capture_output=True,timeout=180)
    elapsed = time.perf_counter()-start
    if child.returncode: raise AssertionError(child.stderr[:4000]+child.stdout[:2000])
    return loads_many(child.stdout), elapsed


def validate_answer(result, facts, pattern):
    if result[0] != 'attention-result92': raise AssertionError(result)
    if result[1] != 'complete':
        if result[3]: raise AssertionError('partial output published')
        return result[1], 0
    if result[2] != pattern: raise AssertionError('changed goal')
    actual = set()
    for tag,values,ids in result[3]:
        if tag != 'match91' or len(ids) != len(pattern): raise AssertionError(result)
        for (p,a,b),index in zip(pattern,ids):
            if not isinstance(index,int) or index < 0 or index >= len(facts): raise AssertionError(ids)
            if facts[index] != [S('atom'),p,[values[a],values[b]]]: raise AssertionError((values,ids))
        if tuple(values) in actual: raise AssertionError('duplicate result')
        actual.add(tuple(values))
    want = reference(pattern,facts)
    if actual != want: raise AssertionError((pattern, facts, actual, want))
    return 'complete', len(actual)


def evaluate(family, seed, arm, branch, policy='adaptive92'):
    data = fixture(family,seed,arm,branch,policy)
    output,seconds = native(data)
    one = lambda tag: next(r for r in output if r[0]==tag)
    core = one('frozen-model94')[1]
    if not one('snapshot-valid94')[1]: raise AssertionError('invalid shared replay')
    answers = [r for r in output if r[0]=='answer94']
    if len(answers) != len(data[5]): raise AssertionError('omitted queries')
    completed = unknown = pending = witness_rows = 0
    counters = [0]*6
    called = set()
    for query,row in zip(data[5],answers):
        if query[1] != row[1]: raise AssertionError('query order')
        status,n = validate_answer(row[2],query[2],query[3])
        if status == 'complete': completed += 1
        elif status == 'unknown': unknown += 1
        elif status == 'pending': pending += 1
        else: raise AssertionError(row)
        witness_rows += n
        counters = [a+b for a,b in zip(counters,row[3][1:])]
        called.update(row[2][4][12])
    if arm in ('eml94','logical94'):
        if completed != 24 or len(core[3]) != 2: raise AssertionError(('incomplete main arm',family,arm,output))
    feedback = one('feedback94')
    return {'family':family,'seed':seed,'arm':arm,'branch':branch,'policy':policy,
            'seconds':seconds,'complete':completed,'unknown':unknown,'pending':pending,
            'mismatches':0,'witness_rows':witness_rows,'basis_count':len(core[3]),
            'basis_patterns':[b[2] for b in core[3]],
            'body_formats':[b[3][1] if b[3][0]=='encoded91' else 'logical91' for b in core[3]],
            'basis_leaf_plans':[b[3][3] if b[3][0]=='encoded91' else b[3] for b in core[3]],
            'called_basis_ids':sorted(called),
            'active_operations':sum(len(v[4]) for v in core[4]),
            'core_json_bytes':len(json.dumps(core,separators=(',',':')).encode()),
            'feedback_status':feedback[1][0], 'feedback_worker_counters':feedback[2][1:],
            'query_worker_counters':counters,
            'candidate_patterns':[c[1] for c in one('formation-candidates94')[1]],
            'formation_update':one('formation-update94')[1],
            'data_sha256':hashlib.sha256(dumps(data[2:6]).encode()).hexdigest(),
            'input_sha256':hashlib.sha256(dumps(data).encode()).hexdigest()}


def circuits():
    code = """
(list-do branch '(principal93 lower93) (list-do n '(1 2 3)
 (let ((code (e94-circuit n))) (list-do xs (e94-bit-inputs n)
  (dump (list branch code xs (e94-eval-code code xs branch 200000 false))) (print "\n")))))
"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w',suffix='.l') as f:
        f.write(code); f.flush()
        p = subprocess.run([str(ROOT/'scripts/run.sh'),'proof',f.name],text=True,capture_output=True,timeout=120)
    if p.returncode: raise AssertionError(p.stderr)
    records = loads_many(p.stdout)
    max_error = 0
    min_log_operand = float('inf')
    rows = []
    for branch,circuit,inputs,result in records:
        values = []
        def resolve(ref):
            if ref == 'one93': return 1+0j
            if ref[0] == 'x93': return complex(inputs[ref[1]][1]/1e6,0)
            return values[ref[1]]
        for tag,a,b in circuit[1]:
            if tag != 'eml93': raise AssertionError(circuit)
            aa,bb = resolve(a),resolve(b)
            if bb.real <= 0 or abs(bb.imag)>1e-9 or abs(aa.real)>6: raise AssertionError((aa,bb))
            min_log_operand = min(min_log_operand,bb.real)
            values.append(cmath.exp(aa)-cmath.log(bb))
        want = resolve(circuit[2])
        product = 1
        for _,value,_ in inputs: product *= value//1000000
        error = abs(complex(result[3][1]/1e6,result[3][2]/1e6)-want)
        max_error = max(error,max_error)
        if abs(want-product)>1e-9 or error>.002 or result[1]!='complete' or bool(result[2])!=(product==2**len(inputs)):
            raise AssertionError((inputs,result,want))
        rows.append({'branch':branch,'inputs':[x[1]//1000000 for x in inputs],
                     'EML_nodes':len(circuit[1]),'native_value':result[3],
                     'oracle_value':[want.real,want.imag],'absolute_error':error})
    return {'checks':len(records),'mismatches':0,'max_absolute_error':max_error,
            'min_oracle_log_operand':min_log_operand,'rows':rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    runs = []
    for family,seed,branch,arm in itertools.product(FAMILIES,range(2),
            ('principal93','lower93'),('logical94','eml94')):
        runs.append(evaluate(family,seed,arm,branch))
        print(f'{family} seed={seed} {branch} {arm}: {runs[-1]["complete"]}/24 complete',flush=True)
    for family,branch,arm in itertools.product(FAMILIES,('principal93','lower93'),
            ('no-prefix94','no-feedback94','no-execution94')):
        runs.append(evaluate(family,0,arm,branch))
        print(f'{family} {branch} {arm}: bases={runs[-1]["basis_count"]}, '
              f'complete={runs[-1]["complete"]}, unknown={runs[-1]["unknown"]}',flush=True)
    result = {'version':'0.0094','runs':runs,'fresh_native_processes':len(runs),'separate_finite_probe_processes':1,
              'total_queries':sum(r['complete']+r['unknown']+r['pending'] for r in runs),
              'complete_checks':sum(r['complete'] for r in runs),
              'unknown':sum(r['unknown'] for r in runs),'pending':sum(r['pending'] for r in runs),
              'mismatches':sum(r['mismatches'] for r in runs),'finite_circuits':circuits(),
              'counter_fields':['evaluations','EML_nodes','accepted','rejected','ground_calls','candidates'],
              'scope':'4 fixed structural families; 2 order/rename/query seeds; 2 explicit branch conventions. '
                      '24 new finite-source queries/run, two main arms plus 3 causal controls. '
                      'Native observation interpretation and basis learning; Python only generates/checks. '
                      'Timing includes startup/formation/validation/replay/query/output, not OS sandboxing or checkpoint I/O. '
                      'Unknowns are not scored as correct answers. Seeds are not independent task families.'}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('runs','finite_circuits')},indent=2))


if __name__ == '__main__':
    main()
