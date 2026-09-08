# TRACE_UNUSABLE diagnosis

Custodian traces for all 57 roots were read from the frozen native-export
archive. Each trace is `NATIVE_VERIFIED`, has a well-formed 6–174-node DAG,
and reconstructs the issued theorem at its root. Packet rows keep `trace`
null. Opportunity RESULT labels are the same 57.

| Subtype | Count | What the frozen transport saw |
|---|---:|---|
| `OUTSIDE_NO_DV_INTERFACE` | 53 | Source `$d` and/or inherited `active_dv` nonempty (33 both, 20 active-only, 0 source-only) |
| `OUTSIDE_USED_CONTRACT_NO_DV_INTERFACE` | 3 | `dfnul4`, `eq0f`, `notab`: used assertions declare `$d` (`df-dif`, `nfcv`, `abid2`) |
| `OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE` | 1 | `vn0ALT`: proof uses extra `vx` (`setvar x`); theorem has no mandatory hyps |

Independent reclassification from the traces plus P1, and a replay of
`trace_transport.prepare`, reproduce the same 53 / 3 / 1 split.

## Why this is not the class-packet wff guard

That predecessor parser refused valid ordinary ground syntax that the rest of
the matcher already handled. Here the observer already produced complete
traces. The filter is the declared first boundary of transport, `typed_context`,
`typed_constructor`, extract and emit: empty source/active/used-contract DV,
used `$f/$e` exactly the mandatory lists, then three homogeneous class/wff
floats.

The three used-assertion-DV roots have empty `required_active_pairs` on every
node. They still fail the declared `row["dv"] == []` check, and they have 1–2
floats, so they would remain `UNKNOWN_INTERFACE` even if that check were
narrowed. `vn0ALT` is a complete 6-node proof of `|- _V =/= (/)` that depends
on an extra active float; it has zero mandatory parameters.

`sslin` is the unique root whose only ordinary-ready blocker is inherited
`active_dv` (`A x`, `B x`, `C x`) that this proof never instantiates. It already
has three homogeneous class floats and empty source `$d`. Admitting it would
change the declared no-DV first boundary, not repair a syntax adapter. That is
a separately reviewed interface expansion, not this confirmation.

## Not claimed

No root is `TRACE_READY`. No cut was re-enumerated. Native training was not
re-exported. This is not `CAUSAL_METHOD_REUSE_SUPPORTED` and does not check
G2.4.
