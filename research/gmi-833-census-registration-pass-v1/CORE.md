# CORE — `gmi-833-census-registration-pass-v1`

**Issue #833, section AA feeder. Closes no row.** Claim ceiling
`SOURCED_PROPAGATION_REGISTER_V1`.

The frozen corpus census registers five list fields and two level fields on
22553 objects and populates none of them (`gmi-833-aa-fallacy-detectors-v1`
measured it; `#949` reported it). This package fills those fields **only from
evidence already committed on `main`**, by exact identity, with one pointer per
written entry, and lists every object it refused to populate. The frozen
census is not edited; this register supersedes it by reference, the way
`SCORES_V3_DELTA.json` supersedes `THEOREM_SCORES_V2.json`.

## Population, before → after (exact, over 22553 objects)

| field | before | after populated | after not populated | how |
|---|---|---|---|---|
| `maturity_level` | 0 (all `UNKNOWN`) | **172** | 22381 `UNKNOWN` (22380 unbound + 1 bound-but-scored-UNKNOWN) | 173 scored rows bound by B1 (145) / B2 (28); v3 delta applied to `W4-C` |
| `evidence_level` | 0 | **170** | 22383 `UNKNOWN` (22380 unbound + 3 bound-but-scored-UNKNOWN) | same binding |
| `assumptions` | 0 | **173** | 22380 `UNREGISTERED` | registrations on bound rows |
| `falsifiers` | 0 | **173** | 22380 `UNREGISTERED` | same |
| `forbidden_extrapolations` | 0 | **173** | 22380 `UNREGISTERED` | same |
| `strongest_parents` | 0 | **179** | 22374 `UNREGISTERED` | 173 registrations + 9 `STRONGEST_PARENT_DECLARED` edges |
| `claim_dependencies` | 0 | **30** objects / 113 edges | 22523 empty | 153 resolved edge records, 12 refused |

Populated records in the delta: **202**. Pointers checked: **1895**, findings
**0**. `UNREGISTERED` is a *string* on a list field, so an empty list can never
be mistaken for it, and 0 populated lists are empty.

## Gap graph

`materiality` re-graded by AAG-3's proved threshold: **847 MATERIAL / 293
CRITICAL** (reproduced exactly; distinct values 1 → 2; 0 monotonicity
violations). `descendants`: **50** of 1140 gaps gain a non-empty set (59
direct, 62 closed); **1090** remain isolated.

## Decidability of AA16–AA37 (the deliverable number)

Of the 19 rows the fallacy lane left undecidable, **5** now have a registered
discriminator — AA24, AA25, AA26, AA27 via the `assumptions` ledger and AA33
via the registered statistical-claim family count plus that ledger — and 1
(AA21) was already decided elsewhere. **13** have no register field carrying
the input they need (logical form, causal assertion, identifiability,
equivariance outcome, objective form, search budget, ecology sample, leakage
ledger, sample size, latent structure). The binding sparsity is
**`assumptions` at 173 / 22553**: AA24/AA25 are evaluable on 15 objects,
AA26/AA27 on 173, AA33 on 10. That is small, and it is the finding: the
register is exact where it exists and it exists on 0.77% of the corpus.

## What was refused, and why

- 24 `ARRIVAL` rows + 1 v3 arrival: package-level results in packages holding
  **0** census objects (they post-date the frozen source). 62 package-level
  registrations likewise.
- 12 dependency-edge records: 6 `AMBIGUOUS_CHILD_IDENTITY` (`FAC-CTW`
  declared 6×, `CAU-1` declared 17×), 6 `NO_OBJECT_AT_CITATION`. All listed in
  `REFUSALS_V1.json` with layer, index, citation and declaration count.
- 0 legacy scored rows; a loose prefix variant would have added 0.

## Reproduce

```sh
python3 -I -B  research/gmi-833-census-registration-pass-v1/registration_pass_v1.py
python3 -I -B  research/gmi-833-census-registration-pass-v1/independent_registration_oracle_v1.py
python3 -I -B  research/gmi-833-census-registration-pass-v1/test_registration_pass_v1.py
python3 -I -O -B research/gmi-833-census-registration-pass-v1/test_registration_pass_v1.py
python3 -I -B  research/gmi-833-census-registration-pass-v1/check_receipt_v1.py
```

Stdlib only; Python 3.8+; every quantity an `int` or exact `Fraction`. Route A
rewrites `REGISTER_DELTA_V1.json`, `GAP_GRAPH_V2.json`, `DECIDABILITY_V1.json`
and `REFUSALS_V1.json` byte-identically (CI asserts a clean diff). 31 tests in
both modes; two routes agree by set equality on every set the receipt reports.

## Files

| file | what |
|---|---|
| `FREEZE_V1.md` | pre-implementation freeze (committed alone, first): rules B1/B2, edge resolution, sentinel semantics, decidability classification, hostiles, null |
| `CENSUS_REGISTRATION_THEOREMS_V1.md` | CRP-1..CRP-5 with all four ledgers |
| `registration_pass_v1.py` | route A; writes the four artifacts; runs pointer/descendant verifiers, hostiles, null |
| `independent_registration_oracle_v1.py` | route B; imports nothing from A |
| `test_registration_pass_v1.py` | 31 tests |
| `check_receipt_v1.py` | builds / verifies `RESULT_V1.json` and `ORACLE_RESULT_V1.json` by equality |
| `REGISTER_DELTA_V1.json` | the populated register (202 records, provenance per entry, package-level results) |
| `GAP_GRAPH_V2.json` | 1140 gaps with `materiality`, `materiality_index`, `descendants` |
| `DECIDABILITY_V1.json` | per-row table AA16–AA37 |
| `REFUSALS_V1.json` | every refusal with reason |
| `HANDCHECK_V1.md` | 20 objects read by hand against their pointers (12 populated, 8 that must stay unpopulated) |
| `MANIFEST_V1.json`, `ISSUE_833_RECONCILIATION_CENSUS_REGISTRATION_V1.json` | pins; reconciliation with an empty `replacements` list |
