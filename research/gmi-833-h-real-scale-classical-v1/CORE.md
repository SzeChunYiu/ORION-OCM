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

## Outcome — one row closed, three reported open

| row | scope | predicted class | recovered class | gates | verdict |
|---|---|---|---|---|---|
| Finite-state/automata intelligence. | `SIGMA_H01` | `PERSISTENT_STATE` | `PERSISTENT_STATE` | **11/11** | **CLOSED** |
| Linear regression / linear classifiers. | `SIGMA_H02` | `AFFINE_SCORE` | `AFFINE_SCORE` | 10/11 | open on `R05` |
| GLMs. | `SIGMA_H03` | `NONLINEAR_LINK` | `NONLINEAR_LINK` | 10/11 | open on `R08` |
| Basis/kernel methods. | `SIGMA_H04` | `LIFTED_BASIS` | `NONLINEAR_LINK` | 9/11 | open on `R01`,`R04` |

**`SIGMA_H01` closes.** On 466,750 fit and 155,583 held-out real rows of the
sha256-bound Debian lexicon, the blind search selected
`MUL(ARG,PARAM) | ADD(NEG(STEP(STATE)),S)` — a program whose delay cell makes it
an exact five-state automaton over the 27-symbol alphabet. Its exact held-out
decision-error count is **17,557 against the blind-selected stateless program's
17,584**, and **17,584 is not beaten in any of 200 order-randomised controls**
(`0/200`): a 27-error margin on 155,583 rows that is nevertheless entirely
destroyed by permuting the order, which is what makes it sequence structure
rather than noise. The order-destroyed twin ecology selects a stateless head.
The contiguous-tail evaluation agrees (30,045 against 30,229 on 194,480 further
rows). Both routes agree; the remint slice recovers the same class; the selected
expression is exactly minimal in the grammar; the table crossover is `m* = 5`.

**`SIGMA_H02` recovered the affine score and is open on the null, not on the
science.** The selected affine arm's exact held-out squared error is **967 parts
per million of the best constant arm's** (546 ppm on the tail), and its exact
sign-decision error count is **16,708 against the majority-sign arm's 45,121**.
The registered null was nevertheless not met: 98 of 200 row-permuted design
controls beat the constant arm — because a least-squares control on a permuted
design **nests** the constant arm, so the two are indistinguishable up to a
relative `1e-4` and the comparison is a coin flip by construction. That is a
vacuous null, the same defect class as a hostile that cannot fire, and its
outcome carries no information either way. `REAL_RUNS/null_diagnostic_H02.json`
records the informative comparison on the identical 200 controls under the
identical seed — **0 of 200 beat the selected arm** — and is labelled
diagnostic-only. It is **not** substituted for the registered null and closes no
row: `R05` at `SIGMA_H02` is reported open.

**`SIGMA_H03` recovered the link and is open on the held-out comparison.** Under
the closeness criterion that A3 froze as that scope's protected interface, the
blind search selected `RECIP(ADD(ABS(S),S))` — a non-affine head that is zero
for `S <= 0` and `1/(2S)` above, so a strictly non-negative link, on a response
that is zero on 77.7% of rows. The registered `Q03c` held decisively: the
identity-link arm emits **8,336 negative predicted means** on the held-out slice
and the log-link arm **0**. `Q03b` failed: the log-link arm is strictly closer on
only **13,937 of 41,695** rows against the identity-link arm's 27,758, and its
exact SSE is **2.77x** the identity link's — reproduced in V1 and V2, held and
tail. At real scale on this ecology the link's advantage is admissibility, not
point accuracy. `R08` is open.

**`SIGMA_H04` did not recover the predicted class.** The blind search selected
`MUL(ARG,PARAM) | MUL(ADD(BIAS,S),S)` — a squared linear score. The non-affinity
is in the **head**, so the registered classifier, whose priority puts a
non-affine body first, returns `NONLINEAR_LINK` and not `LIFTED_BASIS`. The
performance side of the row is strong — the selected arm is at 44.6% of the
affine arm's held-out SSE, and the landmark kernel arm beats the affine arm at
every landmark count, reaching 35.7% at `q = 64`, with the first cost crossover
at `q* = 2` — but `Q04a` as frozen was falsified and the classifier is not
re-read after the fact to rescue it. `R01` and `R04` are open.

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
