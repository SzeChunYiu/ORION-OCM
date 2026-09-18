# Named results — `gmi-833-aa-ledger-gate-v1` (issue #833, section AA)

Claim ceiling: `RATCHETED_LEDGER_EMISSION_GATE_V1`.

Every result below is an exact statement about explicitly named finite objects:
the **329** git-tracked theorem artifacts under `research/` at
`source_main = 5e57d4292266bccf435136e1f7d72caa32e920a0` and the **2345** named
results they expose, the five AA row strings of comment 5684607872, four
constructed fixture corpora, and 200 seeded randomizations. These are
computer-assisted exhaustive checks over declared finite domains. **None is an
analytic proof**, and **emitting a ledger is not evidence that the ledger's
contents are correct** — this package checks emission, never correctness.

---

## LG-1 — at `source_main`, no named result emits all four theorem ledgers

**Scope.** The 329 theorem artifacts and their 2345 named results at
`source_main`, with the four packages this tranche adds excluded from the
baseline because they did not exist then.

**Statement.** **0 of 2345** named results emit all four ledgers. Per ledger the
emission counts are **assumptions 31**, **dependency 0**, **falsifier 93**,
**strongest parent 59**. The dependency ledger AA03 demands has **no instance
anywhere on `main`**, and neither does the experiment-ledger artifact class AA06
names (**0** files). The conservative subset of headings that carry a result
identifier or a theorem word is **1015** of the 2345; **6** theorem artifacts
expose no level-2 heading at all and are reported in their own
`unparsed_theorem_artifacts` category; **42** artifacts are vendored copies
under a `raw/` path carrying **310** of the results, counted and disclosed
rather than dropped.

**Quantifiers.** For every theorem artifact f and every named result r in f.
Universally quantified over the frozen tracked set only.

**Assumptions.** A named result is a level-2 ATX heading that is not a bare
definition marker, as fixed in `FREEZE_V1.md` §5 before the first run. That
predicate **over-approximates** — a `## Scope` section heading counts as a
result — and over-approximation can only overstate the debt and make the gate
stricter, never laxer, which is why it was left as declared rather than
narrowed after the numbers were read. Both bounds are reported.

**Dependencies.** `gmi-833-corpus-census-v1` for the tracked-file enumeration
convention; no dependency on any GMI theorem. The **34** headings that repeat
verbatim inside a single artifact collapse to one key in the per-result
comparison and are disclosed as such.

**Falsifiers.** Any named result on `main` emitting all four ledgers; any
`GMI_EXPERIMENT_LEDGER_V1` artifact on `main`; a dependency-ledger emission the
predicate misses; a recount disagreeing with either route.

**Strongest parents.** `gmi-833-corpus-census-v1` extracts `assumptions`,
`falsifiers` and `strongest_parents` as *census fields* and **owns** that
extraction; it never enforced emission, which is the residual here. The
practice itself is standard scientific reporting — Nosek et al., "Preregistration
revolution", *PNAS* 115(11) 2018, doi:10.1073/pnas.1708274114; Popper, *The
Logic of Scientific Discovery* (1959) for the falsifier; Kapoor & Narayanan,
*Patterns* 4(9) 2023, doi:10.1016/j.patter.2023.100804 for the leakage ledger;
Mitchell et al., FAT* 2019, doi:10.1145/3287560.3287596 and Gebru et al.,
*CACM* 64(12) 2021, doi:10.1145/3458723 for structured reporting. Nothing about
the *idea* of a ledger is claimed novel.

**Forbidden extrapolations.** `CORPUS_LEDGERS_COMPLETE` and
`ALL_THEOREMS_COMPLIANT` are forbidden and are the opposite of this number.
2345 non-compliant results is **not** 2345 defective theorems: the predicate
counts section headings too, and a result may state its assumptions in prose
without a block label. It is a measure of *emission discipline*, nothing more.

**Correction of the record.** The #833 batching plan recorded that
`AA_GAP_OBJECT_THEOREMS_V1.md` and `AB_TERMINOLOGY_THEOREMS_V1.md` "already
emit all four ledgers, so the gate has planted positives". Measured at
`source_main`, they do not: the first emits assumptions on 2 of its 5 results
and a dependency ledger on none; the second emits assumptions on 1 of 3,
strongest parents on 1 of 3, and a dependency ledger on none. The planted
positives had to be authored here.

---

## LG-2 — the emission predicate is exact, decoy-resistant, and agreed by two independent parsers

**Scope.** The same 2349 named results at this tranche's tip, and one
constructed decoy.

**Statement.** Two materially independent parsers — route A cuts spans with a
heading regex and matches block labels by regex; route B walks a line state
machine and finds bold delimiters by index, with **no regular expression
anywhere in its parsing path** — agree on **every** named result, compared as a
`path::result → complete` map by set equality over **2315** distinct keys, not
by count equality. The decoy, a result whose running prose contains
"assumptions", "depends", "falsify", "counterexample" and "strongest parent"
but carries no block-leading label, emits **nothing** under both parsers and is
**rejected by the gate**.

**Quantifiers.** For every named result in the corpus, and for the decoy under
both parsers.

**Assumptions.** A ledger is emitted only as a block-leading `**Label.**` run,
declared in `FREEZE_V1.md` §5. Fenced code blocks are excluded from both
parsers. Accepted label spellings are the declared widenings of the canonical
label; the canonical label is read off the row (see LG-5).

**Dependencies.** LG-1 for the corpus; LG-5 for the label vocabulary's
provenance.

**Falsifiers.** One `(path, result)` key on which the two routes disagree; a
decoy the predicate scores as compliant; a real emission either parser misses.

**Strongest parents.** Markdown parsing is not novel. The residual is the
declared decoy class and the per-result set-equality comparison, which rules
out the false agreement in which two implementations report the same total
while disagreeing about which results are compliant.

**Forbidden extrapolations.** `LEDGER_CONTENTS_VERIFIED` is forbidden: an
assumptions ledger listing the wrong assumptions passes this predicate.

---

## LG-3 — the gate is blocking, ratcheting, and demonstrably able to fail

**Scope.** Four constructed fixture corpora and the live repository.

**Statement.** Against a frozen fixture baseline the gate exits **0** with
**0** violations on the clean corpus, and exits **non-zero** on all three broken
variants: a new non-compliant result (`NEW_RESULT_MISSING_LEDGER`), a compliant
result that loses a ledger (`COMPLIANT_RESULT_REGRESSED`), and the prose decoy.
Each broken variant also trips the monotone `CORPUS_DEBT_GREW` rule. On the live
repository the gate exits **0** with **0** violations while seeing **21** new
named results, and the disclosed debt is unchanged at **2345**. The
demonstration runs inside the test module on every CI invocation, so "the gate
can fail" is re-established on every run rather than asserted in prose.

**Measurement scope is not enforcement scope, and the difference is the
false-positive class.** The census uses the declared over-approximating
predicate, which is right for the debt number because it can only overstate.
**Enforcement** uses the conservative `identified` subset, and the monotone
ratchet binds `identified_non_compliant` (**1015** at baseline), not the
over-approximated **2345**. Without that split, any lane adding a theorem note
that uses `##` for section headings would be failed for a reason with nothing
to do with ledger discipline — the exact way a gate gets switched off. Two
further fixtures hold the line: a new note containing `## Scope` and
`## Claim ceiling` alongside one compliant `## XY-1` **passes** with 2 headings
recorded outside enforcement scope, and the same note with `## XY-1`
non-compliant **fails**. Building that fixture is what exposed `claim` and
`result` as bad result-word triggers — `## Claim ceiling` was being typed as a
named result — and they were removed.

**Quantifiers.** Over the four fixtures and the whole live corpus.

**Assumptions.** The ratchet's scope is deliberate: on `pull_request` the gate
runs over the paths the PR owns, so a lane is never failed for another lane's
debt; on `push` the monotone corpus rule applies. A gate that fires on work you
did not do is a gate that gets switched off.

**Dependencies.** LG-1 for the baseline; LG-2 for the predicate. The
predecessor terminology gate is the parent of the ratchet *shape*.

**Falsifiers.** A broken fixture the gate passes; a clean fixture it fails; a
CI configuration in which the gate's exit code cannot reach the job result.

**Strongest parents.** `gmi-833-ab-terminology-harness-v1/terminology_ratchet_v1.py`
**owns** the ratchet pattern — frozen baseline, owned-file scope on pull
requests, strict scope on push — and it is reused with credit. The residual is
the ledger predicate it carries and the failure demonstration: the gate this
pattern replaced ran its checks under `|| true` and therefore gated nothing.

**Forbidden extrapolations.** A green gate means no *new* ledger debt, never
that the corpus is compliant. `LEDGER_DEBT_CLEARED` is forbidden.

---

## LG-4 — AA06's experiment-ledger artifact class is instantiated and detected

**Scope.** The `GMI_EXPERIMENT_LEDGER_V1` artifact class and its two instances.

**Statement.** `main` carries **0** experiment-ledger artifacts, so AA06's five
ledgers — leakage, search space, cost model, evaluation, sampling bias — had no
instance to be enforced against. This package authors **2**, declared as
planted positives in `FREEZE_V1.md` §5 **before** they were written, one for the
corpus census experiment and one for the gate validation experiment. Both are
detected and both emit all **5** ledgers: recall **2/2**, per-ledger emission
**2** each. Together with the theorem side, planted recall is **9/9** named
results across this tranche's two theorem notes and **2/2** experiment
artifacts.

**Quantifiers.** Over both artifacts and all five ledgers.

**Assumptions.** An experiment artifact is a tracked `research/**` markdown file
whose basename matches `*EXPERIMENT*LEDGER*` **and** which declares the schema
line `GMI_EXPERIMENT_LEDGER_V1`. The schema line is required so that a file
cannot be dragged into the class by its name alone.

**Dependencies.** LG-2 for the label predicate, which is shared with the
theorem side; LG-5 for the five labels' provenance in AA06's own text.

**Falsifiers.** An experiment ledger on `main` the census missed; an artifact
matching the name pattern without the schema line that the gate nonetheless
judges; a planted positive scored non-compliant.

**Strongest parents.** Datasheets and model cards (Gebru et al. 2021; Mitchell
et al. 2019) and the leakage taxonomy of Kapoor & Narayanan (2023) own the idea
of structured experiment reporting. The residual is the machine-checkable
artifact class bound to AA06's own five words.

**Forbidden extrapolations.** Two ledgers is two experiments documented, not a
documented experimental corpus. Every other experiment in the repository remains
unledgered, and that is the disclosed residual.

---

## LG-5 — every required ledger label is read off its own AA row, and no random binding is

**Scope.** The nine canonical labels, the five verbatim AA row strings, and 200
seeded random bindings.

**Statement.** Under a declared normalization (lowercase; markdown emphasis
dropped; hyphens, slashes and commas read as spaces; whitespace collapsed),
**9 of 9** canonical labels occur literally in the verbatim text of the AA row
that demands them, and AA06 contributes exactly **5**. Shuffling which label is
bound to which row, **0 of 200** random bindings satisfy all nine; the maximum a
random binding reaches is **7** and the exact mean is **79/25**.

**Quantifiers.** Over all nine labels and all 200 trials.

**Assumptions.** The normalization is declared, not tuned: it exists because
AA05 writes "strongest-parent" with a hyphen and AA04 writes
"falsifier/counterexample" with a slash. A requirement cannot be invented to
make a row pass, and a row-named ledger cannot be quietly dropped — the guard is
the one the AB tranche proved necessary when it caught two of that package's own
first-draft requirements.

**Dependencies.** The verbatim row strings, quoted in `FREEZE_V1.md` §4 before
implementation; a test asserts the strings used here are byte-identical to the
ones the freeze quotes.

**Falsifiers.** A canonical label absent from its row's normalized text; a
random binding satisfying all nine; a row whose named ledger has no canonical
label.

**Strongest parents.** `gmi-833-ab-terminology-harness-v1` **owns** the
anti-invention guard pattern
(`test_every_required_term_occurs_in_the_row_text`). It is reused with credit;
the residual is its transfer to ledger labels and the row-binding null.

**Forbidden extrapolations.** The guard proves the vocabulary was read off the
rows. It says nothing about whether the rows ask for the right ledgers. A second
diagnostic is disclosed and deliberately **not** claimed as a beaten null:
drawing four random label groups from the corpus' 60 most common block labels
matches or beats the true count of complete results in **3 of 200** trials,
because a completeness count over common labels is not discriminative. That
diagnostic is reported as a limitation of a naive vocabulary null, not as
evidence for anything.
