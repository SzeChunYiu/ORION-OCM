# Author Notes — Implication Systems Studio

Self-contained authoring run, stdlib only, no network. Ten families, six
instances each, sixty instances total. Every emitter is pinned to a fixed
seed (documented in the module docstring) so `python3 emit_all.py` reproduces
`instances.jsonl` byte-identically (verified by back-to-back sha256).

## Families

### Cascade Ladders (seed 1101) — 6 instances
Braided forward chains: each rung lights the next, skip rungs jump 2–5 ahead,
dead-end spurs branch off and stop. Varies: ladder length (6–14), skip-rung
pattern, spur count/positions. Closure always reaches the top rung; min seed
is 0 (pure closure-reading family). The spurs exist to punish the assumption
that every lit atom is on the path.

### Quorum Gates (seed 1102) — 6 instances
A gate fires only when k of its n seats are lit, encoded as one rule per
k-subset. Gates feed gates (seats can be other gates). Varies: quorum size
(2–3), seat count (3–5), which seats start lit, seat prices, chaining depth.
Min seed = cheapest seat bundle that completes the top quorum; gates are
priced 99 so seeding a gate directly is always dominated.

### Toll Routes (seed 1103) — 6 instances
Parallel tolled trails to one summit, some sharing a bridge toll. Key
semantic point I learned while authoring: entering a trail lights the whole
trail (rules chain for free), so only entry tolls and shared-toll placement
decide the answer; mid-trail prices are deliberate decoys. Varies: trail
count (2–4), lengths, shared bridges, price spreads.

### Trap Vaults (seed 1104) — 6 instances
Cheap keys spring needle traps (excluded atoms) that ruin the run; safe keys
cost more, and one instance has no safe key at all. Varies: trap count, safe
route arity (single keys vs a conjunction), safe prices. Honest finding: the
no-safe-key instance is NOT impossible — the goal atom itself can be seeded
at its posted price (99). The interesting answer is the price, not feasibility.

### Guild Overlap (seed 1105) — 6 instances
Craft guilds with overlapping member rolls; each guild's crest fires from the
conjunction of its full roll, and the grand charter needs every crest plus a
bridge fee. Varies: guild count (2–4), pairwise overlap topology (chain,
triangle, star), starter members, bridge price. Shared artisans are the
lever: one seeded member counts toward every guild they belong to.

### Forkjoin Lattice (seed 1106) — 6 instances
Layered DAG; each cell joins its two ground-row neighbours from the layer
below, the apex joins the whole top row. Varies: depth (3–5), width (3–4),
how much of the ground row starts lit, single-parent shortcut wires. One
instance starts fully lit (min seed 0) as a contrast case.

### Loop Spinup (seed 1107) — 6 instances
Closed flywheel rings that idle unless seeded; one seeded arm spins the whole
ring, rings can crank rings (a two-arm conjunction), and two instances poison
an arm so that every cheap entry eventually spins the poison into the
closure — forcing the 99-priced direct seeding of the flywheel. Varies: ring
sizes (3–6), entry prices, couplings, poison placement.

### Near-Miss Keys (seed 1108) — 6 instances
Locks missing exactly one part; look-alike substitutes at different prices
complete them, and the bench holds red-herring parts that imply nothing.
Varies: which/how many parts are missing, substitute price spreads, herring
count, one-vs-two locks. One lock is already complete from base (goal
reachable, seed needed only for the other).

### Redundant Rails (seed 1109) — 6 instances
Junction boxes in series, each reachable either by throwing a whole bundle of
cheap switches (conjunction) or one costly master switch; levels chain so a
per-level bundle-vs-master decision compounds; decoy junctions feed nothing.
Varies: bundle arity (2–4), switch price, master price, decoy count, nested
levels (1–2).

### Ledger Tradeoffs (seed 1110) — 6 instances
A ledger seal needs one line covered per voucher; each voucher has a menu of
OR alternatives — single lines, two-atom pair lines, four-atom tri lines —
and one tempting omni-stamp that would cover everything but is excluded.
Varies: voucher count (2–3), menu widths, shared pair lines, omni price.

## What I found hard

- Chain semantics make "pay per step" impossible: rules propagate for free,
  so any family wanting per-step pricing must force conjunctions (pairs,
  quorums, bundles) at each purchase point. Toll Routes taught me this; the
  blurb now says entry tolls light whole trails.
- IMPOSSIBLE is hard to arrange honestly: any goal atom not in closure(base)
  can be seeded at its posted weight, so the min-seed answer degrades to
  "seed the goal itself" rather than IMPOSSIBLE unless the goal is excluded
  (which contradicts wanting it). I used price-99 goal atoms to make the
  direct route legal but dominated, and recorded the honest costs.
- The addable-atom bound (<=16) bit twice: forkjoin 5x4 and rails with two
  nested levels plus decoys both overflowed; I shrank the lattices and
  dropped decoys on nested instances.
- Intent answers are computed by my own fixpoint + brute-force subset scan
  (in families/_common.py), kept as audit_only records; a few surprised me
  (quorum_gates_03's cheapest seed s2 at 3 rather than the obvious gate
  completion), which is exactly why they are recorded and not asserted.
