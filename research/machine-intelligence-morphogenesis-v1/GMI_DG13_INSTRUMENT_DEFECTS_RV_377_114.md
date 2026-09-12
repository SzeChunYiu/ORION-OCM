# RV-377-114 / DG-13 — two defects in registered instruments, and what they cost the corpus

Found by the DG-8 worker lane. **Both verified here by direct execution before merge.**
Neither is repaired: repairing either changes what a registered object *means* for every
prior claim, which is a decision for the records that rest on it, not a side effect of
finding it.

## Defect 1 — the `extra_unseen_feedback` intervention leaks 50% of its own evaluation set

`ecology.run_genotype`:

```python
if J.get("extra"):
    for xx in smooth.UNSEEN[:4]:
        M.phase("upd"); vm.feedback(xx, target[xx]); M.end_event()
...
eval_x = smooth.UNSEEN if spec["criterion"] == "unseen" else smooth.ALL_X
```

Verified:

```
UNSEEN: [1, 2, 4, 7, 8, 11, 13, 14]   len = 8
extra_unseen_feedback feeds back on UNSEEN[:4] = [1, 2, 4, 7]
criterion `unseen` scores on UNSEEN (all 8)
LEAK: 4 of 8 scored inputs are fed back during development -> 50%
```

Under the `unseen` criterion this intervention **trains on half the inputs it then scores**.
One of the six bars that rule 36 requires a row to clear is measuring something other than
generalisation.

### The effect is NOT uniformly inflationary — checked, not assumed

The intuitive reading is "a leak inflates capability, so rule-36 passes are too generous".
That is **wrong as a general statement**, and assuming it would have produced a false
correction. Measured across the 13 admissible recovered carriers, the leaky intervention
was the **binding** (minimum) one on exactly one: `E_wit1 | KVSTORE`, where it *depressed*
the score. Removing it **raises** that row's minimum from 0.8333 to 0.8750.

So the defect can push either way — extra feedback events also perturb and cost — and each
affected verdict has to be recomputed rather than adjusted by a rule of thumb.

### Impact on `RV-377-113`, the G15 step (ii) claim — recomputed, not argued

| ecology | carrier | min over 6 | min over 5 leak-free | binding (clean) | rule 36 | fx vs constant |
|---|---|---|---|---|---|---|
| **`E_sym5`** | **DENSE** | **0.8542** | **0.8542** | `half_events` | **✓** | **1.500** |
| `E_sym5` | KVSTORE / PROGRAM / TABLE | 0.8542 | 0.8542 | `half_events` | ✓ | 1.500 |
| `E_smooth3` | KVSTORE / PROGRAM / TABLE | 0.8594 | 0.8594 | `shuffled_events` | ✓ | 1.126 |
| `E_smooth1` | KVSTORE / PROGRAM / TABLE | 0.8542 | 0.8542 | `half_events` / `shuffled_events` | ✓ | 0.502 → WITHIN_QUANTIZATION |
| `E_wit1` | KVSTORE | 0.8333 | **0.8750** | `shuffled_events` | **✓ (flips)** | **4.001** |
| `E_wit1` | PROGRAM / TABLE | 0.8333 | 0.8333 | `shuffled_events` | ✗ | — |

> **`G15_STEP_TWO_REACHED` stands.** `E_sym5 | DENSE` binds on `half_events` under both the
> six- and the five-intervention set; its minimum is 0.8542 either way. The defective
> intervention was never load-bearing for it. The claim is unchanged.

**One verdict flips, in GMI's favour.** `E_wit1 | KVSTORE` fails rule 36 on the six and
passes on the leak-free five, at **4.001 fx units** — the largest margin in the table. So
`E_wit1`, the ecology `RV-377-102` built specifically to host a witness, **does** carry an
intervention-robust carrier after all: exemplar memory, not the coefficient carrier.

Valid recoveries: **7 on the six-intervention set, 8 on the leak-free five.**

### Corpus-wide consequence

Every rule-36 verdict in the corpus was taken against a six-intervention family one of
whose members is defective. Rule-36 **failures** where the leaky intervention was binding
may be spurious; rule-36 **passes** rest on one bar that does not measure what it claims.

> **DG-13.** Until `extra_unseen_feedback` is repaired or retired, every rule-36 verdict
> must be reported **twice** — over the full six and over the leak-free five — and any
> verdict that differs between them is `INSTRUMENT_DEPENDENT` and may not be quoted
> unqualified.

## Defect 2 — `E_parity` is not a parity target

```python
def spec_table(table, name, ...):
    return {..., "table": [int(v) for v in table], ...}
```

`table` is passed a **dict**, and iterating a dict yields its **keys**. Verified:

```
E_parity table stored : [0, 1, 2, ..., 15]
E_parity target       : [0, 1, 2, ..., 15]
is identity 0..15?    : True
```

`E_parity`'s obligation is the **identity function**, not parity. Every claim in the corpus
about "the parity ecology" is a claim about an identity target.

This is contained by two independent facts already on record, which is why it changes no
verdict here:

* `RV-377-108`: `E_parity` is `WITHIN_QUANTIZATION` on **both** criteria (0.401 fx units),
  so under rule 40 it can certify nothing and no positive rests on it.
* `RV-377-112`: `E_parity`'s obligation is `NON_DEGENERATE` — the identity takes 16 distinct
  values, so it is at least a real function rather than a constant.

The damage is to **interpretation**, not to any surviving verdict: the corpus has been
calling an identity ecology a parity ecology.

**Not repaired.** Fixing `spec_table` silently re-points every historical `E_parity`
reference at a different target. The defect is recorded, the misnaming is flagged, and the
repair is registered as owed with its consequence stated.

## Terminals

| terminal | value |
|---|---|
| `G15_STEP_TWO_REACHED` | **TRUE** — unchanged, recomputed leak-free |
| `ALL_REGISTERED_INTERVENTIONS_MEASURE_WHAT_THEY_CLAIM` | **FALSE** |
| `ALL_REGISTERED_ECOLOGIES_ARE_WHAT_THEY_ARE_NAMED` | **FALSE** |
| `DG-13_CLOSED` | **FALSE** |

## New protocol rule

> **Rule 46.** An intervention or ecology is part of the instrument, not of the result. Each
> must be validated against its own declared semantics — an intervention must not touch its
> evaluation set, an ecology's realised target must equal its named target — and that
> validation must be re-run whenever either is edited. Two registered objects went years
> without this check; both were wrong.
