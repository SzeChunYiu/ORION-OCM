# G1.1.6 duplicated cognitive cores

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) G1.1 box
“Eliminate duplicated cognitive cores.”

**Terminal:** see [`RESULT.json`](RESULT.json) after the local run.

Parent freeze [`research/g1-vessel-freeze-v1`](../g1-vessel-freeze-v1/CORE.md) is
cited, not overwritten. Production `src/` is not edited or deleted.

## Question

Do language, mathematics and procedural domains share one

```text
M_t = (F_t, O_t, Π_t, C)
```

or have they forked cores?

## Measurement

Live probe on one `ocm.runtime.ocm_runtime.OCMRuntime`:

| Domain | Entry | Where state lands |
|---|---|---|
| language | `language.field_bridge.bind_meaning` | representation atom on the shared `KnowledgeSpace` |
| mathematics | `science.lifecycle.ScienceLedger` + propositional kernel | evidence / conclusion on the same ledger |
| procedural | `work.contracts.Operator` on dict state, then `admit_evidence` | dict apply does **not** write `KnowledgeSpace`; demonstration evidence uses the shared ledger |

Then revoke the language utterance. Language representation leaves LIVE.
Math conclusion and procedural demonstration stay LIVE. That is one C
(shared revoke) with independent warrants, not three cores.

## Lookalikes (classified, not deleted)

- M0 `ocm.runtime.OCMRuntime` (package export) vs live `ocm.runtime.ocm_runtime.OCMRuntime`
- `work.Operator` vs `OperatorSpec`
- `MeaningGraph`, `DialogueWorkspace`, `ScienceLedger` compact / adapter views
- `GovernedSpace` view; Π_nav vs Π_exec naming

None is a live second `(F, O, Π, C)`.

## G1.1.6 honesty

The architecture question **can be honestly checked** (share-one vs fork).
The checkbox **cannot be honestly earned as deletion**: production deletion is
forbidden, and there is no live second core to remove.

## Not claimed

`CURRENT_KSO_PARENT_SUFFICIENT` (#93 empirical field closure).
`DOMAIN_CORE_FORK_REQUIRED`. G1.2 minimality. Production adoption change.
