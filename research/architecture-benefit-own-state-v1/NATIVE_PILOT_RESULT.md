# Native pilot result — a real attribution control, not an architecture win

## Bound execution

Code head: `960be1e205ad5c67a60fc63b3859ec30278b0efa` (PR163).
Workflow: `Architecture benefit own-state`, run `34263462162`, job `102186883079`.
Artifact ID: `10070859161`, name `architecture-benefit-own-state`.
Artifact ZIP SHA256: `b729a7f2006d4635cd6f830251b87da69b3e65123e813a58c410454c355480b6`.
Raw native.json SHA256: `e3ede4f81e8cf887e77d12f9ac1138b4a8f25deb3eeaf0e11fe45b9bf12f58b4`.

The downloaded archive hash was recomputed and matched GitHub's artifact digest.
Its three files are native.json, tests.txt and tests-optimized.txt. The two test
runs each passed all 27 controls. The native pilot completed nine child processes,
all protected output projections matched, and both learned arms had identical
program/method/search-slot traces across all three repetitions. Source custody
and artifact upload succeeded. These statements qualify the code head above,
not every future edit of this branch.

## All measured cells

`native-pilot-rows.csv` preserves all nine aggregate rows, without selection.
Each repetition executes the same exposed 24-task tape in a different arm order.
These are timing repetitions, not three fresh independently sampled lifetimes.

| Arm | Query search slots | All search slots including training/validation | Median whole-child wall seconds | Final serialized bytes |
|---|---:|---:|---:|---:|
| Primitive search + ordinary persistence | 3709 | 3779 | 0.526324388 | 10794 |
| Ordinary persisted fragment learner | 6069 | 6245 | 0.542502475 | 13958 |
| Native OCM fragment/KSO path | 6069 | 6245 | 0.823196595 | 223806 |

Search counts and final serialized sizes are identical across repetitions. Median
whole-child CPU seconds were 0.507074, 0.520412 and 0.770591 respectively. Raw
floating observations are retained in the CSV rather than claimed exact rationals.

For the first 16 queries, when the library is live, primitive search used 2361
slots and each learned arm 4721. After support withdrawal at query 17, all three
arms used 1348 slots on the final eight queries. No outcome was used to select the
24 future task identities. The two training and two validation problems are
previously exposed demonstrations; they are not newly protected evaluation data.

## What follows

1. The existing library's two selected validation successes did not translate
   into aggregate search savings on this broader exposed task slice. Here both
   learned arms use 1.6363 times the query slots and 1.6526 times the total search
   slots of primitive search. This is a search-utility failure on this tape,
   not a theorem that endogenous library learning cannot help.
2. Transplanting the identical native miner/solver into ordinary persistence
   preserves the learned traces exactly. The search effect is attributable to
   the shared mechanism, not to the OCM architectural label.
3. The native OCM path took about 1.5174 times the ordinary learned arm's median
   whole-child wall time here. This is NOT a fair full-architecture loss claim:
   OCM performs additional provenance/admission/lifecycle work, while the ordinary
   parent has only a restricted single-writer snapshot contract. Qualification
   of an equally protected parent is still required. The extra cost is measured;
   how much is necessary versus avoidable has not been profiled or proved.
4. Timing includes process startup, common imports and pilot task construction.
   Bytes are final serialized footprint, not write traffic. Peak RSS is separately
   reported, not added across events. No significance test is applied to these
   repeated copies of one exposed tape.

Overall status remains `ARCHITECTURE_NET_BENEFIT_NOT_ESTABLISHED`.
The executable terminal is `NATIVE_COMPONENT_ATTRIBUTION_CONTROL_COMPLETE`.
The conditional mathematical theorems remain valid; this run does not instantiate
a positive whole-architecture cost certificate.

## Next shared gate with PR161

Do not respond to this negative by selecting only profitable queries, deleting
validation/discovery costs, or training a router on this tape. Preserve it as a
negative development control. The next implementation needs:

- a stronger conventional abstraction-discovery parent and a utility model that
  predicts actual future search savings, not only source-program compression;
- a full-contract persistent parent with the same exact checking, support,
  invalidation and recovery obligations as the native OCM method lane;
- profiling and source-derived bounds that separate necessary semantic work from
  avoidable repeated bookkeeping, before a concrete relative-cost proof;
- independently frozen task families and complete-lifetime sampling for any
  fresh expected-benefit evidence gate.

Existing library-learning and incremental-computation literature are donor
mechanisms, not opponents to be weakened. Improving OCM by adopting them is
consistent with an architecture claim; proving architectural uniqueness is not
required. PR154's non-test checker census and PR161's graph bridge remain separate
compatible work, not altered by this pilot.
