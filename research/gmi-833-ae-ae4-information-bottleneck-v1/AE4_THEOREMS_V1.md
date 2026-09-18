# AE4 named results v1

Scope, fixed by `FREEZE_V1.md`: an 8-atom support with a uniform exact prior
`1/8`, all `Bell(8) = 4140` **deterministic** encoders (hard partitions), seven
registered worlds — five deterministic targets, one exactly rational channel and
one three-valued target whose class sizes force `log2(3)` into the arithmetic —
and a nine-point exactly rational tradeoff ladder.

**No logarithm is ever evaluated.** Every entropy is an exact map
`prime -> Fraction` denoting `sum_q c_q log2(q)`, and the order of two such
values is the sign of `prod_q q^(D c_q) - 1` for a common denominator `D`: a
comparison between two integers. A value is printed as a plain rational only
when its prime support is exactly `{2}`; `H(Y)` for the `AND` world is reported
as `2*log2(2) - 3/4*log2(3)`, not as a decimal.

---

## IB-1 — the formalisation, and the scope restriction it carries

`L_beta(T) = I(T;X) - beta I(T;Y)`, minimised over the registered encoder
family. Because the encoders are deterministic, `I(T;X) = H(T)` and the
objective is `H(T) + beta H(Y|T)` up to a constant in `T`.

**The restriction is registered, not implied.** The optimum is over
**deterministic** encoders — the *deterministic* information bottleneck of
Strouse & Schwab 2017 — and not the stochastic-encoder IB of Tishby, Pereira &
Bialek 1999. The receipt carries `stochastic_encoders_optimised: false` as a
checked field and `IB_OPTIMUM_OVER_STOCHASTIC_ENCODERS_PROVED` is a registered
forbidden promotion. Reading one as the other is a detected hostile.

Six crosswalk entries map every symbol onto a parent with a citation.

---

## IB-2 — identification holds only above an exact tradeoff threshold

**Statement.** For each registered world the relation between the GMI minimal
predictive state `T_GMI` and the IB optimum is classified at **every** point of
the ladder, into `EQUAL`, `GMI_STRICTLY_REFINES`, `IB_STRICTLY_REFINES` and
`INCOMPARABLE`. Two of the four occur and two are exactly `0`, and both zeros
are reported.

**The threshold is the content.** `T_GMI` becomes an IB optimum at `beta = 1`
for six worlds and only at `beta = 6` for the noisy channel — because a noisy
channel caps `I(T;Y)` strictly below `H(Y)`, so the relevance term has to be
weighted much more heavily before the full predictive state pays for its own
description. Below the threshold the optimum is a **strict coarsening** of
`T_GMI`. An unqualified identification of the two objects is therefore false,
and the qualifier is a number, not a hedge.

**Falsifier.** A world whose threshold does not exist inside the ladder; the
checks reject a `None` threshold, so a ladder too short to reach the regime is
caught rather than silently reported.

**Forbidden extrapolation.** `GMI_PREDICTIVE_STATE_IS_THE_IB_OPTIMUM`.

---

## IB-3 — the smallest counterexample, and a negative kept

Two results, deliberately kept apart.

**(a) The stronger counterexample does not exist here — earned by exhaustion.**
The kind first sought was an IB optimum *incomparable* with `T_GMI`. Every
support size from 2 to 6 was searched exhaustively over all partitions, all
deterministic targets and the whole ladder: the count is **0** at every size,
and `INCOMPARABLE` is also `0` over the registered 8-atom worlds. At this scope
every IB optimum is `EQUAL` to `T_GMI` or a **strict coarsening** of it — never
incomparable, never a strict refinement. That this holds for *every* finite
deterministic target and encoder is stated as a **conjecture**, not a theorem of
this package; no general proof is offered.

**(b) The counterexample that does block identification.** The predicate the row
actually needs is weaker: `T_GMI` is not an IB optimum. Over deterministic
targets it holds only at `beta = 0`, which is a statement about the objective's
degenerate end. The failure was attributed to **one stage** — the target family,
not the search — and the matching lever applied: registered rational channels,
for which `I(T_GMI;Y) < H(Y)` and the full state stops paying at a strictly
larger `beta`. The smallest support size carrying a counterexample at a
non-degenerate `beta` is then found, and minimality holds because support size 1
is vacuous, so every strictly smaller size is exhausted by construction.

**Why both are reported.** The first predicate was refuted and the second was
initially too weak. Deleting either and presenting only the third would be the
post-hoc pattern this programme exists to prevent; the revival chain is a
recorded field of the receipt.

---

## IB-4 — relevance for `Y` and relevance for action are different orderings

Within a fixed capacity class the encoder carrying strictly **more** information
about `Y` — strictly smaller `H(Y|T)` — can be strictly **worse** for control
value under the registered utility, and the ordering reverses elsewhere. Both
directions are counted over the census, so the claim is that the two objectives
induce genuinely different orderings, not that one dominates.

**Forbidden extrapolation.** `IB_OPTIMAL_IMPLIES_CONTROL_OPTIMAL`.

---

## IB-5 — when forgetting is optimal

**Condition.** Merging two atoms costs no relevant information **iff** they
carry the same conditional law `p(Y|x)`. Capacity `I(T;X)` strictly falls, so
under any capacity constraint the merge is optimal.

The criterion is checked against the exact conditional entropy on **every**
pairwise merge, with zero mismatches, and both sides are witnessed: free merges
and costly merges are both non-zero and both exhibited.
`FORBIDDEN: FORGETTING_IS_ALWAYS_OPTIMAL` — the costly count is what forbids it.

---

## IB-6 — five named reasons to keep what looks irrelevant

Each mechanism carries a witness or is declared `NOT_WITNESSED`; silence about a
mechanism is a package defect.

| mechanism | witness |
|---|---|
| future task uncertainty | a distinction invisible to the present target and required by a registered future one |
| transfer | the same distinction required after transfer to a different registered target |
| revision | the target is revised on half the support and a previously idle distinction becomes necessary |
| causal intervention | a confounded model in which the observational and interventional contrasts differ **exactly**, so an encoder that keeps the treatment and drops the confounder reproduces the observational conditional and still cannot answer the interventional query |
| verifier need | a distinction irrelevant to *producing* the answer and necessary to *checking* it |

The causal entry was initially **NOT_WITNESSED** because the model chosen had no
real confounding — both contrasts came out `0`. That is recorded: a mechanism
whose model cannot move the quantity witnesses nothing. AE13 earns the causal
rows; this entry witnesses only the retention mechanism.

---

## IB-7 — two frontiers, reported separately

The predictive frontier (capacity against `H(Y|T)`) and the control frontier
(capacity against `V_full - V(T)`) are computed over all 4140 encoders and
reported separately, with the size of each, the exact points of each, and the
count of encoders lying on **both**. The sweep used to compute them is verified
against the quadratic domination definition on a registered slice, so the
speed-up is checked rather than assumed.

---

## IB-8 — five prospectively frozen predictions

`Q1`–`Q5` were written into `FREEZE_V1.md` at commit `c05f8f4c` before any
executor, oracle or receipt blob of this package existed; the workflow proves
that ordering by asserting none of those paths resolves at the freeze commit.
They are evaluated over **every** registered world, as the frozen statements say
("at least one registered world", "every registered world") — evaluating them on
one world would under-implement the freeze rather than test it. The price ladder
is the one frozen and is **not** adjusted after a verdict is seen.

`Q3` is checked per transition: where the chosen encoder changes from `a` to `b`
between ladder prices `lo` and `hi`, the exact crossing price
`(gain(a) - gain(b)) / (cost(a) - cost(b))` must lie in `(lo, hi]`. That is the
same statement as membership in the pairwise difference-quotient set, computed
from the two encoders that actually changed.
