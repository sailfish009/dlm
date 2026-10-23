"""Review regression fixes, explicit old/new codecs, and indexed-only ablation."""
import json
from pathlib import Path
import tempfile
import unittest
from test_sequent import maru
from test_repl import Live
from test_search84 import RARE
from sexp import loads_many


class Search85Tests(unittest.TestCase):
    def test_definition_capacity_restores_with_nonempty_pool(self):
        facts = ' '.join(f'(atom {p} ({a} {b}))' for p in ('r', 's')
                         for a in ('a', 'b', 'c') for b in ('a', 'b', 'c'))
        with tempfile.TemporaryDirectory() as directory:
            q = json.dumps(str(Path(directory) / 'capacity.sexp'))
            first = maru(f'''(dlm 'observe 'dense '({facts}))
(dlm 'search 'cache)
(times-do 13 (dlm 'step))
(assert (= *s85-stop* 'capacity) "resource reason retained")
(assert (dlm-nth *s84-control* 3) "capacity with pending candidates")
(d77-write {q} (d77-pack *dlm-model* *dlm-round* *dlm-events*))
(dump (dlm 'step))''')
            second = maru(f'''(dlm 'open {q})
(assert (= *s85-stop* 'capacity) "same terminal reason on reopen")
(assert *dlm-saturated* "wait without new search event")
(dump (dlm 'step))''')
            self.assertEqual(loads_many(first), loads_many(second))
            self.assertEqual(loads_many(second)[0][2][0], 'waiting')

    def test_event_limit_pauses_real_idle_without_search_work(self):
        repl = Live()
        try:
            repl.exchange('(begin (times-do 256 (dlm \'search \'cache)) (print "FILLED85\\n"))', rb'FILLED85')
            repl.exchange("(dlm 'start 20)", rb'dlm77 running')
            repl.wait(rb'resource-limit event-limit', seconds=8)
            repl.exchange('(assert (not *dlm-running*) "paused")', rb'true')
            repl.exchange('(assert (= *dlm-round* 0) "no attempted search round")', rb'true')
            repl.exchange('(assert (= (dlm-nth *s84-control* 7) 0) "no certification")', rb'true')
            repl.exchange("(dlm 'reset)", rb'committed')
            repl.exchange('(assert (not *dlm-events*) "explicit reset recovers")', rb'true')
        finally:
            repl.close()

    def test_cumulative_request_limit_preflight_with_valid_history(self):
        out = maru('''(set *dlm-pair-budget* 1000)
(times-do 100 (dlm 'search 'ucb) (dlm 'step))
(dlm 'search 'ucb)
(dlm 'start 20)
(define result (dlm 'step))
(assert (equal (dlm-nth result 2) '(paused resource-limit request-limit)) "request cap")
(assert (not *dlm-running*) "no repeated idle refusal")
(assert (= *dlm-round* 100) "preflight before computation")
(assert (= (dlm-nth *s84-control* 7) 0) "no work")
(print "passed")''')
        self.assertEqual(out, 'passed')

    def test_indexed_only_isolates_negative_cache(self):
        rows = []
        for mode in ('indexed', 'cache'):
            output = maru(RARE + f'''(dlm 'search '{mode})
(set *dlm-pair-budget* 1)
(times-do 4 (dlm 'step))
(dump (list (dlm-length (a77-defs *dlm-model*))
 (dlm-nth *s84-control* 7) (dlm-nth *s84-control* 8)))''')
            rows.append(loads_many(output)[0])
        indexed, cached = rows
        self.assertEqual(indexed[0], cached[0])
        self.assertEqual(indexed[2], 0)
        self.assertGreater(indexed[1], cached[1])
        self.assertGreater(cached[2], 0)

    def test_old84_is_accepted_new_modes_require85_tag(self):
        out = maru('''(dlm 'demo)
(define events (dlm-append *dlm-events* '((search84 ucb) (search84-run 1))))
(define replay (a84-replay events))
(define old (list 'dlm-session84 1 (dlm-nth replay 1) 1 events))
(assert (d77-snapshot? old) "old84 snapshot supported")
(define new-events (dlm-append *dlm-events* '((search85 indexed))))
(define current (d77-pack *dlm-model* 0 new-events))
(assert (= (car current) 'dlm-session85) "new explicit format")
(assert (d77-snapshot? current) "new accepted")
(assert (not (d77-snapshot? (s79-field current 0 'dlm-session84))) "new event cannot hide in old format")
(print "passed")''')
        self.assertEqual(out, 'passed')


if __name__ == '__main__':
    unittest.main()
