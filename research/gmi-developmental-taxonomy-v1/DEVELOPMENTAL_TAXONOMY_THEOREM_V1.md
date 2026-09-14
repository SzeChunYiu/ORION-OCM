# Developmental taxonomy — five change types with observable criteria (592 item 3 / 602 A3)

Status: **THEOREM + EXACT FINITE WITNESSES. Admissibility claim** (DU-1: what is
forced/distinguishable under the declared interface, not what neutral search reaches).
Date: 2026-09-14. Scope: finite deterministic developmental system with `n = 3`
local units (the factorisation fixture), plus four declared developmental
registers on top of the global state. Exact integer arithmetic, CPython 3.8 safe.

## Parent subtraction

This unit layers on two parents without duplicating them:

- `DEVELOPMENT_TIMESCALE_SEPARATION_V1.md` — the `B = (B_exec, B_dev)` split and
  the three timescales `T0` execution / `T1` learning / `T2` morphogenesis.
  The taxonomy refines `T1 ∪ T2` into five observable kinds of change.
- `DEVELOPMENTAL_STATE_FACTORIZATION_V1.md` — the exact product fixture
  (`n` units, states `{0,1,2}^n`, `|S_min| = 3^n`, flat entries `2n3^n`,
  `Theta(n)` current-state bits vs `2n3^n` table). The fixture is reused as the
  `INFO` regime; the four additional registers extend it.

No new graphical-model principle is claimed beyond the parent
`FACTORIZATION_CAN_COMPACT_GLOBAL_MODEL_OR_TRANSITION_ENUMERATION`.

## A3 checklist

- [x] storing information vs changing representation
- [x] skill acquisition vs state memorisation
- [x] learning-law change vs ordinary parameter update
- [x] architecture/morphology change vs learned parameter state
- [x] meta-learning / search-policy change vs object-level learning
- [x] hereditary / intergenerational change vs within-lifetime development
- [x] observable decision criteria for each transition
- [x] when two histories are behaviourally equivalent
- [x] when history is irreducible even if present outputs match

## System

A developmental configuration is

```
C = (s, r, K, L, M, g)
```

- `s ∈ {0,1,2}^n` — global product state (`n = 3`), same local rule as the
  parent fixture: per unit `query_i → 0 iff s_i ∈ {0,1} else 1`; `teach1_i` maps
  `0→2, 1→1, 2→2` on the addressed unit (other units unchanged).
- `r ∈ {0,1}` — representation register (encoding table id). Content-preserving
  recoding keeps the abstract `s` while `r` flips.
- `K ⊆ {skill_0, skill_1, skill_2}` — retained skill library (reusable routines
  compiled from state traces; `|K| ≤ 3` in the witness).
- `L ∈ {0,1}` — learning-law register (which update table the `teach1` operator
  consults; law 0 is the parent fixture, law 1 is a variant).
- `M ∈ {0,1}` — morphology register (topology/control-policy id).
- `g ∈ {0,1}` — generation counter (0 = within-lifetime, 1 = hereditary boundary
  crossed).

`T0` is a `query_i`/`teach1_i` step that touches only `s` (when law `L=0`).
All other registers change only via explicit developmental events.

## Five predicates (observable decision criteria)

A developmental transition `C → C'` labelled by its event kind is classified by
which register(s) move, read directly off the before/after trace:

| predicate | fires iff | trace attribute |
|---|---|---|
| `P_INFO` | `s` changes, `r,K,L,M,g` unchanged | state write, no recoding/skill/law/morph/generation change |
| `P_RECODE` | `r` flips, `s` abstract content preserved, `K,L,M,g` unchanged | encoding table changes, skill/law/morph/generation unchanged |
| `P_SKILL` | `K` strictly grows, `s,r,L,M,g` unchanged | library gains an entry, no other register moves |
| `P_LAW` | `L` flips, `s,r,K,M,g` unchanged | update-rule id changes, state/encoding/skill/morph/generation unchanged |
| `P_MORPH` | `M` flips, `s,r,K,L,g` unchanged | topology id changes, others unchanged |

Extensions:

- `P_META` — `P_LAW` with object-level flag (`level = object`): the law change
  governs the object-level `teach1` operator (vs a meta-level scheduler). In the
  witness, every `P_LAW` transition is object-level, so `P_META ⇔ P_LAW`.
- `P_HEREDITARY` — `g` increments (`0→1`), regardless of which other register
  co-moves; within-lifetime transitions have `g` unchanged. The five-type
  classification above is stated for `g`-preserving steps; a hereditary step is
  flagged separately and may co-occur with one of the five (the witness keeps
  them orthogonal: the hereditary step copies `s` into the next generation
  without otherwise changing `r/K/L/M`).

Machine-checked on the `5 × 3` witness log: the five `g`-preserving predicates
are **mutually exclusive** (exactly one fires per log entry) and **jointly
exhaustive** (every log entry fires one). Hereditary flag is orthogonal.

## Witness log

Starting from `C0 = ((0,0,0), 0, ∅, 0, 0, 0)`, 15 transitions in round-robin
order `INFO, RECODE, SKILL, LAW, MORPH × 3`:

- `INFO`: `teach1_0` on `s` (e.g. `(0,0,0)→(2,0,0)`), `r/K/L/M/g` unchanged.
- `RECODE`: `r: 0→1` (or `1→0`), `s` abstract content preserved.
- `SKILL`: `K: ∅→{skill_0}→{skill_0,skill_1}→…`
- `LAW`: `L: 0→1→0→1`
- `MORPH`: `M: 0→1→0→1`

Each entry's before/after is fully enumerated in `taxonomy_v1.py: WITNESS_LOG`.

## Behavioural equivalence and history irreducibility

Histories are finite event sequences from `C0`. Two histories `h1, h2` are
**behaviourally equivalent** (`h1 ~ h2`) iff they land in the same
developmental configuration `C` — equivalently, they induce the same response
on every continuation (same `query_i` outputs and same `teach1_i` successors
for all `i`, plus same `r/K/L/M/g`). This is the Myhill–Nerode quotient on the
deterministic transition graph.

**Irreducibility witness (history matters even when present outputs match).**
In the `s`-component, local states `0` (teachable-unlearned) and `1`
(stubborn-unlearned) are `query`-indistinguishable (`query_i → 0` on both)
yet `teach1_i`-distinguishable (`0→2` vs `1→1`). The product states

```
s_a = (0,0,0)   and   s_b = (1,0,0)
```

both answer every `query_i` with `0`, but `teach1_0` sends `s_a→(2,0,0)` (now
`query_0 → 1`) while `s_b→(1,0,0)` (still `query_0 → 0`). Histories reaching
`s_a` vs `s_b` are present-output-equivalent and behaviourally inequivalent —
history is irreducible to present query outputs alone.

Machine-checked: all-pairs query-output equivalence vs teach-successor
inequivalence is enumerated; the pair above is the lexicographically first
witness. The global quotient still has `3^3 = 27` states and `2·3·27 = 162`
state-event entries (parent fixture preserved); current-state bits remain
`⌈log2 27⌉ = 5 = Theta(n)`.

## Claim ceiling

Finite deterministic `n = 3` witness, exact registers, declared `query/teach1`
interface, admissible scope only. No claim that neutral search reaches any
register's content, that five types are exhaustive in open-ended natural
systems, or that law/morphology distinctions are physically disjoint (the
separation is modelling, per the parent). Falsifier: a `g`-preserving log
entry firing zero or two predicates under the stated attribute rules, or a
history pair violating the `~` characterisation (re-run the checker).

Files: [model](taxonomy_v1.py) → [controls](test_taxonomy_v1.py) →
[receipt](TAXONOMY_RECEIPT_V1.json: on billy-old py3.14 + laptop-billy py3.8,
normal + optimized).
