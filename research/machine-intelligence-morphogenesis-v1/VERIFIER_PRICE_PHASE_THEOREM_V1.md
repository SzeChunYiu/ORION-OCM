# Verifier-price phase theorem v1

Status: **elementary parent-owned theorem used as a Track-B phase-law calibration**, not an ORION novelty claim.

## Setup

For an unseen query, compare:

### M0 — direct information acquisition

Acquire the correct label/output directly at cost

\[
L>0.
\]

### M1 — proposal + exact verifier + fallback

A learned/rule/program morphology has three mutually exclusive outcomes:

```text
correct proposal with probability/rate c
wrong proposal   with probability/rate w
abstention       with probability/rate a
```

with

\[
c+w+a=1.
\]

Every proposal is externally checked at cost `V`.

- correct proposal costs `V`;
- wrong proposal costs `V+L` because the rejected proposal is followed by direct acquisition;
- abstention costs `L`.

No correctness cost is hidden.

---

# Theorem

The expected M1 acquisition cost is

\[
C_1=cV+w(V+L)+aL.
\]

Using `c+w+a=1`,

\[
C_1=L+(c+w)V-cL.
\]

The direct parent costs

\[
C_0=L.
\]

Therefore

\[
C_1<C_0
\]

iff

\[
(c+w)V<cL.
\]

If `c+w>0`, equivalently

\[
\boxed{
\frac{V}{L}<\frac{c}{c+w}
}
\]

where

\[
\frac{c}{c+w}
\]

is proposal precision conditional on making a proposal.

If `c+w=0`, M1 always abstains and exactly ties M0 on this narrow coordinate.

---

# Interpretation

The phase boundary between direct acquisition and propose/check/fallback is controlled by two quantities:

```text
verification price / information-acquisition price
proposal precision
```

The proposal attempt rate affects total cost only through the number of verifier calls; after the algebraic cancellation above, the sign of the advantage is determined by conditional proposal precision versus `V/L`.

This is ordinary decision/lifecycle economics and value-of-information style reasoning. It is adopted as a parent theorem.

---

# Connection to the exact calibrations

## 3-bit exploratory threshold after frozen V=0.25 run

Observed proposal precisions:

```text
SIMPLE  ~0.6332
COMPLEX ~0.4493
```

Thus a post-outcome interval

```text
0.4493 < V/L < 0.6332
```

would induce different preferred policies. This was explicitly treated as exploratory and not retroactively promoted.

## 4-bit prospective replication

The follow-up froze

```text
V/L=0.5
```

before 4-bit acquisition outcomes.

Observed:

```text
SIMPLE proposal precision  = 0.7156875659 > 0.5
COMPLEX proposal precision = 0.4832267848 < 0.5
```

so the theorem predicts exactly the observed policy crossover:

```text
SIMPLE  -> M1 rule proposer/checker cheaper
COMPLEX -> M0 direct acquisition cheaper
```

The 4-bit freeze therefore tests the theorem's region prediction rather than inventing the threshold after outcomes.

---

# Why this matters for Track B

This is the simplest complete example of the type of law Track B seeks:

```text
measurable ecology / mechanism coordinates
-> analytically derived phase boundary
-> prospective disjoint test
-> different morphology/policy frontier regions
```

But the mechanism is heavily parent-owned and the “morphologies” are tiny learning policies. The scientific challenge is to discover similarly predictive boundaries for richer, **non-equivalent intelligence morphologies**.

Candidate future replacements for `proposal precision` include derived measures of:

```text
credit-assignment information
representation complexity
locality / coupling
plasticity
reuse horizon
revision rate
inference vs acquisition amortization
communication / memory cost
```

---

## Terminal

```text
VERIFIER_PRICE_PHASE_BOUNDARY_PROVED_FOR_PROPOSE_CHECK_FALLBACK_POLICY
```

No general intelligence claim follows from this theorem alone.
