# Grand GMI Planning Reachability Semantics and PSR-ID Correction V1

Status: **FORMAL CORRECTION / EXACT-VS-BOUNDED REACHABILITY SPLIT + IDENTIFIER RECONCILIATION**  
Date: 2026-09-12

## 1. Atomic gap

The V1 planning tranche contains two independently checkable presentation gaps that matter for downstream theorem use even though its finite exact-terminal checker is correct on its declared microscope:

1. `PLANNING_SEMANTIC_RESOLUTION_CLAIMS_V1.md` assigns `PSR-3` to the information/computation-separation corollary, `PSR-4` to quotient planning, and `PSR-5` to the raw-history compression witness, while `PLANNING_SEMANTIC_RESOLUTION_THEOREM_V1.md` labels the quotient-planning theorem `PSR-3` and does not label the latter two claims separately.
2. The theorem correctly defines **exact-horizon terminal reachability**, but the claim/prose phrase "finite-horizon reachability" can also mean the standard **reach within at most `t` steps** objective. These two semantics are not identical unless an additional goal-stuttering/absorbing condition is supplied.

The mathematics does not need to be weakened. It needs the reachability objective to be typed explicitly and the local `PSR-*` identifiers to be reconciled.

## 2. Two distinct finite-horizon operators

Let a finite deterministic planning process have states `S`, actions `A`, transition `T:S x A -> S`, and goal predicate `G`.

Define **exact-terminal reachability**:

\[
E_0(s)=G(s),
\]

\[
E_{t+1}(s)=\bigvee_{a\in A} E_t(T(s,a)).
\]

`E_t(s)=1` means that there is an action sequence of **exactly** length `t` whose terminal state is a goal.

Define **bounded reachability**:

\[
B_0(s)=G(s),
\]

\[
B_{t+1}(s)=G(s)\vee\bigvee_{a\in A} B_t(T(s,a)).
\]

`B_t(s)=1` means that a goal is reached **within at most** `t` actions, including time zero.

These are different obligations and therefore different semantic response maps in Grand-GMI terms.

## 3. PRS-1 — exact/bounded divergence theorem

There exist finite deterministic planning systems for which `E_t` and `B_t` differ.

Canonical witness:

- states `S={g,b}`;
- one action `a`;
- goal set `{g}`;
- `T(g,a)=b` and `T(b,a)=b`.

Then

\[
E_1(g)=0,
\qquad
B_1(g)=1.
\]

So "exactly at horizon" and "within horizon" cannot be silently interchanged.

## 4. PRS-2 — quotient preservation for both semantics

Let `~` be an equivalence relation satisfying:

1. **goal respect**: `s~s' => G(s)=G(s')`;
2. **right congruence**: for every admitted action `a`, `s~s' => T(s,a)~T(s',a)`.

Let the quotient transition be

\[
\bar T([s],a)=[T(s,a)].
\]

Define `\bar E_t` and `\bar B_t` on quotient states by the same recurrences as `E_t` and `B_t`.

Then for every state `s` and finite horizon `t`,

\[
\boxed{E_t(s)=\bar E_t([s])}
\]

and

\[
\boxed{B_t(s)=\bar B_t([s]).}
\]

### Proof

For both operators the base case follows from goal respect. Right congruence makes every quotient successor independent of representative. For `E`, induction transports the disjunction over successor exact-terminal values. For `B`, the same induction applies with the additional current-state goal term, which is also preserved by goal respect. QED.

Thus the V1 quotient-planning theorem is valid for its explicitly written exact-terminal recurrence, and it extends to ordinary bounded reachability once the extra `G(s)` disjunct is added.

## 5. PRS-3 — first-action preservation

For `t>=1`, define the exact-terminal successful first-action set

\[
A^E_t(s)=\{a:E_{t-1}(T(s,a))=1\}.
\]

For bounded reachability and non-goal states `s notin G`, define

\[
A^B_t(s)=\{a:B_{t-1}(T(s,a))=1\}.
\]

If `s` is already a goal under the bounded objective, the obligation is already satisfied at time zero; a separate `STOP` convention must be registered before speaking of a required physical first action.

Under goal respect and right congruence,

\[
A^E_t(s)=A^E_t([s]),
\qquad
A^B_t(s)=A^B_t([s]).
\]

This follows immediately from PRS-2 applied to each successor class.

## 6. PRS-4 — when exact and bounded semantics coincide

If every goal state admits an action sequence that can stutter in the goal for every remaining step — in particular, if goals are absorbing under all admitted actions, or an admitted `STOP`/self-loop action is always available at goals — then any trajectory reaching a goal before the horizon can be extended to end in a goal exactly at the horizon.

Under that condition,

\[
E_t(s)=B_t(s)
\]

for every `s,t`.

Without such a condition, equivalence is not licensed.

## 7. Canonical local PSR identifier map

The claims table already fixes the intended local identifiers. This correction makes that mapping normative for the V1 planning tranche:

| ID | Canonical content |
|---|---|
| `PSR-1` | Verifier Semantic-Class Theorem: `Q*=N-max_i n_i`. |
| `PSR-2` | Plan Semantic-Resolution Law: `Q_plan=b^d-b^(d-q)`. |
| `PSR-3` | Information/computation-separation corollary: one-bit first action can require 512 verifier calls in the canonical binary depth-10 witness. |
| `PSR-4` | Semantic Quotient Planning Theorem: goal-respecting right congruence preserves the registered planning recurrence and successful first-action sets. |
| `PSR-5` | Raw-history compression witness: binary depth-12 raw histories collapse to two exact modular semantic states. |

Accordingly, the phrase `PSR-3 — Semantic Quotient Planning Theorem` in `PLANNING_SEMANTIC_RESOLUTION_THEOREM_V1.md` is a **local identifier drift**, not a change in theorem content. In cross-references after this correction, quotient planning is `PSR-4` and the raw-history witness is `PSR-5`.

The V1 theorem file is left byte-for-byte untouched on this correction branch so the frozen historical artifact remains auditable. This file is the additive correction layer.

## 8. Exact hostile verification

`grand_gmi_planning_reachability_semantics_checks_v1.py` independently enumerates finite deterministic systems with:

- `n=2` and `n=3` states;
- two actions;
- every deterministic transition table;
- every goal subset;
- every set partition of states;
- every partition that satisfies goal respect and right congruence;
- horizons `0..3`.

It verifies both exact-terminal and bounded-reachability quotient preservation, and both first-action-set preservation laws where a physical first action is meaningful.

The exhaustive corpus contains **10,086 valid quotient instances**, **241,296 value equalities**, and **90,486 first-action equalities**. It also finds **3,820 cells where exact-terminal and bounded reachability differ**, proving that the semantic distinction is load-bearing rather than cosmetic.

The checker additionally audits the V1 planning documents and requires the legacy identifier drift to be detected while this correction file supplies the complete canonical `PSR-1..5` map.

## 9. Parent subtraction

Classical planning, automata/model checking, MDP reachability, dynamic programming and bisimulation/state-abstraction theory already distinguish terminal-step objectives from bounded reachability and already prove quotient-preservation results under suitable congruence/bisimulation hypotheses.

The Grand-GMI residual here is narrower:

1. bind the reachability operator to the registered obligation before assigning `kappa`, `tau` or morphology consequences;
2. prevent an exact-terminal checker from being cited as evidence for an untyped "within horizon" claim;
3. retain the same obligation-relative quotient logic for either operator once it is declared;
4. keep the local claim identifiers auditable across theorem, claims and receipt layers.

## 10. Falsifiers

This correction is falsified at its declared finite/deterministic scope by any of the following:

1. a goal-respecting right congruence for which quotienting changes an `E_t` value;
2. a goal-respecting right congruence for which quotienting changes a `B_t` value;
3. a non-goal state for which quotienting changes an exact or bounded successful first-action set;
4. failure to reproduce the explicit two-state divergence witness;
5. a post-correction document set in which the normative `PSR-1..5` map is incomplete or contradictory.

Stochastic, partially observed, state-dependent-action, cost-bounded and continuous-time planning require their corresponding parent reachability operators and are not silently covered by this finite deterministic addendum.
