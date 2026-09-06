# FIELD_INTEGRATION_GAP_AUDIT_V0

Status: **source audit / implementation-gap record** for #93.  
Subject: current `main` at the #94 base lineage.  
Purpose: distinguish semantic compatibility from actual shared persistent-field implementation before research steering.

## 1. Finding

Current OCM is **semantically closer to one field than its physical implementation is**.

### KSO

`src/ocm/kso/space.py` defines the canonical `KnowledgeSpace` with typed atoms/hyperedges carrying warrant, authority, scope, epoch and metadata.

### Language meanings

`src/ocm/language/meaning.py` explicitly says:

> A meaning is a *fragment* of the knowledge space.

It uses the KSO `TypeRegistry`, extends it through `meaning_registry`, and uses KSO warrant/CANNOT_CHECK machinery.

However, `MeaningGraph` is physically its own immutable representation:

```text
MeaningGraph(
    nodes: tuple[MNode,...],
    edges: tuple[MEdge,...],
    root
)
```

It is not itself a `KnowledgeSpace` instance.

### Language session

`src/ocm/language/session.py` records successful statements as runtime evidence whose payload contains the `MeaningGraph.as_dict()` and a canonical digest. `SaidEntry` also retains the `MeaningGraph` Python object in session state.

The runtime evidence registry is shared, but the meaning object is not automatically materialized as long-term KSO atoms/relations.

### Dialogue workspace

`src/ocm/dialogue/workspace.py` persists conversation state separately at:

```text
<runtime.root>/dialogue/<conversation>.json
```

It correctly binds speaker commitments to runtime evidence IDs and refuses to load if referenced evidence is missing. `Entity` has an optional `kso_atom` pointer, but this is not a proof that all dialogue entities/commitments share canonical KSO identity.

Therefore the current strongest accurate status is:

```text
SHARED_EPISTEMIC_CONTRACT = YES
SHARED_EVIDENCE/REVOCATION_BACKBONE = PARTIAL/YES
SHARED_TYPE_REGISTRY = YES/PARTIAL
ONE_PHYSICAL_PERSISTENT_FIELD = NOT_ESTABLISHED
```

## 2. Do not overcorrect by flattening everything

A naive response would convert every transient parse node, phrase, discourse mention and chart item into permanent KSO atoms.

That would likely violate the minimal-vessel thesis:

```text
billions of language events
-> billions of explicit objects
-> state-size / maintenance domination
```

The strong General Epistemic Field claim does **not** require every temporary representation to be physically persistent.

Required distinction:

```text
persistent epistemic field
!=
all transient computation/representation state
```

A parse forest, candidate `MeaningGraph`, chart, attention/routing state or temporary dialogue salience may remain transient/materialized state so long as authoritative/persistent consequences bind to the field and remain replayable/revisable.

## 3. Candidate integration levels

Treat these as competing designs, not a predetermined migration ladder.

### L0 — semantic compatibility only (current lower bound)

Separate language/dialogue structures use KSO-compatible concepts and shared evidence IDs.

Pros:
- simple;
- preserves existing language implementation;
- avoids field bloat.

Cons:
- duplicated identities/state may accumulate;
- cross-domain navigation may require adapter scans;
- local revision of cached/materialized language views may be incomplete;
- does not establish the strong one-persistent-field claim.

### L1 — representation object + explicit bindings (**preferred first experiment**)

Keep `MeaningGraph` as a representation payload, but persist a compact field object such as:

```text
RepresentationAtom(
    canonical_digest,
    content_ref,
    scope,
    warrant,
    authority,
)
```

plus explicit bindings/correspondences from selected meaning nodes/roles to canonical field atoms when grounded.

Existing `seed_from_meaning(g, bind)` is conceptually close: it combines a canonical meaning digest with bindings from canonical meaning nodes to knowledge-space atom references.

Required improvement: make the binding/correspondence identity explicit, warranted, scope-bound and locally invalidatable rather than merely a seed dictionary.

Pros:
- one persistent authority-bearing field;
- language-specific internal graph can stay compact/replaceable;
- avoids flattening every surface/detail node;
- multiple paraphrases can point to one underlying field object while retaining distinct utterance/speaker evidence.

Cons:
- correspondence maintenance becomes a first-class cost;
- partial/ambiguous bindings need explicit semantics;
- representation payload remains a second physical structure, albeit as a field-owned representation rather than a second truth store.

### L2 — materialized KSO subspace

Project selected `MeaningGraph` structures into KSO atoms/hyperedges using language registry types.

Use only for structures that need KSO-native navigation/revision/querying.

Required:
- deterministic namespace/ID scheme;
- exact round-trip or declared information-loss contract;
- warrant/authority assignment that does not turn parse structure into world truth;
- no edge-order/duplicate loss;
- local invalidation;
- byte/resource comparison against L1.

### L3 — fully canonical unified graph

Make all long-lived language meanings/dialogue state native KSO structures and eliminate separate persistent stores.

This is **not** the default target. Adopt only if L2 demonstrates significant lifecycle/query value over L1 and packed physical storage makes the state economical.

## 4. Strong recommendation

Test **L1 vs L2**, not `L0 -> L3` by ideology.

The architecture should optimize:

```text
shared authority/revision/identity
+ cross-domain reuse/navigation
- persistent bytes
- maintenance work
- conversion/materialization work
```

If L1 supplies all epistemic benefits at lower cost, a physically separate `MeaningGraph` payload is acceptable and does not falsify the General Epistemic Field.

The correct invariant is:

> There is one authoritative persistent epistemic state graph/lifecycle; representations may be externalized/materialized behind explicit content-bound correspondence objects.

## 5. Dialogue workspace interpretation

Treat `DialogueWorkspace` initially as a **materialized transient/session view**, analogous to a database materialized view or working memory.

It may remain separately serialized if:

1. every authority-bearing commitment is bound to field/runtime evidence;
2. persistent entities that claim cross-session/world identity bind to canonical field IDs or explicit unresolved correspondences;
3. the workspace cannot mint authority;
4. field revocation/version changes invalidate affected workspace entries/caches;
5. the workspace can be reconstructed or checked against field/evidence identities;
6. its bytes/update cost are counted.

Current code already satisfies part of this: commitment evidence IDs are checked on load and missing evidence yields `CANNOT_CHECK`. The remaining gap is stronger canonical identity/cross-view invalidation.

## 6. Required bridge experiments

### GEF-B1 — MeaningGraph representation ownership

Compare L0/L1/L2 on the same frozen language meanings.

Measure:

```text
persistent bytes
conversion/materialization cost
canonical digest preservation
exact relation/feature preservation
shared-entity reuse
revocation behavior
navigation/query work
```

### GEF-B2 — paraphrase shared-object test

Two distinct utterances map to isomorphic/compatible meanings that refer to the same field entity/proposition.

Require:

- distinct utterance/speaker evidence retained;
- underlying field identity reused where warranted;
- no duplicated world-truth object solely due to paraphrase;
- revoking one speaker record does not revoke independently supported field truth.

### GEF-B3 — ambiguous-binding test

One meaning node has two possible field referents.

Require explicit candidate correspondence set / `NEEDS_CONTEXT`; never choose by similarity alone.

### GEF-B4 — cross-view source retraction

A source/evidence object supports a field claim used in a language answer and a scientific/procedural conclusion.

Revoke it and require local reopening of all true dependents, including materialized dialogue/output caches, while unrelated language competence remains intact.

### GEF-B5 — workspace materialization test

Compare separate dialogue JSON versus KSO-native materialization versus reconstructable view.

Measure bytes, per-turn update cost, restart cost, invalidation cost and semantic equivalence.

No design wins merely because it is “more unified.”

## 7. Adoption terminals

```text
L0_SEMANTIC_COMPATIBILITY_ONLY
L1_REPRESENTATION_BINDING_SUFFICIENT
L2_KSO_SUBSPACE_VALUE_SUPPORTED
L3_FULL_PHYSICAL_UNIFICATION_JUSTIFIED
PHYSICAL_UNIFICATION_NO_VALUE
PHYSICAL_UNIFICATION_STATE_COST_DOMINATES
CORRESPONDENCE_MAINTENANCE_DOMINATES
CROSS_VIEW_IDENTITY_NOT_ESTABLISHED
WORKSPACE_VIEW_CONTRACT_SUPPORTED
CANNOT_CHECK_<reason>
```

## 8. Steering consequence

Do not tell a research-director AI that OCM **already has** one physically unified General Epistemic Field.

Tell it instead:

```text
Treat one authoritative General Epistemic Field as the canonical hypothesis.
Current KSO/language/dialogue are semantically aligned but physical unification is an open L1-vs-L2 design question.
Do not flatten transient representations into persistent atoms unless measured value justifies it.
```
