# GMI #833 Section Z / Z13 — adjudication freeze for the frozen prediction `Z13-P1`

This freeze is committed **before any executor, oracle, receipt or enumeration
exists in this package**. Git order proves it.

- `source_main`: `0dcdec54fbece041ee2b7cd1f630469ad85d19d3`
- branch: `research/833-sec-z4`
- adjudicated artifact: `research/gmi-833-z-z13-property-prediction-freeze-v1/FREEZE_V1.md`
  - blob sha `25febfa62cbf73f1f239f3de29436ecd043e67d9`
  - freeze commit `0cc617fc71334b08a60d476993785a7fd3c04a6f`, authored `2026-09-18 18:49:10 +0200`
  - produced by a **different lane** (`research/833-sec-z3`, PR #1039), explicitly
    "not a closure", explicitly for "a later, separate lane" to adjudicate.
    This package is that lane.

Claim ceiling:

```
GMI_833_Z13_ADJUDICATED_VERDICT_ON_FROZEN_PREDICTION_Z13_P1_AT_REGISTERED_THREE_MODE_FINITE_STATE_SCOPE
```

## 0. Disclosure — what was known before this freeze was written

Honesty about ordering matters more than the appearance of blindness. Before
writing this file the author ran a throwaway scratch probe (`probe1`, never
committed, not a route of this package) over the `b <= 1` slice and hand-derived
the resource-ladder algebra. That probe indicated, and this freeze therefore
*expects*:

1. that the frozen closed form for the upper threshold is likely wrong, because
   it uses the **level** `R0(delay2 | b = 1)` where the resource ladder requires
   the **difference** `R0(delay2 | b = 0) - R0(delay2 | b = 1)`;
2. that `P-b` and `P-c` are likely **jointly unsatisfiable** at `b = 1`;
3. that the matched negative ecology at `p2 = 0` is likely misidentified.

Declaring the expectation in advance is what makes the scoring rules below
binding: they are written so that a HIT is still reachable on every axis, and no
rule may be adjusted after the committed executor runs. Any later change to a
rule in §2–§5 must appear as a numbered `FREEZE_V1_AMENDMENT_<n>.md` committed
**before** the receipt it affects.

## 1. The universe, declared exactly

Faithful extension of the registered binary-transducer universe of
`research/gmi-833-z-z6-discrimination-v1` (address `a = 4*st + 2*mode + cur`,
i.e. **mode-indexed** output *and* next-state entries).

- input sequences: `L = 4`, uniform independent bits, all `2^4 = 16` sequences,
  exact rational weights;
- modes `m in {0, 1, 2}`: target at time `t` is `seq[t - m]`;
- canonical initial state `0`; state budget `b in {0, 1, 2}`, `2^b` states;
- **scored window** `t in {2, 3}` — the common window on which all three targets
  are defined. This is the faithful extension of Z6's `t in {1, ..., L-1}`, which
  is Z6's own common window for its two modes. `32` scored moments per mode.
- declared cost `C = eta * (p0*r_now + p1*r_delay1 + p2*r_delay2) + lambda*b`
  with `p0 + p1 + p2 = 1`, exactly as `Z13-P1` declares it.

### 1a. Declared deviation from the frozen adjudication instruction

`Z13-P1` §3.1 says "Build the extended universe exhaustively ... Record its
size." At `b = 2` the universe has `(2^8 * 2^16)^3 = 2^72` members and cannot be
enumerated. This package therefore:

- reports the **exact** size by closed form (an integer, not an estimate), and
  enumerates exhaustively at `b in {0, 1}` where enumeration is feasible;
- replaces enumeration at `b = 2` by a **proved reduction**, which must itself be
  stated as a named lemma with a falsifier and verified independently:
  - `MODE-INDEPENDENCE`: because `mode` indexes both the output and the
    next-state table, the three channels share no entry, so the cost separates
    and each channel may be minimised independently;
  - `MAJORITY-OPTIMALITY`: for a fixed next-state function the error-minimising
    output table is the per-address majority target, so
    `min_error(b, m) = min over next-state functions of sum over addresses of min(n0, n1)`.
- The reduction is **not** licensed by assertion. Route B must verify both lemmas
  by brute force over the full `(output table, next-state)` product at reduced
  `L` and at `b in {0, 1}`, where that product is small enough to enumerate.
  If either lemma fails anywhere it is checked, the whole `b = 2` line is
  reported as NOT ESTABLISHED, not repaired.

## 2. Conventions fixed now, before any enumeration

**C-1 (next-state reading).** The **primary** reading is mode-indexed
next-state, as above, because that is literally Z6's address map and `Z13-P1`
declares itself an extension of Z6. A second reading — one next-state function
shared by all three modes, outputs still mode-indexed — is pre-registered here as
a **sensitivity line only**. It may never supply a second chance at a HIT: if the
two readings disagree on any scored item, the primary reading is the verdict and
the disagreement is reported as a convention-dependence finding.

**C-2 (dominance).** `Z13-P1` states its niche as "the unique property-class
minimiser". Two dominance metrics are therefore scored, both reported, neither
selected after the fact:

- `D-STRICT`: the candidate's property class is the **unique** cost-minimising
  property class (ties with any other class count as failure);
- `D-LEVEL`: the state budget `b = 1` is the **strict** minimiser of `C` over
  `b in {0, 1, 2}` (ties count as failure).

**C-3 (the niche is an interval claim).** The frozen niche is the open interval
`(lambda_2*, lambda_1*)` with the two frozen closed forms. Scoring compares the
frozen interval against the interval actually observed, as exact rationals, on a
`lambda` grid that is guaranteed to straddle both endpoints and to contain at
least one point strictly inside and one strictly outside each side. Endpoint
equality is scored as exact rational equality, never numerically.

**C-4 (the negative ecology is a mechanism claim).** `Z13-P1` states two things
at `p2 = 0`: that "the interval `(lambda_2*, lambda_1*)` collapses", and that the
morphology "must lose its advantage everywhere". The first is a **mechanism**
claim and is scored by the exact width of the observed interval; the second is a
**dominance** claim and is scored under both `D-STRICT` and `D-LEVEL`. Both are
reported. The mechanism claim is the one the freeze itself offers as its
falsifier, so it is the primary scoring line.

## 3. What counts as a HIT

`Z13-P1` is HIT only if **all** of the following hold, exactly:

- `H-1` `lambda_2* = eta*p2*R0(delay2 | b = 1)` is the observed lower endpoint in
  every scored world;
- `H-2` `lambda_1* = eta*p2*R0(delay2 | b = 1) + eta*p1*R0(delay1 | b = 0)` is
  the observed upper endpoint in every scored world;
- `H-3` the observed unique minimiser on the whole open frozen interval satisfies
  `P-a`, `P-b`, `P-c`;
- `H-4` `P-d` holds **non-vacuously**: the property bundle `P-a and P-b and P-c`
  is satisfiable by at least one candidate at `b = 1`, and no lifted member of the
  six registered named families
  (`F_STATELESS`, `F_DEAD_TABLE`, `F_FROZEN_STATE`, `F_MOORE`, `F_MEALY_PURE`,
  `F_IDENTITY_STATE`) satisfies it while being a unique minimiser in the niche.
  **If the bundle is unsatisfiable, `P-d` is recorded `VACUOUSLY_TRUE` and
  `H-4` FAILS**: a property test no object can pass is the tautology failure class
  this section has already been caught by once.
- `H-5` the matched negative ecology behaves as frozen under `C-4`.

Anything less is a MISS on the named axes, published as such in
`FAILED_PREDICTION_REGISTER_V1.json` with the exact retired text. A MISS may not
be repaired into a HIT. A repaired law may be **derived and published beside**
the miss, clearly labelled as derived after the fact and therefore not
prospectively confirmed by this package.

## 4. Two materially independent routes

Route B may not import Route A. Route A simulates candidates over sequences and
tallies per-address majorities; Route B must recompute every reported quantity by
a different construction — full `(table, next)` product enumeration where
feasible, and an independently written search (not exhaustive enumeration) where
not — and must independently verify `MODE-INDEPENDENCE` and `MAJORITY-OPTIMALITY`
rather than assuming them.

Hostiles must be **shown to move the quantity they perturb**. A hostile that
cannot change any scored number is inert and is itself a defect.

## 5. The exact issue rows this package may reconcile

Section Z lives in issue comment `5684819296`. Verbatim rows of `### Z13 — Genuine unseen-form / W4 gate`:

```
- [ ] Freeze a property-first prediction for an unobserved morphology from theory alone.
- [ ] Use P3/P4 architecture-uncommitted search.
- [ ] Recover the candidate without its macro/property template being inserted into the search grammar.
- [ ] Reproduce under grammar remints.
- [ ] Reproduce under independent search algorithms.
- [ ] Perform strongest-parent reduction against all known relevant architecture families.
- [ ] Show a semantics/resource/developmental distinction not reducible to syntactic novelty.
- [ ] Predict the niche in which the candidate should dominate before testing.
- [ ] Claim W4/new-domain status only if the registered W4 criteria are actually met.
```

The remaining three rows of `### Z13` are **out of scope for this package and may
not be touched by it**:

```
- [ ] Demonstrate that niche advantage prospectively.
- [ ] Demonstrate a matched negative ecology where the advantage disappears.
- [ ] Replicate independently.
```

Reasons, fixed now: the frozen niche and the frozen negative ecology are the two
objects under adjudication here, so this lane cannot also be the lane that
demonstrates them; and independent replication is by definition not self-suppliable.

All six rows of `### Z16 — Groundbreaking-result gate` are out of scope. A
groundbreaking-result claim built on a prediction this package may find
partially refuted would be closure by narrowing.

**No neighboring row is earned here.**

## 6. Forbidden promotions

```
Z13_P1_REPAIRED_INTO_A_HIT
Z16_ROW_CLOSED_BY_THIS_PACKAGE
W4_STATUS_CLAIMED
NICHE_ADVANTAGE_DEMONSTRATED_PROSPECTIVELY_BY_THIS_LANE
NEGATIVE_ECOLOGY_DEMONSTRATED_PROSPECTIVELY_BY_THIS_LANE
DERIVED_REPAIR_PRESENTED_AS_PROSPECTIVELY_CONFIRMED
VACUOUS_PROPERTY_TEST_COUNTED_AS_EVIDENCE
RESULT_EXTENDED_BEYOND_L_EQUALS_4_OR_b_GREATER_THAN_2
```
