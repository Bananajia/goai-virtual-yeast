# ADR 0001: Add a non-destructive unified research layer

Status: accepted
Date: 2026-08-10

## Context

The historical project contains hundreds of Python files created under frozen experimental protocols. Those directories are audit evidence, but they duplicate loaders, Pearson implementations, masks, runners, and report writers. Several early control and residual scorers were later invalidated. Moving or rewriting historical files would destroy Locality between a result and its original evidence.

## Decision

Create `research_code/` as a new Module hierarchy and leave every historical directory unchanged.

The public Interfaces are:

1. `pipeline`: load, validate, transform, pair measured controls, and construct OOD splits.
2. `models`: a fit/predict Interface for statistical and learned Implementations.
3. `evaluation`: the only implementation of endpoint, Raw-FC, residual, individuality, variance-ratio, and DEP metrics.
4. `experiments`: one experiment per file, discovered through a registry and executed through a common runner.
5. `future_experiments`: public-only RNA, causal-chain, RAG, and active-calibration research.
6. `reporting`: aggregate-only JSON, Markdown, and later HTML Adapters.
7. `evidence`: immutable references to historical results, validity state, source hash, and replacement lineage.

Historical code is reached through an Adapter only after a golden aggregate parity check. Invalidated experiments remain in the evidence registry but cannot be promoted or used as golden results.

## Safety Seam

Private data loading and public model providers are deliberately separate Seams. A provider accepts only a validated `PublicEvidencePacket`; it cannot accept a dataframe, path, free-form prompt, competition identity, protein vector, or prediction matrix. Network providers are disabled by default.

## Consequences

- Metric fixes have high Leverage because every experiment calls one deep evaluation Module.
- Each experiment file retains Locality: it declares only the question, model Adapter, split, and gate.
- The legacy tree stays reproducible and auditable.
- Some current results cannot be source-level reproduced because the original chemical router source is missing; those entries are marked blocked or reconstructed, never silently treated as original.
