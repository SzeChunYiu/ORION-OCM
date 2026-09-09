# CAPSULE_AUDIT_V1 — pre-PR adversarial audit of `research/quantum-structural-ocm-v1` (issue #216)

Auditor: agent E, branch `research/q216-audit` (base b801a03, = live origin/main).
Audited: the 7 capsule files on `research/quantum-structural-ocm-v1` (agents A+B integrated).
Donor pin: SzeChunYiu/ORION main `1b6f767ea6cd...` — verified unchanged, live, 2026-09-09.

**Overall: PASS_WITH_DEFECTS. Zero P0/P1. Two P2 defects, both documentation-level.
No binding, verdict, terminal, or quoted number was falsified. PR-ready after two small fixes.**

## Verdict table

| # | Check | Verdict |
|---|-------|---------|
| 1 | Binding spot-check (27 artifacts, 12 lane pins, 3 UNBOUND) | PASS, 1x P2 (D1) |
| 2 | Retraction handling (FQ-2/QSD-02 lead; no live 3<4<5 / 85/92 / 708/715) | PASS |
| 3 | Forbidden language (§8 seven terms) | PASS |
| 4 | Mechanism sha256 ×13 + functionality at b801a03 | PASS |
| 5 | 19 §3 fields × 8 donors; normalization declared | PASS |
| 6 | Concrete reopen-falsifier on every PARENT_SUFFICIENT row | PASS |
| 7 | Collision re-check (20 live open PRs) | PASS |
| 8 | Internal consistency (8 donors, verdicts, numerics) | PASS, 1x P2 (D2) |

## Defects

**D1 (P2) — one wrong hex character in a blob SHA.**
`ORION_QUANTUM_SOURCE_LEDGER.json:91` — `"main_blob_sha1": "cd7fe47b3c07d4fff115d9f8a6cdb4b2f4730c5d"`
for `research/extensions/orion-qg/QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json`.
Actual blob at pinned main: `cd7fe47b3c07d4fff115d9f8a6cdb4b2f4730c5e` (final char `e`, not `d`).
Path and terminal are correct and resolve; only the SHA fails a strict verifier. Fix: change `d`→`e`.

**D2 (P2) — capsule file outside the §10 fixed list; manifest incomplete.**
`ORION_QUANTUM_SOURCE_LEDGER.md` exists in the capsule but is not in issue #216 §10's fixed
filename list, and `REPO_STATE.capsule_file_manifest` does not mention it (grep count 0; 7 files
on disk vs 6 listed-existing). REPO_STATE's own rule says §10 fixes the file names. The .md's
content is accurate and retraction-correct. Fix (integrator choice): add it to §10 + manifest,
or fold/drop it before the PR.

Non-defect observations: atlas .md abbreviates QSD-07's verdict to `NO_EARNED_DONOR_RESULT`
(same referent as the .json's full string — unambiguous); the ledger's UNBOUND note about
`qg39_selection_regret_curve.py` is accurate (lowercase basename; case-insensitive match).

## Evidence highlights (full detail in CAPSULE_AUDIT_V1.json)

- **Bindings.** All 27 artifact paths exist at pin `1b6f767e`; 26/27 blob SHAs match; 12/12 lane
  pins resolve; 7/7 byte-identity claims verified IDENTICAL (`git diff lane:path main:path`);
  QG-34 DIFFERS exactly as declared — the weld (4 duplicated keys in main JSON `13a1a28030af`)
  is correctly bypassed via correction receipt `2de63fe9a60b` + digest `7c48f505582a...` +
  sealed blob `61ad64ed0103`, matching the receipt's own "THREE conflicting keys" declaration.
  All 3 UNBOUND claims verified genuinely unbound (phantom `QG39_POST_NULL_RESIDUAL_RESULTS.json`
  absent at main, at 2589801ac, and across `log --all`; zero `RG_*` receipts on main with a
  working control pattern; EXECUTION_PACKET blob `23f6f15b` object-store-only, byte-identical at
  lane 5aa84b52c). Every quoted terminal/number (MAX-R4E-A arms, QG-32 92/48/5895/168/5 probes,
  QG-39 regret, QG-21 90-vs-18 + T-ratio 1, replay 4,545,400/530,944/79,896,607/43, QG-30
  54/15/K-histograms, QG-28 715/1,572,864/0-mismatch/vetoes, census 56, #894 disposition)
  verified verbatim against 20 artifacts dumped at the pin; 5 GitHub comment identities fetched.
- **Retraction.** Every hit of D*=3/F*=4/U*=5/85\/92/708\/715/regret is retraction-scoped,
  stands-as-arithmetic (the correction-receipt reading), a historical citation, or an explicit
  must-NOT-transfer control. QSD-02's `source_result_identity` leads with "RETRACTION
  (authoritative scope)"; the surviving residual quoted matches the retraction doc exactly
  ({0:7,1:30,2:39,3:16} vs null {0:7,1:42,2:34,3:9}; budget-2 regret 2-vs-1).
- **Forbidden language.** Zero claim-form occurrences of the seven §8 terms. Controls prove the
  scan works: `/agi/` matched "pagination"; "quantum-advantage" appears 10x — all inside
  prohibition statements (census boundary quotes, `no_quantum_authority_rule`).
- **Mechanisms.** 13/13 sha256 recomputed at b801a03 match. Functionality confirmed in the
  pinned sources, incl. exact counts: `JumpLevel` = 9 members (0..8) with the three named
  triggers; `ResourceVector` = 11 fields (Pareto, `dominates()`); `IndexedExtractionWork` =
  17 fields; GBS minimax survivor-split; filter-after-composition MEG-16(ii); rarest-input
  postings with warrant kept in `compose_stage`.
- **Fields/falsifiers.** 8/8 donors carry all 19 §3 fields + declared `fq`/`function`;
  normalization declared (line 4), nothing silently dropped. 8/8 `falsifier_that_reopens`
  entries are concrete (306–470 chars), each naming a machine-checkable reopen condition.
- **Collision.** Live re-fetch of ALL 20 open PRs' file lists: zero files under
  `research/quantum-structural-ocm-v1/`. Control `^research/` matched 280–317 files per audited
  PR. All six REPO_STATE-recorded heads (206, 209–213) match live heads exactly — no drift.
- **Consistency.** 8 donors everywhere; verdict distribution 6 PARENT_SUFFICIENT + 1
  PARENT_SUFFICIENT__NO_EARNED_DONOR_RESULT + 1 ALREADY_CLASSICAL_IN_FAMILY + RESIDUAL 0
  identical across parent map, contract map, atlas .json and atlas .md.

## No-alarm attestations (checker-validation duty)

- Forbidden-term scan never returned empty-without-control: substring/spaced controls matched.
- Retraction greps all returned matches (each individually context-judged); absence was never
  inferred from a silent grep.
- Collision 0-overlap read only after the `^research/` control matched per-PR.
- UNBOUND/absence claims established by basename search (case-insensitive) + `log --all` +
  control patterns, not single greps.

CANNOT_CHECK: none. (Agent C's MSC protocol files are not on the branch; the audited files'
statements about it are contract-level and were not found misstated.)
