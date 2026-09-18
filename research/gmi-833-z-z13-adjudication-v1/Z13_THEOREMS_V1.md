# Z13 named results

All results are stated at the scope fixed by `FREEZE_V1.md` §1 and
`FREEZE_V1_AMENDMENT_1.md`: the three-mode extension of the registered binary
transducer universe, `L = 4`, uniform independent inputs, canonical initial state
`0`, state budget `b in {0, 1, 2}`, mode-indexed output and next-state tables,
scored window `t in {2, 3}` (`32` scored moments per mode), exact rational cost
`C = eta*(p0*r_now + p1*r_delay1 + p2*r_delay2) + lambda*b`.

Nothing below is claimed beyond that scope. `L != 4`, `b > 2`, non-uniform input
laws, alphabets larger than `2` and any real or trained system are all outside it.

---

## `ZA-1` — the exact one-bit floors

At `b = 1`, exhaustively over all `(output table, next-state)` pairs per mode:

```
R0(now | b=0) = 0        R0(delay1 | b=0) = 1/2     R0(delay2 | b=0) = 1/2
R0(now | b=1) = 0        R0(delay1 | b=1) = 0       R0(delay2 | b=1) = 5/16
R0(now | b=2) = 0        R0(delay1 | b=2) = 0       R0(delay2 | b=2) = 0
```

`5/16 = 10/32` is attained by exactly `4` next-state functions, none of which is
`next(st, cur) = cur`; under `next(st, cur) = cur` the delay-2 channel sits at
`1/2`.

- quantifiers: for all candidates in the declared universe at the declared budget.
- assumptions: uniform i.i.d. inputs; scored window `{2, 3}`; canonical initial state.
- falsifier: any candidate at `b = 1` with delay-2 error rate `< 5/16`.
- strongest parents: exhaustive finite-state minimisation; the Z6 stateless floor `R0`.
- forbidden extrapolation: these are not floors at any other `L`, window or input law.

## `ZA-2` — thresholds are marginals, and `Z13-P1`'s upper threshold is a level

On the declared grid of `135` worlds (`eta in {1,2,3}`, `(p0,p1,p2)` over eighths):

- the frozen lower threshold `lambda_2* = eta*p2*R0(delay2|b=1)` is the observed
  lower endpoint in **`135` of `135`** worlds;
- the frozen upper threshold
  `lambda_1* = eta*p2*R0(delay2|b=1) + eta*p1*R0(delay1|b=0)` is the observed
  upper endpoint in **`27` of `135`** worlds — exactly the `p2 = 0` slice;
- the observed upper endpoint is
  `eta*(p1*[R0(d1|b=0) - R0(d1|b=1)] + p2*[R0(d2|b=0) - R0(d2|b=1)])
   = eta*(p1/2 + 3*p2/16)`, a **marginal** error mass;
- the frozen form exceeds it by exactly `eta*p2/8` in every world with `p2 > 0`.
  First witness: `eta = 1`, `p = (0, 0, 1)`, frozen `5/16`, true `3/16`.

The defect is structural, not numerical: `Z13-P1` priced the second resource unit
with the delay-2 **level** `R0(delay2|b=1)` where the ladder requires the
**difference** `R0(delay2|b=0) - R0(delay2|b=1)`. The two coincide only when the
higher level attains zero error, which is why `lambda* = eta*p*R0` is right at
two levels and wrong at three.

- falsifier: any world on the declared grid where the marginal form misses the
  observed endpoint. `0` such worlds were found; the null (below) found none either.

## `ZA-3` — the frozen property bundle is unsatisfiable

`P-b` (next-state is the current input) and `P-c` (`r_now = r_delay1 = 0` and
`r_delay2` at the one-bit floor) cannot both hold of any candidate at `b = 1`:

- the `2` next-state functions attaining `r_delay1 = 0` and the `4` attaining
  `r_delay2 = 5/16` are disjoint sets;
- `next = cur` is in the first and not the second.

The same holds under the pre-registered shared-next-state sensitivity reading:
the argmin set there contains `next = cur` with errors `(0, 0, 16)` and a second
machine with `(0, 6, 10)`, and no member has both `r_delay1 = 0` and
`r_delay2 = 10/32`. The refutation is therefore **convention-independent**.

Consequently `P-d` is `VACUOUSLY_TRUE`: it quantifies over an empty set. Under
`FREEZE_V1` §3 `H-4` a vacuous property test is not evidence.

## `ZA-4` — `Z13-P1`'s HIT condition is logically unsatisfiable

Under the registered family lift (`FREEZE_V1_AMENDMENT_1`), `P-b/all` holds of a
candidate **iff** that candidate is in `F_IDENTITY_STATE`. `Z13-P1` requires both
that the niche minimiser satisfy `P-a, P-b, P-c` (`H-3`) and that no named-family
member satisfying `P-a, P-b, P-c` be a unique minimiser in the niche (`P-d`,
`H-4`). Any witness for `H-3` is by definition a named-family member and refutes
`P-d`. `H-3 and H-4` is unsatisfiable by logic alone, before any enumeration.

- assumption: the entry-for-entry lift of Z6's `nxt = 0b10101010`.
- falsifier: a lift of `F_IDENTITY_STATE` that is faithful to Z6 and does not
  coincide with `P-b/all`.

## `ZA-5` — the frozen negative ecology is misidentified

`Z13-P1` says that at `p2 = 0` the interval collapses. The exact niche width is

```
width = eta * ( p1*(R0(d1|b=0) - 2*R0(d1|b=1) + R0(d1|b=2))
              + p2*(R0(d2|b=0) - 2*R0(d2|b=1) + R0(d2|b=2)) )
      = eta * ( p1/2 - p2/8 ),
```

the second difference of the profile. At `p2 = 0` the width is `eta*p1/2`, its
**largest** value at fixed `p1`: `24` of the `27` `p2 = 0` worlds have a strictly
non-empty niche, and the `3` that collapse are exactly the `p1 = 0` ones. The
ecology in which the intermediate morphology genuinely loses its advantage is

```
4*p1 <= p2
```

— the condition under which level `1` leaves the lower convex envelope. This
repaired ecology was derived **after** the frozen one failed and is therefore not
prospectively confirmed by this package; it is frozen for a later lane in
`REPAIRED_ECOLOGY_FREEZE_V1.md`.

## `ZA-6` — what the search actually recovers, and what it is

At `b = 1` the cost-minimising morphologies number `248` (`31` x `2` x `4`
configurations across the three modes). Every one of them:

- attains `r_now = 0`, `r_delay1 = 0`, `r_delay2 = 5/16` (`P-c` holds);
- satisfies `P-a` (its immediate-copy channel reads both state and input);
- uses `next = cur` on the delay-1 channel and a **copy-then-reset** next-state
  function on the delay-2 channel — `next(0, cur) = cur`, `next(1, cur) = 0`
  (or the state-relabelled twin) — so `P-b` fails;
- is a member of `F_MEALY_PURE` and of **no other** registered named family; in
  particular it is **not** in `F_IDENTITY_STATE`.

The separation from `F_IDENTITY_STATE` is a resource quantity, not a syntactic
label: at the same budget `b = 1` the whole of `F_IDENTITY_STATE` is pinned at
delay-2 error `1/2` while the recovered class attains `5/16`. That gap is
invariant under every remint checked (state relabelling with the initial state
carried, input-symbol relabelling applied to machine and task together) and is
moved by a non-remint control (`6` of `14` scrambles change the number).

- forbidden extrapolation: `F_MEALY_PURE` membership means the recovered class is
  a Mealy machine. **No new architecture family is claimed.**

## `ZA-7` — the verdict

`Z13-P1` is a **MISS**. `H-1` holds; `H-2`, `H-3`, `H-4` and `H-5` fail. The
miss is published in `FAILED_PREDICTION_REGISTER_V1.json` with the exact retired
text. No W4 or new-domain status is claimed, and none is claimable: a repository
and issue-wide search (issue body, all `33` issue comments, `git grep -w W4` over
every `.md`, `.json` and `.py`) finds **no registered W4 criteria** anywhere on
`main` — the only `W4` tokens are `fna3`'s unrelated language-world ladder and
`rev-l47`'s "W4 pattern" for prospective re-establishment.
