# COGNITIVE_LADDER_PROTOCOL_V1 — CL-0 measurement and causal-learning substrate

Status: **PROTOCOL. NO RESULT, NO SUPERIORITY CLAIM, NO FIELD CLAIM.**
Programme: issue #143 (Machine Epistemics Cognitive Ladder), rung CL-0, milestone MP-0/MP-1.
Doctrine inherited: #143 §3 (freeze-before-outcome), #50 (scientific thesis), #62 (epistemic experience), #38/#49 (claims review).
Parents named per mechanism in §12. Obligation registry: `docs/theorems/COGNITIVE_LADDER_OBLIGATIONS_V1.json`.

This document fixes the vocabulary, the admissibility conditions, the identification strategy and the
statistical contract for every rung CL-1 … CL-10. It is written **before** any protected outcome and
its hash is the pre-registration commitment of §9.

Nothing here is claimed as new science. The only things first *written down* here are CL-D1 (method
admissibility by description length), CL-D2 (the structural-placebo control), CL-D3 (bits-of-prior
accounting) and CL-D4 (commitment-derived protected draws); each names its parents in §12.

---

## 1. Object of study

A **cognitive lifetime** is a sequence

```text
L = (τ_1, τ_2, …, τ_T)
```

of tasks presented to one persistent machine, interleaved with **custody boundaries** at which the
machine's entire mutable state is written to disk and the process exits. A rung of the ladder is a
tuple

```text
R = (F, Λ, H, C, B, E, P)
```

- `F` — a **task family generator**: a deterministic function from a seed to a task instance, together
  with an exact decision procedure for that instance.
- `Λ` — the **method language**: a finite, enumerable set of candidate cognitive methods, registered
  before execution. `|Λ|` is a declared number, not an informal description (§4, CL-D3).
- `H` — the **hypothesis/evidence channel**: exactly what the machine may observe per episode.
- `C` — the **checker**: an independent exact procedure that certifies or refutes a method on a given
  position. The checker is never a policy donor (§6).
- `B` — the **budget vector**: per-arm limits on search expansions, checker calls, wall time and bytes.
- `E` — the **endpoint set**: primary and secondary, with estimands (§8).
- `P` — the **parent set**: the strongest faithful alternative explanations (§7).

The scientific question of a rung is never "did OCM win". It is: **is there a residual signature after
the strongest parent and the structural placebo have been subtracted?**

---

## 2. Canonical receipt objects

All rungs emit the same seven record types. Every record is canonical JSON, sorted keys, UTF-8, and is
addressed by `sha256` of its canonical serialization. A record is immutable once emitted.

### CL-R1 `CognitiveEpisodeV1`

One unit of verified experience.

```text
episode_id            sha256 of the canonical body
family_id             registered task-family identity
instance_seed         the seed that generated the instance
presented_state       the observation actually given to the machine
permitted_actions     the action set actually offered
outcome               SOLVED | FAILED | ABSTAINED | BUDGET_EXHAUSTED | CANNOT_CHECK
checker_verdict       CERTIFIED | REFUTED | NOT_CHECKED
resource_vector       CL-R7
custody_epoch         which restart epoch produced it
authority             who asserted the outcome (machine | checker | oracle)
```

An episode whose `checker_verdict` is `NOT_CHECKED` may never support a method (CL-T2).

### CL-R2 `MethodRecordV1`

A candidate reusable cognitive object.

```text
method_id             sha256 of (language_id, code_point, scope_declaration)
language_id           identity of Λ, including |Λ|
code_point            the method's index/encoding within Λ
description_bits      |M| in bits under the registered code (§4)
scope_declaration     the set of instances on which the method claims to apply
source_episodes       the episode_ids that induced it
checker_evidence      certificates on positions inside and outside training support
acquisition_cost      CL-R7 at induction time
admissibility         CL-D1 verdict with its three components
revocation_state      LIVE | REVOKED(reason, epoch)
```

A method with `admissibility != ADMISSIBLE` may be stored but may never be counted as a learned
cognitive object in any endpoint.

### CL-R3 `ReuseEventV1`

The only admissible witness of causal use.

```text
reuse_id
method_id
task_id               a fresh task, disjoint from source_episodes by construction
applicability_witness the predicate evaluation that selected this method
execution_trace       the actual operator sequence executed, step by step
counterfactual_arm    which arm this event belongs to (§6)
work_with             resource vector of the invocation
displaced_work        the work the arm would have spent had the method not fired,
                      measured by the matched ablation arm on the same task_id
```

**Presence in memory is not use. Similarity is not reuse.** An endpoint may cite a method only if a
`ReuseEventV1` with a non-empty `execution_trace` exists for it.

### CL-R4 `FailureAttemptV1`

```text
attempt_id, method_id | strategy_id, task_id, scope, budget, outcome, refuted_by
```

A `FailureAttemptV1` records that a strategy failed **at a scope under a budget**. It is never
promoted to impossibility (#143 §3). A later success in the same scope must reopen it and is recorded
as `scope_recovery`.

### CL-R5 `RepresentationChangeV1`

```text
change_id, from_representation, to_representation, evidence, search_cost_before,
search_cost_after, held_out_discrimination, construction_cost
```

`held_out_discrimination` must name at least one held-out world on which the old and new
representations **disagree** and the new one is correct. Without it the record is inadmissible.

### CL-R6 `SubgoalEventV1` / `ProbeEventV1`

```text
subgoal_id | probe_id, task_id, proposed_intermediate, justification,
downstream_value_measured, refusal (when the learned subgoal was declined)
```

Refusals are recorded with the same weight as invocations; a method that never declines is a
suspicious method (§10, attack A13).

### CL-R7 `ResourceVectorV1`

The common cost vector. Every arm reports every coordinate or `null` with a stated reason.

```text
immutable_source_bytes        hand_authored_prior_bytes      pretraining_data_bytes
post_freeze_examples          parameter_count                parameter_bytes
persistent_state_bytes        replay_bytes                   index_bytes
active_bytes_per_query        search_expansions              checker_calls
tool_calls                    storage_reads                  storage_writes
acquisition_cpu_seconds       query_cpu_seconds              gpu_seconds
wall_seconds                  peak_rss_bytes                 energy_joules
revision_work                 index_maintenance_work         recovery_work
N_persistent_objects          k_touched_objects              index_probes
```

Cold and warm executions are reported separately and are never averaged together (E3, #143 §2).

---

## 3. Custody: what makes a restart real

**CL-T1 (custody, PROVED by construction).** A scored reuse is admissible only if, between the
acquiring episode and the reuse, the following occurred and is witnessed in the receipt:

1. the machine serialized its state to a path `S`;
2. the acquiring **operating-system process exited**, with its exit status recorded;
3. a new process was started with a different PID;
4. the new process read `S` and its digest matched the digest written before exit;
5. no file descriptor, shared-memory segment, environment variable or in-process cache carried a
   value derived from the acquiring process, other than through `S`.

The receipt records `(pid_before, pid_after, state_digest_before, state_digest_after)`. A run in which
`pid_before == pid_after` emits the terminal `CUSTODY_VIOLATION` and is not analysable. In-process
"simulated restart" is design evidence only and is never confirmatory (#143 §13).

---

## 4. CL-D1 — method admissibility by description length

The single most likely reviewer attack is: *the method store is an answer cache with extra steps*
(#143 §9, attacks A2 and A11). Ablation alone does not defeat it, because deleting a cache also
removes an advantage. We therefore make the distinction **structural**, checked before any outcome is
scored.

Let `D` be the set of source episodes of a method `M`, encoded under the registered instance code as
`bits(D)`. Let `bits(M)` be the length of `M`'s code point in `Λ` under a prefix code fixed with `Λ`.
Let `bits(D | M)` be the residual: the bits needed to reconstruct every label in `D` given `M`
(zero when `M` reproduces `D` exactly).

**CL-D1.** `M` is **ADMISSIBLE** iff all three hold:

```text
(a) compression   bits(M) + bits(D | M) < bits(D)              (strict)
(b) extrapolation scope(M) ⊋ support(D), and C certifies M on a
                  registered sample of scope(M) \ support(D) drawn
                  from magnitudes strictly greater than max(support(D))
(c) independence  C is an exact procedure that does not consult M,
                  the episode store, or any learned state
```

**CL-T2 (cache exclusion, PROVED).** A verbatim answer cache over `D` has
`bits(M) ≥ bits(D)` and `scope(M) = support(D)`, so it fails both (a) and (b). Therefore no object
admitted under CL-D1 is an answer cache over its own training support. Limitation: CL-D1 does not
exclude a *compressed* cache that happens to lie in `Λ`; that residual is what (b) tests empirically
and what the placebo of §5 bounds.

**CL-T3 (no free lunch from Λ, STATED).** CL-D1 is relative to `Λ`. A `Λ` that contains exactly one
method — the correct one — trivially satisfies (a) and (b) while the machine has learned nothing.
This is exactly what §5's bits-of-prior accounting measures, and why `|Λ|` is a mandatory declared
field of every `MethodRecordV1`.

---

## 5. CL-D3 — bits of prior versus bits acquired

Attack A1 (*OCM's hypothesis language already contains the answer*) is answered with a number, not an
argument.

Let `Λ` be the registered method language and `Λ_E ⊆ Λ` the subset consistent with the evidence `E`
the machine actually observed. Define

```text
prior_bits     = log2 |Λ|                              the search problem the designer posed
acquired_bits  = log2 |Λ| − log2 |Λ_E|                 information the evidence supplied
residual_bits  = log2 |Λ_E|                            what remains undetermined by evidence
```

**Every method claim reports `(prior_bits, acquired_bits, residual_bits)`.** A method for which
`acquired_bits ≈ 0` was given, not learned, and is reported as such regardless of its downstream
benefit. The headline efficiency endpoint is therefore always accompanied by

```text
benefit per acquired bit = Δwork / acquired_bits
```

so that a large `Δwork` bought with a hand-picked `|Λ| = 2` language is visibly worthless.

**CL-T4 (prior-dominance terminal).** If for every registered method `acquired_bits < 1`, the rung
emits `REPRESENTATION_PRIOR_DOMINATES` regardless of measured work reduction.

`Λ` must also contain **decoys**: at least one method that fits all training evidence and is wrong on
held-out worlds (#143 CL-3). A `Λ` in which every consistent hypothesis is correct is an inadmissible
`Λ`, because it makes (b) vacuous.

---

## 6. CL-D2 — the identification strategy: four arms, not two

Removal ablation alone is confounded. Deleting a method changes the store size, the index shape, the
retrieval path and the cache locality at the same time as it removes the knowledge. A reviewer is
entitled to say the measured Δ is infrastructure, not cognition.

Every scored reuse claim therefore runs **four matched arms on the same task_id, same seed, same
budget**:

```text
A_live      full machine, method M present and LIVE
A_removed   M deleted from the store
A_revoked   M present but revocation_state = REVOKED (store shape identical to A_live)
A_placebo   M replaced by M~, a structural placebo (below)
```

A **structural placebo** `M~` is constructed to match `M` on every non-semantic dimension:

```text
same description_bits          same index entries and index depth
same scope_declaration size    same retrieval cost to the selection point
same record byte length        same number of source_episodes
different semantics            M~'s predicate is a registered permutation of M's that is
                               refuted by C outside support(D)
```

`M~` therefore fires the same machinery and pays the same lookup, but carries no correct knowledge.

**The purified effect is defined as**

```text
Δ_purified = work(A_placebo) − work(A_live)
```

and **not** `work(A_removed) − work(A_live)`. The removal and revocation arms are reported as
secondary: `work(A_removed) − work(A_placebo)` isolates the pure infrastructural cost of holding an
object at all, which is a cost the programme must charge itself, not hide.

**CL-T5 (placebo-null terminal).** If `Δ_purified` is not distinguishable from zero at the registered
level while `work(A_removed) − work(A_live)` is large, the rung emits
`REUSE_EFFECT_IS_INFRASTRUCTURAL` — a negative terminal, published as such.

A fifth arm is run wherever the family permits:

```text
A_cache     an explicit solved-position cache, matched to persistent_state_bytes of M
```

`A_cache` must generalize at chance outside `support(D)` while `A_live` generalizes exactly. This is
the direct empirical answer to attack A2.

---

## 7. Parents: first right of refusal

A parent is not a strawman baseline. **The strongest plausible alternative explanation gets first
right of refusal on every effect.** For each rung the parent set must include, where applicable:

```text
P0  the task-specific conventional algorithm (exact DP / Grundy / A* / entropy rule)
P1  the same algorithm with persistent memoization across the same custody boundaries
P2  a small neural model trained on identical post-freeze episodes, checkpointed and
    reloaded across the same custody boundaries
P3  an RL / meta-RL learner where the family admits one
P4+ the N-ladder of #143 §CL-10 as rungs mature
```

`P1` is mandatory and is the parent most likely to explain a naive result: a persistent memo table is
also "learn, persist, restart, reuse". The programme's claim only begins where `P1` is beaten on an
endpoint `P1` cannot reach — generalization to magnitudes outside training support, or local revision
after a rule change (§8, secondary endpoints).

**Parent fairness is a checklist, not a promise.** Each parent record states: identical episode
stream, identical restart custody, identical wall/compute budget, identical checker access, and the
hyperparameter search policy actually used. A parent whose search policy was weaker than OCM's own
tuning effort is flagged `PARENT_UNDERTUNED` and its comparison is not admissible.

`P2` is reported as a **learning curve over post-freeze examples**, never as a single point. A
single-point neural comparison is treated as a protocol defect.

---

## 8. Endpoints and estimands

### Primary capability gate (must pass before any efficiency endpoint is read)

```text
exact task success on the protected draw, with a prospectively declared
non-inferiority margin δ against the strongest parent
```

No efficiency claim survives a failed capability gate (#143 §CL-10).

### Primary efficiency estimand

For each protected task `i` in family `f`:

```text
r_i = work(A_live, i) / work(A_placebo, i)
```

The estimand is the **family-clustered median of `r_i`**, reported with a bias-corrected bootstrap
interval resampling **families**, not tasks. Tasks within a family are not independent units
(#143 §7).

The test is a **permutation test on family-level paired differences**, with the permutation seed
derived from the pre-registration commitment (§9). Effect sizes are reported with intervals; no
p-value is reported without its effect size and its interval.

### Regime endpoints (the actually interesting ones)

A single ratio is a point claim. The programme's thesis is about a **regime**, so the primary
architectural endpoints are slopes:

```text
S1  d(query work) / d(N)        with k reported alongside; the claim is that
                                query work tracks k and not N (#143 ME-S6)
S2  d(acquisition work) / d(families acquired)
S3  dependency-cone size / store size, after a single revocation
S4  stale survivors and collateral invalidations, counted exactly
S5  harmful-transfer rate: fraction of fresh tasks where a fired method
    increased work or produced a wrong answer
```

`S5` is mandatory and is reported in the abstract of any paper claiming transfer. A programme that
reports only its wins is not reporting a regime.

### Cost-of-being-wrong

Every reuse benefit is reported net of the revision cost incurred when a learned method is later
falsified: `recovery_work` and `index_maintenance_work` are added to the OCM arm, never omitted.

---

## 9. CL-D4 — mechanically verifiable pre-registration

Human-subjects pre-registration relies on a trusted timestamp and good faith. A machine programme can
do better: **make the protected tasks a deterministic function of the plan.**

```text
plan            = canonical JSON of {Λ, families, endpoints, budgets, arms,
                  parent configs, analysis script sha256, exclusion rules,
                  stopping rules, δ, α, multiplicity policy}
commitment      = sha256(plan)
protected_seed  = sha256(commitment ‖ "protected-draw-v1")
permutation_seed= sha256(commitment ‖ "permutation-v1")
```

The protected task draw is generated **from `protected_seed`**. Therefore:

- the tasks cannot have been chosen after seeing outcomes without changing `commitment`;
- any third party can re-derive the exact protected draw from the published plan and check it;
- a changed analysis script changes `commitment` and therefore changes the tasks, which makes silent
  analysis drift mechanically visible.

`commitment` is published as an annotated git tag before execution, and every receipt carries it.
A receipt whose `commitment` does not match the tag is inadmissible.

**CL-T6 (pilot separation).** Pilot runs use `pilot_seed = sha256(commitment ‖ "pilot-v1")`, a
disjoint stream. Pilot data may repair engineering and select feasible scales. Pilot data may never
appear in a confirmatory table. A pilot result that is later reported as confirmatory is a
`PROTOCOL_VIOLATION` terminal.

---

## 10. Attack table (required in every paper)

Each rung's report must contain this table filled in: attack → control → result → remaining
limitation. An empty "remaining limitation" cell is itself a review finding.

| # | Attack | Control in this protocol |
|---|---|---|
| A1 | Λ already contains the answer | §5 bits-of-prior; mandatory decoys; benefit per acquired bit |
| A2 | Methods are stored solutions | CL-D1(a)(b); `A_cache` arm; extrapolation beyond training magnitude |
| A3 | OCM gets more memory/tool/checker access | identical `H`, `C`, `B` per arm, recorded in every receipt |
| A4 | Neural comparator under-tuned | `PARENT_UNDERTUNED` flag; declared search policy; learning curves |
| A5 | Pretraining charged, hand-authored code free | `immutable_source_bytes` + `hand_authored_prior_bytes` in CL-R7 |
| A6 | Later tasks are easier (fake amortization) | difficulty-matched protected draw; order permutations |
| A7 | Task ordering chosen after outcomes | §9 commitment-derived order seed |
| A8 | Sparse query work hides global indexing | `index_maintenance_work`, `index_bytes`, cold/warm split |
| A9 | Local revision looks exact because dependencies are incomplete | exact cone ground truth from the generator; stale-survivor count |
| A10 | Failure memory is a task-ID blacklist | scope-recovery family: same task, changed rules, must re-succeed |
| A11 | Reuse effect is infrastructural | §6 `A_placebo`; `Δ_purified` as the primary estimand |
| A12 | Representation discovery is selection from a tiny menu | `|Λ|`, decoys, `prior_bits` |
| A13 | Subgoal is encoded in state features | refusal-required layouts; CL-R6 refusal records |
| A14 | OCM refuses hard cases and looks reliable | abstention rate is a reported endpoint, not an exclusion |
| A15 | Storage/verification cost dominates the lifetime | full CL-R7 on every arm; Pareto reporting, no scalar score |
| A16 | Results depend on one machine/seed/order | MP-7 fresh-host replication; multiple orders and seeds |
| A17 | A conventional symbolic/DB architecture explains it | `P1` persistent memoization parent, mandatory |
| A18 | Transformer + memory + tools reproduces the signature | N4–N7 ladder at CL-10; stated as an open risk until run |

---

## 11. Terminals

The rung emits exactly one primary terminal from the registered set (#143 §10), plus any secondary
terminals. Terminals introduced by this protocol:

```text
CUSTODY_VIOLATION                 §3 restart was not real
REUSE_EFFECT_IS_INFRASTRUCTURAL   §6 placebo reproduces the effect
METHOD_INADMISSIBLE_BY_MDL        §4 no candidate passes CL-D1
PRIOR_DOMINATES_ACQUISITION       §5 acquired_bits below threshold
PARENT_UNDERTUNED                 §7 comparison not admissible
PROTOCOL_VIOLATION                §9 pilot/confirmatory contamination
```

A negative terminal is a publication result. It narrows the field claim; it never triggers benchmark
shopping (#143 §10).

---

## 12. Parents of this protocol

Nothing above is claimed as new mathematics or new methodology in general; each device has a parent.

| device | parent |
|---|---|
| CL-D1 description-length admissibility | minimum description length (Rissanen); two-part codes; Occam-style learnability arguments |
| CL-D2 structural placebo | sham-surgery and sham-stimulation controls in experimental medicine; placebo arms in RCTs |
| CL-D3 bits-of-prior accounting | version-space / information-gain analysis; Bayesian prior-elicitation critique |
| CL-D4 commitment-derived draws | cryptographic commitment schemes; verifiable random functions; clinical-trial pre-registration |
| family-clustered inference | cluster-randomized trial analysis; hierarchical models |
| non-inferiority gate before efficiency | non-inferiority trial design |
| exact game families and P-positions | Sprague–Grundy theory; Bouton's analysis of Nim |
| custody / restart discipline | crash-consistency and durability testing in storage systems |

The contribution claimed is the **assembly**: applying these controls simultaneously to a persistent
machine so that a lifetime-learning claim has an identification argument rather than a benchmark
table.

---

## 13. What this protocol does not do

- It does not establish Machine Epistemics as a field (#143 §15).
- It does not license any cross-domain claim; §9 freezing is necessary, not sufficient.
- It does not make the finite exact games interesting in themselves. They are a microscope.
- It says nothing about scale. `PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM` remains available at every rung.
