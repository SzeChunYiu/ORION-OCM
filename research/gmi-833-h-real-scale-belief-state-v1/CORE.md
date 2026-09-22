# gmi-833-h-real-scale-belief-state-v1 — CORE

**What this is.** A Section-H real-scale measurement of issue #833 for the named
row `Bayesian inference/belief-state systems.`, at its own scope `SIGMA_H17R`,
on a sha256-bound external real source (`/usr/share/dict/american-english`,
104,334 tokens, digest `9e66281f7e51`), with exact integer decision counts and
two materially independent routes.

**It closes nothing.** The row stays open. The package delivers one measured
boundary and the adjacent scoped positive the boundary doctrine requires, with
an empty reconciliation. `CROSS_SCOPE_GATE_COMPOSITION` is in
`forbidden_promotions` and a test asserts that no gate certificate carries a
scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Bayesian inference/belief-state systems.` | `SIGMA_H17R` | **open** — boundary reported |

The family-blind winner rule over the registered readout language `R` (frozen
pre-outcome) does **not** recover this row's intended class. On the registered
amended ecology `F17` the store's own posterior read wins at every stage —
1,005 held errors against the majority rule's 10,099 — while the best weighted-
evidence arm makes 11,421, and the registered weight-reassignment design null
separates them by 1.23× against the registered 3× bar (raw count arms
bit-identical). The stored-label read reproduces the label **exactly** (0
errors) when the store holds the whole source, so the label is storable and the
intended class is dominated rather than the coordinate being unattainable. The
recovered class is the **sibling's** `STORED_LABEL_READ_WITH_FALLBACK`; the row
is not claimed.

**Adjacent scoped positive.** On the subpopulation where the label defines a
response at all — held queries whose stored table presents at least two
hypotheses, 75,618 of 97,018 — the winner rule recovers a class with all four
stages agreeing and clears F1 (917 errors against 8,399). It is recorded,
labelled with the class actually recovered, and flagged
`claimed_for_this_row: false`.

**A registered falsifier fired and is reported.** The first-drafted claim that
the F1 coordinate was structurally unsatisfiable at this label is refuted by
this package's own measurement; `CORRECTED_CLAIM_V1.md` records the claim, the
refutation, and the corrected statement, and the ledger verdict carries
`__REGISTERED_FALSIFIER_3_FIRED`.

## The registered design, in one paragraph

The ecology `F17` is the **set-valued** word-hypothesis table over the
descriptor-closure positions of the sha-bound source: the presentation unit is
every prefix of length ≥ 2 of every token (776,142 positions), and the
hypotheses of a context `q` are the whole source words having `q` as a proper
prefix, with evidence weight `len(w)` — a fan-out-independent channel, screened
against degeneracy before the freeze (the raw token frequency is exactly 1 for
every word on this source and is excluded by registration). The registered
label is the row's two-evidence posterior: `EXT(q) >= 2` **and**
`2*MAX(q) > SUM(q)` **and** `MAX(q) >= T*`, with `T* = 8` fixed pre-outcome as
the modal source-token length of the bound source; single-completion contexts
are ties and take `0`. The presentation is the parent's target-independent
Knuth multiplicative hash `key(i) = (i * 2654435761) mod 2**32`, then the
arithmetic 7:1 slice (`n_fit` 679,124 / `n_held` 97,018, clear of the R11 bar),
with a `rank_fit`/`rank_score` split and a symmetric half-split (`fit_lo` /
`fit_hi`) for regeneration. The original sibling ecology `F15` was measured
first and is filed as the earned boundary that justifies the amendment
(`F15_EARNED_BOUNDARY_V1.md`); the amendment is registered before any amended-
ecology measurement exists, in the K05 pattern. Every claimed quantity is an
exact integer decision count, committed in `REAL_RUNS/` and re-derived by
route B.

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-belief-state-v1
python3 -I -B  independent_oracle_bs_v1.py              # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  real_scale_belief_state_v1.py            # route A, writes RESULT_V1.json
python3 -I -O -B test_real_scale_belief_state_v1.py -v  # 35 tests
python3 -I -B  ci_gates_v1.py selftest                  # every gate fires on a planted positive
```

To re-run the real-scale extraction from the bound source (host of record
billy-old only, CPython 3.14.4, ~5.5 minutes):

```
python3 -B run_real_scale_belief_state_v1.py
```

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + one slice addendum | the custody chain: scope, ecology, amnesty-free claim ceiling, falsifiers; the exact slice form, the readout language `R`, the winner rule and the null constructions |
| `F15_EARNED_BOUNDARY_V1.md` | the measured obstruction on the original sibling ecology that justifies the amendment |
| `CORRECTED_CLAIM_V1.md` | the refuted first-draft claim, the refutation, and the corrected statement |
| `MANIFEST_V1.json` | the package manifest with source binding, scope and parent pins |
| `grammar_bs_v1.py` | the readout grammar `G_BS`: the closed language `R`, the post-hoc classifier, the presentation key, the digest |
| `run_real_scale_belief_state_v1.py` | the real-scale run driver; the only file that reads the real source |
| `real_scale_belief_state_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_bs_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_belief_state_v1.py` | custody, scope, slice, readout, control and reconciliation tests |
| `REAL_SCALE_BELIEF_STATE_THEOREMS_V1.md` | the named results, each with its four ledgers |
| `PARENT_LEDGER.md` | the assimilation ledger: what is taken from which parent and what is not |
