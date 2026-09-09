# Recorded work and timing

| Measured window | Seconds |
|---|---:|
| Caller: one observer invocation |0.532407258986495|
| Observer entry through post-run input/output checks |0.508495400019456|
| Fresh child process |0.443209444987588|
| Consumer-reported inner wall |0.377159358991776|

These windows are nested and must not be summed. The caller includes observer startup and final serialization. The observer window excludes interpreter/import startup, source preparation, root review and final receipt serialization. The child is a fresh process; no OS-cache eviction is claimed.

Child CPU: user 0.418069000000000 s, system 0.019908000000000 s. Maximum RSS: 66,892 KiB. These are process records, not a speed comparison or lifetime-cost estimate.

| Retained consumer work counter | Value |
|---|---:|
| Source nodes considered |659|
| Essential ports considered |78|
| Two-node edges |78|
| Cut dependency visits |1,778|
| Body nodes validated |1,078|
| Expanded node visits |2,353|

The counters describe this audit's work; they are not a complete accounting of native acquisition, storage, source custody or lifetime maintenance. The preceding native export was a separate run and is not hidden inside these timings. The source path returns before matching because the proposal screens stop at syntax/type admission. Matcher counters are absent, not measured zero; no matching speed or zero-cost completeness claim follows.

The 60-second consumer deadline, two-million matching-state allocation and 180-second outer containment are registered limits, not work consumed. The result records `token_bound_reached=false`. No result was selected by rerunning this audit during packaging.
