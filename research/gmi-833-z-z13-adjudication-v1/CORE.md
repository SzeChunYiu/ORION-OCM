# GMI #833 Section Z / Z13 — adjudication of the frozen prediction `Z13-P1`

Closes **nine** of the twelve rows of `### Z13` in issue comment `5684819296`:
rows `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8` and `12`.

Rows `9`, `10` and `11` are left open by `FREEZE_V1.md` §5 and may not be touched
by this package: this lane adjudicates the frozen niche and the frozen negative
ecology, so it cannot also be the lane that demonstrates them, and independent
replication is not self-suppliable. All six `### Z16` rows are likewise out of
scope.

## The verdict

`Z13-P1` is a **MISS**. It was frozen by a different lane on `2026-09-18`
(blob `25febfa6`, commit `0cc617fc`), explicitly for a later lane to score, and
this is that lane.

| frozen claim | verdict | number |
|---|---|---|
| lower threshold `lambda_2* = eta*p2*R0(d2\|b=1)` | CONFIRMED | `135/135` worlds |
| upper threshold `lambda_1* = eta*p2*R0(d2\|b=1) + eta*p1*R0(d1\|b=0)` | **REFUTED** | `27/135`; excess exactly `eta*p2/8` |
| property bundle `P-b and P-c` | **REFUTED** | unsatisfiable under both next-state readings |
| `P-d` | `VACUOUSLY_TRUE` | empty quantification domain |
| HIT condition `H-3 and H-4` | **REFUTED BY LOGIC** | `P-b/all` *is* `F_IDENTITY_STATE` |
| matched negative ecology at `p2 = 0` | **REFUTED** | `24/27` worlds keep a non-empty niche |

The repair — a threshold is a **marginal** error mass, never a level, and the
niche is empty exactly on `4*p1 <= p2` — is derived after the fact, is **not**
prospectively confirmed here, and is frozen for a later lane in
`REPAIRED_ECOLOGY_FREEZE_V1.md`.

## Headline numbers

- one-bit floors: `R0(d1|b=0) = 1/2`, `R0(d1|b=1) = 0`, `R0(d2|b=0) = 1/2`,
  `R0(d2|b=1) = 5/16`, all three channels `0` at `b = 2`;
- universe sizes, exact: `64` at `b = 0`, `16777216` at `b = 1`,
  `2**72 = 4722366482869645213696` at `b = 2` (counted, not enumerated — see
  `FREEZE_V1.md` §1a);
- `248` cost-minimising architectures at `b = 1`, all in `F_MEALY_PURE` and in no
  other registered named family, all using a **copy-then-reset** next-state
  function on the delay-2 channel;
- null: `200` seeded two-parameter threshold laws, best `27/135`, `0` perfect;
  the marginal law `135/135`;
- `8` hostiles, all of which move the quantity they perturb; one registered
  no-alarm control (initial-state shift) which is silent as required.

## What it does not establish

No unseen architecture is claimed: the recovered class is a Mealy machine. No W4 or
new-domain status is claimed — and none is claimable, because a search of the
issue body, all `33` issue comments and every `.md`, `.json` and `.py` in the repo
finds **no registered W4 criteria** on `main`. Nothing about real or trained
systems. Nothing outside `L = 4`, `b <= 2`, binary alphabet, uniform inputs.

Claim ceiling:

```
GMI_833_Z13_ADJUDICATED_VERDICT_ON_FROZEN_PREDICTION_Z13_P1_AT_REGISTERED_THREE_MODE_FINITE_STATE_SCOPE
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z13-adjudication-v1/z13_adjudication_v1.py
python3 -I -B  research/gmi-833-z-z13-adjudication-v1/independent_z13_oracle_v1.py
python3 -I -B  research/gmi-833-z-z13-adjudication-v1/test_z13_adjudication_v1.py -v
python3 -I -O -B research/gmi-833-z-z13-adjudication-v1/test_z13_adjudication_v1.py -v
```

Stdlib only, exact rational arithmetic, no float in any claim. Route A about `4`
s, Route B about `2` s on one core. `21` tests.

## The instruments failed first

Three of them. The first null counted random *property bundles* satisfying the
frozen predicate and scored `0/200` — a number entailed by the unsatisfiability
proof, so it measured nothing; it was replaced by a threshold-law null grounded in
the enumeration and is retained only as a labelled `vacuity_probe`. The first
initial-state hostile was **inert** (`5/16` either way) because the initial state
is a state-relabelling symmetry; it was reclassified as the package's no-alarm
control and a real hostile put in its place. The first relabeling control control did not
fire, because relabelling the machine *and* its outputs is a genuine re-encoding
rather than a broken one; it was replaced by an address scramble, which changes
`6` of `14` cases. A deterministic single-start greedy search also stalls at `4`
errors on the `b = 2` delay-2 channel where exhaustive enumeration and a seeded
hill-climb both reach `0`; that stall is reported, not hidden.

## One gate this package does not pass, and why

`ab-terminology-harness` is red on this branch, and deliberately so. The
`terminology_ratchet_v1` new-file rule fails a lane for any markdown file it adds
that contains a banned term. This package adds four such files, and **all** of
them are freeze documents: `FREEZE_V1.md` and `FREEZE_V1_AMENDMENT_1.md` in each
of this lane's two packages, carrying `16` hits between them.

`4` of the `16` are verbatim quotations of the issue rows the freeze is obliged to
quote byte-exact; PR #1050 exempts exactly that class and is open at the time of
writing. The other `12` are the lane's own prose *inside a committed
pre-implementation freeze* — a document that may not be edited once its receipt
exists, because that immutability is the whole custody property the #833 standard
rests on. Editing them to satisfy a lint would trade a real guarantee for a green
tick, so they are left exactly as committed and the gate is left red with this
note. Every non-freeze file this lane adds is clean: `0` hits.

The general repair this needs — and it is not this package's to make, because
`terminology_ratchet_v1.py` is being edited by #1050 — is either to extend that
PR's exemption to prose inside immutable freeze documents on the same criterion
the ratchet's own source comment already names, or to introduce a
`FREEZE_TERMINOLOGY_ADDENDUM` convention in which a later, editable addendum
carries the vocabulary migration while the freeze itself stays byte-exact.
