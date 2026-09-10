# G5.3 warrant adoption economics v1

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) remaining
G5.3 box:

```text
production adoption only after economics support it.
```

Coordinator: [PR #206](https://github.com/SzeChunYiu/ORION-OCM/pull/206).

**Terminal:** see `RESULT.json` after the local run. Honest terminals are
`PRODUCTION_WARRANT_UNCHANGED`, `DATABASE_PARENT_SUFFICIENT`, or
`PARENT_SUFFICIENT`. `PARENT_SUFFICIENT` is not failure.

This capsule does **not** tick the GitHub checkbox. Adoption is a production
`src/` switch; this run refuses that switch even if a research parent wins at
toy scope.

## Frozen predecessors (cite, do not overwrite)

| Capsule | Terminal | Role |
|---|---|---|
| [`research/g5-factored-warrant-v1/`](../g5-factored-warrant-v1/CORE.md) | `FACTORED_WARRANT_VALUE_SUPPORTED` | hash-consed support DAG; n=3 parity; compression `MIXED_SMALL_N_SHARES_LARGE_N_DOES_NOT` |
| [`research/g5-bdd-warrant-v2/`](../g5-bdd-warrant-v2/CORE.md) | `BDD_PARENT_N3_PARITY_SUPPORTED` | ROBDD n=3 parity; ZDD was OPEN |
| [`research/g5-zdd-warrant-v3/`](../g5-zdd-warrant-v3/CORE.md) | `ZDD_PARENT_N3_PARITY_SUPPORTED` | ZDD n=3 four-way parity; production warrant unchanged |
| [`research/g5-physical-denominator-v1/`](../g5-physical-denominator-v1/CORE.md) | `DATABASE_PARENT_SUFFICIENT` | cited ledger parent; **not** re-issued as `PHYSICAL_DENOMINATOR_CLEAN` |

G5.3/001–007 were earned at n=3 by those parents. This successor asks only
whether **economics** license replacing production `src/ocm/kso/warrant.py`.

Predecessor modules are loaded with `importlib.util.spec_from_file_location`
so `research/g5-packed-field-v1/experiment.py` cannot shadow this capsule.

## Question

Charging, as **separate coordinates** (never dollars, never one scalar):

```text
construction   (antichain re-canon vs DAG/BDD/ZDD from_profile)
query          (identity expand vs reconstruct-to-antichain)
revocation     (liveness under revocation sets)
bytes          (per-interval antichain store vs shared unique tables)
```

does switching production warrant to DAG, ROBDD, or ZDD beat keeping the
current antichain/oracle parent?

Production data is already an antichain. A switch pays conversion on every
ingest. Query-expand of a diagram reconstructs that antichain. Revocation may
be native. Bytes may share.

## Parents

- antichain oracle (production; keep-current arm)
- hash-consed support DAG (v1, imported, not modified)
- research ROBDD (v2, imported, not modified)
- research ZDD (v3, imported, not modified)

Stdlib only. No `dd` / CUDD / pyeda.

## Decision rule

A research parent would have to be better on **every** operating coordinate
(query, revocation, bytes) at every measured *n*, **and** recoup
construction, before economics could support a switch. Toy-scope domination
still does **not** edit `src/`. Mixed Pareto keeps the antichain parent.

## Not claimed

- Production adoption / `src/` switch
- `PHYSICAL_DENOMINATOR_CLEAN`
- Dollars, wall+bytes scalarization, CUDD as a stronger library parent
- GitHub #165 G5.3/008 ticked
