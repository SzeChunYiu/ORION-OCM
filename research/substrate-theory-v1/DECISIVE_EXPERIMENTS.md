# Decisive Experiments v1 — the smallest set that falsifies or establishes the architecture

Each experiment: frozen design before run, exact checkers, physical cost vector, honest terminals, claim ceiling. Order by information gain per cost; E-DEC-2 and E-DEC-5 are already in flight.

## E-DEC-1 Learned serving (closes NEG-I; ladder L4 entry)
**Question.** Can the machine learn WHEN to serve a fragment (learned I/V) — not just profit from an oracle that tells it?
**Design.** Arms: learned router (ledger-supervised, then bandit) vs ORACLE_APPL (M1B's 36/40 upper bound) vs ALWAYS-SERVE vs NEVER-SERVE vs SHUFFLED-ROUTER; frozen libraries, matched budgets; on M1B worlds AND an authored M2 ecology. Terminals: `LEARNED_SERVING_POSITIVE__SCOPE` (beats always/never and shuffled significantly, Holm), `PARENT_SUFFICIENT` (simple ACT-R U=PG−C matches the fancier router — then assimilate the simpler one), `REPRESENTATION_BLOCKED` (router fails everywhere but oracle works: Z features insufficient — locates the blocker in Z, not I).
**Why decisive.** The runtime's only zero-selection joint (KSO audit). If learned serving fails here with oracle headroom proven, the architecture cannot grow conditional behavior on this substrate without a representation change.

## E-DEC-2 Amortisation crossing + closed form (development as economic fact; ladder L3 exit)
**Design.** M1C in flight (#360/#361): fixed one-time dev cost, target ladder {8,32,128,512} straddling the ≈330 estimate, minimal arms; secondary corrected-ledger curve at N_FROZEN=30. ADD: validate the observed crossing against the materialized-view-economics closed form (build cost vs query mix with maintenance term). Terminals: `CROSSING_OBSERVED__AT_REGISTERED_SCOPE` / `NO_CROSSING_AT_MAX_N` / defects.
**Why decisive.** A developmental mechanism that never breaks even at any N is a lab artifact. The closed form turns an empirical crossing into a predictable engineering law.

## E-DEC-3 RSI generation-1→2 (ladder L5/L6 entry)
**Design.** RSI_SPEC's M1/M1B hidden-diagnosis programme: 5 arms (OCM / scripted / random / classical parent / oracle), then generation-2 transfer on a different failure. Terminal readout is the SLOPE, not the diagnosis. 
**Why decisive.** RSI_EARNED anywhere justifies the "recursively grow" half of the goal; AMORTIZER_ONLY honestly retires it at this scope — either way the architecture's central claim is decided.

## E-DEC-4 Consolidation/retirement (unlocks saturation regime)
**Design.** Wake-sleep re-mining + priced retirement vs pure accretion vs churn, at library saturation; Ψ-calibration preservation checked; full cost accounting including consolidation cost. Terminals: `CONSOLIDATION_POSITIVE__SCOPE` / `ACCRETION_SUFFICIENT` (PARENT_SUFFICIENT variant) / `MAINTENANCE_COST_DOMINATES` (a registered flagship negative).
**Why decisive.** Every real growth regime saturates; a substrate that cannot retire capital cannot grow past its first plateau.

## E-DEC-5 Independent-authorship + two-domain generality (ladder L3 ceiling, L7 entry)
**Design.** M2-P2 (in flight, #358): full replication of the #356 developmental result on someone-else-authored ecology via the P1-E3 author unit. Flagship gate-4 study (task #63): same registered core, two materially different domains, transfer measured. Terminals from the frozen #356 protocol + flagship negative terminals.
**Why decisive.** Removes the last authored-by-self caveat from the developmental claim; the two-domain study is the first cross-domain (L7) observation or its registered refutation.

## Sequencing
F-1 failure receipts precede E-DEC-3 (diagnosis needs typed failures). E-DEC-1 needs no prerequisite (ledger logs exist). E-DEC-2/5 already running. E-DEC-4 after E-DEC-1 (serving quality measures consolidation benefit).
