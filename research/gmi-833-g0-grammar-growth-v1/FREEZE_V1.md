# GMI #833 Section-E E8 grammar-growth freeze

**Parent:** #833 Section E
**Child:** #897
**Source main:** `aa131e6d65a648754cead0fe3eaa6fde6069147d`
**Status:** pre-implementation formalism/fixture/claim freeze

This file freezes the exact finite language, cost model, deterministic invention rule, train/held-out split, hostile battery, null model and claim ceiling **before** any executor, oracle, tests, result receipt, manifest, reconciliation specification or dedicated workflow exists on this branch. The machine-readable fixtures frozen here live in `FROZEN_FIXTURES_V1.json` in this commit; every later artifact must consume them by content hash.

## 1. Scientific question and scope

The three open #833 Section-E rows are:

> Define grammar expansion `G_t -> G_{t+1}` from discovered reusable abstractions.
> Implement recursive library formation / primitive invention.
> Test whether newly invented primitives reduce future discovery cost on unseen tasks.

Target disposition: a **finite exact library-growth certificate** at registered scope — conservative monotone grammar extension with cycle rejection (GRW-1), deterministic charged-cost primitive invention from training programs only (INV-1), a frozen two-generation recursive witness (REC-1), and an exact held-out discovery-burden comparison with charged library overhead, an unrelated negative control and an equal-size random-admission null (HLD-1). This is an existence/conditional finite transfer result. It is **not** universal learning-to-learn, open-endedness, or guaranteed transfer.

## 2. Strongest-parent subsumption

Parent machinery is imported, not reclaimed:

- **#233 HST-T04**: under prefix-coded Levin-style allocation, shortening a target encoding by `Δ` multiplies its allocation weight by `2^Δ` (conditional on scheduler/execution/verification costs). Imported as the reason symbol-level description-length savings compound under allocation; the registered metric here is the exact enumerated-index burden, which is computed rather than assumed.
- **#233 HST-T05**: lifecycle macro acquisition is beneficial iff frozen future reuse savings exceed build + maintenance + expected revision cost. This child instantiates that arithmetic exactly as `H_eff * Δ > K` on the frozen finite fixture (THR-1).
- **DreamCoder** iterative wake/sleep library learning, **Stitch** corpus-guided compression, and MDL/refactoring library-learning parents generally: abstraction admission driven by corpus compression. The repository residual is the exact deterministic admission rule with every charge explicit, strict-positive net compression, syntax-independent tie-breaking, cycle rejection, and fail-closed held-out controls.
- **Merged repository parents** (pinned by blob in the post-freeze manifest):
  - `research/g2-utility-gated-parents-v2` (terminal `UTILITY_GATED_LIBRARY_BEATS_PRIMITIVE`, predecessor negative `HARMFUL_TRANSFER_LIMIT`): held-out utility gating of macro admission on the polynomial grammar. Informs the held-out design; this child's admission rule is fixed by #897 as charged corpus compression, and the held-out test measures exactly that registered rule.
  - `research/h1-amortized-rewrite-v2` (terminal `LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS`): library acquisition must be charged against later savings. This child charges build+maintenance into every held-out verdict.
  - `research/h1-amortized-acquisition-v1` (`NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER`): widening the token alphabet raises per-length enumeration volume. Under the registered burden metric this predicts — and this child must preserve rather than hide — a strict burden **regression** on held-out targets with no reusable structure, even before charges.
  - `research/gmi-833-g0-grammar-bias-v1` and `research/gmi-833-g0-cost-privilege-v1`: description-length and cost are grammar-relative unless a certified isometry holds; grammar growth is a bias operation and is registered as such. No unbiased-growth or cost-neutral-growth claim is made.

## 3. Frozen finite language (G0)

- Base token set `Σ = {a, b, c}`, frozen total order `a < b < c`.
- A **program** is a finite sequence of symbols from the current grammar alphabet; G0 programs are words over `Σ`. Binary concatenation/sequence is the only combinator.
- A grammar at time `t` is `G_t = (Σ ∪ M_t)` with macro library `M_t = {m_1, ..., m_t}`; each `m_k` has a frozen **body** `body_k`, a nonempty finite sequence over the alphabet that existed at its admission (`Σ ∪ M_{k-1}`).
- `Expand_L(p)`: recursive symbol-wise substitution of macro bodies until only base tokens remain. Full expansion terminates in base tokens iff the macro dependency relation is acyclic; a cyclic dependency must return `RECURSIVE_LIBRARY_CYCLE` and leave the grammar unchanged.
- **Protected semantics** of a program is its fully expanded base word. Two programs are semantically equal iff their expansions are equal as words.
- **Canonical symbol order** for grammar `G_t`: `a < b < c < m_1 < m_2 < ...` (macros in admission order).
- **Description length** `DL(p)` = number of symbols in `p`; every current-alphabet symbol costs 1.

## 4. Frozen cost model and discovery burden

- **Enumerator**: breadth-by-description-length over all programs of `G_t`; within a length, programs are enumerated in lexicographic order under the canonical symbol order. This is a total order on programs and is deterministic.
- **Discovery burden** `B_G(w)` for target base word `w`: the number of candidate programs enumerated, counted 1-based up to and including the first program whose expansion equals `w`. Enumeration never needs to exceed length `len(w)` because the pure-base program `w` itself exists in every `G_t`. Every enumerated program counts, including macro-using programs; alphabet widening therefore increases burdens on non-reusing targets by construction (registered, not hidden).
- **Library overhead** charged to a verdict: `K_total(L) = Σ_{m ∈ L} (|body_m| + κ)` where `|body_m|` is the definition cost in symbols (the body is written once in current-alphabet symbols) and `κ` is the per-macro maintenance charge.
- **Net held-out comparison** on a frozen set `S` of targets:
  `Net(S) = Σ_{w ∈ S} B_{G0 ∪ L}(w) + K_total(L) − Σ_{w ∈ S} B_{G0}(w)`.
  Success on the reuse-positive set is `Net < 0` strictly. The unrelated control must preserve `Net ≥ 0` (regression shown, not hidden).
- **Registered horizon**: one pass over the frozen held-out suite at the frozen charges. `H_eff` is defined on the reuse-positive set only (below).

### Maintenance charge `κ`

`κ` is a registered rational-parameter of the cost environment, in symbols per admitted macro. Primary frozen value `κ = 1`, derived by the frozen rule: the **largest** grid value in `{0,...,8}` at which deterministic invention on the frozen training corpus still forms the two-generation REC-1 witness (second-generation body exactly `(m_1, m_1)`). The derivation is computed by the receipt ablation over the full grid; every verdict additionally reports its exact break-even `κ`. No other free numeric constant exists in the cost model: definition cost is the body's own symbol count, occurrence thresholds are implied by the strict-positivity arithmetic (a body occurring once can never satisfy `o(|body|−1) > |body| + κ`), and the depth limit is derived in §5.

## 5. INV-1 — deterministic primitive invention (frozen rule)

Input: the frozen training corpus only (list of base words). No held-out data may enter candidate generation, admission, tie-breaking or stopping.

1. **Candidates**: every contiguous subword `u` of some corpus program, over the **current** alphabet, with `|Expand(u)| ≥ 2` base symbols and occurrence count `o(u) ≥ 2`. Occurrence counting is greedy non-overlapping left-to-right within each corpus program (this is exactly the count the rewrite realizes).
2. **Gain arithmetic**: with current corpus symbol count `S`, candidate `u` of current-alphabet length `b = |u|`,
   `charged(u) = b + (S − o(u)(b−1)) + κ` and admission requires `charged(u) < S`, i.e. `gain(u) = o(u)(b−1) − b − κ > 0` **strictly**.
3. **Tie-break key** (frozen, syntax-independent on expanded body): order candidates by `(-gain, Expand(u) as base word under a<b<c, u as a symbol tuple under canonical symbol order, first occurrence (program index, offset))`. Admit the first; no family or target labels participate.
4. **Admission**: new symbol `m_k -> u`; rewrite every corpus program by the same greedy non-overlapping replacement; grammar grows monotonically (`G_(t+1) = G_t ∪ {m_t}`); every old program stays legal and its expansion is unchanged.
5. **Iteration**: repeat over the current alphabet (later bodies may use earlier macros; cycles forbidden) until no candidate has positive gain or `D_reg` admissions have occurred, with `D_reg` = initial corpus symbol count `S_0` (each admission strictly reduces the corpus symbol count by at least `o(b−1) ≥ 1` and the count is nonnegative, so `S_0` is a derived stopping bound, not a tuning parameter).

## 6. GRW-1 — conservative expansion (proof requirement)

For every admitted macro library `L` produced by the frozen rule, and for the hostile cyclic cases:

1. every program legal under `G_t` is legal under `G_{t+1}` with identical expansion (monotone conservative growth);
2. every program using `m_k` has the protected semantics of its full expansion;
3. a macro whose body transitively references itself (directly or through a longer cycle) returns `RECURSIVE_LIBRARY_CYCLE` and leaves the registered grammar byte-identical.

The proof is by induction on the topological order of the macro dependency DAG (written up in the post-freeze theorem note) and is mechanically checked on all registered libraries plus hostile cyclic libraries.

## 7. REC-1 — recursive library witness (frozen expectation)

The frozen training corpus is designed so the frozen rule must form at least two generations: `m_1 -> (a, b)` and `m_2 -> (m_1, m_1)` with full base expansion `(a, b, a, b)`. The certificate must show `m_2`'s body literally contains `m_1` (genuine recursive expression, not an independent re-encoding of `a b a b`), the dependency DAG is acyclic, and expansions preserve exact base-word semantics at every generation. If the frozen rule forms a different library, that is the honest result and the REC-1 row fails; the fixture is not retuned post hoc.

## 8. HLD-1 — held-out discovery-cost test (frozen split and criteria)

Frozen sets (in `FROZEN_FIXTURES_V1.json`, committed before invention runs):

- **Training corpus** `C`: 6 programs, `S_0 = 23` symbols: `ab cab`-family and `abab` repetitions chosen so that (i) `ab` strictly dominates the first admission under the frozen rule at `κ = 1`, (ii) `(m_1, m_1)` is strictly beneficial after the first rewrite, (iii) no third admission is strictly beneficial.
- **Reuse-positive held-outs** `H+` (12 targets): each contains at least two greedy-disjoint occurrences of some length-≥2 subword that occurs at least twice in the training corpus; lengths span 5–10; none equals or is a contiguous subword of any training program; pairwise distinct.
- **Unrelated control held-outs** `H−` (12 targets): no internal repeated subword of length ≥ 2; contains no length-2 subword occurring ≥2 times in the training corpus (`ab`, `ba`); none equals or is a contiguous subword of any training program; lengths 3–4.

Criteria:

1. `Net(H+) < 0` strictly, after charging full `K_total(L)` at `κ = 1`.
2. `Net(H−) ≥ 0`, with the regression preserved and reported (expected strictly positive: alphabet widening raises the enumerated volume at every length below the hit, plus charges).
3. Both sets are frozen before any invention or enumeration run; the freeze-commit custody in CI plus hostile HLK-1 must mechanically demonstrate no held-out data can influence invention.

### NULL-1 — equal-size random-admission null

Because a gate can fake improvement by luck, the certificate reports a random-admission null: for each frozen seed `s ∈ {0,...,199}`, a library of cardinality `|L|` is formed by choosing a subset of that size uniformly over the deterministically ordered G0 candidate pool (all training-corpus contiguous subwords with expansion length ≥ 2 and occurrence ≥ 2) via the frozen integer hash `((s+1)·2654435761 mod 2^32) mod C(pool, |L|)`. For each null library the exact `Net(H+)` and `Net(H−)` are computed with the same charges. Reported: the full null distribution (min/median/max), the number of null libraries strictly beating the true library, and the true library's empirical rank. No stochastic machinery enters the main claims; the null is an exact finite ensemble, not an error bar approximation.

## 9. THR-1 — exact lifecycle threshold (parent #233 HST-T05)

For macro `m` with current-grammar body length `b`, per-occurrence symbol saving `Δ = b − 1` (marginal reading: replacing its body by one symbol in the grammar that already admits its dependencies) and lifecycle charge `K = b + κ`, over the registered horizon with `H_eff(m)` useful occurrences:

```text
lifecycle benefit is exactly positive  iff  H_eff * Δ > K
```

`H_eff(m)` is frozen as the total number of occurrences of `m` across the canonical enumerator's first-hit programs for the `H+` targets. The base-relative saving (full base expansion length minus one) is additionally reported. Both readings and the aggregate `Σ H_eff·Δ > K_total` must hold exactly on the registered fixture.

## 10. Hostile battery (fail-closed)

| id | attack | required terminal |
|----|--------|-------------------|
| HLK-1 | held-out file contents poisoned/replaced before invention | library output byte-identical; any influence is a defect |
| HCYC-1 | cyclic macro dependency (self-loop and 2-cycle) | `RECURSIVE_LIBRARY_CYCLE`, grammar unchanged |
| HDEF-1 | admission computed without definition charge on a crafted corpus | charge is load-bearing: uncharged variant admits a candidate the registered rule rejects |
| HMNT-1 | admission computed without maintenance charge | charge is load-bearing: some admission flips between `κ = 0` and `κ = 1` |
| HZERO-1 | candidate with exactly zero net gain | rejected (strict positivity), corpus unchanged |
| HSEM-1 | corpus rewrite that alters expanded semantics | detected by exhaustive per-program expansion equality; fail-closed |
| HSEL-1 | post-hoc held-out edit after freeze | held-out content hash mismatch detected (`HELDOUT_FREEZE_HASH_MISMATCH`) |

## 11. Independent oracle and determinism

A second implementation (`independent_oracle_v1.py`) must recompute, without importing the main module: expansions of all library programs, the full invention trace from the frozen corpus, the canonical enumeration and every held-out burden under `G0` and `G0 ∪ L`, the threshold identities, and the null ensemble — and agree exactly with the main receipt.

Receipts must be byte-identical under `python -I -B` and `python -I -O -B` and across CPython versions (integer arithmetic only, sorted JSON, no environment or time dependence). Dedicated CI runs both modes and `cmp`s against the committed receipts, enforces freeze custody (this freeze commit precedes all implementation artifacts), pins parent blobs, and runs the #833 reconciliation in check mode on PRs and apply mode on merge to main.

## 12. #833 reconciliation boundary

After and only after exact PR CI is GREEN, replace exactly the three open Section-E rows with checked rows citing #897, this package, the exact headline numbers, and the conditional scope (existence/finite transfer, negative control preserved, no universal claim). No other Section-E row is touched by this tranche.

## 13. Claim ceiling

```text
GMI_FINITE_CONSERVATIVE_RECURSIVE_LIBRARY_GROWTH_AND_HELDOUT_REUSE_BENEFIT_AT_REGISTERED_SCOPE
```

Forbidden promotions (from #897, verbatim): `UNIVERSAL_LIBRARY_LEARNING`, `PRIMITIVE_INVENTION_ALWAYS_HELPS`, `OPEN_ENDED_GRAMMAR_GROWTH`, `UNSEEN_FORM_DISCOVERY`, `P4_RECOVERY_COMPLETE`, `REAL_WORLD_TRANSFER_PROVED`, `ALL_FUTURE_TASKS_CHEAPER`, `COMPLETE_GMI`.
