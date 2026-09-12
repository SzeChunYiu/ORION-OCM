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
