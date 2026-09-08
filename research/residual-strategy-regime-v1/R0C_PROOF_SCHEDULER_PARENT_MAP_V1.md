# R0C proof scheduler parent map V1

**Status:** literature-saturated parent map / no new proof result / no ML authorization.

The layered-vs-indexed observation from the native proof lane is a legitimate
future strategy-selection population only after it is expanded beyond the tiny
current task set.  Automated reasoning already has mature scheduling parents, so
R0C must beat or explain them before claiming a new executive mechanism.

## 1. Existing parent families

### Algorithm portfolios

Gomes and Selman (2001) show that combining/interleaving algorithms can exploit
runtime variation and outperform a single traditional method on distributions of
hard search problems.

### ATP strategy schedules

Production theorem provers already expose this directly:

```text
E       --auto-schedule / --satauto-schedule
Vampire portfolio/CASC schedules
```

They run multiple fully specified proof-search strategies under a resource
schedule.  This is a direct engineering parent for any proposed OCM proof
scheduler.

### Learned strategy scheduling

MaLeS (Kühlwein & Urban, JAR 2015) solves both strategy finding and strategy
scheduling for ATPs.  BliStr/BliStrTune learn or tune E proof-search strategies.
Therefore "learn a scheduler for proof strategies" is already an established
parent category, not a new Machine Epistemics mechanism.

### Restart theory

Luby, Sinclair and Zuckerman (1993) prove a universal restart schedule for a Las
Vegas algorithm whose runtime is random while completed runs are always correct.
This is useful only when R0C actually satisfies the restart assumptions.
Layered and indexed deterministic searches on fixed theorem instances do not
become a Luby-restart problem merely because they have different costs.

## 2. Frozen R0C population contract

Before selector work, construct a prospective family of exact proof tasks with:

```text
same checker/kernel authority;
same theorem statement bytes/types;
same allowed lemma/import information;
same resource ceilings;
no eventual success/failure label exposed as a feature;
no hidden authored route leakage;
>=2 exact safe search/scheduler strategies run on every task;
negative/bounded-exhaustion tasks included if the checker contract permits them.
```

The current #153 observation is donor evidence only.  A population should be
large enough that train/dev/evaluation splits or exact structural bins do not
collapse to theorem identity.

## 3. Legal feature boundary

Allowed prospective features may include cheap structural data already present
before proof search, e.g.:

```text
statement syntax/type shape;
number/type of local hypotheses;
registered lemma/index size;
cheap dependency/topology summaries;
current reusable proof-route/index state;
resource budget and already-spent budget.
```

Forbidden:

```text
whether the theorem eventually succeeds;
which route the checker later accepts;
realized search cost of a strategy before running it;
held-out proof body / hidden route;
evaluation-task identity lookup.
```

## 4. Parent ladder

Evaluate in this order:

```text
P0  single best static exact strategy
P1  hand/frozen deterministic schedule
P2  budget splitting / dovetailing portfolio
P3  restart parent when and only when independence/runtime-distribution assumptions hold
P4  ordinary E/Vampire-style strategy schedule on the frozen strategy set
P5  exact feature bins / finite decision tree
P6  ordinary per-instance algorithm-selection model
P7  learned ATP scheduling/tuning parent (MaLeS/BliStr-style)
P8  OCM-specific learned executive only if all above leave a protected payable residual
```

A claimed OCM residual must compare against the strongest applicable parent, not
against layered search alone.

## 5. Cost model

Report separately:

```text
checker/kernel calls;
search expansions/action attempts;
preprocessing/index construction;
strategy-switch/restart loss;
feature extraction;
scheduler inference/update;
persistent route/index bytes;
checkpoint/replay;
CPU/wall/RSS;
compilation/process startup where relevant.
```

A proof tree shortening or search-attempt reduction is a local method gain.  The
whole-machine theorem from `FORMAL_DECISION_CORE_V2.md` still requires the local
saving to exceed scheduler/runtime overhead.

## 6. Exact selector-sufficiency audit before learning

For every frozen resource price/coordinate and legal pre-search feature schema,
reuse the Phase-2A machinery:

```text
A*(task,state) = set of minimum-cost safe strategies
```

and compute whole-fiber common-action sufficiency plus feature-conditional regret.
If cheap features leave collisions but negligible regret, there is no economic
reason to predict them better.

If legal features alias theorem states whose safe required strategy sets are
disjoint, improve the observation channel or fall back/dovetail; do not increase
model capacity.

## 7. Terminals

```text
STATIC_OR_PORTFOLIO_PARENT_SUFFICIENT_R0C
  a conventional schedule captures the useful residual

PROOF_SCHEDULER_FEATURE_CHANNEL_INSUFFICIENT_R0C
  legal pre-proof observations cannot separate decisions that matter

PROOF_SCHEDULER_RESIDUAL_ALGORITHM_SELECTION_R0C
  safe exact strategy differences remain economically meaningful and predictable
  after conventional portfolios/schedules and complete cost accounting
```

Only the final terminal opens learned algorithm selection.  It still does not
make a neural network authoritative for proof acceptance; the exact checker
remains the authority boundary.