# research/cognitive-ladder — Machine Epistemics cognitive ladder

Programme: [#143](https://github.com/SzeChunYiu/ORION-OCM/issues/143).
Publication constitution: [#144](https://github.com/SzeChunYiu/ORION-OCM/issues/144).

**Read `STUDY_CARDS_V1.md` first.** Every result-bearing artifact here declares its evidence class,
contribution level, decisive causal question, strongest parent, prior-information audit and kill
criterion before it produces anything. Nothing in this lane is confirmatory evidence.

## What this lane is for

The general question, stated without project vocabulary:

> Can an artificial system accumulate persistent reusable competence such that prior learning
> causally reduces the marginal cost of future learning, reasoning and correction, while the
> computation relevant to any one task stays small as total competence grows?

Finite exactly-solvable games are the microscope. They are not interesting in themselves. They are
used because the complete state space, the optimal policy, the failure conditions and an exact
checker are all available, so a causal claim can be identified rather than asserted.

## Layout

| file | role |
|---|---|
| `games.py` | exact game families: one-heap subtraction, Nim, and SUBNIM which needs both |
| `methods.py` | registered method languages with exact version-space counting, MDL admissibility, bits of prior versus bits acquired |
| `prereg.py` | commitment-derived seeds: the protected draw is a function of the plan hash |
| `escalation.py` | the search-more versus jump discriminator and its seven-level ladder |
| `escalation_worlds.py` | nine registered worlds, one per defect type plus the budget hostile |
| `escalation_generator.py` | draws worlds whose minimum sufficient level is true by construction |
| `escalation_parents.py` | four parents including the fully-resourced exact repair planner |
| `failure.py`, `failure_worlds.py`, `failure_parents.py` | scoped failure knowledge and its parents |
| `scaling.py` | the active-subspace meters: N, k, index build and maintenance, crossover |
| `atlas_data.py`, `atlas.py` | the ORION concept validation atlas, generated |
| `study_cards.py` | the #144 classification cards, generated |
| `claim_ledger.py` | PUB-D1: every result with the wording it licenses and the wording it forbids, generated |
| `run_escalation.py` | emits the escalation pilot receipt |
| `subspace*.py` | E1: relevance discovery with the family key withheld |
| `diagnosis*.py` | E2: failure-cause diagnosis with the cause withheld |
| `depend*.py` | E3: dependency discovery with the graph withheld |
| `escalation_independent.py` | E4: blindly perturbed worlds levelled by an independent repair oracle |

Generated files (`ORION_CONCEPT_VALIDATION_ATLAS_V1.*`, `STUDY_CARDS_V1.*`) are never edited by
hand. Edit the source module and re-run it.

## Running

```
PYTHONPATH=research/cognitive-ladder python -m pytest -q research/cognitive-ladder
PYTHONPATH=research/cognitive-ladder python research/cognitive-ladder/atlas.py
PYTHONPATH=research/cognitive-ladder python research/cognitive-ladder/study_cards.py
PYTHONPATH=research/cognitive-ladder python research/cognitive-ladder/claim_ledger.py
PYTHONPATH=research/cognitive-ladder python research/cognitive-ladder/run_escalation.py \
    --out research/cognitive-ladder/results/ESCALATION_PILOT_V1.json
```

Stdlib only, Python 3.11+. Modules import by bare name, so the lane directory must be on
`PYTHONPATH`. The lane deliberately sits outside `src/ocm`: moving it there rewrites sealed source
inventories and breaks receipt verification in CI.

## What this lane does not establish

No causal mechanism, no scaling law, no transfer result, no novelty and no field status. The three
pilots are calibrations. In particular:

- The escalation worlds and the escalation policy share an author, so the accuracy figure is
  calibration rather than confirmation. The binary jump-versus-no-jump decision is already closed
  against a fully-resourced parent elsewhere in the programme, with a protected incremental gap of
  exactly zero, and this lane does not reopen it.
- The failure-knowledge mechanism has already been assigned to truth-maintenance nogoods plus
  responsibility assignment, with the strongest-parent gap frozen at zero before execution. The
  pilot is run as an attempt on that closure's own stated falsifier, and its expected outcome is
  `PARENT_SUFFICIENT`.
- Sparse query work under a supplied family key is a property of the key, not of cognition. The
  only coordinate where a residual could survive is stale detection after a shared support is
  revoked.

Saying this early is not pessimism. It is what would make a surviving residual, if there is one,
worth reading.

## What the four follow-up experiments removed

Each of the three pilots rested on something the world handed the machine. E1 withholds the
relevance key, E2 withholds the cause of a failure, E3 withholds the dependency graph, and E4
withholds the generator's intent by recovering each world's minimum sufficient level through
exhaustive search over the repair lattice instead. None of the four produced a result favourable to
the architecture. Two produced findings about the problem class that hold regardless of it, and
those are recorded in `CLAIM_LEDGER_V1.md` as C9 through C12.

The most consequential is E4: the escalation policy's 70/70 on the old generator becomes 1736/2000
on independent worlds, and its 20-point lead over a fully-resourced repair planner becomes 0.7
points. The old generator's own labels agree with an independent oracle on 53.4% of worlds.

## Vocabulary discipline

`PARENT_SUFFICIENT` is a successful terminal, not a failure, and it does not mean that published
prior work suffices; in several ORION studies the parent federation holds ORION's own typed modules.
Saturation in ORION always means coverage of a declared literature or donor universe. Cognitive
saturation, meaning a system's own reasoning ceasing to yield new decision-relevant structure, is
unclaimed in the ORION repositories and is introduced here as a new concept rather than attributed
to them.
