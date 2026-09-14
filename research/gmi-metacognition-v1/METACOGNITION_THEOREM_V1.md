# Derived metacognition — META-1–4 (checklist item 14 / 602-I6)

Status: **THEOREM + EXACT FINITE WITNESSES. Admissibility claim** (DU-1 standing
rule: what is forced/attainable under the declared interface, not what neutral
search reaches).
Date: 2026-09-14. Scope: finite deterministic test/world/action problems with
exact nonnegative costs (the TDA-1 interface, unchanged), plus a finite
candidate-strategy register for strategy selection. Exact Fractions throughout.

Item-14 gap map: "confidence, error-likelihood and expected-cognitive-value as
*derived internal objects*" → META-1 (confidence), META-2 (error likelihood),
META-3 (expected cognitive value + continue/stop/reconsider rule); "strategy
selection among reasoning methods" (602-I6) → META-4. Calibration criterion and
the self-prediction impossibility bound are inherited (GR4 diagonal; ARC-style
exact calibration below), not re-derived. **Item 14 is POSITIVE at finite scope
on all four.**

## META-1 — confidence is the surviving-candidate success margin

For candidates `S` with adequate-action sets `Γ(w)`, define the common-action
set `C(S) = ∩_{w∈S} Γ(w)`. When `C(S)` is nonempty, acquisition stops (TDA-1)
— but *which* common action to emit, and how strongly to trust it, is still
open. Define the **confidence margin** of action `a` on `S` as

    conf(a, S) = |{w ∈ S : a ∈ Γ(w)}| / |S|.

Machine-checked properties over all 255 nonempty candidate subsets of the 8-world problem:

- exactly the actions with `conf = 1` are the TDA-1 stopping actions (`C(S)`);
- `conf` is monotone under candidate elimination: `S' ⊆ S` and `a` adequate
  on all of `S` implies `conf(a,S') = 1` (confidence never drops for a truly
  adequate action as evidence narrows the field);
- a strictly interior value (`0 < conf < 1`) is *actionable*: it identifies the
  discriminating test family whose outcome cells separate the adequate from the
  inadequate worlds (the witness names the cheapest such test by the TDA-1
  value function).

So confidence is not a researcher-side estimator (cf. the correlated-descriptor
audit, which the issue rightly does not count). It is an internal object of the
acquisition process itself: a function of the surviving candidate set, updated
by every test outcome, gating the stop rule. `conf = 1` *is* the TDA-1 stopping
condition, restated as a graded object rather than a binary gate.

## META-2 — error likelihood is the complement with a price

For emitted action `a` on surviving set `S`, the **error likelihood** is
`err(a,S) = 1 − conf(a,S)`. The content beyond the definition is the *priced*
form: with declared unit failure loss (1 per inadequate emission, uniformly),
the **expected error cost** is `EC(a,S) = 1 − conf(a,S)` exactly:

Machine-checked over all 255 nonempty subsets: EC is the uniform-mean loss of
emitting now; the max-confidence action always minimizes EC (exact duality, no
tie-breaking needed); and EC = 0 iff `a ∈ C(S)`. Uniformity is a declared
indifference premise over the surviving candidates, stated openly — not a
smuggled Bayesian prior over ecologies.

Falsifier: any candidate subset where the max-confidence action does not
minimize EC, or where EC = 0 off the common-action set (re-run the checker).

## META-3 — expected value of further cognition + the stop rule

Let `V(S)` be the TDA-1 optimal worst-case remaining test cost. For a candidate
test `x` with cost `c(x)` and outcome cells `S_xy`, define the **expected value
of cognition** for emitting `a` now vs testing `x` first:

    EVC(a,S,x) = EC(a,S) − [ c(x) + max_y EC(a,S_xy) ]   (worst-case form)
    EVC*(a,S,x) = EC(a,S) − [ c(x) + mean_y EC(a,S_xy) ] (mean form, declared indifference)

**META-3 rule.** Continue with `x` iff `EVC > 0` (worst-case) — the test's
worst branch still leaves less expected error than emitting now, net of cost.
Reconsider (switch candidate action) iff some `a'` has `EC(a',S) < EC(a,S)`.
Otherwise stop and emit.

Machine-checked: on the priced problem, the rule reproduces the TDA-1 stopping
set exactly (stop iff `C(S)` nonempty, where EC hits 0 for the common action
and no test has positive EVC since `max_y EC = 0` cannot beat `−c(x) < 0`…
with the boundary case `c(x) = 0` handled: free tests with splitting power are
always taken, matching TDA-1's deletion argument in reverse). On sets with
empty `C(S)`, the max-EVC test coincides with a TDA-1 minimizing test in all
64 nonempty subsets of the 6-world subproblem. Continue/stop/reconsider is
therefore not a heuristic layered on acquisition — it *is* the acquisition
value function with the error price made explicit.

## META-4 — strategy selection among reasoning methods

Register a finite strategy family `K = {cautious, bold, cheap_first}` with
ZERO execution fees (declared — verified during construction that any fee
above the EC gap begs the question by making bold win everywhere). Values are
worst-case totals: cautious = `V(S)` + worst-leaf min-EC via the TDA-optimal
tree; bold = min-EC now; cheap_first = t0 once then TDA-optimally.

Machine-checked measured partition over all 63 nonempty subsets: bold uniquely
best on 32 (emitting beats costly testing — itself a metacognitive verdict),
17 cautious/bold ties, 11 three-way ties, 3 bold/cheap_first ties. The
selection map is exactly computable by finite enumeration (GG-S5-style finite
specialization, no new machinery), ties listed never silently broken.

Calibration criterion (602-I6): confidence is **calibrated** iff mean adequacy
at each stated level equals that level. META-1 confidence is exactly calibrated
by construction (`conf` IS the adequacy rate over `S`). Miscalibration enters
only via candidate-universe misspecification — a distinct, named failure mode:
confidence is valid *relative to the declared candidates*.


## Claim ceiling (repeated for the registry)

Finite deterministic test/world/action scope, exact costs, declared candidate
universe, declared indifference where means are taken. No learned candidates,
no stochastic observation kernels, no infinite-horizon cognition, no claim that
neutral search reaches these objects (DU-1). The diagonal impossibility bound
(GR4) is inherited unchanged.

Files: [model](metacognition_v1.py) → [17 controls](test_metacognition_v1.py) →
[receipt](META_RECEIPT_V1.json: 17/17 on billy-old py3.14 + laptop-billy py3.8,
normal + optimized).
