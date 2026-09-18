# AC crosswalk addendum v1 — `gmi-833-ac-lanes-harness-v1` (issue #833, section AC)

The frozen parent `GMI_TERMINOLOGY_CROSSWALK_V2.md`
(blob `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054`) **owns** all 48 rows. This
file supplies only what the AC audit measured as missing, in the parent's own
columns and vocabulary. It renames nothing and overrides nothing.

**Citation status is inherited from the parent's own convention.** Every
reference below is `CITE-TF` — a canonical field anchor entered from field
knowledge and **not** checked against a live source during this tranche. AC05
("maintain citation-backed definitions rather than model-generated
definitions") is therefore **not** earned by this file and is not claimed. What
AC06 asks for and what is supplied here is the *presence of an
earliest-or-strongest parent record per idea*, with its verification status
disclosed.

## Part 1 — AC04 term-choice rules for the two rows that state none

AC04: *"When terminology differs across fields, state the cross-field synonyms
and choose one primary paper term."* Two crosswalk rows offer a menu of
cross-field synonyms with no instruction for choosing among them: their
migration rule is a bare `PAPER-RENAME` with no parenthetical. The parent's own
convention is that the parenthetical carries the term-choice rule, so these two
rows state no primary term. The rules below close that, in the parent's format.

| # | legacy GMI term | primary paper term | term-choice rule (migration parenthetical supplied here) |
|---|---|---|---|
| 23 | niche | **region of instance space** | PAPER-RENAME (primary term: *region of instance space*; use *operating regime* only when the region is indexed by a resource or control parameter rather than by instances, and *domain of competence* only when quoting the algorithm-selection literature. Never the ecological reading without a stated instance space.) |
| 33 | parent subtraction | **comparison to strongest baselines** | PAPER-RENAME (primary term: *comparison to strongest baselines*; use *subsumption analysis* when the parent is shown to entail the result, *reduction* when an explicit reduction is exhibited, and *ablation* only for a component removed from the authors' own system. Never *parent subtraction* in paper-facing text.) |

## Part 2 — AC06 earliest/strongest parent records for the eight rows that carry none

AC06: *"Record earliest/strongest known parent for each mathematical idea."*
Eight of the 48 crosswalk rows carry a citations cell with no dated or authored
anchor — they cite the AB audit list, a house discipline, or a sibling artifact
of the same tranche, none of which is a parent. A parent record is supplied for
each below.

| # | legacy GMI term | earliest / strongest known parent | why it is the parent | status |
|---|---|---|---|---|
| 16 | theorem typing | Hales, T. C., "Formal proof", *Notices of the AMS* 55(11), 2008 | draws the analytic-proof versus computer-assisted-check line that theorem typing encodes | CITE-TF |
| 19 | predict | Stone, M., "Cross-validatory choice and assessment of statistical predictions", *JRSS B* 36(2), 1974; Geisser, S., "The predictive sample reuse method", *JASA* 70(350), 1975, doi:10.1080/01621459.1975.10479865 | establish held-out prediction as distinct from in-sample fit — exactly the temporal/epistemic separation the row demands | CITE-TF |
| 21 | machine species | Mayr, E., *Systematics and the Origin of Species*, 1942 (the biological species concept the term borrows); Rice, J. R., "The algorithm selection problem", *Advances in Computers* 15, 1976, doi:10.1016/S0065-2458(08)60520-3 (the algorithm-family reading) | the term is an analogy with two distinct parents; naming both is what stops the analogy being read as a definition | CITE-TF |
| 23 | niche | Hutchinson, G. E., "Concluding remarks", *Cold Spring Harbor Symposia on Quantitative Biology* 22, 1957 (the n-dimensional niche); Rice 1976 (problem/feature space) | Hutchinson owns the multidimensional-region construction the GMI usage reproduces; Rice owns its algorithm-selection reading | CITE-TF |
| 34 | carrier | Turing, A. M., "On computable numbers…", *Proc. LMS* s2-42, 1936; Hopcroft, Motwani & Ullman, *Introduction to Automata Theory, Languages, and Computation*, 3rd ed. 2006 | the tape/storage-as-carrier formalism predates and subsumes the GMI usage | CITE-TF |
| 41 | unseen form | Vapnik, V., *The Nature of Statistical Learning Theory*, 1995 (held-out generalization); Lampert, Nickisch & Harmeling, "Learning to detect unseen object classes by between-class attribute transfer", CVPR 2009, doi:10.1109/CVPR.2009.5206594 (the zero-shot/unseen-class construction) | "unseen" is a held-out-set notion with an established formal meaning; the row demands that the intended sense be specified against it | CITE-TF |
| 47 | discover | Langley, P., Simon, H. A., Bradshaw, G. L. & Zytkow, J. M., *Scientific Discovery: Computational Explorations of the Creative Processes*, MIT Press, 1987 | the canonical treatment of machine discovery, including the requirement that the target not be pre-encoded | CITE-TF |
| 48 | derive-claim typing | Hempel, C. G. & Oppenheim, P., "Studies in the logic of explanation", *Philosophy of Science* 15(2), 1948, doi:10.1086/286983; Popper, K., *The Logic of Scientific Discovery*, 1959 | contribution typing is a claim about explanatory/derivational status; these are its parents, and the sibling template is not | CITE-TF |

## What this file does NOT establish

- It does not verify any citation. Every entry is `CITE-TF`; AC05 stays open.
- It does not claim any listed parent is the true earliest work, only the
  earliest or strongest **known to the register**.
- It supplies no new terminology and changes no match verdict in the parent
  crosswalk.
