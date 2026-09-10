# The MDL win belongs to compression, not to OCM — and it makes the economics pay

Two results from the same run, one of which corrects an attractive misreading.

## The fairness control

`CONTINUED_MDL` beat `ORDINARY_ADAPTIVE_PARENT` by 30× on E7. That looked like OCM
superiority, but it conflated two different things: the selection **rule** (MDL vs
frequency) and the OCM/parent distinction. The parent was serving the *frequency* library.

So the ungated parent was given the **same MDL library**:

| arm | ladder | mean `B` | fragments |
|---|---|---|---|
| `CONTINUED_MDL` | 194 | 966.5 | 7 |
| **`PARENT_WITH_MDL`** | **194** | **966.5** | **7** |
| `ORDINARY_ADAPTIVE_PARENT` (frequency) | 98 | 29 671.1 | 16 |
| `CONTINUED` = `RESET` | 62 | 58 752.6 | 0 |
| `SHUFFLED_HISTORY` | 48 | 108 287.6 | 14 |

**Identical to the slot.** Given the same library the parent matches OCM exactly, as in
every admitting world in this lane.

```text
The win is MDL superiority, NOT OCM superiority.
```

OCM's only genuine advantage over the strongest parent remains
[deployment liveness under ecology shift](../m2p1/records/PLASTICITY_PROBE_V1.json) — the
one thing a static decision list structurally cannot do.

## The economics, on a horizon that was actually executed

The first ledger read zero benefit because it scores `CONTINUED`, which the registered
rule refused. Scoring the arm that actually deployed (`--deployed-arm`, a real defect in
the ledger tool, now fixed):

| ledger | acquisition | break-even | horizon | pays | net |
|---|---|---|---|---|---|
| conservative | 3 021 419 | 52.3 | 43 | ✗ | −536 617 |
| **marginal** | 1 417 932 | **24.5** | 43 | **✓** | **+1 066 870** |
| **incremental** | 710 841 | **12.3** | 43 | **✓** | **+1 773 961** |

57 786 slots saved per target, over **43 future targets that were actually run** — not a
projection from a per-target rate. The developmental investment repays itself inside the
executed horizon on two of three ledgers.

The conservative ledger still does not pay (52.3 needed, 43 available), and it is the one
that charges every developmental solve as pure overhead. That remains the honest ceiling.

## What each gap now stands at

| gap | status |
|---|---|
| lifetime economic advantage | **observed, positive on marginal and incremental**; conservative short by 9 targets |
| OCM-specific superiority | **plasticity only**; the MDL margin is the rule's, not OCM's |
| independent ecology | still negative here — MDL raises the foreign-vocabulary win rate 68→88 of 211 but does **not** admit |

## Method note

`--deployed-arm` was a genuine bug: a successor policy can admit while the registered rule
refuses, and scoring the refused arm reports zero benefit and hides the successor's
economics entirely. Any future comparison of admission policies must score the arm that
actually served a library.
