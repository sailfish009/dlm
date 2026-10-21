#!/usr/bin/env python3
"""Fixed-input FLDx2 proof-pattern learning; Maru receives no gold fields."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import time
import resource

from fld import export
from sexp import Symbol as S, dumps, loads_many

ROOT=Path(__file__).resolve().parents[1]

def payload(out, budget, passes, include_test=False):
    selected=[]
    for split in ('train','validation','test'):
        if split=='test' and not include_test:
            selected.append([])
        else:
            data=loads_many((out/f'{split}.sexp').read_text())[0]
            if data[0]!='fld-batch-v1': raise ValueError('not input-only FLD export')
            selected.append(data[1])
    return [S('fld78-run-v1'),*selected,budget,passes]

def run(out, budget, passes, include_test=False):
    config=dict(adapter='recursive-fld78-v1',budget_per_direction_per_slice=budget,
        train_passes=passes,test_enabled=include_test,selection='first N rows, no label filtering',
        scope='ground propositional only',learning='checked whole-sequent atom-renaming proof patterns',
        max_patterns=32,branch_policies=['left-first','right-first'],tuning=False)
    # Freeze configuration and input BEFORE runtime; no validation/test feedback.
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    request=dumps(payload(out,budget,passes,include_test))+'\n'
    (out/'runtime-input.sexp').write_text(request)
    cmd=[str(ROOT/'scripts/run.sh'),'proof',str(ROOT/'experiments/fld/learn.l')]
    metrics=out/'native-resources.txt'
    if Path('/usr/bin/time').exists():
        cmd=['/usr/bin/time','-f','wall_seconds=%e\nuser_seconds=%U\nsystem_seconds=%S\nmax_rss_kib=%M',
             '-o',str(metrics),*cmd]
    start=time.monotonic()
    usage_before=resource.getrusage(resource.RUSAGE_CHILDREN)
    proc=subprocess.run(cmd,input=request,text=True,capture_output=True,timeout=600)
    elapsed=time.monotonic()-start
    (out/'runtime-results.sexp').write_text(proc.stdout)
    (out/'runtime-stderr.txt').write_text(proc.stderr)
    proc.check_returncode()
    # Gold opened only after the native process exited. It never receives paths to it.
    gold={s:{r['row']:r for r in map(json.loads,(out/f'{s}.gold.jsonl').read_text().splitlines())}
          for s in ('train','validation','test') if s!='test' or include_test}
    groups={}; library=[]; jobs=[]
    for row in loads_many(proc.stdout):
        if row[0]=='fld78-library': library=row[1]; continue
        if row[0]=='fld78-training-state': jobs=row[1]; continue
        tag,split,arm,passno,index,label,poscost,negcost,posreuse,negreuse=row
        if tag!='fld78-result': raise ValueError('unexpected native result')
        key=f'{split}/{arm}/pass{passno}'
        g=groups.setdefault(key,dict(counts=Counter(),correct=0,evaluated_supported=0,
            cumulative_machine_ticks=0,checked_reuse_hits=0,selected_total=len(gold[split])))
        g['counts'][str(label)]+=1
        g['correct']+=label==gold[split][index]['proof_label']
        g['evaluated_supported']+=1
        g['cumulative_machine_ticks']+=poscost+negcost
        g['checked_reuse_hits']+=posreuse+negreuse
    for g in groups.values():
        g['supported_accuracy']=g['correct']/g['evaluated_supported'] if g['evaluated_supported'] else None
        g['coverage']=g['evaluated_supported']/g['selected_total'] if g['selected_total'] else None
    usage_after=resource.getrusage(resource.RUSAGE_CHILDREN)
    native=dict(user_seconds=usage_after.ru_utime-usage_before.ru_utime,
        system_seconds=usage_after.ru_stime-usage_before.ru_stime,
        max_rss_kib=usage_after.ru_maxrss,
        rss_scope='child high-water mark in this adapter process; standalone CLI has one native child')
    if metrics.exists():
        native={k:float(v) for k,v in (line.split('=',1) for line in metrics.read_text().splitlines())}
    report=dict(config=config,groups=groups,learned_patterns=len(library),
        serialized_library_bytes=len(dumps(library).encode()),
        serialized_training_state_bytes=len(dumps(jobs).encode()),
        serialized_runtime_input_bytes=len(request.encode()),
        serialized_runtime_output_bytes=len(proc.stdout.encode()),native_resources=native,
        adapter_subprocess_wall_seconds=elapsed,
        accounting='machine ticks are cooperative frame transitions, not G3 obligations or primitive work; '
            'lookup/check/replay costs are included in wall/CPU/RSS, not ticks; '
            'RSS and timings cover the combined native training plus cold and learned evaluation; '
            'no compression or GPU/LLM equivalence claim')
    (out/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path('/research/FLDx2/data'))
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--limit',type=int,default=100)
    p.add_argument('--budget',type=int,default=200)
    p.add_argument('--passes',type=int,default=2)
    p.add_argument('--include-test',action='store_true')
    a=p.parse_args()
    if not (1<=a.limit<=1000 and 1<=a.budget<=1000 and 1<=a.passes<=10): p.error('bounded limits exceeded')
    begin=time.monotonic()
    for split in ('train','validation','test'):
        if split=='test' and not a.include_test: continue
        export(a.data,a.out,a.limit,split)
        (a.out/f'{split}.audit.json').write_bytes((a.out/'audit.json').read_bytes())
    result=run(a.out,a.budget,a.passes,a.include_test)
    result['total_export_and_evaluation_wall_seconds']=time.monotonic()-begin
    (a.out/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
