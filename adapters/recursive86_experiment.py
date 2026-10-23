"""Compare direct sequential checking with genuine generated branch execution.
Reuses the native-driver timing/held-out checker from Search85; no Python policy.
"""
import json
from pathlib import Path
import random
import statistics
from search85_experiment import run

ROOT = Path(__file__).resolve().parents[1]
MODES = ('ucb', 'nd-cache', 'nd-ucb')


def main():
    schedule = []
    for seed in (0, 1, 2):
        for mode in MODES:
            for repeat in (0, 1):
                schedule.append((seed, 'mixed', mode, False, 'fixed-six', repeat))
                schedule.append((seed, 'distractors', mode, True, 'target-two', repeat))
    random.Random(86).shuffle(schedule)
    rows = [run(*spec) for spec in schedule]
    for workload in ('mixed', 'distractors'):
        for mode in MODES:
            group = [row for row in rows if row['workload'] == workload and row['mode'] == mode]
            print(workload, mode, 'defs', [len(next(r for r in group if r['seed'] == seed)['paths']) for seed in (0, 1, 2)],
                  'calls', statistics.median(r['actual_search_certify_calls'] for r in group),
                  'search', round(statistics.median(r['search_seconds'] for r in group), 4),
                  'workflow', round(statistics.median(r['workflow_seconds'] for r in group), 4))
    report = dict(protocol='36 fresh native processes; three varied seeds x three modes x two repeats x two protocols; randomized arm order',
                  notes=['ucb performs direct sequential native checks; nd modes execute generated choose programs',
                         'batch proposals <=min(budget,16); batch order frozen until checked branch labels return',
                         'nd modes recheck chosen definitions at admission; extra certification is intentional',
                         'all modes use the same native admission criteria and held-out primitive-path proof oracle',
                         'mixed is fixed-six in memory; distractors target-two with attached store and durable close',
                         'timings are parent-observed markers, not broad statistical speed evidence'], results=rows)
    (ROOT / 'docs/recursive86-experiment.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
