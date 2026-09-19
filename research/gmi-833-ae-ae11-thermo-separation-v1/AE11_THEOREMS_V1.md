# AE11 named results

Every result below is stated at the registered finite scope of `FREEZE_V1.md`.
All quantities are exact `Fraction`s or `int`s; no float appears in any claim,
and no energy value is computed anywhere in the package. Route A is
`ae11_thermo_separation_v1.py`, route B is `independent_thermo_oracle_v1.py`,
and the two agree on every value.

## Definition D-AE11a (the four registered quantities)

On a registered composite object `o = (P, x, M, (Q, T))`:

- `H_shannon(o) = H(P)` in bits, where every mass of `P` is an integer power of
  `1/2`, so `H` is an exact rational.
- `K_U(o) = K_U(x)`, the length in bits of a shortest program for the registered
  string `x` on the frozen prefix-free machine `U`, searched exhaustively to the
  frozen cap `LCAP = 14`; an exact integer, or the registered symbol `>LCAP`.
- `S_stat(o)` is carried as the **integer** microstate count `W = |M|` together
  with the exact statement `S_stat = k_B ln W`. Comparisons between macrostates
  are integer comparisons of `W`; no transcendental value is evaluated.
- `S_thermo(o) = Q / T`, an exact rational in the registered units.

## Definition D-AE11b (erased bits, devices, and the registered protocol class)

For a map `f : D -> D` on the registered 4-state logical register,
`m(f) = log2|D| - log2|image(f)|`, an exact integer when both counts are powers
of two. `W_min(f) = m(f) * k_B T ln 2`. A device model is a registered sequence
of primitive logical operations whose composition equals `f`; its registered
cost is the **integer operation count**, never an energy. `R_PROTO` is the class
of protocols that act only on `D` and reset it with the registered reset
primitive. A **registered physical system** is the tuple
`(boundary, dynamics, reservoir, temperature)`; this package registers zero of
them.

---

## AE11-1 — the four notions are pairwise non-functionally dependent

**Scope.** The 8 registered composite objects of `FREEZE_V1.md`, the four
quantities of D-AE11a, the frozen machine `U` at `LCAP = 14`.
**Quantifiers.** All 12 ordered pairs `(A, B)` with `A != B`; existential in the
witness objects.

For each ordered pair `(A, B)` the roster contains two objects `x, y` with
`A(x) = A(y)` and `B(x) != B(y)`, which is exactly the statement that `B` is not
a function of `A`. All **12** pairs are witnessed and **0** are unwitnessed.

Two of the witnesses are classified `derived`: `H_shannon` and `S_stat` are
linked by the registered definitional relation `H_shannon <= log2 W`, because
`W` is the size of the support of `P`, and those two witnesses exhibit the slack
in it — `R_SKEW_DYADIC` and `R_MACRO_A` share `W = 4` with `H_shannon` `7/4`
against `2`, and `R_MACRO_A` and `R_MACRO_B` share `H_shannon = 2` with `W` `4`
against `5`. The other **10** witnesses are classified
`registered_independent`: those pairs have no registered definitional relation
at all, and fixing one quantity leaves the other free. That `S_thermo` is
registered separately is the physics rather than an artifact of how the roster
was assembled: thermodynamic entropy change is a property of a physical process
and is not determined by any informational description of a state, so a coupling
between `Q/T` and the other three would have to be imported, not derived. The
six `S_thermo` cells record exactly that.

**Assumptions.** The registered dyadic masses; the frozen machine and cap; the
canonical coupling `W = |supp(P)|`; the registered `(Q, T)` pairs; exact
rational arithmetic throughout.
**Dependencies.** D-AE11a; the exact `K_U` table of AE11-2; the Shannon
entropy computed twice, by exponent algebra in route A and by integer code-tree
accumulation in route B.
**Falsifiers.** Any ordered pair for which no two roster objects tie in the
fixed quantity while differing in the free one — reported as unwitnessed, and
that pair then contributes nothing to closure. A tie produced by a float
comparison rather than exact equality. A disagreement between the two routes on
any roster value.
**Strongest parents.** Shannon (1948) for `H`; Kolmogorov (1965) and Chaitin
(1966) for `K`, with Li and Vitanyi (2019) for machine-relativity; Jaynes (1957)
for the Gibbs reading of statistical-mechanical entropy; Clausius for `Q/T`.
That these notions are distinct is entirely parent-owned; the residual here is
the single finite roster on which all four are evaluated together and the
machine-checked pairwise table.

**Forbidden extrapolation.** Nothing here says the four quantities are unrelated
in general. `H_shannon <= log2 W` is a genuine relation and is recorded as such.
The claim is non-functional-dependence on the registered roster, not
independence in any probabilistic sense.

---

## AE11-2 — maximal Shannon entropy does not fix algorithmic complexity

**Scope.** The uniform distribution on all `2**6` registered strings, and the
frozen machine `U` at `LCAP = 14`.
**Quantifiers.** Universal over the 64 members of the support; the histogram is
exhaustive.

`R_UNIFORM_BLOCK` has `H_shannon = 6` bits exactly, the maximum available on the
64-string alphabet. Its members carry `K_U` values `11` (2 strings, `000000` and
`111111`), `13` (6 strings) and `14` (56 strings): **three** distinct values.
`R_UNIFORM_BLOCK` and `R_PROCESS_B` share that same maximal `H_shannon = 6`
while their registered strings carry `K_U = 11` and `K_U = 14`.

The instruction codewords form a complete prefix code with Kraft sum exactly
`1`; the program set is prefix-free with Kraft sum exactly `67/128` up to the
cap; **0** of the 64 strings saturate `LCAP`, so the cap is not binding on the
roster.

**Assumptions.** The frozen instruction set and its frozen integer code lengths;
`LCAP = 14`; the output-length ceiling `MAXOUT = 24`; a program is a bit string
that decodes to complete codewords ending in `HALT` with nothing left over.
**Dependencies.** The two independent searches of the program space — bit-string
order with decoding in route A, instruction-sequence order without a decoder in
route B — which agree on all 64 entries and on the `67/128` Kraft sum.
**Falsifiers.** Any string whose two routes disagree; a Kraft sum above `1`; a
registered string with no program at or below the cap; a histogram with a single
`K_U` value, which would make `K_U` constant on the support and destroy the
witness.
**Strongest parents.** Kolmogorov (1965), Chaitin (1966), Solomonoff; Li and
Vitanyi (2019) for the invariance theorem and for the fact that `K` is defined
only up to an additive machine-dependent constant. The counting argument that
most strings are incompressible is parent-owned.

**Forbidden extrapolation.** The numbers `11`, `13`, `14` are values on **this**
machine at **this** cap. They carry no asymptotic content, and the width of the
spread is not a machine-independent quantity. `FREEZE_V1.md` phrases this
witness as `K_U` ranging from a small constant to `m` bits; at string length `6`
with a five-instruction prefix-free set the emit cost pins the ceiling at `14`
and the floor cannot be small, so that numeric phrasing is not attainable and is
not claimed. The receipt carries the discrepancy as an explicit caveat on
`AE11-P1`.

---

## AE11-3 — every resource this tranche names is classified, and no physical one is instantiated

**Scope.** The resources named anywhere in this Section AE tranche.
**Quantifiers.** Universal over the 24 registry rows.

The registry classifies **24** resources into the two registered classes: **12**
`LOGICAL_COMPUTATIONAL` (program-length bits, Shannon entropy bits, microstate
counts, erased-bit counts, device operation counts, and so on) and **12**
`PHYSICAL_ENERGETIC` (joules, watts, kelvin, `k_B`, `k_B T ln 2` as an energy,
metabolic rate, entropy-production rate, and the rest). The executor asserts
that the number of `PHYSICAL_ENERGETIC` resources **instantiated** is exactly
`0`, that **0** rows carry a numeric value in physical units, and that the
receipt contains **no float at all**. The row closes on those verified
properties, not on prose.

`S_thermo = Q / T` is computed, and it is classified `PHYSICAL_ENERGETIC` and
**not instantiated**, because `Q` and `T` are registered symbols with no
physical magnitude: the ratio is exact in registered units and no value in J/K
is produced.

**Assumptions.** That the registry is complete for this tranche — an
over-inclusive list can only make the assertion harder to satisfy, never easier;
that "instantiated" means the package assigns a numeric value in physical units.
**Dependencies.** The float scan over the serialized receipt; the route-B
recount of instantiated physical rows.
**Falsifiers.** Any resource this tranche uses that appears in neither class;
any row with `instantiated: true` in the physical class; any float reaching the
receipt; any claim in the package that states a joule, watt or kelvin value.
**Strongest parents.** Landauer (1961) and Bennett (1982) for the distinction
between the logical and the physical description of a computation; Strubell et
al. (2019) and Henderson et al. (2020) for the measurement methodology this
package explicitly does **not** perform.

---

## AE11-4 — the Landauer bound, audited with its assumptions

**Scope.** The 4 registered maps on the 4-state register, the registered
protocol class `R_PROTO`, and units of `k_B T ln 2`.
**Quantifiers.** Universal over the registered maps; the assumption table is
exhaustive over the four registered assumptions.

Each map carries a lower-bound record on the dissipation of a protocol in
`R_PROTO`, with bound value the exact integer `m`: `0` for `F_BIJECTION`, `1`
for `F_AND`, `1` for `F_ERASE1`, `2` for `F_ERASE2`. The definitional range is
`[0, log2|D|] = [0, 2]`, both endpoints derived from the definition of `R_PROTO`
and of the register and from no observed value. Each record carries an
`attained_by` quasi-static witness, and each record with `m > 0` carries a
`violated_by` witness from the explicitly relaxed class in which the
no-residual-correlation assumption is dropped: conditioned on a registered
ancilla the register has exactly `1` possible state, the relative erased-bit
count is the integer `0`, and the relaxed protocol attains `0`, strictly below
the bound.

`B_LANDAUER__F_BIJECTION` has bound value `0` against a definitional floor of
`0`. It is flagged **vacuous** and `UNFALSIFIED_BOUND` and closes nothing; a
non-negative quantity cannot fall below zero. Across the whole package **16**
bound records are emitted, **4** are vacuous and unfalsified, and **12** carry a
violator.

The four assumptions are listed and each is paired with a registered violation:
single-temperature equilibrium against `RELAXED_TWO_RESERVOIR`; quasi-static
operation against `RELAXED_FINITE_TIME`; no residual correlation against
`RELAXED_CORRELATED_RESET`; logical irreversibility against `F_BIJECTION`. The
finite-time relaxation is recorded as breaking **attainment** and not the lower
bound — a finite-time protocol dissipates strictly more — rather than being
dressed up as a violation it is not.

**Assumptions.** Thermal equilibrium of the reservoir at a single temperature
`T`; quasi-static operation; no residual correlation between the register and
the environment; logical irreversibility of the map. Every one of these is a
condition on the physical statement, and this package asserts none of them of
any real device, because it registers no device.
**Dependencies.** D-AE11b; the erased-bit counts of AE11-5, computed by forward
image in route A and by preimage partition in route B.
**Falsifiers.** A registered map whose erased-bit count differs between the two
routes; a bound record whose vacuity flag disagrees with its definitional range;
a non-vacuous record with no violator; a claimed violator whose attained value
is not strictly below the bound value.
**Strongest parents.** Landauer (1961) owns the bound; Bennett (1973, 1982) owns
logically reversible computation and the demon analysis; Berut et al. (2012) own
the experimental verification, which this package does not repeat and does not
need; Szilard (1929), Sagawa and Ueda (2009) and Parrondo, Horowitz and Sagawa
(2015) own the conditional, correlation-aware form of the bound that the
`RELAXED_CORRELATED_RESET` witness instantiates.

**Forbidden extrapolation.** Nothing here measures or estimates any energy. The
bound is on the dissipation of a protocol in a registered abstract class, in
units of `k_B T ln 2`, with the unit never given a magnitude.

---

## AE11-5 — the erasure bound does not determine total cost

**Scope.** The 4 registered maps and the 2 registered device models.
**Quantifiers.** Universal over the 8 map-and-device instances.

For **every** registered map the two device models compute the same map, carry
the **same** exact integer erased-bit count, and carry registered operation
counts differing by exactly **5** — `DEV_HIGH_OVERHEAD` prefixes a registered
five-operation preamble every member of which is a bijection of the register, so
it changes the net map not at all and the erased-bit count not at all. For
`F_ERASE2` the erased-bit count is `2` under both while the counts are `2` and
`7`. Two implementations with identical `m` therefore have different registered
cost, so `m` provably fails to determine even the logical implementation cost,
let alone a physical energy.

Erased-bit counts and operation counts are kept as separate integers and are
never summed: an erased-bit count and an operation count are different
quantities, and adding them would be the very conflation this row forbids.

**Assumptions.** The registered primitive operation set and the registered
minimal op sequence per map; that a device's registered cost is its integer
operation count and nothing else.
**Dependencies.** The composition check that each device's op sequence really
computes its map, run independently in route A on 2-character strings and in
route B on integer register states under bitwise operations.
**Falsifiers.** A device whose composition does not equal its registered map; a
pair of devices for one map with different erased-bit counts, which would mean
the preamble is not a bijection; an operation-count gap other than 5.
**Strongest parents.** Bennett (1973) owns the fact that computation can be made
logically reversible and that the erasure cost attaches to the erasure step
alone; Landauer (1961) owns the bound that is here shown not to determine the
total.

**Forbidden extrapolation.** This is a statement about registered operation
counts. It says nothing about the energy of any real device, and in particular
it does not license `INFORMATION_SAVINGS_IMPLY_ENERGY_SAVINGS` in either
direction — it is the formal reason a matched hardware experiment is required.

---

## AE11-6 — no physical system is registered, and no claim carries a driven-system term

**Scope.** The registered claims of this package and the registered roster.
**Quantifiers.** Universal over the 7 registered claims and the 10 frozen terms.

A registered physical system is the tuple
`(boundary, dynamics, reservoir, temperature)`. The registered quasi-static
processes supply a temperature symbol and nothing else, so the count of
registered physical systems is exactly `0` — the zero is literal under the
freeze's own definition, not a semantic dodge. The frozen 10-term
driven-system vocabulary scores **0** hits over the 7 registered claims, which
is the no-alarm case on the known-clean roster, and the detector is validated in
the other direction by the planted fixture `FIXTURE_NONEQ_PLANT`, which it flags
on **3** terms. Each frozen term is separately shown to be detectable on a probe
string, so the silence on the clean roster is silence and not blindness.

**Assumptions.** The frozen term list; that the scanned population is the
registered claim sentences, which is the population in which a modelling
commitment would appear.
**Dependencies.** AE11-3's registry, which declares the driven-system resources
without instantiating them.
**Falsifiers.** A registered claim containing a frozen term; a frozen term the
detector cannot find in a probe; any registered object supplying all four
components of a physical system.
**Strongest parents.** Prigogine and the driven-systems literature own the
modelling of maintained states away from equilibrium; England's and the
free-energy-principle literatures own the biological readings. None of them is
used here, and none is extended: this result is a refusal with a checked
receipt, not a contribution to that literature.

---

## AE11-7 — logical irreversibility and dissipation, at the correct scope

**Scope.** The registered maps, their device models, and the registered uniform
input.
**Quantifiers.** Existential in the witness pair; universal in the certified
inequality over the registered maps.

`F_BIJECTION` has erased-bit count exactly `0` and Landauer lower bound exactly
`0`, while its registered device runs `1` operation — strictly positive. The
many-to-one `F_ERASE2` has erased-bit count exactly `2`. That pair is the exact
statement of the correct scope: logical irreversibility lower-bounds the
dissipation **attributable to erasure** under the registered assumptions and
nothing more; it does not bound, and is not bounded by, the cost of running the
implementation.

The scope has a second edge. The count-based `m` is a **lower bound** on the
distributional drop `H(P) - H(f_*P)` under the registered uniform input, and for
`F_AND` the inequality is strict: the drop is `(3/4) log2 3`, which is not
rational, is reported as `NOT_DECIDED` rather than as a decimal, and is
bracketed in `(19/16, 6/5)` by the integer comparisons `3**12 >= 2**19` and
`3**5 <= 2**8`. Since `19/16 > 1 = m(F_AND)`, the count-based erased-bit number
strictly understates the distributional irreversibility of `F_AND`, and the
weaker of the two is the one the Landauer record carries. `F_AND`'s largest
preimage class has size `3`, not a power of two, so the `log2`-of-largest-
preimage reading is reported as `NOT_A_POWER_OF_TWO` rather than rounded.

**Assumptions.** The registered uniform input on `D`; the registered device op
sequences; the two `log2(3)` certificates, each an integer comparison.
**Dependencies.** AE11-4 for the bound records, AE11-5 for the operation counts;
both routes' erased-bit counts and push-forward entropies.
**Falsifiers.** A bijection with a non-zero erased-bit count; a registered
device for `F_BIJECTION` with operation count `0`; a rational value claimed for
`(3/4) log2 3`; a certificate whose integer comparison fails.
**Strongest parents.** Landauer (1961) and Bennett (1973) own the scope
statement itself; Sagawa and Ueda (2009) and Parrondo, Horowitz and Sagawa
(2015) own the modern conditional form; Shannon (1948) owns the entropy drop.

**Forbidden extrapolation.** "Physical dissipation" appears here only as the
bounded quantity of a registered abstract protocol class. No physical
dissipation is measured, modelled on real hardware, or inferred; the comparison
is between two exactly computed integers and one certified rational bracket.
