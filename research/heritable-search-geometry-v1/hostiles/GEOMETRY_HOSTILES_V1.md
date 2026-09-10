# HSG lane F hostiles V1 (R4/R5)

One minimal counterexample per LIFT_FAILS verdict (freeze rule: every LIFT_FAILS ships a
minimal counterexample here, machine-witnessed where enumerable). Witnesses are EMITTED
by `../exact/geometry_dynamics_check_v1.py` on billy-laptop (exact-Fraction arithmetic
where the object is finite); this file states the construction, the JSON certifies it.

| id | row | rung | fails-claim | witness JSON | mechanism |
|---|---|---|---|---|---|
| H1 | G10 | R4 | Σ↦B(Σ,τ) Lipschitz under edit-class metrics | hostile_burden_lipschitz.json | admissibility discontinuity: 1 edit, burden N·p vs p |
| H2 | A_T01 | R4 | d_H(A,A')≈0 preserves subset-infimum | hostile_approx_sets.json | same discontinuity read on sets: ε-Hausdorff, inf drops |
| H3 | G14/A_T06 | R4 | metric-ball locality ≈ cone locality | hostile_cone_ball.json | balls symmetric+nested, Desc asymmetric; both error directions: over_recompute B, under_invalidate A |
| H4 | G15/A_T07 | R4 | HV ratchet under capacity | hostile_hypervolume_capacity.json | capacity-1 archive, scalarization eviction keeps (3,0.5), HV 4→9/6 |
| H5 | G12/A_T02 | R5 | set-reach expansion ⇒ metric-reach expansion | hostile_reach_iff.json | aliasing pseudometric d(s1,s2)=0: new state inside d-closure |

## H1 — burden Lipschitz (G10 R4, LIFT_FAILS)

𝓢 = archives {a} vs {a'}; edit metric d = 1; B(Σ,τ) = horizon price N·p (a never
admitted) vs p (a' admitted first draw). Ratio N−1 unbounded in N ⇒ no Lipschitz constant.
Restoration: only the burden-pseudetric d_B = |ΔB| (conditional row).

## H2 — approximate sets (A_T01 R4, LIFT_FAILS)

A = {a}, A' = A ∪ {a'}, edit distance 1 (rescale the metric for any ε > 0 — metric is a
registered parameter); inf_A C = N·p, inf_{A'} C = p. Repair condition: C must be
L-Lipschitz, which H1 shows program costs are not.

## H3 — cone vs ball (G14 R4, LIFT_FAILS; load-bearing)

DAG {S→A}, B isolated; d(A,B)=1, d(S,A)=d(S,B)=2. Intervention on S: affected = {A} =
Desc(S) exactly (T06 cone locality holds); ball B_d(S,2) = {A,B} ⊃ Desc(S) ⇒
over_recompute on B. Mirror (witness case2): edges {S→A, S→B} both kept, d(S,B)=2,
d(S,A)=3: affected = {A,B}, and ball B_d(S,2) = {B} misses affected A (any ball of
radius r<3 misses A) ⇒ under_invalidate. No metric repairs both (balls symmetric & nested in r;
Desc is neither). Operational reading: cache-skip by proximity is unsound in both
directions; only the cone licence (lane A iff) is sound.

## H4 — hypervolume capacity (G15/A_T07 R4, LIFT_FAILS for the capacity-removed pass)

2-D max objectives, ref (0,0), capacity 1. A_t = {(2,2)}: HV = 4. Arrival x = (3, 1/2):
scalarization w = (2, 1) scores: (2,2) → 6; (3,1/2) → 13/2 — eviction keeps
x, A_{t+1} = {(3,1/2)}: HV = 3/2 < 4. Order-ratchet intact (13/2 > 6); HV
falls: ratchet-in-order ≠ ratchet-in-HV once capacity binds.

## H5 — reach iff (G12/A_T02 R5, LIFT_FAILS)

𝓢 = {s0,s1,s2}; O: s0↦s1; p: s1↦s2 admissible within B. d(s0,s1)=1, d(s1,s2)=0
(aliasing pseudometric), d(s0,s2)=1. Set reach {s0,s1} ⊊ {s0,s1,s2}; d-diameter stays 1;
s2 ∈ d-closure of {s1}: every metric functional of reach unchanged. Repair: metric reach
expands iff new state outside the d-closure of the old reachable set.

Supporting (non-hostile) witnesses emitted by the same checker:
`witness_dobrushin_composition.json` (δ(K)≤δ(Q), submultiplicativity, δ=1 degenerate
case), `witness_ergodic_decomposition.json` (A_T12 finite specialization),
`witness_renewal_reward.json` (A_T05 identity + non-regenerative deviation),
`witness_aliasing_metric.json` (A_T03 fibre-constancy),
`witness_info_geometry.json` (G03/G17 sup-KL family shrink vs metric re-description).
