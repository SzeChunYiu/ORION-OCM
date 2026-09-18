# Novelty ladder v1 — `gmi-833-ab-residual-definitions-v1` (issue #833, AB25)

Row AB25, verbatim from comment 5684607872:

    - [ ] Define a novelty ladder using those academically interpretable levels.

**Antecedent.** AB25 is a back-reference: the levels are not in its own text.
Its antecedent is the row immediately above it, verbatim at `source_main`:

    - [x] Audit `novel intelligence`; distinguish **novel implementation**, **novel architecture**, **novel algorithmic mechanism**, **novel model class**, **novel computational paradigm/domain**, and **novel capability profile**.

The six levels below are exactly the six bolded terms of that row, extracted
from its text. The antecedent was fixed in `FREEZE_V1.md` §4 **before** any
level was written, so the anti-invention guard resolves against a declared
target rather than one chosen to fit.

**What the parent already has.** `GMI_TERMINOLOGY_CROSSWALK_V2.md` row 40 names
the ladder as a sequence — *implementation → architecture → mechanism → model
class → computational paradigm → capability profile* — and instructs authors to
"name the level". It gives **no level an operational criterion, a falsifier, or
a rule for what happens when the criterion fails**. That is what this file
supplies, and it is the whole residual.

**Structure of a level.** Each level states: an **operational criterion** (a
decidable test naming the witness that must be exhibited), a **falsifier**, the
**parent literature** for the level, and a **demotion rule** — what the claim
becomes when the criterion fails. The demotion rule always points strictly
downward and the chain terminates at level 0.

**Total order.** `implementation < architecture < mechanism < model class <
paradigm < capability profile`. A claim at level *k* asserts the criteria of
every level below it are also met. Placement is a claim requiring evidence; this
file places nothing.

---

## Level 0 — not novel

Not one of the six levels the antecedent row names. It is the terminus of every
demotion chain and exists so that demotion always has somewhere to go. It has no
criterion to satisfy: a claim arrives here by failing level 1.

---

## Level 1 — novel implementation

**Operational criterion.** Exhibit an artifact whose input/output behaviour is
extensionally equal to an existing artifact's on the declared interface, while
differing in code, data layout or schedule. The witness is the pair plus the
equality certificate on the declared interface.

**Falsifier.** An existing artifact in the named parent set that the equality
certificate also matches under the declared interface — i.e. the "new"
implementation is a copy or a trivial re-encoding.

**Parent literature.** Program equivalence and compiler correctness: Leroy, X.,
"Formal verification of a realistic compiler", *CACM* 52(7), 2009,
doi:10.1145/1538788.1538814. `CITE-TF`.

**Demotion rule.** Fails → **level 0**. An implementation that is not even
distinguishable from an existing one is not novel in any sense.

---

## Level 2 — novel architecture

**Operational criterion.** Exhibit a structural description — a graph of typed
components and connections — that is **not isomorphic**, under the declared
relabelling group, to any member of the named parent architecture set. The
witness is the description, the parent set, and the non-isomorphism certificate.

**Falsifier.** An isomorphism to a parent architecture under the declared group;
or a declared group so small that trivial relabellings escape it.

**Parent literature.** Neural architecture search: Elsken, T., Metzen, J. H. &
Hutter, F., "Neural architecture search: a survey", *JMLR* 20(55), 2019.
`CITE-TF`.

**Demotion rule.** Fails → **level 1**, provided the level-1 criterion holds;
otherwise → level 0.

---

## Level 3 — novel algorithmic mechanism

**Operational criterion.** Exhibit an input on which the candidate's
*computation*, not merely its output, differs from every parent algorithm in a
way that changes a declared resource or correctness property — and show that
ablating the mechanism destroys the property. The witness is the ablation pair
and the measured property on both sides.

**Falsifier.** An ablation that leaves the property intact (the mechanism is
inert); or a parent algorithm exhibiting the same property by the same
computational route under renaming.

**Parent literature.** Ablation as the standard mechanism test, and the caution
that ablations confound: Lipton, Z. C. & Steinhardt, J., "Troubling trends in
machine learning scholarship", *Queue* 17(1), 2019, doi:10.1145/3317287.3328534.
`CITE-TF`.

**Demotion rule.** Fails → **level 2** if a non-isomorphic structure remains;
otherwise → level 1, then 0.

---

## Level 4 — novel model class

**Operational criterion.** Exhibit a **separation**: a task family the candidate
class represents and every named parent class provably does not, at a stated
resource bound. The witness is the task family, the parent classes, and the
separation argument with its resource bound.

**Falsifier.** A parent class member that represents the same family within the
stated bound; or a separation that holds only at an unstated resource bound, in
which case the claim is about resources, not about the class.

**Parent literature.** Expressivity separations: Vapnik, V. & Chervonenkis, A.,
"On the uniform convergence of relative frequencies of events to their
probabilities", 1971; and the depth-separation line, e.g. Telgarsky, M.,
"Benefits of depth in neural networks", COLT 2016. `CITE-TF`.

**Demotion rule.** Fails → **level 3** if an ablation-surviving mechanism
remains; otherwise downward as above.

---

## Level 5 — novel computational paradigm/domain

**Operational criterion.** Exhibit a **cost-model change**: a declared resource
whose accounting differs from every parent paradigm, such that a problem's
complexity class membership or its resource exponent changes. The witness is the
two cost models side by side and the problem whose accounting differs.

**Falsifier.** A cost model that reduces to a parent's under a constant-factor
or polynomial re-accounting — a re-description is not a paradigm.

**Parent literature.** Kuhn, T. S., *The Structure of Scientific Revolutions*,
1962, is cited **for provenance of the word only and explicitly not as a
criterion**; the criterion's actual parent is machine-model relativization in
complexity theory: Baker, T., Gill, J. & Solovay, R., "Relativizations of the
P =? NP question", *SIAM J. Comput.* 4(4), 1975, doi:10.1137/0204037. `CITE-TF`.

**Demotion rule.** Fails → **level 4** if a separation remains; otherwise
downward as above.

---

## Level 6 — novel capability profile

**Operational criterion.** Exhibit a **profile separation**: a vector of
capability measurements on a declared, pre-registered evaluation set on which
the candidate is not Pareto-dominated by any parent, *and* on which no parent
attains the same profile at any resource allocation. The witness is the
pre-registered evaluation set, the full measurement vectors, and the dominance
check.

**Falsifier.** A parent that attains the profile under some allocation; an
evaluation set chosen after the measurements (which makes the profile a
post-hoc selection artifact, AA33); or a profile that is a scalarization in
disguise (AA29).

**Parent literature.** Pareto dominance: Pareto, V., *Manuale di economia
politica*, 1906; and the pre-registration requirement: Nosek, B. A. et al.,
"The preregistration revolution", *PNAS* 115(11), 2018,
doi:10.1073/pnas.1708274114. `CITE-TF`.

**Demotion rule.** Fails → **level 5** if a cost-model change remains;
otherwise downward as above.

---

## What this file does NOT establish

- **No GMI claim is placed on this ladder.** `LADDER_APPLIED` and
  `CLAIM_IS_AT_LEVEL_N` are forbidden promotions of this package.
- The criteria are *decidable given the witness*; nothing here shows that the
  witness is easy to produce, and for levels 4 and 5 producing it is a research
  problem.
- No citation above was verified against a live source. Every one is `CITE-TF`.
  AC05 is not earned.
- The ladder is a **novelty** axis. It is not the contribution-kind taxonomy of
  `WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md` (theorem / synthesis / generalization /
  new selection law / new empirical result / terminology), which is a different
  axis and is deliberately not merged with it.
