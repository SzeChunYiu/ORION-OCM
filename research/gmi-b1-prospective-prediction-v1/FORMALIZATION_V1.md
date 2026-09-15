# Formalization V1 — prospective prediction custody on two exact known-family objects

Issue: #776. Parents: #602 P0, #431, #433.

## What this result is

The old B2/B3 witnesses are exact derivations, but their `predicted` and `measured` quantities are produced inside the same run. `GMI_PROTOCOL_CONFORMANCE_AUDIT_V1.md` correctly classifies those rows as **not prospectively frozen**.

This successor changes only the evidence order. The donor theorems are not rewritten. A freeze was committed first (`526ff2d4…`), then a prediction-only generator and receipt were committed (`0be66cce…`), and only afterward did the independent scorer/remint implementation exist (`bc15c3ad…`). The protected result was committed later (`0e7a7172…`).

The scientific object is therefore:

```text
registered exact law
-> immutable expected values
-> later unseen surface realization
-> independent exact measurement
-> compare
```

rather than:

```text
same process computes expected and measured values
```

## B2 theorem specialization

For period `m>1` and accepted residue `a`, define the response after a two-symbol history `h` by

```text
f(h) = 1[count(s1,h) mod m = a].
```

### Exact quotient cardinality

The current residue `r=count(s1,h) mod m` is sufficient: future responses depend only on `r` and future increments. Therefore there are at most `m` response-preserving states.

For any two distinct residues `r != q`, choose an added count `k` such that `r+k = a (mod m)`. The continuation `s1^k` makes the response from residue `r` true. Since `q-r` is nonzero modulo `m`, the response from `q` is false for that same continuation. Thus every pair of residues is future-distinguishable, giving at least `m` states.

Hence the quotient index and minimal recurrent state cardinality are exactly `m`.

The scorer does not import this proof as a formula. It builds response signatures for every residue across a complete length-`m` unary continuation set and checks pairwise distinction. It separately constructs the residue-counter realization and replays bounded histories as an executable control.

### Stateless negative

A current-symbol-only policy merges histories with the same final surface token. For each protected `m>1`, such histories can have different count residues and therefore different demanded responses. The scorer groups histories by current token and confirms mixed responses. A matched current-symbol-only response is also scored and correctly becomes stateless-sufficient, so `stateless=false` is not hard-coded.

### State/history crossover

Under the frozen cost units, recurrent state costs one slot per quotient class, `m`, while explicit retained history costs one slot per symbol, `L`. Thus history is cheaper for `L<m`, tied at `L=m`, and state is first cheaper at `L=m+1`. The measured quotient cardinality, not the prediction field, is used to reconstruct the scored crossover.

## B3 theorem specialization

For Boolean feature dimension `d`, integer coefficient vector `w` in the frozen grid, and exact real-valued response

```text
y = <w,x>,
```

observe standard basis vectors in a post-prediction feature-reminted order.

### Identification

After the first `d-1` independent basis observations, exactly one coefficient has not been observed. Every value in the seven-point registered coefficient grid remains possible for that coordinate, hence exactly seven candidate vectors remain consistent.

After all `d` independent basis observations, every coefficient is fixed exactly, so one candidate remains.

For the dependent control, take the first `d-1` independent basis vectors and duplicate the first. There are `d` observations but rank only `d-1`; the unobserved coefficient remains free over the same seven-point grid. Thus seven candidates remain and the vector is not identified. The sample bound is about independent information, not row count.

The scorer verifies these counts by literally enumerating every candidate vector in the registered grid. An independent test checker uses the observation-rank/free-coordinate argument rather than importing the scorer's enumeration routine.

### Full Boolean basis

The set of all Boolean monomials corresponds one-to-one with all subsets of the `d` coordinates, including the empty subset. The scorer explicitly enumerates those subsets; the count is `2^d`. The Boolean input table also has one row per binary `d`-tuple, also `2^d`. Therefore a full monomial feature basis has table cardinality at this finite scope.

## Surface remint

The concrete B2 symbol names and B3 feature orders are derived from the **prediction-authority commit**, which did not exist at the initial freeze. Two independent domain separators generate two different surfaces. Neither surface changes the semantic object. Both are scored, and every measured invariant must be identical across them.

This is a semantic-remint check, not an independent new theorem family.

## Custody

The Git-object gate must establish all of the following:

```text
freeze = 526ff2d4ddee43abc2cf69e8ef820e9b55278154
prediction = 0be66ccebf50bd7e0fac31421b052d2d858adbce
scorer = bc15c3ad583295d1c6dd2bc6f6d00a9ab2b3d984
result = 0e7a717288ee57ef40e3ac0d1015aa7abe6e8d6e

freeze < prediction < scorer < result
```

At the prediction commit, `score_v1.py` and `RESULT_V1.json` must be absent. At the freeze commit, prediction/scorer/result artifacts must all be absent.

## Protected result

Eight protected cases were scored on two post-prediction surfaces each.

- B2: periods 4, 5, 6, 7 all matched exact quotient/minimal-state/stateless/crossover predictions.
- B3: dimensions 2, 3, 4, 5 all matched the frozen `7 -> 1` independent-identification counts, stayed at 7 under the dependent-count control, and matched full-basis/table sizes 4, 8, 16, 32.
- Prediction-tamper, family-label injection, current-symbol-only, and dependent-observation hostiles all fired.

Terminal:

```text
B1_PREOUTCOME_PREDICTION_CUSTODY_SUPPORTED_ON_TWO_FRESH_EXACT_FAMILY_REMINTS
```

## Claim boundary

This establishes that a real freeze/predict/score evidence pipeline works for two materially different exact family objects. It does not retroactively convert the old 21 witnesses into preregistrations.

It does not close B1 globally. In particular, the current corpus audit still reports real-regime replication at 0/19 and matched negative controls measured for only 11/19 families. Other families still need their own prospective successor evidence where that requirement matters.

Forbidden from this result alone:

```text
B1_COMMON_PROTOCOL_CLOSED
KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE
ALL_KNOWN_FAMILIES_PROSPECTIVELY_VALIDATED
REAL_REGIME_REPLICATION_COMPLETE
COMPLETE_GMI
```
