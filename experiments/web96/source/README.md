# Pinned source provenance and reuse notices

## Actual acquisition

- Source: datasets/country-codes, `data/country-codes.csv`.
- Commit: `2d84034a0cae19ea5444b78c2131304a5c7f4bb9`.
- URL: https://raw.githubusercontent.com/datasets/country-codes/2d84034a0cae19ea5444b78c2131304a5c7f4bb9/data/country-codes.csv
- Original bytes: 133,991; CSV records excluding header: 249.
- SHA-256: `bb199ebc9636b9872705e8216f1f849359f136a7668ebfa23a3c58048462ab92`.
- Git blob SHA-1: `2756ebd48579e93f05155a134eeae88aa4a8f125`, compared with
  the pinned GitHub Contents API response. See [git-blob.json](git-blob.json).
- Local acquisition metadata: [origin.json](origin.json). Its timestamp/cache path
  records this research environment, not an external truth guarantee.

This is a third-party compilation of M49 and other sources, **not a direct
reproduction of the UN's current publication**. The upstream README says that the
M49 source files are committed upstream and are not automatically refreshed by
its normal monthly rebuild. Do not infer a current-world date from our fetch date.

## Licensing and retention boundary

The full original CSV is intentionally **not bundled** here. It remains in the
private local acquisition cache (default `~/.cache/dlm-web96`), and generated
full input packets should stay in private temporary files. The product contains
pinned provenance, upstream notices, aggregate check results and limited examples,
not a redistributed full table or all derived geographic bindings.

Read the pinned upstream notices before reusing data:

- [Upstream README](upstream-README.md), especially Data sources and License.
- [Upstream attribution](upstream-ATTRIBUTION.txt).
- [Upstream column/schema metadata](upstream-datapackage.yml).

The maintainers dedicate only their own scripts/selection/arrangement under PDDL;
that does not override the external sources' terms. The README marks UNTERM
material restricted, M49/ISO and several other components unclear, and identifies
other components under CC BY 4.0, Unicode terms, CC0 or citation requests. Our
project's software license is **not** a license for this mixed-source table.
No conclusion about commercial/public redistribution permission is asserted.

Initial inspection also requested `LICENSE` and `datapackage.json` at the pinned
commit; both returned HTTP 404. The actual metadata file is `datapackage.yml`.
Those 404s are not missing training results or silent substitutions.

## Reproduction

From the version root:

```sh
python3 -B adapters/web96.py --online --output /tmp/web96.sexp
```

Subsequent use is offline/cache-only unless `--online` is supplied explicitly.
Retain the cache privately for reproducibility. A cache miss must not be replaced
with a fabricated dataset. Unit tests separately generate small synthetic CSV
protocol fixtures; those are not reported as real downloaded observations.
