# Primary mechanisms used by the theory map

This is parent subtraction, not an exhaustive history.
The primary pages/papers below were inspected on 2026-09-13.
GMI's local proof sources and exact revisions are in
[SOURCE_BINDINGS_V1.json](SOURCE_BINDINGS_V1.json).
An adaptation inherits only the assumptions and conclusions actually stated.

## P1 — Bayesian updating

[Bissiri, Holmes and Walker (2016), §§1–2](https://arxiv.org/pdf/1306.6430)
form a posterior by minimizing expected loss plus KL to a supplied prior;
self-information loss recovers ordinary Bayes.
Formal O3 is the elementary finite positive-likelihood instance.
REAL3's hidden-state update additionally uses total probability and Bayes;
neither identity establishes correctness of the latent model.
This is a faithful finite specialization, not a new updating principle.

## P2 — zero-error information and assistance

[Cubitt, Leung, Matthews and Winter, §§II–IV](https://arxiv.org/pdf/1003.3195)
distinguish zero-error communication from exact channel simulation and keep
shared randomness, entanglement and non-signalling resources separate.
This develops Shannon's zero-error program and is a direct technical parent
for GMI's explicit-assistance boundaries.
Semantic adequacy changes the required decoder relation; no Shannon theorem
claims that mutual information alone settles every task's exact adequacy.
Do not transfer one-shot, asymptotic, unassisted and assisted conclusions
between registers without their matching premises.

## P3 — concentration and learning

[Blumer et al. (1987)](https://doi.org/10.1016/0020-0190(87)90114-1)
connect efficiently obtained short consistent hypotheses to PAC learning.
The publisher abstract was accessible; the full publisher text was blocked.
Formal L1–L3 show their own Hoeffding/union-bound proof for bounded loss and
countable weighted classes. That is an adapted agnostic formulation, not an
assertion that Blumer's original theorem contains this exact optional-time bound.
The [formal learning note](../gmi-formal-derivation-v1/LEARNING.md) also credits
Littlestone–Warmuth and Freund–Schapire for its full-information expert learner.
Risk, regret, realizability and runtime are different quantities.

## P4 — what PAC-Bayes adds

[Seeger (2002), Theorem 1 and Appendix A](https://www.jmlr.org/papers/volume3/seeger02a/seeger02a.pdf)
gives a simultaneous bound for data-selected posterior distributions Q
under a fixed prior P and IID sampling, using KL(Q||P).
The proof combines an exponential moment with a change-of-measure inequality.
It controls the Gibbs risk specified there; deterministic majority-vote
risk is a further question.
Formal L2's log(1/p_h) bound controls individual countable hypotheses.
A code penalty is already available, while a general posterior-KL
specialization is not a conclusion of that proof.
The prior specifies the comparison measure, not a claim that nature sampled
the true hypothesis from it.

## P5 — control, termination and model transfer

[Bertsekas (2020), §§II–V](https://arxiv.org/html/1711.10129v2)
separates costs of proper policies and unrestricted policies in stochastic
shortest paths. Bellman equalities alone can admit unsuitable solutions.
VOC adopts the finite deterministic viable-domain specialization.
[Lobel and Parr (2024), §3 and Appendix B](https://arxiv.org/html/2406.16249v1)
derive simulation bounds through surviving overlap of model trajectories.
FMT adapts this mechanism with stopped-state/terminal charges and one
simultaneous model-confidence event.
CMP5 supplies a separate infinite-horizon statement under common initial law,
common history policy, summable errors or discounting; it supplies no sure
safety inference from a constant positive model error.

## P6 — causal identification

[Pearl (2009), §§2–3](https://ftp.cs.ucla.edu/pub/stat_ser/r350.pdf)
distinguishes statistical information, causal assumptions, identification
and estimation. Back-door adjustment is one sufficient identifying route.
CAU's finite SCM fiber formulation is a faithful specialization; its corrected
supported controls are examples, not a new general identification algorithm.
Randomized assignment identifies the stated effect only when the required
surgical and no-other-mechanism-change assumptions hold.
An experimental invoice is not evidence that those assumptions hold.

## P7 — active decisions and costly deliberation

[Javdani et al. (2014), §§2–3](https://proceedings.mlr.press/v33/javdani14.pdf)
use overlapping decision regions: tests need to locate a successful decision,
not always a unique hypothesis. Their objective averages test count under a
supplied prior and their approximation guarantee belongs to their HEC method.
TDA adapts the adequacy structure to an exact worst-case/retention register;
it does not inherit HEC's guarantee merely by using the same hypergraph.
[Hay et al. (2012), §§2–3, Theorem 5](https://arxiv.org/pdf/1207.5879)
already charge computation in a Bayesian metalevel MDP and bound expected
computation count using value of perfect information.
VOC's deterministic path bound is a different, narrower conclusion.
Nonmyopic computation selection also predates GMI in Russell–Wefald.

## P8 — approximation versus machine realization

[Cybenko (1989), Theorem 2](https://papers.baulab.info/papers/Cybenko-1989.pdf)
gives density in continuous functions on a compact cube for continuous
sigmoidal activation, with unrestricted network size/weights.
The linked file is a copy of the original paper, not a secondary summary.
This does not give exact arbitrary-function realization, trainability,
bounded physical costs or neural necessity.
Formal REAL2 instead constructs a particular finite-state recurrent
threshold/ReLU encoding under its explicit arithmetic register.
Formal O4 is the chain rule on a finite differentiable DAG; neither parent
makes differentiation exact for an arbitrary quantized VM instruction.
