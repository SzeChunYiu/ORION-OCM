# CAPABILITY_PREDICTOR_EVALUATION_THEOREMS_V1

Named results for `gmi-833-capability-predictor-evaluation-v1`.

Claim ceiling:
`GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR_AT_REGISTERED_FINITE_SCOPE`

Every number below is reproducible from `RESULT_V1.json` and
`ROUTE_B_RESULT_V1.json`. All arithmetic is exact `Fraction`/`int`; no float
appears in any claim.

---

## KE-0 — the predictor under test is the parent's, unmodified

**Statement.** For each held-out universe, `F` is the parent module at blob
`7f1bb6808901be2291bf575ee3178247d14d01d4`, with exactly the 23-name
`REGISTRATION_SURFACE` rebound and nothing else.

**Scope / quantifiers.** All five installations (`SIGMA_1` → `SIGMA_SYN`,
`SIGMA_ARCH`, `SIGMA_REAL`, `SIGMA_REAL2`, `SIGMA_REAL3`).

**Evidence.** Two independent proofs. (i) In-process: `install_universe`
captures a sha256 over the `co_code` of every function and method in the parent
module before and after rebinding and refuses to return unless they are equal;
a surface with a missing or extra name is refused with `ValueError`. (ii)
Cross-run: the git blob sha of the parent file, checked by CI against the real
tree.

**Assumptions.** `BETA`/`BETA_SUM` are deliberately outside the surface — they
are the U-2B premises `TypedUncertainty.__init__` validates and the contract
KE-6 is measured against.

**Falsifier.** Any change in the before/after `co_code` digest, or a blob-sha
mismatch.

**Forbidden extrapolation.** The bytecode digest recorded in
`FROZEN_PREDICTIONS_V1.json` is interpreter-version specific (129 code objects
under CPython 3.13 versus 138 under 3.8) and is **not** used as a cross-run
identity check. Only the in-process comparison and the blob sha are.

---

## KE-1 — held-out synthetic machine species

**Statement.** On `SIGMA_SYN` — 64 modular head machines, disjoint from the
parent's `SIGMA_1` — `F` emits a point on 6,136 of 51,840 registered inputs,
abstains on 14,408, refuses 31,296 as inconsistent, raises 0 exceptions, and is
**wrong on 0 of 45,800 (input, consistent-world) pairs**. The emitted object
contains the externally evaluated capability on **234,240 of 234,240** pairs.

**Scope / quantifiers.** For every registered input and every realization in the
survivor set; external capability obtained by *running* each machine over the
whole 31-word protected battery and comparing exactly, never by reading a
registered table.

**Power.** Point rate `767/6480`; abstention rate `1801/6480`; abstention among
answerable inputs `1801/2568`. Abstention is not counted as a hit. All four
registered thresholds are non-degenerate (2,446 / 898 / 180 / 132 inputs at
`2/11`, `5/11`, `7/11`, `9/11` where the survivors genuinely disagree about
meeting `tau`), so the census cannot be satisfied by a constant answer.

**Disjointness.** Exhaustive 64 × 32 descriptor comparison: 0 collisions, plus
the one-coordinate separator `rho[3] = 0` on `SIGMA_1` versus `rho[3] ∈ {1,2}`
on `SIGMA_SYN`.

**Registration truthfulness.** The closed-form capability law agrees with
brute-force simulation on **64/64** machines.

**Assumptions.** The registered universe is the true universe (KP-1D).

**Falsifiers.** A point emission differing from the external capability of any
consistent realization; law-versus-simulation disagreement on any machine.

**Strongest parents.** KP-1A/1B/1C (#1012); Manski's identified sets; Chow's
reject option.

**Forbidden extrapolation.** Nothing is claimed about machines outside
`SIGMA_SYN` (see KE-7).

---

## KE-2 — held-out known architectures

**Statement.** On `SIGMA_ARCH` — 128 machines drawn from four named mechanism
families (`FF` window, `REC` recurrent accumulator, `CTR` saturating counter,
`STK` bounded stack) — `F` emits a point on 10,152 of 51,840 inputs, abstains on
16,680, refuses 25,008, and is **wrong on 0 of 121,920 pairs**; coverage
**528,960/528,960**. Abstention among answerable inputs `695/1118`.

**Blindness, enforced structurally.** (i) No realization record carries a
mechanism tag — every field of `ARCH_RAW[i]` is an integer or a tuple of
integers, machine-checked. (ii) An `ast` reference audit over the descriptor
encoder, `make_spec`, `cap_table`, `install_universe` and all five mask builders
finds zero references to `ARCH_LABELS`/`labels`/`family`/`label`; its negative
control is a planted encoder reading `ARCH_LABELS[0]`, which the audit flags.
(iii) Rebuilding the entire universe under all **24** permutations of the family
names reproduces `ARCH_RAW` exactly, every time. (iv) `k` is strictly coarser
than family identity: `REC` and `CTR` both map to `k = 1`.
See `SUPPLEMENT_1_BLINDNESS_CORRECTION.md` — an `ast` *literal* audit claimed in
the frozen `BLINDNESS_V1.md` was withdrawn as false, not narrowed.

**Registration truthfulness.** The closed-form law — derived from the claim that
a saturating counter with cap ≥ the word length tracks `ones(u)` exactly while a
bounded window or a stack height does not — agrees with brute-force simulation
on **128/128** machines.

**Falsifiers.** Any of the four blindness checks failing; law-versus-simulation
disagreement; a wrong point.

**Strongest parents.** Myhill–Nerode state equivalence; the AJ9A post-hoc family
fingerprints; KP-1B.

**Forbidden extrapolation.** These are finite analogues of the named families,
not the families themselves; no claim is made about real neural, stack or
counter systems at scale.

---

## KE-3 — real trained systems: `F` is sound where registration is truthful

**Statement.** Across three independently frozen populations of 32 real
torch-trained systems each (96 systems, 288 trained heads, CPU, one thread,
registered seeds, a sha256-pinned real source), `F` is **wrong on 0 of 161,632
(input, truthfully-registered-world) pairs**:

| population | truthfulness | truthful pairs | violations on them | untruthful pairs | bridge failures |
|---|---:|---:|---:|---:|---:|
| `SIGMA_REAL` (widths 2, 8) | 19/32 | 34,304 | **0** | 8,112 | 0 |
| `SIGMA_REAL2` (widths 4, 16) | 28/32 | 63,664 | **0** | 1,152 | 128 |
| `SIGMA_REAL3` (widths 12, 32) | 26/32 | see receipt | **0** | see receipt | see receipt |

**Scope / quantifiers.** Protected battery: length-12 binary words read off
`/usr/lib/python3.8/argparse.py` (96,311 bytes, sha256
`cc1e3c3a…c44fd7`), training windows `[0,6000)` and protected-eval windows
`[6000,8000)`, disjoint by position. A task counts as solved only at exact
accuracy `Fraction(correct, total)` meeting the registered predicate.

**Assumptions.** Truthful registration — precisely the premise KP-1D says cannot
be removed.

**Falsifier.** A soundness violation on a truthfully-registered world. None
occurred in any of the three populations.

**Strongest parents.** KP-1B and KP-1D (#1012); the #903 real-system protocol.

**Forbidden extrapolation.** This does not establish that a truthful
registration is obtainable for arbitrary trained systems — see KE-3D, which says
it is not, at this scope.

---

## KE-3D — BOUNDARY, EARNED BY COUNTEREXAMPLE: the real-system bridge

**Statement.** Solvability of the protected tasks by SGD-trained systems at the
registered budget is **not a function of the registered structural coordinates**
`(mechanism, width, skip feature, trained-head set)`. Three registration laws
were frozen prospectively, each on a population the previous outcomes did not
contain, and all three were falsified by their own pre-registered falsifiers.

| law | registered claim | counterexample | truthfulness |
|---|---|---|---:|
| V1 (capacity) | parity solved by any recurrent system **or** any width ≥ 8 | `(GRU, 8, w=1)` reaches 261/400 on parity; `(MLP, 8, ·)` fails both | 19/32 |
| V2 (capacity + no skip shortcut) | parity/mod-3 solved iff `GRU`, width ≥ 8, `w = 0` | `(GRU,16,w=0)` misses mod-3 by **19/2000**; `(GRU,16,w=1)` hits parity **exactly** | 28/32 |
| V3 (99/100 band + width ≥ 16) | parity/mod-3 solved iff `GRU`, width ≥ 16 | `(GRU, 12, ·)` reaches exact accuracy on parity **and** mod-3 at both `w` | 26/32 |

Truthfulness does not improve monotonically (19/32 → 28/32 → 26/32), which is
the signature of a threshold phenomenon in optimization rather than a missing
clause in the law.

**Why this is structural at this scope, not a missing revival.** Each law was
falsified in *both* directions by the same population — a system predicted
solved that missed, and a system predicted unsolved that hit. A fourth law
fitted to these four counterexamples would be tuning to observed outcomes, which
the standing directive forbids; `FREEZE_V3_ADDENDUM.md` section 6 pre-registered
this terminal before the V3 outcomes existed.

**What is NOT concluded.** That `F` is unsound (KE-3 says the opposite, on
161,632 pairs); that no registration law exists at a larger training budget or a
coarser capability contract; that the row is closeable on synthetic data. The
issue row *Test predictor on real trained systems* is therefore **left open**.

**Strongest parents.** Weiss, Goldberg & Yahav (2018) and Merrill (2019) on the
gap between what a recurrent net can represent and what training finds; #903's
banded classification, imported as the V3 lever.

---

## KE-4 — qualitative failure predicted before evaluation

**Statement.** For every one of the 5 × 51,840 registered inputs, the binding
failure mode among the parent's ten was emitted **before any outcome oracle
existed** and bound by sha256 in the freeze commit; the externally attributed
mode, recomputed from measured capabilities by the outcome oracle, is reported
as a confusion matrix stratified by order class.

**The honest reading of the diagonal.** On a universe whose registration is
truthful, the registered and measured capability tables are pointwise equal, so
the predicted and externally attributed modes are equal by an algebraic identity
— the 0 disagreements on `SIGMA_SYN` (20,544 attributable inputs) and
`SIGMA_ARCH` (26,832) confirm that the identity holds and that no bookkeeping
error intervenes, and nothing more. **The substantive evidence is the real-system
universes, where registration is not truthful and the matrix goes genuinely
off-diagonal**; that off-diagonal mass is the measured cost of a bridge failure,
and it is reported per stratum in `RESULT_V1.json`.

**The KP-2D stratification, frozen in advance.** Each input carries a class
fixed at freeze time: `ORDER_FREE` (all 120 cut orders agree), `CONJUNCTIVE`
(they do not, so no order-free attribution exists) or `NO_CROSSING`. For
`SIGMA_SYN`: 19,880 / 28,304 / 3,656. For `SIGMA_ARCH`: 19,980 / 28,084 /
3,776. For `SIGMA_REAL2`: 17,242 / 30,610 / 3,988. For `SIGMA_REAL3`: see
receipt. Scoring a `CONJUNCTIVE` case as a miss would measure the ambiguity
KP-2D already proved, not the predictor; the strata are never pooled.

**Falsifiers.** Any disagreement on a truthfully-registered universe (this would
indicate a bookkeeping error, since the identity forbids it); a replayed
prediction stream whose sha256 differs from the frozen one.

**Forbidden extrapolation.** The diagonal on truthful universes must not be
reported as independent confirmation that the taxonomy predicts real failure.

---

## KE-5 — quantitative resource/capability curves predicted before evaluation

**Statement.** Eight registered curve cases × four thresholds × five universes
sweep the resource coordinate `R.budget` across all three registered budgets.
The predicted disposition and point at every swept point were frozen before any
outcome oracle existed; the replay reproduces the frozen curve with **0
mismatches**, and every point emission agrees exactly with the externally
evaluated capability on the truthfully-registered universes.

**Scope.** Reported as per-point exact agreement counts. No fitted summary and
no error norm is computed: an exact predictor either matches a point or does
not.

**Falsifiers.** A replayed curve point differing from the frozen one; a point
emission whose external value differs; a vacuous census (0 identified points).

**Forbidden extrapolation.** The curve is over the three *registered* budgets,
not over a continuum.

---

## KE-6 — empirical calibration error, measured exactly

**Statement.** The parent proved exact finite coverage with all registered
relations assumed good (coverage exactly 1) and explicitly did not claim
empirical calibration. This result measures coverage under the **registered
fault law**, which is the event structure the `beta`s are premises about: the
typed-uncertainty source and each of the four registered relations `M`, `D`,
`B`, `H` fails independently at exactly its registered rate
(`alpha`, `1/100`, `1/200`, `1/500`, `1/50`), and on failure the true world need
only satisfy the surviving cuts. Coverage is then an exact rational obtained by
enumerating all **32** fault patterns with exact weights.

On `SIGMA_SYN`, against the U-2B nominal lower bounds `L = 913/1000`
(`alpha = 1/20`) and `L = 863/1000` (`alpha = 1/10`):

| `alpha` | `L` | emissions | abstentions | abstention rate | min empirical coverage | violations |
|---|---|---:|---:|---|---|---:|
| 1/20 | 913/1000 | 5,184 | 3,872 | 121/162 | 1191567620413/1224000000000 | **0** |
| 1/10 | 863/1000 | 7,680 | 5,268 | 439/640 | 2380730729/2448000000 | **0** |

**Every calibration figure is reported next to its abstention rate**, because a
predictor that abstains whenever unsure is trivially well covered; and the
**point emissions are gated separately** (minimum point coverage and a
per-emission violation count), because the set-coverage margin is conservative
by construction — the all-good fault pattern alone carries weight close to the
nominal bound.

**Feasible sets carry no coverage number at all.** U-1a has no probability
premise, so the 1/3 of emissions carrying a `FeasibleSet` are excluded from the
calibration census rather than assigned a coverage of 1.

**Hostile with teeth.** Inflating every `beta` twenty-fold produces coverage
below nominal on the same grid — `HE5_inflated_fault_law`, detected.

**Assumptions.** The registered fault law is a *model* of relation failure, not
a measurement of it. Arbitrary dependence between fault channels is not assumed
away in the bound (U-2B), but the enumeration itself uses independent channel
rates.

**Falsifier.** Any emission whose exact empirical coverage falls below its own
emitted `coverage_lower`.

**Strongest parents.** Dawid (1982); Vovk, Gammerman & Shafer (2005); U-2B and
U-4B of #851; El-Yaniv & Wiener on the abstention/coverage trade.

**Forbidden extrapolation.** This is exact coverage under a registered finite
fault model. It is not asymptotic calibration, not conformal validity, and not a
statement about any real distribution shift.

---

## KE-7 — out-of-distribution failure, with the boundary made exact

**Statement.** OOD is defined structurally: a world is out-of-universe iff its
realization is not a member of the installed universe. Only the three cuts that
are properties of the *world* — expressivity, development reachability,
observation — can exclude such a world; the search-budget cut is a statement
about the analyst's enumeration and the typed-uncertainty mask indexes
registered members only.

`SIGMA_OOD` relaxes each generator coordinate of `SIGMA_SYN` one at a time
(moduli `{4,5,12}` beyond the registered `{1,2,3,6}`; a second register `w = 2`;
a fourth head `h ∈ 8..15`), minus the registered 64, leaving **272** genuinely
out-of-universe worlds.

Two strata, reported side by side in `RESULT_V1.json` and never merged:

- **in-universe** — 45,800 (input, world) pairs on `SIGMA_SYN`, **0 soundness
  violations**, as KP-1B requires. This is the region over which soundness was
  actively attacked and held.
- **out-of-universe** — the exact count of (input, OOD-world) pairs, how many lie
  inside the emitted identified set, and how many point emissions are wrong,
  broken down by which coordinate was relaxed.

**The attribution that matters.** A wrong point on an out-of-universe world is
**not** a new finding: it is KP-1D restated, and it is attributable to
registration, not to `F`. Reporting it as a soundness violation would be a
category error. The scientifically interesting quantities are the size of the
OOD region over which `F` nonetheless abstains, and the exact boundary between
the two regimes.

**Falsifier.** A soundness violation in the in-universe stratum. None was found,
across `SIGMA_SYN`, `SIGMA_ARCH` and the truthfully-registered part of all three
real populations.

**Forbidden extrapolation.** "Sound on OOD data" is never claimed and is false
in general; what is claimed is the exact in-universe verified region and the
exact measured behaviour outside it.
