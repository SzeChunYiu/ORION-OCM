# Experiment ledger — descendant-edge derivation over the #833 gap universe

Schema: `GMI_EXPERIMENT_LEDGER_V1`. Package `gmi-833-aa1-gap-graph-v1`, issue
#839. Experiment: derive gap-to-gap descendant edges, closure states and
promotion blocks over the 1140 records of `GAP_GRAPH_V2.json` and the registers
pinned in `FREEZE_V1.md` §3, and measure how many records gain descendants and
how many closures are blocked. The format and the five required ledgers are
owned by `gmi-833-aa-ledger-gate-v1` (LG-4); this is one more instance of it.

**Leakage.** The rules R1–R3, the closure rule and the materiality inputs were
fixed in `FREEZE_V1.md`, committed alone before any builder existed. The
scoping counts that freeze reports (46 R1 edges, 16 R2 edges, 154 closures, 6
blocked by corpus rules, 90 cross-package B1 closures) were measured read-only
**before** the freeze and are labelled `SCOPING_OBSERVED`, not presented as
blind predictions; the result records carry that label in `prior_disclosure`.
The one outcome the freeze could not have seen is the 136-closure block, which
depends on the extracted gaps; it is labelled `POST_OUTCOME`. No rule was
changed after a number was read.

**Search space.** Fixed and total: all 1140 records, all 857 DUPID
adjudications, all 202 register-delta records, all 22553 census objects for
declaration lookup, all 9 flagship results. The fixture spaces are enumerated
completely where finite (4608 digraphs, 13824 gap-promotion, 1000 flagship and
3072 parent cases) and sampled with declared seeds elsewhere (300 graphs, seed
8390839; 200 loop mutations, seed 8390840). Nothing is tuned: there is no
parameter to choose.

**Cost model.** One pass over about 30 MB of pinned JSON; the build takes about
two seconds on one core; the full test module, including both exhaustive and
randomized differentials, runs in well under a minute per interpreter mode. No
network, no third-party dependency.

**Evaluation.** Every reported quantity is an integer, computed by two routes
that share no code (route B re-derives R2 by fixed-point iteration over the
register delta instead of reading the parent's `descendants` field, finds
cycles by Kosaraju instead of Tarjan, and grades materiality by lookup table).
Agreement is by set equality on edge sets, closure sets, repair records, claim
cones and finding lists, not by count equality. The committed graph must equal
a fresh build byte for byte.

**Sampling bias.** The universe is enumerated, not sampled, so the bias is
definitional and disclosed. The descendant relation sees only **stated**
dependencies: 30 child objects carry 113 resolved edges, so most records are
isolated for want of a stated edge, not because they are independent
(`GAP-AD-AA1-SPARSITY`). Closure is awarded only where a rule predicate can be
re-derived mechanically (B1, B3), which favours byte-level duplicates over
semantic ones; the 283 `FIN2UNIV` verdicts rest on single-lane reading and are
left open rather than counted.
