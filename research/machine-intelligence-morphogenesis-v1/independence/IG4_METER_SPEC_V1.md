# IG-4 Independent Meter Specification, V1 (spec-only brief for a blind author)

Record: RV-377-160. Gate: IG-4 METER AUTHORSHIP (bucketing of measured lifecycle resources).
This brief is the ONLY thing the independent author receives, together with one data file
(`k4_v7_traces_v1.json`, format in §3). It contains no code, no reference to any existing meter,
and no numeric bucket edge. Everything the author decides is the author's own.

## 1. Task in one paragraph

A candidate machine has been measured on a panel of synthetic "worlds". For each candidate you
receive a resource trace (§3). You must write a pure-Python 3.11 program (standard library only)
that maps every trace to a bucket on each of ten registered axes (§2), by a rule that is fixed
before you look at any particular candidate, that does not depend on how many candidates fall in
each bucket, and that you justify in writing. Your output is compared later, by someone else,
against another meter's buckets. You will never see that other meter. Do not try to guess it;
build the meter you believe is right and say why.

## 2. The ten registered axes and their registered value vocabularies

Bucket values are strings and must be spelled exactly as below (comparison is string equality).

| axis | registered values |
|---|---|
| `state_scales_with` | one of the 22 state-law names in §2.1, or `UNCLASSIFIED_STATE_LAW` |
| `serve_scales_with` | one of the 21 serve-law names in §2.2, or `UNCLASSIFIED_SERVE_LAW` |
| `update_locality` | `none`, `local`, `global` |
| `routing` | `none`, `input_dependent` |
| `sharing` | `shared`, `unshared` |
| `retrieval` | `none`, `exact_key`, `metric` |
| `serve_iterations` | `one`, `many` |
| `stochastic_serve` | JSON `true` / `false` |
| `verifier_gated` | JSON `true` / `false` |
| `external_authority` | JSON `true` / `false` |

### 2.1 State-law names (`state_scales_with`)

Each name states which world quantities the candidate's retained state grows with. World
quantities are the keys of every probe world (§3). The name is the definition; the functional
form (proportional, product, sum, square, ...) is what the name says.

| name | grows with |
|---|---|
| `n_features` | `features` |
| `n_retained_sections` | `retained` |
| `n_records` | `records` |
| `n_hypotheses` | `hypotheses` |
| `n_constraints` | `constraints` |
| `program_size` | `program` |
| `hidden_width` | `hidden` |
| `state_dim` | `state_dim` |
| `kernel_size` | `kernel` |
| `edge_features` | `edges` |
| `n_positions_squared` | the square of `positions` |
| `n_positions_times_window` | the product `positions` × `window` |
| `n_experts_times_expert_size` | the product `experts` × `expert_size` |
| `corpus_size` | `corpus` |
| `rank_times_dim` | the product `rank` × `dim` |
| `n_members_times_member_size` | the product `members` × `member_size` |
| `proposer_plus_verifier` | the sum `proposer` + `verifier` |
| `dynamics_model_size` | `dynamics` |
| `policy_size` | `policy` |
| `vocab_times_context` | the product `vocab` × `context` |
| `score_model_size` | `score_model` |
| `latent_dim_plus_decoder` | the sum `latent` + `decoder` |

### 2.2 Serve-law names (`serve_scales_with`)

Which world quantities the candidate's per-query work grows with.

| name | grows with |
|---|---|
| `n_features` | `features` |
| `n_retained_sections` | `retained` |
| `log_n_records` | the logarithm of `records` (integer-valued in the traces; the base and rounding convention are yours to infer from the data and to state) |
| `n_hypotheses` | `hypotheses` |
| `search_tree` | the node count of a bounded-depth search tree with branching factor `search_branch` (the depth is a fixed small integer; infer it from the data and state it) |
| `hidden_width_times_length` | the product `hidden` × `sequence_length` |
| `state_dim_times_length` | the product `state_dim` × `sequence_length` |
| `kernel_size_times_positions` | the product `kernel` × `positions` |
| `n_edges_times_rounds` | the product `edges` × `rounds` |
| `n_positions_squared` | the square of `positions` |
| `n_positions_times_window` | the product `positions` × `window` |
| `active_expert_size` | `expert_size` |
| `retrieval_plus_core` | the sum `retrieval` + `core` |
| `core_plus_rank` | the sum `core` + `rank` |
| `n_members_times_member_size` | the product `members` × `member_size` |
| `n_proposals_times_check` | the product `proposals` × `check` |
| `rollout_depth_times_branch` | the product `rollout_depth` × `branch` |
| `policy_size` | `policy` |
| `sequence_length` | `sequence_length` |
| `n_steps_times_model` | the product `steps` × `model` |
| `decoder_size` | `decoder` |

A trace that follows none of the named laws must be bucketed `UNCLASSIFIED_STATE_LAW` /
`UNCLASSIFIED_SERVE_LAW`. Do not invent a nearest label. Traces are exact integers; whether you
demand exact equality with the law, equality up to a positive constant factor, or a fitted
tolerance is your decision, stated in your justification.

### 2.3 Meaning of the eight categorical axes

* `update_locality`: how much of the retained state is rewritten by one feedback event.
  `none` = nothing is rewritten; `local` = a small part; `global` = all or most of it. Where the
  boundary between `local` and `global` lies is your decision, fixed in advance and justified.
* `routing`: `input_dependent` if the amount of per-query work depends on the content of the
  query (how much of the input the answer must consult); `none` if it does not.
* `sharing`: `shared` if one block of parameters is reused across positions / members;
  `unshared` if each position or member has its own.
* `retrieval`: `exact_key` if the candidate looks up stored items by exact key match;
  `metric` if it retrieves the nearest stored items under a metric; `none` otherwise.
* `serve_iterations`: `many` if serving one query makes repeated passes; `one` if a single pass.
* `stochastic_serve`: `true` if the served answer to an identical query can vary between calls.
* `verifier_gated`: `true` if the candidate spends work checking its own answer before serving.
* `external_authority`: `true` if the candidate consults an authority outside its own state
  (an external intervention is charged) during its lifecycle.

## 3. Trace file format (`k4_v7_traces_v1.json`)

```json
{
 "schema": "GMIIG4TraceFileV1",
 "n_probe_worlds": 24,
 "world_quantities": ["branch", "check", "context", "..."],
 "probe_worlds": [ {"branch": 7, "check": 3, "...": 0}, "... 24 worlds ..." ],
 "candidates": {
   "<ref>": {
     "ref": "<ref>", "task_index": 0, "role": "winner|witness|twin|null",
     "retained_state_cells":  [ "one integer per probe world, same order as probe_worlds" ],
     "per_query_work_units":  [ "one integer per probe world, same order as probe_worlds" ],
     "cell_scale_probe": {"world": {"...": 0}, "retained_state_cells": 0, "per_query_work_units": 0},
     "feedback_probe": {"retained_state_cells": 0, "state_cells_rewritten_per_feedback_event": 0.0},
     "content_dependence_probe": {"per_query_work_at_dependence_0": 0.0, "per_query_work_at_dependence_1": 0.0},
     "verification_probe": {"per_query_work_units": 0, "verification_work_per_query": 0.0},
     "external_probe": {"external_interventions_per_lifecycle": 0.0},
     "declared_structure": {
        "parameter_blocks_shared_across_positions": true,
        "lookup_mechanism": "none | exact_key_match | nearest_by_metric",
        "serve_passes_per_query": "single | repeated",
        "answer_varies_across_identical_queries": false
     }
   }
 }
}
```

* The 24 probe worlds assign every world quantity an integer in [2, 24]; quantities vary
  independently of one another across worlds. `retained_state_cells[i]` and
  `per_query_work_units[i]` are the candidate's measured counts in `probe_worlds[i]`.
* `cell_scale_probe` is one more world (the one the candidate was actually evaluated in) with its
  counts.
* `feedback_probe` gives the retained state size in that world and the number of state cells one
  feedback event rewrites (may be fractional because it is an expectation).
* `content_dependence_probe` gives per-query work in the same world when the query's content
  dependence is 0 and when it is 1.
* `verification_probe` gives per-query work and the part of it spent on checking the answer.
* `external_probe` counts external interventions charged per lifecycle.
* `declared_structure` is declared, not measured: these four facts about a candidate are read off
  its construction. The four corresponding axes (`sharing`, `retrieval`, `serve_iterations`,
  `stochastic_serve`) therefore reduce to a vocabulary mapping. Say so in your header; the
  measured axes are the other six.
* `role` says why the candidate is in the file; it carries no information about what the right
  buckets are and must not be used by the meter.

## 4. Deliverable

File `ig4_independent_meter_v1.py`, pure Python 3.11, standard library only, no imports from any
other project file. It must:

1. expose `bucket_trace(trace: dict, probe_worlds: list[dict]) -> dict` returning exactly the ten
   axis keys of §2 with values from the registered vocabularies;
2. run as `python3 ig4_independent_meter_v1.py <traces.json> <out.json>` and write
   `{"schema": "GMIIG4IndependentBucketsV1", "served_model": "...", "label":
   "HUMAN_GATE_BYPASSED__MODEL_PROXY", "rules": {...}, "buckets": {"<ref>": {10 axes}}}` with one
   entry per candidate in the input;
3. carry a module docstring header with: `served_model: <the model id you are running as>`,
   the label `HUMAN_GATE_BYPASSED__MODEL_PROXY`, the date, and a written justification of every
   bucketing rule (the law-matching rule and its tolerance; the `update_locality` boundary; the
   `routing`, `verifier_gated`, `external_authority` thresholds; the vocabulary mapping for the four
   declared axes), each stated as a rule fixed before inspecting any candidate.
4. never read anything other than the one trace file passed on the command line.

Rules on conduct: read only this brief and the trace file; do not read anything else in the
repository, do not read version-control history, do not execute anything beyond a syntax check of
your own file. Decide your rules from the definitions in §2 and the format in §3, then implement
them. A rule tuned to the observed distribution of traces is not admissible.
