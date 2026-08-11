# Public L1000FWD six-signature causal-axis smoke

This is an offline, public-only Interface test. It does not read the competition data, call an external provider, or predict a protein vector.

## Frozen cohort

- Signatures: 6 (HA1E; six distinct perturbagens)
- Frozen mechanism axes: 23
- Structured causal edges: 18
- RNA marker hits used only by the evaluator: 94

## Aggregate metrics

| Metric | Value |
|---|---:|
| `macro_axis_cosine` | 0.122479 |
| `pooled_axis_pearson` | 0.120599 |
| `predicted_axis_precision` | 0.611111 |
| `signed_axis_accuracy` | 0.150943 |
| `top_axis_hit_rate` | 0.666667 |
| `truth_axis_recall` | 0.207547 |

## Interpretation boundary

Interface smoke only: six human HA1E RNA signatures are too small to establish transfer to yeast proteomics. A real local/authorized model must beat this frozen fixture under a preregistered public holdout before promotion.

The fixture manifest records source URLs, retrieval date, byte count and SHA-256. Query metadata and withheld RNA truth are represented by different types, so the provider never receives the evaluator's ranked gene lists.
