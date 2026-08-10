# Data pipeline

The pipeline runs in this order:

1. `align_dataset_frames()` joins metadata and proteome rows by unique
   `sample_ID` and returns a validated condition-by-protein bundle with explicit
   `synthetic`, `public`, or `private_local` scope. Current CSV order is ignored.
2. `require_training_bundle()` rejects any labeled fit bundle that contains a
   role other than `split_final=train`.
3. `MissingnessFilter.fit_raw()` is called on outer-fit raw rows only, before
   log2, so the official mask follows the raw table's NA pattern. Its default
   follows the interpretation material: missingness `< 0.80` is retained and
   `>= 0.80` is removed. `include_boundary=True` reproduces the earlier
   inclusive engineering sensitivity and must be labeled as such.
4. `Log2ProteomeTransformer` converts positive raw intensities to `log2`; zero,
   negative, and original missing values become `NaN`.
5. `MetadataEncoder` fits categorical vocabularies and numeric statistics on
   fit rows. Time uses `log1p`; temperature may use a fit-only z-score; unseen
   categories receive an explicit unknown token.
6. `GroupedOODSplitter` holds out whole identities or whole combinations and
   asserts zero identity overlap.
7. `match_official_controls()` resolves every treated chemical through an
   explicit `OfficialVehicleMap` and matches DMSO/Water using the declared
   source/strain/medium/temperature/time/instrument/plate keys. It fails if an
   official mapping or exact control is absent.
8. `MeasuredControlPairer` constructs Raw-FC from endpoint and a directly
   measured control on the same replicate-by-protein cells. Independent
   all-control means are marked sensitivity analyses and cannot be mixed with
   the primary paired estimand. It returns immutable endpoint/control/response
   snapshots with an internal verification seal required by the evaluator.
9. A model fits only the modeled protein coordinates.
10. `ProteinOutputContract.restore()` can restore an internal full-width matrix.
   A protein with no finite fit observation requires an explicit fit-only
   fallback value; it is never filled silently.
11. The central `evaluation` Module scores the prediction.
12. `SubmissionContract` validates exact sample IDs, official feature names and
    order, finite values, and `log2` scale before writing `prediction.csv`.

The source matrix contains 5,243 protein coordinates. The interpretation
material's strict 80% rule reports 4,232 modeled coordinates; the historical
inclusive experiment reported 4,422. The final submission columns and order are
always taken from the latest official feature contract rather than inferred from
either count.
