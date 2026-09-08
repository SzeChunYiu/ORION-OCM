# Evolvability: useful axes, conditional bounds

8 September 2026. Targeted review of [PR150](https://github.com/SzeChunYiu/ORION-OCM/pull/150)
at `b051177e0670c71e2da657df8779eb60671dd385`. This does not replace its author’s
theory or reproduce the synthetic study. It identifies concrete qualifications
before those statements can become OCM scientific claims.

## Adopt the questions

The proposed three axes are useful: the affected dependency region, how costly
it is to discriminate relevant internal causes, and how difficult it is to find
an adequate repair. Explicit provenance alone does not make any of these cheap.
The lane correctly treats its results as theory/synthetic evidence, acknowledges
strong conventional parents and makes no universal OCM performance claim.

Use these axes when OCM encounters a recurring, measured obstruction. Compare
the same permissible interventions, observations, repair language and checking
costs. A conventional diagnostic or adaptive search method is an implementation
donor. A successful composition can be valuable without making each ingredient new.

The public theory’s neural self-improvement sources may supply abstract experimental
ideas or external comparators. OCM acquisition, policy, retrieval, search and generation
remain entirely mechanical. The source review here does not independently validate
the lane’s claims about those other papers.

## Qualify the probe bound

[Theory lines 190–212](https://github.com/SzeChunYiu/ORION-OCM/blob/b051177e0670c71e2da657df8779eb60671dd385/docs/spec/MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0_2.md#L190)
give the familiar Fano information requirement and then divide it by a per-probe
information bound. That step needs an explicit transcript/conditional assumption.
A marginal bound on each observation is insufficient.

Let independent fair bits be Z and R. Two observations are Y1=R and Y2=Z XOR R.
Each observation alone carries zero information about Z. Together they determine
Z exactly. Thus zero marginal information per probe does not imply that any number
of probes is useless. The [four-state enumeration](COUNTEREXAMPLES.json) verifies
the marginals, joint information, exact recovery and informative/uninformative controls.

A sufficient fixed-horizon formulation is: the action policy has no additional
access to Z beyond its recorded history, and each conditional transcript increment
I(Z;Yi | history, chosen action) is at most b. Chain-rule summation then bounds
the total information by nb. With uniform m-way causes and the usual informative
error range, Fano gives n ≥ ceil((log2(m)−h2(ε)−ε log2(m−1))/b), for b>0.
The example m=30, ε=.05 indeed requires 4.3775945887 bits, hence at least 44 fixed
probes at .1 bit per conditional increment. A random stopping-time or expected-cost
claim needs its own derivation; the integer ceiling cannot simply be carried over.

Scarlett and Cevher explicitly derive adaptive information bounds using the
transcript chain rule and appropriate observation assumptions. Their treatment of
optimization also makes the reduction from successful action to identification
explicit. See Lemma 3 and Theorem 11 of their [Fano guide](https://arxiv.org/pdf/1901.00555).
This supports a clarification of the proposed theorem, not a rejection of Fano.

## Distinguish repair from identifying the cause

[Theory lines 159–184](https://github.com/SzeChunYiu/ORION-OCM/blob/b051177e0670c71e2da657df8779eb60671dd385/docs/spec/MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0_2.md#L159)
label the summed lower-bound decomposition schematic. Before treating it as a
general cost law, specify why successful repair requires the stated identification
task and why the charged phases do not overlap.

Countermodel: 30 possible causes all admit the same registered repair. That repair
needs no diagnostic probe, even when identifying the exact cause would be costly.
This is an authored logical countermodel, not an OCM observation. The relevant
target can instead be a sufficient decision or equivalence class of causes with
the same admissible repair. Require a reduction from repair quality to identification
before charging the full-cause Fano bound. Diagnostic repair trials may also perform
search or verification; sum disjoint work units without charging the same work twice.

## Separate a useful distribution from a confident heuristic

[Theory lines 123–135](https://github.com/SzeChunYiu/ORION-OCM/blob/b051177e0670c71e2da657df8779eb60671dd385/docs/spec/MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0_2.md#L123)
allow posterior/proposal weights in χ=2^H(R|e). A heuristic concentrated on the
wrong repair has low entropy and poor performance. Specify whether this is a
calibrated posterior about successful repairs or merely a proposal distribution.
Measure successful-repair rank, actual evaluations, failures and evaluation cost;
include a matched shuffled-order control. Entropy alone does not establish useful
search reduction, even when the posterior is correct.

For example, one successful-repair hypothesis has probability 1−1/m; N=2^m others
share probability 1/m, with integer m≥2. Entropy is h2(1/m)+1≤2 bits, so χ≤4.
Yet even the optimal unit-cost sequential ordering has expected successful rank
1+(N+1)/(2m), which grows without bound. χ is an effective-diversity statistic,
not a general guarantee about expected repair-search cost. This analytic example
was independently reviewed; it is separate from the executed four-state check.

The true affected closure, an optimal diagnostic burden and an unknown successful-
repair distribution are theoretical objects. Define their observable estimators
and error before treating them as measured properties of the machine.

## Concrete disposition in this programme

Retain native serving adoption as the completed integration result. Continue to
typed acquisition and separated proof families with the strongest ordinary-derived-
lemma parent. Add internal diagnosis only when a concrete repeated failure gives
it an experimentally useful role. No speculative six-stage rebuild is required.

The two recent native-wrapper failures were diagnosed and repaired by AI engineers.
Their preserved records are development experience, not OCM self-discovery or
protected evaluation cases. Future machine repair must select and execute its
intervention itself under a fixed mechanism, with causal-use and cost evidence.

For a future diagnosis experiment, specify the decision target, allowed probes,
conditional observation model, candidate repair space, matched direct-repair parent,
quality criterion and disjoint lifetime costs. Include common-repair, ambiguous-
observation, misleading-priority and genuinely global-change cases. Those cases
can falsify the broad claim while revealing which mechanism needs improvement.

## Read and execution scope

[FETCHED.json](FETCHED.json) binds four files at the exact PR head. The theory’s
contents/heading inventory and selected lines 76–246,675–835,956–1086, PR body and
complete literature matrix were read. Registry/result excerpts were inspected;
their entire study source and results were not independently audited or reproduced.
The primary Fano paper’s abstract and the named relevant passages were read.

Only [evolvability_counterexamples.py](evolvability_counterexamples.py) executed,
on laptop billy with pinned Python 3.11.14, without OCM, a learner, corpus or native
checker. It binds the inspected theory SHA before four-state arithmetic. The
result records its own script digest. Findings are source qualifications and
mathematical counterexamples, not new empirical evidence about OCM.
