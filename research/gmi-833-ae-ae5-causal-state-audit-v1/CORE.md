# gmi-833-ae-ae5-causal-state-audit-v1

Section AE5, five of six rows: a parent-ownership audit against computational
mechanics. **AE5's fifth row is closed in the same tranche by
`research/gmi-833-ae-morphology-sweep-v1` (SWEEP-6), not here** — the two
reconciliation files partition AE5 with no overlap.

**Registered scope.** Length-3 dyadic decision-tree processes: each prefix
declares a fresh fair coin or a constant. `2,187` enumerated, `2,019` registered
(the rest excluded because their causal-state masses are not exactly dyadic),
`1,527` with an exactly computable excess entropy. Every entropy is the exact
rational `Σ 2^-a · a`; **no logarithm is ever evaluated**, and a non-dyadic mass
raises rather than degrading to a float.

| result | numbers |
|---|---|
| `AE5-1` horizon scope | refinement monotone on all **2,019**; `H*` is `1` for **1,863** and `2` for **156**; the witness `F F F F F 0 0` has **1** class at horizon 1 and **2** at horizon 2, so the identification with causal states must carry its horizon |
| `AE5-2` `C_μ` and `E` | `E ≤ C_μ` on **1,527 of 1,527**; strict crypticity `C_μ = 3/2`, `E = 1/2`, `χ = 1`; that member's state masses are the **non-uniform** dyadic triple `(1/4, 1/4, 1/2)`, so `C_μ` is a real entropy and not a relabelled count |
| `AE5-3` parent ownership | **`PARENT_SUFFICIENT` on 4 of 5**, each with its DOI; `novelty_claimed_for_gmi_state_complexity: false`; one named `RESIDUAL` |
| `AE5-4` disagreement | **11 of 12** ordered pairs disagree, **6** with a strict order reversal, so all **6** unordered pairs are non-equivalent; the single determined direction is covered by the **proved** rank ≤ state-count bound, verified on all 2,019 |
| `AE5-6` finite horizon | **5** infinite-horizon assumptions listed and declared not assumed; a guard with **0** alarms here and detection of the planted claim; truncation proved to lose information (`1` class at horizon 1 versus `2` at horizon 2) |

**`PARENT_SUFFICIENT` is the success terminal here.** Four of the five audited
statements are already owned by Crutchfield & Young, Shalizi & Crutchfield,
Crutchfield & Feldman and Jaeger; saying so precisely, with citations and a
machine-readable `novelty_claimed: false`, is the deliverable. The residual is
two narrow things: the horizon-indexed refinement sequence, and the exactly
dyadic family that makes the parent bounds verifiable rather than merely cited.

**Two routes.** Route A propagates the joint forward and uses rational
Gauss–Jordan; Route B walks the tree per word, reads dyadic exponents with
`bit_length`, and uses fraction-free Bareiss elimination. The oracle earned its
keep — it caught a slot-ordering discrepancy before any result was recorded.

**Hostiles.** Five, each proved potent before proved detected.

**Null.** `E ≤ C_μ` raises `0` alarms on the true family and is satisfied by
`0 of 200` shuffled assignments.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae5-causal-state-audit-v1/test_ae5_causal_state_audit_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae5-causal-state-audit-v1/test_ae5_causal_state_audit_v1.py -v
python3 -I -B research/gmi-833-ae-ae5-causal-state-audit-v1/ae5_causal_state_audit_v1.py > /tmp/ae5.json
cmp /tmp/ae5.json research/gmi-833-ae-ae5-causal-state-audit-v1/RESULT_V1.json
```
