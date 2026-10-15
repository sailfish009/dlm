# DLM v0.0038 web experiment

Fetch random Wikipedia/Wikidata class hierarchies (no human labels), learn a
general law on `Ground` + `Experience`, and score it against the kernel.

> v0.0054: the web **access and providers are the model's** now (`dlm.web`,
> `dlm.search`).  `web.py`/`acquire.py` here keep only experiment glue — the
> GIVEN property map and seed list, slug/sentence reduction, and the shaping of
> wiki responses into `Fact`/`Doc` records; all transport and caching are
> delegated to `dlm.web.Web`.

## Run

```bash
./experiments/web/web_learn.sh                 # online, seeds 1 2 3, 60 articles
DOCS=40 SEEDS="1" ./experiments/web/web_learn.sh

# reproduce offline from a cache (byte-identical):
OFFLINE=1 CACHE=/research/dlm_v0.0033/experiments/webloop/cache \
  DOCS=60 SEEDS="1" ./experiments/web/web_learn.sh
```

Everything is cached under `experiments/web/cache`; reports land in
`experiments/web/reports/result_seed*.json`. A second run is offline.

## What it measures

* `identity`  -- raw `subclass_of` facts only (no rule).
* `learned`   -- `Ground` + induced `Experience`.
* `scrambled` -- constants permuted before induction (control).

`held_recovery` = fraction of held-out true pairs derived; `false` = pairs
derived but not in the kernel's true closure. Verdict requires the learned law
to beat identity, derive no false pair, and the scramble not to beat it.

## Files

* `web.py`, `acquire.py` -- copied network extraction (cache-backed, no labels).
* `run.py` -- v0.0038 Ground/Experience pipeline + evaluation.
* `web_learn.sh` -- one-shot runner (fetch -> learn -> evaluate -> determinism).