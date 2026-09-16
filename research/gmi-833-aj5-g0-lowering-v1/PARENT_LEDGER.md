# AJ5 parent / ownership ledger

AJ5 does not claim novelty for generic compiler lowering, register-machine operational semantics, relational transition semantics, conditional branching, or terminal-state encodings.

Strong parents:

- structural operational semantics / labelled transition rules for step semantics;
- register/counter machine instruction semantics;
- relational semantics for nondeterministic/generalized transitions;
- compiler correctness and semantics-preserving translation;
- process/event systems for external input/output interaction;
- finite-state and sequential-circuit feedback semantics for persistent configuration.

Repository-owned residual at this scope:

1. explicit placement of the already-merged `G0-reg-v1` above AJ1–AJ4 rather than at the operational bottom;
2. a named primitive-status ledger (`DERIVED` / `PRESENTATION_ONLY`);
3. two independent lower presentation implementations checked against the canonical G0 interpreter on 484 executions;
4. exact presentation-relative overhead bounds;
5. an explicit theorem-transfer boundary separating semantic invariants from grammar/search/resource quantities that need translation.
