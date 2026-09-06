# Quote-only setup successor — ready for registration
Cause: SMT-LIB output routing requires a quoted string. The original four
CANNOT_CHECK outputs occurred before synth-fun parsing; no generation failure
is inferred.

Only `(set-option :out stderr)` becomes `(set-option :out "stderr")`.
Four task/grammar/macro/other-option/argv/deadline/order identities are unchanged.
Original e91 proposals, manifest and27-file capture-v1 seal remain unchanged.
The unchanged capture.py will use the new input/proposal paths.

Setup-only control contains exactly set-logic, output tag and out commands.
Old form reproduces RuntimeError/exit2 after two dispatched commands.
Quoted form completes three commands/exit0. Neither control contains or
dispatches synth-fun, constraint or check-synth. Raw stdout/stderr are retained.

manifest.json SHA256 36166d8604bd7df00a0f4502c05ab6bc4ee8b0983c0e9e1845ee89c8817e9dcf
PROPOSAL.json SHA256 324707976d300bb3ead91df9d96d1318680d7d33016cd992b548569cf975f867
QUALIFICATION.json binds the actual red/green and predecessor custody.
LAUNCH.json contains the exact UNEXECUTED command.
The root-owned check_outputs_v2.py is source-bound but not executed here.
No synthesis, discovery, successor capture or new-output Z3 check ran.
Native marker/returned-program semantics remain unqualified pending registration
and capture. No option fallback, grammar tuning or automatic retry is introduced.
