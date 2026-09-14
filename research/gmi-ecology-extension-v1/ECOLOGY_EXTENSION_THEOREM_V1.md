# Ecology extension — the 16 missing coordinates (592 item 2 / 602 A2)

Status: **THEOREM + EXACT FINITE CHECKS. Admissibility claim** (DU-1: what is
forced under the declared interface, not what neutral search reaches).
Date: 2026-09-14. Scope: finite declared ecology `E = (D_tau,O,A,F,V,p,b,H,Delta)`
as in `DEFINITIONS_V2_EXACT.md` §2 and `ECOLOGY_AXES_V2.json`. Exact string/integer
checks, CPython 3.8 safe.

## Parent subtraction

This unit **extends** three parents without editing them:

- `ECOLOGY_CONTRACT_V1.json` — 10 core fields + 19 candidate coordinates + measurement rule.
- `ECOLOGY_AXES_V2.json` — 15 axes on which a parent theorem already proves a tractability flip; `other_agents` and `population_structure` added there with TOM-1/teaching parents.
- `DEFINITIONS_V2_EXACT.md` §2 — `E`, `Gamma`, `D0-D3` ladder.

The gap: item 2 audits "other agents is not an ecology coordinate — multi-agent is bolted on separately" and lists 16 unchecked A2 boxes: observation/action/feedback/verifier, drift/regime, recurrence, noise, compositionality, social topology, embodiment, resource prices/budgets, latency/cost, acquisition cost, protected splits, equivalence/remint. All were prose-only before this extension.

No new graphical-model principle is claimed beyond the parents' already-proved flips.

## A2 checklist (16 boxes)

- [x] other adaptive agents as an explicit ecology coordinate (with `NONE`..`MIXED_POPULATION` values)
- [x] observation structure
- [x] action/intervention structure
- [x] feedback and verifier structure
- [x] task distribution and horizon
- [x] drift / regime change
- [x] recurrence / reuse structure
- [x] noise and partial observability
- [x] compositionality / symmetry / relational structure
- [x] social topology where multiple agents exist
- [x] embodiment / sensor / actuator constraints
- [x] resource prices and hard budgets separately
- [x] verification latency / cost / false-adoption loss
- [x] information-acquisition cost
- [x] protected train/development/held-out splits
- [x] ecology equivalence / remint rules to prevent label leakage

Each coordinate carries `definition`, `parent` (first refusal) and `falsifier` (concrete computation that refutes the claim). The contract lives at `ECOLOGY_EXTENSION_CONTRACT_V1.json` with schema `SCHEMA_V1.json`.

## Equivalence / remint rules (the leak guard)

Two ecologies are **equivalent** only under a labelled bijection (remint)
`f` on registered world/task alphabets that preserves `(O,A,F,V,p,b,H,Delta)` up to
renaming by pullback. Concretely:

- `f` is bijective on each registered finite domain;
- for every world `w`, `obs(w)` and `obs(f(w))` are the same up to the alphabet renaming, similarly `V` and the observation/verification contracts;
- no oracle answer or held-out label is exposed through `f`.

Any non-bijective map, or any map that leaks a protected label (e.g. encoding the held-out answer in an "equivalent" task id), **is not a remint**. A claimed replication that survives only under such a map is void. This is the anti-story rule made checkable.

Machine-checked on a 3-world toy: the identity and a disjoint relabelling are accepted as remints; a collapsing map `f(0)=f(1)=0` and a leaking map that copies the answer bit into the task label are rejected.

## Observable decision criteria

A transition or replication can be classified by which ecology coordinate it varies (frozen vs varied rule from `ECOLOGY_AXES_V2.json`); the classifier is the field name itself. A held-out evaluation passes the guard iff its `protected_splits` remint is bijective and its `label_leakage_forbidden` flag is respected — both booleans are `true` in the registered contract.

## Claim ceiling

Finite declared ecologies only, admissible scope, exact string/boolean checks. No claim that any morphology dominates on these axes — that requires the phase-law programme (P1 D). Falsifier: any coordinate whose `definition`/`parent`/`falsifier` is thin (<20/10/20 chars), any `other_agents.values` not containing `NONE` and `ADAPTIVE_OPPONENTS`, any `equivalence_remint_rules` with a `false` boolean or thin falsifier, or any non-bijective "remint" accepted by the checker (re-run `test_ecology_extension_v1.py`).

Files: [contract](ECOLOGY_EXTENSION_CONTRACT_V1.json) + [schema](SCHEMA_V1.json) ->
[model](ecology_extension_v1.py) -> [controls](test_ecology_extension_v1.py) ->
[receipt](ECOLOGY_EXTENSION_RECEIPT_V1.json: on billy-old py3.14 + laptop-billy py3.8, normal + optimized).
