# Z1 named results

Scope is fixed by `FREEZE_V1.md`: the declared union population of `297`
two-level instances (`eta in {1,2,3}` x `p in k/8` x {uniform binary, `7` input
laws, alphabets `A in {2,3,4}`}) and the `135` three-level ladder worlds of the
`L = 4` three-mode universe. Exact rational arithmetic throughout.

---

## `IC-1` — the Marginal Value Principle

For a finite candidate set with declared resource map `rho`, declared channel
errors `r_m`, declared weights `p_m`, declared error price `eta` and the additive
cost `C_lambda = eta*sum_m p_m*r_m + lambda*rho`, define
`E(k) = min { eta*sum_m p_m*r_m(x) : rho(x) = k }`. Then

1. a candidate minimises `C_lambda` for some `lambda >= 0` only if
   `(rho(x), E(rho(x)))` is a vertex of the lower convex envelope of `{(k, E(k))}`;
2. level `k` is the strict minimiser exactly on `(Delta_{k+1}, Delta_k)` with
   `Delta_k = E(k-1) - E(k)` taken along the envelope, and that interval is
   non-empty exactly when `k` is an envelope vertex;
3. **every selection threshold is a marginal error mass and never an error level.**

- quantifiers: for all instances of the declared population.
- assumptions: additive cost, linear resource price, finite candidate set, a
  declared accounting the instance supplies.
- falsifier: a registered selection threshold that is an error level and provably
  not a marginal. `Z13-P1`'s upper threshold is exactly such a candidate, and
  clause 3 is what convicts it.
- strongest parents: Lagrangian scalarisation and the lower convex envelope of
  the achievable rate-distortion set; see `PARENT_DISCLOSURE_V1.md`. **The
  mathematics is not novel.** What is established here is that the registered GMI
  selection laws are its corollaries, exactly, on enumerated finite universes.
- forbidden extrapolation: nothing is claimed for non-additive costs, non-linear
  resource prices, infinite candidate sets, or any real system.

## `IC-1a` .. `IC-1d` — the corollaries, all exact

| corollary | statement | evidence |
|---|---|---|
| `IC-1a` | `lambda* = eta*p/2` | the uniform binary stateless delayed floor is `1/2`, enumerated over `16` tables; `Delta_1 = eta*p/2` |
| `IC-1b` | `lambda*(A) = eta*p*(1 - 1/A)` | floors `1/2`, `2/3`, `3/4` enumerated over `16`, `729`, `65536` tables — the Z5 `CP-5` counts reproduced independently; `0` threshold violations over `3 x 3 x 9` instances |
| `IC-1c` | `lambda* = eta*p*R0` | `R0 = min(q, 1-q)` for all `7` declared input laws; `0` violations; reduces to `IC-1a` at `q = 1/2` |
| `IC-1d` | the three-level ladder | `135/135` worlds: level `1` occupies a non-empty niche **iff** it is an envelope vertex; `0` disagreements |

`IC-1a`-`IC-1c` all have `E(1) = 0`, so their marginal and their level coincide.
That coincidence is stated rather than hidden: it is precisely why clause 3 is not
idle, and why a level-valued threshold survived undetected until a three-level
ladder existed.

## `IC-2` — identification

Within the declared two-parameter law family `eta*p*(a + b*R0)`, `a, b in k/16`,
**exactly one** of the `289` laws reproduces the enumerated threshold on all `297`
instances: `(a, b) = (0, 1)`, which is `IC-1`. Within the ladder family
`eta*(a*p1 + b*p2)`, exactly one of the `289` reproduces the enumerated upper
endpoint on all `135` worlds: `(a, b) = (1/2, 3/16)`, which is `IC-1`'s marginal
pair. `Z13-P1`'s level-valued pair `(1/2, 5/16)` scores `27/135`.

- falsifier: a second law in either grid scoring perfectly.
- this is an identification statement over a declared family, **not** a claim that
  no law outside that family fits.

## `IC-3` — incompressibility, with exhibited witnesses

Call a law **MVP-compressible** iff its prediction is a function of the instance's
MVP content — its declared accounting and its profile `E(.)` — alone. Over the
declared population:

- **non-vacuity**: separations are scored on the `264` **non-degenerate**
  instances (`E(0) > E(1)`, per `FREEZE_V1_AMENDMENT_1`): `99` distinct profile
  groups, of which `75` contain more than one instance, `240` of the `264`
  instances live in a shared group, and the largest group holds `9`. Over the
  full `297`-instance population the counts are `102` groups and `78` shared.
  Envelope-invariance is a real constraint here, not a statement about an empty
  relation.
- **separated (not MVP-compressible), each with an exhibited witness pair**:
  `L_DEGENERACY` (how many candidates the instance's grammar holds),
  `L_MDL` (grammar-induced description length in bits),
  `L_REACH` (grammar-induced single-edit reachability),
  `L_DISTINCT` (whether the alphabet distinction is cost-relevant).
  Each splits at least one shared-profile group: two instances agreeing in
  declared accounting and in `E(.)` at every level, and disagreeing in the law.
  Worked witness for `L_MDL`: `(UNIF, eta = 2, p = 1, A = 2)` and
  `(ALPHA, eta = 2, p = 3/4, A = 3)` both have profile `E = (1, 0)` and both are
  assigned threshold `1` by `IC-1`, yet their grammars need `4` and `10` index
  bits respectively. The same pair separates `L_DEGENERACY` (`16` vs `729`),
  `L_REACH` (`1/4` vs `4/243`) and `L_DISTINCT` (`False` vs `True`).
- **no-alarm (MVP-compressible, as required)**: `L_THRESHOLD` and
  `L_ARGMIN_BUDGET` split `0` of the `75` shared groups. A separator that
  separated everything would be a broken instrument; this one is silent exactly
  where it should be.

**Why they cannot be compressed.** `E(.)` records, per resource level, a single
number: the minimum. It records neither how many candidates attain it, nor how the
grammar indexes them, nor how they sit in the grammar's edit neighbourhood. Every
separated law reads one of those three, so no function of `E(.)` can reproduce it.
The witnesses make that argument concrete rather than merely plausible.

- forbidden extrapolation: incompressibility is established for these four named
  laws over this population. It is **not** a general claim that grammar-level laws
  are never MVP-derivable.

## `IC-4` — compression and arbitrary constants

- raw pair for `IC-1`: `(567 independent predictions, 0 free theoretical degrees
  of freedom)`, under the declared cell rule of one cell per
  `(instance, adjacent-threshold-pair)`.
- raw pair for the bag-of-independent-laws baseline: `(567, 5)` across its `4`
  members; ratio `567/5`.
- every numeric constant in every registered closed form is classified:
  `1/2` in `eta*p/2`, `1 - 1/A`, and `R0` are all **computed values of `E(.)`** —
  enumerated, not chosen; `eta, p, lambda, q, A` are **environment-declared**.
  Exactly **one** constant in the corpus examined is classified
  `ARBITRARY_UNDER_IC-1`: the `5/16` level in `Z13-P1`'s upper threshold, which
  `IC-1` clause 3 forbids.

## `IC-5` — head to head

| theory | two-level population | ladder |
|---|---|---|
| `lambda* = eta*p/2` | `105/297` | — |
| `lambda*(A) = eta*p*(1 - 1/A)` | `153/297` | — |
| `lambda* = eta*p*R0` | `297/297` | — |
| `Z13-P1` two-price ladder | — | `27/135` |
| **`IC-1`** | `297/297` (tautological at two levels — the marginal *is* the level when `E(1) = 0`, and the cell is labelled as carrying no weight) | **`135/135`** |

The load-bearing comparison is the ladder, where level and marginal separate. One
principle with zero free constants covers both slices; the bag needs four members
and five constants and still fails on `135 - 27 = 108` ladder worlds.
