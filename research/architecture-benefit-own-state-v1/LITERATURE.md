# Primary-literature map for the architecture-benefit tranche

This is a scoped reading record, not a claim that all of metareasoning, learning,
formal methods or online algorithms has been exhaustively read. The sources below
were inspected before the proposed comparison and proof obligations were fixed.
Reading depth is explicit: an abstract is not represented as a full-paper review.
The purpose is to reuse mature solutions and isolate the OCM-specific obligations.

## L1. Russell and Wefald (1991), Principles of metareasoning

Primary publisher: https://doi.org/10.1016/0004-3702(91)90015-C

Read scope: publisher abstract and problem statement. Full-paper proof audit is
not claimed. Computation is evaluated through its effect on subsequent external
decisions. Adopt the value-of-computation framing; do not claim that writing a
Bellman recurrence provides a cheap, deployable metareasoner. Its implementation
cost and model accuracy must themselves be established.

## L2. Baxter (2000), A Model of Inductive Bias Learning

Primary author manuscript: https://arxiv.org/abs/1106.0245
Full text inspected: https://arxiv.org/pdf/1106.0245

Read scope: environment-of-tasks formulation, Theorem 2 and discussion in section
2.5. The manuscript is a later arXiv deposit of the 2000 work. Adopt an explicit
task-environment distribution and separate within-task generalization from
across-task generalization. A bound between empirical and environment error does
not guarantee small error, cheap search, worthwhile discovery, or superiority to
persistent conventional parents. OCM needs a cost claim in addition to accuracy.

## L3. Ellis et al. (2021), DreamCoder

Primary manuscript: https://arxiv.org/abs/2006.08381
Full text inspected: https://arxiv.org/pdf/2006.08381

Read scope: wake/sleep architecture, program-library learning and library/search
interaction. Adopt endogenous abstraction from previously solved tasks as an
existing constructive mechanism. A library need not be hand-supplied for reuse to
occur. Do not transfer DreamCoder's empirical results to OCM or equate finite
example agreement with OCM's independent exact identity/proof check.

## L4. Bowers et al. (2023), Top-Down Synthesis for Library Learning (Stitch)

Primary manuscript: https://arxiv.org/abs/2211.16605
Full text inspected: https://arxiv.org/pdf/2211.16605
Artifact: https://zenodo.org/record/7151663

Read scope: sections 3-4 on search/pruning and compression utility; section 6 on
benchmarking, including the higher-order extension in 6.5. Adopt efficient
symbolic abstraction discovery as a serious parent to OCM's recurring-fragment
miner. Compression utility needs overlap-aware accounting; it is not identical
to downstream search or whole-machine wall-time utility. Do not make the blanket
claim that Stitch cannot represent higher-order libraries: the paper explicitly
studies extensions beyond its basic first-order presentation.

## L5. Acar, Blume and Donham (2011), A Consistent Semantics of Self-Adjusting Computation

Primary manuscript: https://arxiv.org/abs/1106.0478
Full text inspected: https://arxiv.org/pdf/1106.0478

Read scope: semantics and consistency/correctness theorem statements, including
section 3; not every proof in the long appendix was independently reconstructed.
Adopt dependency-sensitive reuse and change propagation as conventional parents.
Correctness relative to fresh execution is an explicit semantic requirement.
It does not automatically discharge OCM authority, support identity, revocation,
external effects or persistent ledger obligations.

## L6. Mokhov, Mitchell and Peyton Jones (2020), Build Systems a la Carte: Theory and Practice

Primary author page:
https://simon.peytonjones.org/build-systems-a-la-carte-theory-and-practice/
Primary publication: https://doi.org/10.1017/S0956796820000088

Read scope: author/publication overview and architecture decomposition, not a
line-by-line audit of all proofs. Adopt the separation between scheduling and
rebuilding/dependency decisions. A task graph plus exact invalidation is not
inherently unique to OCM. The comparison should implement or transplant these
conventional components rather than weaken its baseline by resetting every query.

## L7. Arora, Dekel and Tewari (2012), Online Bandit Learning against an Adaptive Adversary: from Regret to Policy Regret

Primary manuscript: https://arxiv.org/abs/1206.6400
Full text inspected: https://arxiv.org/pdf/1206.6400

Read scope: introduction and policy-counterfactual definition; first two PDF
pages inspected, including the displayed policy-regret formulation. Adopt the
warning that an alternative policy changes its own history. Theorem B applies
that distinction to persistent caches and learned libraries. Do not transfer the
paper's adversarial impossibility conclusions to a restricted OCM workload
without checking the assumptions.

## L8. Howard, Ramdas, McAuliffe and Sekhon (2021), Time-uniform, nonparametric, nonasymptotic confidence sequences

Primary manuscript: https://arxiv.org/abs/1810.08240
Full text inspected: https://arxiv.org/pdf/1810.08240

Read scope: introduction and time-uniform/martingale-mixture construction;
first-page figure inspected. Adopt nonnegative-supermartingale evidence and
optional-stopping discipline. The small rational betting process in this tranche
is a deliberately simple application, not the authors' optimized empirical
Bernstein procedure. Its IID complete-lifetime sampling and cost caps must be
justified externally. Twenty correlated queries are not twenty independent
lifetimes; repetition of one fixed pilot tape is not fresh population evidence.

## L9. Spall, Mitchell and Tobin-Hochstadt (2022), Forward Build Systems, Formally

Primary manuscript: https://arxiv.org/abs/2202.05328
Full text inspected: https://arxiv.org/pdf/2202.05328

Read scope: correctness discussion and section 6 distinguishing partial from
total speculative correctness. Adopt explicit effect/hazard assumptions before
reordering, skipping, or speculating on computation. The paper's distinction is
important: total correctness of arbitrary speculative execution is not its
unqualified result. Likewise, pure first-answer equality is not an OCM suffix-
elision or lifecycle proof.

## What the reading changes in the implementation

1. Do not seek a theorem that no conventional machine can emulate OCM. Seek a
   reproducible, useful implementation with a precisely scoped comparative claim.
2. Use existing symbolic library learning and dependency-maintenance parents.
   OCM's added contribution must survive their inclusion and complete costs.
3. Make the baseline counterfactual executable with its own evolving state.
4. Prove cost bounds on a reachable product of both state machines, including
   STOP and cleanup; automatically solve the finite potential constraints.
5. Separate capability/protected-semantic correctness from a statistical net-
   benefit claim. Neither a test count nor a confidence score grants authority.
6. Preserve negative and positive regimes, all attempted lifetimes, acquisition
   costs and invalid records. Do not tune a workload to manufacture an advantage.

## Unfinished literature/implementation obligations

A proof-assistant mechanization and source-to-abstraction refinement are not
supplied. The target-specific efficient library miner and fully qualified
incremental dependency parent are not yet integrated. The native pilot reuses the
repository's existing miner to establish attribution and cost visibility first.
No claim of field-wide literature saturation or mathematical novelty is made.
