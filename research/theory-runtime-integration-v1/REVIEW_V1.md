# Internal review and continuation record

Date: 2026-09-05. This is internal agent review, not independent external scientific review.

The coordinator recovered the remote repository state, inspected the newer local
continuation, and selected the existing V2 method-learning contract as the first
concrete integration target. A continual-learning/epistemic-architecture reviewer
checked existing capability, source custody and learning scope. A mathematical-logic
reviewer checked theorem/implementation correspondence and the distinction between
proof verification, novel results and epistemic evolution.

Both reviewers corrected the initial remote-only interpretation: local `09f8c95`
already contains method generators and stronger runtime corrections, while M11/M12
scientific conclusions require reopening or reevaluation. The existing local
Anthropic comparison was retained instead of duplicating its research.

## Findings and resolution

1. The first M2 witness showed that x and x² agree at 0 and 1 but have different
   polynomial coefficients. It did not submit the wrong candidate to the actual
   verifier. The final check constructs a candidate with valid task/metadata
   bindings and requires `verify_solution` to reject its wrong program.
2. Ordinary Python imports could read existing bytecode caches despite verified
   source files. The final runner copies only hash-checked source/data into new
   private trees, rejects an existing destination, and imports from those trees.
   A control confirms that an existing cache is not copied. The host interpreter
   and standard library remain trusted inputs.
3. Wording was corrected from "self-adoption" to externally governed
   self-reorganisation adoption, and from "no runtime state changes" to "no
   existing runtime state changes": the demonstration uses temporary runtimes.

Both reviewers re-read their fixes and reported the findings addressed. Neither
reviewer claimed to rerun the tests. The coordinator's execution evidence is
recorded separately in `VALIDATION_V1.json`, `BINDING_TESTS_V1.log` and `REPLAY_V1.json`.

## Remaining integration limits

- Only the four named method-learning rows are mapped and exercised here. The
  historical intake list is preserved, and its other rows are not promoted.
- The packet is a manually run review tool, not an adopted runtime authority
  gate, an automated theory learner, or a new CI result.
- Finite numeric checks do not prove all-rational semantics, finite identification
  cases do not establish noisy/open-class learning, and sample search-slot savings
  do not establish whole-lifetime advantage.
- Fresh protected M11/M12 evaluation, external benchmarks, stronger matched parents,
  broader method representations and a genuine proof-kernel integration remain open.
- The existing runtime sources, tests, tools and packaging are unchanged from
  `09f8c95`. All twelve existing successor receipt checks passed after the addition;
  those receipts do not cover this new package or establish new scientific outcomes.

The new branch continues the committed local OCM work and binds the merged V2
theory. Remote publication and merging have not occurred in this continuation.
