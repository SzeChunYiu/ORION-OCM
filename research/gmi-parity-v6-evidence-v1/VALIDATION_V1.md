# Validation readout

All three exact-release interpreters independently audited their actual retained
packet. Each rejected all 50 malformed copies. The shared frontier, terminal and
opcode results matched the earlier partial audit.

There are **19 focused tests per exact interpreter**, all passing normally and
with optimization: **57 normal + 57 optimized**, zero skips. Coverage includes
archive drift, strict JSON, missing/mismatching interpreters, incomplete worker
results, relocation, ambient CI independence and a guard against entering
candidate or measurement code. Source-inconsistent Slurm labels are rejected;
source-legal Slurm/GitHub precedence and optional fields remain accepted.
Independent point-Pareto corner controls establish the stated possible versus
necessary lookup qualification.

The normal and optimized aggregate outputs are byte-identical:
`fc4ac7e1c126c712f5c18dad4fde7d125cfcba1f30c9c6ab8eb5321c991a08f6`.
The [full receipt](FULL_RETAINED_AUDIT_RECEIPT_V1.json) binds every active Python
source, each original packet and every current audit executable.

The separate withheld-interpreter-map control returns exit 2, UNVERIFIABLE and
zero validated packets. It tests unavailable evidence handling; it does not
claim that the three interpreters used for the successful audit were absent.

See [structured validation](VALIDATION_V1.json) and retained test logs under
`raw/validation/`. These are static inspection tests. No new candidate,
priming, warmup, timing or search measurements were performed. Historical
provenance and missing priming traces remain outside the validated scope.
