"""Translation checks, not an independent space79 semantic implementation."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapters'))
from space_dialect import DialectError, parse, verify, lower, run_file, format_module
from test_sequent import maru
from sexp import loads_many


class DialectTests(unittest.TestCase):
    def test_example_cli_execution(self):
        rows = loads_many(run_file(ROOT / 'experiments/space/dialect.mlir'))
        self.assertEqual(rows[0][1][3], 'done')
        self.assertEqual(rows[0][1][5][1], 'proved')

    def test_reject_bad_ssa_types_and_operations(self):
        for body in (
            '%a = space.run %missing 1',
            '%a = space.new\n%a = space.new',
            '%a = space.new : !wrong',
            'space.new',
            '%a = space.unknown',
            '%a = space.new\n%b = space.run %a -1',
            '%a = space.new\n%b = space.run %a 20001',
            '%a = space.new\n%b = space.resume %a j 42',
            '%a = space.new\n%b = space.dump %a label',
        ):
            with self.subTest(body=body), self.assertRaises(DialectError):
                lower(parse('space.module @bad {\n' + body + '\n}'))

    def test_full_state_translation(self):
        dialect = '''space.module @comparison {
%s0 = space.new
%s1 = space.define %s0 d ((p 0)) (pred p ())
%s2 = space.prove %s1 j (problem classical-prop-v1 ((p 0))
 (sequent classical-prop-v1 ((pred p ())) ((and (pred p ()) (pred p ())))))
%s3 = space.run %s2 3
space.dump %s3 prefix
%s4 = space.run %s3 997
space.dump %s4 final
%s5 = space.program %s4 enum ((choose (((accept first)) ((fail last)))))
%s6 = space.run %s5 100
%s7 = space.resume %s6 enum true
%s8 = space.run %s7 100
space.dump %s8 exhausted
%s9 = space.interpolate %s8 i ((p 0)) (pred p ()) (pred p ())
%s10 = space.run %s9 1000
%s11 = space.beth %s10 b ((p 0)) (pred p ()) (pred p ())
%s12 = space.run %s11 1000
space.dump %s12 definitions
}'''
        direct = '''(define s (d79-define (s79-new) 'd '((p 0)) '(pred p ())))
(set s (s79-proof-job s 'j '(problem classical-prop-v1 ((p 0))
 (sequent classical-prop-v1 ((pred p ())) ((and (pred p ()) (pred p ())))))))
(set s (s79-run s 3))
(dump (list 'prefix s)) (print "\\n")
(set s (s79-run s 997))
(dump (list 'final s)) (print "\\n")
(set s (s79-program-job s 'enum '((choose (((accept first)) ((fail last)))))))
(set s (s79-run s 100))
(set s (s79-program-resume s 'enum true))
(set s (s79-run s 100))
(dump (list 'exhausted s)) (print "\\n")
(set s (i79-interpolate s 'i '((p 0)) '(pred p ()) '(pred p ())))
(set s (s79-run s 1000))
(set s (i79-beth s 'b '((p 0)) '(pred p ()) '(pred p ())))
(set s (s79-run s 1000))
(dump (list 'definitions s)) (print "\\n")'''
        self.assertEqual(loads_many(maru(lower(parse(dialect)))), loads_many(maru(direct)))

    def test_strings_are_data_and_old_states_remain_available(self):
        source = '''space.module @data {
%s0 = space.new
%s1 = space.define %s0 "(print evil) // data" ((p 0)) (pred p ())
space.definitions %s1 "name // still data"
space.dump %s0 empty
}'''
        rows = loads_many(maru(lower(parse(source))))
        self.assertEqual(rows[0][1][0][0], '(print evil) // data')
        self.assertEqual(rows[1][1][12], [])

    def test_canonical_text_roundtrip(self):
        source = (ROOT / 'experiments/space/dialect.mlir').read_text()
        first = parse(source)
        canonical = format_module(first)
        second = parse(canonical)
        self.assertEqual(lower(first), lower(second))
        self.assertEqual(canonical, format_module(second))
        self.assertEqual([op.effects for op in first.ops], [op.effects for op in second.ops])

    def test_seeded_event_slices_match_direct_execution(self):
        import random
        rng = random.Random(81)
        module = ['space.module @slices {', '%s0 = space.new',
                  '%s1 = space.prove %s0 p (problem classical-prop-v1 ((p 0)) '
                  '(sequent classical-prop-v1 ((pred p ())) '
                  '((and (pred p ()) (imp (pred p ()) (pred p ()))))))']
        direct = ["(define s (s79-proof-job (s79-new) 'p '(problem classical-prop-v1 ((p 0)) "
                  "(sequent classical-prop-v1 ((pred p ())) "
                  "((and (pred p ()) (imp (pred p ()) (pred p ()))))))))"]
        for index in range(2, 32):
            budget = rng.randrange(6)
            module += [f'%s{index} = space.run %s{index-1} {budget}',
                       f'space.dump %s{index} state']
            direct += [f'(set s (s79-run s {budget}))',
                       '(dump (list \'state s)) (print "\\n")']
        module.append('}')
        self.assertEqual(loads_many(maru(lower(parse('\n'.join(module))))),
                         loads_many(maru('\n'.join(direct))))

    def test_module_boundaries(self):
        for source in ('space.module @x {', 'space.new',
                       'space.module @x {\n%s = space.new\n}\ntrailing'):
            with self.assertRaises(DialectError):
                verify(parse(source))


if __name__ == '__main__':
    unittest.main()
