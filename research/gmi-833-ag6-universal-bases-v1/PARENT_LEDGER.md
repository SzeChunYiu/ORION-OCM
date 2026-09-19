# Parent ownership ledger — `gmi-833-ag6-universal-bases-v1`

Assimilation-first. Every parent below is absorbed, not defended against. Nothing in this list is
claimed novel by this tranche. Each DOI was resolved against Crossref before this file was written;
where a work is a book with no DOI, that is stated rather than a DOI being invented.

## Combinatory / rewrite

| work | identifier | what it owns |
|---|---|---|
| M. Schönfinkel, *Über die Bausteine der mathematischen Logik*, Mathematische Annalen **92** (1924) 305–316 | `10.1007/BF01448013` | the combinator idea and the elimination of bound variables; the ancestor of the `S`/`K` basis |
| H. B. Curry, *Grundlagen der Kombinatorischen Logik*, American Journal of Mathematics **52** (1930) 509 | `10.2307/2370619` | combinatory logic as a formal system; bracket abstraction |
| D. A. Turner, *Another algorithm for bracket abstraction*, Journal of Symbolic Logic **44** (1979) 267–270 | `10.2307/2273733` | optimized bracket abstraction; the reason a naive translation is not the only accounting |
| A. Church and J. B. Rosser, *Some properties of conversion*, Transactions of the AMS **39** (1936) 472–482 | `10.1090/S0002-9947-1936-1501858-0` | confluence; uniqueness of normal forms |

**Not claimed here.** That combinatory logic is Turing universal. That `S` and `K` suffice to define
every computable function. Both are Schönfinkel's and Curry's, and this package's registered
universality claim is strictly weaker — it is realization of 256 named finite transducers.

## Cellular / local

| work | identifier | what it owns |
|---|---|---|
| J. von Neumann (ed. A. W. Burks), *Theory of Self-Reproducing Automata*, Univ. of Illinois Press 1966 | **book, no DOI** | cellular automata as a computational substrate; self-reproduction |
| E. F. Codd, *Cellular Automata*, Academic Press 1968 | **book, no DOI** | reduction of von Neumann's cell state count; construction-universality |
| A. R. Smith III, *Simple Computation-Universal Cellular Spaces*, Journal of the ACM **18** (1971) 339–353 | `10.1145/321650.321652` | the standard construction simulating a machine by a local rule |
| N. Margolus, *Physics-like models of computation*, Physica D **10** (1984) 81–95 | `10.1016/0167-2789(84)90252-5` | block/partitioned cellular update as a computational model |
| M. Cook, *Universality in Elementary Cellular Automata*, Complex Systems **15** (2004) 1–40 | `10.25088/ComplexSystems.15.1.1` | universality of Rule 110, the example AG6's own text cites |
| G. A. Hedlund, *Endomorphisms and automorphisms of the shift dynamical system*, Mathematical Systems Theory **3** (1969) 320–375 | `10.1007/BF01691062` | the Curtis–Hedlund–Lyndon characterization: cellular automata are exactly the shift-commuting continuous maps. This is what makes "is your update really local?" a checkable question, and route B runs the automaton in exactly that block-map form |

**Not claimed here.** That any cellular automaton constructed in this package is Turing universal.
Rule 110's universality is Cook's.

## Register / counter

| work | identifier | what it owns |
|---|---|---|
| M. L. Minsky, *Computation: Finite and Infinite Machines*, Prentice-Hall 1967 | **book, no DOI** | register and counter machines; two-counter universality |

**Not claimed here.** Universality of counter machines.

## Inside this corpus

| package | pinned object | what it owns |
|---|---|---|
| `gmi-833-g0-register-core-v1` | `RESULT_V1.json` blob `5d2948b9c04c84a46f6625e043753a489895478f` | the register/counter basis, the five instruction classes, and the 256-machine × 15-word × 3840-comparison Mealy census this package re-derives and must agree with |
| `gmi-833-ag5-extension-lowering-v1` | `RESULT_V1.json` blob `8f115342ab64a9a85306442ab0811e1c564d709c` | the 21-operator ledger with 0 generators, and the measured structure-dependence of `NEIGHBOR_UPDATE` (680/756) against `POINTWISE` and `GLOBAL_BROADCAST` (0/756) — the parent signal for the cellular basis's locality measurement |
| `gmi-833-ag2-signature-free-syntax-v1` | `RESULT_V1.json` blob `7e2b6b53bdd96c4243de67581be1626ee309ef04` | signature below grammar; the 1/2/11/121 term counts; the 121→33 class collapse; the randomized-semantics null design this package reuses |
| `gmi-833-ag1-descent-stack-v1` | `RESULT_V1.json` blob `530f189a2dac44bf19fe5405f28406365b1a7172` | the `F0..F9` layer DAG, `G0` at `F4`, first divergence at `F6` |
| `gmi-833-aj12-foundation-substrate-relativity-v1` | `RESULT_V1.json` blob `8ae1ed5c051d07d2caff1366eb3bae31bba65862` | formalization-style and substrate relativity; the discipline that a result must not rest on one presentation of the finite objects |
| `research/machine-intelligence-morphogenesis-v1/PHASE_LAW_V1.md` | blob `45c3069e0bafad79de0b6b4f2572ea4f24a38a13` | the shape of the law tested in AG6B-7: a capability/resource Pareto frontier, with the price and capability treatment frozen prospectively |

## The residual contribution of this tranche

Two things, and nothing wider.

1. **The two missing bases, built rather than cited.** AG6 asks for at least three radically
   different universal low-level bases *at bounded executable scope*. Only the register/counter one
   existed on `main`. A combinatory/rewrite basis and a cellular/local basis now exist, each
   realizing the same 256 registered machines on the same 15 words with 0 mismatches, under two
   materially independent routes.

2. **The charged comparison on one frame, and the statement that makes its verdict attributable.**
   A comparison run on three different accountings measures the accountings. This package holds the
   task set, the step definition, the size definition, the budget rule and the capability battery
   fixed, declares exactly what varies, and then observes that the capability/cost frontier differs
   across the three bases. The frontier depends on cost only through its within-basis ordering, so
   it is invariant under every *uniform* strictly increasing normalization — checked executably for
   three of them — and therefore the disagreement cannot be attributed to the accounting. The
   invariance class is stated precisely, and the stronger reading is a registered forbidden
   promotion.

Neither the notion of a capability/resource frontier, nor combinatory logic, nor cellular automata,
nor register machines, nor Kendall's tau, is claimed as this tranche's own.
