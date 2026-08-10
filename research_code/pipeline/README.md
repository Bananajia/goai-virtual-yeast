# Data pipeline

The pipeline runs in this order:

1. `DatasetAdapter.load()` returns a validated condition-by-protein bundle with
   explicit `synthetic`, `public`, or `private_local` scope.
2. `Log2ProteomeTransformer` converts positive raw intensities to `log2`; zero,
   negative, and original missing values become `NaN`.
3. `MissingnessFilter.fit()` is called on outer-fit rows only. At the current
   80% engineering reference, missingness `<= 0.80` is retained and `> 0.80` is
   removed.
4. `MetadataEncoder` fits categorical vocabularies and numeric statistics on
   fit rows. Time uses `log1p`; temperature may use a fit-only z-score; unseen
   categories receive an explicit unknown token.
5. `GroupedOODSplitter` holds out whole identities or whole combinations and
   asserts zero identity overlap.
6. `MeasuredControlPairer` constructs Raw-FC from endpoint and a directly
   measured control on the same replicate-by-protein cells. Independent
   all-control means are marked sensitivity analyses and cannot be mixed with
   the primary paired estimand. It returns immutable endpoint/control/response
   snapshots with an internal verification seal required by the evaluator.
7. A model fits only the modeled protein coordinates.
8. `ProteinOutputContract.restore()` returns the immutable full width with
   fit-only fallback means for non-modeled coordinates.
9. The central `evaluation` Module scores the prediction.

The current competition contract is 5,243 proteins. The historical 80% fit on
the full training set yielded 4,422 modeled coordinates and 821 fallback
coordinates; this numeric fact is stored in evidence, not hard-coded into the
general pipeline.
