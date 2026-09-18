# AE4 parent-ownership disclosure v1

## What is parent-owned and is NOT claimed novel

| result | parent | citation |
|---|---|---|
| the objective `I(T;X) - beta I(T;Y)` and the whole relevance/compression tradeoff | the information bottleneck | Tishby, Pereira & Bialek 1999, arXiv:physics/0004057 |
| hard-partition encoders and the deterministic variant of that objective | the deterministic information bottleneck | Strouse & Schwab 2017, doi:10.1162/NECO_a_00961 |
| the capacity-versus-distortion frontier | rate-distortion theory | Shannon 1959; Berger 1971; Cover & Thomas 2006 |
| the coarsest partition sufficient for `Y` | minimal sufficient statistic | Lehmann & Scheffé 1950, doi:10.1214/aoms/1177729695 |
| retaining what *action* needs rather than what *prediction* needs | information theory of decisions and actions | Tishby & Polani 2011, doi:10.1007/978-1-4419-1452-1_19 |
| paying a price for attention/representation capacity | rational inattention; bounded rationality | Sims 2003, doi:10.1016/S0304-3932(03)00029-1; Simon 1955, doi:10.2307/1884852 |

The entire information-theoretic apparatus of this row is parent-owned. The
crosswalk in the receipt maps **every** symbol this package writes onto one of
the entries above.

## The named residual of this tranche

1. **A decision procedure for entropy order that evaluates no logarithm.**
   Every entropy is carried as an exact rational combination of prime
   logarithms, and the order of two such values is decided by the sign of
   `prod_q q^(D c_q) - 1` — a comparison between two integers. This is
   elementary, but it is what makes an exhaustive `4140`-encoder IB
   optimisation over seven worlds and a nine-point tradeoff ladder a set of
   *exact* statements rather than floating-point ones, and it is what lets the
   receipt print `H(Y) = 2*log2(2) - 3/4*log2(3)` rather than `1.4056`.

2. **The threshold, not the slogan.** The parents say the IB optimum trades
   compression against relevance. What is measured here is the exact tradeoff
   value at which the GMI minimal predictive state *becomes* an IB optimum, for
   each registered world — and that it is `1` for six of them and `6` for the
   noisy channel. Below the threshold the optimum is a strict coarsening; the
   identification is true only above it.

3. **A negative earned by exhaustion, kept.** The counterexample kind this
   package first went looking for — an IB optimum *incomparable* with the
   minimal predictive state — **does not exist** at this scope. Every support
   size to 6 was searched exhaustively over all partitions, all deterministic
   targets and the whole ladder, and the count is `0`. The negative is reported
   with its search scope, the resulting structural statement (every IB optimum
   is `EQUAL` to `T_GMI` or a strict coarsening of it) is labelled a
   **conjecture** beyond the searched range, and the revival that followed is
   recorded rather than presented as the original plan.

4. **Five retention mechanisms, each with a witness or a declared absence.**
   Future-task uncertainty, transfer, revision, causal intervention and
   verifier need are separately instantiated, so *some information must be kept
   although it is irrelevant now* becomes five distinct checkable statements
   instead of one piece of prose.

## What is explicitly NOT claimed

The IB optimum here is over **deterministic** encoders.
`IB_OPTIMUM_OVER_STOCHASTIC_ENCODERS_PROVED` is a registered forbidden
promotion and the receipt carries `stochastic_encoders_optimised: false` as a
checked field. No continuous or infinite-support extension. No rate-distortion
theorem is reproved. No energy or wall-clock price is measured. No architecture
or morphology selection law.

## A correction to the section map, declared before implementation

`AE_SECTION_MAP_V1.md` says the AE4 package "needs AE3's coding-language
registry". Read against AE4's eight row texts that dependency is **not
load-bearing**: every row is an IB/rate-distortion obligation and none consumes
a prefix code, a program length or a description-length registry. The
correction is in `FREEZE_V1.md`, written before any implementation blob existed,
and it is the second instance of the same defect the morphology-sweep lane
found — a map claim about what a package needs that does not survive opening
the rows.
