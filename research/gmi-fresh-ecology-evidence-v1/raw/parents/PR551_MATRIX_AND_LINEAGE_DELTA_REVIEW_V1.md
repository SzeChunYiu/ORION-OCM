# PR551 matrix and lineage delta: source-pinned review

This independent empirical audit is frozen at commit
`70c4f676c13b73fecedf318fee9dd6b4767e847a`. It does not extend or delay
the separately integrated formal V19 result. No search, VM invocation,
campaign, timing, priming, candidate execution, or new measurement was run.

## Scope and exact provenance

Baseline: `08821a0a1a6eead3e68143577a8910843c4c902e`.
The complete delta contains exactly two commits and three paths:

- `745f27bfe80f69333c1d1c6f8749c519fadd4631`, 2026-09-13 17:18:38 UTC:
  learner admissibility map +53 lines and a new 196-line family matrix.
- `70c4f676c13b73fecedf318fee9dd6b4767e847a`, 2026-09-13 17:42:06 UTC:
  RV-377-180 freeze +33 lines reporting a fifth recovery.

All three paths are under `research/machine-intelligence-morphogenesis-v1/`:
`GMI_LEARNER_ADMISSIBILITY_MAP_V1.md`,
`microscopes/results/STAGE_FAMILY_ECOLOGY_MATRIX_V1.json`, and
`GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md`.
Complete changed-path lists, commit records, patch, tracked-tree enumeration,
original blobs, and content/blob hashes are retained in this packet.
See [source bindings](SOURCE_BINDINGS_V1.json) and [static inspection](INSPECTION_V1.json).

No runtime, test, or runner path changed in this delta. The VM is byte-identical
to the baseline: SHA256
`ef6dba6b1b418b6750650b0518c817432c098efb746afeae9dea0ace6bdfe932`,
Git blob `fc176ae7e901bf34aae70456e16fd1784a8fc249`.
This is the historical VM, not the separately repaired NAR VM.

## P551M-1 — retain the matrix; restrict its quantifiers

The new JSON retains 54 rounded score summaries: nine named configurations
on six named V1 ecologies, each summarized by its minimum across six interventions.
It adds `compiled_search`, `program_search`, and `particles_p4` to the six
previously reported cheap configurations. The two search rows each report
(.9583, 1, .9583, .9375, .9375, 1), mean .9653, population SD .0260,
and admission on all six ecologies under the authored rule.

**Accepted conditionally:** these are retained score summaries supporting
the stated selected-configuration comparison if their underlying executions
and declared scoring contract are correct. They are not absent evidence.
The new search summaries supersede the previous snapshot's lack of such
JSON summaries only for this later version; preserve the earlier audit at 088.

**Unknown:** the new JSON supplies no exact runner/command, interpreter,
source binding, seed, basis, event count, serialized candidates, individual
intervention scores, output traces, ledgers, or acquisition/lifetime costs.
Its `fx=16` field is a fixed-point scale, not a complete cost record.
No execution authenticity or common measurement provenance is established here.

**Corrected quantifier:** admission of these two configurations on all six
ecologies is not admission of every search implementation, exclusion of
unexamined memory or gradient implementations, a family optimum, or a frontier.
For a maximized capability family, an observed score is a lower bound.
Such observations cannot refute a proposed constant optimum ceiling without
a same-interface upper bound below an observed score elsewhere, or an
attained/exhaustive optimum certificate. A second unsampled configuration
scoring one on every ecology remains a countermodel to the family inference.

## P551M-2 — finite grammar search, not arbitrary target discovery

The strongest matched implementation parent is the actual archived source:
[VM at the frozen head](https://github.com/SzeChunYiu/ORION-OCM/blob/70c4f676c13b73fecedf318fee9dd6b4767e847a/research/machine-intelligence-morphogenesis-v1/gmi_microscope/vm.py)
and [zoo constructors](https://github.com/SzeChunYiu/ORION-OCM/blob/70c4f676c13b73fecedf318fee9dd6b4767e847a/research/machine-intelligence-morphogenesis-v1/gmi_microscope/zoo.py).
They are mechanism parents, not independent external comparators.
Both search constructors use SEARCH; one executes the program and the other
materializes its lookup representation.

Grammar zero contains 7^4 = 2401 coefficient vectors. SEARCH traverses
`gr.progs[:budget]`, selects the first minimizer of its stored-evidence error
objective, and writes that program. Thus full coverage constructs a minimizer
of this declared finite quantized objective. This is a useful exact positive
result, conditional on the specified evidence, grammar, arithmetic and coverage.

It does not identify an arbitrary true target. Every grammar-zero program is
homogeneous and returns zero on the all-zero input; a positive constant target
there is outside this grammar. This is an analytic extension countermodel,
not a new measured result or a claim about one of the six reported ecologies.
Realizability, evidence identifiability, execution equivalence and total costs
are additional premises for stronger guarantees.

The reported small SD across six ecologies is descriptive. The assertion
that “target-agnosticism” causes flatness is not identified by this matrix:
there is no independently specified intervention on that mechanism.
A bounded finite-grammar optimization theorem is the constructive correction;
no new universal discovery algorithm or measured causal effect is claimed.

## P551M-3 — keep each developmental denominator

The map's “recovered a third of the time” is not a common empirical probability.
Whole source-bound records are retained under `raw/head/.../microscopes/results/`.
Their reported PROGRAM-carrier fractions are:

| Record | Ecology-specific reported fractions |
| --- | --- |
| STAGE_CLASSRATE_FRESH_V43_CLASSRATE_billy | E_cr1 1/3; E_cr2 2/3; E_cr3 1/3; E_cr4 1/3 |
| STAGE_CLASSRATE_FRESH_V45_CLASSRATE_billy | E_cr5 1/3; E_cr6 1/3 |
| STAGE_CLASSRATE_V43_CLASSRATE_DIAG, primary runs | E_smooth1 0/3; E_smooth3 1/3; E_sym5 0/3; E_wit1 1/3 |
| STAGE_CLASSRATE_V43_LANEB_ATROPHIED | E_sym5 1/9 |

The V45 packet retains `INCOMPLETE__RECEIPTS_MISSING`; this audit does not
upgrade that whole packet to complete. The separately listed E_cr5/E_cr6 rows
have their three reported seeds each. Combining the two listed E_sym5 batches
arithmetically gives 1/12, not a universal one-third rate; their batch identity
and provenance must remain distinct. Fixed selected seeds are not by themselves
independent identically distributed draws from a common population law.

**Accepted:** static availability and developmental recovery are different
questions. **Corrected:** state each ecology, batch, carrier definition,
numerator and denominator; do not infer a shared probability or theory ceiling.
The original RV-377-140/142 registers are retained as the matched source parents.

## P551M-4 — fifth primary-lineage report is not causal genealogy

The final append reports DISJ|CONTINUED|S1, E_rnd1→E_sym5, minimum six-score
.8542, burden 68749, trace index 2349, and primary origin [seed,7] with a DENSE
carrier. It reports source capability .6667 and a source carrier mix of
15 PROGRAM, 14 DENSE, 14 TABLE, 14 KVSTORE and 5 NONE.

**Evidence status:** this is a new prose report. The complete 15,600-path
tracked tree was enumerated. No raw-arm filename matching DISJ, CONTINUED
and _S1 occurs; two DISJ_CONTINUED_S0 filenames provide positive controls.
The exact S1 arm-string search finds only the new freeze, the prior evidence
manifest, two prior adjudications and prior evidence-validation metadata.
The three JSON reports identify this arm in missing-unit fields, not as a
retained fifth execution. Search outputs and original JSONs are preserved.
Untracked or remote execution records remain unknown; this is not proof
that the reported execution did not happen.

**Conditional correction:** if that report is accurate, it refutes a universal
claim that the selected recovery's recorded primary source carrier is non-DENSE.
It does not refute or establish causal memory-to-coefficient conversion:
the recorded primary origin omits crossover-donor ancestry. DENSE primary
labels can coexist with memory donors, and the converse is possible.
A carrier label does not establish causal numerical use or necessity.

Preserve the report and withdraw the causal conclusion that both conversion
mechanisms are “dead.” The constructive next certificate would retain the
candidate, complete relevant ancestry and source-bound causal intervention;
none is invented here. The source-ordering explanation remains a hypothesis.

## Custody and boundary

[MANIFEST_V1.json](MANIFEST_V1.json) binds every other file in this packet.
Original upstream bytes are unchanged. Source inspection is sufficient for
the finite-grammar and denominator corrections; it is not a rerun.
The final review boundary is exactly 70c4. Later branch changes are not assessed.
