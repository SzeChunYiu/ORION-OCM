# Z2 row-3 site classifier — post-publication instrument repair (issue #1049)

This is a repair of the instrument, recorded after publication. It is not a
freeze amendment. The universe, learners, invariance table, nulls, verdict
predicate `H9` ("the `LIVE_FLAGSHIP` category is empty") and forbidden
promotions are unchanged, and no row is reconciled here.

## What happened

On `main` at `cc36a309` the Z2 workflow failed. `check_row3_verdict_v1.py`
and `test_09_MP7_corpus_has_no_live_flagship_site` reported 7 `LIVE_FLAGSHIP`
sites. Each one is line 11 (line 22 in the belief-state package) of the
`FREEZE_V1.md` of a merged Section-H real-scale package:
`associative-memory`, `belief-state`, `decision-trees`, `diffusion-refinement`,
`model-free-rl`, `nearest-neighbor` and `particle-population`. Each line quotes
the #833 section header inside a code span:

```
Section of the issue: the `# H. Prior-free derivation of known
```

None of these lines claims anything. The header is the issue's own title,
quoted verbatim as the reconciliation `anchor`. This is the same defect class
amendment 4 recorded (a checker that cries wolf on real input). The
`ROW_MARKERS` rule recognised a quoted row or header only when it opened the
physical line, and here the quotation sits after other words.

## Repair

A backtick code span whose content begins with an issue header marker
(`# X.` / `## X.`) or a checklist marker (`- [ ] ` / `- [x] `), and which itself
carries the token, is classified `MIRROR`. The span may run past the end of
the line, which covers a header quoted across a line break. A span that holds
only the marker, with the token outside it, gives no shelter.

The validation set grows so that the repair is covered both ways:

- **New planted negatives, which must stay quiet:** the header quoted inline
  and continued across a line break, and the header quoted inline with the span
  closed on the same line.
- **New planted positive, which must fire:** `` Under the `# H.` header our
  recovery is ... throughout `` — a live claim beside a quoted marker.

## Result on the live corpus (this branch)

709 markdown files, 98 occurrences, 0 `LIVE_FLAGSHIP`. Validation: 5 of 5
planted positives fire, and 8 of 8 planted negatives and the clean line stay
quiet. `check_row3_verdict_v1.py` holds. `test_z2_minimal_prior_v1.py` passes
under both `-I -B` and `-I -O -B`. `PRIOR_FREE_SITE_AUDIT_V1.json` is
regenerated. The workflow regenerates it live and never byte-checks it.
