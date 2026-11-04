#!/usr/bin/env python3
"""Reproduce web96 lifecycle and fresh-core checks without publishing raw data.

The revision fixture is an explicitly SYNTHETIC local perturbation, not a fetched
upstream revision. This is experiment orchestration/oracle code, not a learner.
"""
import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import socket
import subprocess
import time

from sexp import Symbol as S, dumps, loads_many
from web96 import CACHE, COMMIT, ROOT, acquire, packet
from web96_experiment import oracle, raw_records


def counterfactual(record):
    raw = base64.b64decode(record['raw_base64'])
    values = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline='')))
    columns = values[0]
    found = 0
    for row in values[1:]:
        if row[columns.index('M49')] == '20':
            row[columns.index('Sub-region Code')] = '34'
            row[columns.index('Region Code')] = '142'
            found += 1
    assert found == 1
    text = io.StringIO(newline='')
    csv.writer(text, lineterminator='\n').writerows(values)
    changed = text.getvalue().encode('utf-8')
    url = record['url'].replace(COMMIT, 'f' * 40)  # Explicit test-double URL.
    return dict(record, url=url, final_url=url, fetched_at='2000-01-01T00:00:00+00:00',
                sha256=hashlib.sha256(changed).hexdigest(), raw_base64=base64.b64encode(changed).decode())


def native(driver, payload):
    start = time.perf_counter()
    child = subprocess.run([str(ROOT / 'scripts/run.sh'), 'proof', str(ROOT / 'experiments/web96' / driver)],
                           cwd=ROOT, input=dumps(payload) + '\n', capture_output=True, text=True, timeout=300)
    elapsed = time.perf_counter() - start
    if child.returncode:
        raise RuntimeError(child.stderr[-4000:])
    return child.stdout, elapsed


def check_answer(answer, content, identifier, pattern):
    assert answer[1] == 'complete'
    expected = oracle(raw_records(content)[identifier][1], pattern)
    actual = {tuple(r[1]): tuple(r[2]) for r in answer[3]}
    assert actual == expected and len(actual) == len(answer[3])
    return len(actual)


def interventions(record, output):
    p, rec2 = packet(record), counterfactual(record)
    p2 = packet(rec2)
    text, elapsed = native('interventions.l', [S('intervention-input96'), p, p2])
    forms = {str(x[0]): x[1] for x in loads_many(text)}
    for key in ('failed-ingress-unchanged96', 'definitions-preserved96', 'counterfactual-replay96', 'final-replay96', 'delayed-replay96'):
        assert forms[key] == 'true', key
    assert forms['duplicate96'][0] == 'unchanged96'
    assert forms['omitted-extraction96'][0] == forms['stale-token96'][0] == 'rejected91'
    for key in ('omitted-query96', 'tiny-budget96', 'inactive96', 'stale-document96'):
        assert forms[key][1] == 'unknown' and not forms[key][3]
    assert len(forms['delayed-before96']) == 1 and len(forms['delayed-after96']) == 2
    pattern = [[S('country-subregion96'), 0, 1], [S('subregion-region96'), 1, 2], [S('region-global96'), 2, 3]]
    for key in ('original96', 'historical96', 'restored96', 'counterfactual-answer96', 'final96'):
        source = rec2 if key == 'counterfactual-answer96' else record
        check_answer(forms[key], base64.b64decode(source['raw_base64']), 'web-row96:020', pattern)
    output.write_text(text)
    return dict(checked=True, native_wall_seconds=elapsed, revision_is_synthetic=True,
                source_sha256=p[4], synthetic_sha256=p2[4], definition_counts=[2, 2], delayed_recovery=[1, 2])


def standalone(record, experiment, output):
    d = json.loads(experiment.read_text())
    # JSON loses sexp.Symbol versus quoted string distinctions. Recover the
    # actual typed native form, not a hand-guessed reconstruction of its tags.
    demo = experiment.with_name('web96-demo.sexp')
    model = next(f[1] for f in loads_many(demo.read_text()) if f[0] == 'model96')
    analytical = next(r['model'] for r in d['runs'] if r['arm'] == 'logical96')
    assert json.loads(json.dumps(model)) == analytical
    p = packet(record)
    assert d['source_sha256'] == p[4]
    text, elapsed = native('standalone.l', [S('standalone-input96'), model, p])
    raw = base64.b64decode(record['raw_base64'])
    rows, hashes = 0, []
    forms = loads_many(text)
    for form in forms:
        if form[0] != 'query96':
            continue
        _, identifier, pattern, policy, answer = form
        rows += check_answer(answer, raw, identifier, pattern)
        hashes.append(hashlib.sha256(dumps(form).encode()).hexdigest())
    assert forms[-1][0] == 'standalone-done96' and forms[-1][1] == rows == len(hashes) == 976
    result = dict(fresh_process=True, initial_verification_cache_empty=True, training_archive_absent=True,
                  live_model_absent=True, learner_and_replay_disabled=True, attempts=len(hashes), complete=len(hashes),
                  unknown=0, complete_rows=rows, mismatches=0, native_wall_seconds=elapsed,
                  source_sha256=p[4], query_hashes=hashes)
    output.write_text(json.dumps(result, indent=2) + '\n')
    return {k: v for k, v in result.items() if k != 'query_hashes'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('interventions', 'standalone'))
    parser.add_argument('--cache', type=Path, default=CACHE)
    parser.add_argument('--experiment', type=Path, default=ROOT / 'docs/web96-experiment.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    def denied(*a, **k):
        raise RuntimeError('network disabled during lifecycle experiments')
    socket.socket = denied
    record = acquire(args.cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = interventions(record, args.output) if args.mode == 'interventions' else standalone(record, args.experiment, args.output)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
