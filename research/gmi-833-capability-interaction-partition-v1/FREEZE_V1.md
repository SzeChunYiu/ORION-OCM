# FREEZE_V1 — gmi-833-capability-interaction-partition-v1

**Frozen at**: 2026-09-18, BEFORE any implementation commit in this package.
**Package**: `research/gmi-833-capability-interaction-partition-v1/`
**Branch**: `research/833-ciu-repair`
**Issue context**: #833 (corpus repair tranche); prior revival of the target object under #976 / L58.

---

## 1. Source pins

| item | value |
|---|---|
| `source_main` | `c70dd24eeade46a3afe8322c1a0e0c16a648311e` |
| `source_main_subject` | `Merge pull request #1003 from SzeChunYiu/codex/1002-scalable-morphology-sampling-v1` |
| corrected object | `CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1` (Theorem CI-U + Corollary CI-A4) |
| corrected object path | `research/gmi-capability-interactions-unified-v1/CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md` |
| corrected object blob (at freeze) | `a9a67f8ec06b87aa374f092a72fabc593178ecfe` |
| `interactions_witness.py` blob (at freeze) | `70de5ec72f936bf1c309f0b0024eedf5e18f1c98` |
| `ci_universal_witness_v1.py` blob (at freeze) | `7df48f8f98da1be0a571c81bbad8158c96bfc326` |
| prior disposition of corrected object | GREEN on mainline; confirmed OVERSTRONG by the #939 verdict table, revived under the #976 L58 revival chain |

## 2. Claim ceiling

`G2` — bounded formal framework with explicit falsifiers. This tranche does NOT raise the
ceiling of the corrected object. Nothing here is claimed at G3 or above.

## 3. Issue rows this tranche may reconcile

**NONE.**

`reconcilable_rows = []` (explicitly empty, not omitted).

**No neighbouring row is earned here.**

This tranche is a CORRECTION of an already-GREEN mainline object. It closes no #833
checkbox by itself and produces **no** `ISSUE_833_RECONCILIATION_*.json`. Its receipt is
`CORRECTION_NOTICE_V1.json`.

## 4. What this tranche is permitted to claim (fixed in advance)

1. **PART-1** — an exact partition theorem (named `CIP-1`) over the `(max, joint, sum)`
   burden lattice with four classes `INDEPENDENT / REDUNDANT / PARTIAL_SHARING /
   INTERFERING`, proved mutually exclusive and jointly exhaustive on the admissible
   region fixed by the monotonicity axiom `(M) joint >= max`, including an explicit proof
   for the degenerate `max = sum` (zero-burden) case.
2. **PART-2** — a burden-based classifier and the corrected 351-pair census of the A4
   contract, with a complete per-pair delta table against the shipped labels.
3. **PART-3** — an exact correspondence-and-divergence theorem (named `CIP-3`) between the
   shipped channel-overlap predicate and the burden classification under the A4
   registered nested/fully-shareable accounting, labelled EARNED-BY-COUNTEREXAMPLE.
4. **PART-4** — Lemma B precision (named `CIP-4`): `mu` pinned to counting measure on a
   finite unit set (equivalently, the strict-positivity axiom `mu(A) = 0 => A = empty`),
   with an explicit counterexample showing the `iff nested` direction fails without it.

## 5. Forbidden promotions (fixed in advance)

- MUST NOT delete the `INTERFERING` class. CE-2 shows interference is real outside
  free-option accounting; the class stays in the partition.
- MUST NOT weaken Section 1.2 to prose, nor narrow Corollary CI-A4's scope, nor downgrade
  Theorem CI-U's universal claim. The repair is a strengthening.
- MUST NOT attack Lemmas A, B or C: they are SOUND. Lemma A is unconditional; Lemma B's
  bounds and equality characterization are correct under counting measure on a finite unit
  set; Lemma C's feasible-set-inclusion argument is correct. The defect is confined to the
  naming/classification layer.
- MUST NOT claim any #833 issue row, and MUST NOT edit the #833 issue body.
- MUST NOT raise the claim ceiling above `G2`.
- MUST NOT claim the A4 census generalizes beyond the registered fully-shareable/nested
  accounting of the frozen 27-row A4 contract.

## 6. Pre-registered headline numbers (reproduced at freeze time, before implementation)

Reproduced on laptop-billy (python3 3.8.10) against the frozen
`interactions_witness.py` blob `70de5ec7`, using the corollary's own
fully-shareable/nested accounting (`joint = |channels_X union channels_Y|`,
`individual = |channels|`), over the 27-capability A4 contract:

| quantity | value |
|---|---|
| capabilities | 27 |
| unordered pairs | 351 |
| DEF-1: shipped labels contradicting Section 1.2's own definition | **56 / 351** |
| DEF-2: pairs satisfying more than one Section 1.2 label (taxonomy does not partition) | **287 / 351** |
| no-alarm control: genuinely disjoint-channel pairs, `independent` under BOTH readings | **8 / 8** |
| shipped census | independent 8, synergistic 161, redundant 182, interfering 0 |

Any implementation result that disagrees with these numbers is a defect in the
implementation, not a revision of the freeze.

## 7. Falsifiers of this tranche

- A pair of capabilities under the A4 contract admitted into two classes of the `CIP-1`
  partition, or admitted into none while satisfying `joint >= max`.
- A census disagreement between the two materially independent routes.
- A disjoint-channel pair not classified `INDEPENDENT` by the burden classifier.
- A proof of `joint = max => nested` that does not use strict positivity of `mu`.

## 8. Discipline

- Exact arithmetic only (`int` / `fractions.Fraction`). No floats in any claim.
- Stdlib only; every executor and test runnable as `python3 -I -B` and `python3 -I -O -B`.
- All compute on laptop-billy; the Mac is git/gh and single-file edits only.
