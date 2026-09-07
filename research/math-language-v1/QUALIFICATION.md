# Historical unary-language qualification

The eleven Python sources released in PR139 had **110 passing authored controls**,
with no failures, errors or skips, in the retained metadata qualification. This is a
supplied semantic contract, conventional symbolic solver, controlled-language parser
and independent verifier. It is not an OCM runtime or learner result.

Start with [the compact record index](qualification-records/CORE.md).
[The package index](qualification-records/INDEX.json) binds every archive and map;
[the source freeze](qualification-records/SOURCE_FREEZE.json) binds that historical code.
The prepared-solver successor has a separate [two-package qualification](../math-language-learning-v1/QUALIFICATION.md); the old receipts are unchanged.

## Separate source generations

| Generation | Retained final run | Source files | Outer process wall |
| --- | ---: | ---: | ---: |
| Initial contract | 83 passed | 9 | 0.916747912 s |
| Cache-key accounting successor | 84 passed | 10 | 0.917348383 s |
| Strict metadata successor, released in PR139 | 110 passed | 11 | 0.916452018 s |

These are overlapping suites at different source revisions; the counts are not
additive. Historical semantic/test commit: 7d5043dac6e5c8e2d4ab59baa9978e2af695151b.
Both final snapshots and source copies retain those exact bytes. The current solver
has changed; its prior 110-control evidence is not reassigned to the new source.

The original language archive also retains the initial 69 failures, 69-control
first pass, and the boundary run with 77 passes and two failures. The subsequent
83-control generation repairs surface acceptance of the internal not_every tag
and counts predicate-region tests. These are retained development outcomes.

The cache-key archive preserves its one failing control, one passing repair
control, and separate 84-control full run. Warm cache hits still traverse keys;
the repaired counter charges actual recursive AST-node visits.

The metadata archive preserves 19 failures and seven passes in the first
26-control probe, its 26-control passing repair, and the final 110-control run.
Exact plain-string checks precede schema, task-hash and verdict comparisons.
The API does not sandbox Python code that is already executing.

## What was checked

The suite covers both query polarities, vacuous universals, empty predicates,
nonempty domains, inconsistent premises, distinct existential witnesses, strict
grammar/schema, result/certificate tampering and verifier independence from solve.
The separate set-based oracle exhausts nonempty worlds for its declared family
with up to three predicates; it does not enumerate every bounded AST or theory,
all 32-premise combinations, or all four-predicate worlds.

UNKNOWN supplies two models; INCONSISTENT requires a premise unsatisfiability
certificate and is not an answer by explosion. This is formal controlled notation
with supplied premises, not a claim about unrestricted language or empirical truth.

The unchanged independent review is in independent-review.tar.gz, member
REVIEW.json, SHA256 dd05fbfeafb5b1c1836b25b6185904b56380766004f9387a4ae5b2f3f26dbc0f.
It reports no remaining actionable findings for its stated source/record scope.

## Evidence and costs

The four deterministic archives retain all 179 regular files present in the
three qualification roots and independent review: 841,608 raw bytes. All archive
members were compared directly with originals and their SHA256/size maps.
Original file/directory modes remain in compressed tree metadata. No symlinks
were present. Failed runs, requests, process receipts, source snapshots, raw streams
and JUnit files remain separate and unchanged.

The three original roots are under /home/billy/orion-director-work/20260907:
unary-language-qualification-v1, unary-cache-key-qualification-v1 and
unary-metadata-qualification-v1. Exact paths and archive bindings are in INDEX.

Process receipts retain each invocation's outer wall and waited-child user/system
CPU. They are not performance comparisons, whole-lifetime costs or complete RSS
measurements. Logical solver counters exclude validation, serialization, Python
hashing/equality/allocation and full host execution. No cost superiority is claimed.

[The omission record](qualification-records/OMISSIONS.json) names all ten recorded
temporary case paths, absent at packaging. Their prior creation is not inferred
and their bytes were not reconstructed. Interpreter binaries, installed packages
and the complete host/import closure remain external; retained identity metadata
does not constitute their fresh qualification.

## Portable CI

[The shared workflow](../../.github/workflows/unary-language.yml) now selects both
this package and math-language-learning-v1, with both explicit import roots, on
ubuntu-latest with Python 3.11.14 and pytest 8.3.5. It disables plugin autoload,
uses a run-specific RUNNER_TEMP basetemp, uploads JUnit even on failure, and checks
tracked-source diffs. Actual new-head CI is separate from this historical 110-control
record; changing the workflow does not itself establish a passing execution.

No tests, evidence guards, corpus work, materialization, proofs or scientific
studies were rerun for this packaging. There is no learned-method acquisition,
persistence/restart, causal fresh-use, transfer, scaling, broad chat, or novelty
result in these records. The source observation of stdlib/local imports does not
establish whole-host no-neural qualification.

The [release archive and CI review](release-review-records/REVIEW.json) independently
compared every archived member with its original and checked the prospective
workflow. It did not rerun tests or establish a hosted CI result.
