# gmi-833-h-real-scale-classical-v1 — CORE

**What this is.** Real-scale evidence for the four classical named-family rows of
Issue #833 Section H — finite-state/automata, linear regression/classifiers,
GLMs, basis/kernel methods — with **all eleven** Section-H requirements earned at
**one scope per row**.

**The architectural decision, made in the freeze.** The parent
`gmi-833-h-neutral-four-family-v1` already holds ten of the eleven for these same
four rows at `SIGMA_4F`, a finite `Z3` scope, with
`open_gate = real_scale_test`. Adding an eleventh certificate at a real scale and
declaring the conjunction is `CROSS_SCOPE_GATE_COMPOSITION` — forbidden by
`gmi-833-h-family-requirement-ledger-v1` `HRL-1` and proved invalid by PR #997
`FGS-2`, whose countermodel covers ecology and budget drift explicitly.
**This package therefore imports no certificate from `SIGMA_4F` and earns
eleven at each of its own four scopes.** See `REAL_SCALE_CLASSICAL_THEOREMS_V1.md`
`RSC-1`.

**Real-scale, defined before implementation** (`FREEZE_V1.md` Section 7): every
input value read from a sha256-bound, externally originated source, verified at
run time; `n_fit >= 100,000` and `n_held >= 20,000` at every scope; at least two
arms fitted at that scale; every claimed number computed in exact arithmetic on
rows no arm was fitted on; resource accounting charged at the real index-set
size. It licenses nothing about frontier models, no other data, no other
ecology, no transport to another scope, and neither `M5` nor independent-team
replication.

## Real sources

| id | source | size | sha256 |
|---|---|---|---|
| `D1` | `/usr/share/dict/words` | 972,398 B | `f6c94d35…f4414` |
| `D2` | 9 × `/usr/share/sounds/alsa/*.wav`, 16-bit mono PCM | 614,266 frames | dod `a9f67729…b7a7a` |
| `D3` | 659 × `/usr/lib/python3.8/**/*.py` | 11,219,129 B | dod `41607de5…c9ec9` |

## The one grammar

`grammar_v1.py` + `grammar_v2.py`. Leaves `ARG PARAM ACC S BIAS STATE C0 C1`;
operations `ADD MUL NEG ABS STEP RECIP`; one generic indexed accumulate; one
delay cell. 116 body expressions (≤3 nodes) and 8,155 head expressions (≤5
nodes), exhaustively enumerated and semantically quotiented before any ecology
is loaded, giving **12,614 candidate pairs**. One digest, unchanged across all
four scopes. The generator receives no family name, no family identifier and no
family-specific candidate list; structural names are attached after selection by
a classifier that reads only the expression tree.

## Reproduce

```bash
cd research/gmi-833-h-real-scale-classical-v1
python3 -I -B  independent_oracle_v1.py      # route B, source-separated
python3 -I -B  real_scale_classical_v1.py    # route A, eleven-gate ledger
python3 -I -O -B test_real_scale_classical_v1.py -v
```

Stdlib only, no third-party dependency, exact `Fraction`/integer arithmetic
throughout, Python 3.8-compatible. Floats appear only inside stage-1 fitting
routines whose rationalised output is thereafter treated as data.

Stage 1 needs `D1`–`D3` and runs on laptop-billy only:

```bash
python3 -u run_real_scale_v2.py H01|H02|H03|H04   # search, fit, exact evaluate
python3 -u run_search_sample_v1.py                # survivors + real search sample
python3 -u run_controls_v2.py                     # twins, nulls, automaton
```

## Custody

`FREEZE_V1.md` was committed alone, before any executor existed;
`FREEZE_V1_ECOLOGY_ADDENDUM.md` before any byte of `D1`–`D3` was read;
`FREEZE_V1_SEARCH_AMENDMENT.md` before any held-out slice was read; and
`FREEZE_V2_ADDENDUM.md` before any V2 receipt existed. `git log
--diff-filter=A` order is the record and CI asserts it in both directions.

## The revival pass, in the open

The V1 pass ran to completion and **three of its four structural predictions
failed**. Its receipts and logs are committed unchanged in `REAL_RUNS_V1/`.
Each failure was attributed to exactly one stage and met with one matching
lever (`FREEZE_V2_ADDENDUM.md`): a 4-node head budget cannot contain three
distinct leaves, so no parameterised state update existed in the grammar at all;
a time-ordered sliding-window presentation is not a regression ecology, and the
search correctly preferred an integrator over an affine score; and squared error
is the identity-link criterion, so no link can be recovered under it. The slice
residues were rotated so the V2 predictions are resolved on rows V1 never
evaluated. **This is the only revival pass**; a row whose prediction failed
again is reported open with its attribution.

## Receipts

See `RESULT_V1.json` for every number, `REAL_SCALE_CLASSICAL_THEOREMS_V1.md`
`RSC-1..RSC-6` for the named results and their falsifiers, `PARENT_LEDGER.md`
for what is not claimed novel, and
`ISSUE_833_RECONCILIATION_H_REAL_SCALE_V1.json` for the rows this package
closes. The issue body is not edited by this package.
