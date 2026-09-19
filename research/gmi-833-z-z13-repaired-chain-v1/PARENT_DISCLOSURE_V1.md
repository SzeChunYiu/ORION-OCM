# Z13-P3 — parent ownership disclosure

Assimilation first: the machinery below is not ours, and saying so is what makes
the residual visible.

## What is not claimed novel

- **Lagrangian scalarisation over a lower convex envelope.** That a linear
  budget price selects the vertices of the lower convex envelope of the
  resource-error profile, and that the selection interval of a level is bounded
  by its two marginal differences, is Everett's generalized Lagrange multiplier
  theorem and its multi-objective descendants. `IC-1` (the Marginal Value
  Principle of `gmi-833-z-z1-master-principle-v1`, blob `11012f8f`) is the
  programme's registration of that fact; the envelope mathematics is
  parent-owned and is said so in every named result. Parents: Everett, H.,
  "Generalized Lagrange multiplier method for solving problems of optimum
  allocation of resources", *Operations Research* 11(3):399-417, 1963,
  doi:10.1287/opre.11.3.399; Geoffrion, A. M., "Proper efficiency and the theory
  of vector maximization", *J. Math. Anal. Appl.* 22(3):618-630, 1968,
  doi:10.1016/0022-247X(68)90201-1; Berger, T., *Rate Distortion Theory*,
  Prentice-Hall, 1971.
- **Finite-memory prediction of delayed inputs and its Markov analysis.** The
  one-bit chain `pi_k = (1 - pi_{k-1})/2` and the resulting geometric
  convergence of the delay-2 error to `1/3` are elementary finite-memory
  learning; the qualitative fact that fewer state bits than the delay force a
  positive error floor is the content of the finite-memory literature. Parent:
  Hellman, M. E. and Cover, T. M., "Learning with finite memory", *Annals of
  Mathematical Statistics* 41(3):765-782, 1970, doi:10.1214/aoms/1177696956.
- **Exhaustive finite-state machine minimisation with per-address majority
  outputs.** Choosing the error-minimising output table for a fixed next-state
  function by majority vote per address is the 0-1 loss Bayes rule on a finite
  partition. Parents: Mealy, G. H., "A method for synthesizing sequential
  circuits", *Bell System Technical Journal* 34(5):1045-1079, 1955,
  doi:10.1002/j.1538-7305.1955.tb03788.x; Moore, E. F., "Gedanken-experiments
  on sequential machines", *Automata Studies*, Princeton University Press,
  1956, pp. 129-153.
- **Finite-size drift of a selection boundary.** That a model-selection
  boundary computed on a finite horizon depends on the horizon is the
  finite-size-scaling commonplace of statistical physics; nothing about the
  existence of such drift is new. Parent: Fisher, M. E. and Barber, M. N.,
  "Scaling theory for finite-size effects in the critical region", *Physical
  Review Letters* 28(23):1516-1519, 1972, doi:10.1103/PhysRevLett.28.1516.
- **The universe, the window convention, the copy-then-reset class and the
  `L = 4` numbers.** All belong to the adjudicated parent
  `research/gmi-833-z-z13-adjudication-v1` (branch `research/833-sec-z4`,
  PR #1052, **not on `main`** at `source_main`): `ZA-1` (`5/16` at `L = 4`,
  four attaining functions), `ZA-5` (repaired ecology `4*p1 <= p2`), `ZA-6` (the
  minimisers are `F_MEALY_PURE`), and `REPAIRED_ECOLOGY_FREEZE_V1.md` (blob
  `5bc0597a`). This package is the "later lane" that freeze was written for.
- **The retired expectation.** `Z13-P1` belongs to
  `research/gmi-833-z-z13-property-prediction-freeze-v1` (blob `25febfa6`,
  commit `0cc617fc`, merged in PR #1039). It is cited as the registered expert
  expectation the new prediction contradicts and is never re-scored here.
- **The two-level law.** `lambda* = eta*p*R0` is `DS-5` of
  `gmi-833-z-z6-discrimination-v1` (blob `35ab5d2b`, merged in PR #1039); the
  zero-drift statement of the two-level boundary in `L` is `CP-4` of
  `gmi-833-z-z5-critical-phenomena-v1` (PR #1034).

## The residual contribution of this tranche

1. A **prospective** prediction from the repaired (marginal) law — a closed
   form for the one-bit delay-2 floor as a function of `L`, its exact attaining
   set, both marginal thresholds, the niche rule and a five-world probe table
   including one world that flips with `L` — frozen at `f9301396` before any
   `L = 5` or `L = 6` enumeration existed, and confirmed exactly on both routes
   (`ZP-1`..`ZP-4`).
2. The first `L`-dependent collapse boundary in this programme
   (`p1 = p2*(4R(L) - 1)`: `1/4` at `L in {4, 5}`, `9/32` at `L = 6`), with the
   exhibited flip world `(0, 17/81, 64/81)` as the witness that the retired
   `p2 = 0` law and the two-level zero-drift statement cannot express it
   (`ZP-4`).
3. A Route B that never enumerates a sequence (exact Markov propagation),
   re-verifies the parent's two lemmas by brute force over `16,777,216` joint
   candidates before using them, and locates the niche by scanning rather than
   differencing (`ZP-2`).
4. An honest null: the frozen collapse-rule null failed its uniqueness clause
   on the frozen grid (`9/200` perfect); the failure is attributed to the grid,
   repaired by a pre-committed amendment with two discriminating worlds whose
   outcomes were predicted before enumeration, and the first outcome stays on
   the record (`FAILED_PREDICTION_REGISTER_V1.json`).

None of these is a new theory. They are exact facts about a registered finite
universe and a registered prediction that was made, then tested.

## What this tranche does not do

It does not replicate independently (Route B is same-author; `M5` has zero
instances in this corpus); it does not claim W4 status; it does not claim a new
architecture family; it does not extend beyond `L in {5, 6}`, `b <= 2`, uniform
binary inputs; it does not re-score `Z13-P1`; it does not close any row whose
evidence it does not reach (`Z13` row 11, `Z16` rows 4 and 6 stay open).
