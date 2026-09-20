# Resource distinction: read first
This round computes the exact minimum execution resource needed to distinguish
two states of a finite partial deterministic machine with visible edge costs.

- [Model and proofs](THEORY_V10.md): graph reduction, observation boundary,
  sharp finite bound, nested quotients and snapshot-memory consequence.
- [Kernel scope](FORMAL_SCOPE_V10.md) and [Lean source](ResourceV10.lean).
- [Threshold implementation](threshold_v10.py) and
  [local optimality certificate](certificate_v10.py).
- [Independent residual-state oracle](independent_oracle_v10.py) and
  [receipt](RESULT_V10.json).
- [Freeze](FREEZE_V10.md), [exploratory chronology](PROTOCOL_CONTEXT_V10.md)
  and [primary parents](PARENTS_V10.json).
- [Historical assimilation repairs](ASSIMILATION_BACKLOG_V10.md).
- [Next original requirements to adjudicate](NEXT_ATOMIC_CLOSURE.md).

More resource can split response classes when the observed action/event
determines the resource consumed. Hiding that cost can make classes merge
again. Zero-cost loops require shortest-path witnesses with progress;
arbitrary solutions of Bellman equations can report false finite thresholds.

The algorithms adapt established automata, energy-game and shortest-path
methods. This is a mathematical prediction checked on declared machines,
not a new empirical law or demonstrated all-family theory.
Minimum codes at fixed known resource are not total online memory.
Distinguishing expenditure is not directed process-conversion burden.
