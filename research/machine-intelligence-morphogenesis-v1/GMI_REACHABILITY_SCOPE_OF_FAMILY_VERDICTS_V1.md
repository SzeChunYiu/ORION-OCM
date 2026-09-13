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
