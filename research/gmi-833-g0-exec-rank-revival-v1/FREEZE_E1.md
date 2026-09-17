# GMI #833 Section-E E9 exec-cost rank revival freeze

**Parent:** #833 Section E / #897 follow-up (revival of the tranche-2 GAP-E8-3 rank-fragility lead)
**Base packages:** `research/gmi-833-g0-grammar-growth-v1` (freeze `10f0ef37`, merged #945),
`research/gmi-833-g0-grammar-growth-v2` (merged #978, commit `636a53fb`)
**Source main:** `636a53fb9fdae949aad85131f44e5c78389839c3`
**Status:** pre-implementation formalism/fixture/claim freeze

This file freezes, before any E9 implementation exists on this branch, the rules,
spaces, witnesses, nulls and criteria that repair the cost-fragility recorded in
`SCIENTIFIC_LEDGER_V2.json` GAP-E8-3's rank note: under EXEC-B at ρ=1, 19/200
equal-cardinality random-admission nulls beat the v1 recursive library
(exec net −395,484 vs null min −396,644), while under the count metric 0/200 beat
it (count net −48,739 vs null min −48,373's typo-check: −48,737). All v1/v2
machinery (GRW-1, INV-1, T3 burden DP, EXEC-B per-op model, T8 exec DP, NULL-2
unranking, hostile conventions) is imported unchanged and reused; this freeze
only registers additions. Design derivations were computed off-Mac on
`billy-laptop` with the merged v1/v2 modules only (probes archived in the
package under `design/`); every registered expectation below is probe-verified
and carries an honest-failure clause — if a frozen rule computes a different
value, that is the result and the witness row fails; fixtures are not retuned.

## 1. Scope and claims ceiling

E9 claim ceiling (additive to v1's and v2's):

```text
GMI_833_E9_EXEC_RANK_REVIVAL__BOTH_METRIC_RANK1_WITNESS_BY_NESTING_LADDER__EXACT_AFFINE_EXCHANGE_LAW__STRUCTURE_CLASSIFICATION_AT_REGISTERED_SCOPE
```

Forbidden promotions: the v1 list verbatim, the v2 list verbatim, plus
`RECURSIVE_LIBRARY_EXEC_OPTIMAL` (closed negative, earned-by-counterexample:
the exec-argimal library on every battery corpus is flat),
`SINGLE_JOINT_CHARGE_ACHIEVES_BOTH_METRIC_RANK1` (closed negative for the
frozen five-charge class, earned-by-construction),
`UNIFORM_IN_RHO_RANK1`, `CLOSURE_ARGMIN_ON_C4_C5` (space cap registered),
`NESTING_LADDER_COMPLETE_BEYOND_BATTERY`. The rank-1 statements are
ensemble-relative (0/200 NULL-3 nulls strictly better) with the tie structure
reported exactly; no optimality claim beyond the frozen spaces.

## 2. Frozen formalism (additions only)

- **Nesting family (NFAM).** For a library L with admission order
  m_1..m_d (bodies over the alphabet present at their admission), the nesting
  family NFAM(L) is the set of 2^d libraries obtained by choosing, per level k,
  the level body either as invented (nested, over the current alphabet of the
  k-th admission) or flattened (its full base expansion). The flattening of L,
  `flat(L)`, chooses flat at every level. Members preserve macro names, count,
  admission order and canonical symbol order; only bodies differ.
- **Rung selection (derived rule, zero constants).** For accounting M ∈
  {count, exec(ρ)}: `rung_M(L) = argmin_{L' ∈ NFAM(L)} Net_M(L')` (ties broken
  by the v1 expand-word key on the flattened second-macro body, then by more
  nesting). W_M = rung_M(invented library). This is the *library instance
  adapting to the cost model* — a post-invention refinement over the invented
  chain, not a new invention rule.
- **Fast certified DPs.** The package computes burdens with position-matched
  segmentation DPs (identical integer arithmetic to `v1.burden_dp` /
  `v2.exec_burden`; the S-table is filled from precomputed position→symbol
  matches). Agreement with the frozen v1/v2 implementations is asserted exactly
  on the registered spot sets at ρ ∈ {0,1,4} (HEXR-1) — certification, not
  re-derivation.
- **Search spaces (per corpus, frozen).**
  SPACE-full (v1ref, trap1, trap3): all libraries reachable by any sequence of
  strictly-positive-count-gain admissions under the INV-1 mechanics (no
  candidate pruning), plus their flattenings, plus all G0-pool subsets of size
  ≤ |L_inv|+1 when the materialized subset count ≤ 20,000.
  SPACE-c3: as SPACE-full but the sequential closure extends only the top-10
  candidates per state in the frozen INV-1 tie order (T=10 frozen; probe
  closure = 228 states; no pool subsets — 27,840 > cap).
  SPACE-chain (c4, c5): NFAM(L_inv) only (the uncapped closure exceeds the
  registered state cap 1,500; no closure or argmin claim is made on c4/c5).
- **Exec-MDL gain (for the degeneracy theorem).**
  `gain_execMDL(u) = −ρ·o(u) − exec_ρ(u) − κ` — the exact exec-accounting
  analogue of the v1 charged corpus-compression gain (admitting u as m: every
  rewritten occurrence costs ρ + exec(body) instead of exec(body), definition
  charged exec(body) + κ).
- **Charge class (for the exhaustion registration).** Φ ∈ {count, exec,
  max(count, exec), count+exec, count+dispatch}: for candidate body u over the
  current alphabet, Φ_count = |u|+κ, Φ_exec = exec_ρ(u)+κ, Φ_max = max of the
  two, Φ_sum = |u|+κ+exec_ρ(u)+κ, Φ_countdisp = |u|+κ+ρ·(#macro symbols in u).
  Invention = INV-1 mechanics with gain o(u)(|u|−1) − Φ(u), frozen v1 tie-break.

## 3. Registrations

**EXR-1 (both-metric rank-1 witness).** On every battery corpus
{v1ref, c3, c4, c5, trap1, trap3} with frozen suites (v2 fixtures by hash;
v1ref by v1 fixtures): W = the exec-argmin rung rung_exec(L_inv) at ρ=1 (on
trap1/trap3 the invented library is already flat and W = L_inv's space argmin
{ab,abab} / {ab} — see EXR-3). Registered expectations (probed):
0/200 NULL-3 nulls strictly better under count AND 0/200 under exec at ρ=1,
on all six corpora. Tie census reported: identity draws only (v1ref 19/200
both metrics; trap1 4/200; trap3 16/200; c3: the flat rung is pool-drawable —
ties counted as measured; c4/c5: the flat rung's deepest body (W_k c W_k
expansion) is NOT a corpus subword, hence not drawable — strict margins,
min margin reported). Break-even scans to 2^10: v1ref W ρ†=314 vs L_inv 164;
trap1 W 53 vs 5; trap3 W 41 vs 1; c3/c4/c5 both NONE-in-range (nets negative
through 1024). The v1 rank-1 claim is thereby restored under BOTH accountings,
with the witness's exec-robustness horizon strictly extended.

**EXR-2 (nesting ladder + exact affine exchange law).** Theorem T-E2: for any
L and any L̂ ∈ NFAM(L) with the same macro set, count burdens are equal,
`Net_count(L̂) − Net_count(L) = K(L̂) − K(L) = ΔK`, and
`Net_exec(L̂,ρ) − Net_exec(L,ρ) = −ρ·ΔD·V + ΔK` exactly, where ΔD·V =
Σ_m (D_L(m)−1)·(occurrences of m summed over all visited programs), with
opcost_ρ(m) = |Expand(m)| + ρ·D(m), D(m) = 1 + Σ_{macro s ∈ body} D(s).
Registered: asserted exactly for EVERY same-macro-set pair in NFAM(L_inv) on
v1ref/c3/c4/c5 at ρ ∈ {1,2,4} (probe: 4+11+11+11 = 37 pairs, all exact);
ΔK and ΔD·V reported per pair. trap1/trap3: NFAM is degenerate (already
flat), ΔK = ΔD·V = 0, asserted.

**EXR-3 (argmin structure and the corpus-structure classification).**
- v1ref (SPACE-full, 47 libraries): count-argmin = L_inv (−48,739);
  exec-argmin = flat pair (−396,644 at ρ=1; also at ρ ∈ {2,4}); the count/exec
  Pareto frontier is exactly two points. Strict rank-1 under exec is impossible
  for any library in SPACE-full (the exec-argmin lies in the null pool; any
  strictly-dominating library would beat the space argmin) — ties are
  intrinsic, reported.
- c3 (SPACE-c3, 436 libraries): count-argmin = the (ab)^4-first chain
  {m1=(ab)^4, m2=ab, m3=(m1,m1)} (−31,501,345,179,969,635); exec-argmin =
  its flattening; INV-1's greedy library is within 356 count-ops of the
  closure optimum (greedy ≠ argmin at registered scope — reported, honest).
- c4/c5 (SPACE-chain): the nesting family forms a monotone 4-point staircase
  under (count, exec); count-argmin rung = nested end, exec-argmin rung =
  flat end. No closure/argmin-beyond-chain claim.
- trap1/trap3 (SPACE-full): single-point frontier — one library
  ({ab,abab} resp. {ab}) is argmin under BOTH metrics simultaneously; the
  greedy INV-1 compression arm is beaten by 52/200 (trap1) resp. 33/200
  (trap3) nulls under count AND 49/200 resp. 33/200 under exec (the #978
  trap finding extends to exec symmetric). Classification: recursion-forming
  corpora force the count/exec frontier (the nesting ladder); order-trapped
  corpora admit a both-metric argmin.

**EXR-4 (charge-class exhaustion; the rung-2 negative).** All five Φ paths
computed on all six corpora with libraries, nets and NULL-3 ranks registered.
Expected: no Φ ∈ class invents a library with 0/200 strictly-better under both
metrics on all six corpora (probed: on v1ref Φ_exec/Φ_max/Φ_sum/Φ_countdisp
stop at {ab}, Φ_count yields the eb=19 recursive library; on trap1 all five
are trapped ({bcbc,ab}, {bc,ab} or {bc}); on trap3 all five invent {abc};
on c3/c4/c5 Φ_count (and Φ_countdisp on c4) yield L_inv which is both-rank-1
there but these same Φ fail v1ref/trap1/trap3). Earned-by-construction with
the forcing argument (T-E4): under every Φ in the class the greedy first
admission is forced (v1ref: ab; trap1: bcbc; trap3: abc) because the savings
term o(|u|−1) strictly dominates the charge gap; after the forced first
rewrite the witnesses' bodies are not corpus subwords (trap-mechanism), so no
sequential charge rule reaches them.

**EXR-5 (exec-MDL degeneracy theorem).** T-E3: for every candidate u of every
battery corpus and every ρ ∈ {1,2,4}, gain_execMDL(u) < 0 strictly; the
exec-accounting corpus-MDL invention problem has the empty library as its
unique optimum. Corollary registered: the exec benefit of a library is
enumeration-horizon-side (hit-length shortening), never corpus-exec-side —
the v1 invention mechanism has no exec-MDL analogue, which is WHY the ladder
refinement (not re-invention) is the correct revival instrument.

**EXR-6 (fast-DP certification).** Fast vs frozen exact agreement on: all 12
v1ref H+ targets under L_inv at ρ ∈ {0,1,4}; all trap1/trap3 suite targets
under L_inv at ρ ∈ {1,4}; c3 T1 tier under L_inv at ρ ∈ {1}. Any mismatch
fails the receipt.

**EXR-7 (rung selection semantics).** rung_exec at ρ ∈ {1,2,4} selects the
fully-flat rung on v1ref/c3/c4/c5 (monotone ladder: each un-nesting strictly
decreases exec net when ρ·ΔD·V > ΔK — verified per step) and the identity on
trap1/trap3; rung_count selects the nested end on v1ref/c3/c4/c5 (count
charges strictly prefer small bodies) and the identity on traps.

## 4. NULL-3 (both-metric null ensembles)

NULL-2 machinery verbatim (frozen seeds 0..199, frozen hash, unranking,
equal cardinality |L_inv|, K charges in count-symbols as frozen in v2), run
per battery corpus for BOTH metrics (count; exec at ρ=1). Reported per
corpus: min/median/max, strictly-better counts and tie counts against L_inv,
W and every NFAM(L_inv) rung; drawn-combo signature census against W's
signature (identity-die proof where drawable).

## 5. Hostile battery (fail-closed)

| id | attack | required terminal |
|----|--------|-------------------|
| HEXR-1 | fast DPs vs frozen v1/v2 DPs on registered spot sets | exact agreement |
| HEXR-2 | one opcost perturbed by +1 in the ladder identity | affine-law check must FAIL (tamper-evidence) |
| HEXR-3 | expansion preservation across every NFAM rung | zero mismatches |
| HEXR-4 | unranked vs materialized subsets on feasible pools | identical sequences |
| HEXR-5 | empty library | Net = 0 identically under both metrics |
| HEXR-6 | poisoned H+/H− before invention | library byte-identical |
| HEXR-7 | cyclic body injected into a rung | `RECURSIVE_LIBRARY_CYCLE`, unchanged |

## 6. Discipline and ledger appends

- `research/gmi-833-claim-discipline-v1/`: new authored module
  `authored_e9_append.py` + assembler `assemble_e9_append.py` producing
  `REGISTRATIONS_E9_APPEND.json` = deep copy of REGISTRATIONS_V2.json with
  exactly one change: the `gmi-833-g0-grammar-growth-v1` claim object's
  `forbidden_extrapolations.content` gains the E9 metric-conditionality note
  `METRIC_RELATIVE_RANK1` (the rank-1 claim is metric-conditional; restored
  under both accountings by the E9 nesting-ladder witness; see
  gmi-833-g0-exec-rank-revival-v1) with status `APPEND_E9_EXEC_RANK_REVIVAL`
  and source this package. V1/V2 registers are never written; the assembler
  asserts byte-integrity of both and deep-equality elsewhere. The
  reconciliation row note in the v1 package's
  `ISSUE_833_RECONCILIATION_GRAMMAR_GROWTH_V1.json` is appended (additive
  `e9_note` field) — no replacement row is touched.
- `research/gmi-833-g0-grammar-growth-v2/SCIENTIFIC_LEDGER_V2.json`: append
  the E9 revival record (additive `revival_records` list entry; existing keys
  untouched).

## 7. Receipt, oracle, CI

`exec_rank_revival_v1.py` imports v1+v2 (same directory) and reuses their
machinery; receipts are exact-integer, byte-identical under `-B` and `-O -B`
and across CPython ≥3.8. `independent_oracle_v1.py` recomputes without
importing the main module, USING the frozen v2 slow engine (`v2.exec_burden`)
as the independent implementation: v1ref and trap full verdicts (witness
nets, null sub-ensemble 40 seeds, both metrics), all NFAM rung nets on all
six corpora, the affine-law identities, and the exec-MDL degeneracy scan on
v1ref/trap pools. The dedicated workflow pins this freeze commit (which must
precede every implementation artifact), pins the v1/v2 fixture hashes,
verifies fixture sha256, runs tests + receipt/oracle byte-compares in both
modes, validates the claim ceiling, asserts the committed receipt's headline
integers, and runs the discipline-append integrity check.
