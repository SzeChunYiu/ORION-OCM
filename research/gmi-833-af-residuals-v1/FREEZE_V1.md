# FREEZE_V1 — `gmi-833-af-residuals-v1`

Committed **before any implementation, executor, oracle, test, receipt or measurement of
this package exists**. The first commit touching this directory carries only `FREEZE_V1.md`
and `FREEZE_ROWS_V1.json`; `check_freeze_order_v1.py` re-derives that from git in CI with a
negative control and degrades to a distinct `UNREACHABLE` state, never a pass, if the freeze
commit is unreachable after a squash.

- **`source_main`** = `f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5`.
- **Claim ceiling** =
  `GMI_AF_RESIDUALS_AF1_AF6_AF7_AF8_BARRIER_SURFACES_AND_ATLAS_EXPANSION_AT_REGISTERED_FINITE_SCOPE`.
- **Issue-comment fetch** of comment `5693269426` pinned in `FREEZE_ROWS_V1.json` by sha256
  `35d29bea51a66594…` (35,665 bytes); issue-body fetch pinned by sha256 `d5cd0248ea2f7121…`
  (27,554 bytes). Every row's verbatim text is stored in the JSON with a per-row sha256 and is
  **not** restated in markdown, because several rows contain terms the repo-wide terminology
  gate blocks in prose.

## 1. The exact rows this tranche may reconcile

Fifteen, and only fifteen — every unchecked row of comment `5693269426` at `source_main`:
`AF1_R1`; `AF6_R1` … `AF6_R6`; `AF7_R1` … `AF7_R5`; `AF8_R1` … `AF8_R3`. Each carries, in the
two propagation sweeps (`gmi-833-comment-evidence-propagation-v1`/`-v2`), a recorded reason:
`PARTIAL` with the missing half named, or `NO_EVIDENCE`. This package builds the missing half
and nothing else.

**No neighboring row is earned here.** The checked AF1 `G0` row (pinned as
`checked_but_unsupported_row`) is **not un-checked and not re-evidenced by this package**; its
determination is reported separately (§4). AF9 and AF10 carry no checkboxes. No row of any other
comment is in scope. This package **never edits any comment or the issue body**.

## 2. Pre-registered closure tests, one per row

Each rule is a biconditional fixed now, so a result cannot be re-read into a closure later.

### AF1

`AF1_R1` (upgrade the #833-L developmental-potential row). **Closes iff** (a) the three AF
theorems `AF-T01`, `AF-T02`, `AF-T03` are closed on `main` — `gmi-833-af-barrier-context-v1/RESULT_V1.json`
`status: GREEN` at its pinned blob — and (b) this package supplies, for the orchestrator, a
byte-exact replacement of the body line pinned as `body_row_L` that keeps
`#909 #908 L:2a33e8326125` verbatim and adds the set-valued response object
`Gamma^S_{M0,Delta}(Pi,R,H,Q,V)` with `Current(M0,Q,V)` as its zero-development slice. The
comment row's `new` line is valid **only together with** that body replacement, and the
reconciliation entry says so (`requires_body_replacement: true`). If the orchestrator declines
the body write, the row stays open.

### AF6 — search, complexity, learnability

Finite search universe frozen for `AF6_R1`/`AF6_R2`: `X = {0,1,2,3}`, `Y = {0,1}`, the 16
total functions; a deterministic non-revisiting search algorithm is a decision tree over
observed values — there are exactly `4·(3·(2·1)^2)^2 = 576`; performance is the trace of
observed values, summarized as the index of the first `1` (or `5` if none).

- `AF6_R1` **closes iff** (i) every one of the 576 algorithms has the identical first-hit
  histogram over the 16-function class (the permutation-closed premise) — exact; (ii) the same
  equality holds for every permutation-invariant weighting tested (weights a function of the
  number of ones, exact rationals) and fails for a registered non-invariant weighting; (iii) the
  threshold class `T = {f_k : f_k(x)=1 iff x ≥ k, k=0..4}` is shown **not** closed under
  permutation by an exact witness permutation, and the 576 algorithms have unequal expected
  first-hit on `T` (exact min < max); and (iv) the terminal is
  `OUTSIDE_NFL_SYMMETRY_REGIME_PREMISE_NOT_MET`, never `BROKE_NFL`.
- `AF6_R2` **closes iff** the advantage `Δ(T) = max−min` expected first-hit over the 576
  algorithms is `> 0` on `T` and `= 0` on the permutation closure `cl(T)` (exact), and the
  information required is charged twice: **encoding** as an index into the registered family
  of four candidate classes (`2` bits) and as a 16-bit membership mask; **acquisition** as the
  least `k` i.i.d. task draws that reject "closure-uniform" at error `δ = 1/8`, i.e. the least
  `k` with `(|T|/|cl(T)|)^k ≤ δ` — expected `k = 2` since `(5/16)^2 = 25/256 ≤ 32/256`.
- `AF6_R3` **closes iff** three typed records carry pairwise-distinct premise sets:
  `BLUM_SPEEDUP` (Blum 1967 — Blum measure, existential computable function, unrestricted
  program class, asymptotic, `PARENT_OWNED_NOT_PROVED_HERE`); `FINITE_BUDGET_PARETO` (a
  registered finite implementation family with exact `(time, size)` vectors, exact Pareto
  front — a finite set always has minimal elements, so finite dominance is never a Blum
  statement); `PROOF_RESTRICTED_SPEEDUP` (Hutter 2002 — programs with provable time bounds
  admit an optimal-up-to-constant algorithm, parent-owned); and hostiles labelling a finite
  dominance `BROKE_BLUM` or "asymptotically optimal" are rejected.
- `AF6_R4` **closes iff** the barrier context gains a registered axis `D`
  (distribution/parameter regime) and two exact transitions along `D` alone are recorded:
  (a) vertex cover on registered graphs, exhaustive `2^n` subset checks versus a `k`-bounded
  branching tree at `k = 2`, exact node counts for `n = 4..10`, status
  `RESOURCE_INFEASIBLE_AT_SCOPE` at the registered budget → `DECIDABLE` within budget, residual
  "general problem remains NP-hard (parent)"; (b) first-`1` probing on length-`n` bit strings,
  worst case `n` probes versus exact uniform expectation `2 − 2^{1−n}`.
- `AF6_R5` **closes iff** exact remaining-hypothesis counts are computed for the class
  `{L_k = {a^i : i ≤ k}, k = 0..4}` on words of length ≤ 4 with target `L_2`: positive text
  alone leaves `3` (`L_2, L_3, L_4`) — not identifiable; one labelled negative leaves `1`;
  membership queries reach `1` in `2` queries; and, separately, an operationally equivalent
  pair of B1 machines (the FGS-4 shape) is indistinguishable from input/output traces on all
  words yet distinguishable from state-annotated traces — with the supplied channel logged on
  every case (`EXTERNAL_OBSERVATION`, `REWARD_OR_EVALUATOR_SIGNAL`, interaction/query, trace
  annotation).
- `AF6_R6` **closes iff** a parent map with at least five rows (DEC — Foster, Kakade, Qian,
  Rakhlin 2021; information ratio — Russo & Van Roy; query complexity — Angluin 1987; VC sample
  complexity — Blumer, Ehrenfeucht, Haussler, Warmuth 1989; identification in the limit — Gold
  1967; list identification — Charikar, Pabbaraju, Tewari 2026) states each parent's exact
  premises, what this package computes (only the finite exact counts of `AF6_R5`) and what it
  does **not** compute (DEC and information-ratio values, which need real-valued optimization and
  logarithms — `PARENT_OWNED_NOT_COMPUTED`), and a hostile asserting a generic sample-complexity
  law is rejected (`NEW_GENERIC_SAMPLE_COMPLEXITY_LAW` forbidden).

### AF7 — physical substrate

- `AF7_R1` **closes iff** `S_PHYS_CONTRACT_V1.json` registers the nine coordinates named by the
  row — precision, state preparation, noise, readout, repeatability, time, energy, spatial
  resources, error probability — each typed with an exact rational or integer range, and a
  validator rejects a contract with an unbounded (`null`) precision.
- `AF7_R2` **closes iff** a proposal ledger with at least eight entries (oracle machines —
  Turing 1939; analog recurrent networks with real weights — Siegelmann & Sontag 1994/1995;
  BSS real computation — Blum, Shub, Smale 1989; accelerating/Zeno machines — Copeland 2002;
  Malament–Hogarth spacetimes — Etesi & Németi 2002; infinite-time Turing machines — Hamkins &
  Lewis 2000; noisy analog computation — Maass & Orponen 1998, Maass & Sontag 1999; quantum
  computation — Bernstein & Vazirani 1997, `BQP ⊆ PSPACE`) records for each its exact
  mathematical assumptions, the `S_phys` coordinate each assumption stresses, and a typed
  status from `{MATHEMATICAL_MODEL_ONLY, PHYSICAL_STATUS_UNKNOWN, NO_SUPER_TURING_POWER_CLAIMED}`;
  a row lacking an exact assumption is rejected.
- `AF7_R3` **closes iff** the real-parameter microscope — `n = 12` frozen advice bits,
  `w = Σ b_i 2^{-i}` exact — yields capability exactly `p/n` at readout precision
  `p ∈ {0, 4, 8, 12}` on the advice-indexed task, with `p` bits charged under
  `INITIAL_OR_INHERITED_ORGANIZATION` + `ORACLE_ADVICE_OR_TOOL` and terminal
  `IMPORTED_INFORMATION_OR_ADVICE`; readout beyond `p` that returns true bits is flagged.
- `AF7_R4` **closes iff** under noise flip probability `η = 1/4` per read, `r` majority reads and
  error bound `ε = 1/32`, the exact majority-correct probability and the union-bound count of
  reliably readable bits `p_eff` are computed for `r ∈ {1,3,5,7,9}`, with `p_eff <` precision at
  the registered contract, and the hostile's `applicable` flag confirms that at `η = 0` with
  precision `≥ n` the capability is `1` (power present) so the finite contract genuinely
  removes it — terminal `APPARENT_SUPER_TURING_POWER_DISAPPEARS_UNDER_FINITE_CONTRACT`.
- `AF7_R5` **closes iff** the frontier is recomputed as a function of the contract: (a) at
  precision `4` versus `8` the advice-task capability frontier moves `4/12 → 8/12` by the same
  function, and (b) a hypothetical oracle channel, labelled
  `HYPOTHETICAL_SUBSTRATE_EXPERIMENT_NOT_PHYSICAL_EVIDENCE`, moves a registered query from
  `UNDECIDABLE_RELATIVE_TO_S` to `DECIDABLE_BY_ONE_IMPORTED_ORACLE_QUERY` with a new residual
  above it — `theory_status: UPDATED_NOT_BROKEN`, `physical_evidence: NONE`, and the hostile
  labelling this `PHYSICAL_HYPERCOMPUTATION_ESTABLISHED` rejected.

### AF8 — atlas

- `AF8_R1` **closes iff** `GMI_INTELLIGENCE_ATLAS_B_V1.json` is **committed** with one row per
  B1 presentation carrying: the machine state (its step table), developmental edges (neighbour
  ids with the edit that realizes each), the provenance channel each edge requires, the exact
  capability vector and operational class, raw resources, and a typed barrier status per task
  query — and its projection onto AJ11's row fields reproduces the AJ11 digest
  `09a99f29d2d349d7f28855d3a32776667c65cd1a707ea89129fd77c3328a16ed` exactly; all 260 reachable.
- `AF8_R2` **closes iff** five axes each have at least two registered levels with exact integer
  counts of presentations, operational classes, achieved capability vectors, exact solvers per
  task and Pareto-front size: **budget** (state bound: 1, 2, 3 states → `4`, `256`, `46,656`
  presentations); **information access** (observation window `L ∈ {1,2,3,4}`);
  **interaction** (input/output traces versus state-annotated readout: `148` vs `260`
  distinguishable at B1); **approximation tolerance** (`ε ∈ {0, 1/31, 3/31, 7/31}` of the 31
  protected words); **substrate power** (a registered advice channel revealing the previous
  symbol, provenance `ORACLE_ADVICE_OR_TOOL`, expanding what one-state maps realize).
- `AF8_R3` **closes iff** quotient statistics are computed at three bounds (1, 2, 3 states) —
  class count via canonical minimization, achieved capability-vector set over the frozen five
  tasks, exact-solver existence per task, front size — and the receipt says exactly which
  statistic stabilizes (expected: the achieved capability set stabilizes from 2 states on; the
  class count does not) and shows by construction that the stabilization is task-family
  relative (adding `delay2` changes the achieved set only at 4 states, run on laptop-billy and
  pinned; CI reruns bounds ≤ 3). Terminal
  `QUOTIENT_STATISTIC_STABILIZES_TASK_FAMILY_RELATIVE__NO_UNIVERSAL_LIMIT_CONVERGENCE_CLAIMED`.

## 3. Named results this package may assert

`AFR-1`; `AF6-1` … `AF6-6`; `AF7-1` … `AF7-5`; `AF8-1` … `AF8-3`, one per row above, each with
scope, quantifiers, assumptions, falsifiers, strongest parents and forbidden extrapolations in
`AF_RESIDUALS_THEOREMS_V1.md`. No other identifier may appear in the receipt.

## 4. The AF1 `G0` row — determination only

PR #969 restates the checked `G0` row against a `Gamma+` post-development projection. This
package re-checks `#969` with `/usr/bin/git merge-base --is-ancestor` against `source_main`
and the pulls API at run time and reports which reading the evidence supports. It does **not**
un-check the row and does not build `G0` machinery.

## 5. Two routes, hostiles, nulls

Route A: `af6_search_barriers_v1.py`, `af7_substrate_contract_v1.py`, `af8_atlas_expansion_v1.py`.
Route B: `independent_oracle_v1.py`, importing nothing from route A — algorithms enumerated as
explicit probe-sequence tables rather than recursive trees, transducer equivalence by
finite-word trace comparison rather than product search, canonical minimization by a different
partition-refinement order, binomial probabilities by direct enumeration of outcome strings
rather than the closed form.

| id | planted defect | quantity it must move |
|---|---|---|
| `HA1` | non-closed class labelled closed | closure witness must appear |
| `HA2` | `BROKE_NFL` / `BROKE_BLUM` relabelling of a premise change | rejected |
| `HA3` | advantage on `T` claimed at `0` bits | charge validator rejects |
| `HA4` | `D`-axis transition that drops the general-hardness residual | rejected |
| `HA5` | positive text claimed identifying (`3 → 1` with no channel) | rejected |
| `HA6` | a generic sample-complexity law record | rejected |
| `HA7` | `S_phys` with `null` precision | validator rejects |
| `HA8` | proposal row with no exact assumption | rejected |
| `HA9` | readout beyond precision returning true bits | capability `> p/n` flagged |
| `HA10` | noise hostile at `η = 0`, precision `≥ n` | capability stays `1` (applicability control) |
| `HA11` | recompute labelled `PHYSICAL_HYPERCOMPUTATION_ESTABLISHED` | rejected |
| `HA12` | atlas row stripped of edges/provenance/status | schema `RED`; projection digest intact |
| `HA13` | expansion axis with one level | gate `RED` |
| `HA14` | stabilization promoted to universal convergence | rejected |

**Nulls.** `NA1`: exactly `32` of the `65,536` subsets of the 16 functions are permutation
closed; all 32 tie on all 576 algorithms, and of 200 uniformly random subsets
(`random.Random(20260919)`) the tie rate is recorded and expected `0/200`. `NA2`: 200 random
relabelings of B1 states leave every class count and capability count unchanged (invariance
null for the atlas). `NA3`: 200 random 3-state presentations under `delay2` — exact-solver rate
`0/200`, so the 4-state achieved-set change is not chance.

## 6. Forbidden promotions

`BROKE_NFL`, `BROKE_BLUM`, `NO_FREE_LUNCH_FALSE`, `NEW_GENERIC_SAMPLE_COMPLEXITY_LAW`,
`SEARCH_ADVANTAGE_WITHOUT_PRIOR`, `GENERAL_PROBLEM_MADE_TRACTABLE`,
`PHYSICAL_HYPERCOMPUTATION_ESTABLISHED`, `PHYSICAL_CHURCH_TURING_FALSIFIED`,
`SUPER_TURING_POWER_FROM_NOTHING`, `PHYSICAL_SUBSTRATE_INSTANCE_MEASURED`,
`UNIVERSAL_LIMIT_CONVERGENCE`, `ALL_MACHINE_INTELLIGENCES_COMPLETELY_CLASSIFIED`,
`AF1_G0_ROW_RE_EVIDENCED_HERE`, `AF_SECTION_COMPLETE`, `COMPLETE_GMI`.

## 7. What is not claimed

No classical barrier is contradicted. NFL, Blum speedup, Gold, Angluin, VC, DEC and the
information ratio, Siegelmann–Sontag, and every hypercomputation proposal remain parent-owned
at their own premises. No physical substrate is measured; `S_phys` is a registered contract
and every substrate experiment here is mathematical. Bounds beyond four states are not
characterized. The residual contribution is the executable missing half of fifteen rows,
under rules fixed here.
