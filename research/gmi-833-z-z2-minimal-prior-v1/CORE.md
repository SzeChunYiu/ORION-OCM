# GMI #833 Section Z / Z2 — minimal unavoidable prior / architecture-agnostic derivation

Closes the five rows of `### Z2` in issue comment `5684819296`.

## What it establishes

Over the registered `65552`-candidate binary mechanism universe, with every
hypothesis frozen before the enumeration that adjudicates it:

- **`MP-1`** the syntactic encoding is a strictly non-uniform prior over
  semantics: `65552` candidates collapse to `K = 21904` behaviour classes of
  size `1..785`, at exact total-variation distance `3535488/5608793` (about
  `0.6304`) from uniform-over-classes. "Prior-free" has no referent until a
  reference measure is named, and the two natural namings are this far apart;
- **`MP-2`** a family-blind enumeration is itself a large commitment: in
  canonical order one class is reached at probe `1` and another only at probe
  `65547`;
- **`MP-3`** the bias ladder, exact, on `1906128` undetermined held-out
  prediction pairs: `1/2` with no preference and no measure, `23315/39711` with
  the best of `300` one-bit structural preferences, `5671/11346` with the worst,
  `80663/119133` with a full uniform measure. One bit is enough to beat chance
  **and** enough to fall below it;
- **`MP-4`** the candidate-weighted and class-weighted majorities disagree on
  exactly `0` version-space buckets — the freeze's `H5` refuted and published;
- **`MP-5`** the invariance table over three verified-bijective re-encodings,
  from which the defensible P3/P4 criterion is read: behaviour-multiset and
  objective quantities are invariant, candidate identity and enumeration order
  are not. `H7c` refuted: no registered generator is inadmissible;
- **`MP-6`** one generic twelve-predicate vocabulary and one grammar (digest
  byte-identical across all six runs) select **exactly** the member sets of all
  six registered named families — `16`, `4096`, `512`, `4096`, `61440`, `256` —
  with `0/200` random specifications from the same `3^12` space hitting any
  family;
- **`MP-7`** the live corpus carries `0` informal `prior-free` flagship claims:
  `87` occurrences over `448` files, all in `AUTHORITY 39`, `QUALIFIED_TERM 29`,
  `MIRROR 13`, `NEGATION 5`, `MENTION_NOT_USE 1`.

  Those counts are **corpus-timestamped** at `source_main`
  `5e57d4292266bccf435136e1f7d72caa32e920a0`: the audit scans every
  `research/gmi-833-*` markdown file, so any lane that adds or removes a
  `prior-free` token moves them, and this package's own documents are inside the
  corpus it measures. What is stable, and what CI asserts
  (`check_row3_verdict_v1.py`), is the **verdict** — `LIVE_FLAGSHIP` empty, the
  classifier's planted positives all firing and its planted negatives all quiet
  — not the arithmetic of the day.

## What it does not establish

No universal no-free-lunch theorem, nothing about real or trained systems, no
claim that one bit is the minimum bias outside this universe, no P4 certificate,
no claim about MLP/CNN/Transformer families, and no re-earning of the
terminology migration, the boundary law `lambda* = eta*p/2`, or the
blind-recovery protocol.

Claim ceiling:

```
GMI_833_Z2_EXACT_ENCODING_INDUCED_PRIOR_AND_MINIMUM_SUFFICIENT_INDUCTIVE_BIAS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z2-minimal-prior-v1/independent_minimal_prior_oracle_v1.py
python3 -I -B  research/gmi-833-z-z2-minimal-prior-v1/z2_minimal_prior_v1.py
python3 -I -B  research/gmi-833-z-z2-minimal-prior-v1/prior_free_site_audit_v1.py
python3 -I -B  research/gmi-833-z-z2-minimal-prior-v1/test_z2_minimal_prior_v1.py -v
python3 -I -O -B research/gmi-833-z-z2-minimal-prior-v1/test_z2_minimal_prior_v1.py -v
```

Stdlib only, exact arithmetic, no float in any claim. Route A about 85 s and
Route B about 20 s on one core.

## The instruments failed first — three times

1. The learnability instrument was **inert**: every learner, including all `200`
   nulls, landed within one percent of the same accuracy, because the feature
   restriction was followed by a counting majority that it almost never changed.
   Repaired with a preference-only learner scored on the undetermined
   subpopulation (`FREEZE_V1_AMENDMENT_2.md`).
2. That amendment's **explanation was wrong**: it blamed a majority of
   determined pairs, which the repaired run measures at `3151/16388`, about
   `19.2` percent. Corrected rather than edited (`FREEZE_V1_AMENDMENT_3.md`),
   together with the `H6'` revival lever — which then **failed**: the sub-chance
   witness came from the exhaustive `V12` sweep, not from the declared
   semantic-rarity features.
3. The row-3 site classifier **cried wolf** on its first real run, flagging three
   live flagship sites that were all classifier defects — a backticked mention, a
   cross-line negation, and a negation broken by markdown bold. The validation
   gate had passed because none of those shapes was planted
   (`FREEZE_V1_AMENDMENT_4.md`).

`H3` (naive) survived; `H5`, `H5'`, `H6'` and `H7c` were refuted and are
published as refuted.
