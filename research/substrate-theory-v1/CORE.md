# Substrate Theory v1 — CORE (read first)

`EXPLICITLY_NON_FINAL` · `replace-don't-defend` · successor to HSG v3. Owner umbrella: #277. Built 2026-09-10 against main @ 2d95bcc. Method: refresh live evidence first (new evidence overrides theory); parent-subtract before claiming novelty; every mechanic needs a causal test, not a narrative.

**Goal.** The smallest machine-independent cognitive substrate that grows from experience into broad intelligence, recursively improves how it learns, and shows measurable scaling toward real maths/language/code/planning competence. The current unit is a hypothesis to attack, not a frame to defend.

## The three loops (frozen definitions, with evidence status)

**Cognition:** observation → representation → applicable-unit activation → prediction → selection/composition → execution → independent verification → credit/blame → knowledge/update/consolidation.
Status: the loop runs, but its pivotal joint is **selection** — `decide()` commits `passed[0]` in fixed catalogue order (annex KSO_AUDIT, solve.py:498-502). No value, score, or cost ranks candidates. M1B (#357) proved oracle-applicability unlocks the gain; nothing in the runtime chooses.

**Development:** history H_t → learned search/representation capital S_t → changed future acquisition process → genuinely new verified competence.
Status: **positive at assay scope** (M2-P1 #356: history-induced search prior; stored answers worth zero; shuffled history worse than none; depth dose-response) on ecologies passing a viability gate. Development must also be an *economic fact*: DEV-CAL-3/4 (#353/#359) fixed charging semantics and recovered the ledger; M1C (#360/#361) tests the observed crossing.

**RSI:** failure → self-model → causal hypotheses → active experiment selection → diagnosis → repair generation → prospective prediction → shadow evaluation → externally governed adoption/rollback → improvement episode → updated improvement policy G_{t+1}.
Status: **not earned.** No run has shown cost-to-verified-improvement falling across matched generations; no parent metric exists to borrow (annex ARCH §b). RSI_SPEC.md defines the ledger and the first testbed.

## Capability ladder (entry/exit criteria per level)

| # | Level | Entry test | Status |
|---|---|---|---|
| 1 | Minimal cognitive unit | typed units, warrants, receipts | **EXITED** |
| 2 | Native acquisition | on-path serving beats RESET through registered solve | **EXITED** (M1B #357: 12/40→36/40, ~35× lower burden) |
| 3 | Developmental transfer | history-induced prior on viable ecology, all gates | **CURRENT** — positive at assay scope (#356); ceiling = independently authored ecology (M2-P2, in flight) |
| 4 | Conditional/applicability learning | learned I beats always/never-serve at matched cost | **NOT ENTERED** — oracle-or-nothing today (E-DEC-1) |
| 5 | Recursive development | RSI ledger slope < 0 across ≥2 generations | **NOT ENTERED** (E-DEC-3) |
| 6 | Self-diagnosis/self-repair | hidden-diagnosis rediscovery ≥ classical parent | **NOT ENTERED** (RSI_SPEC §programme) |
| 7 | Cross-domain cognition | same core, ≥2 materially different domains, transfer | **NOT ENTERED** (flagship gate 4) |
| 8 | Validated scaling law | prospective fit + held-out scale prediction | **NOT ENTERED** (SCALING_PROGRAMME) |
| 9 | Real tool-using tasks | verified competence on real maths/language/code | **NOT ENTERED** |
| 10 | Broad machine intelligence | open-ended development beyond authored ecologies | **NOT ENTERED** |

Rule: never infer a higher level from a lower-level positive; never mark a level green by relaxing its frozen test.

## File map (layered: core → detail → raw)

- `COGNITIVE_UNIT_SPEC.md` — field-by-field verdict on u; the corrected unit u₂.
- `THEORY_MAP.md` — dependency graph of all cognitive mechanics.
- `GAP_MATRIX.md` — missing components ranked by expected leverage.
- `RSI_SPEC.md` — RSI formalization, governance stack, M1/M1B hidden-diagnosis programme.
- `EFFICIENCY_ROADMAP.md` — algorithm imports with parents, run order, falsification tests.
- `SCALING_PROGRAMME.md` — independent variables, prospective-fit protocol.
- `DECISIVE_EXPERIMENTS.md` — E-DEC-1..5.
- `annexes/` — raw research records (KSO audit; three parent-subtraction files, 60 ideas total).

## The final answer (provisional, hardened by E-DEC results)

The minimal mechanic set that would justify believing OCM can recursively grow from a small substrate rather than solve structured benchmarks:

1. **Learned serving** (I/V): a value-ranked router over the fragment library, supervised by the existing amortised-return ledger (parents: contextual bandits, ACT-R U=PG−C). Without it every gain needs an oracle.
2. **A prospective value-of-history gate** on every ecology (learnability + non-derivability of the useful prior) — kills benchmark-specialization before it runs. Prototype already operative (substring-disjointness; recall-ALL admission law).
3. **Corrected capital/marginal economics with an observed crossing** — development that never breaks even is a lab artifact, not a mechanism.
4. **Externally governed verification and admission** — already operative; keep the authority lattice explicit and never self-granted.
5. **An RSI generation ledger** — declining cost-to-verified-improvement as *the* recursive-improvement claim, E-signed, rollback-bound.

Items 3–4 are operative, 2 is operationalizing (M2-P2), 1 and 5 are open. Belief is justified only when E-DEC-1 through E-DEC-5 return their frozen terminals on independently authored ecologies.
