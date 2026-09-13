# Reachability scope of family verdicts — what the occupant sets and the packet verdicts actually claim

Date: 2026-09-13. Cross-lane note. Reads `DEVELOPMENTAL_UNDERDETERMINATION_THEOREM_V1.md`
(PR #539, grand-unification lane) against this lane's `RV-377-113` occupant scan, the
`RV-377-180` B6 arms, and the `RV-377-210` NN/non-NN packet. It adds no experiment and
adjudicates nothing. It fixes what three existing objects are statements *about*.

## 1. The occupant sets are law-dependent, not static

`GMI_RV_377_113_INTERVENTION_SCAN.json` is the source of every "registered occupant set" in
this lane, including `E_smooth3 → (KVSTORE, PROGRAM, TABLE)`. Its freeze says what it did:
extract the **recovered** genotype from a search receipt and score it under all six registered
interventions, because `b1.main` scores under `standard` only and rule 36 forbids calling a
single-intervention number admissible.

So an occupant set is *"which carriers had a machine, recovered by the scanned search, that
survives all six interventions."* It is not a statement about the admitted set. "DENSE is not
an occupant of `E_smooth3`" therefore means **no coefficient machine that search recovered there
was admissible** — a statement about a development law, not about what exists.

(The three occupant entries carry byte-identical numbers — `std` 0.8958, `min` 0.8594,
`fx_vs_const` 1.126 — which is not a defect: the archive's best cells in those carriers are
minor variants of one design differing in a single node kind, and the same triple coincidence
reappears independently in `SAME|RESET|S0`'s `final_best_by_carrier`.)

## 2. The other lane proved this cannot be repaired by more work

`DU-1` exhibits two development laws sharing the admitted realization set, the profile map, the
family assignment and every proved necessity, yet yielding different reachable frontiers and
different family verdicts. The reachable frontier is **not a function** of the static data, so no
theorem of the form "necessities imply the trained outcome" can exist. `DU-2` adds that the
admitted *update set* does not determine reachability either — the schedule does — so registering
a set of operations is not registering a development law.

The `RV-377-180` arms are an empirical instance of exactly that. All three arms share the
generator, the alphabet, the operator set, the budget, the ecology, θ and the full rule
36/40/42/23 bar. They differ only in the initial measure. And they reach different frontiers:
the cold arm does not reach the coefficient cell of `E_smooth3`, the structured warm arm reports
reaching it on both seeds run so far. Same static data, different reachable frontier — `DU-1`
measured rather than assumed.

## 3. What this does to the packet's verdicts

`DU-3a`: restricting to reachable realizations never lowers a derived lower bound, so
**exclusions survive** — a robust exclusion obtained without reachability evidence still holds.
`DU-3b`: an upper bound is a construction, and constructions are not inherited by subsets, so a
**family verdict can invert** under restriction to the reachable set.

`RV-377-210`'s verdicts are constructions: a Pareto frontier over a *static, hand-registered*
candidate set. Its terminal was already qualified
`NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE__E3_REPORTED_NOT_BOUND` because the packet reports
class-level reachability from another lane rather than candidate-specific reachability. `DU-3b`
is the reason that qualification is **load-bearing rather than cosmetic**: it is precisely the
direction in which a construction-based verdict is not protected.

Stated conservatively, because the strong version is not earned: B6 supplies the *premise* `DU-3b`
needs — that reachability genuinely differs between development laws on this instrument — and
**not** an observed inversion of a packet verdict. No `RV-377-210` verdict changes here.

## 4. The existence question, and what the discarded genotypes cost

It is tempting to go further and say the coefficient cell of `E_smooth3` is non-empty in the
admitted sense — that would be a *static* fact needing only one witness, independent of Z1–Z3.
That claim is **not available from these receipts.**

Three arms report an admissible atrophied-DENSE machine there, each verified in-run by the same
`verify_candidate` the bar is defined by, with `min_over_six` 0.8542 and the rule-40 margin
recorded. But `first_of_class` does not retain the genotype, so the objects were discarded. An
existence claim whose witness cannot be re-exhibited rests on the run's own in-flight assertion.
That is a log line, not a witness, and it is written here as one.

This inverts the earlier call on that instrument gap. Deferring the genotype field was right while
it was housekeeping — adding it mid-campaign would make the receipts inhomogeneous under a frozen
protocol, and it still would. It is now the difference between a witness and a report, and the
deferral should be paid for deliberately rather than silently.

**Minimal purchase.** One re-run of `SAME|CONTINUED|S1` with the genotype retained yields an
exhibitable, independently replayable witness. It is the cheapest of the three recoveries — its
coefficient machine was first placed at evaluation 3 827, against 18 595 and 18 630 for the
others — and it settles the existence question without touching any pending Z prediction.

## Cross-references

`GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md` §RV-377-180-Z,
`GMI_NN_NONNN_MICROSCOPE_PACKET_RV_377_210_FREEZE.md`, `GMI_RV_377_113_FREEZE.md`,
`research/gmi-grand-unification-v1/DEVELOPMENTAL_UNDERDETERMINATION_THEOREM_V1.md`.

## 5. The K4 selection negative is not a failure of effort — it is `DU-1` measured

The corpus's own record calls this "the outcome most damaging to the programme":

> `K4_SELECTION_PRINCIPLE_CAN_BE_PREDICTIVE` = **FALSE** — cost-minimising neutral search over the typed
> IR does not converge on GMI's predicted 10-axis property vectors: 0 of 264 cells, cross-seed agreement
> **0.0 %**, invariant under a twenty-five-fold budget increase (20 000 → 100 000 → 500 000 evaluations).
> "Which genotype / property vector arises" is not a function of the inputs, not a well-posed prediction
> target.

`DU-1` proves that same sentence: the reachable frontier is **not a function** of the admitted realization
set, the profile map, the family assignment or any proved necessity, and *no theorem of that form can
exist*. One lane measured it and filed it as a defeat; the other lane derived it and filed it as a
boundary. They are the same statement.

That re-reading earns something the measurement alone could not. A negative result invites the question
"would more work fix it?", and the corpus answered honestly that a 25× budget did not. `DU-1` answers it
in general: no budget can, because the target is underdetermined until the development law is registered.
The negative converts from *unexplained* to *derived*, and the repair it names is structural — register
`D` as a primitive input — rather than "search harder".

### Three distinct underdeterminations, one proved and two measured

They should not be collapsed; each is independent evidence and each has a different remedy.

| | source of variation | what is held fixed | evidence | status |
|---|---|---|---|---|
| **U1** stochastic | the search's random draw | law, operators, budget, ecology, bar | K4: 0.0 % cross-seed agreement over 264 cells, budget-invariant | measured |
| **U2** initial condition | the seeded population | law, operators, budget, ecology, bar, **and the seed integer** | `RV-377-180`: `SAME/RESET/S0` does not reach the coefficient cell, `SAME/CONTINUED/S0` reports reaching it | measured |
| **U3** structural | the development law itself | the entire static package | `DU-1`'s two-law witness | **proved** |

`U2` is the one this lane contributes and it is not a special case of either neighbour: the seed integer
is identical across those two arms, so it is not `U1`, and both arms run the same law and operator set, so
it is not `U3`. It sits between them — the same law, differently initialised, reaching different frontiers.

### What survives all three

A claim universally quantified over a machine class survives restriction to any subset of that class, so
it is untouched by `U1`, `U2` and `U3` alike. The channel capability ceilings are of exactly this shape:
`CL-1`/TI-1 states `accuracy ≤ ½ + r/(2L)` for every machine in a channel class defined by *access
structure*, not by reachability. Restricting to the reachable machines leaves them in the class, so the
ceiling still binds — and `RV-377-123` verified it with 0 violations over 40 draws × 5 machines × 9 values
of `r`, tight where predicted, linear R² 0.999815.

So the programme's two halves have different standing, and the boundary between them is sharp:

* **Ceilings and exclusions are law-invariant.** `GMI_PREDICTS_CAPABILITY_OF_AN_UNSEEN_FORM` rests on
  TI-1 and is therefore *not* threatened by `DU-1`. Predicting how far a form's capability can go is
  safe.
* **Occupancy, frontier support and family verdicts are law-dependent.** Predicting *which* form arises is
  the thing `DU-1` says is not well posed without `D`.

Stated plainly: the theory can say how high any species can climb without knowing its development law, and
cannot say which species appears without one. Both halves are load-bearing, and only the second was ever
in doubt.
