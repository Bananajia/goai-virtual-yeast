# Legacy aggregate evidence replay

Date: 2026-08-10

## Outcome

The registry contains 22 records: 20 persistent aggregate sources and two
explicitly source-missing router lineages.

| Replay set | Records | Frozen metrics | Result |
|---|---:|---:|---|
| Persistent Documents evidence | 19 golden records | 30 | PASS |
| Invalidated evidence used as golden | 0 | 0 | PASS |

The invalidated `control-affine-fullpanel-v1` source is retained
as an audit record but is `INVALIDATED` and therefore excluded from golden
replay.  The response-based parts of `threshold-control-calibration-v1` are also
invalidated; its replay is deliberately limited to the frozen 4,422-coordinate
structural count.

The formal train-mean and Metadata Ridge baseline suite is replayed from the
frozen V9 portable report artifact. This adds eight checks for the average-value
trap, the 4,422 + 821 output contract, Endpoint PCC and the explicitly
exploratory pooled-control Raw-FC result.

## Lineage safeguards

- `control-affine-fullpanel-v1` points to the pairwise-clean
  `control-affine-fullpanel-v2-pairwise` replacement.
- Dynamic and public-group pilots point to their later confirmatory/knowledge
  experiments without rewriting either result.
- A valid negative experiment remains reproducible evidence, but its candidate
  is not relabelled as deployable.
- `chemical-router-v3` and `unified-router-final-v3-scoped` are explicitly
  `BLOCKED_SOURCE_MISSING`. Existing narrative summaries are insufficient to
  replay their code or frozen aggregate output.

## Persistence update

`named-pathway-tokens-v1`, `drug-target-localnet-v1`,
`strain-genome-cnv-v1`, and `strain-lof-shrinkage-v1` were copied into the
long-term Documents project on 2026-08-10 without changing the workspace
copies. Their aggregate hashes are unchanged and now replay from the persistent
root.

## Privacy and failure behavior

The replay opened aggregate Markdown/JSON only. It did not read a competition
matrix, validation/test values, identities, predictions, model weights or
protein vectors. Source paths in the registry are relative. Hash verification
precedes metric parsing, and a synthetic tamper test confirms that a changed
file fails before any frozen metric is accepted.
