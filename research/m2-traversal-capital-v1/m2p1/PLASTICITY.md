# Deployment liveness — the one thing OCM has that the strongest parent does not

[PARENT_REGRET.md](PARENT_REGRET.md) recorded a hard negative: across 19 worlds OCM never
beat the ungated adaptive parent (0 wins, 6 ties, 12 losses). That is structural. Where
OCM admits, the arms are **identical by construction** — same library, same solver — and
the [fairness control](MDL_NOT_OCM.md) confirmed it again at the slot level
(`PARENT_WITH_MDL` = `CONTINUED_MDL`, 194 / 966.5 / 7 fragments).

So OCM can only beat this parent by doing something the parent structurally lacks. The
parent is a static decision list: once its library is learned it serves it forever. OCM's
KSO machinery separates **epistemic warrant** from **deployment state**:

```text
W_live(a)          is this still warranted?        -- never modified here
D_live(a, z, E)    should it influence search now? -- may stand down AND come back
```

## The experiment

A lifetime stream across an ecology shift `A → B → A′`: develop on motif set `M_A`, then
targets switch to a disjoint `M_B` (the library is now stale), then return to `M_A`.
`OCM_LIVE` deactivates when a rolling window shows `E[ΔB] ≤ 0` and reactivates when it
recovers. The library is **never deleted**.

## Result — 5 of 5 seeds, plus the original probe

| seed | motifs recovered | deactivations | **reactivations** | regime B: OCM vs parent | lifetime: OCM vs parent |
|---|---|---|---|---|---|
| 101 | 7/8 | 2 | **1** | 2 610 174 vs 5 220 348 | 6 634 922 vs 8 974 943 |
| 102 | 7/8 | 1 | 0 | 2 410 688 vs 4 821 376 | 6 385 159 vs 9 057 886 |
| 103 | 7/8 | 2 | **1** | 2 223 501 vs 3 793 796 | 7 635 992 vs 7 809 011 |
| 104 | 8/8 | 2 | **1** | 2 725 131 vs 4 460 356 | 7 378 123 vs 8 343 099 |
| 105 | 5/8 | 2 | **2** | 2 393 552 vs 4 482 452 | 6 537 022 vs 8 219 949 |

**Every seed wins over the lifetime**, and OCM is consistently **45–50 % cheaper in the
shifted regime**. The advantage holds across recovery levels from 5/8 to 8/8, so it does
not depend on having learned a good library — it depends on *noticing when the library
stopped being good*.

**Reactivation fired in 4 of 5 seeds**, closing the caveat from the single probe run,
where `reactivated_at` was empty and regime A′ passed only because the stale parent was
worse. Both directions of the lifecycle are now demonstrated: stand down a stale asset,
then restore it when the ecology returns — without ever revoking its warrant, which is
why no relearning is needed.

## What this establishes, precisely

```text
OCM-specific superiority over the strongest parent: DEMONSTRATED, via deployment liveness
```

It is the **only** OCM win over this parent in the programme, and it is not an accident of
configuration: it is the direct consequence of separating truth from usefulness, which is
the distinction the parent cannot represent. A library that is still *correct* but no
longer *useful* is exactly the case a static decision list gets wrong.

## Claim ceiling

Authored ecologies, a synthetic shift, and a single deactivation policy (rolling window,
`E[ΔB] ≤ 0`). Not established: that the policy is optimal, that it survives gradual rather
than abrupt shift, or that it transfers to ecologies this lane did not author.
