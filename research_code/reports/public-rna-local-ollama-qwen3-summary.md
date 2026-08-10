# Local open-weight LLM pilot: audited outcome

## Scope

This pilot used only the hash-frozen six-case public L1000FWD fixture and its
public mechanism facts. The causal-chain provider was local Ollama over the
loopback interface. Competition data, external networks and closed model APIs
were not used.

Provider provenance:

- Provider: `ollama-loopback`
- Model: `qwen3:8b`
- Model digest: `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`
- Ollama version: `0.32.5`
- Public fixture SHA-256: `3fc762d05132ac92b42e94f3e43f11cd0379738de685e2629b892258bfdbbed6`

## Result

The one-case smoke completed and was byte-identical on an immediate repeat.
Its aggregate metrics were:

| Metric | Value |
|---|---:|
| Macro axis cosine | 0.094916 |
| Pooled axis Pearson | 0.088561 |
| Predicted-axis precision | 0.333333 |
| Signed-axis accuracy | 0.200000 |
| Top-axis hit rate | 0.000000 |
| Truth-axis recall | 0.200000 |

The preregistered six-case run stopped at anonymous case 2 because the local
model output did not satisfy the closed causal-chain schema. Its status is
therefore `BLOCKED`, not a low six-case score. Partial metrics were discarded,
so there is no defensible full-cohort result yet.

## Interpretation and next gate

This demonstrates that the public-only execution and evaluation Interfaces
work, but not that an LLM mechanism feature improves RNA prediction or transfers
to yeast proteomics. The current gap is structured-output stability under the
strict 23-axis contract. A next attempt must pre-register any change (for
example, a richer cited public fact bundle or a stronger local open-weight
model), apply it uniformly to all six anonymous cases and still forbid access
to RNA truth during inference.

Artifacts:

- One-case aggregate: `public-rna-local-ollama-qwen3-smoke/`
- Six-case fail-closed aggregate: `public-rna-local-ollama-qwen3-six/`

Both artifact directories passed a leakage scan for entity names, prompt and
response fields, RNA truth keys and signature identifiers.
