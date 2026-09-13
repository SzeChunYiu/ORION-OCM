# Strategic theory of mind — TOM-1–3 (checklist item 16)

Status: **THEOREM + EXACT FINITE WITNESSES. Admissibility claim** (DU-1 standing
rule: what is forced/attainable under the declared interface, not what neutral
search reaches).
Date: 2026-09-14. Scope: finite deterministic 2-player games, exact Fractions.

Item-16 gap map: "no derivation that other adaptive agents force *models* of
goals/beliefs/intentions/reliability" → TOM-1; "no recursive belief" → TOM-2;
"no partner-reliability result" → TOM-3. **Item 16 is POSITIVE at finite-game
scope on all three.**

## TOM-1 — adaptive opponents force opponent models

Two-round game, actions `{0=C, 1=D}`. The opponent plays `1` in round 1, then in
round 2 either **copies** the agent's round-1 action (copycat: goal = coordinate)
or **flips** it (contrarian: goal = anti-coordinate). The agent scores matches
with the opponent's current action each round.

The two opponents open identically in round 1 (`opponent_first_move` returns `D`
for both by construction), so no passive round-1 observation distinguishes them
— yet the optimal round-2 replies are opposite (`a1` vs `1−a1`).

Machine-checked over all 8 effective deterministic policies:

- per-opponent optimum is 2/2 (attained, e.g. `(a1=1, f(1)=1)` vs copycat);
- **no single policy attains 2 against both** (best-vs-copycat gets 1 vs
  contrarian and vice versa); max-min over opponent type is 1 < 2;
- with one opponent-type bit (a model of the opponent's response function,
  i.e. of their goal), 2 is attained against both.

Therefore an agent optimal against both adaptive opponents must carry a state
distinction that tracks the opponent's response function. That distinction *is*
the opponent model: goals (coordinate vs anti-coordinate) → response function →
required reply. A fixed mapping from own history alone cannot be optimal for
both. This is GG41 (strategic refinement) made necessary rather than merely
possible: the refined quotient cell is load-bearing for the payoff.

## TOM-2 — recursive belief with exact closure depth

Finite beauty contest on `{0,…,5}`: score `−|n − 2m/3|` against opponent pick
`m`. Naive anchor `L0 = 5`; `L_{k+1} = BR(L_k)` with ties to the smaller pick.

Machine-checked best-response chain: `5 → 3 → 2 → 1 → 1`.

- each deeper level strictly beats its parent against the parent
  (`−1/3` vs `−5/3`; `0` vs `−1`; `−1/3` vs `−2/3`);
- `BR(1) = 1`: depth 3 reaches a fixed point; `L4 = L3`, deeper recursion adds
  nothing — no infinite regress at finite scope;
- at the fixed point the level is its own best reply (`−1/3`, unbeatable vs `L3`).

So recursive belief is *forced* (shallower loses to deeper) and *bounded* (exact
closure depth 3 here). Belief depth is a GMI developmental quantity with a
termination certificate, not an open hierarchy.

## TOM-3 — partner reliability

Two-agent team, shared obligation "play `(C,C)`", team-loss matrix (agent-1 view):
`(C,C)=0, (C,D)=3, (D,C)=1, (D,D)=2`. Partner type: reliable (plays C) or
unreliable (plays D).

Machine-checked:

- both `(C,C)` and `(D,D)` have non-positive unilateral regret for both agents —
  both are Nash. **Regret coordinates alone do not select reliability.**
  Reliability = playing one's part of the *declared team-optimal profile*, so
  the shared team optimum must be part of the declared obligation.
- agent 1 without a signal, minimax: `C → worst 3`, `D → worst 2`, plays `D`;
  on the reliable branch the team then scores 2 instead of the attainable 0.
- with a 1-bit reliability probe (cost `c`): play `C` iff reliable. Reliable
  branch: `0 + c` against unattended `1`. Probe pays on the reliable branch
  exactly when `c < 1`. (On the unreliable branch both play `D`; the probe
  changes nothing there and costs `c` — stated, not hidden.)

Trust is therefore derived, not assumed: the value of reliability information is
an exact number (`1` on the reliable branch here), and the probe cost is charged
against it like any acquisition (cf. item 12's stop-probing law).

## Parents and what is new

Level-k / cognitive hierarchy (Stahl; Camerer–Ho–Chong), the beauty contest
(Nagel), and the stag hunt (Skyrms) are mature parents and keep first refusal on
the game forms. New here: the opponent-type indistinguishability + no-joint-
optimum forcing argument (TOM-1), the exact closure-depth certificate for belief
recursion (TOM-2), and the regret-insufficiency + exact probe-value statement
for reliability (TOM-3) — each typed as GMI quotient/state/acquisition objects
with machine-checked witnesses. No new equilibrium concept is claimed.

## Falsifier

Every equality is an assertion in `test_strategic_tom_v1.py`. Refutation = a
miscount in the game tables, settled by re-running the file. A second
independent implementation of the three evaluators disagreeing would also count.

## Claim ceiling

Finite deterministic 2-player games, exact scope only. No mixed-equilibrium
selection, no infinite-horizon reputation, no learned opponent models, no
finite-sample belief estimation. The teaching-incentive limit (population pays,
sender loses — item 16 follow-up) is NOT closed here: TOM-3 prices reliability
information, not sender incentives.

Files: [model](strategic_tom_v1.py) → [15 controls](test_strategic_tom_v1.py) →
[receipt](TOM_RECEIPT_V1.json: 15/15 on billy-old py3.14 + laptop-billy py3.8,
normal + optimized).
