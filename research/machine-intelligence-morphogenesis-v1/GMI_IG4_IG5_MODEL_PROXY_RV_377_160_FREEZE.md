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
