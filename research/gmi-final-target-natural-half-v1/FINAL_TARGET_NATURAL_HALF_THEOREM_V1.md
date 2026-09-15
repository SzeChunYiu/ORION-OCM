# Final-target natural-intelligence half — Theorem V1

Status: **FORMAL COMPOSITION + FROZEN REGISTRY. Admissible scope only.**
Refs: #592 item 40(a), #602 L1 / L2 / L3 / V7.
Parents (read-only): `gmi-biological-bridge-v1`, `gmi-natural-intelligence-bridge-v1`,
`gmi-derived-lesion-v1`, `gmi-morphology-phase-rv-v1`. Soft-reuse of species
`(E,R,V)` regimes from `gmi-biology-predictions-v1` when that package is present
on a sibling branch; values are inlined here so this capsule stands alone on main.

## 0. Honest claim ceiling

| Label | Meaning in this capsule |
|-------|-------------------------|
| **admissible** | Dual schema registered; `C_pred` rows frozen before any phenotype consultation; composition checks against parents pass under unittest |
| **reachable (not claimed)** | Empirical phenotype scoring, G10 lab validation, neuroanatomical identity, or `HUMAN_COGNITION_EXPLAINED` |

This capsule ticks **admissible** discharge for #592.40(a) and #602 L1–L3/V7 at
the registered formal scope. It does **not** tick or claim:

- `HUMAN_COGNITION_EXPLAINED`
- G10 empirical natural-intelligence validation
- neuroanatomical mapping (no Brodmann / tract / region identity)
- ladder-ceiling half of #592.40(b) (machine↔natural joint ceiling still open)

## 1. Dual schema

### 1.1 Machine half (already on main; composed, not re-derived)

\[
(E, R, V) \mapsto M^\* = \arg\min_M B_M(E,R,V)
\]

as registered by `gmi-morphology-phase-rv-v1` (archetypes: neural / symbolic /
probabilistic). The natural half **imports** this winner as the morphology
coordinate `M` inside each bridge row; it does not invent a second phase law.

### 1.2 Natural half (this capsule)

A prediction is the biological-bridge quadruple

\[
(E_{\mathrm{bio}}, M, C_{\mathrm{pred}}, D_{\mathrm{holdout}})
\]

with the meanings fixed in `BIOLOGICAL_BRIDGE_CONTRACT_V1.md`:

1. `E_bio` — ecology in GMI coordinates (resource / social / niche axes).
2. `M` — morphology/capability law applied (here: phase-RV winner + named
   bridge mechanisms from the inventory).
3. `C_pred` — cognitive profile stated **before** consulting phenotype data,
   with at least one registered failure mode.
4. `D_holdout` — biological observations **held out** (status `HELD_OUT`);
   provenance slot reserved, content not loaded.

A row counts only when all four fields are present and frozen. Retrospective
story-fitting of known ethology is assimilation food, never closure evidence.

## 2. L1 — Animal cognitive phenotype descriptors + profile laws

Descriptors (finite, named):

| id | descriptor | profile law (admissible) |
|----|------------|--------------------------|
| `D_mem` | memory-regime mix | niche variability ↑ → episodic weight ↑; stable niche → semantic-heavy |
| `D_tom` | opponent-model depth | social interaction value must clear TOM recursion cost else depth stays 0/1 |
| `D_meta` | graded confidence / stop | stop iff common action; else confidence scales with candidate-set size |
| `D_plan` | lookahead demand | planning depth ≥1 only where multi-step ecology pays EVC |
| `D_comm` | protocol / culture pressure | cumulative culture only if population × fidelity clears teaching break-even |
| `D_pred` | predictive-motor demand | predator/prey visual-tracking ecology selects predictive-modeling morphology class |

These are **laws over descriptors**, not scored phenotypes. L1 is discharged
when the descriptor set and laws are registered and machine-checked for
internal consistency (monotone axes, distinct profiles across taxa).

## 3. L2 — Cross-species frozen predictions (7 taxa)

Seven taxa with frozen `(E,R,V)` regimes (biology-predictions soft-reuse plus
three completing taxa). Phenotype data remains `HELD_OUT`.

| taxon | E | R | V | `M` (phase winner) | profile emphasis (`C_pred`) |
|-------|---|---|---|--------------------|-----------------------------|
| corvid | 8 | 5 | 7 | neural | high episodic + planning; mid TOM |
| cephalopod | 8 | 3 | 4 | neural | high flexible problem-solving; low social TOM |
| rodent | 5 | 7 | 3 | neural | spatial/episodic navigation; low protocol culture |
| nonhuman_primate | 9 | 8 | 9 | neural | high TOM depth + protocol negotiation |
| cetacean | 8 | 6 | 8 | neural | high communication + culture-like teaching pressure |
| carnivore | 7 | 5 | 5 | neural | high predictive-motor; mid planning |
| human | 9 | 9 | 9 | neural | see L3 (architecture-level profile only) |

Failure mode (shared): any taxon whose held-out phenotype contradicts the
frozen ordinal profile on ≥2 descriptors, after `D_holdout` is unsealed under
a later protocol, voids that row — not this capsule's present claim.

## 4. L3 — Human cognitive-architecture predictions (no neuroanatomy)

Human `C_pred` is an **architecture profile** derived from GMI laws:

- memory regimes: working / episodic / semantic / procedural partition
  (morphogenesis memory-regime law)
- metacognitive stop: META-1 graded confidence
- social recursion: TOM depth bounded by ecology-paid fixed point
- morphology class: phase-RV neural at adult `(E,R,V)=(9,9,9)`
- developmental ordering: infant → child → adult with increasing `(R,V)` at
  fixed high `E` (soft-reuse of biology-predictions trajectory shape)

Explicitly **excluded**: any mapping to cortical areas, white-matter tracts,
neurotransmitter systems, or clinical lesion topography.

## 5. V7 — Natural-intelligence held-out validation (formal scope)

V7 here means **protocol composition**, not empirical pass:

1. Every registry row has `D_holdout.status = HELD_OUT` (no phenotype bytes).
2. Composition with `gmi-derived-lesion-v1`: for each natural profile emphasis,
   the matching derived lesion (`L_mem`, `L_plan`, `L_social`, …) is the
   registered deficit footprint that a future empirical unseal must respect.
3. Composition with `gmi-natural-intelligence-bridge-v1`: morphology→taxon
   pressure classes remain consistent (same pressure class → same morphological
   class).
4. Machine half frontier (`gmi-morphology-phase-rv-v1`) supplies `M` winners;
   natural half does not override them.

Empirical G10 / live ethology batteries remain **reachable, not claimed**.

## 6. #592 item 40 split

| half | status |
|------|--------|
| (a) natural-intelligence half | **admissible present** (this capsule) |
| (b) ladder-ceiling joint claim | **open** (out of scope) |

Machine morphology frontier already lives on main via morphology-phase-RV;
this capsule closes the natural half by dual-schema registration + frozen
`C_pred`, not by asserting joint explanation of human cognition.

## 7. Falsifier

The capsule is void if any of:

- a registered row lacks one of `E_bio`, `M`, `C_pred`, `D_holdout`
- any test consults phenotype content (non-`HELD_OUT` payload)
- claim surface asserts `HUMAN_COGNITION_EXPLAINED`, G10 empirical, or neuroanatomy
- composition checks against parent lesion / bridge / phase-RV contracts fail

## 8. Terminal

```text
FINAL_TARGET_NATURAL_HALF_ADMISSIBLE_V1
```

Admissible formal composition. Not an empirical natural-intelligence closure.
