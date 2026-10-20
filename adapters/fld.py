#!/usr/bin/env python3
"""FLDx2 audit/export/evaluation. Python/pyarrow are adapter-only dependencies.

Grammar audited against FLD_generator/formula.py and
formula_checkers/z3_logic_checkers/intermediates.py: binary chains are left
associative at equal precedence; quantifier scope extends to end of its group.
Gold is written separately and is never passed to Maru.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sexp import Symbol as S, dumps, loads_many

class ParseError(ValueError):
    def __init__(self, reason, offset):
        self.reason, self.offset = reason, offset
        super().__init__(f'{reason} at {offset}')

TOKEN = re.compile(r'\s+|->|#F#|\{[A-Ua-u]+\}|[()&v¬:xyzE]')

class Parser:
    def __init__(self, text):
        self.text, self.tokens, self.i = text, [], 0
        pos = 0
        while pos < len(text):
            m = TOKEN.match(text, pos)
            if not m:
                raise ParseError('unrecognized-token', pos)
            if not m.group().isspace():
                self.tokens.append((m.group(), pos))
            pos = m.end()
    def peek(self, k=0):
        return self.tokens[self.i+k][0] if self.i+k < len(self.tokens) else None
    def error(self, reason):
        raise ParseError(reason, self.tokens[self.i][1] if self.i < len(self.tokens) else len(self.text))
    def take(self, token=None):
        if self.peek() is None or (token is not None and self.peek() != token):
            self.error('expected-' + str(token))
        t = self.peek(); self.i += 1
        return t
    def expr(self, depth=0):
        if depth > 60:
            self.error('depth-limit')
        a = self.prefix(depth+1)
        while self.peek() in ('&', 'v', '->'):
            op = self.take()
            a = [S({'&':'and', 'v':'or', '->':'imp'}[op]), a, self.prefix(depth+1)]
        return a
    def prefix(self, depth):
        if depth > 60:
            self.error('depth-limit')
        t = self.peek()
        if t == '¬':
            self.take(); return [S('not'), self.prefix(depth+1)]
        if t == '(':
            self.take()
            if self.peek() in ('E', 'x', 'y', 'z'):
                exists = self.peek() == 'E'
                if exists: self.take()
                v = self.take()
                if v not in ('x', 'y', 'z'): self.error('expected-variable')
                self.take(')'); self.take(':')
                return [S('exists' if exists else 'forall'), S(v), self.expr(depth+1)]
            a = self.expr(depth+1); self.take(')'); return a
        if t == '#F#':
            self.take(); return [S('bottom')]
        if t and re.fullmatch(r'\{[A-U]+\}', t):
            self.take(); args = []
            if self.peek() and re.fullmatch(r'\{[a-u]+\}', self.peek()):
                args = [[S('const'), S('c_' + self.take()[1:-1])]]
            elif self.peek() in ('x','y','z'):
                args = [[S('var'), S(self.take())]]
            return [S('pred'), S('p_' + t[1:-1]), args]
        self.error('expected-formula')
    def parse(self):
        a = self.expr()
        if self.peek() is not None: self.error('trailing-input')
        return a

def parse(text):
    return Parser(text).parse()

def facts(text):
    # Only fact boundary identifiers are split; formula operators use the parser.
    if not text.strip(): return []
    marks = list(re.finditer(r'\bfact(\d+):\s*', text))
    if not marks or text[:marks[0].start()].strip():
        raise ParseError('expected-fact-id', 0)
    out, seen = [], set()
    for i, m in enumerate(marks):
        ident = 'fact' + m[1]
        if ident in seen: raise ParseError('duplicate-fact-id', m.start())
        seen.add(ident)
        end = marks[i+1].start() if i+1 < len(marks) else len(text)
        try:
            out.append((ident, parse(text[m.end():end])))
        except ParseError as e:
            raise ParseError(e.reason, m.end() + e.offset) from e
    return out

def signature_and_reasons(forms):
    signature, reasons = {}, set()
    def walk(f, bound=frozenset()):
        tag = f[0]
        if tag in ('forall','exists'):
            reasons.add('quantifier'); walk(f[2], bound | {f[1]})
        elif tag == 'pred':
            if f[1] in signature and signature[f[1]] != len(f[2]): reasons.add('arity-conflict')
            signature[f[1]] = len(f[2])
            for t in f[2]:
                if t[0] == 'var' and t[1] not in bound: reasons.add('free-variable')
        else:
            for child in f[1:]: walk(child, bound)
    for f in forms: walk(f)
    return [[k,v] for k,v in sorted(signature.items())], sorted(reasons)

def adapt(row):
    """Reads only allowed input fields; NEVER reads labels/proofs/negative goal."""
    try:
        if re.search(r'\bfake_formula\b', row['facts_formula']):
            return {'status':'unsupported', 'reasons':['translation-only-placeholder']}
        fs = facts(row['facts_formula'])
        goal = parse(row['hypothesis_formula'])
        sig, reasons = signature_and_reasons([f for _,f in fs] + [goal])
        if len(fs) >= 256 or len(sig) >= 1000: reasons.append('size-limit')
        if reasons: return {'status':'unsupported', 'reasons':reasons}
        root = [S('sequent'), S('classical-prop-v1'), [f for _,f in fs], [goal]]
        return {'status':'supported', 'problem':[S('problem'), S('classical-prop-v1'), sig, root],
                'occurrences':[i for i,_ in fs]}
    except ParseError as e:
        return {'status':'invalid-input', 'reasons':[e.reason], 'offset':e.offset}

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def export(data, out, limit=None, split_filter=None):
    import pyarrow.parquet as pq
    out.mkdir(parents=True, exist_ok=True)
    report = {'adapter':'fld76-v1', 'grammar':'FLD generator left-associative equal-precedence', 'splits':{}}
    for split in ('train','validation','test'):
        if split_filter and split != split_filter: continue
        path = data / f'{split}-00000-of-00001.parquet'
        file_hash = digest(path)
        stats, reasons, versions, supported = Counter(), Counter(), Counter(), []
        parquet = pq.ParquetFile(path)
        with (out/f'{split}.inputs.jsonl').open('w') as inputs, (out/f'{split}.gold.jsonl').open('w') as gold:
            index = 0
            for batch in parquet.iter_batches(batch_size=1024):
                for row in batch.to_pylist():
                    if limit is not None and index >= limit: break
                    a = adapt(row); stats[a['status']] += 1
                    reasons.update(a.get('reasons', [])); versions[row['version']] += 1
                    meta = {'split':split, 'row':index, 'version':row['version'], 'file_sha256':file_hash}
                    inputs.write(json.dumps(dict(meta, facts=row['facts'], hypothesis=row['hypothesis'],
                        facts_formula=row['facts_formula'], hypothesis_formula=row['hypothesis_formula'], **a), ensure_ascii=False)+'\n')
                    gold.write(json.dumps(dict(meta, proof_label=row['proof_label'], proofs_formula=row['proofs_formula'],
                        world_assump_label=row['world_assump_label'], negative_hypothesis=row['negative_hypothesis'],
                        negative_hypothesis_formula=row['negative_hypothesis_formula'],
                        negative_proofs=row['negative_proofs'], negative_proof_label=row['negative_proof_label']), ensure_ascii=False)+'\n')
                    if a['status'] == 'supported': supported.append([index, a['problem']])
                    index += 1
                if limit is not None and index >= limit: break
        (out/f'{split}.sexp').write_text(dumps([S('fld-batch-v1'), supported])+'\n')
        report['splits'][split] = dict(rows=index, dataset_rows=parquet.metadata.num_rows,
            columns=len(parquet.schema.names), counts=dict(stats), reasons=dict(reasons), versions=dict(versions), sha256=file_hash)
    (out/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

def evaluate(out, split, budget):
    root = Path(__file__).resolve().parents[1]
    # Only data-only input file is submitted. The gold file is opened AFTER execution.
    start = time.monotonic()
    with (out/f'{split}.sexp').open() as f:
        proc = subprocess.run([str(root/'scripts/fld.sh'), str(budget)], stdin=f, text=True, capture_output=True, check=True)
    elapsed = time.monotonic()-start
    (out/f'{split}.results.sexp').write_text(proc.stdout)
    rows = loads_many(proc.stdout)
    gold = {r['row']:r for r in map(json.loads,(out/f'{split}.gold.jsonl').read_text().splitlines())}
    counts, correct, cost = Counter(), 0, 0
    for tag, index, classification in rows:
        if tag != 'fld-result': raise ValueError('unexpected runtime result')
        label = str(classification[1]); counts[label] += 1
        correct += label == gold[index]['proof_label']
        cost += classification[2][3] + classification[3][3]
    report = dict(split=split, selection='first N rows, no label filtering', evaluated_supported=len(rows),
                  selected_total=len(gold), counts=dict(counts), correct=correct,
                  supported_accuracy=correct/len(rows) if rows else None,
                  coverage=len(rows)/len(gold) if gold else None, search_obligations=cost,
                  budget_per_direction=budget, policy='fixed', training=False, wall_seconds=elapsed)
    (out/f'{split}.evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=Path('/research/FLDx2/data'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--limit', type=int)
    p.add_argument('--split', choices=['train','validation','test'])
    p.add_argument('--evaluate', action='store_true')
    p.add_argument('--budget', type=int, default=1000)
    args = p.parse_args()
    if args.limit is not None and args.limit < 1: p.error('--limit must be positive')
    print(json.dumps(export(args.data,args.out,args.limit,args.split),indent=2))
    if args.evaluate:
        if not args.split: p.error('--evaluate requires --split')
        print(json.dumps(evaluate(args.out,args.split,args.budget),indent=2))
if __name__ == '__main__': main()
