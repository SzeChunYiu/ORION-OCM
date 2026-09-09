# G5.3 ROBDD warrant parent v2

**Terminal:** see `RESULT.json` after the local run.

Successor to [`research/g5-factored-warrant-v1`](../g5-factored-warrant-v1/CORE.md)
(`FACTORED_WARRANT_VALUE_SUPPORTED`), which left ROBDD/ZDD OPEN.

Research parent: Bryant ROBDD (unique table + apply) for lower/upper warrant
Boolean functions. Stdlib only — no `dd` / CUDD / pyeda.

Production `src/ocm/kso/warrant.py` antichain oracle is unchanged.

## Question

Does an independent ROBDD interval parent match the antichain oracle and the
v1 support DAG on exhaustive n=3 revocation liveness, expand, ⊕, and ⊗?

## Parents

- antichain oracle (production)
- hash-consed support DAG (v1, compared, not replaced)
- research ROBDD (this capsule)
- ZDD left OPEN: no ZDD package and no independent ZDD manager in this successor

## Not claimed

Production adoption. Lifetime economics. Packed-field G5.2. ZDD / CUDD as
strongest conventional parent.
