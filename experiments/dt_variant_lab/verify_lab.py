#!/usr/bin/env python3
import json,re
from pathlib import Path
def row(name):
    r=json.loads((Path('variants')/name/'result.json').read_text())
    if len(r['picks'])!=10: raise SystemExit(f'{name}: len(picks)={len(r["picks"])}')
    return r
# required parity
for name in ['baseline','baseline_seed62','d16_f32_l3','d32_h2_l6','d16_h2_l3']:
    r=row(name)
    if r['matches']!=10: raise SystemExit(f'{name}: {r["matches"]}')
    print(f'{name}: parity={r["matches"]}/10 acc={r["accuracy"]}/10')
# recorded variants
for name in ['baseline_seed63','d32_h4_l6','d32_adamw_cos','d32_dropout','d32_f64_l6_noprior','d32_f64_l3']:
    r=row(name); print(f'{name}: parity={r["matches"]}/10 acc={r["accuracy"]}/10 (recorded)')
base=row('baseline'); nop=row('d32_f64_l6_noprior')
if nop['matches']!=4 or nop['accuracy']!=3: raise SystemExit('noprior expectation changed')
# prior-only control
lines=[l for l in Path('prior_only.out').read_text().splitlines() if l.startswith('PRIOR ')]
picks=[int(l.split()[-1]) for l in lines]
if len(picks)!=10: raise SystemExit(f'prior-only len {len(picks)}')
ref=json.loads(Path('../dt_full_port_no_mlir/expected_all.json').read_text())
refp=[x['pick'] for x in ref]; by={x['pick']:x.get('correct',0) for x in ref}
prior_par=sum(a==b for a,b in zip(picks,refp)); prior_acc=sum(by.get(p,0) for p in picks)
print(f'prior_only: parity={prior_par}/10 acc={prior_acc}/10')
if prior_par!=9 or prior_acc!=8: raise SystemExit('prior-only expectation changed')
print('PRIOR_SATURATED', 'yes' if prior_acc==base['accuracy'] else 'no')
# eval-time dropout must not appear in predict
src=Path('variants/d32_dropout/dt_train.c').read_text()
i=src.index('static int predict'); j=src.index('Cache cs[NLAYER];',i)
if 'DROP' in src[i:j]: raise SystemExit('dropout found in predict()')
print('EVAL_DROPOUT off')
print('V0220-VARIANT-LAB-HARDENED-PASS')
