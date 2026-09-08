# Independent retained native-export review

Accepted for the registered export scope. No material blocker was found in the retained source, authority or artifacts. Root decides their next use.

[Review receipt](REVIEW.json) → [raw independent audit](AUDIT-01.json). The audit reader is [audit.py](audit.py), with separate custody, inventory and trace-binding modules. It imports only its own reader modules and the standard library.

## Actual execution and custody

- Gate `e03cc44b…` authorized the one fixed request `e9e04864…`; observed child PID 2048380 exited 0 and was reaped by observer PID 2048362.
- The exact argv, cwd, interpreter, request copy and source maps match. All 25 opening pins, 26 unchanged-input records, nine exporter sources, 35 historical manifest entries and eight output identities were checked against current bytes.
- The actual observer matches its reviewed copy (`17cd28c8…`). The unchanged native checker is `a1586636…`; this review hashes it and never imports or executes it.
- Independent audit PID 2073037 completed against the actual records. Clean data passed; four deliberately different/malformed data cases were refused by the reader's comparison/JSON guards. These are reader controls, not scientific experiments.

## Native authority and complete library

- The stderr contains exactly 8,446 `Verify:` lines: the exact source order of all 4,223 proof labels twice. Fresh-pass progress records every accepted proof in that order. The second pass completed without error or fallback; it observed the released training traces.
- The authority binds the exact prospective contract and all 100 source `$a` entries. No earlier native receipt is inherited.
- The four additions are `csymdif`, `df-symdif`, `c0`, `df-nul`: two class syntax declarations and two definitions. This does not establish four independent mathematical assumptions.
- P0 is byte-identical to its 4,191-entry original. P1 retains all 4,323 contracts in source order: 4,195 current base entries, including all 100 `$a` entries, plus all 128 released theorems. No released root disappears because its trace is unusable.

## Trace output

- All 128 ordinal/label pairs, source/proof raw identities, source statements, full contracts and fresh native scope bindings agree with the fixed release and prefix.
- All 71 accepted trace hashes and used-contract-map hashes match the authority. Their 811 used-contract entries match native/source/P1 contracts, source order and the declared mandatory-hypothesis/no-DV interface. Each recorded trace root has the exact issued theorem statement.
- The other 57 roots retain `TRACE_UNUSABLE`: 53 source/active-DV cases, three used-assertion-DV cases and one mandatory-hypothesis case. Their full observed traces remain in the separate custodian record; their packet trace fields remain empty.
- `PARTIAL_OR_UNUSABLE` is the transport result. Both native proof passes completed. Raw observer progress precedes the transport check, so its 128 `TRACE_READY` entries do not override the final 71/57 split.
- Native proof and trace semantics were not replayed by the reviewer. This checks the retained bindings and declared interface, not eligibility of extracted cuts.

## Costs and limits

Observed outer window: **2.946905880991835 s**; child process: **2.8965960160130635 s**, user **2.821098 s**, system **0.072028 s**, maximum RSS **135,744 KiB**. These overlap and must not be summed. The outer window runs from observer entry through post-run input/output hashes. Interpreter/import startup, source preparation, root review and final receipt serialization are outside it. It is not lifetime cost.

The result is transport readiness under this exact registered authority. It establishes neither 71 learning opportunities nor acquired methods, useful transfer, speedup or novelty. No opportunity census, learner, new native/trace replay or full-corpus read occurred during this review. The full corpus digest remains inherited metadata; the fixed closed prefix alone was inspected for lexical order and source byte spans.
