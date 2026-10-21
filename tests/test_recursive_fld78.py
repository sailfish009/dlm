import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from sexp import Symbol as S, dumps
from recursive_fld import run, payload
from test_reasoning78 import PROBLEM

class RecursiveFld78Tests(unittest.TestCase):
    def test_transfer_frozen_library_and_gold_isolation(self):
        renamed=[S('problem'),S('classical-prop-v1'),[[S('r'),0],[S('s'),0]],
          [S('sequent'),S('classical-prop-v1'),
           [[S('imp'),[S('pred'),S('r'),[]],[S('pred'),S('s'),[]]],[S('pred'),S('r'),[]]],
           [[S('pred'),S('s'),[]]]]]
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            for split,problem in [('train',PROBLEM),('validation',renamed)]:
                (out/f'{split}.sexp').write_text(dumps([S('fld-batch-v1'),[[0,problem]]]))
                (out/f'{split}.gold.jsonl').write_text(json.dumps(dict(row=0,proof_label='PROVED',
                    proofs_formula='NEVER_SEND_GOLD',negative_hypothesis_formula='WRONG_GOAL'))+'\n')
            before=dumps(payload(out,40,2))
            report=run(out,40,2)
            learned=report['groups']['validation/learned/pass0']; cold=report['groups']['validation/cold/pass0']
            self.assertEqual(learned['correct'],1); self.assertEqual(cold['correct'],1)
            self.assertEqual(learned['checked_reuse_hits'],1)
            self.assertLess(learned['cumulative_machine_ticks'],cold['cumulative_machine_ticks'])
            self.assertNotIn('NEVER_SEND_GOLD',(out/'runtime-input.sexp').read_text())
            self.assertNotIn('WRONG_GOAL',(out/'runtime-input.sexp').read_text())
            # Evaluation labels can change reported accuracy, never native answers/library.
            native=(out/'runtime-results.sexp').read_bytes()
            (out/'validation.gold.jsonl').write_text('{"row":0,"proof_label":"DISPROVED"}\n')
            self.assertEqual(before,dumps(payload(out,40,2)))
            changed=run(out,40,2)
            self.assertEqual((out/'runtime-results.sexp').read_bytes(),native)
            self.assertEqual(changed['groups']['validation/learned/pass0']['correct'],0)

if __name__=='__main__': unittest.main()
