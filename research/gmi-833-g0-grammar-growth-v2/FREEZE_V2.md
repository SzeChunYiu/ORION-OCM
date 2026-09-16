# GMI #833 Section-E E8 grammar-growth tranche-2 freeze

**Parent:** #833 Section E / #897 follow-up (issue closed; results land as comments)
**Base package:** `research/gmi-833-g0-grammar-growth-v1` (freeze `10f0ef37`, merged #945)
**Source main:** `9cb5197fb09a781b65be09abcd2fbeca0fd759fb`
**Status:** pre-implementation formalism/fixture/claim freeze

This file freezes, before any tranche-2 implementation exists on this branch, the
corpora, suites, rules, metrics and criteria that close the three gaps recorded
in `SCIENTIFIC_LEDGER_V1.json`: GAP-E8-1 (deeper generational chains), GAP-E8-2
(admission-rule economics head-to-head), GAP-E8-3 (execution-cost burden
variant). All v1 machinery (GRW-1, INV-1, T3 burden DP, T4 lemma, THR-1,
NULL-1, hostile battery) is imported unchanged and reused; this freeze only
registers additions. Machine fixtures: `FROZEN_FIXTURES_V2.json` (this commit).
Design derivations were computed off-Mac on `billy-laptop` with the v1 module
only; every registered expectation below is probe-verified and carries an
honest-failure clause — if a frozen rule forms a different library, that is the
result and the witness row fails; fixtures are not retuned post hoc.

## 1. Scope and claims ceiling

Tranche-2 claim ceiling (additive to v1's):

```text
GMI_833_E8_TRANCHE2_DEPTH3_FORMATION__TIER_CONDITIONAL_COMPOUNDING__ADMISSION_RULE_ECONOMICS__EXEC_COST_ROBUST_AT_REGISTERED_SCOPE
```

Forbidden promotions: the v1 list verbatim, plus `DEPTH_4_PLUS_FORMED`,
`UNIVERSAL_DEPTH_GROWTH`, `COMPRESSION_GATE_DOMINATES`, `UTILITY_GATE_DOMINATES`,
`EXEC_INVARIANT_ALL_RHO`. Neither admission rule is claimed dominant; no
open-ended growth is claimed; the exec-cost robustness claim is per registered
ρ grid with an exact break-even, not uniform in ρ.

## 2. Frozen corpora (all explicit in fixtures; words are strings over {a,b,c})

| id | corpus | S_0 | designed for |
|----|--------|-----|--------------|
| `c3` | 4×(ab)^8 + 19×'ab' | 102 | depth-3 witness, pure-run shape |
| `c4` | 4×W3 + 50×'ab' | 240 | depth-4 attempt (W1=(ab)^4, W_{k+1}=W_k c W_k; W3=35 syms) |
| `c5` | 4×W4 + 117×'ab' | 518 | depth-5 attempt (W4=71 syms) |
| `trap1` | 4×'bcbc' + 2×'abab' + 2×'ab' | 28 | partial waste (useless macro + useful one) |
| `trap3` | 3×'abcabc' | 18 | total swallow (greedy destroys reusable mass) |
| `v1ref` | v1 frozen corpus (by hash) | 23 | coincide arm; fixtures sha-pinned |
| family rows `fn5`,`fn8`,`fn12`,`fl8`,`fl16` | see fixtures | — | formation ceiling evidence (no eval suites) |

Expected traces at κ=1 (honest-failure clauses in fixtures):
`c3`: m1→ab (o=51,g=48), m2→(m1)^4 (o=8,g=19), m3→(m2,m2) (o=4,g=1), saturation,
depth 3. `c4`: m1→ab (o=114,g=111), m2→(m1)^4c(m1)^4 (o=8,g=54), m3→(m2,c,m2)
(o=4,g=4), saturation, **depth 3 (not 4)**. `c5`: m1→ab (o=245,g=242), m2→
(m1)^4c(m1)^4c(m1)^4c(m1)^4 (o=8,g=124), m3→(m2,c,m2) (o=4,g=4), saturation,
**depth 3 (not 5)**. `trap1`: {bcbc, ab}. `trap3`: {abc} only. Family: depth 1
(fn5/fn8/fn12: whole-program collapse), depth 2 (fl8/fl16).

## 3. GAP-E8-1 registrations

**WIT-2 (depth-3 formation, two shapes).** `c3` must form the exact pure-run
chain m3=(m2,m2) (body literally contains m2); `c4`/`c5` must form the
separator chain m3=(m2,c,m2). GRW-1 expansion preservation must hold in-trace on
every corpus (zero failures).

**SAT-1 (structural formation saturation at depth 3).** The registered claim:
under INV-1, every frozen attempt at depth ≥ 4 stops at depth 3. Mechanism
(theorem, to be proven in THEOREMS_V2 as T7): at any level ≥ 2, with P ≥ 4
programs each containing ≥ 2 repeated units, the multi-unit candidate
u^c-u-shaped or run uXu has gain strictly exceeding every unit-level candidate
that a deeper ladder would need (closed-form inequalities
`gain(u u) < gain(u u ... u)` on runs and `gain(u) < gain(u c u)` on separated
blocks for all feasible occurrence counts), so greedy admission collapses the
corpus to single symbols in exactly three admissions (symbol → maximal chunk →
program). Registered instances: `c4`, `c5` (designed depth 4/5, probed depth 3).

**ADM-ALT (rule-attribution diagnostic; no claim).** A registered diagnostic
variant — among strictly-positive-gain candidates whose body references the most
recently admitted macro prefer the frozen tie-break order; fall back to INV-1
order when none qualifies; same charges, same saturation stop — must be run on
`c4`/`c5` and reported. It is expected to form deeper chains (m4 over m3),
demonstrating the SAT-1 ceiling is attributable to the frozen greedy rule, not
to the language. It is a diagnostic only: no held-out claim is made for ADM-ALT
libraries beyond reporting their charged nets.

**CMP-1 (tier-conditional compounding; the T4 question).** Frozen tiered
held-out suites (fixtures; tiers = max k such that the target contains ≥ 2
greedy-disjoint occurrences of the depth-k macro body's expansion; assignment
registered in fixtures): for every corpus (c3: tiers 1–3; c4: tiers 3sep–4;
c5: tiers 4sep–5) and every prefix library L_g (g = 0..admissions):
(a) on each tier T, cumulative burden strictly decreases in g up to the
generation matching that tier, and the first generation past the match strictly
increases it (below-match saturation/regression);
(b) the H− control strictly increases at every g (T4 widening, monotone);
(c) aggregate charged net over the full H+ strictly decreases in g (aggregate
compounding). Probed expectations are in the fixtures; honest-failure applies.

**ECON-1 (formation economics; κ precedent extended).** For each depth-witness
corpus, the minimal filler count f* such that m1='ab' wins with a strict margin
is derived by registered bracket scans (c3: {17..20}, c4: {48..51}, c5:
{115..118}; ties land by the frozen expand-order tie-break and are reported).
The S_0-per-achieved-depth table (23 → 102 → 240/518-at-depth-3) is a derived
output, not a tuned constant. κ* per corpus = largest grid value in {0..8} at
which the registered full trace still forms (c3: 1; c4: 4; c5: 4; traps:
reported); the global primary stays κ=1 (v1 freeze); all headline verdicts run
at κ=1 with per-corpus κ* ablation rows.

## 4. GAP-E8-2 registrations (admission economics head-to-head)

**UTL-1 (utility-gated admission; g2-utility-gated-parents-v2 adapted).** Mine
the candidate pool exactly as INV-1 (same charged gains, same frozen tie-break
order). Admit the first candidate in that order whose tentative library's
**charged aggregate burden on the frozen validation suite V** (cumulative
T3-burden over V + K_total) is strictly below BOTH the primitive-only grammar's
charged V-burden AND the current library's charged V-burden (strict
improvement; the parent's primitive-only comparison plus the iterative
monotonicity conjunct). Rewrite the corpus as INV-1; iterate; stop when no
positive-gain candidate passes. Registered ablations: UTL-1p (primitive-only
conjunct), UTL-1s (stop at first reject instead of skipping). V suites are
frozen per corpus and disjoint from all H+/H− suites and training corpora;
leakage hostile HLK-2 must show poisoned H+/H− leave both arms' libraries
byte-identical (V influencing admission is the gate's function, not leakage).

**H2H-1 (head-to-head verdicts; same burden metric, same charges, same nulls).**
On {v1ref, c3, c4, c5, trap1, trap3}: run INV-1 (compression arm) and UTL-1
(utility arm) at κ=1, evaluate both on the same frozen H+/H− suites with full
K_total charges, plus 200-seed equal-size random-admission nulls per arm
(NULL-2). Registered expectations (probed): v1ref/c4/c5 tie (identical
libraries); c3+V_shallow: compression strictly better (utility gate rejects
m3); c3+V_deep: tie (gate admits m3 — validation-composition sensitivity);
trap1: utility strictly better; trap3: compression net strictly positive
(regression vs primitive-only) while utility net strictly negative. Registered
verdict: **neither rule dominates** — compression fails under corpus/eval
utility mismatch (trap3 mechanism: the greedy 'abc' admission rewrites away the
reusable 'ab' occurrences — an admission-order externality), utility gating
forfeits deep-macro gains when V under-represents deep reuse. Both failure
directions are registered findings, not defects to hide.

## 5. GAP-E8-3 registrations (execution-cost burden)

**EXEC-B (frozen per-op cost model).** Executing a program = evaluating its
symbols in sequence; a base token costs 1 op; a macro costs ρ dispatch ops plus
the execution cost of its body (recursive, no memoization); exec(p) =
Σ_s opcost(s); primary ρ=1, ablation grid ρ ∈ {1,2,4}; `opcost` values are
exact integers. The **execution burden** of a target w = Σ exec(p) over every
program p the canonical v1 enumerator visits up to and including the first hit.
Exact computation (theorem T8): full-length contributions Σ_{l<ℓ*} l·A^{l−1}·C
and the lex-prefix digit-DP Σ over positions/symbols-below-hit of
A^r·(prefix+opcost(s)) + A^{r−1}·r·C, with C = Σ_s opcost(s); must agree with
naive enumeration on all feasible cases (hostile HEXEC-1).

**EXEC-1R (flagship re-run).** Recompute the v1 frozen H+/H− comparison (v1
fixtures by hash, v1 library re-derived) under EXEC-B at ρ ∈ {1,2,4}: the v1
headline survives iff H+ charged net < 0 at every grid ρ and H− net ≥ 0; the
exact break-even ρ† (smallest ρ with H+ net ≥ 0, scanned to 2^10) is reported.
Registered expectation (probed): net < 0 through ρ=128. Additionally: c3 tier
tables, all H2H-1 verdicts, and NULL-2 ensembles are re-run under EXEC-B at
ρ=1; verdict-sign agreement/disagreement with the count metric is reported as
measured.

## 6. NULL-2 (equal-size random-admission nulls)

Identical machinery to NULL-1 (200 frozen seeds 0..199, frozen hash
`((s+1)·2654435761 mod 2^32) mod C(pool,size)`, G0 candidate pool, equal
cardinality, full charges), with pool cardinalities up to 579 (c5): combination
materialization is replaced by **lexicographic combinatorial unranking**
(registered; must equal materialized enumeration on every pool where
materialization is feasible — hostile HUNR-1). Ensembles: c3/c4/c5 full
libraries on their H+/H−; both arms on all six head-to-head corpora; the v1
flagship under EXEC-B (ρ=1). Reported per ensemble: min/median/max, count of
nulls strictly beating the true library, empirical rank. The claim text quotes
measured ranks; no rank-1 is pre-required (the compounding claim rests on exact
prefix arithmetic, the null guards the any-library objection).

## 7. Hostile battery additions (fail-closed)

| id | attack | required terminal |
|----|--------|-------------------|
| HLK-2 | H+/H− poisoned before either arm runs | both arms' libraries byte-identical |
| HCYC-2 | 3-deep cyclic library (m2→(m3,a)) | `RECURSIVE_LIBRARY_CYCLE`, grammar unchanged |
| HZERO-2 | c3 at κ=2 (m3 gain exactly 0) | rejected; trace depth 2 |
| HEXEC-1 | exec DP vs naive enumeration on new libraries | exact agreement |
| HUTL-1 | V suite of unrelated-control targets only | UTL-1 admits nothing (∅ library, fail-closed) |
| HUNR-1 | unranked vs materialized null subsets | identical sequences on feasible pools |
| HSEM-2 | expansion preservation across 3-deep chains | zero in-trace failures on all corpora |

## 8. Receipt, oracle, CI

`g0_grammar_growth_v2.py` imports `g0_grammar_growth_v1` (same directory) and
reuses its machinery; receipts are exact-integer, byte-identical under `-B` and
`-O -B` and across CPython versions. `independent_oracle_v2.py` recomputes
without importing either main module: all traces, tier burdens (independent
DP + naive cross-check), exec burdens (naive where feasible), head-to-head
nets, f*/κ* derivations, and a 40-seed null sub-ensemble. The dedicated
workflow pins this freeze commit (which must precede every implementation
artifact), pins the v1 fixtures/RESULT hashes, verifies fixtures sha256, runs
tests + receipt/oracle byte-compares in both modes, validates claim ceilings
and the ledger, and asserts the committed receipt's headline integers.
