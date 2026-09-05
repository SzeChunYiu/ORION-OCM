# Corrected evaluation prerequisites

This package supplies executable prerequisites for [OCM #38](https://github.com/SzeChunYiu/ORION-OCM/issues/38).
It is development engineering on OCM base `3039e233486252c5092728ab5fbdcdac0aa61ab4`.
It does not execute a protected study, register a study retrospectively, or restore
historical M11/M12 conclusions. Original runtime and receipt files are unchanged.

## Implemented corrections

`match_cases` requires the exact same nonempty lifetime/family/case keys, task,
rubric, information, candidate-channel, order and named resource ceilings in
both arms. Duplicates, missing cases and the historical six-versus-four shape are
rejected. Equal lengths alone are insufficient. The expected case specification
belongs to the evaluator; a solver should receive only its registered input view.

`paired_descriptives` requires an actual, explicitly boolean observation bound
to each declared case. It neither drops undecided cases nor pads missing ones.
It returns exact rational rates and differences separately for each lifetime
and family. It supplies no significance, equivalence or superiority decision:
distinct IDs or seeds do not certify independent inferential units, and matching
declarations do not authenticate actual information exposure or parent strength.

`grade_lifecycle` grades a query against its registered lower/upper warrant
profiles and current revoked identities. Valid prior knowledge does not have to
be UNKNOWN before a new lesson. Revoking that lesson does not kill an independent
live support. If lower support disappears but upper closure is incomplete,
UNKNOWN is retained. Tests compare this calculation with the actual OCM runtime
over all **1,344** three-evidence interval/revocation combinations.
Profiles are supplied by the evaluator and must already incorporate dependency,
scope, contradiction/nogood and evidence-admission checks. This helper does not
discover hidden supports or establish correspondence between English and a query.

`check_self_change_binding` checks the named component target, exact incumbent
and predecessor, candidate/assurance subject, source and scenario identities,
preservation evidence and matched candidate channel. A `machine` alias cannot
replace a different named target. Even consistent metadata returns
`adoption_authorized: false`; receipt authenticity, protected assurance and actual
external adoption remain outside this read-only utility.

These are scoped consequences of the existing warrant interval algebra,
source-bound assurance contract, and V2's corrected
`KSO_LIFETIME_BATCH6_INTEGRATION_REVIEW_V1.md` and
`KSO_OPEN_LIST_CLOSURE_THEOREMS_BATCH7_V1.md` at
`b15abb41e1f9219ea793a15c5e641ac6579adb35`. They are not new learning theorems.

## Next prospective study

Both arms must execute one shared transfer inventory, covering the following
six structural cases rather than their current arm-specific lists:

| Case | Required comparison |
|---|---|
| Partial adapter | Same omitted role and adapter interface |
| Representation correspondence | Same source skill, mapping and destination task |
| Deceptive analogy | Same tempting action and preservation requirements |
| Full science mapping | Same six-role science interface and verifier access |
| Missing science binding | Same missing report role |
| Lookalike verifier | Same deceptive verifier identity and check budget |

This is a design requirement, not six newly measured observations. Candidate
generation and verifier access must also be matched to the strongest faithful
parent. Freeze the actual inputs, parent/source versions, order/failure families,
language rubric, inferential unit, randomization assumptions, margins, power and
missingness rules before protected outcome access. Freeze M11's target and
preservation suites separately from candidate development. External custody and
adoption evidence are still required; none is manufactured here.

The language rubric must record before/after query meaning and admissible support
alternatives. Wording or retained knowledge may differ legitimately across
lifetimes. Semantic correspondence and independently justified support coverage
are prerequisites for a protected language score, not consequences of this
helper returning the expected liveness label.

## Replay and disposition

```sh
python research/evaluation-continuation-v1/test_contracts.py
```

The suite includes unmatched identity/count, different information/resources,
undecided observation, stale binding, prior-knowledge retention, alternative
support, incomplete closure, wrong predecessor and non-authorizing assurance
controls. The tests are authored development checks, not independent scientific
review. The package advances M11/M12 evaluation infrastructure; #38 remains open
for the actual prospective studies, broader learning and verified mathematics.
