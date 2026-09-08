# Isolated release entry repair

The exact Python -I -S -B command could not import registry_scope because the script
added only its donor directory to sys.path. The synthetic import-based controls had
already added the root and therefore did not test this entry condition.

The single-line repair explicitly adds ROOT and ROOT/donor. The release algorithm,
scoped declaration, corpus positions, exclusions and native boundaries are unchanged.

startup-01 retains the actual failure: PID 1991644, exit 1, ModuleNotFoundError.
startup-02 retains the fresh repaired command: PID 1993187, exit 1 at the intended
wrong-request-schema guard. Both used the same authored wrong-schema bytes from
cwd /tmp with isolated Python; neither request contained a corpus or gate path.
No output directory was created. The repaired control passed by refusing correctly.

The previous complete v2 source/request/freeze is retained in source-candidate-02.
RELEASE-SOURCE-FREEZE-03.json now binds only the four release sources and exact
request/scope/proposal. Keep those bytes fixed once root issues its separate gate.

The TRACE_READY hypothesis-contract consumer defect remains a separate documented
blocker in CONSUMER-BLOCKER-01.json. It has no role in custodian release and has not
been patched in this source generation. No actual release or native run occurred.
