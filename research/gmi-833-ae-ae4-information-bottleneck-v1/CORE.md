# gmi-833-ae-ae4-information-bottleneck-v1

Section AE4, all eight rows: where the Information Bottleneck and the GMI
minimal predictive state actually coincide, and where they do not.

**Scope.** An 8-atom support, uniform exact prior `1/8`, all `Bell(8) = 4140`
**deterministic** encoders, seven registered worlds — five deterministic
targets, one exactly rational channel, and one three-valued target whose class
sizes force `log2(3)` into the arithmetic — and a nine-point exact rational
tradeoff ladder.

**No logarithm is ever evaluated.** An entropy is an exact map
`prime -> Fraction` denoting `sum_q c_q log2(q)`, and two of them are ordered by
the sign of `prod_q q^(D c_q) - 1`: a comparison between two integers. A value
prints as a plain rational only when its prime support is `{2}`, so the receipt
says `H(Y) = 2*log2(2) - 3/4*log2(3)`, not `1.4056`.

| result | numbers |
|---|---|
| `IB-1` formalisation | **6** crosswalk entries, each with a citation; `stochastic_encoders_optimised: false` as a checked field |
| `IB-2` the threshold | `EQUAL` **44**, `GMI_STRICTLY_REFINES` **41**, `IB_STRICTLY_REFINES` **0**, `INCOMPARABLE` **0** — both zeros reported; `T_GMI` becomes IB-optimal at `beta = 1` for six worlds and at `beta = 6` for the noisy channel |
| `IB-3` smallest counterexample | support **2**, channel `(0, 1/4)` at `beta = 1`, `T_GMI = 01` against the one-block optimum `00`; minimality by construction |
| `IB-3` proved absence | **0** incomparable optima over support sizes 2–6 searched exhaustively, and 0 on the registered worlds — `EARNED_BY_EXHAUSTION`, with the general statement labelled a **conjecture** |
| `IB-4` two orderings | **162,242** pairs where more information about `Y` is worse for control, **280,779** where it reverses, over **8** capacity classes |
| `IB-5` when to forget | merge is free **iff** the atoms share `p(Y|x)`; **12** free against **16** costly, **0** criterion mismatches |
| `IB-6` when to retain | **5 of 5** mechanisms `WITNESSED` — future task, transfer, revision, causal intervention, verifier need |
| `IB-7` two frontiers | predictive **11** members `(1,2) (2,1) (3,1/2) (4,0)`; control **8** members `(1,3/8) (2,1/4) (3,1/8) (4,0)`; they differ, **5** encoders on both |
| `IB-8` frozen predictions | `Q1`–`Q5` written into the freeze before any executor existed; **all five HELD** across all seven worlds |

**The finding that matters most.** Identification of the GMI minimal predictive
state with the IB optimum is not false and not true — it is true **above an
exact tradeoff threshold** and false below it, and the threshold is six times
larger for a noisy channel than for a deterministic target. That is the
qualifier the row asks for, and it is a number.

**A negative kept rather than deleted.** The counterexample this package first
went looking for — an IB optimum *incomparable* with `T_GMI` — does not exist at
this scope. The exhaustive search that refuted it is reported with its range,
the resulting structural statement is labelled a conjecture, the failure was
attributed to **one stage** (the target family, not the search), the matching
lever was applied — registered rational channels, for which `I(T_GMI;Y) < H(Y)`
— and the re-test found the counterexample at support size 2. The whole chain is
a field of the receipt, not a story told afterwards.

**Two routes that do not share an arithmetic.** Route A decomposes every entropy
into prime logarithms and orders by an exact integer power product. Route B
never factorises anything: it carries the **exponentiated** entropy `(2^H)^M` as
an exact rational and compares by cross-multiplying integers, and it self-checks
that engine against four hand-computed entropies and asserts that a scale which
fails to clear a denominator **raises** rather than rounding. They agree on the
relation totals, on `T_GMI` for every world, and on every threshold including
the noisy channel's `6`.

**Hostiles.** Five, each potent before detected. The sharpest is `H1`: compare
two entropies by their `log2(2)` coefficients alone — what a dyadic-only
implementation computes — and the order of `H(1/3,1/3,1/3)` against `H(1/2,1/2)`
**inverts**. That is the concrete reason the prime-log machinery exists.

**Null.** **0/24** false alarms on worlds whose target is a bijection of the
support evaluated at the top of the ladder, where the minimal sufficient
statistic is provably optimal; **7/7** recall on threshold targets at `beta = 0`,
where the one-block encoder provably wins.

**A correction to the section map.** The map says this package "needs AE3's
coding-language registry". Read against the eight row texts it is **not
load-bearing** — every row is an IB/rate-distortion requirement and none consumes
a prefix code or a description length. The correction is in `FREEZE_V1.md`,
written before any implementation blob existed.

## Reproduce

```bash
python3 -I -B  research/gmi-833-ae-ae4-information-bottleneck-v1/ae4_information_bottleneck_v1.py > /tmp/ae4.json
cmp /tmp/ae4.json research/gmi-833-ae-ae4-information-bottleneck-v1/RESULT_V1.json
python3 -I -B  research/gmi-833-ae-ae4-information-bottleneck-v1/independent_ib_oracle_v1.py
python3 -I -B  research/gmi-833-ae-ae4-information-bottleneck-v1/test_ae4_information_bottleneck_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae4-information-bottleneck-v1/test_ae4_information_bottleneck_v1.py -v
```
