#!/usr/bin/env python3
"""Sequential CPU web-to-basis experiments; independent raw-CSV assignment oracle."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import itertools
import json
from pathlib import Path
import resource
import socket
import subprocess
import time

from sexp import Symbol as S, dumps, loads_many
from web96 import CACHE, ROOT, acquire, packet

ARMS = ('logical96', 'eml96', 'no-prefix96', 'no-formation96', 'no-extraction96')


def raw_records(raw):
    # Independent of extraction worker views, token spans and native parser.
    result = {}
    for no, row in enumerate(csv.DictReader(io.StringIO(raw.decode('utf-8'), newline='')), 1):
        fields = [row[k] for k in ('M49', 'Sub-region Code', 'Region Code', 'Global Code')]
        if not all(x.isascii() and x.isdigit() and 0 < int(x) < 1000 and len(x) <= 3 for x in fields):
            continue
        c, s, r, g = [x.zfill(3) for x in fields]
        result['web-row96:' + c] = (no, [
            ('country-subregion96', 'country:' + c, 'subregion:' + s),
            ('subregion-region96', 'subregion:' + s, 'region:' + r),
            ('region-global96', 'region:' + r, 'global:' + g)])
    return result


def oracle(facts, pattern):
    # Enumerate original fact IDs and enforce variable bindings, including aliases.
    rows = {}
    arity = 1 + max(v for atom in pattern for v in atom[1:])
    for ids in itertools.product(range(len(facts)), repeat=len(pattern)):
        bindings, valid = {}, True
        for atom, fid in zip(pattern, ids):
            fact = facts[fid]
            if str(atom[0]) != fact[0]:
                valid = False
                break
            for role, value in zip(atom[1:], fact[1:]):
                if role in bindings and bindings[role] != value:
                    valid = False
                    break
                bindings[role] = value
            if not valid:
                break
        if valid:
            rows.setdefault(tuple(bindings[i] for i in range(arity)), tuple(ids))
    return rows


def run(p, arm='logical96', queries=244, policies=('adaptive92', 'raw96'), *, raw=None):
    payload = [S('web-run96'), p, S(arm), queries, [S(x) for x in policies]]
    encoded = dumps(payload) + '\n'
    started = time.perf_counter()
    child = subprocess.run([str(ROOT / 'scripts/run.sh'), 'web96-input'], cwd=ROOT,
                           input=encoded, capture_output=True, text=True, timeout=300)
    wall = time.perf_counter() - started
    if child.returncode:
        raise RuntimeError(f'native exit {child.returncode}: {child.stderr[-4000:]}')
    forms = loads_many(child.stdout)
    summary = next(f for f in forms if f[0] == 'summary96')
    model = next(f[1] for f in forms if f[0] == 'model96')
    assert next(f[1] for f in forms if f[0] == 'replay96') == 'true'
    assert forms[-1][0] == 'done96' and forms[-1][1] == min(queries, len(p[7][4]))
    records = raw_records(raw if raw is not None else bytes.fromhex(p[6]))
    complete = unknown = nrows = mismatches = 0
    results = []
    for f in forms:
        if f[0] != 'query96':
            continue
        _, identifier, pattern, policy, answer = f
        if answer[1] == 'unknown':
            unknown += 1
            assert not answer[3]
        elif answer[1] == 'complete':
            complete += 1
            no, facts = records[identifier]
            expected = oracle(facts, pattern)
            actual = {tuple(r[1]): tuple(r[2]) for r in answer[3]}
            wrong = actual != expected or len(actual) != len(answer[3])
            scope = answer[4]
            wrong |= scope[1] != 'country-codes96' or scope[2] != 1 or scope[3] != p[4] or scope[5] != identifier or scope[6] != [no]
            wrong |= answer[2] != 'source-claims96'
            mismatches += int(wrong)
            nrows += len(actual)
        else:
            raise AssertionError(answer)
        results.append(dict(view=identifier, pattern=pattern, policy=policy, answer=answer))
    if arm == 'no-extraction96':
        assert unknown == len(results) and complete == 0
    else:
        assert complete == len(results) and unknown == 0
    assert mismatches == 0
    expected_defs = {'logical96': 2, 'eml96': 2, 'no-prefix96': 1, 'no-formation96': 0, 'no-extraction96': 0}[arm]
    assert len(model[3]) == summary[2] == expected_defs
    if arm in ('logical96', 'eml96'):
        assert model[3][1][2] == [[S('country-subregion96'), 0, 1], [S('subregion-region96'), 1, 2], [S('region-global96'), 2, 3]]
    return dict(arm=arm, native_wall_seconds=wall, definitions=summary[2], active_ops=summary[3], events=summary[4],
                source_rows=summary[5], unresolved=summary[6], attempts=len(results), complete=complete, unknown=unknown,
                complete_rows=nrows, mismatches=mismatches, core_json_bytes=len(json.dumps(model, separators=(',', ':')).encode()),
                model=model, results=results), child.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=CACHE)
    parser.add_argument('--queries', type=int, default=244)
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.queries <= 244 or not 1 <= args.repeats <= 10:
        parser.error('queries 1..244 and repeats 1..10 required')
    # Offline Python guard is not an OS-wide sandbox.
    def denied(*a, **k):
        raise RuntimeError('network disabled during experiments')
    socket.socket = denied
    record = acquire(args.cache)
    p = packet(record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    runs = []
    for repeat in range(args.repeats):
        for arm in ARMS:
            result, text = run(p, arm, args.queries)
            result['repeat'] = repeat
            runs.append(result)
            print(json.dumps({k: result[k] for k in ('arm', 'repeat', 'complete', 'unknown', 'mismatches', 'native_wall_seconds')}), flush=True)
            if repeat == 0 and arm == 'logical96':
                # Compact demo, no raw copyrighted CSV or full input packet.
                first = loads_many(text)
                demo = [f for f in first if f[0] != 'query96'] + [f for f in first if f[0] == 'query96'][:4]
                (args.output.parent / 'web96-demo.sexp').write_text('\n'.join(dumps(f) for f in demo) + '\n')
    output = dict(version='0.0096', source_url=p[2], source_sha256=p[4], native_network=False,
                  raw_bytes=len(bytes.fromhex(p[6])), source_rows=p[7][6], eligible=4 + len(p[7][4]), unresolved=p[7][5],
                  queries_per_run=args.queries, repeats=args.repeats, policies=['adaptive92', 'raw96'],
                  child_high_water_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  data_sha256=hashlib.sha256(dumps(p).encode()).hexdigest(), runs=runs)
    # Do not redistribute a derived copy of the full mixed-license M49 table.
    # Every complete answer was compared above; publish per-query hashes/counts
    # and execution metrics rather than all geographic bindings/cell contents.
    for result in output['runs']:
        compact = []
        for item in result['results']:
            answer = item['answer']
            compact.append(dict(view=item['view'], pattern=item['pattern'], policy=item['policy'],
                                status=answer[1], rows=len(answer[3]),
                                answer_sha256=hashlib.sha256(dumps(answer).encode()).hexdigest(),
                                metrics=answer[5] if answer[1] == 'complete' else []))
        result['results'] = compact
    args.output.write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
