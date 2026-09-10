# G5.3 factored warrant v1

**Terminal:** see `RESULT.json` after the local run.

Research parent: hash-consed support DAGs for lower/upper warrant expressions.
Production `src/ocm/kso/warrant.py` antichain oracle is unchanged.

## Question

Can a factored support DAG keep lower ≠ upper, preserve ⊕/⊗, track upper-only
evidence, and match antichain revocation liveness exactly on exhaustive n=3,
with output-sized `CANNOT_CHECK` instead of approximation?

## Parents

- antichain oracle (production)
- hash-consed support DAG (this capsule)
- ROBDD/ZDD left OPEN: the DAG already shares join/meet subexpressions; a
  separate BDD package is not required to close the parity question at n=3

## Not claimed

Production adoption. Lifetime economics. Packed-field G5.2.
