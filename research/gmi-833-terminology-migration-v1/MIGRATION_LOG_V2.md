# GMI #833 terminology migration — edit log v2 (tranche 2)

Authority: `FREEZE_V1.md` in this package (unchanged; §2 replacement policy, §3 custody, §4 edit
discipline) and `MIGRATION_LOG_V1.md` (tranche 1: 255 edits, 12 packages gate-clean, merged as PR
`#940` / squash `7f06b634`). Gate:
`../gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py`, `--context paper-facing`.

## Scope re-freeze (v2)

Tranche 1 froze a 24-package corpus; the live corpus at v2 base main `9580a8547920764625e53bebd2f50e07d90e438e`
was **57 `gmi-833-*` packages**; during v2, main advanced to `d624c6171a02a2ade7d33664b2326ff003952169`
landing one further non-aj package (`gmi-833-g0-grammar-growth-v1`, PR `#945`), which was migrated at
rebase time — the v2 scope at PR head is **58 packages** (post-freeze landings add migration work at
landing time, per the v1 tail note). v2 scope re-freeze: every `research/gmi-833-*/` paper-facing
markdown package that is NOT in the aj lane (`gmi-833-aj*` packages belong to the aj lane;
inventoried only, never edited here).

Live pre-edit gate inventory at the respective base SHAs (`--json` over all `research/gmi-833-*/`):
**326 hits in 38 packages** = 260 non-aj hits in 25 packages (this tranche's edit scope; includes 36
hits in 4 packages that landed after the tranche-1 measurement: `maturity-rescore` 16,
`ai0-convergence-spine` 3, `corpus-audit-close` 3, `g0-grammar-growth` 2× at rebase time; plus the
236 carried from the tranche-1 tail table minus in-scope drift) + 31 definitional-quote hits in this
package's own freeze + 35 aj-lane hits (12 packages).
Non-aj drift vs the tranche-1 tail table: +24 hits in 4 new packages, +1 [[R1]] site
(`maturity-rescore`), +1 [[R4]] site (`ai0-convergence-spine`), +2 aj packages (+4 aj hits).

Post-edit (this branch, measured over the whole corpus): **69 hits** = 35 aj-lane (untouched, below)
+ 34 acknowledged (this package's freeze 31 + two no-smuggling citation sites 3; see next section).
**Zero unacknowledged hits outside the aj lane.** The Section-A deontic term is at **zero
unacknowledged hits in every non-aj package** (11 sites migrated: see R1 rows below).

## Acknowledge decision (the 31 definitional quote hits + 3 citation sites)

Decision: **acknowledge file**, not a gate authority-rule change. `ACKNOWLEDGED_FINDINGS_V1.json` in
this package lists 17 `file:line` sites (34 hits) with per-site reasons; corpus-scope gate runs pass
those ids via `--acknowledge` (usage string in the JSON).

Rationale. The 31 hits in `FREEZE_V1.md` of this package are the quoted legacy tokens that §2 pins
exactly once so that `[[R#]]` masking in both log files can be unmasked; they are named objects of
the migration itself, not live prose (freeze §1 note, §4). Removing them would break the unmasking
contract; rewriting them would falsify the freeze's own pre-edit inventory. The alternative —
extending the gate's `_authority_doc` self-skip — is rejected: it matches on file NAME, and this
file is named `FREEZE_V1.md` like every other package's freeze, so a name-based whitelist would mask
real hits corpus-wide (a checker-weakening change). The gate's own design already provides
`--acknowledge` for exactly "explicitly acknowledged accepted findings". The 3 no-smuggling hits are
a verbatim citation title plus the canonical econometric term of art it defines (Heckman 1979; the
crosswalk has no replacement row for that sense; freeze §2 sanctions the compound with its
citation). Acknowledged findings are accepted only for the stated quoted/cited-object reasons; any
other finding remains a violation.

## Conventions (v1 conventions apply; v2 deltas)

- Row format and `[[R#]]` masking identical to v1; source of every row is the branch diff
  (`git diff --unified=0` at the single v2 commit), spans generated mechanically from that diff.
- `[[R5]]ies` (resp. `[[R4]]` inside a plural context) marks the y→ies plural of the pinned token.
- Rule table extended with **R10** (not present in v1 — zero v1 corpus hits): the
  finite-enumeration-as-proof term (crosswalk row 46 / migration-rule table "proof of universal by
  enumeration"); replacement: reorder/qualification wording that names what a finite run is
  (reconstruction / certified check), never "proof". One edit this tranche.
- Gate-invisible forms (underscore-joined identifiers, `preselection`, the y→ies plurals, `Sel`)
  are migrated ONLY on lines already edited for a visible hit, for definitional consistency;
  untouched lines keep them (minimal-diff discipline). Such rows are marked by an `*` on the rule
  tag where the removed side also carried an invisible form.
- Package directories whose frozen identifiers contain legacy components are cited with the same
  mask as v1 (e.g. `gmi-833-[[R5]]-[[R4]]-schema-v1`); the on-disk identifiers never change.
- Table/Prose citations of such packages now cite the package's unique underscore-joined executor
  file name (gate-invisible by word-boundary structure, unique across the corpus, a frozen internal
  identifier) or a descriptive name; each site gains a pointer note.
- Command blocks that named such directories resolve them via the unique executor file name
  (`PKG=$(dirname $(ls research/gmi-833-*/<executor>.py))`, verified to resolve to exactly one
  package); tranche-1's glob style where a token-free unique glob exists.
- Unmerged-branch citations: the branch name is cited as its token-free prefix plus a description
  of the elided suffix, with the exact bytes pinned in this log once: `gmi/learning-law-` + the
  [[R4]] token (update-law-nfl sites below).

## DEFERRED population

Zero. Same two checks as v1:

1. Mechanical: over `git diff --unified=0` of the v2 commit, every removed/added line pair carries
   at least one rule match on the removed side (generated and asserted: 207 replaced-line rows, 0
   unattributed; 8 inserted note/command lines carry no removed side by construction).
2. Per-hunk review: each pair is a wording-level substitution (or an explicit identifier-citation
   convention above); quantifiers, scopes, premise sets, falsifier inventories, theorem numbering,
   claim-ceiling strings, receipt keys, terminal strings, file names and directory names are
   identical outside the substituted token. Where a sentence merely DENIES the banned claim
   ("not literally [[R2]]"), the v1 precedent replacement is "not literally assumption-free".

## Custody

Across the single v2 commit the only touched files are paper-facing `.md` files under
`research/gmi-833-*/` (53 files, 25 packages) plus two new files in this package
(`MIGRATION_LOG_V2.md`, `ACKNOWLEDGED_FINDINGS_V1.json`) and one authority-package change, below.
No `RESULT_V1.json` or receipt JSON, no corpus `.py` executor/test, no `MANIFEST_V1.json`, no
workflow file is modified. Manifest custody re-verified at edit time for all 24 edited packages
INCLUDING the three that landed after the tranche-1 measurement: manifests list `.md` artifact
names only — zero sha/blob digest bindings over markdown content; the only test reading
`.md`-suffixed strings (`corpus-census`) uses synthetic fixture paths, never package docs. Frozen
identifiers unchanged everywhere, including
`GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_REGISTERED_SCOPE`,
`NO_VIABLE_MORPHOLOGY`, `NON_ISOMETRIC_REMINT`, `ENCODING_INVARIANT_AT_REGISTERED_REMINTS`,
`GMI_FINITE_HISTORY_SWITCHING_AND_HYSTERESIS_SELECTION_AT_REGISTERED_SCOPE` (all underscore-joined,
gate-invisible), the `Sel(h)` notation, and every package/file/directory name.

Authority-package change (disclosed): `GMI_TERMINOLOGY_CI_GATE_V1.py` `--acknowledge` was broken as
shipped — it compared `(file, line_no)` tuples against `"file:line"` strings, so it could never
suppress any finding. v2 makes the acknowledge path load-bearing (see the decision above), so the
parse is fixed (split on the last `:`, integer-guarded; malformed ids suppress NOTHING — findings
stay visible, the fail-safe direction) and a unit test
(`test_gate_acknowledge_suppresses_only_listed_site` in `test_ab_ac.py`) pins the behavior.
Default gate behavior (no `--acknowledge`) is byte-identical; the authority receipt
(`RECEIPT_ABAC_V1.json`) is untouched and its pinned `run()` output is unchanged.

## Rebase resolution note

- v2 was authored on base `9580a854` and rebased onto `d624c617` (main advanced via PR `#945`,
  which added `gmi-833-g0-grammar-growth-v1`; zero file overlap with v2 edits — no conflicts).
  The new package's two gate hits are migrated in this same commit (rows under its package
  heading below), so the v2 claim holds at the PR head rather than at the authoring base.

## Per-package edit ledger (v2)

Counts: 217 rows over 25 packages / 53 files; by rule R4=81, R5=89, R6=27, R3=15, R8=14, R1=11,
R7=4, R2=3, R10=1 (rows may carry several rules; a row's rules are the tokens on its removed side).
Rule R9 had zero v2 sites.

### gmi-833-ai0-convergence-spine-v1
- `gmi-833-ai0-convergence-spine-v1/GMI_CONVERGENCE_SPINE_V1.md:27` [R4]: `…rence frontier under declared [[R4]] conditions.` -> `- `Pref(Xi)` — Pareto/preference frontier under declared choice conditions.`
- `gmi-833-ai0-convergence-spine-v1/GMI_CONVERGENCE_SPINE_V1.md:39` [R4,R5]: `- #894/#898/#902 and related [[R5]]-[[R4]] tranches feed `SEL`.` -> `- #894/#898/#902 and related architecture-choice tranches feed `SEL`.`

### gmi-833-capability-abstention-v1
- `gmi-833-capability-abstention-v1/CAPABILITY_ABSTENTION_THEOREM_V1.md:99` [R8]: `## 6. [[R8]] and boundary` -> `## 6. Strongest-parent subsumption and boundary`
- `gmi-833-capability-abstention-v1/FREEZE_V1.md:14` [R8]: `## Frozen [[R8]]` -> `## Frozen strongest-parent subsumption`
- `gmi-833-capability-abstention-v1/FREEZE_V1.md:25` [R5]: `- [[R5]]/capability result: `bdc5c3cd4…` -> `- mechanism-structure/capability result: `bdc5c3cd42e312d8c7af52f7ba84220631a25f8a`;`
- `gmi-833-capability-abstention-v1/FREEZE_V1.md:38` [R1]: `## Frozen theorem [[R1]]s` -> `## Frozen theorem acceptance items`

### gmi-833-capability-bounds-interactions-v1
- `gmi-833-capability-bounds-interactions-v1/CAPABILITY_BOUNDS_INTERACTIONS_THEOREMS_V1.md:164` [R8]: `## 6. [[R8]] and claim boundary` -> `## 6. Strongest-parent subsumption and claim boundary`
- `gmi-833-capability-bounds-interactions-v1/FREEZE_V1.md:16` [R8]: `## Frozen [[R8]]` -> `## Frozen strongest-parent subsumption`
- `gmi-833-capability-bounds-interactions-v1/FREEZE_V1.md:19` [R5]: `[[R5]]/capability contract, and #854…` -> `mechanism-structure/capability contract, and #854 compact axiom core.  The historical`
- `gmi-833-capability-bounds-interactions-v1/FREEZE_V1.md:29` [R5]: `- [[R5]]/capability result: `bdc5c3cd4…` -> `- mechanism-structure/capability result: `bdc5c3cd42e312d8c7af52f7ba84220631a25f8a`;`
- `gmi-833-capability-bounds-interactions-v1/FREEZE_V1.md:47` [R1]: `## Frozen theorem [[R1]]s` -> `## Frozen theorem acceptance items`

### gmi-833-cognitive-reaudit-v1
- `gmi-833-cognitive-reaudit-v1/COGNITIVE_REAUDIT_THEOREMS_V1.md:17` [R4]: `…f `T` is not a subset of `S`, [[R4]] is inadmissible` -> `discovery costs. If `T` is not a subset of `S`, choice is inadmissible`
- `gmi-833-cognitive-reaudit-v1/COGNITIVE_REAUDIT_THEOREMS_V1.md:23` [R4]: `…gleton queries, a fixed blind [[R4]] of `k<n` items is` -> `advantage. For singleton queries, a fixed blind choice of `k<n` items is`
- `gmi-833-cognitive-reaudit-v1/COGNITIVE_REAUDIT_THEOREMS_V1.md:24` [R4]: `…stered queries, so equal-size [[R4]] alone is` -> `exact on only `k/n` of the registered queries, so equal-size choice alone is`
- `gmi-833-cognitive-reaudit-v1/FREEZE_V1.md:43` [R4]: `…d and only when its discovery/[[R4]] premium is smaller than the` -> `   is enforced and only when its discovery/choice premium is smaller than the`
- `gmi-833-cognitive-reaudit-v1/FREEZE_V1.md:44` [R4]: `…t it avoids. Equal-size blind [[R4]] is a required` -> `   materialization cost it avoids. Equal-size blind choice is a required`

### gmi-833-corpus-audit-close-v1
- `gmi-833-corpus-audit-close-v1/FREEZE_V1.md:42` [R4]: `to exactly 200. [[R4]] inside a stratum: `random.Ran…` -> `to exactly 200. Sampling inside a stratum: `random.Random(833200)` over the`
- `gmi-833-corpus-audit-close-v1/FREEZE_V1.md:59` [R10]: `| `ENUMERATION_SUBSTITUTED` | [[R10]] (declared enumeration is fine…` -> `| `ENUMERATION_SUBSTITUTED` | an analytic proof is plausibly available but a finite enumeration stands in for it (declar`
- `gmi-833-corpus-audit-close-v1/FREEZE_V1.md:69` [R5]: `…arch grammars encoding target [[R5]] / cost models` -> `packages → search grammars encoding the target architecture / cost models`

### gmi-833-corpus-census-v1
- `gmi-833-corpus-census-v1/AUDIT_PROTOCOL_V1.md:43` [R4]: `## Algorithm-[[R4]] parent boundary` -> `## Algorithm [[R4]] parent boundary`
- `gmi-833-corpus-census-v1/AUDIT_PROTOCOL_V1.md:45` [R4,R5]: `When later GMI [[R5]]-[[R4]] objects are audited, Rice-style problem/feature/algorithm/performance spaces are treated as a strongest-parent comparison. A GMI object is not novel merely because it renames those components ecology/[[R5]]/performance.` -> `When later GMI architecture-choice objects are audited, Rice-style problem/feature/algorithm/performance spaces are trea`
- `gmi-833-corpus-census-v1/AUDIT_PROTOCOL_V1.md:49` [R1]: `…**registered structural audit [[R1]]s** are discharged. `AMBER` me…` -> ``GREEN` means the row's **registered structural audit requirements** are discharged. `AMBER` means an explicit unresolve`
- `gmi-833-corpus-census-v1/FREEZE_V1.md:112` [R1]: `…:** structural metadata/proof [[R1]]s for the declared registered …` -> `- **GREEN:** structural metadata/proof requirements for the declared registered scope are discharged and no material kno`
- `gmi-833-corpus-census-v1/FREEZE_V1.md:114` [R1]: `…issing dependency/scope/proof [[R1]], cycle, overclaim, laundering…` -> `- **RED:** contradiction, critical missing dependency/scope/proof requirement, cycle, overclaim, laundering, or fail-clo`

### gmi-833-developmental-potential-evolvability-v1
- `gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md:10` [R3]: `developmental [[R3]] `X`, current state `x0`, fini…` -> `developmental state set `X`, current state `x0`, finite directed development`
- `gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md:16` [R3]: `…ately fix a finite descendant [[R3]] `Z`, an exact proposal kernel…` -> `Separately fix a finite descendant state set `Z`, an exact proposal kernel `Q``
- `gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md:89` [R3]: `[[R3]] and useful set. Require `U` t…` -> `state set and useful set. Require `U` to be disjoint from the explicit stored`
- `gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md:155` [R3]: `…on-normalized kernels, out-of-[[R3]] useful sets, zero mass,` -> `Hostiles cover non-normalized kernels, out-of-state-set useful sets, zero mass,`
- `gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md:156` [R3]: `…red-target leakage, unmatched [[R3]]s, omitted/negative/misaligned…` -> `stored-target leakage, unmatched state sets, omitted/negative/misaligned resource`
- `gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md:157` [R3]: `…puts, graph edges outside the [[R3]], and parent` -> `charges, float/Boolean inputs, graph edges outside the state set, and parent`
- `gmi-833-developmental-potential-evolvability-v1/DEVELOPMENTAL_POTENTIAL_THEOREMS_V1.md:160` [R8]: `## 7. [[R8]] and boundary` -> `## 7. Strongest-parent subsumption and boundary`
- `gmi-833-developmental-potential-evolvability-v1/FREEZE_V1.md:18` [R8]: `## Frozen [[R8]]` -> `## Frozen strongest-parent subsumption`
- `gmi-833-developmental-potential-evolvability-v1/FREEZE_V1.md:21` [R5]: `[[R5]]/capability objects, #854 comp…` -> `mechanism-structure/capability objects, #854 compact axiom core, #875 developmental`
- `gmi-833-developmental-potential-evolvability-v1/FREEZE_V1.md:30` [R5]: `- [[R5]]/capability result: `bdc5c3cd4…` -> `- mechanism-structure/capability result: `bdc5c3cd42e312d8c7af52f7ba84220631a25f8a`;`
- `gmi-833-developmental-potential-evolvability-v1/FREEZE_V1.md:42` [R3]: `- a finite descendant [[R3]], exact normalized proposal ke…` -> `- a finite descendant state set, exact normalized proposal kernel, registered`
- `gmi-833-developmental-potential-evolvability-v1/FREEZE_V1.md:49` [R1]: `## Frozen theorem [[R1]]s` -> `## Frozen theorem acceptance items`

### gmi-833-g0-grammar-growth-v1
- `FREEZE_V1.md:20` [R8]: `## 2. [[R8]]` -> `## 2. Strongest-parent subsumption`
- `FREEZE_V1.md:68` [R1]: `## 6. GRW-1 — conservative expansion (proof [[R1]])` -> `## 6. GRW-1 — conservative expansion (proof requirement)`

### gmi-833-g0-cost-privilege-v1
- `gmi-833-g0-cost-privilege-v1/COST_PRIVILEGE_THEOREMS_V1.md:7` [R6]: `… difference between isometric [[R6]]s and same-semantics non-isome…` -> `Parent results are subtracted rather than reclaimed. SyGuS makes the candidate expression language/grammar an explicit i`
- `gmi-833-g0-cost-privilege-v1/COST_PRIVILEGE_THEOREMS_V1.md:15` [R4]: `…`m_w(s)=min_{p in s} C_w(p)`. [[R4]] returns the complete set of s…` -> `The post-hoc `family_label(p)` is not an argument of either `rho` or `C_w`. For semantic class `s`, `m_w(s)=min_{p in s}`
- `gmi-833-g0-cost-privilege-v1/COST_PRIVILEGE_THEOREMS_V1.md:29` [R6]: `…djacency establishes that the [[R6]] is a search-graph isometry ra…` -> `**Proof.** Raw-vector equality gives scalar-cost equality pointwise. Semantic preservation establishes a cost-preserving`
- `gmi-833-g0-cost-privilege-v1/COST_PRIVILEGE_THEOREMS_V1.md:31` [R4]: `…nd preserves all class minima/[[R4]] values for all weights. Raw-c…` -> `**Machine certificate.** The six base presentation identities are renamed through all `6!=720` bijections onto fresh syn`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:8` [R6]: `…act finite cost object, label-[[R6]] group, isometric-[[R6]] theorem, structural-bias coun…` -> `This file freezes the exact finite cost object, label-relabeling group, isometric-relabeling theorem, structural-bias co`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:21` [R4]: `…dings can reverse class costs/[[R4]], so universal grammar neutral…` -> `2. **Strong boundary:** same-semantic but non-isometric grammar recodings can reverse class costs/choice, so universal g`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:25` [R8]: `## 2. [[R8]]` -> `## 2. Strongest-parent subsumption`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:80` [R4]: `[[R4]] at weight `w` is the set of s…` -> `Choice at weight `w` is the set of semantic classes attaining the global minimum class cost. Ties remain sets; no lexica`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:128` [R6]: `An isometric grammar [[R6]] on the registered finite obje…` -> `An isometric grammar relabeling on the registered finite object is a bijection `phi` on presentations satisfying all of:`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:225` [R4]: `rather than a singleton [[R4]].` -> `rather than a singleton choice.`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:227` [R6]: `### H4 — incomplete [[R6]] certificate` -> `### H4 — incomplete relabeling certificate`
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:229` [R6]: `A [[R6]] that preserves semantics but …` -> `A relabeling that preserves semantics but not raw `(L,d)` or search adjacency is `NON_ISOMETRIC_REMINT`; it may be used `
- `gmi-833-g0-cost-privilege-v1/FREEZE_V1.md:236` [R4]: `- all class-minimum and [[R4]] identities under those permut…` -> `- all class-minimum and choice identities under those permutations;`
- `gmi-833-g0-cost-privilege-v1/PARENT_LITERATURE_V1.md:8` [R6]: `…ility bias plus the isometric-[[R6]] vs same-semantics/non-isometr…` -> `4. **Repository #875.** Owns finite G0 description-length/reachability bias plus the isometric-relabeling vs same-semant`

### gmi-833-g0-register-core-v1
- `gmi-833-g0-register-core-v1/CORE.md:26` [R4,R5,R6]: `…abilistic derivation, grammar-[[R6]] invariance or [[R5]]-[[R4]] result is claimed.` -> `The supplied register/control representation is a disclosed prior. No unbiased-search, unique-universal-grammar, neural/`
- `gmi-833-g0-register-core-v1/FREEZE_V1.md:12` [R2]: `… prior**. It is not literally [[R2]]. Its five instruction classes…` -> ``G0-reg-v1` is an architecture-uncommitted operational core **relative to a disclosed register/control representation pr`
- `gmi-833-g0-register-core-v1/FREEZE_V1.md:245` [R3]: `- Add typed state [[R3]]s without naming neural/symbol…` -> `- Add typed state representations without naming neural/symbolic/probabilistic families.`
- `gmi-833-g0-register-core-v1/G0_REGISTER_THEOREMS_V1.md:9` [R2]: `…t or a literally architecture/[[R2]] grammar. `G0-reg-v1` delibera…` -> `This tranche does **not** claim a unique universal instruction set or a literally assumption-free grammar. `G0-reg-v1` d`
- `gmi-833-g0-register-core-v1/G0_REGISTER_THEOREMS_V1.md:173` [R1,R4,R5,R6]: `…y under a search law, grammar [[R6]]s, alternate search algorithms, resource scalarizations and [[R5]] [[R4]] remain separate #833 [[R1]]s.` -> `The grammar determines expressibility and description syntax and is therefore a disclosed inductive bias. This result do`

### gmi-833-g0-stochastic-update-v1
- `gmi-833-g0-stochastic-update-v1/FREEZE_V1.md:8` [R3]: `This file freezes the finite [[R3]], exact rational probability c…` -> `This file freezes the finite state set, exact rational probability constructors, operational update/composition semantic`
- `gmi-833-g0-stochastic-update-v1/FREEZE_V1.md:16` [R3]: `## Registered [[R3]] and exact types` -> `## Registered state set and exact types`
- `gmi-833-g0-stochastic-update-v1/FREEZE_V1.md:18` [R3]: `State [[R3]]:` -> `State set:`
- `gmi-833-g0-stochastic-update-v1/FREEZE_V1.md:142` [R3]: `… state outside the registered [[R3]];` -> `- source/destination state outside the registered state set;`

### gmi-833-global-uncertainty-v1
- `gmi-833-global-uncertainty-v1/FREEZE_V1.md:20` [R4]: `…` only when the corresponding [[R4]]/calibration semantics are act…` -> `5. `SelectivePrediction(value_set,error_or_risk_certificate,coverage,version,provenance)` only when the corresponding se`
- `gmi-833-global-uncertainty-v1/FREEZE_V1.md:192` [R1]: `Allowed only if all frozen [[R1]]s pass:` -> `Allowed only if all frozen acceptance items pass:`
- `gmi-833-global-uncertainty-v1/GLOBAL_UNCERTAINTY_THEOREMS_V1.md:330` [R8]: `## 9. Strongest-[[R8]]` -> `## 9. Strongest-parent subsumption`

### gmi-833-heldout-20-transitions-v1
- `gmi-833-heldout-20-transitions-v1/CORE.md:3` [R5]: `…idation of the #833 Section-J [[R5]] phase law.` -> `Prospective finite validation of the #833 Section-J architecture phase law.`
- `gmi-833-heldout-20-transitions-v1/CORE.md:5` [R6]: `…ogram agreement, candidate-ID [[R6]] invariance, exact boundary ti…` -> `Twenty fresh transition cases were frozen before outcome-search code. Full raw enumeration over 65,552 architecture-name`
- `gmi-833-heldout-20-transitions-v1/CORE.md:17` [R5]: `…for at least five real-system [[R5]] transitions.` -> `This does not satisfy the separate requirement for at least five real-system architecture transitions.`
- `gmi-833-heldout-20-transitions-v1/FREEZE_V1.md:31` [R5]: `…avior and `state_bits`, not a [[R5]]/family name.` -> `Initial state is `S=0`. Candidate identifiers and enumeration order are scientifically irrelevant. The evaluator sees be`
- `gmi-833-heldout-20-transitions-v1/FREEZE_V1.md:95` [R4]: `…l one another or share winner-[[R4]] code. Agreement is required o…` -> `They must not call one another or share winner-choice code. Agreement is required on all 40 endpoint worlds (20 low-pric`
- `gmi-833-heldout-20-transitions-v1/FREEZE_V1.md:104` [R6]: `- neutral surface [[R6]] of candidate IDs must not cha…` -> `- neutral surface relabeling of candidate IDs must not change endpoint property winners;`
- `gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md:1` [R5]: `…GMI #833 prospective held-out [[R5]] transition validation v1` -> `# GMI #833 prospective held-out architecture transition validation v1`
- `gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md:71` [R6]: `- neutral candidate-ID [[R6]] invariance on all 40 endpoint…` -> `- neutral candidate-ID relabeling invariance on all 40 endpoints;`
- `gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md:79` [R4,R5]: `…ement: the previously derived [[R5]]-[[R4]] law prospectively predicts 20…` -> `If all frozen predictions and controls are GREEN, this tranche licenses only a bounded M4-style statement: the previousl`
- `gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md:81` [R5]: `…nsition validation, universal [[R5]] prediction, all-known-form re…` -> `It does **not** license real-system transition validation, universal architecture prediction, all-known-form recovery, o`

### gmi-833-history-switching-hysteresis-v1
- `gmi-833-history-switching-hysteresis-v1/CORE.md:5` [R4,R5]: `…t defines history-conditioned [[R5]] [[R4]] through explicit switching co…` -> `It defines history-conditioned architecture choice through explicit switching costs, proves the exact two-form hysteresi`
- `gmi-833-history-switching-hysteresis-v1/FREEZE_V1.md:4` [R4]: `…ef14ad17bd009822225c972e983` ([[R4]]/phase schema #894 merged).` -> `Base main: `44ec64478075bef14ad17bd009822225c972e983` (choice/phase schema #894 merged).`
- `gmi-833-history-switching-hysteresis-v1/FREEZE_V1.md:8` [R5]: `Finite architecture-name-free [[R5]] set `M`. A current ecology supplies exact scalar base costs `c(m)`. The previous selected [[R5]] `h` affects current choice on…` -> `Finite architecture-name-free candidate-architecture set `M`. A current ecology supplies exact scalar base costs `c(m)`.`
- `gmi-833-history-switching-hysteresis-v1/FREEZE_V1.md:10` [R4]: `…e current history-conditioned [[R4]] set is` -> `The current history-conditioned choice set is`
- `gmi-833-history-switching-hysteresis-v1/FREEZE_V1.md:20` [R5]: `History changes observed [[R5]] at the registered current ecology iff there exist previous [[R5]]ies `h1,h2` with `Sel(h1) != S…` -> `History changes the observed candidate architecture at the registered current ecology iff there exist previous candidate`
- `gmi-833-history-switching-hysteresis-v1/FREEZE_V1.md:49` [R5]: `For proposed current [[R5]] `m*`, if for every previous s…` -> `For a proposed current candidate architecture `m*`, if for every previous state `h` and rival `n`:`
- `gmi-833-history-switching-hysteresis-v1/FREEZE_V1.md:57` [R4,R5]: `…eset map sends every previous [[R5]] to the same canonical pre[[R4]] state `h0`, subsequent [[R4]] is history-independent by construction and equals `Sel(h0)`. Charge/reset cost remains external to this identity unless explicitly included in the [[R4]] objective.` -> `…ture to the same canonical pre[[R4]] state `h0`, subsequent choice…`
- `gmi-833-history-switching-hysteresis-v1/FREEZE_V1.md:70` [R5]: `…on, universal hysteresis, all [[R5]] dynamics, or complete GMI.` -> `This tranche does not claim stochastic switching dynamics, endogenous learned switching costs, general non-Markov histor`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:1` [R4]: `…ory, switching and hysteresis [[R4]] v1` -> `# GMI #833 finite history, switching and hysteresis choice v1`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:7` [R4,R5]: `…is tranche extends the finite [[R5]]-[[R4]] correspondence from #893 by making one piece of developmental history explicit: the previously selected [[R5]]. It proves exact finite switc…` -> `This tranche extends the finite architecture-choice correspondence from #893 by making one piece of developmental histor`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:9` [R4]: `…egistered history-conditioned [[R4]]` -> `## 1. Registered history-conditioned choice`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:11` [R5]: `…finite architecture-name-free [[R5]] set `M`. At the registered current ecology, [[R5]] `m` has exact nonnegative base cost `c(m)`. The previous [[R5]] is `h in M`. Switching/migrat…` -> `Fix a finite architecture-name-free candidate-architecture set `M`. At the registered current ecology, candidate archite`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:15` [R4]: `The current [[R4]] correspondence is` -> `The current choice correspondence is`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:21` [R5]: `…e **history-dependent current [[R5]]** iff there exist `h1,h2` suc…` -> `Define **history-dependent current candidate architecture** iff there exist `h1,h2` such that`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:29` [R4]: `… they alter the exact current [[R4]] set under the same instantane…` -> `The criterion above is definitional but operationally important: two histories matter scientifically only when they alte`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:35` [R5]: `… can yield different observed [[R5]] solely because transition bur…` -> `Thus identical instantaneous costs can yield a different observed candidate architecture solely because transition burde`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:110` [R4]: `Therefore current [[R4]] is history-independent.` -> `Therefore current choice is history-independent.`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:127` [R5]: `…e `m*`. If for every previous [[R5]] `h` and rival `n != m*`,` -> `Fix candidate `m*`. If for every previous candidate architecture `h` and rival `n != m*`,`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:141` [R4,R5]: `…enumerates 13,824 exact three-[[R5]] contexts formed from base costs in `{0,1,2}^3` and binary switching matrices. It finds 3,735 candidate/context margin certificates and verifies every one produces the predicted history-independent singleton [[R4]].` -> `The receipt enumerates 13,824 exact three-architecture contexts formed from base costs in `{0,1,2}^3` and binary switchi`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:147` [R4,R5]: `…ervention maps every previous [[R5]] to one canonical pre[[R4]] state `h0`. [[R4]] after reset is then, by const…` -> `…hitecture to one canonical pre[[R4]] state `h0`. Choice after rese…`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:151` [R4,R5]: `…ginal `h`. Hence the previous [[R5]] identity no longer affects the current [[R4]] correspondence.` -> `for every original `h`. Hence the previous candidate-architecture identity no longer affects the current choice correspo`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:157` [R5]: `…he executor rejects malformed [[R5]] sets, missing base/switching entries, negative base cost, negative switching cost and unknown previous/reset [[R5]]ies.` -> `The executor rejects malformed candidate-architecture sets, missing base/switching entries, negative base cost, negative`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:159` [R5]: `…sented by the single previous-[[R5]] variable.` -> `History-dependence and history-erasure are exact scoped predicates. No result here implies that history is globally irre`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:170` [R2,R4,R5]: `…ame-free integration into the [[R5]]-[[R4]] programme, exact machine-readable claim boundaries, and connection to [[R2]]/reachable [[R5]] derivation.` -> `…nd connection to architecture-[[R2]] and reachable-architecture de…`
- `gmi-833-history-switching-hysteresis-v1/HISTORY_SWITCHING_THEOREMS_V1.md:174` [R5]: `…niversal hysteresis, complete [[R5]] dynamics, or complete GMI.` -> `This result does not establish stochastic switching dynamics, endogenous learning of switching costs, general non-Markov`

### gmi-833-maturity-rescore-v1
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:19` [R4]: `… cannot license reachability, [[R4]], empirical validity;` -> `- **EV1** deductive theorem with explicit premises and falsifiers — cannot license reachability, choice, empirical valid`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:33` [R4,R5]: `…e-search-budget`, `search-law-[[R5]]-change`, `global-vs-reachable`, `[[R5]]-[[R4]]*`, `history-switching`, `held…` -> `3. **M3 is never awarded to a package whose search saw the target family/name/property vector** (prior disclosure `P<=P2`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:98` [R5]: `…`gmi-833-finite-search-budget-[[R5]]-v1` | FSB-4 exact global-reco…` -> `| 3 | `finite_search_budget_v1.py` | FSB-4 exact global-recovery threshold (§6) | `forall_fin[registered finite schedule`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:99` [R1]: `…-foundation-v1` | BS-1 legacy-[[R1]] map (§3) | `CONDITIONAL_AT_RE…` -> `| 4 | `gmi-833-foundation-v1` | BS-1 legacy claim-governance map (§3) | `CONDITIONAL_AT_REGISTERED_SCOPE` (same instance`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:109` [R5]: `… `gmi-833-global-vs-reachable-[[R5]]-v1` | GVR-2 exact optimum-rec…` -> `| 14 | `global_vs_reachable_v1.py` | GVR-2 exact optimum-recovery condition (§4) | `forall_fin[registered finite worlds]`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:112` [R5]: `…`gmi-833-morphcap-v1` | CAP-1 [[R5]] invariance (§4) | `CONDITIONA…` -> `| 17 | `gmi-833-morphcap-v1` | CAP-1 mechanism-structure invariance (§4) | `CONDITIONAL_AT_REGISTERED_SCOPE` (determinis`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:113` [R4,R5]: `| 18 | `gmi-833-[[R5]]-[[R4]]-schema-v1` | PHASE-1A argmin …` -> `| 18 | `[[R5]]_[[R4]]_schema_v1.py` | PHASE-1A argm…`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:114` [R4,R5]: `| 19 | `gmi-833-[[R5]]-[[R4]]-v1` | NICHE-1a sufficient coe…` -> `| 19 | `[[R4]]_v1.py` | NICHE-1a sufficient …`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:117` [R5]: `…`forall_fin[registered finite [[R5]] graphs]` | EV2 (20-frontier a…` -> `| 22 | `gmi-833-pareto-topology-v1` | TOPO-1A forward budget-ball topology basis (§5) | `forall_fin[registered finite ar`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:119` [R6]: `| 24 | `gmi-833-[[R6]]-equivariance-v1` | canonical fingerprint invariance (§3) | `forall_fin[registered finite presentations]` | EV2 (6-[[R6]] + 9-quotient-pair certificate…` -> `| 24 | `[[R6]]_equivariance_v1.py` | canonic…`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md:121` [R5]: `| 26 | `gmi-833-search-law-[[R5]]-change-v1` | SLM-4 unique-opt…` -> `| 26 | `search_law_[[R5]]_change_v1.py` | SLM-4 unique-…`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md` [inserted line]: `Rows 3, 14, 18, 19, 24 and 26 cite the package's unique executor file instead of its directory: those six frozen directory identif`
- `gmi-833-maturity-rescore-v1/FREEZE_V1.md` [inserted line]: ``

### gmi-833-[[R5]]-[[R4]]-schema-v1
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md:1` [R4,R5]: `# gmi-833-[[R5]]-[[R4]]-schema-v1` -> `# gmi-833-architecture-choice-schema-v1 (internal identifier unchanged)`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md:3` [R4,R5]: `Finite architecture-name-free [[R5]]-[[R4]] and affine phase-boundary the…` -> `Finite architecture-name-free architecture-choice and affine phase-boundary theorem tranche for #893 / #833 Section J.`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md:5` [R4]: `…ves typed robust-vs-ambiguous [[R4]] under interval uncertainty. I…` -> `It keeps raw Pareto vectors primary, returns full argmin/tie sets, derives exact rational affine crossover cells, and gi`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md` [inserted line]: `The package directory is the frozen internal identifier (it carries retired legacy terms; see `research/gmi-833-terminology-migrat`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md` [inserted line]: ``
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md:10` [R4,R5]: `python -I -B research/gmi-833-[[R5]]-[[R4]]-schema-v1/test_[[R5]]_[[R4]]_schema_v1.py -v` -> `…rname $(ls research/gmi-833-*/[[R5]]_[[R4]]_schema_v1.py))`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md:11` [R4,R5]: `…hon -I -O -B research/gmi-833-[[R5]]-[[R4]]-schema-v1/test_[[R5]]_[[R4]]_schema_v1.py -v` -> `python -I -B $PKG/test_[[R5]]_[[R4]]_schema_v1.py -v`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md:12` [R4,R5]: `python -I -B research/gmi-833-[[R5]]-[[R4]]-schema-v1/[[R5]]_[[R4]]_schema_v1.py` -> `python -I -O -B $PKG/test_[[R5]]_[[R4]]_schema_v1.py -v`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md` [inserted line]: `python -I -B $PKG/morphology_selection_schema_v1.py`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/CORE.md:17` [R4]: `…gration, finite-search-budget [[R4]], niche/coexistence dynamics, …` -> `Open successors remain history/hysteresis, switching/migration, finite-search-budget choice, niche/coexistence dynamics,`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/FREEZE_V1.md:1` [R4,R5]: `# GMI #833 [[R5]] [[R4]] schema v1 — freeze` -> `# GMI #833 architecture-choice schema v1 — freeze`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/FREEZE_V1.md:8` [R4]: `…ycle/resource vectors. Scalar [[R4]] is conditional on a frozen st…` -> `Finite architecture-name-free candidate mechanism classes under an explicitly registered context. A context supplies a v`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/FREEZE_V1.md:18` [R4,R5]: `### SEL-1 — finite [[R5]]-[[R4]] correspondence` -> `### SEL-1 — finite architecture-choice correspondence`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/FREEZE_V1.md:28` [R4]: `…ficient conditions for unique [[R4]]` -> `### SEL-2 — sufficient conditions for unique choice`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/FREEZE_V1.md:36` [R5]: `…ricate an unattainable pseudo-[[R5]] and are not a valid replaceme…` -> `Define coexistence as a Pareto frontier with cardinality greater than one. Preserve the entire frontier. A hostile must `
- `gmi-833-[[R5]]-[[R4]]-schema-v1/FREEZE_V1.md:48` [R4]: `### PHASE-2 — uncertainty-set [[R4]] semantics` -> `### PHASE-2 — uncertainty-set choice semantics`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:1` [R4,R5]: `# GMI #833 finite [[R5]] [[R4]] and affine phase schema v1` -> `# GMI #833 finite architecture choice and affine phase schema v1`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:7` [R5]: `… utility theory or real-world [[R5]] law.` -> `This tranche turns several Section-J questions into one bounded architecture-name-free mathematical object. It is a fini`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:9` [R4]: `## 1. Registered [[R4]] context` -> `## 1. Registered choice context`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:25` [R4]: `The **[[R4]] correspondence** returns, wit…` -> `The **choice correspondence** returns, without tie-breaking fabrication:`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:49` [R5]: `… `gmi-833-global-vs-reachable-[[R5]]-v1`.` -> `This is immediate because the right minimization is over a subset. It is consistent with and deliberately subordinate to`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:51` [R4]: `…ficient conditions for unique [[R4]]` -> `## 3. SEL-2 — sufficient conditions for unique choice`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:84` [R5]: `…minima can fabricate a pseudo-[[R5]] and may not replace the front…` -> `A coordinatewise-minimum summary would report `(1,1)` for `A,B`, but no candidate realizes `(1,1)`. Hence coordinatewise`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:86` [R5]: `## 5. PHASE-1 — affine [[R5]] phase boundaries` -> `## 5. PHASE-1 — affine architecture phase boundaries`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:126` [R4]: `… 6. PHASE-2 — uncertainty-set [[R4]]` -> `## 6. PHASE-2 — uncertainty-set choice`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:152` [R4]: `…certificate for robust unique [[R4]].` -> `This gives a cheap sufficient certificate for robust unique choice.`
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:160` [R4]: `…phase intervals. Empty viable [[R4]] returns the typed terminal `N…` -> `The kernel rejects negative resource coordinates, mismatched resource dimensions, nonpositive scalar weights, duplicate `
- `gmi-833-[[R5]]-[[R4]]-schema-v1/MORPHOLOGY_SELECTION_THEOREMS_V1.md:171` [R5]: `…ty, resource, uncertainty and [[R5]] objects while preserving fail…` -> `The GMI residual at this stage is the common architecture-name-free contract that joins those parents to the existing be`

### gmi-833-[[R5]]-[[R4]]-v1
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md:1` [R4,R5]: `# gmi-833-[[R5]]-[[R4]]-v1` -> `# gmi-833-architecture-choice-v1 (internal identifier unchanged)`
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md:10` [R4]: `…ed #893/#894 owns the general [[R4]]/affine-phase schema, and #895…` -> `Merged #893/#894 owns the general architecture-choice/affine-phase schema, and #895 owns`
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md` [inserted line]: `The package directory is the frozen internal identifier (it carries retired legacy terms; see `research/gmi-833-terminology-migrat`
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md` [inserted line]: ``
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md:16` [R4,R5]: `…ython3 -I -B research/gmi-833-[[R5]]-[[R4]]-v1/test_[[R4]]_v1.py -v` -> `…rname $(ls research/gmi-833-*/[[R4]]_v1.py))`
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md:17` [R4,R5]: `…on3 -I -O -B research/gmi-833-[[R5]]-[[R4]]-v1/test_[[R4]]_v1.py -v` -> `python3 -I -B $PKG/test_[[R4]]_v1.py -v`
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md:18` [R4,R5]: `…ython3 -I -B research/gmi-833-[[R5]]-[[R4]]-v1/[[R4]]_v1.py` -> `python3 -I -O -B $PKG/test_[[R4]]_v1.py -v`
- `gmi-833-[[R5]]-[[R4]]-v1/CORE.md` [inserted line]: `python3 -I -B $PKG/selection_v1.py`
- `gmi-833-[[R5]]-[[R4]]-v1/FREEZE_V1.md:1` [R4]: `# GMI #892 niche/repricing [[R4]]-laws freeze v1` -> `# GMI #892 niche/repricing choice-law freeze v1`
- `gmi-833-[[R5]]-[[R4]]-v1/FREEZE_V1.md:14` [R8]: `## Frozen [[R8]]` -> `## Frozen strongest-parent subsumption`
- `gmi-833-[[R5]]-[[R4]]-v1/FREEZE_V1.md:17` [R4,R5]: `equivalence, #850 [[R5]]/capability, #876 global-vs-reachable [[R4]],` -> `equivalence, #850 mechanism-structure/capability, #876 global-vs-reachable architecture choice,`
- `gmi-833-[[R5]]-[[R4]]-v1/FREEZE_V1.md:18` [R4,R5]: `and #893/#894 [[R5]]-[[R4]]/affine-phase receipts. The five [[R4]]` -> `and #893/#894 architecture-choice/affine-phase receipts. The five choice`
- `gmi-833-[[R5]]-[[R4]]-v1/FREEZE_V1.md:28` [R3,R5]: `…location over a common finite [[R5]] [[R3]];` -> `- local niche allocation over a common finite candidate-architecture set;`
- `gmi-833-[[R5]]-[[R4]]-v1/FREEZE_V1.md:38` [R5]: `a quality/resource-dominating [[R5]] loses under nonnegative price…` -> `a quality/resource-dominating candidate architecture loses under nonnegative prices, a`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:6` [R4]: `[[R4]] correspondence, uniqueness/Pa…` -> `choice correspondence, uniqueness/Pareto conditions, and affine phase`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:12` [R5]: `[[R5]]ies are finite protected compu…` -> `Candidate architectures are finite protected computational-mechanism equivalence classes,`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:15` [R3,R5]: `…iche uses one common nonempty [[R5]] [[R3]].` -> `nonnegative. Every niche uses one common nonempty candidate-architecture set.`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:20` [R5]: `…exact local utility on common [[R5]]` -> ``sum_z mu(z)>0`, and `u_z(m)` an exact local utility on the common candidate-architecture`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:21` [R3]: `[[R3]] `M`. Define the complete loca…` -> `set `M`. Define the complete local winner set`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:30` [R5]: `…ero-mass niche contributes no [[R5]].` -> `zero-mass niche contributes no candidate architecture.`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:93` [R5]: `global winner if another [[R5]] remains superior.` -> `global winner if another candidate architecture remains superior.`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:108` [R5]: `Thus a [[R5]] that is weakly better in qual…` -> `Thus a candidate architecture that is weakly better in quality and weakly cheaper in every`
- `gmi-833-[[R5]]-[[R4]]-v1/SELECTION_THEOREMS_V1.md:125` [R4]: `…#850, #876, and #893/#894. No [[R4]],` -> `Exact Git objects pin #837, #847, #850, #876, and #893/#894. No choice,`

### gmi-833-no-smuggling-audit-v1
- `gmi-833-no-smuggling-audit-v1/CORE.md:3` [R4]: `…valuation priors, and ecology-[[R4]] bias.` -> `Bounded #855 / #833-D audit-tooling tranche for architecture-name leakage, semantic macro smuggling, cost/search/evaluat`
- `gmi-833-no-smuggling-audit-v1/FREEZE_V1.md:19` [R4]: `6. `Build an ecology-[[R4]]-bias audit.`` -> `6. `Build an ecology-choice-bias audit.``
- `gmi-833-no-smuggling-audit-v1/FREEZE_V1.md:115` [R4]: `## A6 — ecology-[[R4]]-bias audit` -> `## A6 — ecology-choice-bias audit`
- `gmi-833-no-smuggling-audit-v1/FREEZE_V1.md:137` [R4]: `… A6 has no registered ecology [[R4]] bias and the declared frame s…` -> `7. A6 has no registered ecology-choice bias and the declared frame status is auditable for the claim being made.`
- `gmi-833-no-smuggling-audit-v1/NO_SMUGGLING_AUDIT_CONTRACT_V1.md:79` [R4]: `…d when only price-conditional [[R4]] is supported.` -> `Thus a universal winner claim is invalid when only price-conditional choice is supported.`
- `gmi-833-no-smuggling-audit-v1/NO_SMUGGLING_AUDIT_CONTRACT_V1.md:113` [R4]: `## A6 — ecology-[[R4]]-bias audit` -> `## A6 — ecology-choice-bias audit`
- `gmi-833-no-smuggling-audit-v1/NO_SMUGGLING_AUDIT_CONTRACT_V1.md:160` [R4]: `…known-frame one-sided ecology [[R4]] producing a general clean res…` -> `- known-frame one-sided ecology choice producing a general clean result;`

### gmi-833-parent-equivalence-v1
- `gmi-833-parent-equivalence-v1/FREEZE_V1.md:101` [R4,R5]: `…45 corpus census, G0 grammar, [[R5]] [[R4]], capability prediction, indep…` -> `No result on #844 terminology, #845 corpus census, G0 grammar, architecture choice, capability prediction, independent r`
- `gmi-833-parent-equivalence-v1/PARENT_EQUIVALENCE_THEOREMS_V1.md:213` [R8]: `### [[R8]]` -> `### Strongest-parent subsumption`

### gmi-833-pareto-topology-v1
- `gmi-833-pareto-topology-v1/CORE.md:3` [R5]: `This tranche lifts [[R5]] transform burden from one sca…` -> `This tranche lifts architecture transform burden from one scalar back to the primary Pareto frontier of nonnegative sema`
- `gmi-833-pareto-topology-v1/FREEZE_V1.md:45` [R5]: `…universal topology, empirical [[R5]] law, known-form P3 recovery, …` -> `Forbidden promotions: complete quantale/enriched-category formalization, universal topology, empirical architecture law,`
- `gmi-833-pareto-topology-v1/PARETO_TOPOLOGY_THEOREMS_V1.md:6` [R5]: `## 1. Why a scalar [[R5]] distance is not primary` -> `## 1. Why a scalar architecture distance is not primary`
- `gmi-833-pareto-topology-v1/PARETO_TOPOLOGY_THEOREMS_V1.md:58` [R5]: `For a finite directed [[R5]] graph, associate each edge `(…` -> `For a finite directed architecture graph, associate each edge `(M,N)` with the Pareto frontier of available direct trans`
- `gmi-833-pareto-topology-v1/PARETO_TOPOLOGY_THEOREMS_V1.md:116` [R5]: `…orward topology on the finite [[R5]] set.` -> `These balls form a basis for a forward topology on the finite architecture set.`
- `gmi-833-pareto-topology-v1/PARETO_TOPOLOGY_THEOREMS_V1.md:134` [R5]: `…s may exist inside particular [[R5]] strata, but the global GMI ob…` -> `No smooth-manifold structure is asserted. Continuous parameter manifolds may exist inside particular architecture strata`
- `gmi-833-pareto-topology-v1/PARETO_TOPOLOGY_THEOREMS_V1.md:138` [R6]: `…invariant under pure semantic [[R6]]s. Therefore the finite Pareto…` -> `GAUGE-1 proved the registered quotient mechanism and transform burdens invariant under pure semantic relabelings. Theref`
- `gmi-833-pareto-topology-v1/PARETO_TOPOLOGY_THEOREMS_V1.md:146` [R5]: `…ciplined coupling to verified [[R5]] transformations, semantic/res…` -> `Pareto antichains, Minkowski sums, multiobjective shortest paths, idempotent semirings, Lawvere-style directed metrics, `
- `gmi-833-pareto-topology-v1/PARETO_TOPOLOGY_THEOREMS_V1.md:148` [R5]: `…nown-form recovery, empirical [[R5]] transitions, or complete GMI.` -> `This tranche does not establish a complete quantale-enriched category, a universal intelligence-space topology, Hausdorf`

### gmi-833-real-transition-protocol-v1
- `gmi-833-real-transition-protocol-v1/FREEZE_V1.md:1` [R5]: `# GMI #833 real-system [[R5]] transition evidence protocol …` -> `# GMI #833 real-system architecture-transition evidence protocol v1 — freeze`
- `gmi-833-real-transition-protocol-v1/FREEZE_V1.md:39` [R5]: `…uns, leakage, or unidentified [[R5]] can never count toward five.` -> `Otherwise return `INSUFFICIENT_REAL_SYSTEM_EVIDENCE` with typed rejection reasons. Synthetic/toy/simulator-only evidence`

### gmi-833-robustness-controls-v1
- `gmi-833-robustness-controls-v1/CORE.md:6` [R6]: `…reserving alternate encodings/[[R6]]s;` -> `- semantics-preserving alternate encodings/relabelings;`
- `gmi-833-robustness-controls-v1/FREEZE_V1.md:30` [R7]: `## R1 — matched grammar [[R7]]` -> `## R1 — matched grammar negative control`
- `gmi-833-robustness-controls-v1/FREEZE_V1.md:34` [R7]: `A registered [[R7]] `C-` is matched iff:` -> `A registered negative control `C-` is matched iff:`
- `gmi-833-robustness-controls-v1/FREEZE_V1.md:47` [R6]: `… alternate semantic encodings/[[R6]]s` -> `## R2 — alternate semantic encodings/relabelings`
- `gmi-833-robustness-controls-v1/FREEZE_V1.md:49` [R6]: `A [[R6]] pair consists of finite encod…` -> `A relabeling pair consists of finite encodings `e1,e2` plus a declared bijection `phi` between their symbols/candidates `
- `gmi-833-robustness-controls-v1/FREEZE_V1.md:61` [R6]: `…r a pure semantics-preserving [[R6]] and therefore surface `ENCODI…` -> `Frozen hostile: lexicographic tie-breaking over surface identifiers must change the chosen canonical class after a pure `
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:21` [R7]: `## 2. R1 — matched grammar [[R7]]` -> `## 2. R1 — matched grammar negative control`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:29` [R7]: `A [[R7]] `C-` is **matched** iff:` -> `A negative control `C-` is **matched** iff:`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:50` [R6]: `## 3. R2 — semantic [[R6]] / alternate encoding` -> `## 3. R2 — semantic relabeling / alternate encoding`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:52` [R6]: `…` and `e2:S2->K` form a valid [[R6]] pair when a bijection `phi:S1…` -> `An encoding is a finite map `e:S->K` from surface identifiers `S` to canonical protected semantic classes `K`. Two encod`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:62` [R6]: `…ical invariance under a valid [[R6]]` -> `### R2 theorem — canonical invariance under a valid relabeling`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:64` [R6]: `…surface names, then two valid [[R6]]s yield the same canonical res…` -> `If a decision rule `A` is semantic, i.e. there exists `A_K` with `e(A(e)) = A_K(K-data)` independently of surface names,`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:68` [R6]: `…actor through `K`. The frozen [[R6]] changes the lexicographically…` -> `**Hostile.** A lexicographic surface-name tie break need not factor through `K`. The frozen relabeling changes the lexic`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:142` [R6]: `…re validly present, while the [[R6]], alternate search, and altern…` -> `The frozen sensitive fixture is the exact counterexample: all four controls are validly present, while the relabeling, a`
- `gmi-833-robustness-controls-v1/ROBUSTNESS_CONTROL_THEOREMS_V1.md:159` [R6]: `- a non-bijective/nonsemantic [[R6]] treated as invariance evidenc…` -> `- a non-bijective/nonsemantic relabeling treated as invariance evidence;`

### gmi-833-stochastic-predictive-v1
- `gmi-833-stochastic-predictive-v1/FREEZE_V1.md:9` [R8]: `… hostile witnesses, strongest-[[R8]], open descendants, and claim …` -> `This file freezes the exact finite controlled-stochastic scope, theorem statements, hostile witnesses, strongest-parent `
- `gmi-833-stochastic-predictive-v1/FREEZE_V1.md:90` [R8]: `### Strongest-[[R8]]` -> `### Strongest-parent subsumption`
- `gmi-833-stochastic-predictive-v1/FREEZE_V1.md:154` [R8]: `### Strongest-[[R8]]` -> `### Strongest-parent subsumption`
- `gmi-833-stochastic-predictive-v1/FREEZE_V1.md:224` [R4]: `…exact independent core-column [[R4]];` -> `- exact independent core-column choice;`
- `gmi-833-stochastic-predictive-v1/FREEZE_V1.md:255` [R4]: `…istency, rates, and core-test [[R4]] under estimation error;` -> `- finite-sample identification, consistency, rates, and core-test choice under estimation error;`
- `gmi-833-stochastic-predictive-v1/FREEZE_V1.md:277` [R1]: `Allowed only if all frozen [[R1]]s pass:` -> `Allowed only if all frozen acceptance items pass:`

### gmi-833-transform-geometry-v1
- `gmi-833-transform-geometry-v1/CORE.md:3` [R5]: `…chitecture-name-free verified [[R5]] transforms at a finite regist…` -> `This tranche defines architecture-name-free verified architecture transforms at a finite registered scope, proves exact `
- `gmi-833-transform-geometry-v1/FREEZE_V1.md:3` [R5]: `…el for architecture-name-free [[R5]] classes.` -> `Freeze scope: finite exact deterministic transformation kernel for architecture-name-free mechanism classes.`
- `gmi-833-transform-geometry-v1/FREEZE_V1.md:13` [R5]: `A registered [[R5]] transform is a directed edge …` -> `A registered architecture transform is a directed edge carrying source, target, exact semantic-error increment, nonnegat`
- `gmi-833-transform-geometry-v1/FREEZE_V1.md:40` [R6]: `- grammar/[[R6]] invariance;` -> `- grammar/relabeling invariance;`
- `gmi-833-transform-geometry-v1/TRANSFORM_GEOMETRY_THEOREMS_V1.md:1` [R5]: `# GMI #833 [[R5]] transformation geometry v1` -> `# GMI #833 architecture transformation geometry v1`
- `gmi-833-transform-geometry-v1/TRANSFORM_GEOMETRY_THEOREMS_V1.md:3` [R5]: `… foundation tranche; not full [[R5]] topology or developmental equ…` -> `**Status:** finite exact foundation tranche; not full architecture topology or developmental equivalence.`
- `gmi-833-transform-geometry-v1/TRANSFORM_GEOMETRY_THEOREMS_V1.md:9` [R5]: `…ts are architecture-name-free [[R5]]/mechanism classes already adm…` -> `Fix a registered scientific scope `Omega`. Objects are architecture-name-free mechanism classes already admitted by the `
- `gmi-833-transform-geometry-v1/TRANSFORM_GEOMETRY_THEOREMS_V1.md:87` [R5]: `…frozen. It is not a universal [[R5]] distance.` -> `The scalar `d_w` exists only after weights are frozen. It is not a universal architecture distance.`
- `gmi-833-transform-geometry-v1/TRANSFORM_GEOMETRY_THEOREMS_V1.md:124` [R5]: `…s to architecture-independent [[R5]] classes, evidence, assumption…` -> `The residual GMI contribution at this stage is a machine-checkable transform contract that connects those parent objects`
- `gmi-833-transform-geometry-v1/TRANSFORM_GEOMETRY_THEOREMS_V1.md:142` [R6]: `…ic-kernel naturality, grammar/[[R6]] invariance, a topology of the…` -> `This tranche does not establish developmental naturality, stochastic-kernel naturality, grammar/relabeling invariance, a`

### gmi-833-update-law-nfl-v1
- `gmi-833-update-law-nfl-v1/FREEZE_V1.md:123` [R4]: `…rged branch `gmi/learning-law-[[R4]]` is non-authoritative context only. It conditionally maps registered premises/prices to five learning laws and explicitly refuses premise-free [[R4]]. This tranche does not import…` -> `The old unmerged branch whose name is `gmi/learning-law-` plus the retired legacy term (frozen identifier; exact bytes p`
- `gmi-833-update-law-nfl-v1/UPDATE_LAW_NFL_THEOREMS_V1.md:149` [R4]: `…ical branch `gmi/learning-law-[[R4]]` contains a conditional capability/price-to-law selector and explicitly refuses premise-free [[R4]]. It is useful historical cont…` -> `The unmerged historical branch whose name is `gmi/learning-law-` plus the retired legacy term (frozen identifier; exact `
- `gmi-833-update-law-nfl-v1/UPDATE_LAW_NFL_THEOREMS_V1.md:165` [R4]: `…not block useful learning-law [[R4]]. Instead it proves why such [[R4]] must state the ecological/mod…` -> `The result does **not** establish `ALL_ALGORITHMS_EQUAL_IN_REAL_WORLD`, and it does not block useful learning-law choice`


## Remaining corpus at this commit (aj lane only; not edited here)

35 hits in 12 `gmi-833-aj*` packages — identical per-package counts before and after this branch
(no-alarm check; the untouched-lane assertion):

| package | hits |
|---|---|
| `gmi-833-aj4-process-organizations-v1` | 6 |
| `gmi-833-aj9b-k01-blind-recovery-v1` | 5 |
| `gmi-833-aj9c-k02-blind-recovery-v1` | 4 |
| `gmi-833-aj9d-k03-blind-recovery-v1` | 4 |
| `gmi-833-aj5-g0-lowering-v1` | 3 |
| `gmi-833-aj9e-k04-blind-recovery-v1` | 3 |
| `gmi-833-aj9f-k05-blind-recovery-v1` | 3 |
| `gmi-833-aj5-g0-compilation-v1` | 2 |
| `gmi-833-aj7-objective-provenance-v1` | 2 |
| `gmi-833-aj0-foundation-scope-v1` | 1 |
| `gmi-833-aj6-aj8-development-value-intelligence-v1` | 1 |
| `gmi-833-aj8-intelligence-boundary-v1` | 1 |

Verification invocation (exit 0 expected; residual empty). Run under `bash` — zsh does not
word-split the unquoted command substitution, which would hand the gate one malformed id instead
of 17 (a malformed id suppresses nothing, so the run stays honest, merely noisy):

```bash
python3 -I research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py \
  $(ls -d research/gmi-833-*/ | grep -v 'gmi-833-aj') --context paper-facing \
  --acknowledge $(python3 -c "import json;print(' '.join(p['id'] for p in json.load(open('research/gmi-833-terminology-migration-v1/ACKNOWLEDGED_FINDINGS_V1.json'))['pairs']))")
```

Claim ceiling is unchanged (`TERMINOLOGY_MIGRATION_AT_GMI_833_PAPER_FACING_SCOPE`, freeze §5);
aj-lane packages remain open work for their own lane, and post-v2 landings still add migration
work at landing time.
