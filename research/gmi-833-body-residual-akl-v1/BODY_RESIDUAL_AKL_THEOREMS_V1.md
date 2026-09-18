# Named results — `gmi-833-body-residual-akl-v1` (issue #833, body rows A, K, L)

Claim ceiling `GMI_833_BODY_RESIDUAL_AKL_DISPOSITION_AT_REGISTERED_FINITE_SCOPE`.
`source_main = 5e57d4292266bccf435136e1f7d72caa32e920a0`, freeze
`c9dec25dad00ddde53ddadd3852c1d5fef1a0e03`.

Every result below is an exact statement about named frozen artifacts. **None
asserts that any GMI theorem is true, and all three rows in scope remain OPEN.**
The audited term of row A is written `ROW_A_TERM`; its literal spelling is in
`FREEZE_ROWS_V1.json` and `RESULT_V1.json` and is deliberately kept out of every
markdown file of this package, so that measuring the debt does not add to it.

---

## RA-1 — the residual of `ROW_A_TERM`, exactly, under three declared scopes

**Scope.** Files tracked at `source_main`, with the bytes taken **from the git
object store by blob sha**, never from the worktree. A worktree read would make
every count depend on what main has merged since `source_main`: a file another
lane modified would differ from its frozen blob and a deleted one would be
missing. Validated: with one in-scope file deliberately given three extra hits
and another deleted from the worktree, both routes still return exactly
`2,710 / 704 / 2,645`.

**Statement.**

| scope | definition | files scanned | files with hits | hits |
|---|---|---:|---:|---:|
| `S1` | every tracked `*.md` and `*.tex` | 2,758 | 739 | **2,779** |
| `S2` | every tracked `*.md` under `research/` | 2,668 | 711 | **2,730** |
| `S3` | the flagship set of `ABH-2`, minus this package — **governing** | 2,645 | 704 | **2,710** |

The two largest concentrations in `S3` are `machine-intelligence-morphogenesis-v1`
(1,148) and `gmi-grand-unification-v1` (619); together they hold **65%** of the
residual. The complete per-package and per-file table is in `RESULT_V1.json`
(one package name there cannot be quoted in markdown without failing the
repo-wide terminology gate, which is why this table stops at two).

**A third handle on the same number.** The three scopes are not independent, and
the identity `S3 = S2 - required_to_remain + repo-root markdown` must hold
exactly: `2,730 - 21 + 1 = 2,710`. It is asserted in the receipt and in the
tests, so a scope definition that silently gained or lost a file cannot pass
unnoticed even if both routes made the same mistake.

**Quantifiers.** For every file f in scope S, the count is the number of
whole-word matches of the frozen parent gate's own pattern for this term,
case-insensitive, singular or plural. Universally quantified over the scope; no
sampling.

**Assumptions.** A hit is a site the gate flags, not a proven misuse — the
parent's own caveat, inherited unchanged. The row's phrase *paper-facing theory*
is **undefined in this repository**: there is no `papers/` directory and no
artifact defines it. This package does not invent a definition and does not
narrow the row to a self-chosen subset.

**Falsifiers.** A file in `S3` carrying the term that the scan reports clean; a
file outside `S3`'s stated definition counted inside it; disagreement between
the two routes on any of the nine numbers above.

**Validated on real data, both directions.** No-alarm: a control token absent
from the corpus scores **0** over the same scope. Recall: a control word that
must occur scores **100,844**, so a zero can never be read off a scanner that
silently matches nothing. Hostile `HA1` (drop the plural branch) moves the count
`2,710 → 1,926` and is named. Hostile `HA2` (silently drop one package from the
walk) moves the file census `2,645 → 2,112` and is named.

**Strongest parents.** `gmi-833-tranche-ab-ac-lit` owns the pattern;
`gmi-833-ab-terminology-harness-v1` owns `ABH-2`, which measured the *whole
banned list* over the flagship set at **9,703 sites in 1,400 of 2,572 files** —
a different, larger quantity than this row's single term.

**Forbidden extrapolations.** 2,710 is not a count of errors. It is not evidence
that the migration lane failed. It does not license a definition of
*paper-facing theory*.

**Disposition.** The row's governing verb is `Replace`. The `S3` residual is
`2,710 != 0`, so under the rule fixed in `FREEZE_V1.md` §2.1 the row **does not
close**.

---

## RA-2 — what the row's preservation clause requires to remain

**Statement.** Inside the four declared terminology-authority and migration
packages, `ROW_A_TERM` occurs **21 times in 8 files**. The row says *while
preserving exact legacy mappings*, so those occurrences are **required to
remain**: the crosswalk cannot map a legacy term it is forbidden to name.

**Why this matters.** Counting them would be a false positive, and a checker
that cries wolf on its first real run gets switched off. `S3` therefore excludes
them by construction, and the number is reported rather than hidden.

**Falsifiers.** An occurrence counted as required-to-remain that lies outside the
four declared packages.

---

## RA-3 — who is able to repair the residual (NOT a closure argument)

**Statement.** Of the **704** files carrying the `S3` residual, **73** are pinned
by content hash in at least one frozen manifest or ledger elsewhere in the
repository, accounting for **272** of the 2,710 sites; **631** files and **2,438**
sites are unpinned by that rule. Editing a pinned file changes its blob sha and
breaks the custody binding that another package's manifest asserts.

**The pin rule, stated so it can be falsified.** A JSON object that carries both
a value equal to a tracked path containing `/` and a key whose name matches
`sha256|sha1|blob_sha|digest` with a 40- or 64-hex value pins that path. Nothing
else counts.

**A false-positive class caught on the first real run, and removed.** The first
version accepted bare basenames and matched repo-root `README.md`, `LICENSE` and
`NOTICE` against manifest entries for *different* files of the same name nested
inside a source packet. Three such claims were rejected once the rule required a
path separator, and the rejection is reported rather than silently dropped.

**Validated both directions.** Hostile `HA4` asserts a pin that no manifest
contains: **1 of 1 refused**. Re-opening every one of the 73 true pins and
requiring the claimed manifest to literally name the path: **0 refused**.

**Forbidden extrapolations.** This does not say the residual is unowned, does not
say it cannot be repaired, and is not a reason the row is closed. It says a mass
edit by a single lane is not the repair route, and it names
`gmi-833-terminology-migration-v1` as the owner.

---

## BR-1 — the bridge dichotomy on the registered real populations

**Scope.** `SIGMA_REAL`, `SIGMA_REAL2`, `SIGMA_REAL3` — the parent's three
prospectively frozen populations of real torch-trained systems, 32 machines
each; both registered contracts `E_full` and `E_v0`; the parent's registered
input grids, 51,840 inputs per population.

**Definitions.** A **bridge** assigns to each machine a non-empty set of
admissible solved-bit values. It is **truthful by construction** iff that set
contains every outcome the training protocol can produce. `CB-PROTO` is the
protocol-conservative bridge: a head the protocol leaves untrained cannot be
registered solved, every trained head stays free. An emission is
**world-invariant** iff `F` emits a point in every admissible world with the same
value, and **non-degenerate** iff that value is a strictly positive rational —
the parent's own standard, which is how it found its `FREEZE_V4` power defect.

**Statement.** Under `CB-PROTO`, **0 of 32 machines in each of the three
populations**, under **either** contract, has a singleton admissible value set
with a strictly positive value. Because the survivor set is world-independent —
`survivor_mask` consults `M`, `D`, the search budget, `H` and `U` only, never
`CAP` — it follows that at **every** input a non-degenerate world-invariant point
requires the bridge to resolve **every** machine in `survivors(x) & Res(R)` to one
common positive value.

**Quantifiers.** For every input x of the registered grid, for every truthful
bridge B, for every contract: if `F` emits a non-degenerate world-invariant point
at x under B, then every machine of `survivors(x) & Res(R)` has a singleton
`B(m)` and all those singletons are equal and positive.

**The requirement is per input, not global.** A registered expectation in
`FREEZE_V1.md` §2.2 said `N(k) = 0` for every `k < 32`. That is **contradicted**
by the measurement — see `BR-2` — because an input whose survivor set happens to
lie inside the resolved machines is resolvable early. The per-input statement
above is what holds and is what is claimed; the global reading is withdrawn.

**Assumptions.** `CB-PROTO`'s exclusion of untrained heads is a protocol clause,
not a proof. It only ever *shrinks* the admissible set, so it can only *raise*
the census: it is the lane's most favourable conservative bridge.

**Falsifiers.** An input, a population and a truthful bridge strictly coarser
than full resolution of that input's surviving admissible machines at which `F`
emits a non-degenerate world-invariant point.

**Strongest parents.** `gmi-833-capability-predictor-v1` owns `F`,
`survivor_mask`, `verdict` and the degeneracy standard;
`gmi-833-capability-predictor-evaluation-v1` owns every population.

**Forbidden extrapolations.** Nothing here says capability prediction is
impossible in general, or outside these three registered populations and grids,
or that `F` is defective.

---

## BR-2 — the conservative-bridge census, and the cost curve of the obstruction

**Statement.** Over all **155,520** registered inputs of the three real
populations, `F` emits **0** non-degenerate world-invariant point predictions
under `CB-PROTO`, and **0** under the strictly wider `CB-MAX`.

**The counter is not stuck at zero.** Three independent demonstrations:

| control | census |
|---|---|
| `HB1` the parent's registered law, full resolution, `SIGMA_REAL` / `REAL2` / `REAL3` | **1,680 / 3,408 / 3,472** |
| `HB1b` the parent's V4 held-out populations at full resolution, `SIGMA_SYN2` / `SIGMA_ARCH2` | **3,872 / 2,400**, across 3 distinct positive values each |
| `HB3` count `0` and `UNSATISFIED` as non-degenerate | **4,928 / 4,928 / 3,872** points appear |

`HB1b` reproduces, from this package's independently written counter, exactly the
non-degenerate point counts the parent publishes for `KE-1` and `KE-2` —
**3,872** and **2,400**. Those two populations are not real trained systems and
carry no part of this row's disposition; they exist so that a census of `0`
cannot be read off an instrument unable to return anything else.

`HB2` widens the bridge to `CB-MAX`: the census must not rise, and does not
(**0**). A hostile that cannot move its own quantity is a test of nothing; each
of the four above is checked to move, or provably not move, the quantity it
perturbs.

**The resolution curve.** `N(k)` is the census on `SIGMA_REAL3` when the first
`k` machines of a registered order are collapsed to the parent's V3 registered
law and the rest keep `CB-PROTO`:

| order | `N(0)` | first `k` with `N(k) > 0` | `N` at that `k` | `N(32)` |
|---|---:|---:|---:|---:|
| rank ascending | 0 | **3** | 1,024 | 3,472 |
| rank descending | 0 | **12** | 352 | 3,472 |

The two orders disagree everywhere in between, so the curve is **order-dependent**
and is reported as a bound on the obstruction, never as a property of a canonical
ordering — the same limitation the parent declares for `KP-2D`.

**What the curve does not license.** Resolving a machine means *supplying its
measured solved-set*. `N(k)` for `k > 0` is therefore **not** a truthful-by-
construction bridge: it is the amount of outcome information the bridge must
carry before `F` says anything non-degenerate. At this scope that information is
available only by (a) a structural registration law — falsified three times by
its own pre-registered falsifiers, with the terminal registered in the parent's
`FREEZE_V3_ADDENDUM` §6 before the V3 outcomes existed — or (b) direct outcome
measurement by the parent's external evaluator, which is the quantity under test
rather than an input to it. Whether (b) is admissible is a question the parent
lane owns; this package does not settle it and does not close the row on it.

**Two routes.** Route A reasons structurally and never enumerates a world. Route
B is black-box: it installs concrete worlds on the registration surface, runs the
parent `F` end to end, and counts inputs whose point is identical and positive in
every world. The two agree on the census (`0` and `0`), on the input total
(155,520) and on all three positive controls (1,680 / 3,408 / 3,472).

**Disposition.** The rule fixed in `FREEZE_V1.md` §2.2 closes the row iff the
`CB-PROTO` census is at least 1. It is **0**, so the row **stays open**, and the
obstruction is **structural at this scope, earned by proof** rather than
unattempted. No fourth registration law was proposed, fitted or tested.

---

## BR-3 — `KE-3` is conditioned on an outcome-selected event

**Statement.** The parent's positive `KE-3` — `F` is wrong on **0 of 161,632**
(input, truthfully-registered-world) pairs — is conditioned on the registration
being truthful. Registration truthfulness held on **19 + 28 + 26 = 73** of
**3 x 32 = 96** real systems, and membership in that event is decided **by the
measured outcome**. A statistic conditioned on an outcome-selected event is
therefore not a test of the predictor on real trained systems.

**What this does NOT say.** It does not say `KE-3` is false, that `F` is
defective, or that the parent overstated: the parent itself reports `KE-3`
beside `KE-3D` and declines to close the row on it. `BR-3` names the property
that makes that decision correct.

**Falsifiers.** A demonstration that the conditioning event is decided without
reference to the measured outcome.

---

## FC-1 — `FFA-1`, a checkable criterion for a genuinely future task family

**Statement.** A candidate family `C` is admissible for a frozen prediction `P`
iff all four clauses hold: (1) `C` carries a verifiable date; (2) that date is
strictly later than the committer timestamp of the commit that froze `P`; (3) `C`
is exogenous — not authored, generated, parameterized or chosen by this
programme, and **not a blob of this repository at all**; (4) the date evidence
does not originate from an artifact this programme controls.

**Clause 3 was amended after the freeze, and the amendment is disclosed.** The
freeze wrote *not reachable as a blob of this repository at the freeze commit*.
Read literally, a file another lane of this same programme commits an hour later
would pass clause 3, which is plainly not what *exogenous to this programme*
means, and it made the verdict depend on what main had merged. The qualifier is
removed; the clause is now strictly stronger and no longer moves with the branch.
Recorded as deviation `D3`.

**Validated in both directions before any verdict was read.** Four fixtures, all
four agreeing with their expectation: a constructed candidate satisfying all four
clauses is **admitted** (recall — a criterion that admits nothing is worthless);
`HC1`, dated after the freeze but authored in-session, is **rejected at clause 3**;
`HC2`, exogenous but with an unattested date, is **rejected at clause 4**; an
undated candidate is **rejected at clause 1**.

**Falsifiers.** A planted admissible candidate the checker rejects; a candidate
failing a clause that it admits.

**Forbidden extrapolations.** `FFA-1` is a custody test, not a test of scientific
merit, and passing it does not make a prediction correct.

---

## FC-2 — no admissible candidate is reachable in-session

**Statement.** Of **6** candidate families enumerated — five pinned repository
blobs spanning the grammar fixtures, the developmental theorem notes, the real
byte sources and the real-system battery, plus one this lane could author —
**0 are admissible**. Every repository blob fails clause 2 (introduced before the
freeze at `1789747076`) and clause 3 (endogenous); the in-session candidate
passes clause 2 and fails clause 3.

**The absence is established a second, independent way.** Rather than arguing
over the candidate list, the check is made exhaustive over the repository: **every
one of the paths tracked at HEAD is a blob of this repository**, hence endogenous,
hence fails clause 3 whatever its date, so the count of exogenous candidates
reachable here is **0** by enumeration rather than by argument. That verdict does
not move when main merges. Route B re-derives it through a different git query —
`ls-files` and ISO committer dates instead of `ls-tree` and epoch times.

**Why this is the honest disposition.** Futurity is a **custody** property, not a
sampling property. Anything this lane authors, and anything pinned from a
repository blob, is out-of-sample but **past**. Redefining *future* to mean
*out-of-sample* would close the row by narrowing its meaning, which is forbidden.
A dated external source published after a frozen prediction would qualify, and
`FFA-1` is exactly the gate such a source must pass; constructing one is not
possible inside a single session, so the row **stays open**.

**Strongest parents.** `gmi-833-real-developmental-validation-v1` recorded this
obstruction in prose and left the row open; this package supplies the criterion,
the checker and the measured count.

---

## Summary of dispositions

| row | section | disposition | the quantity that keeps it open |
|---|---|---|---|
| `ROW_A` | A | **OPEN** | `S3` residual **2,710** sites in **704** of 2,645 files |
| `ROW_K` | K | **OPEN** | `CB-PROTO` census **0** of **155,520** inputs; positive controls 1,680 / 3,408 / 3,472 |
| `ROW_L` | L | **OPEN** | **0** of 6 candidates admissible under `FFA-1`; 0 exogenous posterior blobs |
| `ROW_M1`–`ROW_M3` | M | **NOT IN SCOPE** | owned by #926 / draft PR #927 |
