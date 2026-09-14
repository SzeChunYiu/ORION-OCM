# Measured constant footprint: discharging TT-6's premise

Status: **MEASURED ON A VALIDATED SIZE CONTRACT; ONE CONCLUSION STRENGTHENED,
ONE EARLIER RANKING WITHDRAWN**
Date: 2026-09-14

Parent: [TT-1..TT-7](THRESHOLD_TASK_FRONTIER_THEOREM_V1.md). Instrument:
`constant_footprint_v1.py`. Checker: `check_frontier_v1.py`. Receipt:
`RECEIPT_V1.json`.

## 1. The gap this closes

TT-6 said: charge a constant cell at any positive rate and the threshold
rendering strictly dominates the `2**n` table. Its second component was a
declared **count** of integer cells, and the theorem was explicit that a count
is not bytes and not memory. So the positive half rested on a premise nobody
had measured — the weakest link in it, and named as such.

This replaces the premise with measurements. Two exact sizes of the constant
payload, on an object-size contract the checker validates and refuses to guess
about, for every registered realization at n = 3..8.

## 2. TB-1 — the integers cost nothing, and that is measured

> **TB-1.** Every integer in every registered payload is a **shared object**:
> identical (`is`) to a value built independently. So counting the integers as
> incremental memory would double-count objects that already exist.

The tables here hold only 0 and 1, and CPython caches small integers. The
checker verifies the identity rather than citing the implementation detail.

This is why the in-memory measure below counts **tuple objects only**. Adding
`sys.getsizeof` of each leaf would have inflated the table's cost by 28 bytes a
cell and flattered the conclusion this document is testing.

## 3. TB-2 — the two measures, and the size contract they are stated against

- `marshalled_constant_bytes` = `len(marshal.dumps(payload))`, the serialized
  size CPython itself writes for these constants. Exact and deterministic.
- `tuple_structure_bytes` = `sum(sys.getsizeof(node))` over every tuple node in
  the payload, the incremental in-memory cost given TB-1.

Both are stated against a validated contract: empty tuple 40 bytes, tuple slot
8 bytes, small integer 28 bytes, 63-bit `sys.maxsize`. A build that differs
makes the checker **raise** rather than restate different numbers under the same
claim, exactly as the opcode-layout contract does.

Measured, n = 8:

| realization | opcodes | cells | marshalled | in-memory |
|---|---:|---:|---:|---:|
| `THRESHOLD_COMPARISON_BOOL` | 28 | 1 | 8 | **0** |
| `NESTED_CONSTANT_TABLE` | 28 | 256 | 1793 | 14280 |
| `FLAT_INDEX_TABLE` | 44 | 263 | 1323 | 2088 |
| `MONOTONE_DNF_CHAIN` | 570 | 0 | 3 | **0** |
| `HIDDEN_UNIT_NET_BOOL` | 34 | 2 | 13 | 0 |

The threshold payload is **constant in n** — 8 marshalled bytes, zero tuple
structure — while the nested table's structure is exactly `2**n - 1` tuple nodes
and `2**(n+1) - 2` slots. The checker pins both.

## 4. TB-3 — TT-6's domination survives measurement

> **TB-3.** In both measured coordinates, at every n in 3..8, the threshold
> rendering strictly dominates **both** table renderings and is undominated.

So TT-6 is no longer conditional on a premise about pricing. The domination is
measured, in two independent senses, and it holds against the flat table as well
as the nested one.

## 5. TB-4 — the count coordinate ranked two realizations it should not have

> **TB-4.** The count coordinate reports that the nested table strictly
> dominates the flat table at every n. Both measurements report them
> **incomparable**: nested is cheaper in opcodes, flat is cheaper in both sizes.

The reason is structural and the checker records it: the nested rendering pays a
40-byte tuple header `2**n - 1` times, once per interior node, while the flat
rendering pays it once. At n = 8 that is 14280 bytes against 2088, a factor of
6.8, against a count of 256 cells against 263 that ranked them the other way.

**This is withdrawn from TT-6, not defended.** A count of cells is not a
conservative proxy for size: here it inverted a comparison. TT-6's own claim
survives because its margin is between one cell and `2**n`, not because a count
was a safe stand-in.

## 6. TB-5 and TB-6 — one frontier confirmed, one strictly sharpened

> **TB-5.** Under the serialized measure the undominated set is **exactly** the
> counted one: `{MONOTONE_DNF_CHAIN, THRESHOLD_COMPARISON_BOOL}` for n >= 5. So
> TT-6 was not an artifact of counting cells.

> **TB-6.** Under the in-memory measure the frontier is strictly smaller, and
> from n = 5 the threshold rendering is the **unique** undominated realization
> of majority-n.

TB-6 is the sharper result and it comes from TB-1. The gate chain's only
advantage was using no constant at all, worth one cell in the count. Measured,
that advantage is worth **nothing**: the threshold form's single constant is an
interned integer that already exists, so both sit at zero incremental memory and
the gate chain's 570 opcodes against 28 decide it. The count coordinate was
overcharging the threshold form for a constant that costs no memory.

At n = 3 and n = 4 the optimum is a tie rather than unique, shared with the
other minimal renderings that also sit at zero structure — which is TT-4's
refutation appearing again in a second coordinate. Minimal cost still does not
force the threshold structure at those n; it does from n = 5, in this measure,
over this register.

## 7. Residue

- **Neither measure is resident set size.** One is a serialized length, the
  other the size of the tuple objects. Nothing here is RSS, page-resident cost,
  cache behaviour or allocator overhead.
- **TB-1 is a property of these payloads, not of tables in general.** A table of
  values outside CPython's small-integer cache would allocate, and its
  in-memory cost would then include its values. Every table registered here
  holds 0 and 1 only.
- **The size contract is one build.** CPython 3.12, 64-bit. The checker refuses
  on any other rather than restating different numbers.
- **Still no timing**, and still point verdicts over registered candidates under
  CU-1 and CU-3b. Measuring the second component does nothing about coverage.
- **Nothing about learning.** Every realization here is written, not trained.

Terminal: `GRAND_GMI_THRESHOLD_TASK_FRONTIER_GREEN_AT_FINITE_SCOPE`.

## 8. Parent mathematics and contribution boundary

The parent facts are elementary: the product order, `marshal`'s serialization
format, `sys.getsizeof`, and CPython's small-integer cache. No novelty is
claimed for any of them, and the cache is verified by identity here rather than
cited. The contribution is discharging TT-6's pricing premise with two exact
measurements, the identity check that keeps the in-memory measure from
double-counting, the withdrawal of the nested-versus-flat ranking the count
produced, and the uniqueness at n >= 5 that the count had hidden.
