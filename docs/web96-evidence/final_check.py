#!/usr/bin/env python3
"""Preservation, evidence and product consistency; not a scientific-truth oracle."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'docs/web96-evidence'
CHANGED = {'README.md', 'VERSION', 'scripts/run.sh', 'adapters/web.py',
           'src/dlm/basis91-ir.l', 'src/dlm/basis91-session.l',
           'src/dlm/composition95-ir.l', 'src/dlm/composition95-session.l'}
RESULTS = {'docs/web96-experiment.json', 'docs/web96-demo.sexp', 'docs/web96-interventions.sexp'}
MARKDOWN = ['README.md', 'docs/web96-design.md', 'docs/release-0096.md', 'experiments/web96/source/README.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    predecessor = load(E / 'predecessor.json')
    previous = Path(predecessor['root'])
    assert ROOT.name == 'dlm_v0.0096' and previous.name == 'dlm_v0.0095'
    for name, value in predecessor['files'].items():
        assert sha(previous / name) == value, ('predecessor changed', name)
    status = subprocess.check_output(['git', '-C', str(previous), 'status', '--porcelain=v1', '-uall']).decode()
    assert status == predecessor['status']
    assert sha(previous / 'maru-compiler') == sha(ROOT / 'maru-compiler') == predecessor['compiler']
    assert (previous / 'maru-compiler').readlink() == (ROOT / 'maru-compiler').readlink()
    changed = {name for name, value in predecessor['files'].items() if sha(ROOT / name) != value}
    assert changed == CHANGED, changed
    assert sha(ROOT / 'README-0095.md') == predecessor['files']['README.md']
    assert (ROOT / 'VERSION').read_text() == '0.0096\n'
    boundary = load(E / 'version-boundary.json')
    assert boundary['stage'] == 'before_implementation' and boundary['matched_files'] == len(predecessor['files']) == 598
    preservation = dict(predecessor=str(previous), actual_nonignored_files=len(predecessor['files']),
                        hashes_preserved=True, status_preserved=True, compiler_preserved=True,
                        compiler_sha256=predecessor['compiler'], compiler_link=str((ROOT / 'maru-compiler').readlink()),
                        archived_readme_preserved=True, inherited_changed=sorted(changed), no_reset_or_commit=True)
    (E / 'preservation.json').write_text(json.dumps(preservation, indent=2) + '\n')
    assert all(code == 0 for code in load(E / 'suite-status.json').values())
    targeted = (E / 'web96-tests.log').read_text()
    offline = (E / 'offline-tests.log').read_text()
    assert re.search(r'Ran 26 tests in [0-9.]+s\n\nOK', targeted)
    assert re.search(r'Ran 290 tests in [0-9.]+s\n\nOK', offline)
    assert '6 legacy local-HTTP tests excluded' in offline

    d = load(ROOT / 'docs/web96-experiment.json')
    expected_hash = 'bb199ebc9636b9872705e8216f1f849359f136a7668ebfa23a3c58048462ab92'
    assert d['source_sha256'] == expected_hash and d['raw_bytes'] == 133991
    assert d['source_rows'] == 249 and d['eligible'] == 248 and len(d['unresolved']) == 1
    assert d['queries_per_run'] == 244 and d['repeats'] == 2
    assert len(d['runs']) == 10
    arms = Counter(r['arm'] for r in d['runs'])
    assert arms == dict.fromkeys(('logical96', 'eml96', 'no-prefix96', 'no-formation96', 'no-extraction96'), 2)
    for r in d['runs']:
        assert r['attempts'] == 976 and len(r['results']) == 976 and r['mismatches'] == 0
        assert not r['model'][2] and not r['model'][4]
        expected = {'logical96': 2, 'eml96': 2, 'no-prefix96': 1, 'no-formation96': 0, 'no-extraction96': 0}[r['arm']]
        assert r['definitions'] == expected == len(r['model'][3])
        assert r['native_wall_seconds'] > 0 and r['core_json_bytes'] > 0
        assert r['complete'] == (0 if r['arm'] == 'no-extraction96' else 976)
        assert r['unknown'] == (976 if r['arm'] == 'no-extraction96' else 0)
        for q in r['results']:
            assert len(q['answer_sha256']) == 64
            if r['arm'] == 'no-extraction96':
                assert q['status'] == 'unknown' and q['rows'] == 0
                continue
            assert q['status'] == 'complete' and q['rows'] == 1
            if q['policy'] == 'adaptive92':
                ids = q['metrics'][12]
                if r['arm'] in ('logical96', 'eml96'):
                    assert ids == ([1] if len(q['pattern']) == 2 else [2, 1])
                elif r['arm'] == 'no-prefix96':
                    assert ids == [1]
                else:
                    assert ids == []
        if r['arm'] in ('logical96', 'eml96'):
            body = r['model'][3][1][3]
            if body[0] == 'encoded91':
                body = body[3]
            assert body[0] == ['call91', 1, [0, 1, 2]]
    totals = {k: sum(r[k] for r in d['runs']) for k in ('attempts', 'complete', 'unknown', 'complete_rows', 'mismatches')}
    assert totals == dict(attempts=9760, complete=7808, unknown=1952, complete_rows=7808, mismatches=0)
    standalone = load(E / 'standalone.json')
    assert standalone['complete'] == standalone['complete_rows'] == standalone['attempts'] == 976
    assert standalone['unknown'] == standalone['mismatches'] == 0 and len(standalone['query_hashes']) == 976
    for key in ('fresh_process', 'initial_verification_cache_empty', 'training_archive_absent', 'live_model_absent', 'learner_and_replay_disabled'):
        assert standalone[key]
    assert standalone['source_sha256'] == expected_hash
    intervention = (ROOT / 'docs/web96-interventions.sexp').read_text()
    for marker in ('(failed-ingress-unchanged96 true)', '(definitions-preserved96 true)',
                   '(counterfactual-replay96 true)', '(final-replay96 true)', '(delayed-replay96 true)',
                   '(omitted-query96 (web-answer96 unknown incomplete-worker ()))',
                   '(inactive96 (web-answer96 unknown inactive-source ()))'):
        assert marker in intervention, marker
    assert not (ROOT / 'experiments/web96/source/country-codes.csv').exists()
    assert not re.search('[\uac00-\ud7a3]', (ROOT / 'README.md').read_text())

    names = sorted(set(subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-co', '--exclude-standard', '-z']).decode().split('\0')) - {''})
    products = [n for n in names if (ROOT / n).is_file() and n not in RESULTS and
                (not n.startswith('docs/web96-evidence/') or n == 'docs/web96-evidence/final_check.py')]
    for name in products:
        if name.endswith('.py'):
            ast.parse((ROOT / name).read_text(), filename=name)
    subprocess.run(['bash', '-n', str(ROOT / 'scripts/run.sh')], check=True)
    subprocess.run(['git', '-C', str(ROOT), 'diff', '--check'], check=True)
    own = MARKDOWN + ['adapters/web96.py', 'adapters/web96_experiment.py', 'adapters/web96_lifecycle.py', 'tests/test_web96.py']
    own += [str(p.relative_to(ROOT)) for p in (ROOT / 'src/dlm').glob('web96-*.l')]
    own += [str(p.relative_to(ROOT)) for p in (ROOT / 'experiments/web96').glob('*.l')]
    for name in own:
        assert not any(line.rstrip(' \t') != line for line in (ROOT / name).read_text().splitlines()), name
    links = []
    for name in MARKDOWN:
        for dest in re.findall(r'\[[^\]]*\]\(([^)]+)\)', (ROOT / name).read_text()):
            if re.match(r'\w+://|#|mailto:', dest):
                continue
            target = (ROOT / name).parent / dest.split('#')[0]
            if target != E / 'final-checks.json':
                assert target.exists(), (name, dest)
            links.append((name, dest))
    source_manifest = ''.join(f'{sha(ROOT / n)}  {n}\n' for n in products)
    (E / 'source.sha256').write_text(source_manifest)
    report = dict(version='0.0096', predecessor_files=598, inherited_changed=sorted(changed),
                  targeted_tests=26, offline_tests=290, legacy_http_excluded=6, suite_status=load(E / 'suite-status.json'),
                  sequential_runs=10, experiment_totals=totals, standalone_complete=976,
                  product_hashes=len(products), artifact_hashes=0, local_links=len(links), checks_passed=True)
    artifacts = sorted([str(p.relative_to(ROOT)) for p in E.iterdir() if p.is_file() and p.name not in ('SHA256SUMS', 'final_check.py')]
                       + sorted(RESULTS))
    if 'docs/web96-evidence/final-checks.json' not in artifacts:
        artifacts.append('docs/web96-evidence/final-checks.json')
        artifacts.sort()
    report['artifact_hashes'] = len(artifacts)
    (E / 'final-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    for name, dest in links:
        assert ((ROOT / name).parent / dest.split('#')[0]).exists()
    (E / 'SHA256SUMS').write_text(''.join(f'{sha(ROOT / n)}  {n}\n' for n in artifacts))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
