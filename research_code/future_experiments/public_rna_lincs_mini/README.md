# Public RNA / L1000FWD mini-pilot

This is the smallest reproducible test of the proposed route:

`public drug facts -> structured causal chain -> 23 mechanism axes -> public RNA-axis evaluator`

The fixture freezes six L1000FWD HA1E signatures (rapamycin, MG-132,
thapsigargin, oligomycin C, etoposide and nocodazole). It is under 5 KB and its
manifest contains source URLs, retrieval date, byte count and SHA-256.

The loader returns query metadata and withheld ranked RNA genes through
different types. Providers receive only strict public mechanism packets. The
offline smoke uses a deterministic fixture provider, makes no network request,
and writes only aggregate metrics.

Run from `research_code/`:

```bash
PYTHONPATH=. python3 -m future_experiments.public_rna_lincs_mini \
  --output reports/public-rna-lincs-mini
```

This six-signature human RNA experiment cannot establish transfer to yeast
proteomics. It validates the data contract and evaluator before spending local
LLM or authorized public-API budget.

## Local open-weight pilot

The local mode probes exactly one installed Ollama tag, records its digest and
server version, and sends only the frozen public mechanism packet to the
loopback provider. Start with one anonymous case:

```bash
PYTHONPATH=. python3 -m future_experiments.public_rna_lincs_mini \
  --mode local-ollama --model qwen3:8b --case-limit 1 \
  --output reports/public-rna-local-ollama-qwen3-smoke
```

Only after that succeeds, request all six:

```bash
PYTHONPATH=. python3 -m future_experiments.public_rna_lincs_mini \
  --mode local-ollama --model qwen3:8b --case-limit 6 \
  --output reports/public-rna-local-ollama-qwen3-six
```

The runner persists aggregate metrics, anonymous counts and provider/model
provenance only. It never persists entity names, prompts, responses, causal
chains or per-case vectors. Any invalid structured output blocks the full run;
partial metrics are discarded rather than cherry-picked.
