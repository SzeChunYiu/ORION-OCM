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
