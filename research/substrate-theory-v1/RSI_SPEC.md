# RSI Spec v1 — recursive self-improvement, earned

## Definition (frozen)

An **improvement episode** e_i is: failure signal → self-model read → causal hypotheses → active experiment selection → diagnosis → repair generation → prospective prediction (written before evaluation) → shadow evaluation → externally governed adoption/rollback. 

**RSI is earned** iff across matched generations G_1..G_k (matched = same task-class budget, same evaluator, same governance): cost-to-verified-improvement ℓ(G) = C(e)/verified_gains(e) is **strictly decreasing**, or verified-gains-per-resource strictly increasing. One generation cannot earn RSI — the claim lives in the *slope*, and **no parent metric exists** (ARCH annex §b: Soar chunking gives practice curves, DreamCoder compression-over-order, STaR constant-cost gains with quick saturation — none measures declining cost-to-verified-improvement).

## Terminals (pre-registered)

- `RSI_EARNED__SCOPE_<s>` — slope < 0 across ≥2 matched generations at registered scope.
- `AMORTIZER_ONLY` — flat/rising slope: the substrate amortizes but does not recursively improve. **Valid phase-1 outcome, not a failure to bury.**
- `GOVERNANCE_BLOCKED` — repairs blocked by the evaluator: mechanism untestable at this scope.
- `CANNOT_CHECK_<reason>`.

## Governance invariants (absolute; parents: CEGIS oracle separation, SPIBB baseline protection, HCOPE/doubly-robust gating, shadow→canary; DGM self-tampering is the capture lesson)

1. OCM may diagnose, propose, experiment, predict, learn. It **cannot** alter: evaluator, thresholds, authority system, cost accounting, protected task generator, verifier, historical evidence.
2. Every proposed change binds: source/patch hash + executable hash + prediction receipt + shadow-run result.
3. Self-generated claims never grant authority; adoption is E-signed external; rollback is automatic on prediction-receipt mismatch.
4. Learned value (control layer) may order/prune, **never** flip unit liveness or admission (COGNITIVE_UNIT_SPEC placement rule).
5. Writable-closure check: the running system's evaluator set is verified disjoint from its writable set each episode (static property, Gödel-machine separation transposed to an empirical check).

## The M1/M1B hidden-diagnosis programme (generation 1)

**Testbed.** OCM receives ONLY the original M1/M1B failure evidence (pre-diagnosis artifacts: M1 native-acquisition receipts, the APPLICABILITY-missing signature as it appeared raw) plus a safe intervention space (probes, ablations, library operations — never evaluator/generator). The later causal structure (oracle-applicability result #357, DEV-CAL charging attribution #353/#359) is **hidden from the tested OCM**.

**Arms.** (a) OCM self-diagnosis with its failure-class taxonomy wired; (b) scripted diagnosis (the actual historical sequence); (c) random ablation; (d) strong classical diagnostic parent (dependency-graph + delta-debugging baseline); (e) oracle (given the true causal graph). Metric: experiments-to-correct-diagnosis at matched experiment budget; prediction precision of the diagnosed cause.

**Generation 2 (the RSI test).** A *different* later failure (e.g. the shared-substring mining failure, E3's refusal signature) is presented. Question: does carrying generation-1's improvement episode (its diagnosis traces, typed constraints, updated experiment-selection policy) reduce generation-2's cost-to-correct-diagnosis below generation-1's, at matched budget, versus a fresh OCM? That slope — not any single diagnosis — is the first RSI_EARNED/AMORTIZER_ONLY readout.

**Freeze discipline.** Prediction receipts written before each evaluation; arms pre-registered; exact checkers sha-bound; no interim looks; terminals verbatim above. Compute on laptop billy / billy-old / LUNARC; never the Mac.

## What RSI is NOT

- Not self-modification of the evaluator (forbidden above).
- Not "got faster on the same tasks" without a matched-generation slope.
- Not a benchmark delta purchased by tuning thresholds (no-threshold-relaxation rule).
