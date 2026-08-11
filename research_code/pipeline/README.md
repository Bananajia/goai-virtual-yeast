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
   The LIVE competition CLI adds a stricter preflight: any finite value `<=0`
   aborts training with a count, so only original `NA` can remain missing.
5. `MetadataEncoder` fits categorical vocabularies and numeric statistics on
   fit rows. Time uses `log1p`; temperature may use a fit-only z-score; unseen
   categories receive an explicit unknown token.
6. `GroupedOODSplitter` holds out whole identities or whole combinations and
   asserts zero identity overlap.
7. `match_official_controls()` resolves every treated chemical through an
   explicit `OfficialVehicleMap` and matches DMSO/Water using all seven sealed
   semantic roles: source/strain/medium/temperature/time/instrument/plate.
   `OfficialControlMatchColumns` binds those roles to the physical organizer
   column names and may add stricter keys, but cannot omit a role. The legacy
   subset matcher is retained only as the explicitly named
   `match_exploratory_controls()` API. Official pairing fails if a chemical
   vehicle mapping or exact control is absent.
8. `MeasuredControlPairer` constructs Raw-FC from endpoint and a directly
   measured control on the same replicate-by-protein cells. Independent
   all-control means are marked sensitivity analyses and cannot be mixed with
   the primary paired estimand. It returns immutable endpoint/control/response
   snapshots with an internal verification seal required by the evaluator.
9. A model fits only the modeled protein coordinates.
10. `ProteinOutputContract.restore()` can restore an internal full-width matrix.
   A protein with no finite fit observation requires an explicit fit-only
   fallback value; it is never filled silently. The published metadata Ridge
   config freezes this as the median of all finite train-only log2 cells.
11. The central `evaluation` Module scores the prediction;
    `OfficialScorecard` routes the required families by declared split without
    inventing an unpublished aggregate total.
12. `SubmissionContract` validates exact sample IDs, official feature names and
    order, finite values, and `log2` scale before writing `prediction.csv`.
    The latest official template may be a unique ordered subset of the artifact
    protein panel and remains authoritative.

The source matrix contains 5,243 protein coordinates. Applying the stated
train-only strict rule to the current release gives 4,422 modeled coordinates
and zero proteins exactly at 80% missingness, so `<0.80` and `<=0.80` select the
same panel. The interpretation PDF's reported 4,232 cannot be reproduced by its
shown formula on this release and is not a machine constant. Final submission
columns and order always come from the latest official feature contract.
