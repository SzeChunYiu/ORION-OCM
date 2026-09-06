# Machine Epistemics Field Dynamics V1

Parent issue: #345. Base: `05f08fe71466d4dd192294fe00cf26d526026522`.

This file defines the dynamics over the registered state `Ξ` from `FIELD.md`. Each law below is either derived from already registered Machine Epistemics results, a scoped theorem in this package, parent-owned, or explicitly open. No finite checker upgrades an all-size claim.

## 1. Seven transition families

Write `Ξ --τ--> Ξ'` for an admissible transition.

### F — fast inference

`F_q`: atomize → seed → navigate → fire → extract → compose → check.

A fast step may change `P.runtime` activation, traces and candidate sets, and must account for cost in `B` and append its execution receipt to `X`. It may **not** add registered truth warrant, external authority, evidence identity, scope, or world state. Under a fixed registered snapshot it either converges within the declared numerical/budget contract or terminates with a typed non-success result. Exact equality `Ξ'=Ξ` denotes semantic projection equality only, never literal audit-state equality.

### E — evidence and revision

`E_e`: admit, revoke, reinstate, supersede, expire, add/remove a registered contradiction/nogood under the applicable protocol.

Warrant changes only through explicit support/certificate changes. `reinstate(e)` and `relearn(e')` are different transitions even if current behaviour becomes equal.

### L — learning

`L_o`: a registered instruction, demonstration, observation, interaction outcome, experiment or other acquisition event updates a compatible hypothesis/model class and may admit query-relative procedures with provenance.

An exact/registered observation may eliminate hypotheses. Unregistered reward/feedback may update routing or weights but does not change truth warrant.

### R — representation and organisation

`R_J`: quotient/abstraction, consolidation, conservative extension, fibre split/merge/relink, operator-library change, or governed Jump.

A quotient is reusable only under the registered sufficiency conditions: navigation lumpability/intertwining, warrant measurability and answer-factorization for the registered query/revision family. An additive structural change carries lineage/adoption evidence and supports exact quarantine rollback. A governed Jump additionally requires a registered obstruction/ceiling certificate and external adoption authority.

### T — temporal/environment

`T_x`: exogenous revision of the registered world/model context. The machine may or may not observe the change immediately.

Persistence is always relative to a registered revision envelope. Missing upper closure is `CANNOT_CHECK`, not evidence that no change occurred.

### M — communication and multi-agent

`M_msg`: testimony, dialogue commitment, shared evidence, codec/meaning transfer, rendering and distributed update between machine or human/machine epistemic states.

Speaker/source authority does not become world-truth authority through repetition. Shared assumptions remain shared after composition; independence must be separately warranted.

### G — governance, action and self

`G_u`: query, experiment, clarification, abstention, external action proposal/commit, self-diagnosis, self-change proposal, shadow evaluation, external adoption and rollback.

Truth warrant, bounded-risk actionability and action permission are different coordinates. Self-model evidence may diagnose or propose; it cannot self-authorize.

## 2. FD-01 — authority non-amplification

**Status: `DERIVED_FROM_EXISTING_FOUNDATION`.**

For every internal transition and authority coordinate `c`, the authority of a derived object is bounded above by the meet of its operator/bridge and input authorities. In particular an internal operator whose `commit` coordinate is bottom cannot derive positive external-commit authority from its tails.

Only a registered external-authority source may add positive commit authority. This is a lattice/information-flow rule, not evidence that a particular external source is legitimate.

The scope is authority **of each derivation**, not coordinatewise decrease of a
whole repository containing newly copied records. For a registered rule with
ceiling `c` and required premises `a_i`, the admissibility predicate is
`a_out ≤ c ∧ ⋀_i a_i`. Induction on a finite derivation proves that no path
exceeds its source/rule ceilings. `authority_preserved` checks a proposed output
against this bound and rejects a forged positive commit coordinate.

## 3. FD-02 — warrant/source conservation

**Status: `DERIVED_FROM_EXISTING_FOUNDATION`.**

Every `LIVE` derived object has at least one consistent registered support alternative after dependence flattening and post-composition nogood filtering. A navigation score, neural confidence, rank, retrieval frequency or statistical population guarantee is not itself an individual truth support.

If all candidate supports are removed, contradicted, outside scope, or only upper/possible supports, the result is not silently `LIVE`.

## 4. FD-03 — local revision law

**Status: `DERIVED_FROM_EXISTING_FOUNDATION`, relative to an explicit dependency model.**

Let `Δ` be the set of atoms/evidence whose registered liveness/value changed. Let `Impact_D(Δ)` be the least dependency-closed set. Objects outside the cone retain their registered warrant/liveness under that dependency model; objects inside are obligations to reopen or recheck, not automatic retractions.

This theorem gives no authority that `D` contains every hidden dependency. Dependency completeness is a separate model-closure obligation.

Proof scope: each node's update function reads only its declared predecessor
nodes and its unchanged local parameters. The least reachability cone includes
every node reachable from changed input/parameter/nogood identities. Induction
on a finite evaluation schedule leaves all other inputs and outputs unchanged;
for cyclic systems this additionally requires the registered unique fixed-point
semantics or preservation of the same fixed-point selection. Nogood, scope,
expiry, operator and global-normalization changes must themselves appear as
dependency roots. Any changed tail reopens all heads; reopening is distinct from
the all-tail warrant gate for firing an inference.

## 5. FD-04 — fast/slow fixed-point stability

**Status: `PROVED_SCOPE_LIMITED`.**

Let `P,P'` be nonnegative row-substochastic matrices, `s,s' ≥ 0` with `||s||_1,||s'||_1 ≤ 1`, and `α∈(0,1]`. Define the unique restart fixed points

`a*  = α s  + (1-α) P^T  a*`

`a*' = α s' + (1-α) P'^T a*'`.

Then

`||a*' - a*||_1 ≤ ||s'-s||_1 + ((1-α)/α) ||P'-P||_∞`,

where `||M||_∞ = max_i Σ_j |M_ij|`.

### Proof

Set `β=1-α` and `d=a*'-a*`. Subtract the fixed-point equations:

`d = α(s'-s) + β P^T d + β(P'-P)^T a*'`.

For a nonnegative row-substochastic `P`, `||P^T z||_1 ≤ ||z||_1`. Also the restart fixed point has `||a*'||_1≤1`. Therefore

`||d||_1 ≤ α||s'-s||_1 + β||d||_1 + β||(P'-P)^T||_1 ||a*'||_1`

`≤ α||s'-s||_1 + β||d||_1 + β||P'-P||_∞`.

Since `1-β=α`, division by `α` gives the stated bound. ∎

Interpretation: a slowly changing seed/kernel yields a quantitatively controlled change in the **activation fixed point**. This is not a bound on truth, semantic correctness, warrant, or answer stability unless the downstream decision also has a registered margin/certificate.

The exact checker enumerates 20,736 two-state kernel/seed pairs as a finite hostile calibration; the all-size statement is the proof above. It rejects signed/superstochastic kernels, non-unit seed mass, dimension mismatch, floating-point inputs and `α` outside `(0,1]` as `CANNOT_CHECK`. It reuses 144 exact solutions inside this fixed immutable calibration; this is not caching mutable epistemic conclusions.

For a time-indexed contraction `f_t`, with `a_{t+1}=f_t(a_t)`, fixed point
`z_t=f_t(z_t)`, factor `β<1` and drift `δ_t=||z_{t+1}-z_t||`, triangle inequality
gives `e_{t+1}≤β e_t+δ_t` for `e_t=||a_t-z_t||`, hence
`e_t≤β^t e_0+Σ_{k<t}β^(t-1-k)δ_k`. For constant drift bound δ this is at most
`β^t e_0+δ(1-β^t)/(1-β)`. This reconstruction belongs to contraction tracking,
including [Bernstein and Dall'Anese (2018)](https://arxiv.org/abs/1804.09768v2).
Async, changing-factor and downstream decision claims require their extra
hypotheses and are not proved by this recurrence.

## 6. FD-05 — epistemic hysteresis and reversibility

**Status: `PROVED_SCOPE_LIMITED`.**

There are different notions of return:

- **semantically reversible:** restoring the same immutable evidence identity and registered structure can restore the same `π_sem(Ξ)`;
- **behaviour-reversible:** a new evidence identity may restore the same current answers while changing future revocation/reopening behaviour;
- **irreversible:** an external world effect, deleted history, unquarantined structure, changed model semantics or lost evidence identity prevents exact inverse replay.

Thus `π_sem(reinstate_e(revoke_e(Ξ)))=π_sem(Ξ)` can hold when the identity was
previously admitted and no intervening changes affect its registered semantics.
The full states differ: history has grown and expenditure has increased. Calling
the complete append-only state transition an exact inverse is **refuted** by the
two-event fixture. `relearn(e')` remains lifecycle-distinct. Structural rollback
restores the semantic projection only when produced structure and caches are
lineage-stamped/quarantined and the predecessor representation is recoverable.

## 7. FD-06 — epistemic persistence and viability

**Status: `PARENT_SUFFICIENT` for the general controlled-invariance mathematics; Machine Epistemics supplies the typed safe set.**

For a registered commitment define a viable state as one in which:

1. required propositions have the required liveness/contradiction status;
2. scope and epoch apply;
3. required authority is present;
4. statistical/risk conditions meet the declared task contract when the action uses them;
5. the relevant property remains valid through the declared revision envelope until the commitment linearization point;
6. resource budget permits the required checks/action.

For an uncontrolled finite revision relation `T` and property set `P`, persistent validity is the parent safety kernel

`K(T,P)=S \ Pre_T^*(S\P)`.

For controlled epistemic actions, the natural extension is the viability kernel: the largest state set from which at least one admissible epistemic action can keep the state inside the registered viable set against the specified environment/revision model. Parent viability/control theory gets first right of refusal; no ORION novelty is claimed by naming the safe set epistemically.

Let finite `U(s)` contain permitted actions, and let nonempty `Post(s,u)` be the
complete set of environment successors **after** the controller chooses `u`.
Starting with `W_0=P`, compute
`W_(k+1)={s∈W_k: ∃u∈U(s), Post(s,u)⊆W_k}`.
Each strict step removes a state, so stabilization takes at most `|S|` strict
steps. The stable set admits a memoryless safe policy by selecting one witness
action per state. Conversely, each removed layer has no action avoiding an
earlier losing layer; induction excludes any universally safe strategy. Thus
this is the greatest controlled invariant subset. Empty action sets are losing;
waiting requires an explicit self-loop. Empty successor sets or missing upper
closure return `CANNOT_CHECK`, not vacuous safety. Different move order, partial
observation, fairness or probability semantics require another parent model.

This greatest fixed point concerns indefinite safety. A commitment with a
finite deadline instead needs the corresponding finite-horizon backward
recursion or a registered absorbing successful-commit state. Indefinite
viability is sufficient but can be unnecessarily strong for finite-horizon
commitment; this checker does not silently equate the two contracts.

## 8. FD-07 — information/interface conservation

**Status: `OPEN_RESEARCH`; several finite/class-specific fragments are already parent-owned/proved.**

Conjectured field principle: a warranted reduction in registered uncertainty cannot exceed the discriminating information supplied by the allowed observations, certificates, queries, interventions and prior model restrictions once their information/resource content is charged.

For finite version spaces one coordinate is `log2|V_before|-log2|V_after|`; it telescopes along nested updates. It is **not** a universal entropy or a law for arbitrary continuous/neural state. Query information, closure/exclusion certificates and causal interventions affect different epistemic coordinates and cannot be collapsed to one scalar without assumptions.

A valid general theorem needs an explicit access model and a strongest communication/decision-tree/information-theory parent. This package deliberately does not promote it.

**Finite parent reconstruction.** For a nonempty finite hypothesis set V with
uniform prior and a complete deterministic response function `f:V→Y`, observing
`y` leaves exactly `V_y=f⁻¹(y)`. Eliminating any other compatible hypothesis is
unsupported without additional registered evidence. Expected reduction is
`Σ_y (|V_y|/|V|) log₂(|V|/|V_y|)=H(Y)≤log₂ m`, where m is the number of nonempty
fibres. This is the finite entropy bound from
[Shannon (1948)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf),
with its hypotheses retained. The checker verifies the equivalent integer
inequality `N^N≤m^N ∏_y n_y^n_y` on 1,092 finite response maps.

There is **no per-observation log₂ m bound**: a binary test on eight hypotheses
whose rare fibre is a singleton gives realised reduction `log₂8=3`, exceeding
one bit. The expectation still satisfies the bound. Nor does one correct guess
prove side-channel information. Nested positive version-space sizes telescope
through multiplication of the exact ratios `|V_before|/|V_after|`; revocation
can expand V and is not an information-gain-only transition. Outside-model
observations reopen the model and return `CANNOT_CHECK` in this checker.

## 9. FD-08 — commuting abstraction and structural change

**Status: `PARENT_SUFFICIENT` for finite quotient dynamics plus Machine-Epistemics measurability gates; conservative-extension part `PROVED_SCOPE_LIMITED`.**

For a finite quotient map `q`, fast dynamics commute with projection when the registered transition kernel is strongly lumpable/intertwined on each required revocation state. Epistemic reuse additionally requires warrant and answer measurability on the quotient.

For a conservative extension `ι:Ξ→Ξ'`, every predecessor registered query/liveness result must embed unchanged on the image. If inference/revision/abstraction do not commute, the correct result is `REFINE_REQUIRED` or reopen—not silent reuse of the old certificate.

Specifically, with indicator projection Q (one 1 per fine-state row), strong
lumpability is `PQ=Q Pbar`. A warrant/answer vector must be constant on each
fibre. A deterministic revision must separately satisfy
`q(R(s))=Rbar(q(s))` for **every** registered state and revision. Substitution
proves the commuting diagram. Each condition is needed: an identity kernel is
lumpable for blocks `{0,1},{2}`, but revision `[0,2,2]` separates 0 and 1 and
cannot descend to that quotient. Current liveness measurability does not prove
future-revocation measurability. Invalid/overlapping/incomplete partitions are
`CANNOT_CHECK`. No quotient optimization is authorized by a single passing
snapshot. See [strong lumpability criterion](https://arxiv.org/html/0710.1986v2)
and [refinement mappings](https://lamport.azurewebsites.net/pubs/abadi-existence.pdf).

## 10. FD-09 — multi-agent non-laundering

**Status: `PROVED_SCOPE_LIMITED` for authority/dependence preservation; quantitative fusion remains conditional/open.**

A testimony/communication transition preserves source identity, shared dependencies, scope and authority. Repetition does not raise `world_truth`; a chorus that shares one assumption is still dependent on that assumption.

Numerical fusion of multiple fallible witnesses/verifiers requires an explicit dependence/coupling model. Distinct process, prompt, seed, model or machine identity is not by itself an independence certificate.

Proof scope: composition unions evidence identities idempotently and applies
FD-01's authority bound. Induction over a finite message DAG preserves shared
roots and cannot raise authority. This proves conservation under the declared
algebra, not accuracy of testimony. Scalar multiplication of support scores is
not a homomorphism of idempotent shared-source composition unless its scalar
algebra also preserves that identity; exchangeability does not supply
independence. Quantitative dependent-witness fusion remains parent-scoped/open.

## 11. FD-10 — self-model separation

**Status: `DERIVED_FROM_EXISTING_FOUNDATION` (batch 5).**

The self-model fibre `K_self` contains observations, diagnostics, predictions, proposals and assurance receipts about the machine. It has no automatic object-world or external-commit authority. Shadow evaluation is non-interfering with object state; self-change proposals require pre-outcome predictions, held-out evaluation and an external adoption source. Rollback follows stamped lineage.

The finite noninterference contract permits writes only to self records, shadow
trace and meter. Equality of every other before/after coordinate proves one-step
noninterference; induction proves it for a finite sequence. The checker rejects
world, commit or undeclared-key changes. This is a contract/model theorem, not
proof that an OCM process implements memory or concurrent capability isolation.

## 12. FD-11 — resource monotonicity / no-free-representation

**Status: `PROVED_SCOPE_LIMITED` for cumulative accounting; parent lower-bound/frontier work remains `OPEN_RESEARCH`.**

Every epistemic transition has a resource delta over the registered vector: immutable description, mutable memory, sequential time, total work, I/O/bandwidth, verifier cost, preprocessing/index/parser cost, training/acquisition cost and any other explicitly relevant resource.

Changing representation may reduce one coordinate and increase another; it cannot erase a real resource by moving it outside the accounting boundary. Claims of superiority are Pareto/resource-scoped, not parameter-count-only.

Cumulative expenditure satisfies `c'=c+d`, `d≥0`, on the **same named axes and
units**; induction gives `c_t=c_0+Σd_i`. Instantaneous memory can decrease after
freeing objects, and a remaining budget decreases after spending. These are
separate stocks, not negative refunds to historical cost. `resource_add` checks
equal dimensions, exact values and nonnegative deltas; omitted coordinates and
units remain a caller's registration obligation. This accounting identity is
`PROVED_SCOPE_LIMITED`; a universal representation lower bound is
`OPEN_RESEARCH`, not a claimed theorem.

## 13. FD-12 — typed terminal completeness

**Status: `PROVED_SCOPE_LIMITED` for finite acyclic pipelines or grammars with a decreasing natural-valued fuel/rank checked on every step.**

A finite registered pipeline/control grammar with that progress condition terminates in an explicit result rather than an untyped stuck state. Finiteness of the state alphabet alone is insufficient: the one-state self-loop is a counterexample. The vocabulary may include `PASS`, `FAIL`, `LIVE`, `UNKNOWN`, `DEAD`, `CONTRADICTED`, `GAP`, `OBSTRUCTION`, `REFINE_REQUIRED`, `REOPEN_REQUIRED`, proposal/adoption results, resource exhaustion and `CANNOT_CHECK`.

`CANNOT_CHECK` is absorbing for any downstream assertion that requires the unavailable premise/check; it is never converted to PASS by omission.

The exact checker enumerates a finite six-stage status grammar and a planted
“ignore CANNOT_CHECK” mutant. A successful step consumes one unit of finite
budget and advances the stage; an earlier non-success is absorbing. The rank
`min(remaining stages, remaining fuel)` proves termination. Malformed vector
length, unregistered status or non-materialized input returns `CANNOT_CHECK`;
insufficient fuel returns `RESOURCE_EXHAUSTED`. Stages include a **hypothetical
COMMIT result**, not an external commit action. All assertions disabled by
optimized Python cause CLI `CANNOT_CHECK`, never an unverified PASS.

## 14. Dynamical regimes

These are state-machine regimes, **not physical phases**:

- `STABLE_INFERENCE` — F dynamics under a fixed valid state;
- `REVISION` — E transition followed by local reopening;
- `DRIFT` — T invalidates a scope/model/certificate coordinate;
- `CONTRADICTION` — N eliminates a joint support;
- `SATURATION` — registered lower-level search is complete for the declared family;
- `OBSTRUCTION` — a checked lower-level ceiling blocks the goal;
- `JUMP_PROPOSED` — R proposal exists but has no adoption authority;
- `ADOPTED` — external G transition stamps a representation/organisation change;
- `DISTRIBUTED_UNCERTAINTY` — communication/coupling assumptions are insufficient;
- `CANNOT_CHECK` — a required premise, checker, closure or resource is unavailable.

The frontier is to understand transitions between these regimes under incomplete, nonstationary and multi-agent environments without assuming the answer into the model.
