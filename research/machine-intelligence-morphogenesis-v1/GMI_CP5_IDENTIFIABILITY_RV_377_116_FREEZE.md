# RV-377-116 — FREEZE: CP5, operational identifiability

Frozen BEFORE the run. Outcomes appended only.

## What CP5 requires, and why CP2 already threatens it

CP5 asks for **operational identifiability and realization theorems, so the formal objects
can be measured in arbitrary implementations.** Identifiability is the harder half: can the
theory's internal objects be recovered from black-box observation of a system?

The corpus's central internal object is the **carrier** — the dominant state kind actually
read by the served computation (`NONE` / `DENSE` / `TABLE` / `KVSTORE` / `PROGRAM`). It is
the descriptor `B1` uses to say *which known mechanism* a search recovered, and every
statement of the form "the coefficient carrier was recovered" is a statement about it.

`RV-377-115` measured that 266 distinct normal forms collapse to 17 distinct observable
signatures, worst case 183 forms sharing one signature. That says structure is not
recoverable from behaviour. **It does not yet say the carrier is not**, because the carrier
is far coarser than the normal form — five values, not 266. Many structures could share a
behaviour while all having the same carrier.

So the question is sharp and open: **do genotypes that are observationally
indistinguishable always have the same carrier?**

If yes, the carrier is identifiable from black-box observation and CP5's identifiability
half holds for the corpus's central object. If no, then two systems can be
indistinguishable under every registered ecology and every registered intervention while
the corpus labels them as different mechanisms — and every carrier-based claim becomes a
claim about the *genotype*, not about anything an observer could measure.

## Method

Reuse `RV-377-115`'s construction exactly: 600 typechecked genotypes from the R5 operator
grammar (seed 12345, 0–12 operators), `observable(g)` = `response_signature` over all 6
registered ecologies × all 6 registered interventions, `carrier_of(g)` from `b1`.

Group by observable signature. Within each group, count distinct carriers.

Report separately for **all 600** and for the **116 behaviourally non-trivial** genotypes
(`RV-377-115` measured 484/600 as trivial — ≤1 distinct non-abstain answer — and the
trivial ones would inflate any collision count for an uninteresting reason).

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| X1 | **The carrier is NOT identifiable** — at least one observable signature is realized by genotypes with ≥2 distinct carriers. | every signature maps to exactly one carrier |
| X2 | The failure **survives restriction to non-trivial genotypes**. | collisions only among the 484 trivial ones |
| X3 | **`NONE` is involved in the majority of colliding groups** — a stateless transducer and a stateful machine that happen to serve the same answers. | most collisions are between two stateful carriers |
| X4 | Fewer than half of all signature groups are collision-free. | ≥ half are clean |

X1 and X2 are predictions **against** the corpus's methodology: if they hold, the carrier
descriptor — on which `RV-377-113`'s G15 step (ii) claim and the whole `B1` recovery
programme rest — is not an observable property, and CP5's identifiability half fails for
the object that matters most.

X3 is a mechanism prediction that could be wrong independently of X1.

If X1 is falsified — if observationally identical genotypes always share a carrier — that
is a genuine positive for CP5 and for the B1 methodology, and it will be recorded without
hedging.

## What this cannot settle

Identifiability here is relative to the **registered** observation set: 6 ecologies × 6
interventions. A richer probe set could separate genotypes this one cannot. A negative
result therefore says "not identifiable by the corpus's own instrument", which is the
operative claim, not "not identifiable in principle". The realization half of CP5 is not
addressed by this run.

---

# RV-377-116 — ADJUDICATION (appended; nothing frozen above was edited)

## Results

```
--- ALL 600 ---
  distinct observable signatures : 17
  signatures with >1 carrier     : 3
  collision-free signatures      : 14  (82.4%)
  worst signature spans carriers : ['DENSE', 'KVSTORE', 'NONE', 'PROGRAM', 'TABLE']
  collisions involving NONE      : 3/3

--- NON-TRIVIAL (n=116) ---
  distinct observable signatures : 12
  signatures with >1 carrier     : 0
  collision-free signatures      : 12  (100.0%)
```

| id | prediction | outcome |
|----|-----------|---------|
| X1 | the carrier is NOT identifiable | **CONFIRMED** — 3 signatures span ≥2 carriers, worst spans all five |
| X2 | the failure survives restriction to non-trivial genotypes | **FALSIFIED** — 12 of 12 clean, **100 %** |
| X3 | `NONE` is involved in the majority of collisions | **CONFIRMED** — 3 of 3 |
| X4 | fewer than half of signature groups are collision-free | **FALSIFIED** — 82.4 % clean |

**Two of four predictions failed, both in GMI's favour.** I expected the carrier descriptor
to be exposed as unobservable and it was not.

## What the result actually says

X1 is confirmed only in the weak, expected sense. **All three identifiability failures are
among behaviourally trivial machines, and every one of them involves `NONE`.** That is the
benign case: a machine that emits at most one distinct answer is a machine whose internals
cannot be inferred, because it exhibits nothing to infer from. A stateless transducer and a
`DENSE` machine that both do nothing are observationally identical, and no one claims
otherwise.

Restricted to the 116 genotypes that actually *do* something, **the carrier is perfectly
identifiable: 12 of 12 observable signatures map to exactly one carrier.**

> **The carrier is an observable property of any machine that is not behaviourally trivial.**
> Two systems indistinguishable under all 6 registered ecologies × all 6 registered
> interventions, and exhibiting more than one distinct answer, always have the same carrier
> on this sample.

## Why this matters more than the prediction I got wrong

This **rescues the descriptor that `RV-377-113` depends on.** `G15` step (ii) — the session's
one surviving positive — is a claim about `E_sym5 | DENSE`, a genotype at capability 0.9115
and squarely in the non-trivial region. Had X2 held, that claim would have been about the
genotype's internals rather than about anything an observer could measure, and the whole
`B1` recovery programme with it.

It does not hold. The carrier survives as an operationally meaningful object exactly where
the corpus uses it.

## Contrast with `RV-377-115`, which is not contradicted

`RV-377-115` found structure **not** recoverable from behaviour: 266 normal forms → 17
signatures, worst 183:1, surviving restriction to non-trivial genotypes. That stands.

The two results are consistent and together they are sharper than either alone:

> **The fine structure of a machine is not identifiable from its behaviour; its carrier is.**

The quotient by observational equivalence is far too coarse to recover a genotype, and just
fine enough to recover which of five mechanism classes the genotype belongs to. CP5's
identifiability half therefore holds **for the coarse object the theory actually quantifies
over**, and fails for everything finer.

## CP5 status

| half | status |
|---|---|
| identifiability of the carrier (non-trivial machines) | **HOLDS** at registered scope, 12/12 |
| identifiability of the carrier (all machines) | **FAILS**, confined to trivial machines, all involving `NONE` |
| identifiability of fine structure | **FAILS** (`RV-377-115`) |
| **realization** | **NOT ADDRESSED** — not started, not claimed |

## Ceiling

Identifiability here is relative to the corpus's own instrument: 6 ecologies × 6
interventions, 600 genotypes, one grammar. A richer probe set could only *improve*
identifiability, so the positive is robust in that direction; but a **different** grammar
could produce colliding non-trivial genotypes this sample does not contain. The claim is
"identifiable by the corpus's own instrument on this grammar", not "identifiable in
principle".
