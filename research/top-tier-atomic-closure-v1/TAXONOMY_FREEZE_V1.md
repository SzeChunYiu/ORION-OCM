# TTAC Atom Taxonomy + Readiness Schema — FREEZE V1

Owner issue: #277 (Top-Tier Atomic Closure Programme).
Parents: #144 publication constitution, #165 master roadmap, #233 HSG semantic execution,
#151 developmental lineage, #149 self-evolution, #93 field, #221 HPC evidence, #42/#52.

Frozen BEFORE any repository scoring (TTAC-D0 rule). Append-only afterwards; amendments
must not retroactively raise any readiness value. Supersession by stronger evidence,
counterexamples, parents or mathematics is the only sanctioned change direction.

---

## 1. Atom classes

Every scientifically material atom belongs to exactly one class:

| Class | Definition | Closure character |
|---|---|---|
| `THEOREM` | Formal statement about HSG/semantic-execution machinery with a proof or finite certificate | closes by proof, not by measurement |
| `ENGINEERING_MECHANISM` | A mechanism that works reliably (engine, gate, evaluator, scheduler) | reliability is not discovery; closes at scope with measurement+causal bounds |
| `EMPIRICAL_REGULARITY` | A measured quantitative phenomenon claim (burden curves, scaling regimes, ecology effects) | closes by prospective confirmation + replication |
| `DEVELOPMENTAL_LINEAGE` | A causal claim about one persistent lineage across task ecologies (#151) | closes by prospective causal knockout + disjoint replication + autonomy audit |
| `SELF_EVOLUTION` | A governed self-change generation claim (#149 lifecycle) | closes per #149 outcome vocabulary; negative outcomes are first-class |
| `GOVERNANCE_META` | Claims about the programme's own evidence machinery (autonomy audit, replication, claim ceilings) | closes by audit artifact, not by performance |

Cross-cutting: any atom may additionally carry a NEGATIVE disposition
(`REFUTED_WITH_COUNTEREXAMPLE`, `TRADEOFF_FRONTIER_ONLY`); negatives are retained, never discarded.

## 2. Atom terminals

Exactly one terminal per atom (a terminal may be revisited only by superseding evidence,
recorded as an amendment):

```
PROVED                              machine-checked universal proof (THEOREM only)
PARENT_SUFFICIENT                   strongest parent already owns the function (success terminal)
FINITE_CERTIFIED                    finite-scope certificate with explicit world scope (THEOREM only)
EMPIRICALLY_SUPPORTED_AT_SCOPE      prospective evidence holds inside a frozen scope; ceiling = scope
REFUTED_WITH_COUNTEREXAMPLE         explicit counterexample/world retained
TRADEOFF_FRONTIER_ONLY              claim reduces to an honest frontier, no dominance
CANNOT_CHECK_<reason>               measurement impossible under stated constraint; reason mandatory
```

`PARENT_SUFFICIENT` is terminal-success: never engineer past a parent that genuinely owns
the function. `CANNOT_CHECK_<reason>` must name the missing instrument, not a resource shortage.

## 3. Readiness vector

`R(a) = (T, P, M, C, G, S, R, A, E)` per #277 sec 1. Generic ladder:

| Level | Meaning | Evidence binding (#144 sec 4) |
|---|---|---|
| 0 | MISSING | no artifact |
| 1 | SPECIFIED | question/falsifier registered, not run |
| 2 | EXPLORATORY | E1/E2-class result only; adaptive-exploratory caps here |
| 3 | PROSPECTIVELY_CONFIRMED | E3 frozen confirmatory study for that coordinate's question |
| 4 | DISJOINTLY_REPLICATED | E4: new seeds/families/order/host |
| 5 | INDEPENDENTLY_REPRODUCED | E5: independent scorer or second implementation |

Coordinate-specific readings:

- `T` theory: for THEOREM atoms T tracks proof status itself (5 = checked + independently
  re-verified; 4 = machine-checked/replayed; 3 = finite certificate with scope ceiling).
- `P` strongest-parent subtraction: 3 requires a faithful strongest parent run at matched
  information/resources/checker access and subtracted (NOT RUN ≠ 2; it stays 1).
- `M` measurement validity: 3 requires the metric's hostile gaming families bounded or
  explicitly carried into the claim ceiling (`MEASUREMENT_VALIDITY_V1` row).
- `C` causal evidence: 3 requires prospective knockout/ablation of the claimed object that
  flips the outcome (E3); correlated pre/post does not reach 3.
- `G` generalization: cross-domain transfer with negative-transfer controls retained.
- `S` scaling/lifetime economics: full-lifecycle cost vector (incl. maintenance, index,
  rejected-candidate work), frozen non-dominance rule.
- `R` replication: maps directly to E4 (4) / E5 (5); internal replay never exceeds 2.
- `A` autonomy audit: requires `EXTERNAL_COGNITIVE_INPUT_LEDGER` entries covering the
  atom's causal chain; 4 = clean-room/no-private-state audit.
- `E` external/ecological validity: non-toy worlds or independent scorer.

## 4. Closure profiles (load-bearing coordinates per class)

Only load-bearing coordinates gate closure; others are recorded as `null` and never block.

| Class / terminal | Load-bearing minimum (others null) |
|---|---|
| THEOREM → PROVED | T5, P3, R4, A2 |
| THEOREM → FINITE_CERTIFIED | T3 + explicit world scope, P3, A2 |
| THEOREM → PARENT_SUFFICIENT | P5 (verified parent owns statement), T3 |
| ENGINEERING_MECHANISM → EMPIRICALLY_SUPPORTED_AT_SCOPE | M3, C3, R3, A2, S2 (scope ceiling mandatory) |
| ENGINEERING_MECHANISM → PARENT_SUFFICIENT | P4, M2 |
| EMPIRICAL_REGULARITY → EMPIRICALLY_SUPPORTED_AT_SCOPE | M3, C3, R4, S2 |
| DEVELOPMENTAL_LINEAGE → EMPIRICALLY_SUPPORTED_AT_SCOPE | M3, C4, G3, S3, R4, A4, E3 |
| SELF_EVOLUTION → any #149 outcome | per #149 frozen machine-quality contract; minimum M3, C3, A4 |
| GOVERNANCE_META | audit artifact completeness; M3 |

A headline (paper-level) claim inherits `min` over its load-bearing atoms' load-bearing
coordinates; the programme strength is that minimum — optimize it, not task counts.

## 5. Claim ceiling rules

1. Ceiling of an atom = strongest claim compatible with its CURRENT vector; exceeding it is
   a defect (`forbidden_overclaims` list is non-exhaustive enforcement).
2. Finite certificates never lift to universal claims (P2 ≠ P1).
3. Adaptive-exploratory results cap at EXPLORATORY (2) forever; confirmation requires a new
   frozen study.
4. A coordinate raised to ≥3 must cite evidence sha + evidence class; value decreases are
   allowed (new hostile finding) via amendment with cause.
5. Autonomy unaudited ⇒ no self-development/self-evolution claim (A gates the sentence, not
   the number).

## 6. Artifact skeleton (owner D-step)

| Artifact | D-step |
|---|---|
| `ATOM_REGISTRY_V1.json` | D1 |
| `READINESS_MATRIX_V1.json` | D2 |
| `DECISIVE_CLAIM_REGISTRY_V1.json` | D2 |
| `BLOCKER_DAG_V1.json` | D3 |
| `MEASUREMENT_VALIDITY_V1.json` | D4 |
| `EXTERNAL_COGNITIVE_INPUT_LEDGER.jsonl` | D5 (prospective from freeze; historical only with evidence, else UNKNOWN) |
| in-flight map (D17–D28, #221) onto coordinates | D6 |
| `FLAGSHIP_EXPERIMENT_V1.json` | D7 |
| `PARENT_FIRST_REFUSAL_V1.json` | D8 |
| `REPLICATION_MATRIX_V1.json` + E3 protocol | D9 |
| E3→E4→E5 execution receipts | D10 |

## 7. Locks inherited

- N2 language, N4 formal proof, N5 adoption stay LOCKED exactly as in #233 FREEZE_V1.
- Prior evidence (HST/HSG v1–v3, D12–D15) append-only; never reinterpreted.
- In-flight #233 D17–D28 and #221 continuous jobs are mapped (D6), never duplicated or
  disturbed.
- HSG explicitly non-final; this freeze is explicitly non-final (supersede, don't defend).
