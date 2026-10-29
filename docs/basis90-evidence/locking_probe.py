"""Explicit two-process native basis-store lock probe; no network."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
from test_repl import Live
from test_sequent import maru


def main():
    with tempfile.TemporaryDirectory() as directory:
        q = json.dumps(str(Path(directory) / 'basis.sexp'))
        live = Live()
        try:
            live.exchange(f"(basis90 'open {q})", rb'\(basis90 epoch 0')
            live.exchange("(basis90 'save)", rb'\(saved90\)')
            code = f'''(assert (equal (basis90 'open {q}) '(rejected90 locked-or-path)) "writer lock") (print "passed")'''
            assert maru(code) == 'passed'
            live.send('(define checkpoint-original90 b90-checkpoint)\n'
                      '(define-function checkpoint-refuse90 (path snapshot expected) false)\n'
                      '(set b90-checkpoint checkpoint-refuse90)\n')
            live.exchange("(basis90 'close)", rb'\(rejected90 checkpoint\)')
            assert maru(code) == 'passed'
            live.send('(set b90-checkpoint checkpoint-original90)\n')
            live.exchange("(basis90 'close)", rb'\(closed90\)')
            assert maru(f'''(assert (= (car (basis90 'open {q})) 'basis90) "lock released")
(basis90 'close) (print "passed")''') == 'passed'
        finally:
            output = live.close()
            assert live.p.returncode == 0, output[-4000:]
    print('PASS two-process writer exclusion, failed-close attachment, successful-close lock release')


if __name__ == '__main__':
    main()
