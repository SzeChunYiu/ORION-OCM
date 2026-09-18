# Named results — `gmi-833-ab-residual-definitions-v1` (issue #833, section AB)

Claim ceiling: `DECLARED_DEFINITION_ARTIFACT_V1`.

AB08 and AB25 are **authoring** rows: their governing verbs are
`parent-subtract` and `Define`. The results below are exact statements about
two artifacts authored here and about the two verbatim row strings of comment
5684607872 at `source_main = 5e57d4292266bccf435136e1f7d72caa32e920a0`, plus
200 seeded random bindings. **A definition is not an empirical result.** Nothing
here establishes that GMI is novel with respect to Rice, and nothing here places
any GMI claim on the novelty ladder.

---

## RD-1 — Rice's five components are subtracted, each with a verdict and a named residual

**Scope.** `RICE_PARENT_SUBTRACTION_V1.md` and the five components AB08's own
text names.

**Statement.** The five component names are **extracted from AB08's row text**,
not typed in, and each binds to exactly one section. All **5** carry all five
required fields non-empty — Rice's object, GMI's object, verdict, what Rice
already supplies, and the residual — with a verdict in the closed vocabulary
`{ABSORBED, PARTIAL, DIVERGENT}`: **2 ABSORBED** (problem space, feature space),
**3 PARTIAL** (algorithm space, performance space, selection mapping),
**0 DIVERGENT**. Every `ABSORBED` component's residual is literally `None`. A
closing section states what is **not** claimed novel with respect to Rice, and
the file cites Rice's DOI.

**Quantifiers.** For every component named in AB08's text.

**Assumptions.** Rice's model is the five-tuple `(P, F, A, R^n, S)` with
`f : P → F` and `p : A × P → R^n`. A `PARTIAL` verdict means the component's
role is Rice's and only a named residual is not. Two of the three residuals
(grammar-induced structure of `A`; refusing to scalarize `R^n`) are owned by
other packages on `main` and are credited, not claimed; the third — that a
algorithm selection map whose codomain includes candidates absent from the fitting
portfolio needs its own identifiability argument — is stated as a **gap with no
result behind it**.

**Dependencies.** `gmi-833-tranche-ab-ac-lit` for the crosswalk row that cites
Rice; `gmi-833-g0-grammar-bias-v1` and `gmi-833-finite-pareto-density-v1` own
two of the three named residuals.

**Falsifiers.** A component of AB08's list with no section; a field left empty;
a verdict outside the vocabulary; an `ABSORBED` component that nonetheless
claims a residual (hostile H2 constructs exactly that and is rejected); a
subtraction in which nothing is absorbed, which would be a novelty claim wearing
a subtraction's clothes.

**Strongest parents.** Rice, J. R., "The algorithm selection problem",
*Advances in Computers* 15 (1976), doi:10.1016/S0065-2458(08)60520-3 **owns**
the four-space model and the selection mapping outright; Smith-Miles, *ACM
Computing Surveys* 41(1), 2008, doi:10.1145/1456650.1456656 owns its modern
restatement; Wolpert & Macready, *IEEE TEC* 1(1), 1997, doi:10.1109/4235.585893
owns the impossibility of a uniformly best selector. Both `CITE-TF`. The
residual claimed here is the **component-by-component subtraction itself**,
which the crosswalk does not perform: it cites Rice without subtracting him.

**Forbidden extrapolations.** `GMI_IS_NOVEL_WRT_RICE`, `RICE_SUBSUMED` and
`PARENT_EXHAUSTED` are forbidden. A subtraction table records what the parent
already owns; it does not adjudicate novelty, and 3 PARTIAL verdicts are three
places a novelty claim *could* live, not three novelty claims.

---

## RD-2 — the six novelty-ladder levels are operational, ordered and terminating

**Scope.** `NOVELTY_LADDER_V1.md` and the six levels named in AB25's declared
antecedent row.

**Statement.** The six level names are **extracted from the antecedent row's
bolded terms**, in row order, and the ladder's sections match that order
exactly. All **6** carry all four required fields non-empty — operational
criterion, falsifier, parent literature, demotion rule — and all **6**
criteria name the **witness** that must be exhibited. The six criteria are
**pairwise distinct**. Every demotion rule points **strictly downward**, and the
chain from every level terminates at **level 0**, which is declared as a
section so that demotion always has somewhere to go.

**Quantifiers.** For all six levels, and for the demotion chain from each.

**Assumptions.** A criterion is *operational* when it names a decidable test
together with the witness that test consumes; it is not thereby claimed that
producing the witness is easy, and for levels 4 and 5 producing it is a research
problem. The ladder is a total order in which level *k* asserts every level
below it.

**Dependencies.** RD-3 for the antecedent's provenance;
`GMI_TERMINOLOGY_CROSSWALK_V2.md` row 40, which names the six levels as a
sequence and supplies no criterion, falsifier or demotion rule for any of them.

**Falsifiers.** A level with a missing field; a criterion that is a restatement
of another level's (hostile H4 duplicates one and the distinctness flag flips);
a demotion rule pointing upward (hostile H3) or into a cycle; a seventh level
not named by the antecedent row (hostile H5).

**Strongest parents.** Per level, and all `CITE-TF`: Leroy, *CACM* 52(7), 2009,
doi:10.1145/1538788.1538814 (implementation equivalence); Elsken, Metzen &
Hutter, *JMLR* 20(55), 2019 (architecture); Lipton & Steinhardt, *Queue* 17(1),
2019, doi:10.1145/3317287.3328534 (ablation as mechanism test); Vapnik &
Chervonenkis 1971 and Telgarsky, COLT 2016 (class separation); Baker, Gill &
Solovay, *SIAM J. Comput.* 4(4), 1975, doi:10.1137/0204037 (machine-model
relativization — the actual parent of the paradigm level, with Kuhn 1962 cited
for the word's provenance and **explicitly not as a criterion**); Pareto 1906
and Nosek et al., *PNAS* 115(11), 2018, doi:10.1073/pnas.1708274114 (profile
dominance and pre-registration). The crosswalk **owns** the six level names and
their order. The residual is the criterion, falsifier, parent and demotion rule
per level — none of which exists anywhere on `main`.

**Forbidden extrapolations.** `LADDER_APPLIED` and `CLAIM_IS_AT_LEVEL_N` are
forbidden: **no GMI claim is placed on this ladder here**. The ladder is a
novelty axis and is deliberately **not** merged with the contribution-kind
taxonomy of `WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md`, which is a different axis.

---

## RD-3 — every required item is read off its own row, and AB25's antecedent was declared in advance

**Scope.** The five AB08 components, the six antecedent levels, the AB25 row
itself, and 200 seeded random bindings.

**Statement.** **18 of 18** guard checks hold. AB08's five components occur
literally in **AB08's own text**, so AB08 needs no exception. AB25's six levels
occur in the **antecedent row's** text and — the point of the exception —
**none of the six occurs in AB25's own text**, which is asserted rather than
assumed. Shuffling which artifact section is bound to which row-named item,
**0 of 200** random bindings reproduce the true one; the true binding matches
all **11**, the maximum a random binding reaches is **7**, and the exact mean is
**203/100**.

**Quantifiers.** Over all 18 guard checks and all 200 trials.

**Assumptions.** AB25 is a back-reference, so a literal-occurrence guard over
AB25's own text is unsatisfiable by construction. Rather than weaken the guard,
the antecedent row was **fixed in `FREEZE_V1.md` §4 before any level was
written**, and the guard resolves against it. A test asserts that the antecedent
string used here is byte-identical to the one the freeze quotes, and route B
recovers all three strings from the freeze independently rather than sharing a
constant with route A.

**Dependencies.** The freeze, committed as the first and only file of this
package path.

**Falsifiers.** A required item absent from its resolved row; one of the six
levels turning out to occur in AB25's own text (which would make the exception
unnecessary and require its removal); a random binding reproducing the true one;
a route-B recovery differing from route A's constants.

**Strongest parents.** `gmi-833-ab-terminology-harness-v1` **owns** the
anti-invention guard pattern, which caught two of that package's own first-draft
requirements. It is reused with credit; the residual is the declared-antecedent
resolution for back-referencing rows, which the parent's guard cannot express.

**Forbidden extrapolations.** The guard proves the requirements were read off
the rows. It says nothing about whether the artifacts' *content* is correct —
whether Rice really absorbs the problem space, or whether level 4's separation
criterion is the right one. Those are judgements, and they are not certified
here.
