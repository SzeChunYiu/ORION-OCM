# Prospective capability perturbations — formalization V1

Issue #784; parent #602 V4. Freeze authority: commit `0fbd39d4e4848cd18d56552725e6c87412d041bf`.

This successor is deliberately narrower than the pre-existing perturbation calculus in this directory. The earlier calculus owns the signed-margin mechanics and finite abstention calibration; this artifact adds only freeze-first held perturbations against the pinned F4 predictor.

## PERT-P1 — independent capability oracle

For an integer margin vector

```text
m = (m_mem, m_plan, m_comm, m_route, m_verify),
```

define

```text
memory_exact        = 1[m_mem >= 0]
planning_exact      = 1[m_mem >= 0 and m_plan >= 0]
coordination_exact  = 1[m_comm >= 0]
verified_tool_exact = 1[m_route >= 0 and m_verify >= 0].
```

The held scorer implements these equations independently. It must not call the pinned predictor's `capability_oracle` helper.

## PERT-P2 — monotone-envelope determinacy boundary

The pinned predictor is fit on the full development cube `{-1,0,1}^5`. For target `t`, it returns 1 if a positive development point lies coordinate-wise below the query, 0 if a negative development point lies coordinate-wise above the query, and `CANNOT_IDENTIFY` otherwise.

For the three frozen main post points:

```text
A_post=(-2,0,0,0,0) -> (0,0,C,C)
R_post=(0,0,0,-2,0) -> (C,C,C,0)
D_post=(0,0,-2,0,0) -> (C,C,0,C)
```

The directly affected targets have negative development witnesses above the held point and are therefore determinately 0. For the unrelated targets, the `-2` coordinate lies below the development cube, so no positive development witness can lie below the held point; the corresponding negative target condition also cannot provide an above witness at the unchanged zero coordinate. The correct registered output is therefore abstention.

At the positive `+2/+3` controls, `(0,0,0,0,0)` is a positive development witness below the query for all four targets, so every prediction is determinately 1.

This is selective prediction, not a claim that all out-of-cube points are identifiable.

## PERT-P3 — exact transformation laws

### Ablation

Only `memory_margin` changes. Main: `2 -> -2`; safe control: `3 -> 2`.

### Resource repricing

With frozen routing budget `B=5`, demand `d=1`, and price `p`,

```text
routing_margin = B - p*d.
```

Thus `p:3->7` gives `+2->-2`, while safe `p:2->3` gives `+3->+2`.

### Environmental drift

With frozen communication shock `s`,

```text
communication_margin_after = communication_margin_before - s.
```

Thus `+2-4=-2` for the main pair and `+3-1=+2` for the safe pair.

The executable reconstructs these relations from the frozen registration rather than accepting the post points by assertion.

## PERT-P4 — direct-deficit sets

For each pre/post pair define

```text
D = {t : oracle_pre(t)=1 and oracle_post(t)=0}.
```

The frozen exact sets are

```text
ablation_main  -> {memory_exact, planning_exact}
repricing_main -> {verified_tool_exact}
drift_main     -> {coordination_exact}
```

and each safe control has `D=empty`.

A predictor cell counts as correct only when it is determinate and equals the independent oracle. `CANNOT_IDENTIFY` cells are reported separately and never counted as successes.

## Evidence classes and falsifiers

- PERT-P1/P3/P4: P1 finite definitions/algebra.
- PERT-P2: P1 consequence of the frozen monotone-envelope rule and full development cube.
- Scoring the 12 held points, predictor-blob verification and mutation hostiles: P2 exact computation.

The claim is falsified if the predictor blob differs from the frozen SHA; any frozen transformation or expected vector changes after activation; a main post point is substituted inside the development grid; a determinate cell disagrees with the independent oracle; a frozen abstention does not occur exactly; safe controls change; or normal and optimized receipts differ.

Strongest allowed terminal:

`PROSPECTIVE_CAPABILITY_PERTURBATIONS_VALIDATED_AT_REGISTERED_SYNTHETIC_SCOPE`

Forbidden: universal capability prediction, real-world perturbation calibration, causal identification outside the registered oracle, universal G6, or complete GMI.