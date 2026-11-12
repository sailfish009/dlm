# dt_array_backend_probe (v0.0217 feasibility)

See `REPORT.md`.

```bash
./run_probe.sh
```

Artifacts:

- `fixture.py` / `fixture.h` — DT-1 fold-0 Q16 fixture from v0.0204.
- `dt_selector_c.c` — full Q16 selector (no proof, no training).
- `maru_case0.out` — Maru v0.0204 reference line.
- `verify_probe.py` — parity gate.
