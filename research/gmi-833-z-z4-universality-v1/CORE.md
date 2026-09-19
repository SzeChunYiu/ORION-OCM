# GMI #833 Section Z / Z4 — universality classes of machine intelligence

Closes **three** of the five rows of `### Z4` in issue comment `5684819296`:
rows 2, 3 and 5.

Rows 1 and 4 are **deliberately left open**, and `FREEZE_V1.md` forbids this
package from touching them. Row 4 names MLP, CNN and Transformer and carries no
*where justified* clause; row 1 says "many named architectures" and carries none
either, and the issue's own enumeration of named architectures is row 4's list.
Answering either from a binary transducer universe whose named families are
Moore and Mealy would be closure by narrowing. Row 3 carries the explicit clause
*where mathematically justified*, which is what licenses a scoped answer there.

## What it establishes

- **`UC-1`** class membership by resource response rather than by name: `568`
  classes, sizes `2..14360`, `0` singletons, strictly between the `6` registered
  named families and the `21904` behaviour classes, invariant under renaming,
  and non-degenerate by a guard validated on two planted degenerate definitions;
- **`UC-2`** exact frontiers at every rung — `{(0,2)}`, `{(0,8)}`, `{(0,24)}`
  without state and `{(0,0)}` with one bit — the Moore/Mealy frontier separation
  `{(8,0)}` vs `{(0,0)}` at identical budget, and the exact asymptotic forms:
  the stateless delayed minimum is `(L-1)*2^(L-1)`, exactly half the scored
  moments, at every rung. **No exponent is reported**: the ladder has `2` and
  `3` rungs and an exponent fitted to that is not identified. The guard issuing
  that refusal is validated in both directions — it accepts a synthetic `5`-rung
  axis;
- **`UC-3`** of `16` distinctions, exactly **one** survives both the semantic
  quotient and re-encoding invariance: *output independent of state* vs *output
  independent of input*. `13` are implementation details and `2` are encoding
  artifacts. The state-bit split and the Moore/Mealy membership split are both
  among the casualties, and both refutations were frozen hypotheses.

## What it does not establish

Nothing about MLP/CNN/Transformer; no general collapse of named architectures;
no universal exponent; no asymptotic law beyond `L = 4`; no claim that this
quotient is canonical or that irreducibility here means irreducibility under all
re-encodings.

Claim ceiling:

```
GMI_833_Z4_RESOURCE_RESPONSE_UNIVERSALITY_CLASSES_AND_SURVIVING_DISTINCTIONS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z4-universality-v1/independent_universality_oracle_v1.py
python3 -I -B  research/gmi-833-z-z4-universality-v1/z4_universality_v1.py
python3 -I -B  research/gmi-833-z-z4-universality-v1/test_z4_universality_v1.py -v
python3 -I -O -B research/gmi-833-z-z4-universality-v1/test_z4_universality_v1.py -v
```

Stdlib only, exact integers, no float in any claim. Route A about `72` s,
Route B about `6` s on one core.

## The instruments failed first

`HS3` and `HS4` as first written **could not fail**: one checked that two fields
exist, the other was the constant `len(LADDER_L) < 4`. Both are the Z7 `C4`
failure class. `HS5` was registered and never implemented. And `N2` came out
`0/200` for the wrong reason — a uniformly random split across `21904` behaviour
classes cannot even reach the clause it was supposed to test. All four were
repaired, and the repair declared, before any repaired number was used
(`FREEZE_V1_AMENDMENT_1.md`).
