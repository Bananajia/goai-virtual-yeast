# Legacy aggregate evidence replay

Date: 2026-08-10

## Outcome

The registry contains 25 records: 22 golden aggregate sources, one invalidated
source and two explicitly source-missing router lineages.

| Replay set | Records | Frozen metrics | Result |
|---|---:|---:|---|
| Golden aggregate evidence | 22 records | 75 | PASS |
| Invalidated evidence used as golden | 0 | 0 | PASS |

The invalidated `control-affine-fullpanel-v1` source is retained
as an audit record but is `INVALIDATED` and therefore excluded from golden
replay.  The response-based parts of `threshold-control-calibration-v1` are also
invalidated; its replay is deliberately limited to the frozen historical
4,422-coordinate structural count. On the current release, the train-only
`<80%` panel contains 4,422 proteins and
has zero exact-boundary ties. The interpretation PDF's 4,232 count is not
reproduced by its shown formula and is not inferred from this record.

The formal train-mean and Metadata Ridge baseline suite is replayed from the
frozen V9 portable report artifact. This adds eight checks for the average-value
trap, the historical 4,422 + 821 restoration contract, Endpoint PCC and the
explicitly exploratory pooled-control Raw-FC result. The old restoration width
is not a submission feature-contract claim.

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
