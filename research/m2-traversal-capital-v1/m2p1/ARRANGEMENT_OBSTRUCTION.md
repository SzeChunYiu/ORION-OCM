# Why d ≥ 2 cannot be tested here — and why that is the same problem as frequency ranking

Four attempts to test whether the developmental benefit survives at generalisation
distance `d ≥ 2` all failed. Rather than attempt a fifth, the constraint was derived.
It is a genuine obstruction, and it traces back to a specific line in the registered
learner.

## Three constraints, and they cannot be satisfied together

| constraint | requirement | wants |
|---|---|---|
| **recovery** | `train_n ≥ c·m` — the learner must see enough arrangements to mine the motif set | train_n **large** |
| **novelty** | `train_n · (k(m−1)+1) < A(m,k)` — distance-2 targets must exist at all | train_n **small** |
| **depth** | `2·Σᵢ mⁱ ≤ b_min(2k)` — the guided stream must reach the composition first | k **small** |

`c ≈ 5` is the *lenient* end of the measured range (E5 used 35 training items for 6
motifs, `c = 5.8`; E8 used 66 for 7, `c = 9.4`). `A(m,k)` is the measured count of
**canonical** arrangements — only ~5 % of combinations are the first-in-enumeration
program for their normal form.

The depth bound uses `b_min`, not `b_max`: admission requires **every** held-out target to
be non-inferior, so the binding case is the cheapest target, not the dearest. Using
`b_max` is what made `k = 4` look feasible when it empirically was not.

Swept over the whole grammar:

```text
novelty + depth feasible : 2 configurations
ALL THREE feasible       : 0 configurations

VERDICT: ARRANGEMENT_GENERALISATION_NOT_TESTABLE_IN_THIS_GRAMMAR
```

## This retro-explains every failed attempt

| attempt | config | why it was infeasible |
|---|---|---|
| D1/D2 | m=12, k=4, train=120 | depth: `2g = 45 240` vs `b_min = 21 846`; `ORACLE_FAMILY` also failed, confirming depth not library |
| M8D1/D2 | m=8, k=4, train=30 | one favourable draw that did **not** replicate (4 seeds: −30 % to +19 %) |
| k=3 saturated | m=12, k=3, train=120 | novelty: 120 ≫ 18, only 4 targets at d≥2 |
| feasible attempt | m=12, k=3, train=18 | **recovery**: needs ≥ 60, had 18 → library harmful at both distances in 6/6 seeds |

The last one is the informative failure: it satisfied novelty and depth, and starved on
recovery — which is the constraint the first feasibility map omitted.

## The root cause is the frequency ranking

Why is `m` capped so tightly? Because the motif set must be **substring-disjoint** — the
[learnability condition](LEARNABILITY.md) — and that is required only because
`learn_generator` ranks fragments by `(support count DESC, length DESC)`. A shared
substring accumulates strictly higher support than the motifs containing it and displaces
them from the fixed top-16.

Substring-disjointness caps the motif alphabet at

```text
m · (ℓ − 1) ≤ P²        (only P² distinct length-2 strings exist)
```

so with `P = 4` primitives, `m ≤ 16/(ℓ−1)`. That cap is what starves `A(m,k)`, and a
starved `A(m,k)` is what makes recovery and novelty irreconcilable.

**So the obstruction to testing U2 at `d ≥ 2` and the recommendation to "learn utility,
not frequency" are the same problem.** Frequency ranking forces substring-disjointness;
substring-disjointness caps the alphabet; the capped alphabet makes arrangement novelty
untestable. A utility-based admission rule — scoring `E[ΔB] − C_match − C_use − C_verify`
rather than support count — would not require disjointness, would permit a much larger
motif alphabet, and would move `ALL_THREE` off zero.

## Consequences

**For the claim.** U2 is bounded at `d = 1` **by the substrate**, not by the experiments.
The hostile review's reading stands, and no further run in this grammar can change it.
`d ≥ 3` was already empty by counting; `d ≥ 2` is now shown untestable under the
mechanism's own operating conditions.

**For the programme.** This is a concrete, quantified obstruction for U6/U10
open-endedness: a substrate whose abstraction alphabet is capped by its own ranking rule
cannot exhibit generalisation over novel arrangements, however much compute is applied.

**What would make it positive**, in order of directness:

1. **Replace frequency ranking with utility ranking** in admission — removes the
   disjointness requirement and the alphabet cap. Smallest change, largest effect, and
   independently motivated by the non-monotone dose-response.
2. **Enlarge the grammar** (`P > 4`, or `max_length > 8`) — raises `A(m,k)` directly.
3. **Relax the integration mode** to `λ(z)` with `ε` fallback — raises the depth ceiling
   from `2g ≤ b_min` to `g/ε ≤ b_min`, buying room in `k`.

All three are already on the roadmap for other reasons, which is corroboration rather
than coincidence.

## Instrument defect in the first P = 6 run — recorded, guarded

The first extended-grammar distance run reported `seed 1000: rec=0/10 lib=0 | d1 0.0% |
d2 0.0%`. That was **not** a distance result. The 200 000-slot budget is sized for the
registered grammar (87 381 programs); at `P = 6` the space is 2 015 539 programs and
length-8 targets begin at slot 335 928, so **no training target was solvable**, the
library was empty, and 0 % / 0 % is `CONTINUED ≡ RESET` with nothing served.

A silent zero from an unserved arm is the same defect class as the [G4 null-arm
false-FAIL](RESULT.md) earlier in this lane. Repair: budget default raised to cover the
full grammar at the chosen `P`, and a hard `BUDGET_INSUFFICIENT` terminal whenever fewer
than half the training targets solve — so the run fails loudly instead of reporting a
result it did not measure. Log preserved as `records/EXT_DISTANCE_200k_INVALID.log`.

The re-run (4 seeds, 2.1 M slots, parallel) is the one whose result counts.
