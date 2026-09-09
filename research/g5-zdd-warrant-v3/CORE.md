# G5.3 ZDD warrant parent v3

**Terminal:** see `RESULT.json` after the local run.

Successor to [`research/g5-bdd-warrant-v2`](../g5-bdd-warrant-v2/CORE.md)
(`BDD_PARENT_N3_PARITY_SUPPORTED`), which left ZDD OPEN, and to
[`research/g5-factored-warrant-v1`](../g5-factored-warrant-v1/CORE.md)
(`FACTORED_WARRANT_VALUE_SUPPORTED`).

Research parent: Minato ZDD (unique table + apply; suppress nodes whose
hi-edge is the 0-terminal) for lower/upper warrant families. Stdlib only —
no `dd` / CUDD / pyeda.

Production `src/ocm/kso/warrant.py` antichain oracle is unchanged.

## Question

Does an independent ZDD interval parent match the antichain oracle, the v1
support DAG, and the v2 ROBDD on exhaustive n=3 revocation liveness, expand,
⊕ (family OR), and ⊗ (family product)?

## Parents

- antichain oracle (production; strongest conventional parent in-repo)
- hash-consed support DAG (v1, imported, not modified)
- research ROBDD (v2, imported, not modified)
- research ZDD (this capsule)

## Not claimed

Production adoption. Lifetime economics. `PHYSICAL_DENOMINATOR_CLEAN`.
CUDD / packaged ZDD as a stronger library parent (stdlib manager only).
GitHub #165 G5.3 checkboxes are not ticked by this capsule.
