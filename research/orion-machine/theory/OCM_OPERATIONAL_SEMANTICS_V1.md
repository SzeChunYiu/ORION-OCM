# Lane #203 record — operational semantics of the minimal OCM substrate

**Terminal: `PARENT_OBJECT_ADOPTED`.** The substrate is a certificate-gated store with ATMS-label
liveness under a whole-system resource vector; every constraint it must satisfy is owned by a named
parent. `SEMANTICS_V1_FROZEN` is **not** issued: freezing requires the independent assumption audit
(#203 last checkbox; OM-WP3-class obligation), which is unreturned and was not simulated.
**Proof-assistant encoding: `CANNOT_CHECK`** — no toolchain is provisioned; this is a could-not-run,
not a pass.

Date: 2026-09-04 · Umbrella: #194 · Execution master: #197 · Lane: #203
Executable semantics: `reference/ocm_reference_semantics.py` · Tests: `tests/unit/test_ocm_reference_semantics.py`

**Status: NO NOVELTY OR BREAKTHROUGH CLAIM.** Every constraint below is checked exhaustively at
`n = 4` evidence atoms with its denominator, a planted failure, and a mutation asserted applied.

## 0. Substrate-form restatement (operator directive, #194 comment 5539487737, 2026-09-04)

This lane *is* the substrate. The directive asks for "the minimal substrate and constraints" from
which forms of intelligence are to be discovered, so the semantics is written as the smallest
transition system in which the three directive capabilities are even statable: (a) acquire a
procedure with warrant from each of five channels; (b) compose procedures with warrant preserved;
(c) revise representation, strategy and architecture without losing exact authority over what is
already known. Nothing task-level — goals, working state, observations, actions, the transition
function that solves tasks — is fixed here; those are the *emergent forms* the directive leaves to
discovery and are represented only by a behaviour tuple the checker never interprets.

## 1. The substrate

`Σ = (E, Store, V, Ch, compose, revoke, revise, R)`

| component | definition | #194 §3 coordinate |
|---|---|---|
| `E = {0..n−1}` | finite evidence atoms — the units that can later be revoked | part of `E` (evidence/authority state) |
| `Store` | records `(behaviour, profile, scope, epoch, channel, kind, checked_by_V, complete)`; `profile` is an antichain of inclusion-minimal sufficient warrants over `E` — the RCL formal object, **imported from the committed `rcl_model.py`**, not re-implemented | `M` (persistent procedural memory) + `E` |
| `V` | the checker: accepts a certificate against a behaviour; it checks, it never solves (#194 C7) | `V` |
| `Ch` | five admission paths — instruction, demonstration, interaction, experimentation, feedback — each producing a certificate of a stated *kind* | `rho` (parse interface), `X` |
| `compose` | skill composition with warrant and scope preserved | `A` (operators) |
| `revoke(R)` | evidence revocation `R ⊆ E`, epoch increment, re-evaluation | `delta` restricted to `E` |
| `revise` | representation (coarsening of `E`), strategy (admission policy), architecture (store encoding) | `Theta`-level self-change |
| `R` | `(B_theta, B_mut, V_cost, Q_queries, W_update, recourse, abstentions)` | §4 vector, restricted to the coordinates that exist here |

`B_theta` is the substrate's own description (the module's byte length × 8, recomputed each run) and
is constant across every transition — the interpreter constant of lane #202's F4.

**What each channel can warrant** (the substrate's only commitment about channels):

| channel | certificate kind | warrant carried | store status on admission |
|---|---|---|---|
| instruction | positive | ≥ 1 exhibited full warrant | positive-only (`complete = False`) |
| demonstration | positive | ≥ 1 exhibited full warrant (a checked trace) | positive-only |
| interaction | query | warrants assembled from liveness answers, charged to `Q_queries` | positive-only |
| experimentation | closure | exhibited warrants certified to be *all* of them | complete (`complete = True`) |
| feedback | endpoint | none — behaviour only | no warrant; every liveness query abstains |

This is lane #200's hierarchy `I0 < I1 = I2 < I3` (feedback < demonstration/instruction <
experimentation) read as channel semantics, with interaction as query access to any rung.

Liveness of a record under revocation `R` is three-valued: `True` if a warrant survives; `False`
if none survives *and* the profile is complete; `None` (abstain) if none of the exhibited warrants
survives but the profile is positive-only — absence of a live witness is not proof of absence
(#221 required finding 6; RCL-2b).

## 2. Constraints, each with its parent

| id | constraint | exact check at `n = 4` | planted failure (fires) | strongest parent | disposition |
|---|---|---|---|---|---|
| S1 | a record is live only if admitted through `V` and accepted | 2 `V` calls, bad certificate rejected | laundering path (admit without `V`) caught by the invariant | proof-carrying code — Necula 1997 | `PARENT_OWNED` |
| S2 | `profile(p∘q) = min{J ∪ K}`, `Live_{p∘q} = Live_p ∧ Live_q`, `scope(p∘q) = scope(p) ∩ scope(q)` | 20×20 antichain pairs × 8 revocations = 3,200 (n=3, exhaustive); 4,000 seeded pairs × 16 = 64,000 (n=4); two composition routines agree | union scope: 2 countermodels | ATMS label combination for a conjunction (de Kleer 1986, *An assumption-based TMS*: the label of a node derived from two nodes is the minimal set of unions of their environments); intersection of refinement/trust types for scope | `PARENT_OWNED` |
| S3 | after `revoke(R)`, the live set equals the set computed from full profiles | 168 antichains × 16 revocations = 2,688, 0 mismatches; two independently written evaluators agree 2,688/2,688 | positive-only store: 485 cells where truth is live and the store must abstain; 0 false retractions | dependency-directed truth maintenance — Doyle 1979; ATMS label consistency | `PARENT_OWNED` |
| S4 | a coarsening `π` of `E` under a **committed policy** (`over` / `under`) answers every `R ∈ Γ` exactly **iff** every `R` is a `π`-block union; the coarsest exact `π` is the partition generated by `Γ`; an abstaining store is honest, not exact, and is counted separately | all 15 partitions of 4 atoms × 4 registered `Γ` families, both policies evaluated on all 168 profiles, measurability judged by an independently written test (exact-partition counts 1, 4, 1, 4; generated partition coarsest in all four) | merging atoms `{1,2}` while `Γ ∋ {1}`: false-retract witness `[[2]]`, false-retain witness `[[1]]` | Blackwell sufficiency; lane-201 L1 (meet of kernels) | `PARENT_OWNED` |
| S5 | swapping the admission policy leaves every already-admitted record's liveness signature unchanged | 167 records × 16 revocations, 167/167 unchanged | re-admitting a record through feedback drops its warrant: signature changes, caught | monotone knowledge base / no-retroactive-weakening (TMS in-lists) | `PARENT_OWNED` |
| S6 | re-encoding the store as revocation signatures and back is exact | 168/168 round trip; signature injective | encoding dropping one coordinate: 1 collision among 168 | RCL-0 (canonical antichain ⇔ monotone function ⇔ ATMS label uniqueness) | `PARENT_OWNED` |
| S7 | every transition charges the coordinate it consumes; `B_theta` never changes | admit→`V_cost`, interaction→`Q_queries`, compose→`B_mut`, revoke→`W_update` (3 re-evaluated, 2 reopened, 2 abstentions) | a "free" store mutation with no counter change is caught | full-system honesty rule, #194 §4; lane-201 L4 | `PARENT_OWNED` |

**Theorem S4 (stated).** Let `Γ ⊆ 2^E` be the admitted revocation family and `π` a partition of `E`.
A store that keeps, for each warrant `J`, only the set of `π`-blocks `J` meets, and that commits to
a policy for revocations it cannot express (`over`: revoke every touched block; `under`: revoke only
covered blocks), answers `Live_J(R)` exactly for every `R ∈ Γ` and every profile iff every `R ∈ Γ`
is a union of `π`-blocks;
and the coarsest such `π` is `π_Γ`, the partition in which `a ~ b` iff no `R ∈ Γ` separates them.
*Proof.* If `R` is a block union, `J ∩ R = ∅ ⇔ blocks(J) ∩ blocks(R) = ∅`, so the coarse answer is
exact. If some `R ∈ Γ` splits a block `B`, take `J = {a}` with `a ∈ B ∖ R`: the fine answer is
live, but the coarse store cannot distinguish `J` from `{b}`, `b ∈ B ∩ R`, which is dead — so any
policy gives a false retract on one or a false retain on the other (both witnesses are exhibited by
the checker). Coarsest: `π_Γ` makes every `R ∈ Γ` a block union by construction, and any `π` with
that property refines `π_Γ` since two atoms in different `π_Γ`-blocks are separated by some `R`. ∎
*Checker defect, found before merge.* The first draft of the census scored the `abstain` policy
inside the exactness loop; since `abstain` returns `None` on every split, `exact` coincided with
`is_block_union` by construction and the biconditional could not fail — `VACUOUS_CONTRAST`, found
by Cursor Bugbot on PR #279 at `e9a0222`, reproduced, and repaired in place (the PR was unmerged and
nothing was hash-bound to a review target): the two committed policies are now evaluated
separately, abstention is counted as its own quantity (zero exactly on measurable partitions), and
measurability is judged by an independently written test so that mutation M3 is caught for its
registered reason (exact-partition counts go to 15/15/15/15 under the mutation). Recorded in
`OCM_FAILURE_LEDGER.md`.

This is constraint (c) for *representation* revision: the coarsest authority-preserving
representation is determined by the admitted revocation family, exactly as lane #201's L1
determines the coarsest query-preserving representation. `PARENT_OWNED` (Blackwell 1953).

## 3. The parent object

The RCL profile — an antichain of minimal sufficient warrants with liveness under revocation — **is
an ATMS label** (de Kleer 1986): the label of a node is the minimal set of consistent environments
(assumption sets) from which the node follows; retracting an assumption kills exactly the
environments containing it; the node stays *in* iff an environment survives. RCL-0 (canonical
injectivity) is label uniqueness; RCL-4 (full-antichain sufficiency) is label completeness; S2 is
label combination; S3 is label consistency after assumption retraction. The identification is
recorded on the RCL audit (`revocation_complete_learning/RCL_KILL_GATE_AUDIT_V1.md`) as a
parent-collapse of the *formal object*; the counting theorems RCL-1..3 on that object remain
elementary calibration, and the conditional barrier RCL-7 remains the standard NP/coNP implication.

## 4. Resource contract

`R = (B_theta, B_mut, V_cost, Q_queries, W_update, recourse, abstentions)`. Coordinates of #194 §4
absent from this substrate — `B_static` beyond the module itself, `T_seq`, `W_parallel`, `IO`, `BW`,
`Q_quantum`, `E_energy` — are absent, not zero-claimed. Anti-laundering rules realised as checks:
no admission without a charged `V` call (S1, S7/M4); no revocation without charged re-evaluation
(S7); no store change without a counter change (S7 planted); the substrate description is a
constant, never a saving (S7 `B_theta_constant`). Warrant Lift (`H_0(L|B)`, lane #200 Thm A) is the
`B_mut` a complete store needs beyond behaviour; a positive-only store spends less `B_mut` and pays
in `abstentions` — the storage–abstention trade the RCL lane's frontier describes, visible here as
485 abstention cells for the one-witness store.

## 5. Lane checklist disposition

| #203 task | Disposition |
|---|---|
| define `OCM = (X,S,M,G,E,A,Theta,delta,rho,V,H,R)` with finite descriptions | the substrate covers `M, E, A(compose), Theta(B_theta), delta(revoke/revise), rho(channels), V, R`; `X, S, G, H` are task-level and deliberately unfixed (directive: emergent) |
| separate immutable core, static library, mutable memory, parser, verifier, router | core = `B_theta`; memory = `Store`; verifier = `V`; parser = channel kinds; router/library = not modelled |
| deterministic/randomized variants; exact/approximate conversion | deterministic only; the S4 policies (`over`, `under`, `abstain`) are the exact/approximate conversion of a coarse store |
| evidence/provenance/authority dependencies and scoped reopening | profile, scope, epoch; `recourse` counts reopened records |
| WLL state (behaviour, support, evidence, certificate, scope, epoch, status) | `Record` fields; status ∈ {live, retracted, abstain} |
| current vs lifecycle equivalence, Warrant Lift | lane #200 Thm A/D; not restated |
| resource vector and anti-laundering | §4 |
| executable reference semantics and receipts | this module; receipt in `receipts/OCM_LANES_202_203_RECEIPT_V1.json` |
| nontrivial, adversarial, degenerate machines | planted: laundering, positive-only, split coarsening, re-admission, dropped coordinate, free mutation; degenerate: empty profile (certified dead vs abstain) |
| well-formedness / resource conservation first | S1–S7 |
| Transformer→OCM and OCM-fragment→parent simulations | fragment→parent: §3 (ATMS) by identification; Transformer→OCM: `CANNOT_CHECK`, nothing compiled |
| proof assistant, axiom/sorry controls | `CANNOT_CHECK`: no toolchain provisioned |
| independent assumption audit | unreturned; not simulated |
| terminal | `PARENT_OBJECT_ADOPTED` |

## 6. Non-consequences and reopen conditions

Supported: S1–S7 as exact finite statements; Theorem S4; the ATMS identification. Not supported:
that this substrate is *sufficient* for any task, that any form of intelligence emerges from it,
architecture superiority, novelty, priority, language, quantum, publication readiness. No checkbox
in #197 is closed by this file (OPS-012).

Reopens if: the independent assumption audit finds a constraint that encodes its conclusion; a
proof-assistant encoding is provisioned and a stated theorem fails to check; or a channel is shown
to require a warrant kind the five-row table cannot express.
