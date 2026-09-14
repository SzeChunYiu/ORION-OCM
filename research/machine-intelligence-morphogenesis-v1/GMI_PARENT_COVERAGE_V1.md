# Section Q measured: where the parent-subtraction programme actually stands

Date: 2026-09-15. Addresses checklist section **Q** (parent-subtraction programme, 23 traditions).
Witness: `gmi_microscope/parent_coverage_audit.py`. Receipt: `microscopes/results/STAGE_PARENT_COVERAGE_V1.json`.

Section Q asks for a live reduction/ownership entry for each of 23 research traditions. **Before writing 23
entries, the question is how many already exist** — and the corpus already has the right instrument:
`research/parent-absorption-v1/LEDGER.json`, 20 entries with exactly the schema Q needs (parents with
citations, what the parent explained, a disposition, whether the parent is sufficient at scope, the residual,
and the higher-order question remaining).

This measures coverage. **It writes no entries**, and that is a deliberate choice: an entry invented from
memory, with plausible-sounding citations, would be worse than an empty box — because an empty box is honest
about not knowing, and a fabricated citation is not.

## 1  Result

| | count |
|---|---:|
| traditions in section Q | 23 |
| **solid coverage** | **7** |
| suspect coverage (excluded) | 3 |
| **no entry at all** | **13** |

Dispositions among covering entries: `ADAPT 14, ADOPT 4, LEAVE_OPEN 4, REJECT 1`. A pin fails if that ever
collapses to a single disposition, or if nothing is ever rejected or left open — a ledger that only absorbs
and never declines is not doing subtraction.

## 2  Matching on family alone undercounts — and matching too loosely overcounts

The ledger's families are **mechanic-specific** (`indexing`, `program_library_learning`, `tms_atms`), not
named after research traditions. Matching a tradition against family names alone misses real coverage: the
`program_library_learning` entries cite **DreamCoder** and **Stitch** by name, which is exactly what makes
them a parent-subtraction record for Q's DreamCoder box. So the audit matches against the family, the id,
**and the names and citations of the cited parents**.

That widening then creates the opposite risk, and it fired immediately.

## 3  The audit caught its own false positive

`P-SELF-CHANGE-SEARCH` came out "covering" **three unrelated traditions** — Levin/OOPS, AutoML-Zero, *and*
Bayesian inference — because those words appear incidentally in its citations. A citation mentioning Bayesian
methods does not make a self-change-search entry a parent-subtraction record for Bayesian inference.

So the audit downgrades any coverage that rests **only** on an entry spanning three or more traditions.
Those three are reported as **SUSPECT and not counted**. A pin asserts the gate actually fires — if no entry
is ever promiscuous, the gate is untested and the count it protects is unverified.

This is the same failure mode as the B1 audit's `"production system"` matching `real-regime`, and the same
remedy: widen the signal to catch real matches, then guard against what the widening lets in.

## 4  The thirteen with no entry

Named, so the gap is a list rather than an unknown:

AIXI / universal intelligence · MAML / learned optimizers / meta-RL · Categorical & compositional learning
theory · ACT-R / Soar / NARS / OpenCog · RL / hierarchical RL / model-based planning · Active inference &
predictive processing · Memory systems / CLS / continual learning · MoE / modular continual learning ·
Hyperdimensional & vector-symbolic computing · Neural cellular automata & morphogenetic computation ·
Evolutionary & open-ended artificial life · Analog / physical / quantum computation · Universal computation
/ lambda / register machines.

Several of these are ones the corpus has *results* adjacent to — B12 residual memory borders CLS, B10
conditional specialization borders MoE, B19 continual borders continual learning. **Adjacency is not a
subtraction entry**, and recording it as one would be exactly the over-claim this audit exists to prevent.

## 5  Scope, and what is not established

This measures **coverage only**. It does **not** assess whether a covering entry is *adequate*: coverage
means an entry exists and cites that tradition, not that the subtraction is complete or correct. Seven solid
is therefore an upper bound on how much of section Q is genuinely done.

The audit reads the whole repository rather than a single directory, so it locates the ledger by walking
upward rather than by a fixed relative depth — a fixed depth resolved only inside a full checkout, which made
it silently unrunnable anywhere else.
