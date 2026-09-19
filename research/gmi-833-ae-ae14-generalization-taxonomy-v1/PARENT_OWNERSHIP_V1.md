# AE14 parent-ownership disclosure

Assimilation-first: the parent work below is absorbed and credited, and the
residual contribution of this tranche is stated afterwards. **Nothing in the
list is claimed novel.**

## Strongest parents

| parent | what it owns | citation |
|---|---|---|
| Compositionality and systematicity | the argument that a system can match a data distribution and still fail to recombine known parts, and that recombination is the diagnostic | Fodor and Pylyshyn, "Connectionism and cognitive architecture: a critical analysis", Cognition 28 (1988) 3-71. doi:10.1016/0010-0277(88)90031-5 |
| Compositional generalization benchmarks | matched in-distribution accuracy with divergent recombination behaviour, and the taxonomy of generalization axes | Lake and Baroni, ICML 2018, arXiv:1711.00350; Hupkes, Dankers, Mul and Bruni, JAIR 67 (2020) 757-795. doi:10.1613/jair.1.11674 |
| Analogy as structure mapping | that analogy is a relation-preserving map, not proximity in a representation space | Gentner, "Structure-mapping: a theoretical framework for analogy", Cognitive Science 7 (1983) 155-170. doi:10.1207/s15516709cog0702_3; Hofstadter, in *The Analogical Mind*, MIT Press (2001) |
| Interpolation versus extrapolation | that the interpolation regime is a statement about the convex position of a query relative to the training set, and is rarer than assumed | Balestriero, Pesenti and LeCun, "Learning in high dimension always amounts to extrapolation", arXiv:2110.09485 (2021) |
| Memorization versus generalization | that exact fit on the training set is compatible with chance behaviour off it, and that some memorization is necessary | Zhang, Bengio, Hardt, Recht and Vinyals, ICLR 2017, arXiv:1611.03530; Feldman, STOC 2020. doi:10.1145/3357713.3384290 |
| Learning theory for bounded classes | that what a hypothesis class can realize is decided by the class, not by the optimizer | Valiant, CACM 27 (1984) 1134-1142, doi:10.1145/1968.1972; Blumer, Ehrenfeucht, Haussler and Warmuth, JACM 36 (1989) 929-965, doi:10.1145/76359.76371 |
| Juntas and decision-tree complexity | the lower bounds that make a bounded-arity class genuinely unable to compute a function of more coordinates | Mossel, O'Donnell and Servedio, JCSS 69 (2004) 421-434, doi:10.1016/j.jcss.2004.04.002; O'Donnell, *Analysis of Boolean Functions*, Cambridge University Press (2014). doi:10.1017/CBO9781139814782 |
| Kraft inequality and description length | prefix-free integer code lengths and the model-class-relative reading of compression | Kraft, MIT MSc thesis (1949); Rissanen, Automatica 14 (1978) 465-471, doi:10.1016/0005-1098(78)90005-5; Grunwald, *The Minimum Description Length Principle*, MIT Press (2007). doi:10.7551/mitpress/4643.001.0001 |
| Horn clauses and forward chaining | the immediate-consequence operator, its least fixpoint, and derivation depth | van Emden and Kowalski, "The semantics of predicate logic as a programming language", JACM 23 (1976) 733-742. doi:10.1145/321978.321991 |

## What is NOT claimed novel

- That memorization, interpolation, extrapolation, systematic generalization,
  analogy, planning and reasoning are distinct notions.
- That a bounded-arity class cannot compute a function of more coordinates.
- That in-distribution accuracy can be matched while recombination behaviour
  differs.
- That analogy is a relation-preserving map rather than proximity.
- That description length is defined relative to a model class and a code.
- That the least fixpoint of a Horn system is reached by iterating the
  immediate-consequence operator.

## Residual contribution of this tranche

1. **One consistent finite roster** on which all seven modes are exact
   predicates over `(task, learner class, training support)` and are evaluated
   simultaneously in exact rational arithmetic, with a closed-form route and an
   independently written enumeration oracle agreeing on every value.
2. An **exhaustive class enumeration** that settles the reducibility question by
   decision rather than by survey: every function constant off the support,
   all 70 depth-2 juntas, all 32 affine functionals and all 520 block-modular
   compositions are checked, and the exact best attainable accuracy of each is
   reported against a composition learner that is exact.
3. A **matched pair with exactly equal Bayes predictive accuracy** and exactly
   opposite recombination behaviour (`0` against `1`), and a second matched pair
   with **exactly equal integer description length** and different exact transfer
   (`3/8` against `3/4`).
4. A **prospectively frozen mechanism predictor** scored against a registered
   uniform null and, separately, against an exhaustive family sweep over every
   function of each structure type — the sweep, not the seven chosen instances,
   is what makes the predictor's `7/7` evidence rather than a fit.
5. A **machine-checked refusal** of the registered blanket promotion, with the
   guard checker validated in both directions, and a **reported refutation** of
   the package's own prediction `AE14-P1` together with the implication
   certificate that explains it.

## What this tranche does not earn

No neighbouring AE row of issue comment 5692689542 and no row of the #833 issue
body. No statement about systems outside the registered finite scope, about
`n > 4`, about budgets other than the registered ones, or about which model class
a real system should use. The registered promotions listed in `FREEZE_V1.md`
remain refused.
