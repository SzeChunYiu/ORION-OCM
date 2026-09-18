# Section Z structural map v1

Section Z of SzeChunYiu/ORION-OCM#833 does **not** live in the issue body. It lives in
issue comment `5684819296`, whose byte-exact body is 12,036 bytes and contains:

- one `## Z — Groundbreaking Science Gates (mandatory flagship layer)` heading,
- eighteen `### Z<n> — ...` subsection headings,
- **131** `- [ ] ` rows, **all unchecked** at the time of this map,
- a trailing `## Groundbreaking flagship closure rule` prose block that contains
  **no checkbox rows** and must never be reconciled.

Mechanical checks performed on the live body (`gh api .../issues/comments/5684819296 --jq .body`):

| check | result |
|---|---|
| rows matching `^- \[ \] ` | 131 |
| rows checked (`- [x] `) | 0 |
| duplicate row strings | 0 |
| row strings that are proper substrings of another row | 0 |
| subsection heading depth | `###` (three hashes), **not** `##` |

The substring check matters: Z8/Z10/Z11 contain many short `Include ...` rows
(`- [ ] Include verifier noise/failure.`, `- [ ] Include realistic workloads.`).
None collides, so a byte-exact `old` string identifies its row uniquely, but any
future reconciliation must re-run this check rather than assume it.

## Row census

| subsection | rows | title |
|---|---:|---|
| Z1 | 6 | Explanatory compression / master principle |
| Z2 | 5 | Minimal unavoidable prior / architecture-agnostic derivation |
| Z3 | 5 | Invariance and representation independence |
| Z4 | 5 | Universality classes of machine intelligence |
| Z5 | 6 | Critical phenomena and scaling |
| Z6 | 6 | Theory discrimination against strongest parents |
| Z7 | 6 | Prospective impossibility and failure prediction |
| Z8 | 10 | Hostile out-of-distribution science |
| Z9 | 7 | Blind external prediction protocol |
| Z10 | 10 | Real-system prospective morphology selection |
| Z11 | 9 | Intelligence Morphology Benchmark |
| Z12 | 9 | Prediction sharpness, uncertainty and scientific risk |
| Z13 | 12 | Genuine unseen-form / W4 gate |
| Z14 | 7 | Cross-substrate and natural-intelligence test |
| Z15 | 6 | Decisive falsifiability |
| Z16 | 6 | Groundbreaking-result gate |
| Z17 | 8 | Flagship robustness |
| Z18 | 8 | Independent hostile scientific review |
| **total** | **131** | |

## Grain analysis — what each subsection actually demands

Z is not 131 independent tasks. Every subsection is a *single protocol or
artifact* decomposed into its required ingredients, which is why one
well-scoped package can discharge a whole subsection. The four buckets below
are the batching unit.

### Bucket HARNESS — an exact harness over an already-frozen on-main result

The predictions/outcomes already exist on `main` and were frozen prospectively by
their own lanes; the missing thing is the **measuring instrument**. Nothing new
has to be discovered, so these are the cheapest honest rows in Z.

| subsection | rows | scored object already on `main` |
|---|---:|---|
| Z12 | 9 | `gmi-833-heldout-20-transitions-v1` (40 frozen endpoint morphology predictions, 20 boundary ties), `gmi-833-capability-predictor-evaluation-v1` (`FROZEN_PREDICTIONS_V*.json` prediction sets + external truth sets) |
| Z17 | 8 | any designated flagship conclusion; needs **one pass per central conclusion**, not one pass total |

### Bucket EXACT-FORMAL — provable now over the finite G0 quotient

`main` already carries an exact finite universe (the merged `G0-fin-v1` slice at
structural budget `(2,2)`: 576 presentations, 21 protected-semantic classes,
step cap 6, protected inputs `(),(0,),(1,)`) and an exact 65,552-candidate
binary-transducer universe. Both are enumerable in stdlib Python with `Fraction`
arithmetic, so these subsections are proof work, not discovery work.

| subsection | rows | what is provable |
|---|---:|---|
| Z2 | 5 | exact finite no-free-lunch over the quotient; minimal-bias characterization; the `prior-free` → `architecture-uncommitted` terminology migration already has a lane (`gmi-833-terminology-migration-v1`) |
| Z3 | 5 | transformation registry, invariance of quotient-level quantities, equivariance of presentation-level ones, adversarial semantics-preserving recodings, exact description-length / reachability bias (`gmi-833-remint-equivariance-v1`, `gmi-833-g0-grammar-bias-v1`, `gmi-833-transform-geometry-v1` are the parents) |
| Z4 | 5 | quotienting named families by scaling/resource behaviour; which distinctions survive the quotient |
| Z5 | 6 | the `λ* = ηp/2` boundary is already an analytic threshold; finite-size scaling over the budget ladder is exhaustive |
| Z7 | 6 | resource-dependent impossibility regions are exactly the infeasible cells of the finite grid |
| Z15 | 6 | falsifier registry with executable checkers; `main` already contains real failed preregistered predictions to publish |

### Bucket NEW-SCIENCE — genuine derivation or discovery, cannot be harnessed

| subsection | rows | the hard part |
|---|---:|---|
| Z1 | 6 | a compact variational/selection principle that actually *implies* the registered laws as corollaries, plus a proof that named laws cannot be compressed into it |
| Z6 | 6 | preregistered environments where GMI and a strongest parent genuinely disagree — most parents (MDL, Bayes decision theory, bounded rationality) are observationally equivalent to GMI on the finite quotient, so the honest terminal for several rows may be the row's own escape clause |
| Z8 | 10 | an independent hostile-world generator with nine named ingredient classes |
| Z11 | 9 | an actual benchmark whose scoring target is theory prediction |
| Z13 | 12 | the W4 gate: an unseen morphology recovered without its template in the grammar, with a prospectively predicted niche |
| Z16 | 6 | one genuinely surprising, predicted-before-observed result |

### Bucket EXTERNAL-GATE — no model-only route

These rows name a *person or an independent team* as the instrument. Under the
operator's standing directive they close with the strongest legitimate proxy,
explicitly labelled `HUMAN_GATE_BYPASSED__MODEL_PROXY`, never presented as
externally obtained — and a proxy built in a hurry is precisely the
`POST_HOC_SUSPECT` failure class audit #976 filed. They are deliberately left
open here.

| subsection | rows | gate |
|---|---:|---|
| Z9 | 7 | separated prediction/test teams and a third-party adjudicator |
| Z10 | 10 | five materially different real domains with CPU/GPU/wall-time/memory/I/O/energy measurement |
| Z14 | 7 | cross-species natural-cognition evidence |
| Z18 | 8 | five independent hostile reviewer roles with authority to reopen green gates |

## Cheap obligations vs genuine science

Within the buckets, rows split again by *what kind of thing closes them*:

**Registration rows** (create/freeze/register a named artifact, then prove the
artifact is real and machine-checkable) — roughly 45 rows. Examples:
`Freeze qualitative failure-mode predictions.` (Z7),
`Publish benchmark-generation rules before hidden outcomes.` (Z11),
`Freeze a final hostile-review report before manuscript submission.` (Z18).
These are cheap **only if** the artifact they register is real and the freeze
genuinely predates the outcome; a registration row closed with a post-hoc
artifact is the exact defect #976 found.

**Measurement rows** (score/measure/quantify an existing population) — roughly
35 rows, the whole of Z12, most of Z17, `Quantify theory compression` (Z1),
`Quantify grammar-induced description-length and reachability bias` (Z3),
`Test finite-size scaling` (Z5). Exactly computable; these are the highest
rows-per-unit-effort in Z.

**Derivation rows** (prove/derive/characterize) — roughly 30 rows.
`Prove or characterize why literally prior-free search is impossible` (Z2),
`Derive critical thresholds analytically` (Z5),
`Prove invariance/equivariance results` (Z3),
`Derive resource-dependent impossibility regions` (Z7).

**Discovery rows** (obtain a result that does not yet exist) — roughly 21 rows.
All of Z13 and Z16, the discriminating experiments of Z6, the real-domain
outcomes of Z10, the cross-species predictions of Z14. No amount of harness
work closes these.

## The one structural trap in Z

Z17's rows say *central conclusions* and *the flagship claim*, plural and
definite. Discharging Z17 for one designated conclusion and marking the rows
done would be closure by narrowing. Z17 therefore needs a **register of central
conclusions** (the `BASELINE_V1.md` §1 A1–A14 assertion table is the natural
authority) and one robustness pass per entry before its rows can honestly close.
The same trap does **not** apply to Z15, whose row 1 says *the flagship theory*,
singular, and explicitly asks for a reduction to 3–5 falsifiers.
