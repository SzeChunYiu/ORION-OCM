# Grand GMI Structural Neural Bound Theorem V1

Status: **THEOREM / DERIVED CLASS LOWER BOUND + ATTAINED TIGHTNESS + EXHAUSTIVE ENUMERATION**
Date: 2026-09-13

Authority for the machinery: `MORPHOLOGY_PHASE_LAW_DERIVATION_V1.md` (PL-1,
PL-2, PL-3b, PL-4b), `CANDIDATE_UNIVERSE_COVERAGE_CORRECTION_V1.md` (CU-2,
CU-3b), `MORPHOLOGY_SELECTION_THEOREM_V1.md` (MS-3).
Checker: `grand_gmi_structural_neural_bound_checks_v1.py`.

## 1. Gap addressed

Every parity-3 result so far is a **point verdict over registered
candidates**. The V5 and V6 assessments say so explicitly, and CU-3b proves
the harder half: without a coverage proof, such a verdict carries no
information about the residue, and **adding candidates can never upgrade it**,
because two extensions consistent with all registered evidence give opposite
verdicts.

So the candidate-expansion programme, however hostile, cannot reach a family
statement. What can is a derived lower bound over a structural class, because
PL-2 quantifies over a predicate rather than a list and therefore binds
members nobody has written.

This theorem supplies one, for one class, one task and one exact coordinate.

## 2. SN-1 — the registered class

Fix the task as exact parity on all eight three-bit inputs, and the coordinate
as `python_opcode_count_per_full_domain_sweep`, exactly as registered in the
V4 to V6 preregistrations: the validated straight-line opcode count per call,
times the eight inputs.

The structural predicate `sigma_NEURAL` admits a Python realization of the
single-hidden-layer integer-threshold form, in either of two registered code
shapes:

- **Shape A**, independent units. Each of `k` hidden units is written
  `h_i = int((<integer linear form over a, b, c>) >= t_i)`.
- **Shape B**, one shared form. A single line `s = <integer linear form>`
  followed by `k` units written `h_i = int(s >= t_i)`. This is how a competent
  implementer writes a network whose units share a weight vector, and it is
  strictly cheaper than shape A for that case, so omitting it would have
  inflated the bound.

The output is one line `return int((<integer linear form over h_0..h_{k-1}>) >= t)`.
Linear forms are rendered canonically and minimally: a zero coefficient omits
its term, a unit coefficient omits its multiply, and a subtraction is written
as a subtraction. Any other rendering of the same form costs at least as much,
so the canonical rendering is the right one for a lower bound.

This is a scope decision, not a discovery. By PL-4b, weakening the predicate
can only lower the bound; §7 states the residue.

## 3. SN-2 — the coefficient range is not binding

> **SN-2.** Enumerating hidden units over coefficients in `[-2,2]` and over the
> strictly wider range `[-4,4]` yields the **same set** of hidden behaviours,
> and the wider range never renders a behaviour more cheaply.

A hidden unit's behaviour is a linearly separable Boolean function of three
binary inputs, and there are finitely many of those. The enumeration finds
**104** distinct behaviours, which is the number of threshold functions on
three variables. Widening the coefficients adds none, and a coefficient of
magnitude above one costs two extra opcodes to render, so it cannot be
cheaper.

Hence the derived bound below is not an artifact of the coefficient bound: it
would be unchanged by admitting arbitrarily large integer weights.

## 4. SN-3 — the exhaustive minimum, and it is attained

> **SN-3.** Over the registered class, exact parity is **infeasible** with one
> or two hidden units and feasible from three. The minimum opcode count is
> attained, and the minimizing member computes parity.

Enumerated minima per call, by unit count, on CPython 3.12.3:

| `k` | minimum per call |
|---|---|
| 1 | infeasible |
| 2 | infeasible |
| 3 | **39** |
| 4 | 45 |

The `k = 1, 2` infeasibility is **derived here by enumeration**, not cited. It
is consistent with the classical single-hidden-layer threshold lower bound for
parity, which this work neither proves nor relies on.

The minimum is `39` per call, `312` per full domain sweep. A minimizer is

```
def f(x):
    a, b, c = x
    s = a - b - c
    h0 = int(s >= 1)
    h1 = int(s >= 0)
    h2 = int(s >= -1)
    return int((h0 - h1 + h2) >= 1)
```

The enumeration composes per-line costs, so the checker verifies that the
composed prediction equals the count of the actually compiled minimizer, and
that the minimizer computes parity on all eight inputs. Both hold.

## 5. SN-4 — the enumeration is complete over unit count

> **SN-4.** Every unit count of five or more is excluded by a cost floor, so
> enumerating to four is complete.

Each hidden unit contributes a strictly positive line cost, so a `k`-unit
member costs at least the function overhead plus `k` minimum unit lines plus
the cheapest possible output line. On CPython 3.12 that floor is `41` at
`k = 5`, already above the enumerated minimum `39`, and it only grows with
`k`. Together with SN-2 and SN-3, the bound therefore holds over **all** unit
counts and **all** integer coefficient magnitudes in this class.

## 6. SN-5 — the structural exclusion, and SN-6 — tightness

> **SN-5.** The registered non-neural XOR realization costs `88` per sweep
> against the derived class bound of `312`. By PL-2 the bound holds of every
> member of the class, so no member — written or unwritten — beats that
> witness.

| Interpreter | derived class bound | XOR witness | margin |
|---|---:|---:|---:|
| CPython 3.11.15 | 344 | 88 | 256 |
| CPython 3.12.3 | 312 | 88 | 224 |
| CPython 3.13.12 | 288 | 72 | 216 |

This is the first statement in this evidence line about machines nobody has
built. It is PL-2 supplying the bound and CU-2 transferring the verdict, on a
real instance rather than the synthetic grid of the derivation layer.

> **SN-6.** The registered `N_SUM_THRESHOLD3_V3` candidate **attains** the
> derived bound on every tested interpreter, so the bound is tight in the
> PL-3b sense.

Two consequences. First, PL-3b applies: with the class bound attained, the
comparison is about true optima rather than about the looseness of a
relaxation, so the exclusion is physical at this coordinate rather than
epistemic. Second, the candidate register was **not** understating the neural
family — no member of the enumerated class is cheaper than the candidate
already registered. The hostile expansion could not have done better here.

The optimum is not unique: the minimizer above differs from the registered
candidate and costs the same. By MS-3, only properties common to all
minimizers are derived, so nothing follows about a particular weight pattern.

## 7. Residue, stated as CU-3 requires

Closed within this class, not merely sampled:

- every unit count, by enumeration to four plus the SN-4 floor;
- every integer coefficient magnitude, by SN-2 saturation;
- both registered code shapes;
- every threshold placement, by exhaustive enumeration of separable
  behaviours.

Open, and not touched by anything above:

- **more than one hidden layer**;
- **activations other than an integer-threshold comparison**;
- **vectorized or array realizations**, whose opcode accounting differs;
- **realizations that precompute their outputs** — the structural predicate
  excludes these by definition rather than by discovery, and they are the
  lookup family, itself already measured as non-neural;
- **any substrate or language** other than the registered CPython opcode
  coordinate;
- **wall and process time**, which this derivation never uses. The CL-2 and
  CL-3 boundaries about observed windows are untouched because no window is
  involved.

Terminal: `GRAND_GMI_STRUCTURAL_NEURAL_BOUND_GREEN_AT_FINITE_SCOPE`.

## 8. What this changes, precisely

The parity-3 reading moves from

`ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE` over four registered
candidates

to a **class exclusion** for the single-hidden-layer integer-threshold class
at the registered exact coordinate, with an attained bound, plus the residue
above. The verdict for the physically legal set of parity-3 realizations
remains open, because the registered class is not a proved cover of it, and
CU-1 makes that a separate obligation.

No claim is made about neural realizations in general, about any other task,
about timing, or about any substrate other than CPython bytecode.

## 9. Parent mathematics and contribution boundary

The parent facts are elementary: monotonicity of a minimum under set
inclusion, exhaustive finite enumeration, and the finiteness of the set of
linearly separable Boolean functions on three inputs. The classical
single-hidden-layer threshold lower bound for parity is mentioned only as
context and is not used. No novelty is claimed for any of them. The
contribution is the construction of an enumerable structural class for this
registered instance, the saturation and cost-floor arguments that close its
unit-count and coefficient residues, the attained bound, and the resulting
class exclusion with its residue stated.
