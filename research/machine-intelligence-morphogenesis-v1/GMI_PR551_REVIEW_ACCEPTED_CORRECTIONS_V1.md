# Corrections accepted from the pinned review of PR #551

Date: 2026-09-13. Source: `research/gmi-grand-unification-v1/PR551_SCIENTIFIC_REVIEW_7E3F68AE_V1.md`
(grand-unification lane, PR #556). Every point below is **accepted**, and each factual claim was
re-verified in this checkout rather than taken on trust. Nothing here is disputed.

## 1. The prospectivity claim for X1/X2 is RETRACTED

The `RV-377-210` adjudication presented the registration as made "before the other lane's V4 timing
exists" and used commit times as execution times. Verified independently with `gh run view`:

| record | time (UTC) |
|---|---|
| V4 run `34749100254` started | 09:11:55 |
| V4 run `34749100254` finished, conclusion success | **09:13:57** |
| registration commit `d83d789f` authored and committed | **09:23:06** |

**The V4 timing data existed nine minutes before the registration was committed.** The claim as written
is false. Further, the V5 result packets carry **no execution timestamp of any kind** — checked, the only
time-like fields are `protected_timing_measurement_executed` booleans — so their commit time cannot
establish when they ran, and my "104 minutes after" line inferred execution from publication.

What survives: X1 and X2 were written without my having looked at any timing or opcode measurement, and
the reasoning used only the candidates' structure. But that is unverifiable from the record, which is
precisely the review's point. **Correct status: a hypothesis whose observation-time blindness is
unverified, not a pre-data prediction.** The outcome table (X1 held, X2 held on every coordinate) stands
as a *consistency* result between two instruments; the epistemic upgrade I claimed from prospectivity
does not.

## 2. Z6 is not a pre-data prediction either

Their witness recovery (commit `f91c78ed`, 12:32:17 UTC; PR #552 public at 12:33:09) already identified
`KVSTORE`, `INSERT` and `NEAREST` alongside `DENSE` in a pruned graph. My Z6 commit is `7e3f68ae` at
13:21:57 UTC — **49 minutes later**. The answer existed publicly before the hypothesis was registered.
Same correct status as above: a later hypothesis with unverified blindness. It is also, on their
evidence, *already supported* — which makes it a retrodiction, not a prediction.

## 3. Deletion resistance does not establish semantic necessity

I wrote that a node survives atrophy "only if deleting it drops the machine below the floor", and read a
retained DENSE node as load-bearing. The pinned routine is a **canonical greedy sequence of typed
single-node deletions, capped at 24 rounds**, which skips type-check failures and never searches
rewirings or semantic equivalents. Survival therefore means *not removable by the allowed local moves
within the cap*, which is weaker than necessary.

Their constructive counter-control goes further and is the decisive part: replacing the `DENSE` output
with a zero vector **preserves query values, abstention and ordered common stores** — the dense numeric
cell has no active numeric consumer — and the presence-based descriptor then reads `KVSTORE`. So a
machine this lane would label a coefficient recovery can be behaviourally a memory machine with an inert
dense cell.

This is stronger than the hybrid caveat I registered as Z6. **The honest reading of every "atrophied
carrier DENSE" result in this lane is syntactic presence plus deletion resistance, reported separately
from any claim of coefficient use or of a hybrid learning mechanism.** `Z1`–`Z3` inherit this and are
re-scoped accordingly: they are claims about a presence-based descriptor, not about coefficient machines.

## 4. The parent-sufficiency terminal is scoped to its tested comparator

I wrote that a second twin hit would mean "any developed archive suffices". It would not. A 2/3 result
concerns **this one registered twin population**, these seeds, this target, this search law and this
resource allowance. It cannot quantify over every developed archive, and it does not establish matched
OOPS or PowerPlay sufficiency. If `F-Z3` trips, the terminal is reported with exactly that scope.

## 5. The tenth arm is now bound

The `SAME|TWIN|S1` hit was reported without its receipt. The ten completed arm receipts are now committed
under `evidence/b6-arms-20260913/` with a `MANIFEST.json` binding sha256 over the exact bytes, each
receipt's own `receipt_sha256`, and its `source_receipt_sha256`. `SAME|TWIN|S1` is
`14944fe3da89e903…`, `dense_found = true`.

---

Recorded as a standalone document rather than folded into the freezes, so that the corrections are as
findable as the claims they correct. The review states it reran no experiment and mutated no frozen
registration; neither does this.
