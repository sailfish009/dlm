#!/usr/bin/env python3
"""Verify actual predecessor preservation, product boundary and 0095 evidence.
Does not rerun or replace native tests. Hashes prove artifact consistency only.
"""
from __future__ import annotations
import ast
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/composition95-evidence'
sys.path.insert(0, str(ROOT / 'adapters'))
from sexp import loads_many


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode()


def inventory(root):
    return sorted({n for n in git(root, 'ls-files', '-co', '--exclude-standard', '-z').split('\0')
                   if n and (root / n).is_file()})


def main():
    predecessors = json.loads((EVIDENCE / 'predecessors.json').read_text())
    preservation = {}
    for version, old in predecessors.items():
        root = Path(old['root'])
        current = inventory(root)
        assert current == sorted(old['files']), (version, 'inventory changed')
        assert git(root, 'status', '--porcelain=v1', '-uall') == old['status'], version
        assert all(digest(root / n) == h for n, h in old['files'].items()), version
        assert digest(root / 'maru-compiler') == old['compiler'], version
        preservation[version] = {'actual_files_unchanged': len(current), 'status_unchanged': True,
                                 'compiler_unchanged': True}
    old = predecessors['0094']
    inherited = [n for n, h in old['files'].items() if not (ROOT / n).is_file() or digest(ROOT / n) != h]
    expected = ['README.md', 'VERSION', 'scripts/run.sh', 'src/dlm/attention92-control.l',
                'src/dlm/attention92-ir.l', 'src/dlm/basis91-check.l', 'src/dlm/basis91-formation.l',
                'src/dlm/basis91-ir.l', 'src/dlm/basis91-plan.l', 'src/dlm/basis91-session.l']
    assert sorted(inherited) == sorted(expected), inherited
    assert (ROOT / 'VERSION').read_text() == '0.0095\n'
    assert digest(ROOT / 'README-0094.md') == old['files']['README.md']
    assert digest(ROOT / 'maru-compiler') == old['compiler']
    boundary = json.loads((EVIDENCE / 'version-boundary.json').read_text())
    assert boundary['stage'] == 'copy_before_implementation' and boundary['matched_files'] == len(old['files']) == 562
    preservation['successor'] = {'changed_inherited_paths': inherited,
                                 'compiler_unchanged': True, 'README_archive_matches': True}
    (EVIDENCE / 'preservation.json').write_text(json.dumps(preservation, indent=2) + '\n')

    statuses = json.loads((EVIDENCE / 'suite-status.json').read_text())
    assert all(v == 0 for v in statuses['exit_codes'].values()), statuses
    for filename, count in [('typed-tests.log', 26), ('offline-tests.log', 264)]:
        text = (EVIDENCE / filename).read_text()
        assert re.search(rf'Ran {count} tests in [\d.]+s\n\nOK(?:\n|$)', text), filename
        assert 'FAIL:' not in text and 'ERROR:' not in text, filename
    offline = (EVIDENCE / 'offline-tests.log').read_text()
    assert '264 tests; 6 legacy local-HTTP tests excluded' in offline
    stores = (EVIDENCE / 'store-runtime-tests.log').read_text()
    assert 'store=0 runtime=0 graph=0' in stores
    assert 'ERROR:' not in (EVIDENCE / 'native-tests.log').read_text()

    report = json.loads((ROOT / 'docs/composition95-experiment.json').read_text())
    runs = report['runs']
    assert len(runs) == 40 and report['sequential']
    assert len({(r['seed'], r['branch'], r['arm'], r['repeat']) for r in runs}) == 40
    hashes = defaultdict(set)
    total = defaultdict(int)
    arms = defaultdict(lambda: defaultdict(int))
    for r in runs:
        assert r['queries'] == 12
        assert all(r['checks'][1:])
        assert r['counts']['mismatches'] == 0 and r['max_absolute_error'] < .002
        hashes[r['seed']].add(r['data_sha256'])
        for k, v in r['counts'].items():
            total[k] += v
            arms[r['arm']][k] += v
        kinds = [m[0] for m in r['library']]
        if r['arm'] in ('shared95', 'logical95'):
            assert kinds == ['basis91', 'numeric95', 'numeric95', 'numeric95', 'composite95', 'composite95']
            assert r['library'][-1][4] == [['output95', 5]]
            assert r['library'][3][6] == ['paired95', f"channel-c-{r['seed']}", 1, [['measure95', 0], ['measure95', 2]]]
            assert r['counts']['complete'] == 12
        elif r['arm'] == 'no-output95':
            assert len(r['library']) == 7 and r['profile'][1:4] == [1, 4, 2]
            assert r['library'][-1][4] == [['measure95', 0], ['measure95', 2]]
            assert r['counts']['complete'] == 12
        else:
            assert r['counts']['unknown'] == 12 and r['counts']['complete'] == 0
            assert r['profile'][3] == 0
    assert all(len(h) == 1 for h in hashes.values())
    assert dict(total) == {'complete': 288, 'unknown': 192, 'checked_rows': 2592, 'mismatches': 0}, dict(total)
    for seed in (0, 1):
        for branch in ('principal93', 'lower93'):
            for repeat in (0, 1):
                group = {r['arm']: r for r in runs if (r['seed'], r['branch'], r['repeat']) == (seed, branch, repeat)}
                assert group['shared95']['library'][1:] == group['logical95']['library'][1:]
                assert group['shared95']['library'][0][3][0] == 'encoded91'
                assert group['logical95']['library'][0][3][0][0] == 'fact91'

    demo = ROOT / 'docs/composition95-demo.sexp'
    assert demo.read_bytes() == (ROOT / 'docs/composition95-input-demo.sexp').read_bytes()
    records = loads_many(demo.read_text())
    assert next(r for r in records if r[0] == 'profile95')[1][1:4] == [1, 3, 2]
    intervention_records = loads_many((ROOT / 'docs/composition95-interventions.sexp').read_text())
    probes = {r[0]: r for r in intervention_records}
    assert probes['omitted-worker95'][1][0] == 'rejected95'
    assert probes['missing95'][1][1] == probes['budget95'][1][1] == 'unknown'
    assert probes['counterexample95'][1][1] == probes['counterexample95'][2][1] == 'unknown'
    assert probes['counterexample95'][-1] == 'complete'
    assert probes['definition-vs-application95'][2:5:2] == ['complete', 'unknown']
    assert probes['replay95'][1]

    files = inventory(ROOT)
    products = [n for n in files if '-evidence/' not in n and n not in {
        'docs/composition95-demo.sexp', 'docs/composition95-input-demo.sexp',
        'docs/composition95-interventions.sexp', 'docs/composition95-experiment.json'}]
    products.append('docs/composition95-evidence/final_check.py')
    products = sorted(set(products))
    for n in products:
        p = ROOT / n
        if p.suffix == '.py':
            ast.parse(p.read_text(), filename=n)
        if p.suffix == '.sh':
            subprocess.run(['bash', '-n', str(p)], check=True)
        if n in expected or n not in old['files']:
            if p.suffix in ('.py', '.l', '.md', '.sh', '.sexp'):
                assert all(line == line.rstrip() for line in p.read_text().splitlines()), n
    subprocess.run(['git', '-C', str(ROOT), 'diff', '--check'], check=True)
    links = []
    for n in ('README.md', 'docs/composition95-design.md', 'docs/release-0095.md'):
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', (ROOT / n).read_text()):
            if link.startswith(('http:', 'https:', '#')):
                continue
            target = (ROOT / n).parent / link.split('#')[0]
            if target == EVIDENCE / 'final-checks.json':
                continue  # output of this checker, verified after creation below
            assert target.exists(), (n, link)
            links.append((n, link))
    source_manifest = EVIDENCE / 'source.sha256'
    source_manifest.write_text(''.join(f'{digest(ROOT / n)}  {n}\n' for n in products))
    artifacts = {p.relative_to(ROOT).as_posix() for p in EVIDENCE.rglob('*') if p.is_file()
                 and p.name not in ('SHA256SUMS', 'final_check.py')}
    artifacts |= {'docs/composition95-demo.sexp', 'docs/composition95-input-demo.sexp',
                  'docs/composition95-interventions.sexp', 'docs/composition95-experiment.json',
                  'docs/composition95-evidence/final-checks.json'}
    summary = {'preservation': preservation, 'tests': {'offline': 264, 'new': 26, 'excluded_http': 6},
               'experiment': dict(total), 'runs': 40, 'product_hashes': len(products),
               'artifact_hashes': len(artifacts), 'local_links_checked': len(links),
               'syntax_whitespace_and_diff_check': True, 'demo_input_byte_identical': True}
    (EVIDENCE / 'final-checks.json').write_text(json.dumps(summary, indent=2) + '\n')
    assert (EVIDENCE / 'final-checks.json').exists()
    (EVIDENCE / 'SHA256SUMS').write_text(''.join(f'{digest(ROOT / n)}  {n}\n' for n in sorted(artifacts)))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
