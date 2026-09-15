# Repairing the K4 instrument: neutral search recovers retention

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Repair: `gmi_k4_substitution_repair_v1.py` (the frozen model is not modified).
Probe: `gmi_k4_substitution_probe_v1.py`.
Receipt: `microscopes/results/STAGE_K4_SUBSTITUTION_REPAIR_V1.json`.
Executed on `laptop-billy`; receipt md5-verified across transfer.

`GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1.md` established that the frozen K4 cost
model contains **no substitutions**, so the mechanism the apparatus was built
to detect cannot be expressed in the space it searches, and named the repair.
This builds it.

**The frozen model is untouched.** `gmi_k4_resource_native_v4` is imported and
left exactly as it is, so every registered campaign result stands unchanged.

## Three corrections, each independently principled

| | correction | why |
|---|---|---|
| **R1** | amortise `state_storage` by reuse | the model already divides `development_compute` by reuse, which is per-use normalisation; building a store is a one-time cost in the same group. PVR-3 pays `S` **once**. |
| **R2** | let the store reduce serving work | `state` and `work` come from two independently generated expressions, so nothing couples them. A machine that has stored an answer does not recompute it — gated on `retrieval`, so a machine that cannot consult its store gains nothing. |
| **R3** | amortise `search_compute` by reuse | `gp · tokens` is the cost of **finding** the candidate. Paid once, like development — but left flat. |

None mentions any family. R2 is PVR-3 applied per query.

## R3 was found by measurement, not by guessing

Decomposing the repaired winner at reuse 64:

| channel | cost | share |
|---|---:|---:|
| **`search_compute`** | **10.80** | **86.5 %** |
| `serve_compute_latency` | 0.82 | 6.6 % |
| `development_compute` | 0.38 | 3.1 % |
| `state_storage` | 0.25 | 2.0 % |

The amortised development term is **0.38** while the unamortised search term is
**10.80** — a 28× distortion.

> **The objective was roughly seven parts description length to one part
> everything else.** Cost minimisation was description-length minimisation
> wearing nine channel labels, which is why every channel correlated positively
> with every other and why more budget always meant *smaller*.

I had expected state to be triple-charged across storage, development and
retraining. It is not: that subtotal is 12.8 % against 19.0 % saved in the
per-use channels. The diagnosis was wrong and the measurement corrected it.

## The result: retention recovered by reuse alone

A label-free search over 4 000 sampled candidates. It sees only costs and never
a family name.

| reuse | repaired winner | coverage | retains | frozen winner |
|---:|---|---:|---|---|
| 1 | `metric` / state 1 | 0.016 | no | `metric` / 1 |
| 2 | `metric` / 1 | 0.016 | no | `metric` / 1 |
| 4 | `metric` / 1 | 0.016 | no | `metric` / 1 |
| 8 | `exact_key` / 1 | 0.016 | no | `metric` / 1 |
| 16 | `exact_key` / 1 | 0.016 | no | `metric` / 1 |
| 32 | `exact_key` / 1 | 0.016 | no | `metric` / 1 |
| 64 | `exact_key` / 16 | 0.250 | no | `metric` / 1 |
| **128** | `exact_key` / 48 | **0.750** | **yes** | `metric` / 1 |
| **256** | `exact_key` / 64 | **1.000** | **yes** | `metric` / 1 |
| 512 – 4096 | `exact_key` / 64 | **1.000** | **yes** | `metric` / 1 |

> **Under the frozen model the winner is identical at every reuse level across
> a 4096-fold range. Under the repair it marches monotonically from no
> retention to full coverage, and declines to retain when there is no reuse to
> amortise.**

Retained state is monotone in reuse; coverage saturates at 1.000; retention is
selected at 5 of 12 levels and *not* at low reuse. That last point is the
control that matters — a model that retained everywhere would be one that
*prefers* retention rather than one that *prices* it.

This is PVR-3 recovered by neutral search: the same break-even that governs
consolidation, chunking, teaching, culture and concept formation, now appearing
in a cost-minimising search that was given no family labels.

## Where the substitution lives

A population-wide correlation is the wrong instrument: two of the three
retrieval settings cannot consult a store, so any real substitution is diluted.

| pricing | subpopulation | corr(storage, serve) | material trade |
|---|---|---:|---|
| frozen | all | −0.0154 | no |
| frozen | can retrieve | −0.0167 | no |
| repaired | all | −0.0801 | **yes** |
| repaired | can retrieve | **−0.1472** | **yes** |

R2 alone creates the trade; R1 alone does not. The repaired correlation is
still weak because most sampled candidates cannot retrieve at all — which says
the **sampler**, not only the pricing, shapes what is findable.

## What this does and does not establish

**Establishes** that the 0-of-264 result is an instrument property. Three
corrections, none of which mentions a family, turn a search that was blind to
reuse across 4096× into one that recovers the retention mechanism and correctly
declines it without reuse. Under NS-1 consequence 2 that is the signature of
`INCONCLUSIVE_GRAMMAR`, not `THEORY_RED`.

**Does not** re-run any K4 cell or change any registered verdict. The frozen
model is deliberately untouched, so nothing here reclassifies the 159
`THEORY_RED` cells in-place. The per-cell audit named in the root-cause
document is now executed as
`gmi_k4_substitution_percell_audit_v1/`
(`GMI_K4_SUBSTITUTION_PERCELL_AUDIT_THEOREM_V1.md`, stage receipt
`microscopes/results/STAGE_K4_SUBSTITUTION_PERCELL_AUDIT_V1.json`): it partitions
which of the 159 **admit a substitution under this repaired pricing**
(admissible reading only; reachability remains clause (c) /
`gmi_k4_repaired_campaign_v1`). A campaign under the repaired pricing is a
decision about the registered protocol, not something to do silently.

**Scope.** One grammar (`G2_SYMBOLIC_PROGRAM`), scale 4, 4 000 sampled
candidates. `LOOKUP_RATIO` and the coverage model are a modelling choice — the
*shape* (storage substitutes for recomputation, gated on retrieval) is forced by
PVR-3, the constants are not. Retention is scored as coverage ≥ 0.5, an
arbitrary bar; the monotone march and the saturation at 1.000 do not depend on
it.

**Falsifier.** Show a pricing with all three corrections under which the winner
is still reuse-invariant; or show that R2's gating on `retrieval` smuggles in a
family label. The probe asserts the frozen control stays flat, so if the
baseline ever moves this document fails CI rather than going stale.
