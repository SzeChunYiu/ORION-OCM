# Experiment ledger — corpus-wide ledger-emission census

Schema: `GMI_EXPERIMENT_LEDGER_V1`. Package `gmi-833-aa-ledger-gate-v1`,
issue #833, row AA06. Experiment: measure, at
`source_main = 5e57d4292266bccf435136e1f7d72caa32e920a0`, how many named
results in the repository's theorem artifacts emit each of the four
theorem-side ledgers.

This file is one of the **planted positives** declared in `FREEZE_V1.md` §5:
`main` carries no `GMI_EXPERIMENT_LEDGER_V1` artifact at all, so the AA06 gate
would have had nothing to have recall against. It is a real ledger for a real
experiment, not a fixture.

**Leakage.** None is possible in the measuring direction: the census reads
git-tracked bytes and never trains, fits or selects on an outcome. The one real
leakage risk runs the other way — this package **authors** theorem notes and
experiment ledgers that the census then counts. It is controlled by writing the
baseline with `--exclude-prefix` over all four package directories this tranche
adds, recorded in `LEDGER_BASELINE_V1.json` under `excluded_prefixes` with its
reason, so the baseline is a picture of `main` and not of this lane's own work.
No other exclusion is applied; vendored copies under `raw/` paths are counted
and separately disclosed rather than dropped.

**Search space.** Fixed and total, not sampled: every git-tracked `research/**`
markdown path whose basename contains `THEOREM` (case-insensitive) — 329 files
at baseline — cut at level-2 ATX headings into 2345 named results. There is no
tuning loop and nothing was selected: the file predicate, the heading predicate
and the accepted label vocabulary were all fixed in `FREEZE_V1.md` §5 before the
first run, and the run produces whatever it produces.

**Cost model.** One pass over 2674 tracked markdown files, ~9 MB of text, no
network, no third-party dependency; both routes complete in seconds on one
core. The null caches per-result label sets once and runs 200 trials over the
cache, so the null costs one corpus pass, not two hundred.

**Evaluation.** The reported quantity is an integer count per ledger and a
per-result boolean, evaluated twice by materially independent parsers (route A
regex spans, route B line state machine with no regex in the parsing path) and
compared by set equality over `(path, result title)` keys, not by count
equality. A count agreement between two implementations that disagree on
*which* results are compliant would be a false agreement; set equality rules it
out.

**Sampling bias.** The corpus is enumerated exhaustively, so there is no
sampling of files. The residual bias is definitional, and it is disclosed
rather than corrected: the declared heading predicate **over-approximates**
named results — `## Scope` and `## Claim ceiling` are counted as results in
files that use `##` for sections. Over-approximation can only overstate the
debt and can only make the gate stricter, never laxer, so the declared
predicate stays primary; the conservative subset (1079 headings carrying a
result identifier or a result word) is reported alongside it as the other
bound. Six theorem artifacts expose no level-2 heading at all and are reported
in their own `unparsed_theorem_artifacts` category — "could not check" is never
merged into "checked and fine".
