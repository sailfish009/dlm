import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fld', ROOT/'adapters/fld.py')
fld = importlib.util.module_from_spec(spec); spec.loader.exec_module(fld)

class ParserTests(unittest.TestCase):
    def test_generator_associativity(self):
        a = fld.parse('{A} -> {B} & {C}')
        self.assertEqual(a[0], 'and'); self.assertEqual(a[1][0], 'imp')
        self.assertEqual(fld.parse('¬{A} v {B}')[1][0], 'not')
    def test_quantifier_scope(self):
        a = fld.parse('(x): {A}x -> (Ex): ({B}x & {C}x)')
        self.assertEqual(a[0], 'forall'); self.assertEqual(a[2][0], 'imp')
        self.assertEqual(a[2][2][0], 'exists')
        self.assertEqual(fld.signature_and_reasons([a])[1], ['quantifier'])
    def test_ground_and_arity(self):
        self.assertEqual(fld.adapt({'facts_formula':'fact1: {A}{a}', 'hypothesis_formula':'{A}{a}'})['status'], 'supported')
        self.assertIn('arity-conflict', fld.adapt({'facts_formula':'fact1: {A}', 'hypothesis_formula':'{A}{a}'})['reasons'])
        self.assertIn('free-variable', fld.adapt({'facts_formula':'fact1: {A}x', 'hypothesis_formula':'{A}x'})['reasons'])
    def test_full_consumption(self):
        for s in ('{A})', '({A}', '{A} garbage', '{A}{a}{b}', '{A} ->', '(): {A}', '(Ex):'):
            with self.assertRaises(fld.ParseError, msg=s): fld.parse(s)
        with self.assertRaises(fld.ParseError): fld.facts('fact1: {A} fact1: {B}')
    def test_no_gold_dependency(self):
        class Guard(dict):
            def __getitem__(self, key):
                if key not in ('facts_formula','hypothesis_formula'): raise AssertionError('gold access')
                return super().__getitem__(key)
        row = Guard(facts_formula='fact1: {A}', hypothesis_formula='{B}', proof_label='DISPROVED')
        self.assertEqual(fld.adapt(row)['status'], 'supported')
        self.assertNotIn('DISPROVED', fld.dumps(fld.adapt(row)['problem']))
    def test_empty_and_placeholder(self):
        self.assertEqual(fld.facts(''), [])
        self.assertEqual(fld.adapt({'facts_formula':'fact1: fake_formula', 'hypothesis_formula':'{A}'})['status'], 'unsupported')
    def test_data_strings(self):
        x = [fld.S('record'), 'a (b) "c" \\ d\n¬', 12, []]
        self.assertEqual(fld.loads_many(fld.dumps(x)), [x])

if __name__ == '__main__': unittest.main()
