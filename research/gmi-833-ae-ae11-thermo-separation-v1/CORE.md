# gmi-833-ae-ae11-thermo-separation-v1

Section AE11 of issue #833 asks that four entropy-like notions be kept formally
distinct, that GMI resource claims be split into logical and physical ones, that
Landauer-style lower bounds be audited rather than over-read, that driven-system
upkeep be modelled only where a physical system is registered, and that logical
irreversibility be compared with physical dissipation at the right scope.

The discipline of this package is that it **computes no energy value at all**.
Landauer statements are carried as `W_min = m * k_B T ln 2` with `m` an exact
integer; statistical-mechanical entropy is carried as the integer microstate
count `W` with the exact statement `S_stat = k_B ln W`; thermodynamic entropy
change is the exact rational `Q / T` in registered units. Nothing transcendental
is ever evaluated numerically, and the receipt contains no float.

| what the row asks | the exact answer |
|---|---|
| four notions kept distinct | **12 of 12** ordered pairs witnessed non-functionally-dependent on 8 registered objects: 2 witnesses exhibit the slack in the one registered definitional relation `H_shannon <= log2 W`, **10** are registered-independent, **0** unwitnessed |
| the classic case | `R_UNIFORM_BLOCK` has maximal `H_shannon = 6` bits while its 64 members carry `K_U` **11 (2 strings), 13 (6), 14 (56)** on the frozen machine |
| logical versus physical resources | **24** resources classified, **12** `LOGICAL_COMPUTATIONAL` and **12** `PHYSICAL_ENERGETIC`; instantiated physical resources **0** |
| Landauer audit | `m = 0` (`F_BIJECTION`), `1` (`F_AND`), `1` (`F_ERASE1`), `2` (`F_ERASE2`); **16** bound records, **4** flagged vacuous and `UNFALSIFIED_BOUND`, **12** carrying a `violated_by` witness |
| no whole-system energy from bit erasure | for **every** registered map the two device models carry the **same** erased-bit count and registered operation counts differing by exactly **5**: `F_ERASE2` erases `2` bits under both while the counts are `2` and `7` |
| driven-system upkeep | registered physical systems **0**; the frozen 10-term vocabulary scores **0** hits over the 7 registered claims and **3** hits on the planted fixture |
| correct scope | `F_BIJECTION`: erased bits `0`, Landauer bound `0`, registered operation count `1 > 0`. `F_ERASE2`: erased bits `2`. For `F_AND` the count-based `m = 1` is **strictly below** the distributional drop, bracketed in `(19/16, 6/5)` |

## The frozen machine, and why its numbers are machine-relative

`K_U` is the length of a shortest program on one frozen prefix-free machine with
the instruction set `EMIT0` (2 bits), `EMIT1` (2), `HALT` (2),
`REPEAT_LAST_K_N` (7), `COPY_PREFIX` (6), searched exhaustively to the frozen
cap `LCAP = 14`. The instruction codewords form a complete prefix code — Kraft
sum exactly `1` — and a program is a bit string that decodes to codewords ending
in `HALT` with nothing left over, so the program set is prefix-free as well; its
Kraft sum up to the cap is exactly `67/128`.

Every one of the 64 registered strings has a program at or below the cap, so
**0** strings saturate `LCAP` and the registered symbol `>LCAP` is never needed
on the roster. That `K_U` is relative to this machine and to this cap is a
property of the definition, recorded in the receipt, not a defect concealed.

**One honest tension with the freeze.** `FREEZE_V1.md` phrases the classic
witness as `K_U` ranging "from a frozen small constant to `m` bits". At string
length `6` with a five-instruction prefix-free set that numeric phrasing is
arithmetically unreachable: an emit costs 2 bits and `HALT` costs 2, so the
ceiling is pinned at `6*2 + 2 = 14` and the floor cannot be small. What is
witnessed — and all that is claimed — is that a single maximal Shannon entropy
value of `6` bits coexists with members at **three** distinct `K_U` values
spanning `11` to `14`. The receipt carries this as an explicit caveat on
prediction `AE11-P1` rather than paraphrasing the freeze as satisfied.

## Two routes

Route A makes a single ordered pass over the bit-string program space and
decodes each candidate, computes Shannon entropy by closed-form exponent
algebra, reads the microstate count off the registered support, and derives
erased bits from the forward image. Route B enumerates instruction sequences
depth-first in instruction-table order with **no decoder at all**, computes
Shannon entropy by building the canonical code tree and accumulating integer
leaf depths over a common power-of-two denominator, builds the microstate set
explicitly, derives erased bits by partitioning the domain into preimage
classes, and represents register states as integers under bitwise operations
rather than as strings. Route B has no executable import of route A; the test
parses route B's AST and asserts it. The two agree on every value, including
the whole 64-entry `K_U` table and the `67/128` program Kraft sum.

## Bounds, and the ones that close nothing

Every bound is emitted with a definitional range and a vacuity flag. Four are
vacuous and are reported as `UNFALSIFIED_BOUND` with `used_for_closure: false`:
the Landauer and entropy-drop bounds of `F_BIJECTION` (value `0` against a
definitional floor of `0` — a non-negative quantity cannot fall below zero) and
the Gibbs bounds of the two maximal-entropy objects (value `6` against the
alphabet ceiling `6`). Reporting them as vacuous is the point of the machinery:
Landauer's bound genuinely says nothing about a logically reversible map. The
12 non-vacuous records each carry a `violated_by` witness from an explicitly
relaxed class — dropping the no-residual-correlation assumption makes the
relative erased-bit count the integer `0`, which is strictly below every
positive `m`.

## Null and no-alarm

Detector: how many of the 12 ordered pairs a roster can witness. The registered
roster witnesses **12**. Over **200** random rosters drawn from a deterministic
integer generator the counts are **5 (6 trials)** and **6 (194 trials)**; the
largest is **6** and **0** trials reach 12. The primary comparison is
threshold-free — the witness strictly exceeds the largest null magnitude — and
no threshold is used anywhere. The no-alarm case holds: the conflation detector
reports **0** unwitnessed pairs on the clean roster. Witnessing needs an exact
tie in the fixed quantity, which random rosters supply only for `K_U` and the
microstate count, and that is exactly why they stop at 6.

## Hostiles

All five registered hostiles are potent first and detected second:
`H_ENTROPY_CONFLATE` (microstate counts forced to be a function of
`H_shannon`; witnessed pairs fall below 12), `H_ERASED_BITS` (`F_ERASE2`
reported as 1 against the recomputed 2), `H_LCAP` (cap 13; the registered roster
string `000010` moves from 14 to `>LCAP`), `H_OVERHEAD_EQUAL` (device counts
`[2, 7]` collapse to `[2, 2]` and the non-inference witness is gone),
`H_PHYSICAL_CLAIM` (a planted instantiated physical resource takes the count
from 0 to 1).

## Rows this package does not close

Three AE11 rows stay **OPEN**. They ask for measured energy on real hardware,
for a matched information-savings against energy-savings experiment, and for a
biological separation of metabolic upkeep from information processing. Each is
instrument-blocked; the byte-exact row text and the specific instrument each one
needs are carried in
`ISSUE_833_RECONCILIATION_AE11_THERMO_SEPARATION_V1.json` and in
`MANIFEST_V1.json`. The exact non-inference witness above is the formal reason
the second of them is required; it is not a substitute for it.

Claim ceiling:
`GMI_833_AE11_FOUR_ENTROPY_NOTIONS_SEPARATED_AND_LANDAUER_SCOPE_AUDITED_WITHOUT_ANY_ENERGY_MEASUREMENT`.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae11-thermo-separation-v1/test_ae11_thermo_separation_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae11-thermo-separation-v1/test_ae11_thermo_separation_v1.py -v
python3 -I -B research/gmi-833-ae-ae11-thermo-separation-v1/ae11_thermo_separation_v1.py
python3 -I -B research/gmi-833-ae-ae11-thermo-separation-v1/independent_thermo_oracle_v1.py
```

The executor writes `RESULT_V1.json` to stdout, byte-identical in both modes and
on CPython 3.8 and 3.12. 65 tests; verdict `GREEN`; 32 named checks all true.
