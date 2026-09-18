# GMI #833 maturity rescore v3-W4 — named results

Package `gmi-833-maturity-rescore-v3-w4-v1`. Claim ceiling `AUDIT_RELABEL_ONLY`.
Every result below is a statement about LABELS under an already-frozen rule. None
is a statement about the world, and none closes a #833 row.

Shared assumptions for MRW-1 .. MRW-5:

- **A1.** The maturity/evidence rubric is exactly the one frozen in
  `research/gmi-833-maturity-rescore-v2-v1/FREEZE_V2.md` (blob
  `7e3a055d00361ba6204e38db8a6be5c24d1a580a` at `source_main`), imported unchanged.
- **A2.** `source_main = 5126041da7ce608f69157f281ca492ac9618c8e4`. All blob pins in
  `MANIFEST_V1.json` hold there and are re-verified at run time.
- **A3.** Git add-order and ancestry, read from objects reachable in the repository
  (main, plus the origin branches and pushed tags named in the manifest), are a
  faithful record of the order in which artifacts were committed.
- **A4.** The #976 L47 verdict `POST_HOC_SUSPECT (CONFIRMED, double-verified)` against
  `gmi-novel-intelligence-w4-v1` is an INPUT, not a question. MRW-1 re-verifies its
  git evidence independently but does not re-litigate the adjudication.

---

## MRW-1 — the parent's M4 was licensed by a precondition that is false

**Statement.** Let `p = gmi-novel-intelligence-w4-v1` and let `r` be its v2 score row
`GMI833_V2_LEGACY_074_W4-C`. Under A1, `r`'s level `M4` is licensed only by the support
kind `FROZEN_HELDOUT`, whose frozen defining condition is *"freeze artifact precedes
outcome"*. On `source_main`, `RESULT_V1.json` of `p` is first added at `08c4d206` and
`FREEZE_V1.md` at `7ce73e5d`, and `08c4d206` is a strict ancestor of `7ce73e5d` with the
reverse false. Therefore that condition is FALSE for `p`, `FROZEN_HELDOUT` is not an
available support kind for `r`, and `M4`/`EV3` were not earned.

**Scope and quantifiers.** One package, one row, at `source_main`. Nothing is asserted
about any other M4 row, and nothing is asserted about whether `p`'s mathematics is right.

**Falsifiers.** (i) `merge-base --is-ancestor 08c4d206 7ce73e5d` fails, or the reverse
succeeds; (ii) either file's first-add commit differs from the above at `source_main`;
(iii) the v2 freeze's `FROZEN_HELDOUT` row is shown not to carry the parenthetical
precondition; (iv) a second `FROZEN_HELDOUT`-bearing artifact of `p` is shown to precede
the outcome.

**Strongest parents.** `research/gmi-833-corpus-passes-v2-v1` L47 pass (#976) owns the
CONFIRMED custody finding and the mitigating seed fact; this result claims no novelty in
the finding, only in carrying it into the ladder.

**Forbidden extrapolations.** Not a claim that `p`'s W4-C theorem is false; not a claim
that the seed custody was post hoc (it was prospective); not a licence to restore `M4` on
the strength of the prospective child.

---

## MRW-2 — what the parent does earn: M2 / EV2

**Statement.** Under A1 and MRW-1, the observed support surviving for `W4-C` is
`EXACT_FINITE_CERTIFICATE`: the package's executor establishes every W4 box — the held-out
`k = 5` box included — by exhaustive integer computation over the declared bounded universe
(`F(k)` for `k in {2,3,4}`, fresh `k = 5`, fixed budget `B = 3`), with no floating-point
literal or cast, no `random`, no `numpy` and no sampling in the file. The frozen table maps
that support kind to `EV2` and `M2`. Therefore `r` earns `M2 / EV2`.

**Why not M0.** The G2 rubric row (`SAMPLED_STATISTICAL` / `EMPIRICAL_UNFROZEN` →
`evidence_EV = UNKNOWN`, `M0`), which v2 applied to `G15_STEP_TWO_REACHED`, targets support
that is *only* unfrozen and sampled. This package's support is unfrozen but exact. The
audit falsified the custody of the freeze document, not the exactness of the certificate,
and the frozen rule keys on the observed support kind, not on the discredited claim.

**Why not M3.** `M3` additionally requires the P3/P4 architecture-prior-free condition,
which is not evidenced here: the family `F(k)` is registered by the package itself, so the
search saw the target family. v2 expected that carve-out only for the `aj9*` blind-recovery
family.

**Falsifiers.** (i) any float, RNG or sampling call is found in
`novel_intelligence_w4_v1.py`; (ii) any W4 box is shown to depend on the freeze document's
prospectiveness rather than on the computation; (iii) the frozen table is shown to map
`EXACT_FINITE_CERTIFICATE` to anything other than `EV2`/`M2`; (iv) evidence that the search
did not see the target family, which would reopen `M3`.

**Forbidden extrapolations.** `M2` is not a verdict on the W4-C statement's truth, and it
is not a promotion path back to `M4` for this package under any later evidence: the
commit-order defect is permanent.

---

## MRW-3 — the arrival earns M4 / EV3, and its custody is demonstrable only off main

**Statement.** Let `q = gmi-novel-intelligence-w4-prospective-v1`. On `source_main` every
file of `q` is added in the single squash commit `103e4274`, so main-only add-order
forensics — the method the L47 screen applied to 231 packages — cannot decide freeze-versus-
outcome for `q`; the honest state is INDETERMINATE, not FAIL and not PASS. On the PR-#988
branch, anchored on origin by the pushed tags `rev-l47-w4-freeze-custody -> 56195abe` and
`rev-l47-w4-results -> 81d1b9c3`, the commit `56195abe` contains exactly
`FREEZE_V2_PROSPECTIVE.md` and `FREEZE_V2_PROSPECTIVE.json` in `q`'s directory and nothing
else, and is a strict ancestor of the executor commit `c1056b31` and of the results commit
`81d1b9c3`, with the reverse false both ways. The freeze blobs are byte-identical at
`56195abe` and at `source_main` (`ec68c133`, `ae20c46f`), which licenses reading the branch
evidence onto `source_main`. Hence `FROZEN_HELDOUT` holds for `q`, and the frozen table
gives `EV3` / `M4`.

**Why not M5.** `RECEIPT_MULTIHOST_V1.json` records two hosts and two Python versions
(3.8.10 and 3.14.4) producing a bit-identical result, which resembles `EV4`. The frozen
table forbids it in the same cell: *"never M5: intra-package != independent replication"*
(v1 rule 2). Same package, same authors, same code.

**Falsifiers.** (i) `56195abe`'s tree contains any executor, test or result of `q`;
(ii) the ancestry relation fails or reverses; (iii) either freeze blob at `56195abe`
differs from `source_main`; (iv) either custody tag resolves elsewhere; (v) the branch
objects prove unreachable, in which case the correct report is NOT-CHECKED, never PASS.

**Strongest parents.** `research/gmi-novel-intelligence-w4-prospective-v1`
(`FREEZE_V2_PROSPECTIVE.md`) owns the prospective re-establishment and its own custody
statement; this result verifies that statement independently rather than accepting it, and
claims nothing beyond placing the package on the ladder.

**Forbidden extrapolations.** Not a claim that the parent's defect is erased; not `EV4`
from the multi-host receipt; not W4 domain status beyond the registered finite family.

---

## MRW-4 — the corrected headline: M4 holds at 23 and becomes true

**Statement.** Applying MRW-2 and MRW-3 as a delta over the 197 published rows gives
`M0 48 / M1 30 / M2 90 / M3 6 / M4 23 / UNKNOWN 1`, total 198, and
`EV0 46 / EV1 30 / EV2 96 / EV3 23 / UNKNOWN 3`, total 198. Against the published
`48 / 30 / 89 / 6 / 23 / 1` (total 197) the delta is `M2 +1`, `total +1`, every other class
0. The `M4` total is unchanged at 23 while its membership changes:
`gmi-novel-intelligence-w4-v1` leaves and `gmi-novel-intelligence-w4-prospective-v1` enters.

**This is a swap, not a null result.** The published 23 counted a package whose frozen
held-out prediction the corpus itself had disproved, and omitted the package that had
re-earned one. The corrected 23 counts neither error.

**Falsifiers.** (i) any class count fails to sum to the row count; (ii) route A and route B
disagree on any integer; (iii) the published distribution fails to reproduce the checklist
line `48/30/89/6/23/1`; (iv) either delta record is shown not to follow from the frozen
table.

**Stated alternative, recorded not hidden.** If the arrivals rule's `gmi-833-*` name glob
is applied literally rather than through v2's own closest-typed-rule convention, the arrival
is excluded, `M4` falls to 22, and the headline does change — and the ladder is then
provably incomplete, which is the worse outcome. MRW-5 is why the primary landing is the
closest typed rule.

---

## MRW-5 — the propagation defect is structural, not merely a race

**Statement.** Cross-checking all 30 adverse verdict entries carried by the
`gmi-833-corpus-passes-v2-v1` registers against `THEOREM_SCORES_V2.json` resolves to
`UNREFLECTED 3` (two distinct packages: `gmi-novel-intelligence-w4-v1`, counted by two
registers, and `gmi-833-g0-grammar-growth-v1`), `OUT_OF_SCORED_POPULATION 18`,
`REFLECTED_OR_IMMATERIAL_TO_SCORE 8`, `NOT_ADVERSE 1`. A materially independent
schema-agnostic route discovers 53 adverse package mentions across the same registers and
finds the same `UNREFLECTED` set, so the explicit enumeration missed no section.

Two causes, and only the second makes the class recur:

1. *Temporal.* The rescore merged at `f4020d06` (2026-09-16T14:58:50+02:00); the audit at
   `c4def870` (19:04:05+02:00). The rescore could not have seen the verdict and was never
   refreshed.
2. *Structural.* The arrivals inclusion rule filters by the directory-name glob
   `gmi-833-*`. A revival package that re-earns a property for a non-`gmi-833-*` parent can
   never enter the scored population through that glob, at any later date. Recorded as gap
   **G-NAME**. `gmi-novel-intelligence-w4-prospective-v1` is exactly such a package, which
   is why it was unscored while the disproved parent kept its M4.

**Second-order finding, verified not asserted.** The `g0-grammar-growth` flag is a
squash-merge artifact, and its `M4` score is SUSTAINED: on the origin branch
`research/833-g0-grammar-expansion-v1`, the freeze commit `10f0ef37` contains only
`FREEZE_V1.md` and `FROZEN_FIXTURES_V1.json` and strictly precedes the implementation
commit `65073060`; the only post-merge change to the freeze on main is the #947 terminology
migration (2 lines added, 2 removed — two heading renames). No score of that package is
altered by this tranche. The general lesson: the L47 screen's `SINGLE_COMMIT_FREEZE_RESULT`
(45) and `CUSTODY_NON_DEMONSTRABLE` (18) classes are substantially artifacts of squash
merging, and the repair is the one `gmi-novel-intelligence-w4-prospective-v1` already used —
push custody tags for the freeze and results commits.

**Falsifiers.** (i) the checker fails any hostile (H1 synthetic plant, H2 the real published
W4 row, H3 / H3b the real no-alarm cases, H4 arithmetic tamper, H5 custody-returns-false on
the parent); (ii) the seeded null yields a nonzero flag count; (iii) the two routes disagree
on the `UNREFLECTED` set; (iv) a register section carrying adverse verdicts is shown to have
been skipped by both routes; (v) the g0 branch evidence is shown not to hold.

**Forbidden extrapolations.** Not a claim that the remaining 45 `SINGLE_COMMIT_FREEZE_RESULT`
packages are all fine — they are UNCHECKED here, which is not the same as checked-and-fine.
Not a claim that the 18 `OUT_OF_SCORED_POPULATION` packages have score defects: they have no
scores at all.
