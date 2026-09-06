# Executed development readout

The [exact prospective plan](https://github.com/SzeChunYiu/ORION-OCM/issues/73#issuecomment-5557323635) was registered before this single attempt.
Actor source head 7557ab98201f828f222e48dc4afc9aeb15516185 contains the reviewed implementation
at b0454c01d5fde8c367dc7c1ea16b8066931c7883 and a subsequent plan-only commit.
Plan SHA 14c6c7ed9f621cc733fb3538a1954cda2fdec698952d2796e50fb6c804b0fdd3.
No source, model, profile, plan or runtime-lock drift was observed before/after capture.
All 10 chunk processes exited 0 with 21 rows each; outer process and all 10 worker PIDs were absent after sealing.

## Actual capability

Both arms received the same 100 fixed public syntax word lists (1584 words, punctuation included)
and 5 complete public CLIA specifications. Each used the same fixed Stanza model/configuration and cvc5/Z3 interfaces.
Native used direct donor/checker calls. OCM used the existing shared executive and full Stanza+cvc5 catalogue,
persisting checked answers and state across first start plus four resumes.
Native remained OCMRuntime-free. Syntax admission was structural/model-supported observation, not a gold correctness claim.
CLIA admission independently required the declared typed grammar and Z3 UNSAT of the negated specification.

| Metric | Native | OCM |
|---|---:|---:|
| Valid accepted syntax |100/100|100/100|
| UAS |1411/1584 (89.08%)|1411/1584 (89.08%)|
| Base LAS |1368/1584 (86.36%)|1368/1584 (86.36%)|
| Full LAS |1361/1584 (85.92%)|1361/1584 (85.92%)|
| UPOS |1522/1584 (96.09%)|1522/1584 (96.09%)|
| Exact tree |34/100|34/100|
| Exact typed tree |32/100|32/100|
| Verified CLIA programs |5/5|5/5|

All 100 native/OCM selected syntax trees were identical.
The actual external grader returned GRADED_DEVELOPMENT. The prospective interpretation is PARENT_SUFFICIENT:
the independently executed conventional parent supplies the same checked capability on this fixed panel.
The integration result supports feasibility; it provides no OCM-specific capability residual.
No hosted LLM was executed in this attempt.

## Observed costs

One CPU0 affinity was inherited by the exact recorded launch. The actual reuse/model pilot was held.
Two initialization-only controls elsewhere on the host were reported during capture (0.17s, no donor/model call);
the larger fixture suite was deferred. This was a shared host, not an isolated performance experiment.
Fresh process does not mean flushed OS page cache.

| Observation | Native | OCM |
|---|---:|---:|
| Sum of outer worker wall |26.999257s|143.524862s|
| Reaped direct-child CPU observation |26.729480s|136.578287s|
| Final durable bytes |242,514,881|253,018,514|
| Shared full model/profile archive bytes |242,210,513|242,210,513|
| Other durable bytes |304,368|10,808,001|

Observed OCM wall was about 5.32 times native; additional durable state was 10,503,633 bytes.
The full outer capture took 175.409085s. Initial external grading took 1.095106s and is a separate evaluation cost.
OCM per-chunk wall was 8.61,15.12,24.83,39.04,55.93s; attribution requires a separately scoped analysis,
since ordered chunks differ in their inputs. These observations establish no efficiency improvement.
Model copies, cold loads, source/model checks, proposals, checks, commits and replay fall within the measured actor envelopes.
Wrapper self and waited-child CPU are separately scoped. Full process-tree CPU and energy remain UNKNOWN.
Compiled pipeline bytes are not separately attributable; exact durable file inventory is retained.
Installation/import costs and prior operational failures remain in the preceding engineering packet.

## Limits and provenance

The 100-item balanced genre/length panel was already exposed, including earlier native qualification outcomes.
Primary denominators retain all 100 rows/1584 words, including the duplicated word-sequence group
(99 distinct exact sequences). Prior normalized TRAIN overlap diagnostics contain 5 rows; exact-word diagnostics 4.
Those diagnostics do not establish absence of broader imported Stanza training or selection exposure.
The combined recurrent model and conll17 vectors carry broader, partly known supervised and lexical priors.
Original training/tuning/failed-attempt/resource histories remain unknown; no TRAIN-only or training-fair claim is made.
Stanza/PyTorch are adopted infrastructure; fixed weights/dictionaries are operator priors; native is the capability parent;
grammar/Z3 and the official UD scorer are checker tools.
No population accuracy, protected independence, noninferiority, broad language capability or frontier parity is established.
No new theory or controller was introduced. Whole-lifetime efficiency, local revision, learned reuse and exact revocation
need their own surviving evidence under the existing owners; this fixed donor repeat does not supply it.
