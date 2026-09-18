# BLINDNESS_V1 — how family labels are kept out of `F`

The row *"Test predictor on held-out known architectures"* is only meaningful if
the architecture family cannot leak into the predictor's inputs. Convention is
not enough, so blindness is enforced three structurally independent ways and
each is machine-checked.

## 1. The realization record has no label field

`build_sigma_arch()` produces two parallel sequences:

- `ARCH_MACHINES[i] = (mech, param, w, h)` — the simulator's argument, used only
  by the external evaluator;
- `ARCH_RAW[i] = (param, w, h, k, rho, dev, obs)` — the **registered
  realization**, which is what `F` sees.

The mechanism string is absent from `ARCH_RAW` by construction. `F` reads only
`rec[3]` (`k`), `rec[4]` (`rho`), `rec[5]` (`dev`) and `rec[6]` (`obs`), plus the
capability table; none of those carries a family name. `ARCH_LABELS` is a third,
separate sequence that no predictor path ever touches.

## 2. `ast` audit of the descriptor encoder

`arch_descriptor` is the only function that turns a machine into a registered
realization. The test suite parses the module with `ast` and asserts that the
body of `arch_descriptor` contains **no string literal equal to any family name**
and no attribute or subscript named `family`/`label`. The encoder does consult
`ARCH_K[mech]`, i.e. the *mechanism* tag, which selects the simulator; that is a
structural property of the machine, and the audit proves the derived value `k`
takes the same value for `REC` and `CTR` (both `k = 1`), so `k` is not a
one-to-one recoding of the family name.

The audit's negative control is a planted hostile encoder that branches on the
literal `"REC"` to boost `k`; the audit must flag it.

## 3. Label-permutation invariance

The strongest check, because it does not depend on reading the source. The test
applies each of the 24 permutations of `("FF","REC","CTR","STK")` to
`ARCH_LABELS`, rebuilds the universe, and requires the sha256 of the full
51,840-row prediction stream to be **byte-identical** under every permutation.
If any family name reached `F`, some permutation would move a prediction.

## 4. What blindness does *not* claim

It does not claim `F` is unable to *infer* an architecture class from structure —
it demonstrably can, and `k` is exactly such an inference. The claim is narrower
and checkable: the family **name** is not an input, so the held-out
known-architecture result is not a lookup.
