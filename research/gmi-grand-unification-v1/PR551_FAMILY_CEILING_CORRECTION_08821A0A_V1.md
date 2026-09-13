# PR551 selected scores versus family ceilings

The complete immutable [source delta packet](../gmi-pr551-delta-08821a0a-v1/MANIFEST_V1.json)
binds the [pinned assessment](../gmi-pr551-delta-08821a0a-v1/PR551_DELTA_CORRECTION_08821A0A_V1.md),
source excerpts and reported summaries at
[08821a0a](https://github.com/SzeChunYiu/ORION-OCM/commit/08821a0a1a6eead3e68143577a8910843c4c902e).
Its13 payloads are preserved separately from NAR's earlier32-file audit.
The two changed paths are prose/data, with no VM code change.

For selected configuration a, varying scores c(e) do not imply varying
optimal family ceilings F(e)=sup_{b in family} score(b,e).
A second unmeasured admitted configuration scoring1 at every ecology gives
F(e)=1 everywhere while all selected scores still vary.

A constructive separation instead needs a same-scope upper bound U(e1)
for every admitted family member and a feasible witness L(e2), with
U(e1)<L(e2). For a proposed ceiling variation at most delta, require
L(e2)-U(e1)>delta. Attainment is unnecessary for a valid upper bound.
Interfaces, families and costs must agree across the comparison.

The new matrix retains36 reported rounded minimum scores and six constant
baselines, but lacks the execution/source/runtime and complete intervention
records needed to authenticate an execution or determine a full frontier.
Four search cells and another partial matrix are prose-only reports.
Withdrawal of broad memory dominance is appropriate when competitors were
omitted; replacing it with broad exact-search dominance remains unsupported.
This is an analytic inference correction plus source-bound summary inspection,
not a new experiment, measured capability recovery or global family verdict.
