# What composition costs: a predicted law for a form nobody had built

Date: 2026-09-14. Addresses checklist section **K** — predict unseen forms before discovery, and
predict how far their capability can go.
Prediction: `gmi_microscope/predict_composition_law.py`, frozen at commit `0c9abc83`.
Adjudication: `gmi_microscope/compare_composition_law.py`, written afterwards.
Receipts: `STAGE_COMPOSITION_LAW_PREDICTION_V1.json`, `STAGE_COMPOSITION_LAW_VERDICT_V1.json`.

## 1  The form, and why it was unseen

Every family in this corpus is derived for **one** obligation. Nothing had been built for a machine
required to satisfy **several at once**, and no family states what that costs. The generic answer — the one
you get by tracking each obligation separately — is the **product** of their indices.

That is the form this document predicts and then measures: the multi-obligation machine.

## 2  The prediction, frozen before the adjudicator existed

The freeze is checkable from git rather than asserted:

```
0c9abc83  FROZEN PREDICTION about an unbuilt form: what composition costs
          ... later commit ...  the adjudicator
```

**Law 1 — composing counting obligations is sub-multiplicative, and exactly lcm.**
`A_m` accepts iff the number of `b`s is divisible by `m`; its index is `m`. For a k-fold intersection the
product bound is `∏ mᵢ`. The prediction is that the index is exactly **`lcm(m₁ … m_k)`**.

The reason is that the obligations are *not independent*: **one counter drives all of them.** By the Chinese
Remainder Theorem the joint residue `(n mod m₁, …, n mod m_k)` is determined by `n mod lcm`, and takes
exactly `lcm` distinct values. Composition is free wherever the moduli share factors, and costs the full
product only when they are pairwise coprime.

**Law 2 — composing with a suffix obligation is additive, not multiplicative.**
`B` accepts iff the string ends with `ab`; its index is 3. The prediction is that intersecting *any* of the
composed counting forms with `B` costs exactly **+2**, never ×3 — the same `+2` already measured for a
single modulus, now claimed over a *composed* form, which had not been tested.

**Capability ceiling.** With moduli at most 12, the largest attainable index is **27720 = lcm(1…12)**, and no
choice of moduli from that range exceeds it *however many obligations are stacked*.

## 3  The test set discriminates rather than flatters

This was fixed before measuring. The tuples were chosen so that two rival hypotheses are both excluded:

| moduli | product bound | predicted | measured |
|---|---:|---:|---:|
| 6,10,15 | 900 | 30 | **30** |
| 4,6,9 | 216 | 36 | **36** |
| 12,18 | 216 | 36 | **36** |
| 2,4,8 | 64 | 8 | **8** |
| 6,15 | 90 | 30 | **30** |
| 4,6 | 24 | 12 | **12** |
| 2,3,5 | 30 | 30 | **30** |
| 3,5,7 | 105 | 105 | **105** |

`(6,10,15)` collapses **30×** below the product bound; `(3,5,7)` does not collapse **at all**. So
*"composition always collapses"* and *"composition is always the product"* are both refuted by the same
table, and a law that merely said "cheaper than the product" would not have survived. Both of those
discrimination conditions are asserted in the witness, so a future test set that lost them fails CI.

## 4  Verdict

| claim | result |
|---|---|
| Law 1 — index = lcm | **holds on all 11 tuples** |
| Law 2 — suffix costs +2 | **holds on all 11 tuples** |
| ceiling — max index over moduli ≤ 12 | measured **27720**, predicted 27720 |

Collapse against the product bound ranges from **1.0× to 30.0×**.

## 5  What this says about capability, which is what section K asks

**Capability does not grow with the number of obligations; it saturates.** Stacking more counting
obligations cannot take the machine past the lcm of the moduli available to it. Adding a fourth, fifth or
hundredth obligation drawn from moduli ≤ 12 buys nothing beyond 27720 states. The ceiling is a property of
the *alphabet of obligations*, not of how many are imposed.

That is a prediction about a form's reach, made before the form was built, and it is the shape section K
asks for: not "this machine can do X" but "no machine of this kind can exceed X".

**The two laws also separate two kinds of composition.** Counting obligations compose *multiplicatively but
with cancellation* (lcm). A suffix obligation composes *additively* (+2). These are different mechanisms —
one is arithmetic sharing of a single counter, the other is the collapse of suffix distinctions that no
suffix can probe — and a theory that treated composition as one operation would predict neither.

## 6  Scope

Exact integer arithmetic, no sampling. Eleven tuples, verified by explicit product construction restricted
to reachable states followed by Myhill–Nerode table filling. The ceiling is verified as a max-lcm
enumeration over all 4095 non-empty subsets of moduli 1…12 — **not** by constructing the 27720-state
machine, which is stated in the receipt's `scope` field. The laws are established for counting obligations
over a two-letter alphabet and one suffix obligation; nothing here claims a general composition law for
arbitrary obligations, and Law 2's mechanism is specific to obligations whose distinctions no suffix can
probe.
