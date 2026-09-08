# SYNTHESIS_V1 — parent absorption and the phase boundary

**GENERATED FILE — edit `synthesis.py`, then run `python synthesis.py`.**

> An acquired structure beats deriving on demand only in the JOINT regime rho AND beta AND phi: the structure is demanded again, the resource it economizes is scarce, and evidence about it composes across episodes. Outside that regime the parent wins by arithmetic and not by being cleverer, which is why seven PARENT_SUFFICIENT terminals in this lane say more about the worlds than about the machine.

**Status.** CONJECTURE, FITTED POST HOC. The rule was written after all ten rows above were known and it reproduces all ten, which is worth exactly nothing on its own -- a rule fitted to ten points that explains ten points has been fitted, not tested. One row (DEV-1 at 256 bits) requires the interval reading of beta and would score the other way under a threshold reading, and it is marked. The law becomes evidence only if the frozen out-of-sample prediction below survives.

## Absorption register

| parent | verdict | receipt | novelty removed |
|---|---|---|---|
| Belady (1966) optimal replacement | `ADOPT` | `results/RETAIN_E10_V1.json` | Any claim that OCM's retention policy is a good cache. It is not the policy that pays; a clairvoyant policy is available and was used. |
| de Kleer (1986) ATMS; Reiter (1987) minimal hitting sets | `ADOPT` | `results/SUPPORT_E6_V1.json, results/DEPEND_E3_V1.json` | Any claim that support-family discovery is new. It is 1986 work. |
| DreamCoder and Stitch | `ADAPT` | `results/LIBDISC_E5_V1.json` | Any claim that OCM discovers reusable abstractions others miss. |
| ordinary least squares over a monomial basis, degree-escalating | `GENERALIZE` | `results/INDEP_E8_V1.json` | Any claim that learned causal factorization needs a transform representation, and any reading of the earlier PARENT_SUFFICIENT as vacuous -- with an independent parent it became informative and adverse. |
| lookup classifier over evidence vectors; naive Bayes over per-probe likelihoods | `GENERALIZE` | `results/PROBESEM_E11_V1.json` | Any claim that OCM diagnoses better because it represents semantics. |
| lazy re-derivation (retain nothing, recompute on demand) | `GENERALIZE` | `results/DEPEND_E3_V1.json, results/SUPPORT_E6_V1.json, results/RHO_E7_V1.json` | Any claim that those four negatives were about OCM's architecture. |
| curriculum and transfer learning; catastrophic forgetting | `OPEN` | `../developmental-spine/... DEV1_D0_TO_D1_V1.json` | Any claim that developmental carry-over is a new phenomenon. |

Not one parent in this lane is classified REJECT, because not one of them lost. Under the old reading that was seven defeats; under the doctrine it is an absorption backlog, and the backlog has a shape, which is the next section.

## The three coordinates

### `rho` — demand

Is the acquired structure required again?

**Isolated by.** E7 (results/RHO_E7_V1.json), which sweeps reuse-opportunity density and holds mechanism, parents, budgets, checker and horizon fixed

**When absent.** every negative in the programme; the density-zero row is the anti-rigging control and it reproduces them

**Measured as.** fraction of tasks whose minimal solution cost strictly increases when the acquired structure is removed -- certified, not assumed

### `beta` — scarcity of the economized resource

Is the resource that holding this structure saves actually scarce?

**Isolated by.** E10 (results/RETAIN_E10_V1.json) for storage bits, E11 (results/PROBESEM_E11_V1.json) for labelled cases

**When absent.** lazy re-derivation wins by a theorem rather than by a policy; this is the coordinate no experiment before E10 had ever varied

**Measured as.** whether the resource is bounded or priced. NOT a threshold: DEV-1 shows an upper edge too, where the store is so tight that carried structure cannot be displaced by what the next stage needs and the lineage loses

### `phi` — factorisation of the index

Does evidence about the acquired object compose across episodes?

**Isolated by.** E11, directly (a semantics cell against a row keyed by an outcome vector); E8, incidentally (a full transform against degree-escalating least squares)

**When absent.** each episode's evidence is usable only on episodes that match it exactly, so acquisition costs more than it returns

**Measured as.** whether one episode's evidence updates a per-object cell or a per-configuration row

## In sample (all of it)

| study | rho | beta | phi | predicted | observed | agrees |
|---|---|---|---|---|---|---|
| E1 supplied-key lookup | 0 | 0 | 1 | PARENT_SUFFICIENT | PARENT_SUFFICIENT | yes |
| E3 eager dependency | 1 | 0 | 1 | PARENT_SUFFICIENT | PARENT_SUFFICIENT | yes |
| E6 support families | 1 | 0 | 1 | PARENT_SUFFICIENT | PARENT_SUFFICIENT | yes |
| E7 rho sweep | 1 | 0 | 1 | PARENT_SUFFICIENT | PARENT_SUFFICIENT | yes |
| E5 library discovery | 1 | 0 | 1 | PARENT_SUFFICIENT | PARENT_SUFFICIENT | yes |
| E8 independent factorization | 1 | 0 | 0 | PARENT_SUFFICIENT | PARENT_SUFFICIENT | yes |
| E10 bounded retention | 1 | 1 | 1 | MACHINE | MACHINE | yes |
| E11 learned probe semantics | 1 | 1 | 1 | MACHINE | MACHINE | yes |
| DEV-1 D0 to D1, 1024 bits | 1 | 1 | 1 | MACHINE | MACHINE | yes |
| DEV-1 D0 to D1, 256 bits | 1 | 0 | 1 | PARENT_SUFFICIENT | PARENT_SUFFICIENT | yes |

The rule was written knowing all of these rows. Agreement of 10/10 is a statement about the rule's construction, not about the world.

## The frozen out-of-sample prediction

### PERISHABLE_EVIDENCE

**Why this one.** It is the half of the deep root's falsifier that is still unrun, and the three coordinates assign it a sign that is NOT the sign the rest of this lane would lead anyone to guess.

**Design.** E10's world, with one change: derived evidence PERISHES. An answer derived at step t can be re-derived later only at a cost rising with elapsed time, so postponing is no longer free. Retention budget is left UNBOUNDED and generously large -- beta is deliberately switched OFF as a storage constraint -- and rho and phi are held at E10's values.

**Coordinates.** {'rho': True, 'beta': True, 'phi': True}

**Why beta is TRUE here.** beta is TRUE even though the store is unbounded, because beta is scarcity of the resource the structure economizes, and here that resource is the OPPORTUNITY to derive cheaply, which perishes. This is the load-bearing move: if beta only ever meant 'bits are capped' then the law is a statement about caches. If it means 'the economized resource is scarce' then perishability must switch it on, and the prediction below follows without any further choice.

**Predicted.** `MACHINE`

**What refutes the law.** PARENT_SUFFICIENT in the perishable world. That would show beta is specifically about bounded storage rather than about scarcity of the economized resource, the three coordinates would not be the right three, and the law would be a caching result with an inflated name.

**What confirms it, and how weakly.** MACHINE in the perishable world confirms the generalized reading of beta on ONE further point. That is one out-of-sample point, not a validated law, and the receipt must say so in those words.

**Commitment.** `4789eeb30c5e464e542dea1daca221ed034c871b773a74f6dc8312332c88d943`

## Outcome

**Verdict.** `SURVIVED_ONE_TEST` — `results/PERISH_E12_V1.json`

The crossover extension at which a rule beats a memoizer falls from 16 to 8 as the perishability ramp rises, so acquisition pays at strictly lower compressibility once the opportunity to derive cheaply perishes. beta therefore does generalize beyond bounded storage, which is what the prediction was for.

**The correction it forced.** The prediction's justification contained an error and E12's pilot found it. This module argued that with storage free and unbounded, keeping everything you derive is the folklore-optimal policy. That is false. Compression reduces the number of DERIVATIONS, not merely the number of bits, so at a large enough extension a rule wins whether or not derivation perishes -- and the pilot duly produced a confirmation that was an artifact of compression with perishability doing nothing at all. The corrected experiment sweeps extension, checks the lam = 0 row against an arithmetic break-even computed from the cost constants alone, and reports the SHIFT of the boundary rather than a win. Both the wrong argument and the confirmation it would have bought are on the record.

**How much this is worth.** One out-of-sample point. The law now has one prediction it could have failed and did not, which moves it from a rule fitted to ten rows to a rule with one surviving prediction, and no further. Two of its three coordinates have still never been varied outside the experiments that defined them.

**Adverse finding in the same run.** E12 also ran the unrun half of the deep root's falsifier and it went AGAINST the machine. eager_all_rules_parent -- which acquires every rule before seeing any demand, and lost in E3, E6, E7 and E10 -- beats the demand-triggered arm wherever the ramp is steep, because it buys every derivation at the cheapest price the world will ever offer. The demand trigger this programme identified as the missing ingredient is itself a cost once waiting is charged. It is recorded here because it is the finding a lane reporting its own surviving prediction would be most tempted to leave in the receipt and out of the summary.

**Status now.** CONJECTURE WITH ONE SURVIVING OUT-OF-SAMPLE PREDICTION. The frozen LAW_STATUS above is left exactly as written, because it is inside the commitment digest and editing it would rewrite the prediction after seeing the result. What changed is only this: the prediction was run and did not fail. That is one point. It is not a validated law, the in-sample agreement is still worth nothing, and the run that confirmed the prediction also refuted the argument that motivated it.

## What this does not establish

Three binary coordinates over ten synthetic rows. Nothing here measures a real task ecology, none of the coordinates is measured continuously, and the beta interval rests on a single pair of budgets in one experiment. The law is falsifiable, which is its only current virtue.
