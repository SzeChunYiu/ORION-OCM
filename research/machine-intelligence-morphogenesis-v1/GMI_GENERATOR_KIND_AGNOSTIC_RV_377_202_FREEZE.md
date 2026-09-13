# RV-377-202 — FREEZE: the leave-one-out ablation re-run with a kind-agnostic generator

Revival of the RV-377-118 Lane C instrument finding (`GMI_RV_377_118_LANE_C_INSTRUMENT_NOTE_V1.md`):
13 of the 33 ablatable kinds — `ABSTAIN, DENSE, KVSTORE, LINEAR, LOOKUP, MATERIALIZE, NEAREST, PROGEXEC,
PROGRAM, SCORESELECT, TABLE, VERIFY, VERSIONED` — returned `STRUCTURAL_TO_GENERATOR` on every ecology:
the mutation grammar constructed them **by name** (`seed_genotype`, `op_insert_verifier`, `op_materialize`,
`op_add_lineage`), so deleting the kind crashed the generator before any search.

## Root cause and minimal justified change

One stage: the GENERATOR, not the search, the ecology, or the theory. `seed_genotype` picks its founding
carrier from a fixed tuple and wires fixed execution kinds; three operators insert fixed kinds; `mutate`
does not treat an operator exception as a failed draw. The repair (commit before this run, additive):

* every kind the generator names is looked up in the live alphabet (`k in morph.KINDS`); an absent seed
  carrier or execution kind falls back to the same-class alternatives, an operator whose kind is absent
  returns the genotype unchanged;
* `mutate` charges an operator exception as a failed draw instead of propagating it.

With the full alphabet every filtered list equals the original tuple and no exception path is taken, so the
draw sequence is unchanged: `test_gmi_morphgen_kind_agnostic.py` pins the digest of 200 generator outputs
computed on main@fa5a754f **before** the edit (`7698605a…c1e1`) and requires the edited generator to
reproduce it. Every existing receipt therefore stands.

## Frozen predictions (extending RV-377-110 T3/T4 and RV-377-118 C1/C2 to the 13 kinds)

Units: 13 kinds × 3 rule-40 discriminating ecologies (`E_smooth1`, `E_smooth3`, `E_sym5`) = 39 runs,
`primitive_ablation.run_one(kind, eco, 0, 20000, tag_prefix="ABL2")`, receipts
`STAGE_B1_ABL2_<kind>_<eco>_S0.json`. A kind is REDUCIBLE on an ecology iff the reduced alphabet still
reaches an admissible archive elite (θ = 0.85) there; IRREDUCIBLE otherwise. Baselines are the existing
`STAGE_B1_ABL_FULL_<eco>_S0.json` (admissible on all three).

| id | prediction | falsifier |
|---|---|---|
| **C3** | Fewer than 6 of the 13 kinds are IRREDUCIBLE on every ecology: the alphabet carries alternatives (`LOOKUP`/`NEAREST`/`SCORESELECT`; `TABLE`/`KVSTORE`; `VERIFY`/`VERIFYTAB`; `DENSE`/`PROGRAM` seeds) | ≥ 6 kinds irreducible everywhere |
| **C4** (RV-377-110 T4 restated) | `DENSE`, `TABLE`, `KVSTORE`, `PROGRAM` are NOT all irreducible: deleting any one of the four leaves an admissible elite on ≥ 1 ecology | all four irreducible on all three ecologies |
| **C5** (RV-377-118 C1 restated) | the irreducible set differs between ecologies: ≥ 1 kind IRREDUCIBLE on one ecology and REDUCIBLE on another | identical verdict vectors across the three ecologies |
| **C6** | zero `STRUCTURAL_TO_GENERATOR` or `ERROR` receipts: every one of the 39 units executes a genuine search | any non-executed unit |

Kill condition: if C6 fails the repair is incomplete; the failing kind is diagnosed and the run repeated
after a second commit, never adjudicated with gaps. Ledger: RV-377-202. Terminal names:
`PRIMITIVE_ABLATION_COMPLETE_OVER_33_KINDS_AT_REGISTERED_SCOPE` / `…_INCOMPLETE_<n>_UNITS`.

---

## Disclosed observation during execution (not a prediction, not a change)

The 39 ABL2 units are far more expensive than the RV-377-110 sizing implied, and the cost is extremely
uneven across kinds. Measured on billy-old (CPU time ≈ elapsed for every worker, i.e. these are compute
costs, not contention):

| unit | CPU seconds |
|---|---|
| median completed ABL2 unit | ≈ 3 700 – 7 000 |
| `ABSTAIN_E_smooth1` | 4 502 |
| `DENSE_E_smooth1` | 6 981 |
| slowest two still running at the time of writing | **30 489** and **25 413** |

The same pathology appears outside this lane: the B6 source search `E_twin2 S2` (`RV-377-180`, an unmodified
20 000-evaluation B1 search on a random-table ecology) had consumed **28 713 CPU-seconds at 100 % CPU** while
its siblings `E_twin0 S0` and `E_rnd2 S2` finished in 1 836 s and 692 s — a 15–40× spread on the *same*
instrument with only the seed and target table differing.

So the per-candidate evaluation cost of the neutral search varies by more than an order of magnitude with
the alphabet and the ecology, at a fixed evaluation budget. The charged-evaluation count (20 000) is
therefore **not** a proxy for charged compute, and any resource statement that treats the two as
interchangeable is wrong by up to 40×. This is the charged-lifecycle analogue of the chart-cap finding in
`RV-377-039/040`, where a nominally fixed budget hid a 10^5–10^6 spread in real work.

Recorded here because it was observed while executing this freeze; it changes no prediction, no threshold
and no unit of RV-377-202, whose predictions C3–C6 are scored on verdicts, not on wall-clock. It is a
standing caveat for any future sizing estimate and for `B_search` accounting.

## Adjudicator validated on real data before use (partial run, NOT the adjudication)

`primitive_ablation.adjudicate` was run on the receipts in hand and hand-checked before it is trusted
to score C3–C6:

* `STAGE_B1_ABL_SUM_E_sym5_S0` — best capability 0.8854 ≥ θ, admissible carriers KVSTORE/PROGRAM/TABLE →
  hand verdict REDUCIBLE, matches the adjudicator.
* `STAGE_B1_ABL2_ABSTAIN_E_smooth1_S0` — best 0.8958 ≥ θ → REDUCIBLE, matches.
* `STAGE_B1_ABL_TABLE_E_sym5_S0` — `STRUCTURAL_TO_GENERATOR` → excluded from the tested set, **not**
  silently counted as REDUCIBLE. The `MISSING` path is exercised too (`GATE_E_smooth1` is still running).

Partial state at the time of validation: **25 kinds fully tested, 7 awaiting their ABL2 re-run, 1 missing**.

> Among the 25 fully-tested kinds, **every one is REDUCIBLE on all three ecologies** — deleting it still
> leaves an admissible elite. Irreducible-everywhere count so far: **0**.

Read carefully, this is a statement about *this* ablation's question only: no single primitive is necessary
for reaching admissibility on these three ecologies at 20 000 charged evaluations. It does not say the same
machines are found without it, and single-kind deletion does not test pairs or larger subsets, so it is not
a minimality result for the alphabet. C3–C6 are **not** scored here; this section exists so that the
instrument is known-good before the verdicts are read, per the programme's validate-the-checker-first rule.
