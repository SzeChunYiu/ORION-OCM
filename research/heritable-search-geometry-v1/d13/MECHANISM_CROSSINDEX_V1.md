# D13 — Mechanism-vocabulary cross-index V1 (Epistemic Atlas expansion)

Motivated by D12's universal hidden-pair miss (see `../d12/D12_SCORING_V1.md`):
all five calibration arms — including the exhaustive oracle — missed the H1
donor (metabolic economics for A_T05) because every arm's discipline partition
is keyed by FIELD NAME, and the structurally-matched donor lives in a
non-adjacent field. Calibration conclusion: remote-donor recall is
partition-limited, not effort-limited. This file is the repair: a cross-index
keyed by MECHANISM VOCABULARY, so the router can reach across partitions
without enumerating them.

## How the router uses it (D11 wiring)

`atom statement → mechanism terms (extracted from the statement's operative
verbs/nouns) → cross-index rows → candidate donor disciplines (INCLUDING
non-adjacent) → one L2 probe each (10 units) → route deep only on structural
overlap`. Probe budget share: `cross_partition_probe_share = 0.05·B_total`
(D12 constant, uncalibrated — first measurement lands with the next freeze).

## V1 index (12 mechanism terms × owner disciplines)

| id | mechanism term | owning disciplines (canonical instances) | first V1 probe target |
|---|---|---|---|
| M01 | saturation / nonlinear capacity limit | enzyme kinetics (Michaelis–Menten); congestion pricing; queueing (M/M/1/K); server saturation; toxicity dose-response | biochemical kinetics |
| M02 | channeling / localization of flow | metabolic substrate channeling; JIT supply chains; network function placement; dedicated-lane circuits | metabolic organization |
| M03 | threshold economics (build vs per-use) | metabolic enzyme investment; warehouse/facility location; cache warming vs cold fetch; tooling amortization | OR / economics |
| M04 | renewal / regenerative cycles | renewal-reward (inventory); cell turnover; garbage-collection cycles; planned replacement | OR reliability |
| M05 | depletion / non-renewable stock | optimal extraction (Hotelling); fisheries collapse; memory leak / heap exhaustion | resource economics |
| M06 | ratchet / monotone accumulation | hypervolume archives; Kelly compounding; irreversibility (hysteresis); CO2 accumulation | EC/QD |
| M07 | allocation under capacity | surrogate/successive-halving budgets; metabolic flux allocation; kidney exchange; spectrum auctions | ML theory |
| M08 | contraction / coupling of processes | Dobrushin coefficients; co-evolutionary lockstep; thermodynamic coupling; MCMC coupling | probability theory |
| M09 | neutral sets / degeneracy | Landau degeneracy; genetic code redundancy; polygonal billiards; kernel null-spaces | statphys |
| M10 | sufficiency / compression of information | Blackwell experiments; bisimulation; rate-distortion; sufficient statistics | information theory |
| M11 | local-to-global consistency | sheaf gluing; CSP consistency; lumpability; coarse-graining (renormalization) | CSP/sheaf |
| M12 | exploration necessity | bandit best-arm lower bounds; PAC-Bayes; novelty search (minimal criterion) | ML theory |

## OPEN-cell routing (coverage-matrix expansion)

Every OPEN cell in `../HSG_COVERAGE_MATRIX_V1.json` (21 open-pending cells + 2
open atoms) now carries mechanism terms + a first V1 probe target. **Cells
remain OPEN** — this is routing metadata, not evidence; no verdict changes.

### Theorem cells (11)

| cell | open question | mechanism terms | probe |
|---|---|---|---|
| A_T01/R2 | subset-infimum, stochastic dominance | M10 | information theory |
| A_T03/R2 | aliasing impossibility (aliased-state distributions) | M09 | statphys |
| A_T04/R3 | coded-search share under kernel proposals | M10 | information theory |
| A_T05/R7 | amortization identity with shared modules (2-level) | M03, M02 | OR/economics (+ metabolic-organization cross-partition row — the D12 H1 direction) |
| A_T06/R7 | locality cones spanning levels | M08, M11 | probability theory |
| A_T07/R6 | ratchet under kernel-choice eviction | M06 | EC/QD |
| A_T08/R3 | dominance order on kernel FAMILIES | M10 | information theory |
| A_T08/R4 | family dominance under metric perturbation | M10, M08 | information theory |
| A_T14/R3 | NFL kernel-averaging; Dobrushin-contractive families | M08, M12 | ML theory |
| A_T14/R4 | NFL under metric sensitivity | M08 | probability theory |
| A_T16/R5 | Blum speedup under kernel composition | M12 | ML theory |

### Concept cells (10)

| cell | open question | mechanism terms | probe |
|---|---|---|---|
| G05/R6 | ecology drift (E_t) | M04 | OR reliability |
| G05/R7 | open system: task inflow/outflow, non-conserved measures | M04, M07 | OR reliability |
| G07/R7 | verification crossing a system boundary (external channel) | M02 | metabolic organization (compartment-crossing channeling) — cross-partition row |
| G08/R6 | time-varying constitution (governed amendment process) | M06 | EC/QD |
| G08/R7 | multi-constellation levels | M11 | CSP/sheaf |
| G11/R6 | kernel evolvability drift | M12 | ML theory |
| G13/R7 | cross-level charging (inheritance economics) | M03 | OR/economics |
| G14/R7 | multi-level dependency cones | M11 | CSP/sheaf |
| G16/R7 | amortization across coupled trajectories | M03, M02 | OR/economics |
| G17/R6 | prior as moving target (Fisher/KL geometry) | M10 | information theory |

### Open atoms (2, fully unrouted)

| cell | open question | mechanism terms | probe |
|---|---|---|---|
| A_T10/all | Ev estimator at R3 (kernel Ev), R4 (metric sensitivity) | M08, M09 | probability theory (estimator stability under kernel perturbation = Dobrushin contraction) |
| A_T11/all | module promotion under uncertain future use (option value form) | M03, M05 | resource economics (real options / Hotelling-style option value) |

Note the two deliberate cross-partition probes planted by honest routing (not
by construction): G07/R7 → metabolic organization and A_T05/R7 → metabolic
organization. If the next calibration shows the router reaching those rows,
the cross-index is doing its job.

## honest scope

V1 covers the 12 terms that appeared in D10–D12 statements and receipts; it is
NOT a completed ontology — each row names one probe target, not a proof of
transfer. The H1 pair (saturation+channeling → metabolic economics) is the
existence proof that cross-partition rows are reachable this way; it was
constructed (by the curator, pre-freeze) exactly to be unreachable without an
index like this one.

## verification hook

Next calibration freeze (D15) must include: (a) a hidden pair whose donor is
ONLY reachable via this cross-index (measures `cross_partition_probe_share`),
and (b) an anti-donor INSIDE the retrieval surface (makes the false-analogy
charge testable — D12's H2 was never reached by any arm). Both requirements
are recorded in `../d12/D12_SCORING_V1.json` → `hidden_pair_outcomes`.
