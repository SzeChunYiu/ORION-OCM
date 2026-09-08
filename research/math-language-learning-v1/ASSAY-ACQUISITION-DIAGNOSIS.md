# Why the corrected assay acquired no methods

**Earliest common failing stage: the shared mining/pool construction stage.**
All eight A processes completed; neither development utility nor storage rejected a
nonempty library. This is a checked negative acquisition outcome, not missing execution.

## Actual funnel, identical in both adaptive arms

Counts below are per episode, not doubled across the two independently run arms.

| Episode | Eligible checked proof branches | Tried subcovers | Valid essential | Nonessential | Counterexample | Singleton groups excluded | Final pool |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 4 | 10 | 2 | 5 | 3 | 2 | 0 |
| 1 | 4 | 4 | 0 | 4 | 0 | 0 | 0 |
| 2 | 2 | 4 | 1 | 1 | 2 | 1 | 0 |
| 3 | 1 | 3 | 0 | 3 | 0 | 0 | 0 |

Episodes 0/2 contain useful independently checked composite attempts, but each
canonical rule appears only once and fails the registered repeated-support gate.
Episodes 1/3 have no essential composite before that gate: every attempt is redundant.
It would be incorrect to attribute all four episodes solely to the multiplicity filter.

Each arm checks 32 training answers and 16 development baselines per episode.
All complete. Across 128 training inputs: 27 ENTAILED, 23 CONTRADICTED,
74 UNKNOWN and four INCONSISTENT; individual predicate emptiness remains allowed.
The mining receipts say NO_REPEATED_RULE; all candidate pools, development trial
arrays, ranking arrays and selected libraries are empty. The selector consequently
returns NO_METHOD_ACQUIRED, not NO_DEVELOPMENT_BENEFIT.
All eight A reports have CHECKED, empty methods, zero prior/current uses and positive
persist spans. Empty-library admission and cold validation therefore completed.

## Three causal levels

1. **Visibility:** acquire reads only checked query-obligation unsat certificates
   from consistent training tasks whose proved conclusion is universal. It requires
   a proper two-premise subcover; two-premise full tasks cannot donate their whole proof.
   Of 124 consistent inputs, 28 branches reach the universal-obligation gate.
   Eleven lose the proper-subcover condition and six have fewer than two cover members.
   Only 11 branches remain, producing the 21 attempts in the table.
2. **Representation and normalization:** each attempted fragment is the original
   two statements plus original query/negation, alpha-renamed and premise-sorted.
   The independent universal checker rejects 13 redundant fragments and five false
   subcover implications. It accepts three structurally different essential fragments.
3. **Acquisition criterion:** groups require at least two distinct semantic training
   supports. The three accepted groups are singletons, leaving zero candidates for
   development. No positive/negative candidate utility was measured; zero trials
   cannot establish that learned methods would be useless.

The >=2 requirement is this learner's registered discovery/admission criterion,
not a logical necessity for universal soundness. One independently proved discovery
can be sound. Keep >=2 unchanged in the first revival to isolate representation.
Utility and causal fresh use require their own evidence; multiplicity supplies neither.

## What the present abstraction does and does not cover

Predicate renaming and premise order already normalize. Semantic support identity
enumerates all nonempty worlds modulo renaming, so aliases cannot count twice.
Training expressions are atomic: missing normalization of input Boolean groups is
not an observed cause here. No renaming-only fix explains these empty pools.

Signed-literal normalization is still relevant to the dependency representation:
every(A,B) is the clause not-A or B; no(A,B) is not-A or not-B.
It exposes symmetry, repeated literals and shared proof steps without changing meaning.
The three accepted flat fragments have different dependency/equality structures;
literal sorting alone does not make them the same original fragment.

For example, episode 0 training rows 17 and 29 both use a positive/negative pivot B.
Row 17 resolves (not-A or B) with (not-A or not-B) to not-A, then weakens to
the checked query not-A or not-C. Row 29 resolves (not-A or B) with
(not-B or not-C) directly to not-A or not-C.
Their flat queried fragments differ, but their intermediate dependency step recurs.
This is a source/record-backed explanation of a candidate abstraction, not a measured
success of a new learner. Episode 2 row 13 has another unit-clause version.

## One minimal revival and falsifying developmental test

First add exact signed-clause normalization and dependency-preserving pivot
parameterization over the existing checked training certificates. Extract only
actual two-premise dependency steps from proper original covers; retain task digest,
branch, cover, normalization mapping, pivot, residual clauses and conclusion linkage.
Canonicalize the observed pivot/residual roles; do not inject a chosen target rule.
A small checkable intermediate-step record is needed: today's cover indices alone
cannot authenticate an abstracted intermediate conclusion different from the query.
A general anti-unification framework or another prover is unnecessary for this test.

Independently validate every normalization, original dependency and lifted universal
schema, including essentiality and Boolean substitution. Keep >=2 distinct original
semantic supports. Never group all valid rule implications by their all-true tables:
that would erase which premises and conclusion the learned method actually relates.
The normalizer and compiler are supplied symbolic machinery; this is not evidence
of inventing resolution. Acquisition is the trace-derived template and checked support
binding, followed by the unchanged development selector. Both adaptive arms share it.

One bounded authored control should replay checked training donors with distinct
semantic tasks but differing raw fragments, alongside alpha-only duplicates,
singleton donors, polarity/cover tampering and redundant-premise controls.
Predict a repeated dependency candidate for the genuine pair, none for aliases or
singletons, and refusal of invalid proofs; disabling the donor reproduces the old pool.
Then apply the frozen donor uniformly to all permitted training data and assess only
the existing development rows, keeping every rejection, match, counter and cost.
No guaranteed positive is asserted: unchanged empty pools or no development benefit
falsify the proposed improvement at their respective stages.
Runtime application must preserve checked normalization/binding, not merely claim
that the existing structural matcher already recognizes the compiled representation.

Freeze donor/selection before any successor final evaluation. Do not inspect or tune
against original final task bodies, answers or annotations. A future evaluation must
retain its honest held-out status and separate run authority; no seed is chosen here.
No scientific rerun, new proof search, source edit or broad test was performed here.

## Exact evidence and source bindings

All paths are under /home/billy/orion-director-work/20260907/.
unary-assay-acquisition-diagnosis-v1/FACTS.json SHA256:
37c41f6e13a44a628617651550a47f56f04341e661a8d682f8f0b5d02d891f19.
It binds all 48 A raw/request/process/report files, 14 frozen source/policy files,
per-arm gate counts and matched input/answer/acquisition/ranking/library identities.
Both arms have byte-identical canonical acquisition receipts per episode, not merely
the same empty-library digest. Current source is commit 6465c982ee9c17fbbad0a3484da36e06ae807bdc.
Sources: unary_rule_acquire.py (gates/subcovers/support threshold);
unary_rule_identity.py (alpha rules versus semantic support identity);
unary_rule_check.py (validity/essentiality); unary_method_selection*.py
(training/development/decision); unary_method_selected.py and unary_parent_store.py
(admission). Exact source copies and complete SHA256 bindings accompany this note.
