# Decisive experiments and performance gates

[Read first](CORE.md) · use #115 for engineering, #62 for learning, #73 for integrated comparisons, #38/#49 for acceptance.

## Define performance before optimizing it

The primary useful output is a **correctly completed task with valid support**, not tokens/second, parser derivations, tests passed or abstractions created.

For each request measure semantic correctness, completion, appropriate clarification/refusal and stale/unauthorized outputs. Report p50/p95 latency and CPU time at equal quality. Report failures/timeouts in the denominator; faster refusal must not look like faster solving.

Lifetime cost includes initial acquisition, indexing, parsing/compilation, all queries, checks, consolidation, failed attempts, persistence, revision, replay and retained storage. Keep time/CPU/memory/bytes/checker calls as a vector rather than hide trade-offs in an arbitrary score.

For a proposed optimization, estimate the observed crossover:

```text
extra preparation + extra maintenance over Q requests
    < sum of saved end-to-end request costs over those Q requests
```

If steady conditions permit it, report Q_break_even ≈ extra preparation / per-request saving. If the denominator is nonpositive, there is no measured crossover. Also report the actual task stream; stationarity is an assumption.

**Suggested commissioning objectives, not established results:** warm familiar language tasks p95 ≤1 second; small registered problem-solving tasks p95 ≤5 seconds, including checking and response. These are usability targets for the initial bounded service. Calibrate feasible input/field scales on laptop billy, then freeze evaluation settings; do not silently exclude harder requests to meet a clock.

## E0 — baseline and comparator integrity

**Question:** are we measuring the same task, information and authority in each arm?

Recover the uncommitted M12 comparator patch onto current main selectively. Its exposed A/E implementation is not whole-system parity. Qualify shared speaker attribution, language lessons, transfer inputs, restart and withdrawal before interpreting performance differences.

Create one public development stream with raw language requests, acquisition, unrelated tasks, correction, restart, method withdrawal and repeated solving. Freeze source/model/checker/task identities and capture the entire process tree.

**Pass:** both arms receive equivalent information and expected lifecycle powers; results identify every unresolved capability asymmetry. A missing comparator feature becomes CANNOT_CHECK for that contrast, not zero performance.

**Figure:** baseline capability and cost decomposition. **Owner:** #38/#73.

## E1 — actual-runtime integration and overhead

**Hypothesis:** existing kernels and reusable preparation reduce serving cost without changing accepted results.

Compare reference OCM, one integrated replacement, and native persistent pipeline on the same task stream. Run cold process, warm service, then update/revoke/restart. Randomize paired execution order; control model loading and process contention.

Validate the real call path by injecting a recording provider/backend and forbidding the replaced helper in that selected mode. Require exact candidate/decision/lifecycle parity, not merely successful construction of an experimental object.

Count global passes, copied bytes, input/incidence visits, support evaluations, considered operators, solver calls, checker preparation/checks, ledger bytes and exact fallbacks. Include near-threshold/tied activations and post-update invalidation.

**Adopt:** exact obligations preserved and a prospectively defined complete-task/lifetime Pareto improvement at the registered workload. Warm-only savings keep their narrow label. **Owner:** #115 FK-0–4/#72.

## E2 — locality, revision and storage

**Hypothesis:** exact indexes and incremental lifecycle state keep local work tied to actual relevant/changed structure.

Use development growth points such as 1×, 3×, 10× and the largest feasible scale; freeze actual counts after the preflight. Vary independently:

| Axis | Falsifying condition |
|---|---|
| Unrelated N grows, relevant region fixed | Hidden full scans/digests/index rebuilds erase locality |
| Operator catalogue grows | Candidate selection or maintenance remains proportional to all operators |
| Local evidence withdrawal | Stale dependents or collateral invalidation |
| Shared premise with global fanout | System must process the genuinely global cone honestly |
| Alternate/upper-only support | Incorrect LIVE/UNKNOWN/DEAD transitions |
| Repetition/residual density | Factoring loses on incompressible or exception-heavy data |
| New distinguishing operator | Old summary remains used beyond its sufficiency certificate |
| Full audit/export | Output-sized global cost must remain visible |

Use exact reference comparisons on tractable cases and scalable independent invariants/certificates at larger cases. Instrument k as actual distinct atoms, edges, support nodes and bytes touched across **the whole request**. A tiny returned set with a global preparatory scan is not sparse execution.

Compare one representation dimension at a time: append backend, dependency index, warrant DAG, packed/sharing storage. Measure retained memory and cleanup over long streams.

**Adopt:** exactness and complete measured gain in the declared ecology. No universal O(k) statement. **Owner:** #115 FK-5–9/#70/#72.

## E3 — end-to-end language and learned communication

**Hypothesis:** a compact listener/speaker can acquire useful new families and retain them through revision.

First complete the explicitly seeded text→task→checked answer→English fixture. Then freeze TRAIN, DEV and protected semantic families, including unseen vocabulary/construction combinations, role reversal, negation, scope, quantities, ambiguous references and an artificial/non-English order.

Compare persistent conventional construction memory, reset learner and OCM; expose the same examples and corrections. Report initial authored priors and donor model training information separately from acquired competence.

Grade exact task meaning, response semantic fidelity, task completion and appropriate clarification. Test the listener and realizer separately against fixed gold meanings, then test the full conversation. Use independent meaning checks; later fluency judgments require a blinded rubric. Show accuracy versus acquired examples, not just final score.

**Adopt:** gain on new combinations without forgotten prior lessons or invalid transfer. Protected N1/N2 terminals retain their existing owners and prerequisites. **Owner:** #43/#52/#53/#55, later #44.

## E4 — composition and acquired-method utility

**Question 1:** did the learner produce usable structure? Execute the already prepared saved-predicate consumption assay under #62. It is public development and cannot become protected evidence.

**Question 2:** does acquired structure causally improve later tasks? Use a frozen library and later distinct semantic functions, including related, unrelated and adverse-transfer families. Record observed search use or verified executable-application use, distinguishing both from final macro text and reconstruction. Unobservable search internals remain unknown.

Use a 2×2 design where feasible:

| System | Fixed library | Adaptive library |
|---|---|---|
| Strong native persistent pipeline | N-fixed | N-adaptive |
| OCM with same donors/powers | O-fixed | O-adaptive |

N-adaptive versus N-fixed tests donor learning. O-adaptive versus O-fixed tests learning within OCM. O-adaptive versus N-adaptive tests the complete-system difference. The interaction (O-adaptive−O-fixed)−(N-adaptive−N-fixed) estimates an incremental learning effect on the predeclared outcome scale; targeted coupling ablations are still required to attribute it to a particular mechanism. Give comparators matched provenance, checks, history and acquisition opportunities.

Include removal of the learned structure, primitive-alias normalization, shuffled/equal-sized irrelevant libraries, and independently sufficient replacement support. Freeze new functions before protected access; new arguments for an old function do not count as new semantic functions.

**Adopt:** higher later capability or cheaper complete lifetime at matched capability. Alias-only syntax reduction remains a representation result unless later utility is measured. **Owner:** #62/#71/#73.

## E5 — protected two-domain machine test

Run language interaction and verified procedural/mathematical tasks through the same field/lifecycle. Use multiple independent lifetimes with related and unrelated tasks, order variation and interventions.

Primary comparators: strongest faithful native persistent system and a qualified strong LLM with the same documents, tools, memory, feedback and adaptation opportunities. Domain-specialized donors remain comparators even when OCM adopts them. Model names, versions, prompts, access and costs are frozen at launch.

Select quality non-inferiority margins from task consequences before outcomes. Determine independent lifetime count from development variance/precision or power analysis. Repeated calls in one lifetime and tasks sharing a template are not independent samples. Preserve clustering, report paired uncertainty and predeclare primary endpoints/multiplicity handling.

An unavailable or unfairly constrained LLM arm prevents an LLM-comparability claim; native capability and engineering work may still proceed.

**Claims are separate:** bounded capability; learned communication; useful method learning; locality; revision; lifetime economics; LLM comparability. One positive does not promote every claim. **Owner:** #73/#38/#49.

## Failure-to-next-action rule

Record failure at one stage, reproduce against the strongest parent, research the mechanism, change that stage, and retest with preserved outcomes. Keep the original negative.

Current concrete revivals: runtime bypass → narrow adapter; history overhead → existing transactional donor; parser explosion → semantic evidence/ambiguity control; primitive aliases → useful later-consumption and normalized library utility; explicit solver timeout → native-interface/search diagnosis; unfair parent → shared-input comparator qualification.

Conclude a bounded experiment when its frozen criterion is resolved. Continue the programme through an explicit improvement path where broader capability remains unmet; do not tune the criterion until the result becomes positive.
