# RV-377-110 — FREEZE: leave-one-out ablation of the primitive alphabet (critical-path item 1)

Frozen BEFORE the run. Outcomes appended only.

## The question, and why it is answerable by construction

Critical-path item 1: *finish the zero-prior question decisively — either derive the
remaining primitives, or prove/declare the minimal irreducible axioms.*

The corpus states the strong gate as:

```
all registered families reach >=K4
major cross-family frontier predictions reach >=K5
all applicable estimator assumptions are explicit and tested
no untyped blocking dependency remains
```

`RV-377-107` measured the first clause directly: **0 of 264 K4 cells green**. The
derivation route to zero-prior closure is therefore not merely incomplete, it is
failing at its first conjunct. That forces the *other* branch of item 1: if the
primitives cannot all be derived, the honest move is to determine **which of them are
irreducible** and declare those as the minimal axiom set, with a proof obligation
attached to each.

That is decidable by construction, not by argument. `morph.KINDS` holds **36** typed
primitive kinds. For each kind `k`, delete `k` from the alphabet, rebuild the operator
grammar over the reduced alphabet, and re-run the B1 neutral search:

* reduced alphabet still reaches an admissible witness → `k` is **REDUCIBLE** (the
  theory does not need it as an axiom; it is derivable from the rest)
* admissibility is lost → `k` is **IRREDUCIBLE at registered scope** — an axiom
  candidate

## Design

* **33 ablatable kinds.** `INPUT`, `OUTPUT`, `TARGET` are the I/O boundary: `morphgen`
  already refuses to propose them and no ecology is well-formed without them, so
  ablating them tests nothing about derivability. They are classed **STRUCTURAL a
  priori** and that classification is declared here, not discovered.
* **4 ecologies, and only 4.** Rule 40 admits only ecologies that survive the
  best-constant control by at least one fx unit. Per `RV-377-108`:

  | ecology | status | margin |
  |---|---|---|
  | `E_wit1` | **used** | 2.400 / 3.401 fx |
  | `E_smooth1` | **used** | 1.399 fx (`all`) |
  | `E_smooth3` | **used** | 1.901 fx (`all`) |
  | `E_sym5` | **used** | 1.399 fx (`unseen`) |
  | `E_sym3` | **EXCLUDED** | NON_DISCRIMINATING, best constant 0.9062 / 0.8750 |
  | `E_parity` | **EXCLUDED** | WITHIN_QUANTIZATION, 0.401 fx both criteria |

  The two exclusions are recorded in code (`primitive_ablation.EXCLUDED`) with their
  reasons, so the omission is visible rather than silent — the defect rule 39 names.
* 33 × 4 = **132 ablation runs**, plus **4 full-alphabet baselines**.

## The precondition that makes or breaks this experiment

**An ablation is only meaningful on an ecology where the FULL alphabet reaches
admissibility.** If the baseline already fails, removing a primitive cannot be
observed to cost anything, and every kind would read as "reducible" for the trivial
reason that nothing worked to begin with.

Measured now, before the run: at 2 000 evaluations the full alphabet on `E_wit1`
reaches best capability **0.8333 — not admissible** (θ = 0.85), with no carrier
admissible. 27.5 s per 2 000 evaluations, so 20 000 evaluations ≈ 275 s per run.

So the run is staged:

1. **Baseline stage.** Full alphabet, 4 ecologies, 20 000 evaluations. Establish where
   the neutral search is admissible at all.
2. **Ablation stage.** Run the 33 leave-one-out ablations **only on the ecologies whose
   baseline is admissible.** Any ecology whose baseline fails is reported as
   `ABLATION_UNDEFINED_HERE` and contributes no primitive classification.

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| T1 | **At most 2 of the 4 baselines are admissible at 20 000 evaluations.** The B1 neutral search has a long record of not recovering carriers (`RV-377-058`: 0 of 6). | 3 or 4 baselines admissible |
| T2 | **At least one baseline IS admissible**, so the ablation stage is not vacuous. | 0 of 4 admissible → experiment yields nothing and must be re-run at higher budget |
| T3 | **Fewer than 10 of the 33 kinds are IRREDUCIBLE.** Most of a 36-kind alphabet should be redundant; a large irreducible core would mean the alphabet was fitted to the answer. | ≥ 10 irreducible |
| T4 | **`DENSE`, `TABLE`, `KVSTORE` and `PROGRAM` are NOT all irreducible.** These are the four carriers B1 uses as descriptors. If every one of them is individually necessary, the carrier taxonomy is an assumption, not a finding. | all four irreducible |

T3 and T4 are the predictions against GMI. A large irreducible core, or four
individually-necessary carriers, would mean the primitive alphabet encodes the
conclusions the theory claims to derive — the `IG-5` primitive-selection gate failing
in the open.

## What this cannot do

This settles irreducibility **at registered scope only**: one search family, one
budget, the ecologies above, one seed per cell. A kind that survives ablation here may
still be necessary on an ecology not in the registry. The result is a lower bound on
the axiom set, never an upper bound, and will be stated that way.
