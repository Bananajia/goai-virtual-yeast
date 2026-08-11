# Future experiments

This folder is physically separated from the competition-data pipeline.

## Executable now

### `public_causal_chain/`

One provider Interface with three Adapters:

- deterministic offline fixture;
- loopback-only Ollama;
- optional OpenAI-compatible public-only Adapter, disabled by default.

Inputs are closed-schema public facts with allowlisted citations. Outputs are
3–8 evidence-linked edges ending on one of 23 mechanism axes. No Adapter accepts
a dataframe, local path, private identity, arbitrary prompt, response matrix,
embedding, or protein vector.

### `public_rna_lincs_mini/`

Six frozen public L1000FWD signatures test whether a structured mechanism chain
aligns with public human RNA response at the mechanism-axis level. The default
run is deterministic and offline:

```bash
PYTHONPATH=. python3 -m future_experiments.public_rna_lincs_mini \
  --output reports/public-rna-lincs-mini
```

It is a smoke test, not evidence that human RNA transfers to yeast proteomics.

A loopback-only `qwen3:8b` check has also been run. One anonymous case completed
deterministically; the six-case cohort stopped fail-closed on invalid structured
output at case 2, so no full-cohort metric is claimed. See
`../reports/public-rna-local-ollama-qwen3-summary.md`.

The same module now has a loopback-only local open-weight mode. It resolves the
exact Ollama model digest, runs one anonymous smoke case first, and may then run
all six. Invalid model JSON/schema fails closed and partial scores are not kept.
No competition file is opened by this path.

## Next protocol before any external model call

1. Freeze a public compound holdout and public source hashes.
2. Compare fixture, local Qwen, local Gemma, identity permutation, axis
   permutation, zero, and leave-one-compound mean.
3. Calibrate LLM directions against public RNA only; never expose RNA truth to
   the provider process.
4. Require both models to improve axis PCC/cosine and signed top-k metrics.
5. Only then evaluate a public-to-yeast bridge. Competition matrices remain
   outside this folder and outside every provider payload.

LoRA remains optional. With six public cases there is not enough supervision to
justify post-training; it should begin only after a larger licensed public
mechanism corpus and a held-out evaluation set exist.
