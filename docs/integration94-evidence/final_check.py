"""Verify the actual copy boundary, final products, regression logs and evidence."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
records = json.loads((HERE/'predecessors.json').read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


preservation = {}
for version, record in records.items():
    old = Path(record['root'])
    for name, expected in record['files'].items():
        assert digest(old/name) == expected, ('predecessor changed',version,name)
    status = subprocess.check_output(['git','status','--porcelain=v1','-uall'],cwd=old).decode()
    assert status == record['status'], ('status changed',version)
    assert digest(old/'maru-compiler') == record['compiler']
    preservation[version] = {'files':len(record['files']),'status_preserved':True,
                             'files_preserved':True,'compiler_preserved':True}
record = records['0093']
changed = sorted(name for name,expected in record['files'].items() if digest(ROOT/name)!=expected)
expected = ['README.md','VERSION','scripts/run.sh','src/dlm/attention92-execution.l',
            'src/dlm/attention92-ir.l','src/dlm/basis91-check.l','src/dlm/basis91-execution.l',
            'src/dlm/basis91-formation.l','src/dlm/basis91-ir.l','src/dlm/basis91-session.l']
assert changed == expected, changed
assert digest(ROOT/'maru-compiler') == record['compiler']
assert digest(ROOT/'README-0093.md') == record['files']['README.md']
assert (ROOT/'VERSION').read_text().strip() == '0.0094'
(HERE/'preservation.json').write_text(json.dumps({'predecessors':preservation,
  'successor_inherited_changes':changed,'compiler_unchanged':True,'readme_archived':True},indent=2)+'\n')

# Current nonignored product inventory, not stale historical release manifests.
files = set(subprocess.check_output(['git','ls-files','-co','--exclude-standard','-z'],cwd=ROOT).decode().split('\0'))
products = sorted(name for name in files if name and (ROOT/name).is_file() and
  ('/' not in name or name.startswith(('src/','scripts/','adapters/','tests/','experiments/')) or
   (name.startswith('docs/') and name.count('/')==1 and name.endswith('.md'))))
for name in products:
    if name.endswith('.py'): ast.parse((ROOT/name).read_text(),filename=name)
subprocess.run(['bash','-n',str(ROOT/'scripts/run.sh')],check=True)
subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
new = [n for n in products if n not in record['files']]
for name in new+changed:
    if Path(name).suffix in ('.md','.l','.py','.sh'):
        for line in (ROOT/name).read_text().splitlines():
            assert line == line.rstrip(), ('trailing whitespace',name)
links = 0
for name in ('README.md','docs/integration94-design.md','docs/release-0094.md'):
    path = ROOT/name
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        if re.match(r'^[a-z]+://',target) or target.startswith('#'): continue
        destination = path.parent/target.split('#')[0]
        # The release links to this checker's own output; verify it after write.
        assert destination.exists() or destination == HERE/'final-checks.json', (name,target)
        links += 1

report = json.loads((ROOT/'docs/integration94-experiment.json').read_text())
assert report['fresh_native_processes'] == 56 and len(report['runs']) == 56
assert report['total_queries'] == 1344 and report['mismatches'] == 0
assert report['finite_circuits']['checks'] == 28 and report['finite_circuits']['mismatches'] == 0
for arm in ('logical94','eml94'):
    runs = [r for r in report['runs'] if r['arm']==arm]
    assert len(runs)==16 and all(r['complete']==24 and r['basis_count']==2 for r in runs)
for logical in [r for r in report['runs'] if r['arm']=='logical94']:
    coded = next(r for r in report['runs'] if r['arm']=='eml94' and
        (r['family'],r['seed'],r['branch']) == (logical['family'],logical['seed'],logical['branch']))
    assert logical['data_sha256'] == coded['data_sha256']
    assert logical['basis_patterns'] == coded['basis_patterns']
    assert coded['body_formats'] == ['eml94','eml94']
for arm in ('no-prefix94','no-feedback94','no-execution94'):
    runs = [r for r in report['runs'] if r['arm']==arm]
    assert len(runs)==8 and all(r['basis_count']==1 for r in runs)
for name,count in [('offline-tests.log',238),('integration-tests.log',25)]:
    text = (HERE/name).read_text()
    assert f'Ran {count} tests' in text and '\nOK\n' in text, name
assert 'OFFLINE_EXIT=0' in (HERE/'offline-tests.log').read_text()
assert 'NATIVE_EXIT=0' in (HERE/'native-tests.log').read_text()
for marker in ('STORE_EXIT=0','RUNTIME_EXIT=0','GRAPH_STORE_EXIT=0'):
    assert marker in (HERE/'store-runtime-tests.log').read_text(), marker
assert (ROOT/'docs/integration94-demo.sexp').read_bytes() == (ROOT/'docs/integration94-input-demo.sexp').read_bytes()
checks = {'predecessors':preservation,'inherited_changed_files':changed,'product_hashes':len(products),
          'local_links':links,'python_ast':True,'shell_syntax':True,'whitespace':True,
          'offline_tests':238,'new_tests':25,'graph_oracle_complete_checks':6144,
          'finite_circuit_checks':28,'experiment_processes':56,
          'experiment_complete_checks':report['complete_checks'],
          'experiment_unknown':report['unknown'],'experiment_pending':report['pending'],
          'mismatches':0,'compiler_preserved':True,
          'manifest_scope':'Actual copy-time/current nonignored products (root/source/adapter/script/test/experiment/root docs markdown); evidence artifacts separately.'}
(HERE/'source.sha256').write_text(''.join(f'{digest(ROOT/name)}  {name}\n' for name in products))
(HERE/'final-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
assert (HERE/'final-checks.json').is_file()
artifacts = sorted(p for p in HERE.iterdir() if p.is_file() and p.name!='SHA256SUMS')
artifacts += [ROOT/'docs'/name for name in ('integration94-experiment.json','integration94-demo.sexp',
                                          'integration94-input-demo.sexp','integration94-interventions.sexp')]
(HERE/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT)}\n' for p in artifacts))
print(json.dumps(checks | {'artifact_hashes':len(artifacts)},indent=2))
