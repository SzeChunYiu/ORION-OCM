# PR551 delta at 08821a0a — source and claim correction

This read-only audit starts at the frozen 7328d5b3 snapshot and ends at
08821a0a1a6eead3e68143577a8910843c4c902e. It preserves the earlier 32-file
NAR diagnosis packet unchanged. No VM, ecology, search or capability run was
performed for this delta audit.

## Exact change set

Two commits, in chronological order:

- 5e22676208bfb1c5d5847ff6fc913d87effcb860, 2026-09-13T16:50:27Z:
  adds the family/ecology score summary and its initial interpretation.
- 08821a0a1a6eead3e68143577a8910843c4c902e, 2026-09-13T16:51:41Z:
  appends the correction of the memory-dominance interpretation.

The complete endpoint name/status diff has exactly these two paths, both
under research/machine-intelligence-morphogenesis-v1/:

| Status | Path |
| --- | --- |
| Modified | GMI_LEARNER_ADMISSIBILITY_MAP_V1.md |
| Added | microscopes/results/STAGE_FAMILY_ECOLOGY_MATRIX_CHEAP_V1.json |

The first commit changes both paths; the second changes only the Markdown.
No Python, native runtime, test, registration or other raw result file changes
between these endpoints. This absence statement is limited to the complete
two-commit delta, not the entire PR or uncommitted work on other machines.

The two endpoint trees differ (32066ddc8a855176802f26cde3ce3b9d8644d5b2
versus 4cd7c8dcecff5034f601f07f4da7716b1ec67f67).
Both endpoints have VM blob fc176ae7e901bf34aae70456e16fd1784a8fc249 and
byte-identical vm.py, SHA256
ef6dba6b1b418b6750650b0518c817432c098efb746afeae9dea0ace6bdfe932.
Thus this delta neither implements nor invalidates NAR's independently
reviewed parameter-marker correction. Its score interpretations cannot be
promoted to claims about the corrected runtime.

## P551D-1 — retained score summary, incomplete execution provenance

The new JSON is actual newly retained evidence: 36 rounded minimum scores
for six named configurations on six ecologies, six best-constant scores,
the intervention names, theta, an fx field, descriptive statistics and
admissibility labels. It is not merely prose and must be preserved.

Its complete key set is bound in SOURCE_BINDINGS_V1.json. The file does not
retain an executing script/command, source/binary hashes, runtime version,
seed, basis, event count, serialized genotypes, per-intervention results,
outputs, primitive ledgers, or acquisition/evaluation costs. Consequently
it supports inspection of the reported score summary, not independent
authentication or complete reproduction of its execution.

The four compiled_search entries and the claimed partial full-matrix run
are present only as prose in this delta. They are not rows of the new JSON.
The old E_parity and extra_unseen_feedback names remain the declared
historical interface, not the corrected parity/leak-free V2 interface.

## P551D-2 — selected configurations are not family optima

The new paragraphs infer from variation of one selected configuration per
row that an ecology-independent family ceiling is falsified. This inference
exceeds the measurements: selected feasible scores are lower bounds on the
family supremum, not evaluations of that supremum. The document itself
observes that different gradient configurations have different scores.

A finite countermodel suffices. Let configuration a have any reported
scores c(e) in [0,1], and let another admitted configuration b score1 on
every ecology. Then c(e) may vary arbitrarily while the same-family optimum
F(e)=sup_g capability(g,e) equals1 everywhere. This is a logical countermodel,
not a claim that such b exists in these ecologies.

Retain the narrower result: the reported selected-row capabilities vary,
and these observations defeat an exact constant-selected-row hypothesis.
A vague "roughly flat" hypothesis additionally needs a declared tolerance.
They do not by themselves refute a constant optimal family ceiling or any
law about developmental occupancy.

A constructive test of the stronger claim needs a bound on the same
family, interface, scoring rule and admissibility scope. For two ecologies,
a certified upper bound U(e1) and a feasible lower bound L(e2) satisfying
U(e1)<L(e2) disprove exact ceiling equality. Attained/exhaustively established
optima are another sufficient route. If the claim is range <=delta, require
L(e2)-U(e1)>delta. A mere upper bound need not be attained; lower-bound
observations alone cannot provide this separation. These are standard
supremum/upper-bound comparisons, not a new search or statistical method.

## P551D-3 — valid withdrawal, overextended replacement

Accept the explicit withdrawal of broad memory-family dominance: the
selected set omitted slow program_search, compiled_search and particles_p4.
A universal ranking was not licensed by that selected comparison.

The replacement "the exact-search family is the broadly admissible one"
still exceeds the retained partial comparison. Conditional on their
reported correctness and a common interface, four successful compiled_search
cells give four witnessed cells for that configuration; they do not
establish family-wide optimality, supremacy over all configurations,
generality beyond the registered ecologies, or a lifetime-cost frontier.
The cheap-row scores and their narrower descriptive ranking may be retained.
No cost/capability monotonic law follows from the omission itself.

## Source authority

- [Baseline map](https://github.com/SzeChunYiu/ORION-OCM/blob/7328d5b3b0a5111fd43c3e277679faf0edeee1bb/research/machine-intelligence-morphogenesis-v1/GMI_LEARNER_ADMISSIBILITY_MAP_V1.md).
- [New map](https://github.com/SzeChunYiu/ORION-OCM/blob/08821a0a1a6eead3e68143577a8910843c4c902e/research/machine-intelligence-morphogenesis-v1/GMI_LEARNER_ADMISSIBILITY_MAP_V1.md).
- [New retained JSON](https://github.com/SzeChunYiu/ORION-OCM/blob/08821a0a1a6eead3e68143577a8910843c4c902e/research/machine-intelligence-morphogenesis-v1/microscopes/results/STAGE_FAMILY_ECOLOGY_MATRIX_CHEAP_V1.json).
- [Unchanged VM](https://github.com/SzeChunYiu/ORION-OCM/blob/08821a0a1a6eead3e68143577a8910843c4c902e/research/machine-intelligence-morphogenesis-v1/gmi_microscope/vm.py).

The complete exact source bytes, per-commit path lists, endpoint diff, commit
objects and hashes are retained locally in raw/ and SOURCE_BINDINGS_V1.json.
