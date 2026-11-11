#!/usr/bin/env python3
"""Parse Maru p-prove candidate evaluations into a reward table."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = subprocess.run([str(ROOT / "scripts/dt1_bridge.sh")], cwd=ROOT, text=True, capture_output=True, timeout=180)
rows = []
for line in p.stdout.splitlines():
    m = re.match(r"CAND (\w+) ids=\(([^)]*)\) rules=(\d+) proof=(\w+)", line)
    if m:
        ids = m.group(2).split() if m.group(2) else []
        rows.append({"name": m.group(1), "ids": ids, "rules": int(m.group(3)), "proof": m.group(4)})
print(json.dumps({"rc": p.returncode, "rows": rows}, indent=2))
