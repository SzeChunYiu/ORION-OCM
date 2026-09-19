# Parent ownership — gmi-833-ae-ae3-compression-learning-v1

Assimilation first. Every classical result below is used as given and none is
claimed novel.

## Literature parents

- **Kolmogorov complexity and the invariance theorem.** Kolmogorov 1965;
  Solomonoff 1964; Li & Vitányi, *An Introduction to Kolmogorov Complexity and
  Its Applications*, 4th ed., Springer 2019,
  doi:10.1007/978-3-030-11298-1. Uncomputability, upper semi-computability, and
  machine-dependence up to an additive constant are theirs. This tranche never
  computes `K`.
- **Minimum description length.** Rissanen 1978,
  doi:10.1016/0005-1098(78)90005-5; Grünwald, *The Minimum Description Length
  Principle*, MIT Press 2007, doi:10.7551/mitpress/4643.001.0001. The two-part
  code and its consistency theory are theirs.
- **Occam's razor / compression implies learning.** Blumer, Ehrenfeucht,
  Haussler & Warmuth 1987, doi:10.1016/0020-0190(87)90114-1. **This is the
  direction this tranche does not claim.** The AE3 rows ask for the converse
  failures, which is what is delivered.
- **PAC-Bayes.** McAllester 1999, doi:10.1145/307400.307435; Shawe-Taylor &
  Williamson 1997, doi:10.1145/267460.267466. The bound is transcendental and is
  never evaluated here; only the prior/code-length correspondence is used.
- **Bayesian coding.** MacKay, *Information Theory, Inference and Learning
  Algorithms*, CUP 2003. The negative-log-prior / code-length identity is his.
- **Kraft–McMillan inequality.** Kraft 1949; McMillan 1956,
  doi:10.1109/TIT.1956.1056818; Cover & Thomas, *Elements of Information
  Theory*, 2nd ed., Wiley 2006, doi:10.1002/047174882X. The feasibility test
  that defines the regeneration family is theirs.
- **The rate–distortion reading of task-relevant compression.** Shannon 1959;
  Tishby, Pereira & Bialek 1999, arXiv:physics/0004057. Notion `B` is their
  rate-at-fixed-distortion idea specialised to coordinate juntas.
- **No free lunch.** Wolpert 1996, doi:10.1162/neco.1996.8.7.1341. The fact that
  training fit alone constrains nothing off-sample without an inductive bias is
  his; AE3-4 exhibits an exact finite instance, not a new theorem.

## Repository parents (pinned by blob sha at `source_main`)

| parent | what it owns | pin |
|---|---|---|
| `gmi-833-theory-baseline-v1` | the section's baseline vocabulary | `201ee8e8…` |
| `gmi-833-foundation-v1` | the #833 formalization scope | `c0c574c4…` |
| `gmi-833-ae-ae1-structure-separation-v1` | task-relative exploitable structure and the accessibility separations | `ceb77f5b…` |
| `gmi-833-ae-ae10-usable-information-v1` | `U(W,T,R)` and the budgeted achievability gap | `69aafebe…` |
| `gmi-833-finite-candidate-space-v1` | the finite program-space enumeration discipline | `4086d6be…` |

## What is NOT claimed novel

Uncomputability of `K`; the invariance theorem; MDL; Occam bounds; PAC-Bayes;
Kraft–McMillan; rate–distortion; no free lunch; the general observation that
compression and generalization can come apart.

## The residual contribution

Three things, all small and all finite:

1. a **registered, Kraft-checked finite coding-language family** in which every
   code length is an exhaustively computed integer, so that "shortest
   description" is a decidable object rather than a gesture at `K`;
2. the **three-notion separation census** on that family — all six ordered
   pairs shown non-determining by exact counts rather than by example alone;
3. the **measured invariance boundary**: which verdicts survive independent regenerations, with an
   exact predicate where one exists and an enumerated exception set where it
   does not. The literature's invariance theorem is asymptotic and up to an
   additive constant; at this finite scope the honest answer is that two of the
   three verdicts are conditional, and that is what the receipt says.
