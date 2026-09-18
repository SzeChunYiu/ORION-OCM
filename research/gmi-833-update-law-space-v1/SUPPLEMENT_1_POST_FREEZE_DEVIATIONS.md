# SUPPLEMENT 1 — post-freeze deviations, disclosed

`FREEZE_V1.md` section 8 requires that any correction to the freeze land as a
numbered supplement rather than an in-place rewrite. This is that supplement.
Five things in the shipped package differ from what the freeze pre-committed.
None is silent, and each is recorded with what changed, why, and whether it
postdates the result it touches.

The freeze itself has NOT been edited. Its text still says what it said at
commit `5c5c36e4`, and the git order still proves it predates every
implementation artifact.

---

## D1 — composition's quiet-step clause (POSTDATES THE OBSERVATION; disclosed)

**Frozen:** section 3.1 defined composition as running the second stage at
`(r1, ext(h,r1), b')` unconditionally, and claimed under IL-1.4 that
`(A_star, o)` has the zero-charge no-op as an identity.

**Shipped:** composition presents the second stage with `ext(h, r1)` EXCEPT
after a stage that consumed no resource and changed nothing, which does not
advance the history.

**Why, and the honest ordering.** The first run of the executor returned
`monoid_identity_ok = false`. Diagnosis: with an unconditional extension map the
no-op is a left identity only, because composing on the right still advances the
history. The clause that repairs it is derived from AX-3 — finite path cost is
coordinatewise addition, so a zero-charge step contributes nothing to the
developmental record and cannot register an interaction — and with it the monoid
is two-sided and unconditional, which is strictly stronger than the conditional
result the unmodified definition would have licensed.

**The deviation is that the clause was adopted AFTER seeing the result it
fixes.** That is the shape a post-hoc repair takes, and the corpus audit (#976)
treats that shape as suspect by default. Two things bound the exposure: the
derivation stands on an axiom that was already registered before this tranche
began, not on a new premise invented to fit; and the change is visible in the
git history rather than folded into the freeze. An auditor who rejects D1 is
left with the weaker but still true statement — left identity only — and nothing
else in the package moves, because no other result depends on the clause.

## D2 — the IL-2/IL-3 null statistic (SUPERSEDED; the frozen one was invalid)

**Frozen:** section 6 pre-committed "200 randomized IL-2/IL-3 controls whose
verdict is drawn from a permuted threshold: required agreement with the oracle
`0/200`."

**Shipped:** 200 draws in which a threshold taken from a DIFFERENT registered
path is asked to locate the exact tie of the target path; required hits `0/200`.

**Why.** The frozen statistic is not a valid null. Verdict agreement between a
shuffled threshold and the true one has substantial probability by chance — most
grid points are far from any tie, so both thresholds return the same strict
verdict and "agreement" is uninformative. Demanding `0/200` on it would have been
demanding something that ought not to happen even if the theory were correct.
The shipped statistic tests what the frozen one was reaching for — that the
crossover location is not recoverable from a mismatched threshold — and it does
have the property that `0/200` is the honest expectation under a true theory.
The true threshold is shown to locate the tie on `75/75` paths, so the control is
demonstrably able to fire.

This change postdates the freeze and was made because the frozen statistic was
wrong, not because it failed.

## D3 — the IL-4 graph family (SLOT PRE-REGISTERED; contents filled after)

**Frozen:** section 3.3 listed "source-chain, deep-chain, fan-in, fan-out,
square (equal sources and outputs), and a bridge graph chosen so that a mixed
order is a live possibility", and forbade "post-hoc redefinition of the order
space, the cost model or the graph family after seeing the census".

**Shipped:** the chains and the fan-in were enlarged (more eliminable interior
vertices, so the census is over 6 to 120 orders rather than 2), and a seventh
graph `skip_waist_n2_p2` was added after the first census.

**Why.** `bridge_n3_p3` was built to fill the frozen slot for "a graph where a
mixed order is a live possibility". It turned out symmetric: both pure orders
cost exactly 12 and no mixed order beats them, so the slot went unfilled and the
pre-committed boundary could not have been either confirmed or refuted.
`skip_waist_n2_p2` — a skip edge across a narrow waist — fills it, and does so in
the direction the freeze anticipated.

**What did NOT change, which is the part that matters.** The order space is the
same (all interior-vertex elimination orders), the cost model is the same
(`indeg x outdeg` per elimination, `sweep_price`, `retention_price`, `w` from the
declared storage schedule), the reporting rule is the same (report the argmin
whatever it is), and every formula — `sigma_star`, `rho_star`, the trichotomy,
the sweep-count necessity argument — was tested unmodified against the enlarged
family. No number was tuned. `bridge_n3_p3` is retained in the shipped family
rather than dropped, precisely so that the graph that failed to fill its slot is
visible in the receipt.

An auditor is entitled to treat `skip_waist_n2_p2` as a demonstration rather
than a prediction, and the theorem note should be read that way: the mixed-order
finding confirms a regime that Naumann (2008) already proved exists. Its role
here is to stop this package from claiming the reverse order is globally
optimal, and it discharges that role whether or not it was registered first.

## D4 — the screen's exemption structure (STRICTLY TIGHTENED)

**Frozen:** section 3.1 pre-committed the A1 screen "over every identifier in
the definition module" with "the declared exemption (`PARENT_OWNERSHIP` prose
file only)".

**Shipped:** the exemption list grew from one file to seven whole-file
exemptions during development, and was then replaced entirely by an
occurrence-level allowlist. Two files are now skipped whole — the denylist and
the hostile fixtures, both of which hold the screened vocabulary by
construction. Every other file, including the theorem note and the
parent-ownership file, is screened in full; each legitimate hit is declared as a
specific `(file, denylist entry)` pair with a reason; an unmatched hit fails and
so does an allowance that is never exercised. The routes, the test, `CORE.md`
and both receipts are declared absolutely clean and may carry no allowance at
all.

The intermediate seven-file state was weaker than the freeze in spirit, since it
would have let the theorem note — the document most able to hide a name — go
unscreened. The shipped state is stronger than the freeze: the freeze exempted
one whole file, the package now exempts two whole files that cannot be
meaningfully screened at all and screens everything else down to the individual
occurrence.

## D5 — the reading of `w` (CLARIFICATION, forced by the frozen formula)

**Frozen:** `sigma_star = (n - p) * E / (N - w)` with `w` described as "the peak
live-set size of the primal evaluation".

**Shipped:** `w` counts only INTERNAL live values, and a value is live from its
production step to its last consumption step INCLUSIVE, with designated outputs
live to the end.

**Why.** Counting source values in `w` can make `N - w` negative and the frozen
formula ill-defined. Source values are retained identically by both accumulation
directions, so excluding them from both sides of the comparison is the reading
that makes the frozen expression well posed, and it changes no comparison. The
inclusive live range is the physically correct one: to compute a node its parents
must still be resident at that step. Both routes implement this definition
independently — Route A by a last-use table, Route B by a per-prefix live count —
and agree on `w` for all seven graphs.

---

## What did not deviate

The four target rows, `source_main`, the claim ceiling, the parent-ownership
list, the forbidden promotions, the admissibility clauses A1-A4 including the
worst-case budget clause, the closed forms `rho_local = (d+1)/(m+1)` and
`sigma_star = (n-p)E/(N-w)`, the IL-2/IL-3 price and ecology grid, the
two-route requirement, all fourteen hostiles and the second null control are
shipped exactly as frozen.

---

## D1 sensitivity receipt — added on review, measured not asserted

The D1 entry above states that an auditor who rejects the quiet-step clause is
left with "left identity only" and that "nothing else in the package moves".
That was an inspection claim. It has since been **measured**.

**Method.** The executor was re-run on laptop-billy with the clause forced off —
the single line `quiet = is_noop(d1, c1, r, coords)` replaced by `quiet = False`
— and every leaf field of the resulting `RESULT_V1.json` was diffed against the
shipped run.

**Result.**

| | |
| --- | --- |
| certificate leaf fields compared | 774 |
| fields that change when D1 is disabled | **1** |
| the changed field | `/IL_1/monoid_identity_ok`, `true` → `false` |
| stdout summary diff | 0 lines |

The 686/686 mixture census, the 49/49 composition-closure census, the
3,450-case IL-2/IL-3 grid and every IL-4 field are **invariant** to the clause.
The composition operator itself is modified by D1, so closure was the field most
at risk of moving with it; it does not move.

**Reading.** The exposure created by the post-hoc adoption is exactly one
boolean. An auditor who rejects D1 strikes `monoid_identity_ok` and the
two-sided half of IL-1.4, and nothing else in the package changes value. The
IL-1 row in #833 now carries this disclosure inline rather than only here.
