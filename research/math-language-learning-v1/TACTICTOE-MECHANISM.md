# TacticToe: a concrete non-neural proof-search donor

Primary-source reading, 2026-09-08. This note proposes future comparisons;
it changes neither the registered unary experiment nor its evidence.

## What the sources establish

The 2021 TacticToe paper records successful goal–tactic examples, uses explicit
term/type features and distance-weighted nearest neighbours to rank tactics and
theorem arguments, and guides Monte Carlo tree search with those predictions.
It also generalizes tactic arguments and removes redundant tactic choices.
The older A* implementation and the later MCTS implementation are distinct
versions. These mechanisms provide an existing example of learning proof-search
guidance without a neural network.
[Author-hosted paper](https://cl-informatik.uibk.ac.at/images/publications_pdf/2021/tgckjurkmn-jar21.pdf)

HOL4's documented `ttt` entry point returns a generated proof script. Recording
training tactics is a separate potentially expensive step; missing recorded tactics,
timeouts and reconstruction failures are explicit failure modes.
[Official command documentation](https://hol-theorem-prover.org/kananaskis-14-helpdocs/help/Docfiles/HTML/tacticToe.ttt.html)

The current upstream README distinguishes ordinary `ttt` from optional `ttt_tnn`
using a tree neural network. It describes cache identities containing theory,
script, ancestry and compatibility information, plus stale-data invalidation.
Therefore an OCM integration must pin the implementation and select the
non-neural route explicitly; the whole modern repository cannot simply be called
neural-free. The documentation and current branch also describe different cache
generations; an old prebuilt archive is not automatically compatible.
[Upstream README](https://raw.githubusercontent.com/HOL-Theorem-Prover/HOL/develop/src/tactictoe/README)

The journal publication is in *Journal of Automated Reasoning* 65, 257–286 (2021).
Its historical benchmark scores do not establish a present matched OCM comparison.
[Publication record](https://cl-informatik.uibk.ac.at/research/publications/publications-2021/tactictoe-learning-to-prove-with-tactics)

## What OCM should borrow — proposed mapping

| Donor mechanism | OCM implementation candidate | Required distinction |
|---|---|---|
| Goal–tactic recording | Persist checked episode traces as method-selection examples | Having a recorded tactic is different from inventing a new method. |
| Explicit feature retrieval | Inverted indexes over typed goal features and admissible methods | Similarity ranks candidates; it supplies no warrant. |
| Goal-conditioned argument selection | Bind a generic method to retrieved, scoped theorem objects | Actual applicability and output checking remain authoritative. |
| Guided tree search | Search over goal decompositions with explicit heuristic statistics | Search scores remain separate from correctness and scope. |
| Redundancy removal | Retire dominated proposals while retaining their provenance | A locally redundant method may matter under a changed library. |
| Versioned recording cache | Reuse checked derived data within a verified immutable snapshot | Dependency changes must invalidate precisely affected entries. |

An OCM adaptation should first expose one ordinary primitive-search parent and
one equally adaptive parent with the same traces, features, methods, theorem
library, restart policy and compute. A faithful HOL4 TacticToe run is a separate
upstream-system comparator. Reimplementing a few ideas in Python is an adapted
donor, not an executed TacticToe baseline.

## Small falsifying experiment before large mathematics

Freeze a modest theorem family with dependency-ordered training and held-out
goals. Exclude the target proof and downstream facts that reveal it. Let both
adaptive arms record the same permitted proof episodes; charge recording,
feature/index construction, failed attempts, proof reconstruction and storage.
After restart, compare checked solves and total cost against the primitive parent.

Disable only the recorded method-selection information in a paired diagnostic;
preserve the same tactics, theorem access, resource allocation and verifier.
Then grow irrelevant recorded experience at fixed relevant structure and measure
retrieval, ranking, checking, expansions and maintenance work. This separates
benefit from learning, benefit from ordinary indexing, and any additional OCM
effect. A larger library that makes lookup linear fails the intended scaling test.

For math-to-language transfer, first reuse the same checked goal decomposition
and support graph through a supplied controlled-language parser and realizer.
Measure a new language presentation separately from a new semantic problem.
Tactic selection itself does not supply discourse planning, lexical knowledge or
open-ended conversational understanding. Those need their own tasks and evidence.

## Immediate decision

Borrow explicit trace-based selection and version-aware caching as engineering
mechanisms. Do not add a HOL4 installation to the current unary repair. First fix
the diagnosed acquisition bottleneck, then run this bounded proof-search study
before attempting FLT-scale claims. This note makes no novelty or performance claim.
