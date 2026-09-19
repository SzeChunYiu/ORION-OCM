# Z2 freeze amendment 4 — the row-3 site classifier fired three false positives

Committed **before** any receipt, result file or reconciliation of this package
is committed, and before the repaired classifier's verdict is used anywhere.
`source_main`, the claim ceiling and the five reconcilable rows are unchanged;
no neighboring row is earned here.

## 1. What happened

The first run of `prior_free_site_audit_v1.py` over the live
`research/gmi-833-*` markdown corpus at `source_main` returned `74`
occurrences, `3` of them in the `LIVE_FLAGSHIP` category — the category
`H9` claims is empty. Its own validation gate passed: both planted positives
fired and all three planted negatives stayed quiet.

Every one of the three is a **classifier defect**, and each is a different
defect. They were found by reading all three sites, which is the only reason
they are not in this package's receipt as a finding:

| site | text | why it is not a live flagship claim | defect |
|---|---|---|---|
| `research/gmi-833-z-map-v1/Z_STRUCTURAL_MAP_V1.md:79` | ``the `prior-free` → `architecture-uncommitted` terminology migration already has a lane`` | the token is *mentioned*, inside backticks, while naming the migration itself; nothing is claimed prior-free | no use/mention distinction |
| `research/gmi-833-corpus-audit-close-v1/FREEZE_V1.md:84` | "…recorded as a screened/not-screened status …, **never** as / a proof of prior-freeness." | it is a negation; the negation marker `never` sits on the previous physical line | classification scoped to one physical line |
| `research/gmi-833-z-z15-decisive-falsifiers-v1/CORE.md:101` | "it does `**not**` mean prior-free" | it is a negation; markdown emphasis inside the phrase defeats the literal marker `does not mean` | markdown emphasis not normalised |

A checker that cries wolf on its first real run is a checker that gets switched
off, and the planted-negative set that cleared it did not contain a single one
of these three shapes. The validation was real but its coverage was not, which
is the defect worth recording: *a validation gate is only as strong as the
shapes it plants.*

## 2. Repair, fixed before the repaired verdict is used

- **Normalise markdown emphasis** (`*`, `_`, backticks) out of the text before
  negation-marker matching, so `does **not** mean` matches `does not mean`.
- **Classify at sentence scope**, using the occurrence's physical line joined
  with the preceding physical line, so a negation carried across a line break is
  seen.
- **Add a sixth category `MENTION_NOT_USE`** to `FREEZE_V1.md` §6: the token
  appears inside backticks or inside a `->`/`→` migration arrow, i.e. it is
  named rather than asserted. The five original categories are unchanged and
  `LIVE_FLAGSHIP` keeps its meaning exactly.
- **Extend the planted-negative set** with the three shapes above plus a
  cross-line negation and a bolded negation, and **extend the planted-positive
  set** with a bolded live claim and a live claim on a continuation line, so the
  gate covers the repairs rather than merely re-passing.

`H9` is unchanged in content: the `LIVE_FLAGSHIP` category must be empty. If a
genuine live site survives the repair it is published as a finding and row 3 does
not close.

## 3. No other change

The universe, the learners, the invariance table, the specification vocabulary,
the nulls, the other hostiles and the forbidden promotions stand as written.
