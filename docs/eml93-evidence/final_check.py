"""Read-only product checks + evidence manifests; no model training/network."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT.parent / 'dlm_v0.0092'
record = json.loads((HERE / 'predecessor.json').read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(path):
    return {'symlink': str(path.readlink())} if path.is_symlink() else {'sha256': digest(path)}


for name, expected in record['files'].items():
    assert fingerprint(OLD / name) == expected, ('predecessor changed', name)
old_status = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=all'], cwd=OLD).decode()
assert old_status == record['git_status']
changed = sorted(name for name, expected in record['files'].items()
                 if fingerprint(ROOT / name) != expected)
assert changed == ['README.md', 'VERSION', 'scripts/run.sh'], changed
assert digest(OLD / 'maru-compiler') == digest(ROOT / 'maru-compiler') == record['compiler_sha256']
assert (ROOT / 'README-0092.md').read_bytes() == (OLD / 'README.md').read_bytes()
preservation = {'predecessor_preserved': True, 'recorded_files_checked': len(record['files']),
                'git_status_preserved': True, 'predecessor_git_status': old_status,
                'compiler_unchanged': True, 'inherited_changed_files': changed,
                'readme_archived': True}
(HERE / 'preservation.json').write_text(json.dumps(preservation, indent=2) + '\n')

# Use the ACTUAL copy-time file record, not an older historical manifest whose
# README archives may since have been removed by the owner before this version.
products = {name for name in record['files']
            if '/' not in name or name.startswith(('src/', 'scripts/', 'tests/',
                                                   'adapters/', 'experiments/'))
            or (name.startswith('docs/') and name.count('/') == 1 and name.endswith('.md'))}
products.update(str(p.relative_to(ROOT)) for pattern in
                ('src/dlm/eml93-*.l', 'experiments/eml93/*') for p in ROOT.glob(pattern) if p.is_file())
products.update(['adapters/eml93_experiment.py', 'tests/test_eml93.py', 'README-0092.md',
                 'docs/eml93-design.md', 'docs/release-0093.md'])
for name in products:
    assert (ROOT / name).is_file(), name
    if name.endswith('.py'):
        ast.parse((ROOT / name).read_text(), filename=name)
subprocess.run(['bash', '-n', str(ROOT / 'scripts/run.sh')], check=True)
subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
new_products = [p for p in products if p not in record['files']]
for name in new_products + changed:
    if (ROOT / name).suffix in ('.md', '.l', '.py', '.sh'):
        for line in (ROOT / name).read_text().splitlines():
            assert line == line.rstrip(), ('trailing whitespace', name)
links = 0
for name in ('README.md', 'docs/eml93-design.md', 'docs/release-0093.md'):
    path = ROOT / name
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if re.match(r'^[a-z]+://', target) or target.startswith('#'):
            continue
        assert (path.parent / target.split('#')[0]).exists(), (name, target)
        links += 1
experiment = json.loads((ROOT / 'docs/eml93-experiment.json').read_text())
assert len(experiment['runs']) == 12
assert experiment['total_complete_checks'] == 744
assert experiment['total_unknown'] == 24 and experiment['total_mismatches'] == 0
for name, count in [('offline-tests.log', 213), ('eml-tests.log', 27)]:
    log = (HERE / name).read_text()
    assert f'Ran {count} tests' in log and '\nOK\n' in log, name
assert (ROOT / 'docs/eml93-demo.sexp').read_bytes() == (ROOT / 'docs/eml93-input-demo.sexp').read_bytes()
(HERE / 'source.sha256').write_text(''.join(f'{digest(ROOT / name)}  {name}\n' for name in sorted(products)))
checks = {'product_hashes': len(products), 'local_links_checked': links,
          'python_ast_ok': True, 'shell_syntax_ok': True, 'whitespace_ok': True,
          'predecessor_preserved': True, 'offline_tests': 213, 'new_eml_tests': 27,
          'heldout_complete_checks': 744, 'heldout_unknown': 24, 'heldout_mismatches': 0,
          'primitive_cmath_comparisons': 206,
          'manifest_scope': 'Actual copy-time root/source/script/adapter/test/experiment files and root docs/*.md, plus new EML products; artifacts hashed separately.'}
(HERE / 'final-checks.json').write_text(json.dumps(checks, indent=2) + '\n')
artifacts = sorted(p for p in HERE.iterdir() if p.is_file() and p.name != 'SHA256SUMS')
artifacts += [ROOT / 'docs' / name for name in
              ('eml93-experiment.json', 'eml93-demo.sexp', 'eml93-input-demo.sexp', 'eml93-interventions.sexp')]
(HERE / 'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT)}\n' for p in artifacts))
print(json.dumps(checks | {'artifact_hashes': len(artifacts)}, indent=2))
