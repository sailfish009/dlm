"""Native search ablation with randomized arm order and attached-store timing.
Python supplies fixtures/measurement only, never selects native candidates.
"""
import json
import os
from pathlib import Path
import random
import select
import statistics
import subprocess
import tempfile
import time
from sexp import Symbol as S, dumps, loads_many

ROOT = Path(__file__).resolve().parents[1]
MODES = ('legacy', 'indexed', 'cache', 'rank', 'ucb')


def edges(prefix, word):
    return [[S('atom'), S(p), [f'{prefix}{i}', f'{prefix}{i+1}']] for i, p in enumerate(word)]


def fixture(seed, workload):
    rng = random.Random(8500 + seed)
    if workload == 'distractors':
        a = edges('a', ['edge'] * (3 + seed))
        b = edges('b', ['edge'] * (3 + seed))
        for name, facts in (('a', a), ('b', b)):
            facts += [[S('atom'), S('noise'), [f'{name}x{i}', f'{name}y{i}']]
                      for i in range(8 + 2 * seed)]
            rng.shuffle(facts)  # Shuffle useful facts too, not only disconnected noise.
    else:
        patterns = [('rsrs', 'rsr'), ('rrssr', 'rrs'), ('srrsrs', 'srrs')]
        wa, wb = patterns[seed]
        a = edges('a', wa) + edges('ax', wa[:2])
        b = edges('b', wb) + edges('bx', wa[:2])
        rng.shuffle(a)
        rng.shuffle(b)
    return a, b


def execute(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.l') as driver:
        driver.write(code)
        driver.flush()
        started = time.perf_counter()
        proc = subprocess.Popen([str(ROOT / 'scripts/run.sh'), 'proof', driver.name],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        streams = {proc.stdout.fileno(): bytearray(), proc.stderr.fileno(): bytearray()}
        stdout = streams[proc.stdout.fileno()]
        stderr = streams[proc.stderr.fileno()]
        marks = {}
        sampled_hwm_kib = 0
        try:
            while streams:
                if time.perf_counter() - started > 180:
                    raise TimeoutError('native experiment exceeded 180s')
                try:
                    for line in Path(f'/proc/{proc.pid}/status').read_text().splitlines():
                        if line.startswith('VmHWM:'):
                            sampled_hwm_kib = max(sampled_hwm_kib, int(line.split()[1]))
                except (FileNotFoundError, ProcessLookupError):
                    pass
                ready, _, _ = select.select(list(streams), [], [], .02)
                for fd in ready:
                    data = os.read(fd, 65536)
                    if not data:
                        del streams[fd]
                    else:
                        streams[fd].extend(data)
                now = time.perf_counter()
                for marker in ('BEGIN85', 'END85', 'CLOSED85'):
                    if marker not in marks and (marker + '\n').encode() in stdout:
                        marks[marker] = now
            proc.wait(timeout=5)
        except BaseException:
            proc.kill()
            proc.wait()
            raise
        finally:
            proc.stdout.close()
            proc.stderr.close()
        if proc.returncode:
            raise RuntimeError(bytes(stderr).decode() + bytes(stdout).decode())
        text = bytes(stdout).decode()
        if len(marks) != 3:
            raise AssertionError(text)
        for marker in marks:
            text = text.replace(marker + '\n', '')
        return loads_many(text), dict(
            search_seconds=marks['END85'] - marks['BEGIN85'],
            workflow_seconds=marks['CLOSED85'] - started,
            sampled_process_hwm_kib=sampled_hwm_kib)


def run(seed, workload, mode, attached, protocol, repeat):
    a, b = fixture(seed, workload)
    probe = edges('heldout', 'rssrsr') if workload == 'mixed' else edges('heldout', ['edge'] * 5)
    with tempfile.TemporaryDirectory() as directory:
        code = f"(dlm 'open {json.dumps(str(Path(directory) / 'native.sexp'))})\n" if attached else ''
        code += f"(dlm 'observe 'a '{dumps(a)})\n(dlm 'observe 'b '{dumps(b)})\n"
        if mode != 'legacy':
            code += f"(dlm 'search '{mode})\n"
        code += '''(set *dlm-pair-budget* 8)
(define bench-calls85 0)
(define bench-original85 a77-certify)
(define-function bench-certify85 (model candidate)
  (set bench-calls85 (+ bench-calls85 1)) (bench-original85 model candidate))
(set a77-certify bench-certify85)
(define iterations85 0)
(print "BEGIN85\\n")
'''
        if protocol == 'fixed-six':
            code += '(times-do 6 (dlm \'step) (set iterations85 (+ iterations85 1)))\n'
        else:
            code += '''(while (and (< iterations85 128) (< (dlm-length (a77-defs *dlm-model*)) 2))
 (dlm 'step) (set iterations85 (+ iterations85 1)))
'''
        code += '(print "END85\\n")\n'
        if attached:
            code += "(define closed85 (dlm 'close))\n(assert (= (car closed85) 'closed) \"durable close\")\n"
        code += '(print "CLOSED85\\n")\n'
        code += f'''(define evaluation85 (a77-close *dlm-model* '{dumps(probe)}))
(assert (= (dlm-nth evaluation85 1) 'complete) "heldout closure complete")
(define hits85 0)
(list-do proof (dlm-nth evaluation85 2)
  (assert (dlm-verify-proof proof '{dumps(probe)} (a77-rules *dlm-model*)) "independent native proof check")
  (if (= (dlm-nth proof 2) 'rule) (set hits85 (+ hits85 1))))
(define expected85 0)
(list-do definition (a77-defs *dlm-model*)
 (set expected85 (+ expected85 (dlm-length (a77-path (dlm-nth definition 2) '{dumps(probe)})))))
(assert (= hits85 expected85) "primitive-path reference agrees with learned closure")
(dump (list iterations85 (a77-words (a77-defs *dlm-model*)) bench-calls85 hits85
 *s84-control* *s85-stop*)) (print "\\n")
'''
        rows, measured = execute(code)
    steps, paths, calls, hits, controller, stop = rows[0]
    return dict(seed=seed, workload=workload, mode=mode, attached=attached,
                protocol=protocol, repeat=repeat, steps=steps, paths=paths,
                certify_calls_including_replay=calls, heldout_proved_instances=hits,
                controller_serialized_bytes=len(dumps(controller).encode()),
                actual_search_certify_calls=controller[7] if mode != 'legacy' else None,
                negative_cache_hits=controller[8], stop=stop, **measured)


def main():
    schedule = []
    for seed in (0, 1, 2):
        for mode in MODES:
            for repeat in (0, 1):
                schedule.append((seed, 'mixed', mode, False, 'fixed-six', repeat))
                for attached in (False, True):
                    schedule.append((seed, 'distractors', mode, attached, 'target-two', repeat))
    random.Random(85).shuffle(schedule)
    results = [run(*spec) for spec in schedule]
    report = dict(protocol='randomized arm order; structurally varied three seeds; five modes; two repeats',
                  caveats=['fixed-six budget8 counts different work units for legacy and indexed modes',
                           'search time is measured between parent-observed stdout markers; no hard time guarantee',
                           'workflow time includes startup, open/observe/configure, search and durable close; excludes heldout evaluation',
                           'attached search includes full checkpoint replay; certification counter includes replay',
                           'sampled VmHWM is a whole-process peak-memory proxy, not equal-memory control',
                           'heldout graph is a small formal transfer probe; no broad generalization claim'], results=results)
    target = ROOT / 'docs/search85-experiment.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    for workload, protocol in (('mixed', 'fixed-six'), ('distractors', 'target-two')):
        for attached in ((False,) if protocol == 'fixed-six' else (False, True)):
            for mode in MODES:
                rows = [r for r in results if (r['workload'], r['attached'], r['mode']) == (workload, attached, mode)]
                print(workload, 'store' if attached else 'memory', mode,
                      'defs', [len(next(r for r in rows if r['seed'] == seed and r['repeat'] == 0)['paths']) for seed in (0, 1, 2)],
                      'search', round(statistics.median(r['search_seconds'] for r in rows), 4),
                      'workflow', round(statistics.median(r['workflow_seconds'] for r in rows), 4),
                      'calls', statistics.median(r['certify_calls_including_replay'] for r in rows))


if __name__ == '__main__':
    main()
