# D12 calibration scoring V1 — reveal + arm scores + D11 router constants

Scored by the centre (curator) after ALL five arm logs landed on main. Custody
commitments verified at scoring time (below). Source of truth: the merged arm
logs `research/heritable-search-geometry-v1/d12/arms/A{1..5}_LOG.jsonl`; every
number here is machine-derived from those files by `D12_SCORING_V1.json`
(provenance: sha of each log at scoring time recorded there).

## Custody verification (freeze HSG_D12_CALIBRATION_FREEZE.json)

- **H1** `sha256("ocm-hsg-d12-2026-09-10||" + preimage) = 2c1145da…cd10f1` —
  VERIFIED. Preimage (now revealed): `A_T05 macro-amortization threshold
  economics <-> metabolic economics: substrate channeling and enzyme saturation
  (Michaelis-Menten saturation; cost-benefit of metabolite channeling vs
  diffusion) — donor discipline: biochemical kinetics / metabolic organization`.
- **H2** `sha256("ocm-hsg-d12-2026-09-10||ANTI") = d833e2d7…210df` — VERIFIED as
  an EXISTENCE-ONLY commitment: the frozen hash covers `salt||ANTI`, NOT the H2
  content. The H2 preimage (revealed here from curator custody, never in any
  lane context): `A_T18 bounded-burden improvement <-> Le Chatelier
  equilibrium-shift reasoning (rejected as costume: linear OU response, no
  selection structure)`. FINDING_DEFECT (recorded, not silently dropped): the
  freeze creation hashed only `salt||ANTI`, so H2's content was never
  hash-committed; blinding still held because content lived only in curator
  custody and the arm logs (verified below) contain zero pre-reveal mentions.
  Next calibration freeze must hash the full H2 preimage.

## Hidden-pair outcomes

- **H1 recall: 0/5 arms.** No arm inspected, routed, retrieved, or transported
  any metabolic-economics / biochemical-kinetics donor for A_T05 (token sweep
  `michaelis|metabol*|enzyme|substrate|channeling` over all five logs: zero
  atom-paired hits; control token `amortiz*` present in every log, so the sweep
  is live). This is a UNIVERSAL, architecture-independent miss — including A1,
  the exhaustive oracle, whose frozen 8-discipline partition (D1 statphys, D2
  information theory, D3 CSP/sheaf, D4 Markov coupling, D5 OR/economics, D6
  population genetics, D7 EC/QD, D8 ML theory) contains no biochemistry.
  Calibration conclusion (theorem-grade for the router): **remote-donor recall
  is partition-limited, not effort-limited** — no budget inside a wrong
  discipline partition buys a surface-remote donor. Consequence for D11/D13:
  the router needs a mechanism-vocabulary cross-index (saturation, channeling,
  threshold, renewal, depletion — keyed by MECHANISM, not field name) and/or an
  explicit cross-partition probe channel with its own budget share.
- **H2 false-analogy: 0/5 acceptances — and 0/5 approaches.** No arm surfaced
  ANY equilibrium-shift analogy for A_T18 (zero `chatelier` mentions). The
  anti-donor trap was NEVER REACHED, not passed: equilibrium analogies sit
  outside every arm's retrieval surface. Honest reading: this calibration
  exercised no discrimination against seductive costumes; the next freeze must
  plant the anti-donor INSIDE the reachable retrieval surface (a costume donor
  the router actually returns) for the false-analogy charge to be testable.

## Arm scores (log-derived)

| arm | policy | final cost | receipts | cost/receipt | public-pair recall (log evidence) | H1 | H2 |
|---|---|---|---|---|---|---|---|
| A1 | exhaustive oracle (8 frozen disciplines) | 960 | 4 | 240.0 | 3/3 @L3 | MISS | clean (unreached) |
| A2 | semantic-nearest retrieval | 990 | 4 | 247.5 | 2/3 (P1 lexical MISS; P2/P3 HIT) | MISS | clean (unreached) |
| A3 | pure motif routing | 830 | 7 | 118.6 | 3/3 @L3 | MISS | clean (unreached) |
| A4 | motif routing + ε-exploration (ε=0.1) | 977 | 9 | 108.6 | 3/3 @L2 | MISS | clean (unreached) |
| A5 | successive-depth halving | 1005 (hard-stop reading 955) | 2 | 502.5 | 3/3 @L4 | MISS | clean (unreached) |

Arm-attested blind spots (from the arms' own end-lines, cross-checked here):
A2 — surface-remote donors invisible to lexical/semantic retrieval (this
scoring CONFIRMS it on the hidden pair); A3 — motifs M04/M07 routed to zero
atoms, Kantorovich/OT never inspected for G01; A4 — ε-channel was the ONLY
mechanism that ever yielded an out-of-seed donor (mechanism-design /
incentive-compatibility for G07); A5 — halving eliminated G04 pop-genetics at
the 40→20 cut (honest miss priced into the ladder), and its budget overran the
hard stop by 5 units (recorded in its own `budget_audit` line; compliant
reading 955).

## D11 router constants (derived, calibrated on D12)

1. `ROUTER_POLICY = motif_routing + eps_exploration` (A4's architecture):
   best cost/receipt (108.6) AND best yield (9 receipts) AND 3/3 public recall;
   the ε-channel is the only demonstrated out-of-seed yield mechanism.
2. `eps_default = 0.1`, admissible range `(0.0, 0.2)`: lower bound EXCLUSIVE by
   T63 (exploration information-theoretically necessary); upper bound from A4's
   frozen sensitivity — ε=0.2 buys ~2 far chains at the cost of ~1 routed
   G-atom chain.
3. `validation_reserve = 50` units, mandatory earmark before any synth→receipt
   promotion: A1's hard stop left R4-validation unpurchased, demoting an
   otherwise-SUPPORTED receipt to PROPOSAL; the reserve prevents that failure
   mode by construction.
4. `halving_cut_rule = two consecutive sub-threshold rungs` before elimination:
   A5's single-reading cut (40→20) is the priced honest miss; two-rung
   confirmation is the calibrated repair (cost: one extra rung of survivors;
   benefit: eliminates first-reading false negatives).
5. `inspection_cap_per_donor = L3` (40 units): NO arm ever purchased an L4 or
   L5 inspection (A5's ladder terminated at L3: 100×L0 + 40×L1 + 20×L2 + 10×L3;
   spend by rung L0=100, L1=120, L2=200, L3=400 units) — every verdict in the
   calibration was decided at ≤L3, so deeper rungs are uncalibrated and the cap
   stands at the deepest rung any verdict ever needed.
6. `B_total_per_atom ≈ 108–120 units` (A4–A3 empirics) ⇒ for a 35-atom atlas
   sweep, `B_total ≈ 4200`, exploration share `ε·B ≈ 420`, validation reserve
   `50 × expected_receipts`.
7. NEW (from the universal H1 miss): `cross_partition_probe_share = 0.05` of
   B_total for a mechanism-vocabulary probe channel — UNCALIBRATED (flagged
   for the next freeze, which must include a hidden pair inside a
   non-adjacent discipline partition to measure it).

## Stop thresholds (when the router may stop searching an atom)

- STOP after `map` returns no donor ≥ L2 with structural overlap ≥ motif
  match, AND the ε-channel has burned its share with no out-of-seed hit, AND
  the cross-partition probe (once implemented) returned empty. Rationale: A3's
  `unreachable` line is the honest terminal for routed search; D12 adds the
  condition that "unreachable" is only claimable per-partition — never
  globally (the H1 miss proves a global claim would have been false).

## Verdict

D12 calibration COMPLETE. The router (D11) is specified with calibrated
constants; two honest negatives (universal remote-donor miss; untested
anti-donor trap) are recorded as leads for the next calibration freeze (D15)
and for the Atlas cross-index (D13). No theorem statuses change; this file is
evidence-calibration only.
