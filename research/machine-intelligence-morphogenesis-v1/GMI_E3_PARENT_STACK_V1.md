# GMI E3 parent stack v1 — formal mathematics + execution-verified code

Status: **parent-first protocol input**, not an ORION novelty claim.

Refs #369 #46 #47 #208 #233 #377 #373.

This file freezes the strongest parent roles that the first real GMI validation pair must respect. The purpose is to adopt mature capability stacks and reserve OCM credit only for a residual developmental effect under matched information/tools/resources.

---

# 1. Domain pair

The first E3 pair is:

```text
formal mathematics / Lean 4
execution-verified coding / software tasks
```

Why these two first:

- both admit external machine-checkable receipts;
- their semantics are materially different enough to test whether GMI definitions survive a domain change;
- mature parent systems exist, making weak comparisons difficult;
- both can expose pre-solution search/proposal traces needed for K1-style causal mediation.

This protocol does **not** unlock #46. Mathematics execution remains governed by the lock/owner on #46. The present work defines common theory/measurement contracts only.

---

# 2. Formal mathematics parent stack

## M-P0 — Lean 4 kernel / pinned environment

Role: **external checker / execution substrate**, not cognition.

The verifier must bind:

```text
Lean version
mathlib/repository commit
imports
allowed axioms
statement digest
checker configuration
```

A kernel-accepted proof establishes only the formal proposition actually checked. It does not by itself establish that a natural-language statement was formalized faithfully.

## M-P1 — LeanDojo-v2 / Pantograph-class theorem interaction infrastructure

Role: **infrastructure** when used only for repository tracing, proof-state interaction and execution.

LeanDojo-v2 is the current LeanDojo path for new projects and supports repository tracing, lifelong dataset management, retrieval-augmented agents and Lean interaction:

- https://leandojo.org/leandojo
- https://github.com/lean-dojo/LeanDojo-v2

LeanDojo Benchmark 4 contains 122,517 theorem/proof records and exposes a `novel_premises` split intended to reduce easy proof/premise memorization.

Do not attribute LeanDojo tracing/RPC itself to OCM cognition.

## M-P2 — retrieval-augmented proving / ReProver-class parent

Role: **strong theorem-search parent**.

ReProver combines premise retrieval, tactic generation and proof search under LeanDojo:

- https://github.com/lean-dojo/ReProver

A GMI/OCM result must not claim novelty for premise retrieval, retrieval-conditioned tactic generation or best-first proof search.

## M-P3 — LeanAgent-class lifelong theorem parent

Role: **mandatory lifelong-learning parent**.

LeanAgent explicitly studies continual/lifelong formal theorem proving across 23 Lean repositories with curriculum ordering, an evolving theorem/proof database and progressive retriever training:

- https://arxiv.org/abs/2410.06209

Therefore the following are parent-owned at broad conceptual level:

```text
persistent theorem/proof database
continual retriever improvement
stability / backward transfer
lifelong proving across repositories
```

OCM residual, if any, must go beyond this with matched evidence for such things as verified applicability, proof-method abstraction, typed failure constraints, revision, complete lifecycle economics, cross-validation-regime transfer, or cheaper acquisition of future search capital.

## M-P4 — strong agentic formal prover reference

Role: **capability reference**, not necessarily a developmental parent.

Current agentic systems can solve very high fractions of public formal benchmarks. PutnamBench contains 672 Lean statements; current public agentic campaigns report near/full saturation under pinned Lean/checker stacks. Treat PutnamBench primarily as a calibration/reference estate, not as protected evidence of new developmental capability.

Official benchmark repository:

- https://github.com/trishullab/PutnamBench

A current reproducible agentic reference campaign is available at:

- https://github.com/humanfia/putnambench

Public benchmark success may reflect public-statement/model exposure and strong harness engineering. It is not sufficient for GMI developmental claims.

## M-P5 — harder/private/structural references

### FormalProofBench

Private graduate-level formal mathematics benchmark with natural-language problems paired with Lean statements; the reported best frontier foundation-model result in the release paper is 33.5%.

- https://arxiv.org/abs/2603.26996

Role: capability calibration and evidence that harder verified theorem proving remains unsolved.

### TheoremBench

Dependency-rich Lean4 benchmark built around nearly 100 classical theorems, with main/premised variants and theorem-level coverage/token-efficiency analysis.

- https://arxiv.org/abs/2606.09450

Role: structural/partial-progress calibration, especially useful for proof decomposition and premise/subtheorem behavior.

## M-P6 — autoformalization / statement-faithfulness parent family

Natural-language-to-Lean translation is a separate mature problem from proof search.

Required separation:

```text
formal statement compiles
!=
formal statement faithfully represents the user's theorem
```

A proof experiment beginning from natural language must record statement-faithfulness review/verification separately from Lean proof acceptance. A frozen foundation model may be used as the language/formalization donor under #369, but the identical donor must be available to matched parents.

---

# 3. Coding / software parent stack

## C-P0 — compiler/runtime/tests

Role: **external execution/checker substrate**.

Bind:

```text
repository commit / environment image
language/toolchain versions
allowed tools/network
build command
public and protected tests
resource/time limits
```

Passing a test suite establishes `TEST_SUITE_VERIFIED` only to the strength of that suite. It does not automatically prove full specification correctness.

## C-P1 — strong ordinary agent harness

Role: **minimum practical parent**.

The strongest comparison should normally include the same foundation model plus a conventional coding harness with shell/git/search/edit/test/retry capability.

This is the baseline already demanded by #208.

## C-P2 — memory / retrieval / reflection / skill-library parent product

Role: **mandatory parent product**, not optional weak baselines only.

At minimum permit parents powers equivalent to:

```text
persistent trajectory/retrieval memory
failed-attempt/reflection memory
explicit reusable skills/procedures
same tools/checkers
same foundation model
same context and lifetime information where not OCM-specific
```

### Repo-To-Skill / DisCo-class parent

Repo-To-Skill reports an AREX-Skill Library of 5,000+ verified skills distilled from 1,000 ML repositories, with fixed backbone/harness/budget gains on several research/code workloads:

- https://arxiv.org/abs/2609.02749

Therefore `extract reusable operational skill from repositories and improve later tasks` is not an OCM novelty.

### ContinualSkillBench parent

ContinualSkillBench evaluates sequential skill learning across five domains × 100 interconnected subtasks and finds sequential context often helps, explicit skills help selectively, and skill maintenance is not universally better than in-context adaptation:

- https://arxiv.org/abs/2608.03874

This is a strong negative/conditional parent for any claim that explicit persistent skills necessarily improve future coding.

## C-P3 — Terminal-Bench 2.1-class capability calibration

Terminal-Bench 2.1 provides current long-horizon terminal workloads and a strong-agent leaderboard:

- https://www.tbench.ai/leaderboard/terminal-bench/2.1

Role: public calibration / harness stress test. It is not by itself a protected lifelong developmental assay.

## C-P4 — SWE benchmark caution

SWE-bench Verified must not be treated as an uncontested frontier confirmatory set. OpenAI's February 2026 audit reports contamination and flawed tests and recommends no longer using it as a frontier launch measure:

- https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/

A July 2026 audit also reports substantial broken-task rates in SWE-Bench Pro:

- https://openai.com/index/separating-signal-from-noise-coding-evaluations/

Consequences:

```text
public SWE results = calibration/reference only unless task validity is independently audited
protected/private authored task families preferred for confirmatory development claims
all verifier defects retained as ASSAY_DEFECT / CANNOT_CHECK, never scored as model failure/success silently
```

#208's protected H1/H2 discipline remains authoritative for coding execution.

---

# 4. Matched parent arms for E3

Where compatible with each domain, the common ladder should include:

```text
P0  strongest direct foundation-model / domain prover or coding agent reference
P1  same donor + ordinary retrieval/memory
P2  same donor + reflection/failure feedback
P3  same donor + explicit skill/method library
P4  strongest integrated persistent parent product
R   RESET_OCM / reset developmental state
C   CONTINUED_OCM / persistent developmental state
S   SHUFFLED or cross-history control where semantically valid
```

Math-specific parent examples may instantiate `P4` with a LeanAgent/ReProver-style lifelong prover stack. Coding-specific `P4` may instantiate persistent memory + reflection + skills + same foundation model/tools.

A parent may use the strongest faithful mechanism appropriate to its own paradigm. Matched information/tools matter more than forcing identical internals.

---

# 5. What parents are allowed to solve for us

GMI/OCM should **adopt** parent strengths instead of rebuilding them.

Allowed donor ownership includes:

```text
fluent language understanding/generation
Lean interaction and kernel checking
premise retrieval
neural tactic/code proposal generation
best-first/tree search
compiler/interpreter/test execution
ordinary persistent retrieval memory
ordinary reflection/retry
ordinary explicit skill libraries
repository indexing
```

The treatment question is whether the governed persistent developmental state changes future cognition/acquisition in a way the strongest faithful parent product does not already explain at equal/lower burden.

---

# 6. Novelty is not required for theory establishment

The E3 question is not:

> Did ORION invent theorem proving or coding agents?

It is:

> Do the same GMI/HST state, morphology, burden, verification and developmental-capital definitions remain coherent and empirically useful across two materially different real validation regimes?

A scientifically successful E3 terminal may therefore be:

```text
GMI_SEMANTICS_TRANSFER_ACROSS_MATH_CODE
PARENT_PRODUCT_SUFFICIENT_FOR_DEVELOPMENTAL_EFFECT
OCM_K1_SUPPORTED_ONLY_IN_ONE_DOMAIN
OCM_K2_NOT_ESTABLISHED
DOMAIN_SEMANTICS_REQUIRE_THEORY_REVISION
CANNOT_CHECK_<reason>
```

Parent sufficiency strengthens the general theory if the parent mechanism cleanly instantiates it.
