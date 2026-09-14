# Message passing: rounds, carrier, and the expressiveness ceiling (B8)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/message_passing_witness.py`.
Receipt: `microscopes/results/STAGE_MESSAGE_PASSING_V1.json`.
Derived by a parallel worker. Witness and receipt md5 **independently
reproduced** on `laptop-billy` (98.7 s, exit 0) before this document was
written. Four clean-directory runs gave byte-identical receipts.

`GMI_EQUIVARIANCE_DERIVATION_V1.md` derived convolution from **translation**
symmetry. This is the same argument on a general graph — **permutation**
symmetry, with the neighbourhood replacing the window.

## The descriptor comes first, and refutes with a relabelling

Over the full `S₄` on 4 places, exhaustively: `any_marked`, `cap_dist_4`,
`marked_and_company`, `odd_dist_3`, `own_mark`, `reach_1/2/3` are equivariant.
`is_node_0` and `lowest_partner_marked` are **refuted with an exhibited
relabelling** — config `0000` under perm `1023`, and config `0010` under
`0213`.

## Rounds are read off the obligation

Over 32 768 configurations, colour classes by round:
`[2, 30, 818, 1420, 1494, 1498, 1498, 1498, 1498]`, stable from round 6.

| obligation | `own_mark` | `reach_1` | `reach_2` | `reach_3` | `odd_dist_3` |
|---|---:|---:|---:|---:|---:|
| rounds | 0 | 1 | 2 | 3 | 3 |

Hop count maps to round count 1:1 — **searched, not assumed.**

## The carrier is not the answer alphabet

This is the headline, and it refutes the obvious reading of CSR-1.

| obligation | rounds | answers | states | bits |
|---|---:|---:|---:|---:|
| `reach_3` | **3** | **2** | **2** | 1 |
| `odd_dist_3` | **3** | **2** | **3** | 2 |

The two are matched on rounds **and** on answer alphabet, and still differ in
carrier. Exhaustion over **65 536** two-state machines finds **2** that meet
`reach_3` and **0** that meet `odd_dist_3`.

> `odd_dist_3` must keep telling "not reached" from "reached at an even
> distance" — a distinction it **never reports**. CSR-1 counts distinctions
> still to be made, not answers given.

**The search has a working positive control**: `reach_3` is found. Without that,
`odd_dist_3` finding nothing would prove nothing about the world and everything
about the searcher.

## The ceiling

All 32 768 six-node graphs grouped on their stable colouring. `connected` and
`has_triangle` are **blind**; `leafy` is determined from round 2 — the matched
positive, so blindness is a property of the obligation rather than of the
method.

The pair, **found by grouping rather than chosen**:

- **A** = `C₆`, connected
- **B** = `2×C₃`, disconnected

Both have degree sequence `[2,2,2,2,2,2]`, are **non-isomorphic by exhausting
all 720 relabellings**, and are merged at **every** round 0–8 with the colouring
frozen from round 7.

Minimality: no blind pair exists for connectivity at n = 3, 4 or 5, from the
same finder that fires twice at n = 6.

## Burden, and what saturates

`traffic = rounds × 2|E| × width`, both factors taken from the measurements
above. Crossover against shipping the whole configuration once: `reach_1` at 4,
`reach_3` at 12, `odd_dist_3` at 24, `cap_dist_4` at 48 — **strictly ordered by
`rounds × bits`** = 1, 3, 6, 9.

Obligations met per round run 2,3,4,7,7,7,7,7,7 while cells spent run
0,30,848,2268,3762,5260,6758,8256,9754.

> Expressiveness saturates at round 3; the partition keeps refining to round 6;
> **the bill never stops.**

## Neutral recovery

A menu of five accesses — `SELF`, `INCIDENT_BAG`, `INCIDENT_INDEXED`,
`POPULATION_BAG`, `WHOLE_TABLE` — asserted free of *message*, *aggregat*,
*neighbour*, *gnn*, *network*, *convol*, *graph*, *passing*, *propagat*.

**All five win somewhere**, and the relational access wins 5 of 10 — never a
majority. `is_node_0` is met only by `WHOLE_TABLE`, at 327 680 cells.

## What is argued rather than measured

Recorded because the worker insisted on it.

- **"At any number of rounds" is licensed in the ceiling and *not* in the
  carrier result.** In the ceiling it is a theorem: colours only refine, the
  colouring is frozen from round 7, and the exhibited pair is measured as merged
  at every round. In the carrier result it is **not** — valid round counts form
  an intersection of eventually-periodic sets whose joint period is far beyond
  any searchable bound. The primary claim is pinned at `rounds = 3`; the sweep
  to `R ≤ 24` is reported separately and must not be read as "any".
- **The finest-state lemma is half argued.** That the colour is producible by a
  local rule is *measured* — rule tables harvested, replayed from round 0, with
  a gate that fires if one local view ever yields two next states. That *no
  r-round machine separates more than the round-r colour* is a proof by
  induction; the receipt says so verbatim
  (`"no_machine_separates_more": "ARGUED BY INDUCTION, NOT ENUMERATED"`).
- **`rounds_under_incident_bag: None` is access-specific, not unreachability.**
  `marked_and_company` is `None` there and is met by `POPULATION_BAG` for 20
  cells. That contrast is itself a result: a permutation-equivariant global
  obligation the *relational* machine cannot meet at any round, because on a
  disconnected configuration a place never learns the population.
  > Equivariance licenses a relational machine; it does not make one sufficient
  > — the same shape as the parity/combiner finding in B5.
- **The three-state lower bound is subcorpus-scoped.** The exhaustive two-state
  search runs on the 8 096 configurations of the 5-node world with max degree
  ≤ 2. Sound in the negative direction, since a full-world machine restricts to
  one of those searched; the machine it *did* find for `reach_3` is separately
  verified on the whole world.
- **A tie-break that had to be fixed.** A first version sorted by
  `(cost, access_name)`, which handed both zero-round obligations to
  `INCIDENT_BAG` alphabetically and inflated its win count to **7 of 10**. Ties
  now break toward the least-exposing access, and the tied set is reported.
  `POPULATION_BAG` and `INCIDENT_BAG` are genuinely incomparable and their
  relative order is arbitrary; nothing reported depends on it.
- **`bits = 1` for `reach_1` was briefly hardcoded** in the burden table. It now
  has a verified machine like the others, so every number in the burden section
  traces to a measurement.

Gates were validated by four mutations on billy, each tripping its intended
assertion — including making the matched positive blind, and replacing the
exhibited pair with a separating one.

**Falsifier.** Exhibit a round-based machine separating `C₆` from `2×C₃`; or a
two-state machine meeting `odd_dist_3` at three rounds; or an access that wins
nowhere in the menu.
