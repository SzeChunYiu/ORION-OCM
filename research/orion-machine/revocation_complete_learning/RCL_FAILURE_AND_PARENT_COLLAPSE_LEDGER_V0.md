# RCL failure and parent-collapse ledger V0

**Date:** 2026-09-03  
**Programme:** ORION-V2 #194  
**Execution:** ORION-V2 #197  
**Status:** `APPEND_ONLY__NO_NOVELTY_AUTHORITY`

| ID | Killed or threatened claim | Disposition | Strongest reason | Reopen condition |
|---|---|---|---|---|
| RCL-F01 | “Computational traces helping learning is new.” | `PARENT_OWNED` | ICLR 2026 computational-trace identification already proves major learnability changes and treats corrupted traces. | A theorem concerns future revocation completeness beyond static trace identification. |
| RCL-F02 | “Learning the warrant antichain from liveness queries is a new learning problem.” | `PARENT_OWNED` | The object is a monotone DNF/hidden hypergraph; exact membership-query learning has established lower and upper bounds. | The result jointly learns reusable operator semantics and warrant/authority state and cannot be decomposed at equal resources. |
| RCL-F03 | “One valid proof is enough for future retention.” | `REFUTED` | RCL-2/RCL-2b construct a revocation that invalidates the emitted proof while an omitted alternative remains live. | The proof bundle carries an explicit exhaustive/completeness guarantee or a complete on-demand prover is charged. |
| RCL-F04 | “All alternative warrants can be kept essentially for free.” | `REFUTED_AS_GENERAL_CLAIM` | RCL-1b gives a class with one common current proof but an exponential zero-query future-information requirement. | Restrict the warrant class or revocation family, or allow approximation/query/abstention and state the resulting frontier. |
| RCL-F05 | “Selective invalidation over known dependencies is new.” | `PARENT_OWNED` | Provenance semirings, causal justifications, TMS/ATMS, Datalog maintenance and self-adjusting computation own alternative derivations and affected-region updates. | The dependency/warrant object is itself learned and a joint theorem survives the parent product. |
| RCL-F06 | “Exact future deletion requiring memory is new.” | `PARENT_OWNED` | Ticketed, central-space and system-aware unlearning already establish memory/deletion/update tradeoffs. | Revocation cannot be reduced at equal cost to an explicitly supplied example forget set. |
| RCL-F07 | “Alternate-path authority revocation is new.” | `PARENT_OWNED` | VERA preserves agents with independent authorizing paths in a supplied delegation DAG. | Learned procedural warrants plus evidence/checker/scope changes yield a theorem not obtainable by VERA plus ordinary learning. |
| RCL-F08 | “Provenance-to-forget-set mapping is new.” | `PARENT_OWNED` | OriginBlame propagates record/token provenance and resolves contributor revocation into precise forget sets. | The hard part is whether a derived operator remains independently warranted, not locating records. |
| RCL-F09 | “The result is a post-Transformer architecture separation.” | `NOT_SUPPORTED` | A recurrent/looped Transformer with identical memory, proof, query and update interfaces can implement the finite algorithms. | Prove an unavoidable resource obstruction under exact parity. |
| RCL-F10 | “The elementary RCL theorem pack itself establishes external novelty.” | `BLOCKED` | The proofs use antichain, counting and indistinguishability arguments and have close provenance/unlearning/hypergraph parents. | Full theorem-level parent reconstruction, three clean post-addition searches and independent hostile review. |
| RCL-F11 | “Revocation-Shattering Dimension is automatically a new complexity measure.” | `BLOCKED_HIGH_COLLISION` | Learning–unlearning storage already has eluder-dimension lower bounds and star-number/ticketed upper bounds; conditional signature counts also resemble standard shattering and communication notions. | Prove a nontrivial relation or separation from eluder/star/teaching/query dimensions, or use RSD only as notation. |

## Current surviving object

```text
jointly learn:
    reusable operator semantics
    + revocable warrant/provenance structure
from:
    independently checked execution experience

then support:
    evidence / checker-version / scope / authority changes

while measuring:
    stored counterfactual-warrant information
    + post-revocation proof/data queries
    + update/recourse
    + collateral skill loss
   + false/stale authority
   + abstention
```

## Required kill test

The candidate dies if the strongest faithful composition

```text
trace learning
+ monotone-DNF/hypergraph learning
+ ticketed/exact unlearning
+ provenance/TMS/self-adjusting computation

proof-carrying execution
+VERA/OriginBlame
+Recurrent Transformer implementation
```

reconstructs the final theorem with the same information and whole-system resources.

## Custody note — binding re-freeze 2026-09-04

The content binding recorded for this artifact no longer matches its bytes. The
binding is re-taken over the current bytes. The prior binding is retained below
and, alongside the new one, in every receipt that carries it.

| | bytes | sha256 |
|---|---|---|
| binding recorded 2026-09-03 in `4655495` | 4751 | `466e6da9d056e815c0c58df5daa2c12f657c106ec4f6d3dd053559795a136bb6` |
| bytes actually committed, and re-bound here | 4746 | `12ca96d8e8da0864802087e276b4e2d85ebae87d88c2e7329cb0f4b9e30ca23c` |

**This records a drift; it does not bless one.** Nothing above this note was
altered to make the hashes agree, and this note grants no scientific authority.

### What is established

This artifact and both receipts that bind it were created together in a single
commit, `4655495`, which is all-insertions across 18 files.

Three independent searches agree, and the scope of each is stated rather than
assumed. (i) `git log --all --full-history` on this path returns only `4655495`
and the later merge `7015cdb`; the same query on `RCL_AI_SESSION_HANDOFF_V0.md`
returns three commits, so the short answer is not an artefact of history
simplification. (ii) No blob of 4751 bytes exists in the local object store:
6,765 objects were scanned and the 4,746-byte blob was found as the control.
The local clone is shallow, so that scan is exhaustive for the retained history
rather than for everything the remote holds. (iii) The GitHub commits API for
this path on this branch closes that gap for the branch the artifact lives on,
and returns the same single commit. Neither working checkout of this branch on
the authoring machine holds a differing copy.

The recorded binding was therefore taken over a pre-commit draft that was never
pushed: **this file has never existed in version control at its recorded
length.** The lane commits `0b4641e`, `24d5a11` and `313790b`, which restored
other artifacts in this lane, never touched this path.

### What was excluded

Six reconstruction sweeps failed to produce bytes hashing to the recorded value.
Each carried a positive control that had to fire, and did.

| sweep | positive control | result |
|---|---|---|
| n-gram, 3,165 distinct 5-grams x 4,747 positions | recovered `end` | no contiguous run occurring elsewhere in the file |
| inflection-aware anomaly scan | flagged `indepent` | no corrupted word; all 22 flagged tokens legitimate |
| space multiset, 16,108,764 multisets | recovered a synthetic 5-space indentation loss | not 5 spaces at indentation or `+` sites |
| structured whitespace, 113 combinations over 8 enumerated sites | exhaustive over the enumerated sites | no combination reproduces the binding |
| typographic/encoding, hyphen to en/em dash pairs x every insertion position, 33.6M candidates | recovered a synthetic two-dash-plus-space original | no encoding-width restoration reproduces the binding |
| whole-word omission, 5,007 four-letter words x every word boundary | recovered a synthetic omitted word | no single omitted word reproduces the binding |

The first three were run by the preceding custody lane; the last three were run
in this one.

The visible whitespace irregularities — lines 39 and 40 carry a three-space
indent where lines 35 to 38 carry four, and `+VERA` and `+Recurrent` lack the
space their siblings carry — sum to four bytes, not five, and no completion of
them to five reproduces the recorded hash. The difference is therefore not a
single minimal edit of any shape tested above.

### What remains open

The bytes the recorded binding was taken over are not recoverable from any
source reachable from this repository. Whether they differed from the current
bytes in substance or only in transport formatting cannot be determined. No
claim, disposition, strongest reason or reopen condition in the table above is
changed by this note.
