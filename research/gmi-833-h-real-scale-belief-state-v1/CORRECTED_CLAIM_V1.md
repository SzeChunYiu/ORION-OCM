# Corrected claim record — `gmi-833-h-real-scale-belief-state-v1`

This file records a claim that this package's own measurement **refuted**, and
the corrected claim that replaces it. It exists because the package must not
contain a claim its receipt contradicts, and because a boundary is only worth
what its correction record is worth.

## The claim, and where it came from

While the amended ecology `F17` was being screened (before the readout language
of this package was finalised), the measured picture was:

- the registered label's base rate on the fit slice is 0.1047, so the
  fit-majority class is `0` and the registered majority fallback therefore
  reproduces the constant arm `C0` on every query the table does not cover;
- on the full held set the best readout found was `C0`, at 10,099 errors —
  exactly the majority rule's count;
- with the store extended past the registered slice to **all 776,142
  positions** (100% coverage), the best arm still made **4,570** errors against
  an F1 need of 4,041.

From those three measurements the drafting claim was: *the registered F1
coordinate is structurally unsatisfiable at this label — the label's own
optimal decision error exceeds half the majority rule's, so no readout of any
closed language and no store budget can close it.*

That claim was drafted into an earlier version of `FREEZE_V1.md` section 9 as
**falsifier 3**. It is kept in the freeze in that exact form, because a
falsifier registered with numerical form is what makes the refutation
checkable rather than a private correction.

## Why it was wrong

The screened arm set did not contain a correctly-defined stored-label arm for
the amended ecology. Once the language was finalised with `MEM_FALLBACK`
defined as *the stored posterior of the query under the slice's own table*, the
measurement changed:

- held winner `MEM_FALLBACK`, **1,005** errors against the majority's 10,099 —
  F1 holds with room to spare;
- with the store set to the whole source, `MEM_FALLBACK` reproduces the label
  **exactly: 0 errors on all 97,018 held queries**;
- the best weighted-evidence arm is `WPAIR>=3_12` at 11,421 errors, and the
  registered weight reassignment moves it only 11,421 → 14,083 (1.23×).

So the label is not merely attendable — it is **storable**, and a store that
holds the query's completions holds the label. The F1 coordinate is satisfied
by the stored-label read, and the boundary of this package is a different one:
the **intended class** (`WEIGHTED_EVIDENCE_BELIEF`) loses to the stored-label
read, and the registered null cannot separate them.

## The corrected claim

> On the registered amended ecology `F17` at `SIGMA_H17R`, the family-blind
> winner rule over the closed readout language `R` recovers
> `STORED_LABEL_READ_WITH_FALLBACK`, not the intended
> `WEIGHTED_EVIDENCE_BELIEF`. The intended class's best arm makes 11,421 held
> errors against the stored-label read's 1,005, and the registered
> weight-reassignment design null separates them by only 1.23× against the
> registered 3× bar while leaving every raw count arm bit-identical. The row is
> therefore **not recovered at this scope**, and stays open.

## The registered falsifier that fired

`FREEZE_V1.md` section 9 falsifier 3, verbatim: *the label's full-source
optimum — the best achievable decision error over the label, with the store set
equal to the whole source — does **not** exceed half the held majority count
(which would falsify the claim that F1 is structurally unsatisfiable at this
label)*.

Measured: the full-source optimum is **0**, and half the held majority count is
**5,049**. `0 > 5,049` is false, so the falsifier **fires**: the F1
unsatisfiability claim is refuted. `RESULT_V1.json` carries
`registered_falsifier_3.falsifier_3_fired = true` and the ledger verdict is
`BOUNDARY_REPORTED__REGISTERED_FALSIFIER_3_FIRED`, and both routes A and B
assert this condition. The refuted claim appears nowhere in this package except
in this file and in the freeze's falsifier, where it belongs.

## What this changes and what it does not

- It **changes** the statement of the boundary: from *F1 is unattainable* to
  *the intended class is dominated by the stored-label read*.
- It does **not** change the outcome for the row: the row stays open, the
  reconciliation is empty, and no promotion of any kind is claimed.
- It does **not** change the `F15` boundary
  (`F15_EARNED_BOUNDARY_V1.md`), which is a separate ecology and a separate
  measurement, made with a store whose table cannot read the label: there the
  label depends on source tokens outside the store, the 100%-coverage F1 miss
  (4,570 against 4,041) stands, and the registered reassignment leaves the raw
  arms bit-identical with the weighted winner degrading by 2.07×.
- It **does** demonstrate the package's own rule working: a claim drafted from
  screens was refuted by the authoritative run, and the refutation was recorded
  with its number and its verdict flag rather than quietly dropped.

## Ledgers

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered slice and presentation; the registered label with `T* = 8`; the
88-arm language of the slice addendum; the store = whole source used only as a
boundary datum (0 errors), never as a fitted configuration.

**Dependencies.** `REAL_RUNS/scope_SIGMA_H17R.json` for every measured number;
`FREEZE_V1.md` section 9 for the falsifier text as registered;
`RESULT_V1.json` for the verdict flag.

**Falsifiers.** A store budget at which the stored-label read fails to
reproduce the held labels; a language in which a weighted-evidence arm beats
the stored-label read; a reassignment under which the intended class separates
from the stored-label read while the raw arms stay intact. Any one would
invalidate this correction record.

**Strongest parents.** The requirement ledger's discipline that a falsifier is
registered before the outcome and evaluated mechanically afterwards; the
sibling packages' corrected-claim records (the H05 R09 correction and the
sibling `MEM_FALLBACK` admission forms).
