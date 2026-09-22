# Named results — K05 (Symbolic logic systems.) closure in `gmi-833-family-derivation-symbolic-ssm-retrieval-v1`

Every result below is stated at the scope registered by
`FREEZE_V1_SLICE_ADDENDUM_K05_V1.md` (the amended recovery-resource protocol)
and at no other scope. No result here is composed with any certificate of any
other package; `FGS-2` forbids it and `CROSS_SCOPE_GATE_COMPOSITION` is in the
forbidden promotions of the reconciliation document.

Scope: row `Symbolic logic systems.`; the frozen `B_CONTR` battery (17,424
tasks, sha256 `5b385f0edfa0…`, complete enumeration of contraction-reachability
decisions over the 22-term universe with all 36 nonempty rule subsets of size
<= 2 of the 8 constant contractions); the frozen `M_ITER(18, 16)` model and
basis of `machinery_v1.py`; the amended recovery envelope (work <= 14, every
expression <= 320 nodes, total <= 32 cells, cost <= 540, steps <= 16).

---

## `K05-R1` — full B_CONTR contraction-reachability decision at the amended resource scope

**Statement.** The hand-built machine `k05_v5_work/k05_v5_result_v1.json`
(`M_ITER`, 18 input cells, 14 work cells, output cell 31, steps 16, rho 1,
cost 536) decides **every** one of the 17,424 frozen `B_CONTR` tasks:
0 / 1,176 positive errors, 0 false positives, 0 illegal runs (all 17,424 legal).
It realizes y = 1 iff the goal is reachable from t0 under the union over the
(<= 2) rules of each rule's per-rule transitive closure — NOT over cross-rule
alternating chains (56 tasks with alternating-rule 2-step paths have y = 0; the
census two-step chains are all `[0,0]` / `[1,1]`; the 64 two-step positives are
exactly the same-rule chains). Verification is three-way: the package evaluator
`posthoc_adjudicate_v1.run_iter` (82.7 s), the coordinator re-run
`k05_v5_work/verify_coord_v1.py` (identical counts), and a second independent
evaluator `k05_v5_work/k05_v5_verify_independent_v1.py` which imports none of
the construction or adjudication code, re-simulates the machine from its JSON
and re-derives the battery predicate from `battery_generate_v1.py` alone, and
reports `matches_receipt: true`. The K05 fingerprint clauses hold as real
interventions (`k05_v5_work/k05_v5_clauses_v1.json`): C1 compositional discrete
structure in cell state (token-equality / shape bits on a recorded trace); C2
rule-based contraction rewrites detected (one `3R->2` and one same-rule
two-step chain execute and fire the detectors); C3 control among more than one
legal successor (all 20 `(t0, ruleset)` pairs with >= 2 distinct one-step
successors fire).

**Quantifiers.** This battery, this machine model, this amended resource scope
only. Nothing is claimed about any other symbolic-logic ecology, grammar, or
resource envelope; in particular the in-protocol envelope remains bounded at
the reflexive witness (`K05-B1`).

**Assumptions.** The `B_CONTR` battery is byte-frozen at the registered sha256
(asserted at load by the construction script); the `M_ITER(18,16)` model, the
frozen basis `{ADD, NEG, GE_c}` and guard `D = [-3,3]` of `machinery_v1.py`;
the amended envelope of `FREEZE_V1_SLICE_ADDENDUM_K05_V1.md`; the battery's y
is the union over rules of each rule's per-rule `reachable_set` closure (the
generator's own semantics).

**Dependencies.** `k05_v5_work/k05_construct_v1.py` (construction),
`k05_v5_work/k05_v5_result_v1.json` (machine + verified counts),
`k05_v5_work/k05_v5_run.log` (run log), `k05_v5_work/verify_coord_v1.py` and
`k05_v5_work/k05_v5_verify_independent_v1.py` (+ `.json`, independent
re-verification), `k05_v5_work/k05_v5_clauses_v1.py` (+ `.json`, clause
interventions), `battery_generate_v1.py`, `posthoc_adjudicate_v1.py`,
`machinery_v1.py`, `NEUTRAL_BATTERY_FREEZE_V1.json`.

**Falsifiers.** A positive task on which the machine outputs 0, or a negative
task on which it outputs 1, over the 17,424-task battery; an illegal run; a
clause C1-C3 failing its intervention; an independent evaluator that
disagrees with the committed receipt.

**Strongest parents.** The K05 reflexive constructive witness
(`REVIVAL_V2.json`, in-protocol, 384 / 1,176, cost 54) whose per-position
equality structure the machine extends; the K08 readout-repair closure
(revival v3, same package) as the recovery-mechanism precedent; the FDT
package's `PRIOR_DISCLOSURE_V1.md` fingerprint clauses and battery
construction; `gmi-833-blind-recovery-v2-v1` for the blindness protocol.

---

## `K05-B1` — the in-protocol resource boundary (reflexive-only optimum)

**Statement.** Under the original frozen protocol (work <= 6, every expression
<= 40 nodes, total <= 24 cells, steps <= 16), full recovery is structurally
impossible and the strongest decision machine is the reflexive witness
(6 work cells, cost 54): 792 / 1,176 positives caught, 384 / 1,176 errors,
0 false positives. The proof (`K05_LOWER_BOUND_V1.md`) is a counting argument:
a correct decision needs >= 19 distinct atomic equality bits simultaneously in
the output's dependency cone (5 reflexive token-equalities + 4 t0-shape tests +
per-slot g-leaf / inner / inner-left tests); a work cell presents at most two
{0,1} bits under guard 3 and a packed cell cannot expose a shared bit
individually; the layout is time-invariant so the 16 steps add no predicates;
and the inlined node floor (~285-390) exceeds 6 x 40 = 240. The v5 build is the
empirical confirmation (36 distinct equality subtrees, 14 work cells, 522
operator nodes). This boundary is measured and earned-by-measurement, not
assumed.

**Quantifiers.** The original frozen envelope only. Under the amended envelope
(`K05-R1`) full recovery holds.

**Assumptions.** Same frozen substrate as `K05-R1`; the `TR1_K05`
within-frozen-bounds check of `revival_verify_v2.py` (work <= 24 - 18 = 6,
`max(expr_size) <= 40`).

**Dependencies.** `K05_LOWER_BOUND_V1.md`; `REVIVAL_V2.json` (the reflexive
witness machine and its counts); `k05_census_v3.json` (the 792 / 320 / 64
positive decomposition).

**Falsifiers.** An in-protocol machine with strictly fewer than 384 errors on
the full battery (a counterexample would shrink the boundary); a proof gap in
the counting argument.

**Strongest parents.** The K05 reflexive witness and its census characterization
(`k05_census_v3.json`); the FDT package's registered resource-bound discipline
(`PRIOR_DISCLOSURE_V1.md` CH2 cell-cap derivation); the K08 within-bounds
closure as the contrast case where recovery DID fit the envelope.
