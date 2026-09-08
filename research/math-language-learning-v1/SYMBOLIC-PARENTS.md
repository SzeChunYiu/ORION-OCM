# Symbolic parents for checked method acquisition

Primary-source research, 2026-09-08. This is a prospective mechanism supplement,
not a change to the active registered assay or a result from it. No laptop reads,
experiments, installation or new dependency were used for this note.
The reported name search covered six programme summaries only; it establishes
neither repository-wide absence nor novelty. The proposals below are our inferences.

## Mechanisms to absorb

| Donor | Actual mechanism and reusable contribution | Boundary for OCM |
| --- | --- | --- |
| Soar chunking / explanation-based behavior summarization (EBBS) | When substate reasoning produces a superstate result, backtrace the contributing production instantiations; retain supporting conditions, variable identities and constraints; compile a production that can reproduce the result later. This is a concrete route from solved reasoning to reusable procedural knowledge. | Export a support-bearing rule candidate from a checked training trace. Generalization must preserve dependencies and negative conditions; a chunk firing alone is not an independent mathematical proof. [Official manual](https://soar.eecs.umich.edu/soar_manual/04_ProceduralKnowledgeLearning/) |
| Popper, learning from failures | Generate a logic-program hypothesis within a declared bias, test positive/negative examples, and derive constraints from failures. Under the paper's assumptions, overly general hypotheses eliminate generalizations; overly specific ones eliminate specializations. Reuse the failure-informed search, rather than repeatedly testing equivalent rejected programs. | Candidate elimination needs a justified subsumption relation. For arbitrary Boolean AST edits, adding/removing syntax is not automatically a sound generalization order. [Cropper and Morel paper](https://arxiv.org/abs/2005.02259) |
| Metagol | A Prolog meta-interpreter searches substitutions for predicate variables in supplied metarules. Its examples demonstrate invented predicates; recursion requires suitable metarules. Search uses iterative deepening over clause count. | Metarules are supplied inductive bias, not acquired knowledge. Share and freeze that bias before training; distinguish learned predicate substitutions/compositions from manually provided successful rules. [Author-maintained implementation and documentation](https://github.com/metagol/metagol) |

These described mechanisms are symbolic: dependency analysis and production
matching, logic-program search, unification, and logical/constraint solving.
They require no neural encoder, gradient training or LLM-produced rule library.
That is a mechanism-level inference from the documented algorithms, not a claim
that every possible integration or dependency has been audited as neural-free.

Two practical details prevent an unfair or misleading implementation:

- Soar procedural learning is disabled by default. Explicitly enable and record
  the intended chunking regime. Its documentation warns about overgeneralization
  from local negation; the documented `record-utility` facility is marked
  unimplemented, so it cannot supply measured savings for this comparison.
  [Official chunk command reference](https://soar.eecs.umich.edu/reference/cli/cmd_chunk/)
- Popper's current repository specifies examples, background knowledge and a bias
  file; it also documents newer combine-stage solvers and optional noisy learning.
  Pin an actual revision and declared algorithm/settings. Do not describe an
  arbitrary current checkout as exactly the paper's original implementation.
  [Official Popper repository](https://github.com/logic-and-learning-lab/Popper)

## A faithful and equally adaptive challenger

Use an enabled symbolic learner with the same permitted training inputs, verified
training results, primitive semantics and developmental selection information.
Preserve the learner's actual search and learning; a frozen hand-written rule list
would not be the adaptive parent. If OCM receives proof traces, provide the same
trace interface and charge its construction to both arms. No held-out answer,
semantic fingerprint or original-run annotation becomes a strategy feature.

For a first bounded integration, translate learned candidates into the existing
universal-rule data schema, then use the shared independent schema checker and
answer checker. Preserve empty predicates, classical negation and distinct
existential witnesses. Prolog failure-to-prove must never stand in for a classical
negative proof or turn UNKNOWN into false. Reject unrepresentable candidates;
retain their search, translation and refusal costs.

A Python trace compiler inspired by EBBS is an adapted donor, not an executed
Soar baseline. Likewise, restricting Popper/Metagol to the unary rule fragment
tests that fragment; it does not establish performance against unrestricted
recursive program induction. Report the exact retained mechanism and restrictions.
Prefer a faithful upstream implementation for an upstream-system claim.

Separate three records in either store:

1. **Correctness:** independent universal-schema validation plus the actual
   task-specific proof/use check. Fitting training examples is insufficient.
2. **Discovery:** actual training support, learner trace, source identity and
   learned candidate provenance. A valid rule may still lack observed acquisition.
3. **Utility:** held-out development measurements under the declared cost rule.
   Proven correctness or a recorded derivation cannot certify positive utility.

Give the conventional parent real content-addressed persistence, cold restore,
current-role validation, learned-rule matching and exact fallback. Share the same
semantic deduplication, allowed cache lifetimes, candidate eligibility and selection
rule. Do not add KSO emulation or unrelated OCM source scans to its operation cost.
Charge actual candidate search, failed candidates, trace creation, checking,
matching, persistence, restore, failed fallback and cleanup; report missing totals
as unavailable. Neural-free computation still has these costs.

## One falsifying comparison

In a separately preregistered paired experiment, independently acquire the same
donor policy in conventional and OCM arms from equal inputs. Compare canonical
candidate/library identities before cold restart; an unexplained difference is a
comparison defect, not evidence for either arm. Then measure checked fresh use
over the same fixed horizon, with observed acquisition-plus-service cost closure.

For a task with actual learned-rule use, inhibit only that matched learned method
in a paired replay while preserving the task, primitive solver and cache policy;
require a checked fallback and record all extra work. This tests causal savings
from the acquired method, whereas premise removal separately tests support dependence.
If both restored arms exhibit the same valid causal reuse and the conventional
parent matches or improves the full-horizon cost, the hypothesis that the OCM
runtime organization is necessary for that benefit is falsified for this scope.
An advantage requires measured closure; an unavailable total supports neither side.

Adopt trace-to-rule compilation and failure-informed induction as concrete donor
mechanisms. Keep the current experiment unchanged; implementation and comparison
would need their own source qualification and prospective registration.
