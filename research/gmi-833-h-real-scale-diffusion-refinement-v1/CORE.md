# gmi-833-h-real-scale-diffusion-refinement-v1 — CORE

**What this is.** A Section-H real-scale measurement of issue #833 for the named
row `Diffusion/iterative-refinement systems.`, at its own scope `SIGMA_H33R`,
on a sha256-bound external real source (`/usr/share/dict/american-english`,
104,334 tokens, digest `9e66281f7e51`), with exact integer decision counts and
two materially independent routes.

**It closes this row and nothing else.** The reconciliation replaces exactly the
one row, `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`, and a test
asserts that no gate certificate carries a scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Diffusion/iterative-refinement systems.` | `SIGMA_H33R` | **recovered** — 11/11 |

The family-blind winner rule over the registered readout language `R` (51 arms,
frozen pre-outcome as the registered base ladder unioned with the registered
`T*`) selects **`REFINE<=25`** — class `REFINEMENT_INDEX`, a readout whose value
is a **refinement step index** — at the held stage with **1,479** exact decision
errors against the majority rule's **5,197** (F1 need 2,598; prototype agreement
36,624 / 38,103), at the rank stage 6,057 against 11,218, and on both
regeneration halves 15,409 and 18,069 against 18,574 and 18,638 — the same class
at all four stages.

**The row's sibling channel loses by measurement, inside the same language.**
The registered single-draw family (`DRAW0`, `DRAW>=k` — the channel of
`Latent-variable generative systems.`) makes **30,557** at its best, a factor of
**20.7**; the raw cardinality family makes **5,197**, a factor of **3.5**. The
registry's own `STOCHASTIC_SOURCE_CHANNEL` contract is carried verbatim as a
**steer**, with its citation to the merged sibling package's steer reading, and
the interface this package registers — a refinement step index over a registered
sequence of stochastic perturbations — is justified in `FREEZE_V1.md` section 12
by the measured design fact that the contract's `x5` expression is a source
*address*, so a family-blind argmin over raw source-probe arms is mechanically
nearest-exemplar retrieval.

**The storable-label arm is admitted and loses.** `MEM_FALLBACK` reaches the
minimum error count at every stage and loses the registered tie-break on charged
cost at every stage: it costs **2** charged units against the refinement arm's
**1**, under the registered rule "fewest exact decision errors, ties broken by
fewer charged-cost units, then by readout name". The tie and both costs are
committed per stage in `RESULT_V1.json` under `stage_min_errors`, so the gate
sees it rather than being told it.

**The registered controls are the strongest lines, and all four fire.**
The **global** design null (seed 20261001) degrades the refinement arm 1,479 →
**6,678** (**4.52x**, past the registered 3x bar) while the cardinality arm is
**bit-identical** at 5,197 and the single-draw arm moves only to 27,553 — so
three families separate mechanically under one reassignment. The label-null
makes **10,043** against the majority's 5,197. The source-order matched
presentation control fires: under the un-permuted contiguous presentation the
registered arm makes 4,657 and does not clear the F1 margin of 2,598.

## The registered design, in one paragraph

The ecology `F33` is the **stochastic-refinement** table over the
descriptor-closure contexts of the sha-bound source: the presentation unit is
every prefix of length ≥ 2 of every token (`T_ctx` = 671,860 positions, 168,834
distinct contexts), the stored table of a slice is its one-step continuation
pairs, and a task is a held context of length ≥ 3 with at least two full-source
candidates. The registered alphabet is the source's 69 characters under the
Knuth order `(ord(c) * 2654435761) mod 2**32`, with successor `sigma`; the
presented candidate is the canonical candidate advanced by a target-free probe
offset; and the protected interface is the **refinement index** — the number of
`sigma` steps required before the presented candidate re-enters the context's
full-source support, capped at 256 — thresholded at the registered `T*`. The
labelling configuration and `T*` are fixed **before any fit** by a registered
balance criterion over four source-derived configurations, measured on the full
source with no slice, no store and no readout evaluated; the criterion's own
outcome (`T* = 25` at rate 84,340 / 168,834) is recorded in the receipt rather
than named in the freeze. The presentation is the parent's target-independent
Knuth hash `key(i) = (i * 2654435761) mod 2**32`, then the arithmetic 7:1 slice
(`n_fit` 587,877 / `n_held` 83,983, clear of the R11 bar), with a
`rank_fit`/`rank_score` split and a symmetric half-split for regeneration. The
R8 frozen-prediction record is written and flushed before any null or control is
run (38,103 rows, sha256 `26661dc087eebf63…`). Every claimed quantity is an
exact integer decision count, committed in `REAL_RUNS/` and re-derived by
route B.

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-diffusion-refinement-v1
python3 -I -B  independent_oracle_dr_v1.py                    # route B -> ORACLE_RESULT_V1.json
python3 -I -B  real_scale_diffusion_refinement_v1.py          # route A -> RESULT_V1.json
python3 -I -O -B test_real_scale_diffusion_refinement_v1.py -v # 37 tests
python3 -I -B  ci_gates_v1.py selftest                        # every gate fires on a planted positive
```

To re-run the real-scale extraction from the bound source (host of record
billy-old only, CPython 3.14.4, ~55 s):

```
python3 -B run_real_scale_diffusion_refinement_v1.py
```

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + one slice addendum | the custody chain: source, ecology, labelling criterion, sibling class, scope, claim ceiling, falsifiers; the exact slice form, the readout language `R`, the winner rule, the ladder meta-rule and the null constructions |
| `MANIFEST_V1.json` | the package manifest with source binding, scope, freeze pins and parent pins |
| `grammar_dr_v1.py` | the readout grammar `G_DR`: the closed language `R`, the post-hoc classifier, the presentation key, the digest |
| `run_real_scale_diffusion_refinement_v1.py` | the real-scale run driver; the only file that reads the real source |
| `real_scale_diffusion_refinement_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_dr_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_diffusion_refinement_v1.py` | custody, scope, slice, readout, control and reconciliation tests |
| `REAL_SCALE_DIFFUSION_REFINEMENT_THEOREMS_V1.md` | the named results, each with its four ledgers |
| `PARENT_LEDGER.md` | the assimilation ledger: what is taken from which parent and what is not |
