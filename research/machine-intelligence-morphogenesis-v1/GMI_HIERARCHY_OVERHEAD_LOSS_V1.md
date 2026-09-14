# When hierarchical abstraction loses to overhead — I3 (#602)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS**. Closes the last box of I3. The other four are in
`GMI_HIERARCHICAL_CHUNKING_THEOREM_V1.md` (action chunking, macro formation, the depth stopping law) and
`GMI_SUBGOAL_DERIVATION_V1.md` (reusable subgoal structures).

## 1. Why the earlier sweep could not answer this

The hierarchy sweep showed a second level contributing 0 % at high storage price. But **"adds nothing" is
not "loses"**: an optimiser free to choose the empty chunk set can never do worse than flat, so optimising
over subsets **cannot exhibit a loss by construction.** Answering I3's box needs a different question.

Two questions instead:

* at what price does the **optimal** structure become flat?
* what does a **committed** hierarchy — one already built and paid for — cost against flat at that price?

## 2. Result

| storage price | flat | optimal chunk set | optimal cost | committed hierarchy | committed loses? |
|---:|---:|---|---:|---:|---|
| 1 | 72 | abc, abd, abe | 27 | 27 | no |
| 6 | 72 | abc, abd, abe | 42 | 42 | no |
| 10 | 72 | **abc** | 54 | 54 | no |
| 15 | 72 | abc | 59 | 69 | no |
| **20** | 72 | abc | 64 | **84** | **yes** |
| **30** | 72 | **(none)** | 72 | 114 | yes |

## 3. The two thresholds are different, and the order is the point

> **A committed hierarchy becomes a liability at price 20. Abstraction stops paying altogether only at
> price 30.**

The order matters and is easy to get backwards. Between 20 and 30 there is a regime where the **optimal
structure still benefits from chunking** (one chunk, 64 against flat's 72) while an **over-committed
three-chunk hierarchy is already worse than flat** (84 against 72). In that band the right response is to
**prune**, not to abandon.

And the optimum degrades **gracefully rather than falling off a cliff**: three chunks at low price, one
chunk from 10 to 20, none at 30. Each chunk drops out as it stops clearing the PVR-3 threshold, so
hierarchy thins before it disappears.

> **The loss a committed hierarchy suffers is exactly the storage paid for chunks that no longer clear the
> reuse threshold.** Overhead does not make abstraction wrong; it makes *unpruned* abstraction wrong.

## 4. A correction recorded

The witness script printed a summary line asserting the opposite order — that abstraction stops paying
before it starts hurting. **The data say the reverse**, and the script's gloss was wrong while its numbers
were right. Recorded because a one-line summary is exactly the artifact most likely to be quoted without
the table beneath it.

## 5. Scope

**Derived:** the two distinct thresholds, their order, graceful degradation of the optimum, and the
identity of the committed hierarchy's loss with wasted storage.

**Assumptions:** uniform storage price across chunks, a fixed task mix, and a committed set chosen at low
price. A hierarchy committed under a *different* mix would fail at a different threshold — which is the
same statement, since the wasted storage is whatever no longer clears the threshold.

**Falsifier:** a price at which the committed hierarchy beats flat while the optimum is already flat, which
would invert the two thresholds.

## 6. I3 status — all five boxes

| box | where |
|---|---|
| action chunking | chunking theorem — PVR-3 on a retained sub-quotient |
| cognitive macro formation | same, for reasoning sequences |
| hierarchy depth stopping law | chunking theorem — levels self-limit because retention lowers `C` and raises the next bar |
| reusable subgoal structures | subgoal derivation — entry states, locally realised |
| **when abstraction loses to overhead** | **here** |
