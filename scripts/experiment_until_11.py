#!/usr/bin/env python3
"""Deadline-driven DT-1 discovery supervisor.

The supervisor, not the assistant turn, owns the stop condition: it keeps
running the architecture probes with fresh seeds until 11:00 and writes a
summary.  Individual probes are bounded so one bad run cannot hang the loop.
"""
import json
import os
import re
import signal
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments_until_11"
OUT.mkdir(parents=True, exist_ok=True)
DEADLINE = datetime(2026, 11, 11, 11, 0, 0)
# Fast probes only. Depth probes are run with a separate hard timeout.
PROBES = [
    "dt1_axiom_select",
    "dt1_binding",
    "dt1_verifier",
    "dt1_pool",
    "dt1_combined",
    "dt1_depneg",
]


def run_probe(name, seed):
    src = ROOT / "experiments" / name / "run.py"
    text = src.read_text()
    text = re.sub(r"seed\(\d+\)", f"seed({seed})", text)
    tmp = OUT / f"{name}_{seed}.py"
    tmp.write_text(text)
    start = time.time()
    try:
        p = subprocess.run(
            ["python3", str(tmp)],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
            start_new_session=True,
        )
        lines = [x for x in p.stdout.strip().splitlines() if x.strip()]
        tail = lines[-2:] if lines else []
        return {
            "probe": name,
            "seed": seed,
            "rc": p.returncode,
            "seconds": round(time.time() - start, 2),
            "tail": tail,
            "stderr": p.stderr.strip()[-500:],
        }
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(os.getpgid(exc.pid), signal.SIGKILL)
        except Exception:
            pass
        return {
            "probe": name,
            "seed": seed,
            "rc": "timeout",
            "seconds": round(time.time() - start, 2),
            "tail": [],
            "stderr": "timeout",
        }


def heartbeat():
    while True:
        print(f"heartbeat {datetime.now()} alive", flush=True)
        time.sleep(5)


def main():
    print(f"start {datetime.now()} deadline {DEADLINE}", flush=True)
    threading.Thread(target=heartbeat, daemon=True).start()
    seed = 100
    n = 0
    while datetime.now() < DEADLINE:
        for name in PROBES:
            if datetime.now() >= DEADLINE:
                break
            print(f"probe {name} seed={seed} at {datetime.now()}", flush=True)
            row = run_probe(name, seed)
            with (OUT / "results.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(json.dumps(row, ensure_ascii=False), flush=True)
            seed += 1
            n += 1
    lines = (OUT / "results.jsonl").read_text().splitlines() if (OUT / "results.jsonl").exists() else []
    (OUT / "summary.md").write_text(
        "# DT-1 discovery until 11:00\n\n"
        f"- runs: {n}\n"
        f"- records: {len(lines)}\n"
        f"- stopped: {datetime.now()}\n",
        encoding="utf-8",
    )
    print(f"done {datetime.now()} runs={n}", flush=True)


if __name__ == "__main__":
    main()