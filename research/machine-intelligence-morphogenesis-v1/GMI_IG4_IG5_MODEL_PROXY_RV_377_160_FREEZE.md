# RV-377-160 — IG-4 / IG-5 closure by independent model proxy: freeze

Status at freeze: **FROZEN_BEFORE_COMPARISON**. Date: 2026-09-12. Base: `origin/main` `088eb863`
(includes #455–#466). Branch `gmi/ig4-ig5-model-proxy-v1`. Spec commit `406f2a16`; trace commit
`8a3c4920`. The independent artifacts exist on disk at the time of this freeze and have **not** been
executed against the traces or the reference set; no agreement number and no coverage number has been
computed. Sections 1–6 are frozen. Section 7 (adjudication) is empty at freeze and is filled after the
billy-old run without editing 1–6.

Operator rule applied (2026-09-04): a human/external gate is never left blocking; it closes with its
strongest legitimate proxy labelled `HUMAN_GATE_BYPASSED__MODEL_PROXY`, never as externally obtained.

## 1. What is being closed, exactly

`GMI_INDEPENDENCE_GATE_DECOMPOSITION_V1.md` §2 leaves two residues after IG-1..IG-3:

* **IG-4 METER AUTHORSHIP** — totals are corroborable by a general-purpose profiler; the *bucketing*
  (which measured trace counts as which registered property value) is a same-author modelling choice.
* **IG-5 ENCODING AUTHORSHIP** — the three K4 grammars share one author, so their agreement excludes
  implementation artefacts but not a shared conceptual bias about which primitives are "natural".

Every claim in `GMI_COMPLETENESS_BOUNDARY_THEOREM_V1.md` §2 carries "same-author evaluator, meter and
primitives" as its standing limitation (§6). This record replaces the *external author* on IG-4 and
IG-5 with a *fresh-context model session given only a specification*, and tests whether the
programme's load-bearing K4 negative survives an independently bucketed meter.

**Scope of "bucketing" here.** The K4 V7 verdicts decide `K4_RECOVERY_GREEN` by equality of a
measured 10-axis property vector with a frozen target (`GMI_K4_LOFO_FREEZE_V1.json` `property_axes`:
`state_scales_with`, `serve_scales_with`, `update_locality`, `routing`, `sharing`, `retrieval`,
`serve_iterations`, `stochastic_serve`, `verifier_gated`, `external_authority`). IG-4 bucketing is
the map from a candidate's measured resource trace onto those ten registered values. The allocation
of cost into the nine charged channels (`charged_cost_channels`) is a separate same-author choice and
is **not** closed here; it is named as residue in §6.

## 2. Method (frozen)

1. **Spec-only briefs** (`independence/IG4_METER_SPEC_V1.md`, `independence/IG5_PRIMITIVE_SPEC_V1.md`,
   commit `406f2a16`): registered axis names and vocabularies, a trace format, the bucketing task; the
   neutrality requirement, the abstract R5 closure rules, the minimality criterion, the five carrier
   classes and nine parents. No code, no path into the meter or the alphabet, no numeric bucket edge.
2. **Trace extraction** (`independence/extract_k4_traces_v1.py`, run on billy-old, commit
   `8a3c4920`): every candidate referenced by the 264 protected receipts (226 winners, 264 witnesses,
   260 negative twins, 1584 null rows; 2334 in all) is reconstructed from the receipt and verified
   against the receipt's candidate id (sha256 of the serial; fail closed). Each is measured on a
   data-independent 24-world probe panel (world i, quantity v ↦ 2 + sha256(`IG4-TRACE-V1:i:v`)[:8]
   mod 23) plus the cell's own world, a feedback probe, a content-dependence probe, a verification
   probe, an external probe, and four declared structural facts. The label-free file
   `k4_v7_traces_v1.json` (sha256 `41f2ba14…`) contains zero occurrences of any registered label,
   verdict or family id (grep control: 0 hits vs 7002 for a field name). The native buckets and every
   verdict input sit in a separate file the blind author never receives.
3. **Blind authors**: two fresh-context general-purpose model sessions (roles `ig4-blind-author`,
   `ig5-blind-author`), each given only its brief (verbatim) and, for IG-4, the trace file. Conduct
   rules in the brief: no other file, no git history, no execution (IG-4: one syntax check). The
   served model is asserted by the author inside the artifact. Artifacts:
   `independence/ig4_independent_meter_v1.py`, `independence/ig5_independent_primitives_v1.json`.
4. **Comparison** (`independence/ig4_reaggregate_v1.py`, `independence/ig5_coverage_check_v1.py`),
   executed on billy-old only, `nice -n 10`, one process; receipts
   `microscopes/results/IG4_INDEPENDENT_METER_AGREEMENT_old.json` and
   `microscopes/results/IG5_INDEPENDENT_ALPHABET_COVERAGE_old.json`, rsynced back and sha256-verified.
   The re-aggregator first re-derives all 264 native verdicts from the native buckets with the V4/V5
   adjudication logic (controls → witness expressibility → null dominance → target match / cheaper
   non-target → twin flip → budget); any mismatch aborts. It then re-adjudicates every cell with the
   independent buckets substituted for every property vector (winner, witness, twin, nulls) and all
   costs, scores, controls and budgets held fixed.

## 3. Prediction P1 (IG-4), frozen

**P1.** Over the 2334 candidate rows, per-axis bucket agreement between the independent meter and the
native V4 meter is **≥ 80 % on ≥ 8 of the 10 axes**, and re-aggregating the 264 K4 V7 verdicts with
the independent buckets flips **no** `THEORY_RED`, `THEORY_RED_NULL_DOMINATES` or
`INCONCLUSIVE_GRAMMAR` cell to `K4_RECOVERY_GREEN`.

**P1b (stricter, informative subset).** Four axes (`sharing`, `retrieval`, `serve_iterations`,
`stochastic_serve`) are declared structural facts in the trace and reduce to a vocabulary mapping;
their agreement is expected by construction and does not count as evidence. On the six *measured*
axes (`state_scales_with`, `serve_scales_with`, `update_locality`, `routing`, `verifier_gated`,
`external_authority`) agreement is ≥ 80 % on ≥ 4 of 6, **including both scaling axes**, and zero
cells flip to GREEN.

**Falsifier and its reading.** If any cell flips to GREEN under the independent buckets, the K4
negative depends on the author's meter at that cell and `K4_PROPERTY_PREDICTION_GREEN_AT_PROTECTED_TIER`
is reopened for that cell; this is the load-bearing outcome and is reported first. A verdict movement
between non-GREEN classes (e.g. `THEORY_RED` ↔ `INCONCLUSIVE_GRAMMAR`) is recorded as a finding about
the witness's expressibility under the independent meter and does not reopen F1.

**Preservation rule.** Buckets are not tuned after the agreement is seen. An axis below 80 % is a
preserved finding with a per-axis diagnosis from the disagreement confusion table. Exactly one
revival iteration (RV-377-161, fresh blind author) is permitted, and only for a *demonstrable spec
ambiguity* (a rule the brief left open in words that two reasonable authors would fix differently);
a disagreement that reflects a genuine modelling difference (e.g. what fraction of state rewritten
counts as `global`) is kept as the result.

## 4. Prediction P2 (IG-5), frozen

**P2.** The independently selected alphabet covers **every** registered carrier class — memory,
coefficient, program/search, belief, dynamical — by explicit compilation of each of the nine
reference parents with description overhead ≤ 2× the native reference, **or** the author names the
class it cannot express (`NOT_EXPRESSIBLE`, recorded as `NAMED_INEXPRESSIBLE`). Either outcome closes
the gate at model-proxy tier; the RED outcome is an `EXPRESSED` compilation that fails typecheck
against the author's own signatures or exceeds 2×, a forbidden macro kind name, a missing required
class, or an unproducible input type.

Native reference sizes (node counts of registered genotypes; computed by the script at run time):
`m1` `zoo.exemplar_table`, `m2` `zoo.hamming_knn(3)`, `m3` `zoo.soft_retrieval`, `c1`
`zoo.gradient_net(2)`, `p1` `zoo.program_search`, `p2` `zoo.particles(4)`, `p3` `zoo.compiled_search`;
`b1` and `d1` have no zoo adapter and use two native-alphabet reference genotypes written in the
coverage script and typechecked by `morph.typecheck` (11 and 10 nodes by construction; the belief
reference realizes the posterior as a coefficient block, the dynamical reference as a read-modify-write
scalar state — description-level references, not behavioural ones, and recorded as such).

## 5. Status vocabulary (frozen)

* IG-4: `CLOSED__HUMAN_GATE_BYPASSED__MODEL_PROXY` iff P1 holds; `RED__HUMAN_GATE_BYPASSED__MODEL_PROXY`
  with the per-axis numbers otherwise. P1b is reported alongside and qualifies the closure
  (`…__DECLARED_AXES_EXCLUDED_P1B_HELD` / `…_P1B_FAILED`).
* IG-5: `CLOSED__HUMAN_GATE_BYPASSED__MODEL_PROXY` iff P2 is GREEN or NAMED_LIMIT (with the named
  class); `RED__HUMAN_GATE_BYPASSED__MODEL_PROXY` otherwise.
* Neither status is ever written as externally obtained. `KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE`
  and `NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE` stay `FALSE` regardless
  (decomposition §4: IG-4/IG-5 are among the reasons but not the only ones).

## 6. Residues named at freeze (not closed by this record)

1. **Same model family.** The blind authors run on the same served model family as the programme's
   authoring agent (fresh context, not fresh model). Shared training-level priors about "natural"
   primitives are not excluded; the record is a *context* independence proxy, not a *model* one.
2. **Synthesized traces.** K4 candidates are factor tuples, not executed machines; the six measured
   probes are computed from the same-author lifecycle constitution. What the proxy tests is the
   bucketing step, not the measurement step. The four declared axes are vocabulary mappings.
3. **Cost-channel allocation.** The nine charged channels and their formulas remain same-author; the
   `THEORY_RED` cost comparisons (winner vs witness, null vs witness) are not re-derived here.
4. **Native reference for belief/dynamical** is same-author and description-level.
5. **Primitive-level IG-5 is tested at the description level** (typecheck + overhead), not by running
   the independent alphabet through the K4 search or the biosphere.

## 7. Adjudication (filled after the run; §1–6 unedited)

_Empty at freeze._

### 7.1 Execution record

Host billy-old (`billy-laptop-old`, Python 3.11.16, one `nice -n 10` process); tree rsynced from commit
`a387559d` and md5-verified (5/5 files identical) before the run; receipts rsynced back and sha256-verified
(3/3 identical, compared by reading both digest files). Receipts: `microscopes/results/IG4_INDEPENDENT_METER_AGREEMENT_old.json`
(sha256 `a9912afd…`) and `microscopes/results/IG5_INDEPENDENT_ALPHABET_COVERAGE_old.json` (sha256 `557cf892…`);
the blind meter's own output `independence/ig4_independent_buckets_v1_old.json` (sha256 `ab87728a…`). Both
blind authors asserted `served_model: claude-fable-5-1` and recorded the label `HUMAN_GATE_BYPASSED__MODEL_PROXY`.

**Checker validation before reading any result.** The re-aggregator re-derived all 264 native verdicts from the
native buckets (264/264; it aborts otherwise). A shuffle control (independent buckets permuted across the 2334
candidates, seed 1) drops agreement to 0.179 (`state_scales_with`), 0.181 (`serve_scales_with`), 0.713
(`update_locality`), 0.851 (`routing`), so the agreement below is not a property of the comparison code.

### 7.2 P1 (IG-4) — HELD

| axis | agreement, all 2334 | agreement, 226 winners |
|---|---|---|
| `state_scales_with` | 2334/2334 = **100 %** | 226/226 |
| `serve_scales_with` | 2334/2334 = **100 %** | 226/226 |
| `update_locality` | 2315/2334 = **99.19 %** | 215/226 = 95.13 % |
| `routing` | 100 % | 100 % |
| `verifier_gated` | 100 % | 100 % |
| `external_authority` | 100 % | 100 % |
| `sharing`, `retrieval`, `serve_iterations`, `stochastic_serve` (declared) | 100 % | 100 % |

10 of 10 axes ≥ 80 % (P1 requires ≥ 8); 6 of 6 measured axes ≥ 80 % with both scaling axes at 100 % (P1b).
Re-aggregated verdicts: `THEORY_RED` 150 → 150, `THEORY_RED_NULL_DOMINATES` 76 → 76, `INCONCLUSIVE_GRAMMAR`
38 → 38; **0 cells move, 0 flip to GREEN**. The K4 V7 negative (F1 at protected tier, 0/264) does not depend
on the author's bucketing.

**The one disagreement, preserved.** All 19 `update_locality` misses are `native = global`, `independent =
local`; all 19 candidates (11 winners, 8 negative twins) have `retrieval = exact_key`. Diagnosis: the native
meter labels `update_locality` from the candidate's declared locality factor; the independent meter buckets
the *measured* rewritten fraction (rule: `global` iff rewritten/retained ≥ 1/2). Under the exact-key volatility
discount charged by the lifecycle constitution, a declared-global update on those candidates rewrites 0.095–0.462
of the retained state, which any majority rule calls `local`. This is a genuine modelling difference between
"declared" and "charged" locality, not a brief ambiguity: the brief left the local/global boundary to the
author and the author fixed a majority rule before seeing data. No RV-377-161 revival is opened. The finding
is recorded as `NATIVE_UPDATE_LOCALITY_IS_DECLARED_NOT_CHARGED_ON_19_OF_2334_ROWS`; it moves no verdict
because none of the 19 rows' remaining nine axes match a frozen target.

Independent rules as frozen by the blind author (from the receipt): law match = exact integer proportionality
to the literal law on all 24 worlds (no additive offset, no nearest label; constant or multiply-matching traces
unclassified); `log_n_records` inferred as ceil(log2 records); `search_tree` inferred as `search_branch^3`;
`routing` = any difference in per-query work between content dependence 0 and 1; `verifier_gated` /
`external_authority` = any positive charge; the four declared axes mapped by vocabulary and stated as such.

**IG-4 status: `CLOSED__HUMAN_GATE_BYPASSED__MODEL_PROXY__DECLARED_AXES_EXCLUDED_P1B_HELD`.**

### 7.3 P2 (IG-5) — GREEN, all five classes covered

Independent alphabet: 32 kinds over 9 types (state 5: `TABLE`, `STORE`, `BLOCK`, `VEC_STATE`, `POPULATION`;
routing 4; transform 11; update 6; verification 2; interface 4), served-output kind `SERVE`. No forbidden
macro name; no required class missing; type closure clean (no dead output, no unproducible input, no
undeclared type). All nine parents `EXPRESSED`, 0 typecheck errors against the author's own signatures.

| parent | class | independent nodes | native reference nodes | overhead |
|---|---|---|---|---|
| `m1_exact_table` | memory | 7 | 6 (`zoo.exemplar_table`) | 1.17 |
| `m2_nearest_exemplar` | memory | 8 | 6 (`zoo.hamming_knn(3)`) | 1.33 |
| `m3_soft_retrieval` | memory | 10 | 6 (`zoo.soft_retrieval`) | 1.67 |
| `c1_threshold_net` | coefficient | 14 | 11 (`zoo.gradient_net(2)`) | 1.27 |
| `p1_program_search` | program/search | 9 | 7 (`zoo.program_search`) | 1.29 |
| `p2_population_search` | program/search | 9 | 7 (`zoo.particles(4)`) | 1.29 |
| `p3_compile_then_serve` | program/search | 11 | 8 (`zoo.compiled_search`) | 1.38 |
| `b1_finite_belief` | belief | 10 | 11 (native reference in script) | 0.91 |
| `d1_linear_recurrence` | dynamical | 13 | 10 (native reference in script) | 1.30 |

Every overhead ≤ 2×; maximum 1.67 (soft retrieval), minimum 0.91 (belief, where the independent alphabet
carries a distribution-like state kind and a multiplicative reweighting update and is *smaller* than the
native coefficient realization). Two conceptual differences from the native alphabet are visible and are
recorded as evidence that the selection was not a rename: the independent author keeps an explicit
`VEC_STATE` + `MULT_REWEIGHT` pair (a belief carrier as a first-class state family) and a `LINEAR_SCAN`
transform for the dynamical parent, where the native alphabet realizes belief through the coefficient
carrier and dynamical state through a read-modify-write memory phase. Coverage is description-level
(typecheck + occurrence count), as frozen in §6.5.

**IG-5 status: `CLOSED__HUMAN_GATE_BYPASSED__MODEL_PROXY`.**

### 7.4 What moves and what does not

* `GMI_INDEPENDENCE_GATE_DECOMPOSITION_V1.md` §4 register: `IG-4 METER` and `IG-5 ENCODING` move from
  `PENDING_INDEPENDENT_*` to `CLOSED__HUMAN_GATE_BYPASSED__MODEL_PROXY` (addendum appended there).
* `GMI_COMPLETENESS_BOUNDARY_THEOREM_V1.md` §6 "Independence" gap: addendum appended; the standing limitation
  is narrowed from "same-author evaluator, meter and primitives" to "same-author *evaluator and cost-channel
  allocation*; meter bucketing and primitive selection reproduced by a fresh-context model proxy".
* `K4_PROPERTY_PREDICTION_GREEN_AT_PROTECTED_TIER` stays **FALSE** (0/264, now invariant under an
  independently bucketed meter). `KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE` and
  `NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE` stay **FALSE**.
* Residues §6.1–6.5 stand unchanged. Nothing is labelled externally obtained.
