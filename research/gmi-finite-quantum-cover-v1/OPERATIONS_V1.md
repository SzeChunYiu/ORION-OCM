# Exact evidence operations

Python 3.12 and its standard library suffice. Run on Linux:

```sh
python3 -I -B check_finite_quantum_v1.py
python3 -I -O -B check_finite_quantum_v1.py
python3 -I -B test_finite_quantum_v1.py
python3 -I -O -B test_finite_quantum_v1.py
```

The checker emits the complete deterministic receipt. Normal and optimized
outputs must match the retained JSON byte-for-byte, including every source and
theorem binding. The tests check relocation away from the repository and a
different working directory. Source parents live inside this directory;
there are no live grand-theory imports, network calls or third-party packages.

The executable evidence includes:

- All 343 ordered triples of nonempty subsets of three actions, compared with
  exhaustive classical encoder/decoder construction and independent quantum
  lower certificates; 1,029 promised input/context checks.
- Eight positive mixtures and 24 supported pure choices, all preserving
  adequacy while changing the full allowed-output response distribution.
- Two-bit random access with its four-dimensional orthogonality lower bound
  and the separately declared two-dimensional sender-informed construction.
- Non-symmetric factor and nonprojective POVM controls, including an exactly
  checked receiver isometry.
- Shared-seed fixing with both exact binary identity branches and a failure
  control for independently averaging correlated states and effects.
- An exact dense-coding assistance control, with the two-dimensional transmitted
  subsystem distinguished from the four-dimensional receiver composite.
- The inherited 14-ray witness, all 74 promised Born checks and 37 newly
  compiled isometries, plus independent four-color rejection and the five-color
  upper certificate.
- Fifteen hostile changes: zero/float states, missing registers, lost completeness,
  wrong outputs, tiny exact leakage, weakened promise/obligation bindings,
  unsupported pure-state selection, and invalid or merely approximate mixtures.

The executable verifier accepts real rational rays and factors, with exact
normalization. It does not claim general complex/algebraic feasibility or run
quantifier elimination. Those general statements follow from the analytic
proof and its identified mature parents. A failed checker or missing source is
not a quantum infeasibility certificate.

No ecology or hardware experiment is launched. The test logs describe
verification execution only. [Validation bindings](VALIDATION_V1.json) and
[the manifest](MANIFEST.json) bind the checked artifacts.
