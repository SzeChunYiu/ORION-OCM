# Frozen registered scope: universe generator and input grid

**Status:** FROZEN before any executor, oracle, census or receipt exists. The
universe is produced by the deterministic rule below, not by a hand-authored
table, so per-mode non-emptiness is a discovered property of the census rather
than a design target.

## 1. Registered universe `Sigma_1`

### 1.1 Tasks and weights

```text
T   = (t_0, t_1, t_2)
mu  = (1/2, 1/3, 1/6)          exact Fractions, sum = 1
```

### 1.2 Realization index

```text
X = { x(a,b,c) : a in {0,...,7}, b in {0,1}, c in {0,1} },   |X| = 32
```

enumerated in ascending `(a, b, c)` order.

### 1.3 Deterministic attribute rules

```text
solve(x)    = { j in {0,1,2} : bit j of a is 1 }
pc(x)       = popcount(a)
k(x)        = (a + b) mod 3                 in K = {0,1,2}        (capacity level)
rho(x)      in N^14 : rho_0 = pc(x)+1, rho_1 = b+1, rho_2 = c+1,
                      rho_3 .. rho_13 = 0                          (#805 contract,
                                                                    3 active coords)
devcost(x)  = 2*pc(x) + k(x)                                       (development charge)
searchkey(x)= (rho_0(x), a, b, c)
s(x)        = 0-based rank of x in X sorted ascending by searchkey (cheap-first
              deterministic complete search trace, #877)
o(x)        = (k(x), b)   in O = K x {0,1},  |O| = 6               (observable signature)
```

### 1.4 Registered capability contracts `E`

Both share `(T, mu)` and the resource budget field supplied by `R`.

```text
E_full : verifier V accepts all three tasks.
         u(x, t_j) = 1 if j in solve(x) else 0
E_v0   : verifier V does not externally verify t_0 at this contract.
         u(x, t_0) = 0 always;  u(x, t_j) = 1 if j in solve(x) else 0, j = 1,2
cap_E(x) = sum_j mu_j * u(x, t_j)          exact Fraction
```

`max cap_{E_full} = 1`; `max cap_{E_v0} = 1/3 + 1/6 = 1/2`. `E_v0` instantiates the
CAP-3 information ceiling: the shortfall comes from the verification/observation
contract, not from computational weakness.

### 1.5 Contract-side resource verdict

```text
q_{E,R}(x) = cap_E(x)     if rho(x) <= b - m coordinatewise (all 14 coords)
           = UNSATISFIED  otherwise
```

`UNSATISFIED` is a distinct bottom; `UNSATISFIED >= tau` is false for every
registered `tau`, and `UNSATISFIED` is never coerced to `0`.

## 2. Frozen input grid (main census)

Query semantics REGISTERED on this grid. Axes enumerated in the stated order.

| axis | registered values | count |
|---|---|---|
| `M` = `K_M subset K` | all 8 subsets, enumerated by bitmask `0..7` | 8 |
| `R` = `(b, m)` | `b in { (2,1,1), (3,2,2), (9,3,3) }` (coords 0..2; coords 3..13 = 0) crossed with mandatory shared charge `m in { (0,0,0), (1,0,0) }`, budget-major | 6 |
| `D` = `B_dev` | `{2, 6, 99}`; `Reach(x)` iff `devcost(x) <= B_dev` | 3 |
| search budget `B` | `{0, 6, 12, 20, 32}`; `Seen(x)` iff `s(x) < B` | 5 |
| `H` = `o*` | `{ NO_OBSERVATION, (1,1), (2,0) }`; `Obs` = all of `X` for `NO_OBSERVATION`, else `{x : o(x) = o*}` | 3 |
| `U` | `U0 = FeasibleSet(X, X)`; `U1 = ConfidenceSet(X, {x : c(x)=0}, alpha=1/20)`; `U2 = ConfidenceSet(X, X, alpha=1/10)` | 3 |
| `E` | `{ E_full, E_v0 }` | 2 |
| `tau` | `{ 1/6, 1/2, 2/3, 1 }` | 4 |

Main census size: `8 * 6 * 3 * 5 * 3 * 3 * 2 * 4 = 51,840`.

## 3. Frozen registered relation failure budgets

The candidacy chain is a U-2A/U-2B relation chain `C_0 -> C_M -> C_D -> C_B -> C_H`.
Registered per-relation failure budgets:

```text
beta_M = 1/100,  beta_D = 1/200,  beta_B = 1/500,  beta_H = 1/50
sum beta = 37/1000
```

Composed coverage lower bound for a `ConfidenceSet` with source budget `alpha`:

```text
coverage_lower = max(0, 1 - alpha - sum beta)
U1 : 1 - 1/20 - 37/1000 = 913/1000
U2 : 1 - 1/10 - 37/1000 = 863/1000
```

A `FeasibleSet` emission carries **no** coverage field at all (U-1a has no
probability premise). The independence product
`(1-alpha) * prod_i (1-beta_i)` is computed only to be refused and reported as
strictly larger.

## 4. Frozen semantics-defect sub-census

Exhaustive over the declared defect sub-grid; every case must terminate
`CANNOT_CHECK` with the matching reason and mode `FM_CANNOT_CHECK`.

```text
defect in { QUERY_NOT_REGISTERED, QUERY_NOT_TOTAL_ON_DOMAIN }   2
K_M       all 8 subsets                                         8
H         3 registered values                                   3
U         3 registered values                                   3
size = 2 * 8 * 3 * 3 = 144
```

## 5. Frozen order-census sub-grid

Main grid restricted to `U = U0` and `E = E_full`:
`8 * 6 * 3 * 5 * 3 * 1 * 1 * 4 = 8,640` inputs, each re-attributed under all
`5! = 120` permutations of the cuts `(Expr, Res, Reach, Seen, Epis)`.

Note the order census permutes the cut **ladder** used for attribution only. The
predictor's survivor set `C` and its emission are order-invariant by construction
(intersection is commutative), which the census also checks.

## 6. Frozen null control

`NULL_MARGINAL`: emit, for every input, the most common `cap_E` value over the
registered universe under `E_full`, computed by the executor from the universe (not
hardcoded), with ties broken by the smallest value. Reported numbers: point
emissions and exact soundness violations for the null and for `F`, on the same
frozen grid.

## 7. Frozen replay commands

```bash
python3 -I -B  research/gmi-833-capability-predictor-v1/capability_predictor_v1.py
python3 -I -O -B research/gmi-833-capability-predictor-v1/capability_predictor_v1.py
python3 -I -B  research/gmi-833-capability-predictor-v1/oracle_route_b_v1.py
python3 -I -B  research/gmi-833-capability-predictor-v1/test_capability_predictor_v1.py -v
python3 -I -O -B research/gmi-833-capability-predictor-v1/test_capability_predictor_v1.py -v
```

Route B must not import route A; the test asserts this from route B's source text
and from `sys.modules`.
