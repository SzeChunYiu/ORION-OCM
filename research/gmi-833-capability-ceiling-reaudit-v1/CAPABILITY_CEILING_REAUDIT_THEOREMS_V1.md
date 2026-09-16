# Capability-definition audit and eleven ceiling reproofs v1

**Issue:** #918  
**Parent:** #833 Section K  
**Claim ceiling:** `GMI_833_CAPABILITY_DEFINITIONS_AND_ELEVEN_CEILINGS_REAUDITED_AT_REGISTERED_SCOPE`

## 1. Scope and source ownership

The pinned A4 source has exactly 27 distinct capability IDs and eleven required fields per row: identifier, name, five operational fields, negative twin, strongest parent, atlas reduction, and falsifier. The pinned F2 registry has exactly eleven distinct ceiling IDs. Their source blob identities, rather than copied prose, establish byte custody.

This tranche does not claim that every possible verbal definition is architecture-independent. It audits the pinned structured artifact. Nor does it infer an unrestricted theorem from a finite census: the general statements below have direct analytic proofs; executable enumeration checks bounded corollaries and hostile controls only.

AX-1 supplies an external behavioral specification, AX-2 makes all registered channels and state explicit, AX-3 meters resources, and AX-5 supplies external capability contracts. Where a theorem needs a probability law, linear map, tree, query family, or decoder, that object is an additional external contract—not a hidden architectural premise.

## 2. Architecture-independence criterion and 27-row result

For a row, define its operational tuple

`A=(inputs, allowed_info, required_behaviour, success_metric, resource_metric)`.

The row is architecture-independent at registered scope when:

1. all eleven schema fields are present, no extra field is smuggled in, and the registered text contracts are well formed;
2. `A` states externally testable inputs, information access, behavior, success, and resources;
3. no operational field requires a named implementation family; and
4. adjoining an audit-only implementation label and applying any bijective remint to that label leaves `A` unchanged.

The executor checks those predicates for all 27 rows, records each canonical row digest, and pins the whole original JSON blob. All 27 pass. The phrase “architecture edit” in `cap-self-improvement` denotes an externally permitted intervention alongside self-rewrite and hyperparameter update; it does not require an architecture family. Functional terms such as policy, causal identification, message protocol, store, and query describe contract roles, not privileged implementations.

The result is intentionally bounded: absence of a fixed token list is not a semantic proof about arbitrary future prose. Source drift, a missing/malformed/extra field, a named implementation family in an operational field, or changed external semantics under remint falsifies the registered audit.

## 3. Reproof inventory

### C1 — `F2_STATE_CAPACITY_MEMORY`

**Domain and assumptions.** Let `H/~` be any set of history classes that some common continuation must distinguish, and let `Q` be the complete registered persistent response-state carrier after those histories. No external memory or later channel re-separates merged histories; success is zero-error. Dependencies: AX-1, AX-2, AX-5.

**Theorem.** Any successful realization induces an injection `H/~ -> Q`; therefore `|H/~| <= |Q|`.

**Proof.** If two obligation-distinct classes reach the same complete registered persistent state, target-independent continuation from that state produces the same protected response, so one obligation fails. Thus their states differ. QED.

**Tightness boundary.** A realization with one code state per class is sufficient only when representatives/codes can be chosen and the registered response map realizes them. The historical finite delayed-label equality is a corollary.

**Parent / hostile / falsifier / status.** Parent: Myhill–Nerode and distinguishing-state bounds. Hostile: three pairwise-separated classes, two states. Falsifier: an exact in-scope realization with fewer states. Status: valid after upgraded reproof.

### C2 — `F2_OBSERVATION_QUOTIENT`

**Domain and assumptions.** Arbitrary sets `X,Z,A`, observation `O:X->Z`, required response `g:X->A`, and no later informative channel. Dependencies: AX-1, AX-2, AX-5.

**Theorem.** A zero-error decoder on observed values exists iff `g` is constant on every fiber of `O`, equivalently iff `g` factors through `O` on `im(O)`.

**Proof.** If `g=pi o O`, equal observations have equal responses. Conversely fiber constancy makes `pi(O(x))=g(x)` well defined on `im(O)`. Values outside the image are irrelevant; extending to all `Z` requires a default when `A` is nonempty. QED.

**Parent / hostile / falsifier / status.** Parent: deterministic sufficiency/garbling and quotient factorization. Hostile: two latent points with one observation and different required actions. Falsifier: a transcript-only exact decoder that separates one fiber. Status: valid, generalized from finite sets.

### C3 — `F2_COMMUNICATION_BANDWIDTH`

**Domain and assumptions.** Sender classes `K`, message carrier `M`, distinct required receiver actions, deterministic decoding, and no correlated receiver side information. Dependencies: AX-1, AX-2, AX-3, AX-5.

**Theorem.** Zero-error coordination requires an injection `K->M`, hence `|K|<=|M|`. For a fixed `B`-bit carrier this yields `|K|<=2^B`.

**Proof.** Two classes with the same receiver-visible message receive the same action, contradicting their distinct obligations. QED.

**Tightness boundary.** An injective code is sufficient when the registered encoder/decoder family realizes it; cardinal inequality alone does not silently supply a computable code.

**Parent / hostile / falsifier / status.** Parent: deterministic communication complexity and transcript counting. Hostile: five classes, four messages. Falsifier: an in-scope exact protocol exceeding the carrier. Status: valid after upgraded reproof.

### C4 — `F2_PRECISION_BOUNDARY`

**Domain and assumptions.** Any code carrier `C`, response-profile set `Y`, frozen decoder `d:C->Y`, and target family `T subseteq Y`. All precision-bearing selection channels are included in `C`. Dependencies: AX-1, AX-2, AX-3, AX-5.

**Theorem.** The representable profiles are exactly `im(d)`. Covering `T` requires `T subseteq im(d)`; for finite carriers, or under ordinary choice-based cardinal comparison, this implies `|T|<=|C|`.

**Proof.** Restricting `d` to codomain `im(d)` is a surjection from `C`. A finite target, or the stated choice principle, selects one preimage code for every covered profile and thereby injects the target into `C`. QED.

**Correction.** The old one-dimensional threshold / `N+1` placement / `B`-bit theorem remains a valid finite corollary for its frozen decoder. It is not promoted to a universal precision law, and “threshold architecture” is removed from the general theorem.

**Parent / hostile / falsifier / status.** Parent: hypothesis-class cardinality under quantized code carriers. Hostile: five required profiles, four codes. Falsifier: a fixed decoder whose image exceeds its code domain. Status: narrowed and re-proved as an architecture-neutral code-carrier bound.

### C5 — `F2_UPDATE_CHANNEL_PLASTICITY`

**Domain and assumptions.** From one initial state, target-dependent persistent information enters only through a finite event sequence with arbitrary registered alphabets `U_1,...,U_T`; all other dynamics are target-independent. Dependencies: AX-2, AX-3, AX-5.

**Theorem.** The selected successor set is the image of a map from `U_1 x ... x U_T`; for finite alphabets, or under ordinary choice-based cardinal comparison, its cardinality is at most the product cardinality. A constant finite alphabet of size `A` yields `A^T`.

**Proof.** Once the transcript is fixed, target-independent dynamics select at most one successor. Thus target selection factors through the transcript product. QED.

**Tightness boundary.** Equality requires an injective transcript-to-successor realization, not merely a large alphabet.

**Parent / hostile / falsifier / status.** Parent: finite-rate control/reachability counting. Hostile: five target-distinct successors through two binary updates. Falsifier: more successors than registered transcripts. Status: valid after upgraded reproof.

### C6 — `F2_PROTECTED_RANK_FRONTIER`

**Domain and assumptions.** A finite-dimensional vector space `V` over any field and an exact linear protected-response map `L:V->W`. An admissible update `delta` must satisfy `L(delta)=0`. Dependencies: AX-2, AX-3, AX-5.

**Theorem.** Admissible updates are exactly `ker(L)`, and `dim ker(L)=dim(V)-rank(L)`. Thus `s` independent exact protected directions require `rank(L)+s<=dim(V)`.

**Proof.** The retention equation defines the kernel; rank-nullity gives its dimension, and a kernel basis attains it. QED.

**Correction.** For a nonlinear response `f`, replacing `L` by an explicitly registered derivative `Df_x` proves only a local first-order statement. It does not prove global exact nonlinear retention. Without a derivative contract, the rank claim is inapplicable.

**Parent / hostile / falsifier / status.** Parent: rank-nullity and null-space projection. Hostile: rank two on dimension three with a demand for two independent protected directions. Falsifier: an exact linear counterexample. Status: narrowed to exact-linear or explicit first-order scope.

### C7 — `F2_PLANNING_RESOURCE_HORIZON`

**Domain and assumptions.** Any registered rooted tree, finite depth `h`, and through-depth node set `V_<=h`. Every node may independently contain the sole decisive event; no oracle, pruning certificate, dominance rule, or state merging applies. Dependencies: AX-1, AX-2, AX-3, AX-5.

**Theorem.** Guaranteed complete coverage requires the inspected set to contain all of `V_<=h`; its inspection-cardinality lower bound is therefore `|V_<=h|`, including nonuniform or infinite levels.

**Proof.** If `u` is uninspected, the no-event world and the world with the sole event at `u` have identical inspected data, so the procedure cannot be correct on both. QED.

**Tightness boundary.** Set-theoretically inspecting the whole set is sufficient. An operational exhaustive algorithm additionally needs enumeration/well-order and completion semantics. For a finite full `b`-ary tree, breadth-first inspection attains the geometric sum.

**Parent / hostile / falsifier / status.** Parent: adversarial exhaustive tree search. Hostile: six inspections for seven nodes through binary depth two. Falsifier: guaranteed coverage omitting a possible decisive node. Status: valid after upgraded reproof.

### C8 — `F2_SEARCH_BUDGET_VERIFIED_CLASS`

**Domain and assumptions.** Candidate set `C`, membership oracle, exactly one valid candidate, and success defined as querying that candidate and receiving its positive certificate. For a run whose queried subset is `Q`, no side channel links unqueried candidates. Dependencies: AX-1, AX-2, AX-3, AX-5.

**Theorem.** If `|Q|<|C|`, direct positive verification is not guaranteed.

**Proof.** Cardinal inequality implies some `c in C\Q`. Place the unique valid candidate at `c`; every issued query is negative and no positive certificate is observed. QED.

**Correction.** In a finite `N`-candidate problem, if success means mere identification under an exactly-one promise, `N-1` negative answers identify the last unqueried candidate. Thus the historical `N` lower bound is retained only for direct positive verification; the identification reading is retracted. Querying all of an arbitrary `C` additionally requires a traversal/enumeration and completion semantics.

**Parent / hostile / falsifier / status.** Parent: unstructured membership-query complexity. Hostile: five candidates and four negative queries—the fifth is identified but not positively verified. Falsifier: guaranteed positive verification without querying the valid point. Status: narrowed to direct positive verification.

### C9 — `F2_VERIFICATION_BUDGET_FALSE_ADOPTION`

**Domain and assumptions.** Arbitrary coordinate set `I`, inspected set `S`, measurable defect-set space, and probability law `mu` for which `{D:D intersect S=empty}` is measurable. Perfect checking adopts iff no inspected defect is found. Dependencies: AX-1, AX-2, AX-3, AX-5 plus the stated probability contract.

**Theorem.** False-adoption probability is exactly

`mu({D : D intersect S = empty})`.

Against distribution-free nonempty singleton defects, zero false adoption requires `S=I`.

**Proof.** Under perfect checks, adoption of a defective candidate occurs exactly on the displayed miss event. If `i` is unchecked, defect set `{i}` is missed; full coverage intersects every nonempty defect set. QED.

**Finite corollary.** Uniform `r`-subsets of an `M`-set and `q` inspected coordinates give `choose(M-q,r)/choose(M,r)`, with numerator zero when `M-q<r`.

**Parent / hostile / falsifier / status.** Parent: acceptance sampling/hypergeometric coverage. Hostile: the sole defect occupies an unchecked coordinate. Falsifier: disagreement with the event measure or adversarial zero-FA under incomplete coverage. Status: valid with distributional and adversarial branches separated.

### C10 — `F2_INFORMATION_ACQUISITION_BUDGET`

**Domain and assumptions.** A deterministic finite-depth adaptive decision tree; node `v` has registered outcome carrier `A_v`; exact hypothesis labels must differ. No unregistered information channel exists. Dependencies: AX-1, AX-2, AX-3, AX-5.

**Theorem.** Exact hypotheses inject into complete transcript leaves, so their cardinality is at most the leaf-set cardinality. A uniform `A`-ary depth-`q` tree gives `|H|<=|A|^q`, for finite or infinite `A`.

**Proof.** Two hypotheses at one leaf produced the same full registered transcript and cannot be assigned distinct exact labels by a transcript-only decoder. QED.

**Tightness boundary.** Equality requires a registered query family that realizes a separating leaf code. Leaf cardinality alone does not provide such queries.

**Parent / hostile / falsifier / status.** Parent: decision-tree leaf counting/source coding. Hostile: five hypotheses, four leaves. Falsifier: exact identification beyond the leaf carrier with no other channel. Status: valid after upgraded reproof.

### C11 — `F2_SOCIAL_OBSERVATION_IDENTIFIABILITY`

**Domain and assumptions.** Arbitrary hidden-model set `Theta`, complete registered transcript map `tau:Theta->T`, required response `g:Theta->A`, and no private-state label or unregistered diagnostic channel. Dependencies: AX-1, AX-2, AX-5.

**Theorem.** Exact task response exists iff `g` factors through `tau`; full hidden-model identification exists iff `tau` is injective.

**Proof.** Apply C2 to social transcripts. For full identification take `g` to be the identity on `Theta`. QED.

**Parent / hostile / falsifier / status.** Parent: deterministic observation quotient and statistical identifiability. Hostile: two models share the complete transcript but require different held-out responses. Falsifier: a transcript-only decoder separates them. Status: valid, generalized from finite hidden-model sets.

## 4. Executable witness boundary

The deterministic executor checks 332 bounded cases:

- 64 observation-factorization pairs;
- 25 finite injection cardinalities;
- 40 finite product-channel bounds;
- 168 hypergeometric verification cases;
- 35 direct-verification versus mere-identification boundary cases.

It also rejects one explicit hostile per ceiling. These checks can falsify the implementation or a finite corollary. They do not prove the arbitrary-set statements; Sections C1–C11 do that analytically.

## 5. Strongest result and exclusions

If pins, ledger, tests, normal/optimized replay, and exact three-row reconciliation are green, the earned terminal is:

`GMI_833_CAPABILITY_DEFINITIONS_AND_ELEVEN_CEILINGS_REAUDITED_AT_REGISTERED_SCOPE`.

This does not establish a morphology-to-capability predictor, empirical transfer, real-system validation, stochastic approximate-identification rates, continuous optimization rates, global nonlinear retention, architecture ranking, or a universal best architecture.
