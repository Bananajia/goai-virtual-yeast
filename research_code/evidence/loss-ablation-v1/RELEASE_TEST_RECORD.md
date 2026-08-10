# Loss-ablation clean Adapter — test record

Date: 2026-08-10

The release-safe integration was checked without loading competition matrices:

```text
uv run --locked python -m unittest discover -s tests -v
Ran 77 tests ... OK

research_cli.py run loss_ablation_evidence --scope aggregate-only --data-root ..
records requested/passed/failed/blocked = 1/1/0/0
frozen scalar metrics verified = 8
result status = GOVERNANCE

node --check html/mobile-digest/build_mobile_digest.mjs
PASS
```

Additional checks passed for JSON parsing of `evidence/registry.json`, Python
bytecode compilation of the Adapter and experiment registry, source SHA-256,
relative evidence paths, and absence of local/private filesystem paths. The
evidence file SHA-256 is
`47715a866cc5bc1053f3d3c0cc33f1eba28adecc2109df915c3e4c39db45f938`.

This record tests the clean aggregate Adapter. It is separate from the historical
private numeric run's 19/19 synthetic/contract tests and independent aggregate
replay, which remain documented in the optional persistent experiment tree.
