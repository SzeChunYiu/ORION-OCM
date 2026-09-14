# Derived-component lesion matrix — L5 (checklist item 29)

Status: **THEOREM + EXACT FINITE WITNESSES. Admissibility claim.**
Date: 2026-09-14. Scope: finite deterministic tasks over the 6-world fixture
plus six task families that isolate the derived mechanisms. Lesions remove the
*mechanism* of one derived component while keeping the search basis
(`B_exec/B_dev`, `query_i/teach1_i`, `t0/t1`) intact.

## What "lesion" means here

Prior lesion work ablates basis elements (removes a primitive). This unit
ablates *derived* components: memory retention, attention routing,
planning lookahead, causal adjustment, social opponent modelling, and
consolidation replay. Each lesion is a surgical restriction on which
information or transformation the agent may use, not a deletion of `delta`
or `F`.

## Six lesions (one per derived component)

| lesion | mechanism removed | surgical restriction |
|---|---|---|
| `L_mem` | persistent retention | agent state is reset to `S0` before each task step (no carry-over) |
| `L_att` | conditional routing (GG55) | routing is fixed to `x0` (ignore `q`) |
| `L_plan` | planning simulation | lookahead depth `0` (act on immediate `EC` only, no `EVC` expansion) |
| `L_causal` | causal adjustment (CAU-3) | adjustment set forced empty (observe `P(Y|X)` not `P(Y|do X)`) |
| `L_social` | opponent modelling (TOM-1) | opponent state hidden (act as if fixed policy, ignore opponent `q`) |
| `L_consol` | consolidation replay | offline replay disabled (no `M*_t` saving, pay `t` not `t - ceil(log2 N_t)`) |

Basis-ablation control: `L_basis` removes one test (`t1`) — a different
deficit pattern, proving double dissociation vs the derived lesions (see
below). No lesion removes `delta` or the world set.

## Task families (measured, not stipulated)

Six tasks, each 0/1 scored, average over the registered world/task sample:

```
T_mem    — delayed reproduction (GG54): m=3 alternatives after delay
T_att    — conditional routing (GG55): (x0,x1,q) -> x_q  (8 worlds)
T_plan   — 2-step goal requiring lookahead depth >=1
T_causal — W4a/W4b gap: distinguish P(Y|X) from P(Y|do X)
T_social — TOM-1 copycat vs contrarian: need opponent type
T_consol — 2-episode retention needing M*_t joint states
```

Success under no lesion is 1 on each family (verified by the checker).
Under lesion `L_x`, success on `T_x` drops while at least one other task
remains at 1 — the dissociation signal.

## Double dissociation (exact table)

Machine-checked over the registered families:

| lesion | T_mem | T_att | T_plan | T_causal | T_social | T_consol | note |
|---|---|---|---|---|---|---|---|
| none   | 1 | 1 | 1 | 1 | 1 | 1 | intact |
| `L_mem`   | 0 | 1 | 1 | 1 | 1 | 0 | memory/consolidation coupling (shared retention) |
| `L_att`   | 1 | 0 | 1 | 1 | 0 | 1 | attention/social coupling (both need conditional routing) |
| `L_plan`  | 1 | 1 | 0 | 1 | 1 | 1 | planning isolated |
| `L_causal`| 1 | 1 | 1 | 0 | 1 | 1 | causal isolated |
| `L_social`| 1 | 1 | 1 | 1 | 0 | 1 | social isolated |
| `L_consol`| 1 | 1 | 1 | 1 | 1 | 0 | consolidation isolated (narrower than L_mem) |
| `L_basis` | 1 | 1 | 0 | 1 | 1 | 1 | basis control: planning deficit via different mechanism (missing t1) |

Predicted dissociations (each pair demonstrates that two components are
not the same thing):

- `L_mem` hurts `T_mem` but not `T_att`; `L_att` hurts `T_att` but not `T_mem`.
- `L_plan` hurts `T_plan` but not `T_causal`; `L_causal` hurts `T_causal` but not `T_plan`.
- `L_social` hurts `T_social` but not `T_plan`; `L_plan` hurts `T_plan` but not `T_social`.
- `L_consol` hurts `T_consol` but not `T_mem`-single-step (memory single-step stays 1 — the dissociation is `L_mem` kills both, `L_consol` kills only consolidation). Basis control `L_basis` mimics `L_plan`'s profile via a different cut — proving the deficit pattern alone does not identify the mechanism.

No lesion is claimed to be a brain lesion or clinical prediction.

## K/V6 probe reading (second use of same matrix)

The same six deficits are the "predict-then-verify" footprint of a derived
component set: a held-out system that recovers a lesion's missing capability
must supply the mechanism that lesion removed (up to behavioural
equivalence). This is a protocol obligation for any future K/V6 unseen-form
recovery claim, not a discovery itself.

## Claim ceiling

Finite task families, declared scoring, deterministic lesions, admissible
scope only. No claim to model neuropsychological double dissociation or
that basis-ablation patterns are unique. Falsifier: any lesion row whose
0/1 entry mismatches the checker on re-run, or any claimed dissociation
pair that fails on the registered families.

Files: [model](derived_lesion_v1.py) -> [controls](test_derived_lesion_v1.py) ->
[receipt](LESION_RECEIPT_V1.json: on billy-old py3.14 + laptop-billy py3.8,
normal + optimized).
