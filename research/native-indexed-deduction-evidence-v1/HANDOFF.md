# Indexed weighted deduction — completed, mixed cost result

The indexed scheduler preserves the reference's finite proof costs and native
proof validity. Its observed scheduling cost increased on the positive target and
decreased on the bounded negative target. It is not an unconditional replacement
for the layered reference, and it does not establish an end-to-end speedup.

This is the frozen exposed authored engineering comparison. It changed only the
scheduler. Prior acquisition, the learned method, typed compiler, full ordinary
library, bank, target and native authority remained unchanged. No OCM runtime or
protected task was changed, and producer A was not rerun.

## Fixed comparison

| Cell | Minimum tree cost, both | Layered scheduler s | Indexed scheduler s | Layered cold B s | Indexed cold B s |
|---|---:|---:|---:|---:|---:|
| Positive, ordinary | 3 | 0.294217 | 0.303692 | 4.576359 | 4.579266 |
| Positive, I enabled | 2 | 0.262869 | 0.292199 | 4.529286 | 4.578557 |
| False, ordinary | No proof within 8 | 0.446021 | 0.339729 | 4.779053 | 4.528530 |
| False, I enabled | No proof within 8 | 0.423212 | 0.346806 | 4.629090 | 4.628751 |

Each scheduler span includes complete ordering and, for the indexed arm, incidence
construction and heap/settlement work. Separate internal setup/settlement times were
not recorded. Do not derive them from counters or attribute the observed positive
slowdown specifically to index construction or heap operations.

Every B independently paid for cold restoration and ordinary compilation. Compiler
spans ranged from 3.784639 to 3.924733 seconds and dominated the call. These are single
fixed-order observations, not reliable estimates of repeatable timing improvements.
The mixed result and the full cold cost remain authoritative; no retuned rerun was made.

All eight arms generated the same 69,219 ordinary instances from all 4,191 assertion
contracts and the same 255-formula/15-class bank. Instance digest:
`a7ef326f24a0ceb8507d0ff86b0007dc450aedd886ffad44ef3955280f2e7d0a`.
The enabled arms added the same six atomic-bijection I instances. I was actually
used in both positive enabled derivations. No false-target proof was returned.
The `used_ids` field records methods in the returned proof, not every intermediate
proposal: the false indexed enabled arm still reached two macro candidate actions.

## Exact authority and cost objective

All four successful arms emitted the same 21-label normal proof in this run. Each
separate native checker accepted all 4,095 old proofs plus the exact new target,
with the same 96 trusted assertions. Equality of proof bytes was observed, not a
qualification prerequisite: another equally minimal proof would need its own check.
The common emitted proof contains three semantic and three syntax applications,
eleven floating labels and four logical-hypothesis occurrences.

Supplied facts cost zero; each rule or macro adds one to the sum of ordered premise
costs, preserving repeated occurrences. This minimizes abstract proof-tree actions,
not expanded native proof size, shared-DAG cost or running time. Strictly positive
rule cost makes every selected antecedent cheaper than its head, permitting exact
Knuth/Nederhof finalization even with positive cycles. Empty rules are seeded at one;
unseeded cycles remain unreachable. Parallel actions preserve their identities.

The false results mean no proof within the finite bank and cost eight. They do not
establish unrestricted absence. Separate prior authored semantics supplies the
false target's nonentailment evidence.

## Work and materialization remain visible

| Cell | Layered action attempts | Indexed incidence visits | Indexed ready actions | Indexed settled facts |
|---|---:|---:|---:|---:|
| Positive, ordinary | 141,792 | 40,902 | 6,419 | 76 |
| Positive, I enabled | 72,579 | 25,133 | 2,481 | 47 |
| False, ordinary | 553,752 | 98,250 | 35,165 | 181 |
| False, I enabled | 553,800 | 98,258 | 35,167 | 181 |

These columns count different operations and cannot be treated as a common work
unit or a speedup ratio. Before those visits, each indexed arm ranked and indexed
69,219 ordinary records, plus six when I was enabled, and materialized 137,790 or
137,802 premise incidences. The reference also sorted every available action.
No repeated whole-action scan occurs in the indexed queue loop; full setup remains.

Indexed queue pushes/pops were 183/76, 142/47, 183/183 and 184/184 respectively. The two
negative cells discarded two and three stale entries. All counters, cold costs and
per-process RSS are retained in SUMMARY.json, including extra method overhead.
Peak child RSS over the lifecycle was 140,016 KiB.

## Qualification and parent assimilation

Twelve focused controls passed, including repeated premises, zero rules, parallel
actions, seeded/unseeded cycles, exact 8/9 cutoff, supplied/unreachable targets and
a late cheaper candidate with a stale queue entry. Two independently implemented
oracles — synchronous min-plus recurrence and decreasing-budget rule-tree cost
sets — agreed with both schedulers on 3,159 selected small cases.

Those cases are 351 distinct two-rule sets drawn from 27 rules using three heads and
nine explicitly listed tail templates, evaluated at three chosen seedsets and three
targets. They are exhaustive over that listed construction, not all possible tails
or scientific task families. Ten missing-API RED controls, the initial ten GREEN
controls and the final twelve GREEN controls are retained as development generations.
A stray prose heredoc marker was removed before dispatch; original contract bytes
and its initial binding remain. No experiment condition changed in that correction.

The algorithm is established weighted deduction. DONORS.md records inspected HALP,
Dyna and hypergraphs source revisions and assumptions. No donor implementation was
installed or copied into the scheduler; exact fetched sources and licenses remain
in the internal research record. This adaptation is not a new OCM algorithm.

## Measurement boundary and next decision

The eight cold search/four native-check lifecycle took 41.667922 seconds, with
39.891872 child user CPU seconds and 1.137559 system seconds. It includes its twelve
nested observers, source/input hashing and stream retention. Do not add nested spans
again. Earlier acquisition/qualification and later evidence packaging are separate.
All arms share the same post-A snapshot; this is a scheduler/method-use comparison,
not a machine-with-learning versus never-learned lifetime comparison.

Keep both qualified schedulers available for subsequent research. The remaining
observed bottleneck is cold ordinary compilation, while this study localizes the
mixed effect only to the combined scheduler stage. Any persistent index, compiled
cache or lazy construction is a separate axis with its own maintenance and exact
invalidation obligations; this record supplies no outcome for those changes.
No general speed, locality, lifetime, language, novelty or publication claim follows.

Read SUMMARY.json, PROCESS-SUMMARY.json, CONTROLS.json and SOURCES.json for exact
results and bindings. The full prefix, catalogue, source generations, requests,
process records and native proofs are retained in the internal evidence archive.
