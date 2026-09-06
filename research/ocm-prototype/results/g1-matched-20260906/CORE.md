# CORE — matched native/OCM development stream

**PARENT_SUFFICIENT for the measured donor capability; G1_NOT_ADMITTED.**
The frozen source is 00c85dff3e63941856657d886946ebc3466577b2. The same unchanged
vessel receives both donor descriptors for every request across two domains.

| Outcome | Native | OCM |
|---|---:|---:|
| Selected valid syntax outputs |100/100|100/100|
| UAS |1294/1584 (81.692%)|1294/1584 (81.692%)|
| Base LAS |1234/1584 (77.904%)|1234/1584 (77.904%)|
| Full LAS |1231/1584 (77.715%)|1231/1584 (77.715%)|
| UPOS |1487/1584 (93.876%)|1487/1584 (93.876%)|
| Exact full-label tree / tree+UPOS |32/100 /30/100|32/100 /30/100|
| Grammar and universal specification passed |5/5|5/5|
| Worker wall seconds |6.986|134.503|
| Reaped process-tree CPU seconds |6.852|127.735|
| Final durable bytes including model |11,826,796|22,195,258|

All 100 selected typed trees are identical. Programs are compared by independently
checked grammar/specification, not by string equality or underspecified cases.
The syntax gate certifies structure and model provenance; external gold determines
accuracy. Completed refusal, execution failure and unattempted items stay distinct.

The 100-case panel is balanced by genre/length and is public development data.
Tokens, case and punctuation are supplied. It is neither a natural-frequency EWT
estimate nor a protected noninferiority test. No pooled cross-domain score is used.
Whole-lifetime savings, sparse cognition, local neural unlearning and a strong-LLM
comparison remain unestablished. Both arms include the same 11,631,918-byte model.

Timing is descriptive on laptop billy. The frozen run was 01:23:12.927796–01:25:34.527572 UTC.
An independent 290-case donor prediction/grading ran 01:24:02.887817–01:24:05.101668 UTC,
overlapping OCM chunk 3; hosted tool qualification also used this machine.
Training, installation, external grading and energy are outside the worker totals.
Both training attempts are charged separately in the linked donor provenance.

- [External selected-answer grades](external-grade.json), including per-item outcomes and resource scope.
- [Raw actor receipt](receipt.json) and [pre-run bindings](run-binding.json); chunk input/output files remain byte-identical.
- [Frozen stream](../g1-matched-plan-v1/plan.json) and [training evidence](../g1-trained-donor-20260906/CORE.md).
- [Diagnostic profile](diagnostic-profile/receipt.json) and [call attribution](diagnostic-profile/profile-cumulative.txt): a separate repeat-query diagnostic on an isolated state copy; not benchmark timing.
- [Checksums](SHA256SUMS). Current-main CLIA and native-import controls use deliberately invalid model bytes and carry no language claim.

Run the external grader from the prototype directory with `--plan ../ocm-prototype/results/g1-matched-plan-v1 --run THIS_DIRECTORY --gold PATH_TO_HASH_BOUND_EWT_DEV --out NEW_FILE`.
Full gold-based controls require `OCM_G1_DEV_PATH`; default absence is an explicit pytest skip, not a passed gold check.
Owners: #73/#43/#72; anchors: #50/#62/#69/#42; acceptance: #38/#49.
