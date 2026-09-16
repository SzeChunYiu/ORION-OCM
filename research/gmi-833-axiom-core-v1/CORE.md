# gmi-833-axiom-core-v1

Bounded #854 / #833-C compact foundation tranche.

This package separates:

- six **object-level** finite axioms (`AX-1`…`AX-6`);
- five derived definitions/theorems (`DEF-1`…`DEF-5`);
- two scientific-governance metarules (`META-1`, `META-2`).

It constructs one explicit finite model satisfying all six object axioms, registers every required realization channel and all five uncertainty kinds, and exhaustively checks a 128-case contradiction hypercube. The eight issue-mandated hostile classes plus three audit hostiles have exact AX/DEF/META attribution. This proves satisfiability/non-contradiction only for the registered finite core at the implemented semantics; it is not an absolute consistency proof.

## Reproduce

```bash
python3 -I -B research/gmi-833-axiom-core-v1/test_axiom_core_v1.py -v
python3 -I -O -B research/gmi-833-axiom-core-v1/test_axiom_core_v1.py -v
python3 -I -B research/gmi-833-axiom-core-v1/axiom_core_v1.py
```

Claim ceiling: `GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE`.
