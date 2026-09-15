# Freeze V1 — prospective two-phase known-family prediction custody

Issue: #776. Parents: #602 P0, #431, #433.

**Pre-outcome authority.** This commit freezes the scientific question, source authorities, protected successor parameters, prediction laws, post-prediction remint rule, scoring rules, falsifiers, and claim ceiling. At this commit there is no `PREDICTIONS_V1.json`, no successor scorer/oracle, no protected result, and no CI workflow for this capsule.

## Pinned base and donor objects

Base `main` commit:

```text
c0501931d44e91910fa7b9518c35a59d914d7bf3
```

Pinned donor witnesses:

```text
research/machine-intelligence-morphogenesis-v1/gmi_microscope/finite_state_witness.py
blob 5009d9f19eb43c5ee0ab59ee691889543c391102

research/machine-intelligence-morphogenesis-v1/gmi_microscope/linear_family_witness.py
blob 2d2656deed99d4aa603e8d7ec622a4fa706fb147
```

Pinned donor receipts:

```text
research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_FINITE_STATE_V1.json
blob 143df98737d04f6a05df1fe791706d82cff9ffd8

research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_LINEAR_FAMILY_V1.json
blob 94f36f3f294836963b9c933e0a42a9df8db97ec7
```

The donor receipts explicitly report `prediction_frozen_before_outcome: false`. This successor does not edit or upgrade them.

## Separation rule

The evidence order is mandatory:

```text
FREEZE_V1 commit
  -> prediction-only implementation + PREDICTIONS_V1.json commit
  -> successor remint/scorer/oracle implementation
  -> RESULT_V1.json commit
  -> CI/replay hardening
```

The prediction commit must precede every protected scorer/result object. The scorer may read the committed prediction receipt for expected values but may not import/call the prediction implementation. The independent oracle must reconstruct the measured quantities from the frozen semantic parameters.

## No family-label rule

Predictor-visible case rows may contain only:

```text
case_id
object_kind
semantic integer parameters
registered cost units
```

They may not contain architecture names, family names, donor filenames, or target phenotype labels. `object_kind` is one of the generic mathematical objects `periodic_sequence_response` or `finite_coefficient_identification`.

## B2 successor — periodic sequence-response objects

Alphabet surface labels do not exist yet. For each case, the semantic alphabet has two abstract symbols `(s0,s1)`. The response after history `h` is

```text
1[ count(s1 in h) mod period == accepted_residue ].
```

Protected cases:

```text
Q2_A  period=4  accepted_residue=1
Q2_B  period=5  accepted_residue=3
Q2_C  period=6  accepted_residue=2
Q2_D  period=7  accepted_residue=5
```

Frozen prediction law:

1. The response-preserving future quotient has exactly `period` classes.
2. Therefore the minimal recurrent state cardinality is exactly `period`.
3. For every protected case, a policy that sees only the current symbol is insufficient because histories ending in the same current symbol can occupy different residue classes.
4. One state slot is charged per quotient class and one history slot per retained symbol. Therefore explicit history is cheaper for `L < period`, tied at `L = period`, and recurrent state is cheaper first at `L = period + 1`.
5. Any exhaustive machine search that is blind to `period` as a target must find no exact machine with fewer than `period` states and at least one with exactly `period` states.

The prediction implementation may compute these values from `period`; it may not enumerate successor outcomes.

### Post-prediction surface remint

Only after the prediction receipt is committed, the scorer derives concrete symbol strings from the prediction-authority commit:

```text
token(case_id, j) =
  "S_" + SHA256("T602-B1P-B2-SURFACE|" + prediction_commit + "|" + case_id + "|" + j)[:12]
```

for `j in {0,1}`. The scorer must show that replacing these strings with a second independently domain-separated pair leaves all measured invariants unchanged.

## B3 successor — finite coefficient-identification objects

Each protected case has Boolean feature domain `{0,1}^d`, integer coefficient vector `w`, and exact real-valued response `y=<w,x>`. Candidate coefficients for the identification oracle are all integer vectors in `{-3,-2,-1,0,1,2,3}^d`.

Protected cases:

```text
L3_A  d=2  w=(2,-1)
L3_B  d=3  w=(1,-2,3)
L3_C  d=4  w=(-1,2,-3,1)
L3_D  d=5  w=(2,-1,3,-2,1)
```

Frozen observation protocol:

- independent prefix: the `d` standard basis vectors, in a post-prediction reminted feature order;
- `d-1` control: the first `d-1` standard basis vectors;
- dependent-count control: `d` observations consisting of the first `d-1` standard basis vectors plus a duplicate of the first basis vector.

Frozen prediction law:

1. Exact real-valued observations on the first `d-1` independent basis vectors leave more than one candidate coefficient vector consistent.
2. The `d` independent basis observations identify exactly one vector.
3. `d` observations with rank only `d-1` remain ambiguous; count alone is not sufficient.
4. The full Boolean monomial basis over `d` features has exactly `2^d` features, equal to the Boolean input-table cardinality.

The prediction implementation may derive these quantities from `d`; it may not enumerate successor candidate vectors or call the later scorer.

### Post-prediction feature remint

Only after the prediction receipt is committed, the scorer orders feature positions by

```text
SHA256("T602-B1P-B3-FEATURE|" + prediction_commit + "|" + case_id + "|" + original_index)
```

and gives them opaque labels

```text
F_ + first_12_hex_of_same_digest.
```

A second domain separator must produce a different surface order/labels while preserving all measured invariants.

## Prediction receipt contract

`PREDICTIONS_V1.json` must contain, for every protected case:

- the allowed generic semantic parameters;
- the exact expected quantities produced by the frozen laws;
- `outcomes_seen=false`;
- `scorer_exists=false`;
- donor/source identities only in top-level custody metadata, never inside predictor-visible case rows.

The receipt must be deterministic and byte-reproducible from a prediction-only script.

## Independent scoring contract

The later scorer/oracle must be a new file absent from the prediction commit.

For B2 it must independently:

- enumerate bounded histories and continuation signatures deeply enough to stabilize the quotient for every registered period;
- construct an exact `period`-state counter machine and replay it;
- exhaustively reject every smaller state count at a separately frozen finite replay horizon sufficient to distinguish all residue classes;
- test current-symbol-only policies;
- verify the history/state cost ordering.

For B3 it must independently:

- enumerate all candidate integer coefficient vectors in the registered grid;
- count consistency after `d-1`, independent `d`, and dependent `d` observations;
- compute the full Boolean monomial count by explicit subset enumeration, not by importing the prediction formula.

## Hostiles

1. **Prediction tamper:** alter one expected value in memory and require scoring to return mismatch.
2. **Surface remint:** two domain-separated surface encodings must give identical measured invariants.
3. **B2 assumption control:** replace a protected periodic obligation by a current-symbol-only response; the stateless-insufficient conclusion must become false.
4. **B3 dependence control:** `d` dependent observations must not be accepted as identification.
5. **Label injection:** predictor-visible case rows containing `family_name`, `architecture_name`, donor paths, or phenotype labels must be rejected.
6. **Same-phase contamination:** any scorer/result file present in the prediction-authority commit invalidates custody.
7. **Post-outcome mutation:** freeze and prediction Git objects are immutable authorities; later edits do not supersede them.

## Acceptance

The protected V1 result is GREEN only if every frozen B2 and B3 prediction matches the independent scorer on both surface remints, every hostile fires as registered, and Git-object custody proves:

```text
freeze_commit < prediction_commit < scorer/result commits.
```

Normal Python and `python -O` must emit byte-identical prediction/result artifacts.

## Claim ceiling

If GREEN, the strongest allowed terminal is:

```text
B1_PREOUTCOME_PREDICTION_CUSTODY_SUPPORTED_ON_TWO_FRESH_EXACT_FAMILY_REMINTS
```

This is evidence that the repository can execute the B1 pre-outcome-prediction protocol correctly on two materially different exact families. It is not all-family B1 closure and does not change the existing facts that real-regime replication is 0/19 and matched negative controls are measured on only 11/19 families.

Still forbidden from this child alone:

```text
B1_COMMON_PROTOCOL_CLOSED
KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE
ALL_KNOWN_FAMILIES_PROSPECTIVELY_VALIDATED
REAL_REGIME_REPLICATION_COMPLETE
COMPLETE_GMI
```
