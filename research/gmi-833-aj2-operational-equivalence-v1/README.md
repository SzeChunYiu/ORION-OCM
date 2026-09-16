# gmi-833-aj2-operational-equivalence-v1

Closure package for #833 AJ2 at a finite registered test scope.

Reproduce:

```bash
python3 -I -B research/gmi-833-aj2-operational-equivalence-v1/check_aj2.py
python3 -I -O -B research/gmi-833-aj2-operational-equivalence-v1/check_aj2.py
```

The checker exhausts all 19,683 three-preparation/three-effect response tables over probabilities `{0,1/2,1}`, validates operational equivalence and quotient reconstruction with two independent algorithms, and preserves the incomplete-test-family hostile as a scope boundary.

Claim ceiling: `AJ2_OPERATIONAL_EQUIVALENCE_AND_STATE_RECONSTRUCTION_AT_FINITE_REGISTERED_TEST_SCOPE`.
