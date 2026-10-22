#!/usr/bin/env python3
"""Run the native operating-rule probe and account for its representation costs."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'experiments/space/output')
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    state=(a.out/'space.sexp').resolve()
    driver=(ROOT/'experiments/space/run.l').read_text()
    driver+='\n(assert (d77-write '+json.dumps(str(state))+ ' probe) "inspection dump")\n'
    before=resource.getrusage(resource.RUSAGE_CHILDREN);begin=time.monotonic()
    with tempfile.NamedTemporaryFile(mode='w',suffix='.l') as f:
        f.write(driver);f.flush()
        proc=subprocess.run([str(ROOT/'scripts/run.sh'),'proof',f.name],text=True,capture_output=True,timeout=180)
    elapsed=time.monotonic()-begin;after=resource.getrusage(resource.RUSAGE_CHILDREN)
    (a.out/'report.sexp').write_text(proc.stdout);(a.out/'stderr.txt').write_text(proc.stderr)
    proc.check_returncode()
    report=dict(purpose='local operating rules, structural reuse, and definition formation; no benchmark promotion',
        model='DLM0079, classical-prop-v1',wall_seconds=elapsed,
        user_seconds=after.ru_utime-before.ru_utime,system_seconds=after.ru_stime-before.ru_stime,
        max_rss_kib=after.ru_maxrss,rss_scope='child high-water mark; standalone CLI has one native child',
        serialized_inspection_state_bytes=state.stat().st_size,
        inspection_state_sha256=hashlib.sha256(state.read_bytes()).hexdigest(),
        report_sha256=hashlib.sha256(proc.stdout.encode()).hexdigest(),
        note='State is an inspection dump, not a trusted restart snapshot. Includes boundary certificates and retained jobs. '
             'Event counts are not primitive or elapsed-time budgets. No physical parallelism, compression or brain-equivalence claim.')
    (a.out/'resources.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
