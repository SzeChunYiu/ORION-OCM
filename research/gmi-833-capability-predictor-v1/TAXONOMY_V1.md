# Prospective failure-mode taxonomy — derived before any census

**Status:** FROZEN. This file is committed before the executor, the oracle, the
tests and every receipt. Nothing below was chosen after seeing a failure.

**Derivation principle.** The modes are not enumerated from observed failures.
They are read off the *structure* of the registered contract: a capability
prediction can fall short of a target only because one of the registered cuts
between the global admissible class and the emitted answer removes every
target-attaining realization, or because the registered evidence leaves the
target undecided. Each registered cut therefore generates exactly one mode, and
the two typed non-answers of #851/#913 generate the two terminal modes. That is
the whole derivation; the census only *checks* it is a partition.

## 1. The registered cut ladder

Fix the registered finite realization universe `X` of `SCOPE_V1.md`, a registered
capability contract `E` with threshold `tau > 0`, and a registered resource
object `R`. Write `cap_E(x)` for the exact contract score
`E_{t~mu}[u(trace_x(t))]` of CAP-1 and

```text
q_{E,R}(x) = cap_E(x)      if rho(x) <= b - m coordinatewise
           = UNSATISFIED   otherwise
```

where `b` is the registered 14-coordinate lifecycle budget and `m` the mandatory
shared charge of BUDGET-1. `UNSATISFIED` is a distinct bottom: `UNSATISFIED >= tau`
is false for every registered `tau`.

Five registered cuts, in the frozen ladder order, with the dependency reason for
that order:

| i | cut `P_i` | registered source | why it sits here |
|---|---|---|---|
| 1 | `Expr(M)`   | `M` morphology/capacity constraint | a realization must be expressible before anything can be charged to it |
| 2 | `Res(R)`    | `R` lifecycle budget after the BUDGET-1 mandatory shared charge | an expressible realization must be runnable within budget before its development can be charged |
| 3 | `Reach(D)`  | `D` developmental law, cost-charged reachability (`Reach_Delta(M0,B_dev)`) | a budget-admissible realization must be developmentally reachable before a search can reach it (#874) |
| 4 | `Seen(B)`   | registered deterministic complete search trace, budget `B` (#877) | a reachable realization must be inside the cost-feasible search prefix to be a candidate |
| 5 | `Epis(H,U)` | registered interaction history `H` and typed uncertainty set `U.C` | evidence acts on the observer, never on the world, so it is applied last |

Nested classes and ceilings:

```text
A_0 = X
A_i = A_{i-1} ^ P_i          (i = 1..5)
c_i = max { cap_E(x) : x in A_i }   with c_i = BOTTOM when A_i = {}
```

`A_0 >= A_1 >= ... >= A_5` by construction, so `c_0 >= c_1 >= ... >= c_5` by the
CAP-2A supremum-over-superset argument (KP-2A). `BOTTOM` is below every rational.

The survivor set used by the predictor is

```text
C = X ^ Expr(M) ^ Reach(D) ^ Seen(B) ^ Epis(H,U)
```

— note `Res(R)` is **absent**: resource inadmissibility is a contract verdict, not
a candidacy verdict. Consequently `A_5 = C ^ Res(R)`.

Cuts 1-4 are **attainment** cuts: they change what is achievable in the world.
Cut 5 is an **epistemic** cut: it changes only what is identifiable by the
observer. This two-tier split is why an attainment obstruction takes priority
over an epistemic one: when `c_5 < tau` no consistent budget-admissible
realization reaches the target *in fact*, so resolving the observer's ambiguity
could not produce a target-meeting system.

## 2. The ten modes

Evaluated in this frozen priority order; the first matching clause assigns the
mode. Let `q_tau(x) = 1 if q_{E,R}(x) >= tau else 0` be the registered threshold
query (a coarser query in the exact sense of U-4A; certification is an instance of
ABSTAIN-1 on `q_tau`, not a parallel `min` shortcut).

| id | predicate | structural obstruction | parent |
|---|---|---|---|
| `FM_CANNOT_CHECK` | the capability query or the threshold is not registered, or the query is not total on `X` | no registered semantics to evaluate | U-3 / U-4, #913 |
| `FM_INCONSISTENT` | `C = {}` | registered assumptions are jointly inconsistent; no surviving world | U-3B / U-4A, #913 |
| `FM_INFORMATION_CEILING` | `c_0 < tau` | the registered admissible class itself cannot reach `tau`: impossibility region | CAP-2 / CAP-3 |
| `FM_EXPRESSIVITY` | `c_1 < tau <= c_0` | the morphology/representability constraint is the first binding cut | #848 CAP-1, #837 sec. 4 |
| `FM_RESOURCE` | `c_2 < tau <= c_1` | the lifecycle budget after the mandatory shared charge is the first binding cut | BUDGET-1 (#906) |
| `FM_REACHABILITY` | `c_3 < tau <= c_2` | target-attaining realizations exist and are affordable but are not developmentally reachable | GVR (#874) |
| `FM_SEARCH_BUDGET` | `c_4 < tau <= c_3` | reachable but outside the cost-feasible search prefix | FSB (#877) |
| `FM_OBSERVED_SHORTFALL` | `c_5 < tau <= c_4` | the registered history/uncertainty set excludes every target-attaining candidate: the prediction is a certified negative | U-2A image, CAP-2 |
| `FM_ALIASING` | `c_5 >= tau` and `q_tau[C] != {1}` | target-attaining and target-missing candidates are observationally aliased; certification is forced to abstain | CAP-3 aliasing + ABSTAIN-1 |
| `FM_NONE` | `c_5 >= tau` and `q_tau[C] = {1}` | no shortfall: the target is met by every consistent world and certified | — |

## 3. What the census must prove

- **Disjointness.** For every registered input, exactly one clause fires. The
  checker evaluates all ten predicates independently (not as an if/elif chain) and
  requires the count of true predicates to be exactly 1.
- **Exhaustiveness.** Zero inputs with no true predicate.
- **KP-2C (unique binding cut).** For every input assigned a ladder mode `i` in
  1..5, `c_{i-1} >= tau` and `c_i < tau`; for `FM_INFORMATION_CEILING`, `c_0 < tau`.
- **Non-emptiness.** Per-mode counts are reported as discovered facts. An empty
  mode is reported empty.

## 4. Declared boundary, in advance

First-crossing attribution is **order-dependent**, and this is a genuine property
of constrained systems, not a bug. Example shape: with two cuts `P,Q` where the
full conjunction is below `tau`, dropping `P` alone restores attainability, and
dropping `Q` alone does not, the prefix `{P}` may still be above `tau` so order
`(P,Q)` attributes to `Q` while order `(Q,P)` attributes to `P`. The tranche
therefore censuses all `5! = 120` orders of cuts 1-5, reports the exact number of
grid inputs whose assigned mode is order-sensitive, and ships an explicit
two-cut counterexample. The unconditional positive that survives is KP-2C: the
assigned cut is the unique one that destroys attainability *conditional on its
predecessors in the registered order*, and the registered order is justified by
the dependency column of the table in section 1.

## 5. Hostiles the taxonomy checker must DETECT

- `TAXONOMY_OVERLAP`: a variant using `<=` instead of `<` at one rung, producing an
  input in two modes.
- `TAXONOMY_GAP`: a variant with `FM_ALIASING` deleted, producing an input in none.
- `LADDER_REORDER`: a variant that applies `Epis(H,U)` before the attainment cuts,
  producing an epistemic attribution for a physical shortfall.

All three must be flagged by the same checker that reports zero overlaps and zero
gaps on the true taxonomy. Validating the checker on the true taxonomy (the
no-alarm case) is as required as the planted-positive recall.
