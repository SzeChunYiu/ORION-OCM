# Capability predictor V1 — morphology descriptor (F4 box 1)

**Issue:** #602 F4. **Status:** SPECIFICATION ONLY, claim ceiling G1 (no empirical G6 claim). **This file specifies the 8-field architecture-name-free descriptor `D(M)` whose enumerability the validator checks; the contract remains `CONTRACT_V1.json`.**

Lane B, worktree `issue-592-ggu`. Lane A owns registry this turn — no registry row or capsule digest is added here.

## 1. What `D(M)` is and is not

`D(M)` is a functional capability descriptor, not a model class label. Every value is an enumerable declared computational role with a charged cost. Knowing `D(M)` suffices to apply the F2/G2 ceilings (state, cut, planning, verification, acquisition) and the Phenomenology Atlas reductions (GG54–GG59); knowing only a brand name does not.

**Brand-label rule (enforced by `SCHEMA_V1.json` and `capability_predictor_v1.py`).** No field admits a free-text brand string such as `Transformer`, `RNN`, `CNN`, `GNN`, `Diffusion`, `Mamba`, `MoE` as a value. Known families are encoded as composites: e.g. a Transformer-like regime is approximated by `state_carrier=PRODUCT_VECTOR(d=512) + native_operators={CONTENT_ROUTED_COMBINATION, AFFINE_THRESHOLD} + communication=POINT_TO_POINT_ROUTED + memory_organization=UNIFIED_FLAT`, not by the word `Transformer`. The validator rejects any descriptor whose field value is not in the frozen allowlist.

`F1 is G1, do not raise it:` this descriptor inherits the F1 G1 registration ceiling. It does not claim that descriptor distance correlates with empirical capability.

## 2. The eight fields

Each field carries `definition / values / why needed / strongest parent (first refusal) / falsifier`. Parents receive first refusal: a predictor earns credit for a field only when varying that field alone moves predicted capability past the parent-priced baseline at matched other fields.

### 2.1 `state_carrier` — distinguished persistent state

**Values (enumerable):** `FINITE_ALPHABET(n)` | `PRODUCT_VECTOR(d, field∈{F2,FP16,FP32}, precision)` | `GRAPH_INDEXED(nodes, edge_locality∈{local, fully_connected})` | `EXTERNAL_ADDRESSABLE(store_bits, latency, bandwidth)` | `HYBRID_COMPOSITE(product of above)`. Parameter `n,d,nodes,store_bits` are bounded non-negative integers frozen in `SCHEMA_V1.json` ranges.

**Why needed:** Without a declared carrier, temporal semantic-cut bounds (GG54, GG57) are vacuous. Exact delayed reproduction of `m` obligation-distinct histories requires `|S| ≥ m`; continual retention of two independent facts requires `|S| ≥ 4`. Different carrier kinds make different `|S|`↔`τ` tradeoffs physically reachable (e.g., external addressable buys `|S|` at latency/rho cost).

**Strongest parent:** Shannon channel capacity / finite-automaton state complexity; GG54 Temporal Memory Cut; GG57 Retention Capacity; physical resource bridge (Landauer/Bremermann, `rho`).

**Falsifier:** A predictor that assigns identical capability to `FINITE_ALPHABET(2)` vs `FINITE_ALPHABET(8)` on the `m=6` delayed-reproduction microscope where exhaustive encoding census proves `|S|<m` cannot be exact, or a claimed exact success with `|S|<m`.

### 2.2 `native_operators` — atomic transformations

**Values:** Ordered multiset drawn from allowlist `{FINITE_TABLE_LOOKUP, AFFINE_THRESHOLD, LOCAL_EQUIVARIANT_MAP, CONTENT_ROUTED_COMBINATION, GRAPH_LOCAL_MESSAGE, STACK_OR_COUNTER, VERIFIER_QUERY, TOOL_ORACLE_INVOKE}` each with a scalar `tau` price. `HYBRID_SET` is the explicit union; free-text entries are invalid.

**Why needed:** `tau` separates which obligations factor through cheap local transforms versus require routing/search. Atlas rows for convolution/weight sharing, GNN message passing, and transformers reduce to which native ops are cheap; the predictor must price them, not name them.

**Strongest parent:** Circuit complexity; equivariant learning theory (Cohen–Welling); `tau` complexity spectrum; GG55 Conditional Routing Advantage (strict `3/4` vs `1` separation).

**Falsifier:** Two descriptors identical except `native_operators` adds `CONTENT_ROUTED_COMBINATION` that receive identical predicted accuracy on the uniform `(x0,x1,q)→x_q` world where fixed routing is provably `6/8` and routed `8/8`.

### 2.3 `control_update_law` — decision and developmental dynamics

**Values:** Pair `(control, update)` where `control ∈ {FIXED_POLICY, STATE_CONDITIONED, SEARCH_DERIVED, VERIFIER_GATED}` and `update ∈ {NO_UPDATE, DISCRETE_REWRITE, PARAMETRIC_STEP, MEMORY_REPLAY}` with a declared step/iteration budget.

**Why needed:** Separates deployment capability (frozen program/weights) from developmental change (learning). In-context adaptation (GG56) — capability improving at deployment with frozen long-term parameters because prompt changes the transient cut/state — and retention failure (GG57) are `update`-law phenomena. Planning-vs-habit crossover lives here.

**Strongest parent:** POMDP control/update; recursive GMI lift where learner state contains its own update rule; planning semantic resolution theorem; GG56/GG57.

**Falsifier:** Predictor scores `NO_UPDATE` equal to `MEMORY_REPLAY` on the sequential `(x,y)` retention world where every final state of size `<4` is provably inexact by exhaustive encoding.

### 2.4 `memory_organization` — how persistent storage is structured

**Values:** `UNIFIED_FLAT | PARTITIONED_SHORT_LONG | EXTERNAL_RETRIEVAL_CHANNEL | HIERARCHICAL_COMPRESSION | DUAL_WRITE_PROTECTED(rank r)` with declared capacity shares and consolidation/replay policy.

**Why needed:** Same `|S|` under different organization yields different capacity/retention frontiers and retrieval efficiency `eta_ret`. CSR-1 consolidation (`M*_t = N_t` reconstruction) and interference/stability–plasticity tradeoff are organization-level laws.

**Strongest parent:** Complementary learning systems; CSR-1 consolidation frontier; GMI interference/stability–plasticity; GG12 task-directed acquisition (residual distinction pricing).

**Falsifier:** Unified-flat predictor matches partitioned predictor on a consolidation microscope where `M*_t=N_t` reconstruction is provably required at bounded `|S|`, or identical `eta_ret` predictions where residual distinction accounting differs by organization.

### 2.5 `communication` — cut structure among subcomponents/agents

**Values:** `NONE_ISOLATED | BROADCAST_BOUNDED(width, cost) | POINT_TO_POINT_ROUTED(bandwidth, latency) | SHARED_EXTERNAL_STORE(bandwidth, noise)` plus topology when multiple carriers exist.

**Why needed:** Coordination/tool capability is cut-bounded (SC-1, GG25). Attention *is* conditional cut allocation (GG55). Without this field, multi-agent or tool gains are misattributed to internal `tau`.

**Strongest parent:** Shannon communication theory; SC-1 semantic cut theorem; GG55 conditional routing; GG58 tool boundary; GG25 team cut/cooperation.

**Falsifier:** Equal coordination predictions for `NONE_ISOLATED` vs `BROADCAST_BOUNDED(1 bit)` on a world where GG25 proves at least `log2(m)` bits are necessary to distinguish coordinated responses.

### 2.6 `verification` — verifier channel

**Values:** `NONE_PASSIVE | MEMBERSHIP_ORACLE | EQUIVALENCE_ORACLE | PROOF_CHECKER | DISTRIBUTED_CONSENSUS` with schedule `(available steps)` × `latency × per-call cost × false-adoption cost (asymmetric)`.

**Why needed:** Verifier information changes the reachable verified-solution class at fixed search `tau` (CL-6 / PVR-3) and floors false-adoption. Passive vs active learning separations are `V`-separations (Gold/Angluin).

**Strongest parent:** Angluin `L*` vs Gold passive intractability; PVR-3 certificate validity window; CL-6 verifier cut law.

**Falsifier:** Equal verified-solution reach at matched search budget for `NONE_PASSIVE` vs `EQUIVALENCE_ORACLE` on a class where parent proves passive intractability but active learning constructs the concept.

### 2.7 `development_law` — search that produces the morphology

**Values:** `ENUMERATIVE_SEARCH | VARIATION_SELECTION_POPULATION | GRADIENT_BASED_UPDATE | VERIFIER_GUIDED_SYNTHESIS | HYBRID_DEVELOPMENT(mixture weights)` with declared variation operator, selection rule, encoding and budget.

**Why needed:** Admissibility (DU-1: what *could* succeed) does not imply reachability (what `D` *will* find). The same ecology/resource optimum may be reachable under one `D` and unreachable under another. Search burden and neutral-recovery claims are `D`-properties.

**Strongest parent:** Gold/Goldman learnability; developmental reachability selection theorem; NAS/AutoML search bias theory; neutral search methodology.

**Falsifier:** Identical capability predictions for `ENUMERATIVE_SEARCH` vs `VARIATION_SELECTION_POPULATION` on a world where the optimum lies provably outside the former's bias/encoding but inside the latter's, yet measured reachability differs.

### 2.8 `resource_profile` — charged budgets and prices

**Values:** `b` = vector of hard caps `(desc, exec, upd, ver, rev, acq, store_bits, time)`; `p` = non-negative price vector per `DEFINITIONS_V2_EXACT.md` §5 (affine `p^T r`); `rho` = physical map to `(time, energy, silicon area)` per physical resource bridge. Continuous params are bounded reals.

**Why needed:** Every F2 ceiling is resource-bounded (state, planning horizon, verification, acquisition). Repricing (`p` flip) must move Pareto predictions; budgets gate feasibility. Same functional morphology at different `rho` is a different practical capability (e.g., long-context vs short-context).

**Strongest parent:** Bounded rationality (Simon); resource-rational analysis (Lieder & Griffiths 2020); Blackwell experiment comparison; Landauer/Bremermann; `DEFINITIONS_V2_EXACT.md` §5 affine framework.

**Falsifier:** Predictor's Pareto ordering does not move when `p` is flipped to penalize the previously cheaper coordinate, or a budget-violating morphology is predicted feasible without adjusting `rho`.

## 3. Enumerability and equivalence

Each field's `allowed_values` are frozen in `SCHEMA_V1.json`; the validator checks membership and bounded ranges. Two descriptors are equivalent iff their 8-field values match up to finite-alphabet isomorphism (bijection on state labels) and operator-cost reparameterization preserving the `tau` pullback. Brand renaming is not an equivalence witness. This is the anti-story guard for F4: `D(M)` cannot be chosen after outcomes.

## 4. Relation to species provisional 9-tuple

The G-provisional species tuple `(state carrier, native operators, control law, update law, memory org, comm, verification, development law, resource profile)` is the 9-tuple split of `control_update_law` plus verbiage alignment. `D(M)` is its tightened, enumerable 8-field form; the split is documented for lineage, the frozen interface is the 8-field version. Any future G-species equivalence/speciation work must refine this descriptor, not replace it with brand labels.
