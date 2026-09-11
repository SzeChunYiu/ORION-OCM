# Ultimate Track-B question — current scientific status v1

Status date: 2026-09-11. This is an evidence/logic status, not a manifesto.

## Ultimate question

Can there be a general theory of machine intelligence in which a minimal cognitive substrate generates known forms such as neural, symbolic, probabilistic, programmatic and OCM-like systems; explains their developmental limits/dominance; and predicts forms not yet discovered?

## Q1 — Is there one unique minimum irreducible cognitive unit?

### Current answer

**No such unit is established, and several mature results make the strongest representation-independent version unlikely.**

Reasons:

1. finite deterministic networks of finite adaptive local units flatten exactly into finite-state transducers;
2. universal program formalisms can represent all computable morphology families, making expressivity alone vacuous;
3. universal description complexity is reference-machine/language relative up to compiler constants;
4. even simple generated function classes can have multiple distinct minimal bases;
5. no-free-lunch/speedup results attack unrestricted universal optimality.

Current terminal:

```text
NO_REPRESENTATION_INDEPENDENT_UNIQUE_COGNITIVE_ATOM_ESTABLISHED
```

The live target is instead:

```text
resource-bounded equivalence class of execution + developmental generating bases
```

with scope explicit.

This conclusion could be overturned by a much stronger lower-bound / asymmetric-compilation result under physically meaningful resource constraints, but no such result exists in the Track-B evidence yet.

---

## Q2 — What generates different forms of machine intelligence?

### Current answer

The original single `Generator theta(...)` should be decomposed into three objects:

1. **Generative closure** `M_B` — which morphologies the frozen basis/grammar can express/develop;
2. **Developmental/ecology frontier** `F_B(E)` — which morphology equivalence classes are nondominated under task, resource, verification and lifetime conditions;
3. **Search dynamics** `Gamma` — which reachable/frontier morphologies are actually discovered at finite search budget.

Within a chosen morphology, ordinary learning is a fourth object:

\[
M_{t+1}=U(M_t,e_t).
\]

Thus:

```text
basis says what can exist;
ecology/resources say what is worth existing;
search says what is found;
learning says how the found form changes with experience.
```

This is currently the strongest clean formalization of the handwritten generator idea.

### What is not answered

We do not yet have a cross-paradigm basis whose family-scale compilation/developmental costs are shown to be nontrivial and acceptable.

---

## Q3 — What limits a form of intelligence, and why does one form dominate?

### Current answer

Dominance is not one scalar property of the architecture. It is ecology/resource/development dependent.

The correct primary object is the developmental Pareto frontier over:

```text
verified capability
acquisition/search cost
inference/reasoning cost
update/learning cost
memory/storage
communication
verification
maintenance/revision
retention/plasticity
```

A morphology can be limited by:

- representation/expressivity at the registered bound;
- acquisition/search difficulty;
- weak credit assignment;
- sample/information limits;
- inference/communication cost;
- verifier cost;
- maintenance/revision cost;
- plasticity loss / catastrophic interference;
- hardware mismatch;
- short reuse horizon that cannot repay training/build cost.

### Exact calibration obtained

In a tiny exact label-memory ecology, two perfect morphology families occupy different Pareto points:

```text
local-state storage    = [3, 0.5, 0.0, 0.0, 1]
topology/edge storage  = [4, 0.0, 0.5, 0.5, 1]
```

under the registered raw coordinates.

The exact scalar boundary is:

\[
\text{topology wins iff }
 w_{state} > 2w_{desc}+w_{edge}+H w_{message}.
\]

This demonstrates the mathematical *shape* of a morphology phase law, but the generic principle is parent-owned by resource rationality/algorithm selection.

### Stronger residual

Track B needs a phase law where:

- morphology candidates are generated endogenously from a shared basis, not a human portfolio;
- development/acquisition cost is included;
- phase boundaries are frozen before search;
- neutral search recovers them on disjoint ecologies.

---

## Q4 — Can the theory predict a form of intelligence humans have not discovered?

### Current answer

**Not yet.**

A legitimate positive requires:

```text
known-parent frontier mapped
-> theory predicts a phase-diagram hole
-> required properties frozen before search
-> neutral basis/search discovers candidate
-> candidate non-equivalent to every applicable known parent
-> new Pareto/developmental region
-> disjoint ecology replication
-> independent search/implementation where feasible
```

No current OCM/Track-B result meets this bar.

Current terminal:

```text
UNKNOWN_MORPHOLOGY_NOT_YET_PREDICTED_OR_DISCOVERED
```

---

## Q5 — Can the process that generates intelligence forms itself improve?

### Current answer

Conceptually formalized as meta-morphogenesis, but empirically unestablished.

This would require evidence that later generations improve the process that searches/generates future morphologies, e.g. lower cost to discover frontier-improving forms on fresh ecologies, with parent/AutoML/evolutionary search controls.

Current terminal:

```text
META_MORPHOGENESIS_UNESTABLISHED
```

---

# Current best answer to “what is general machine intelligence?”

The evidence does **not** currently support:

> one special ORION cognitive atom is the universal building block of intelligence.

The strongest defensible hypothesis is instead:

> Machine intelligence consists of resource-bounded adaptive computational morphologies generated from some execution/development basis; different factorizations and learning laws become advantageous under different task, information, verification, hardware and lifetime regimes. Generality lies in the laws connecting basis, development, ecology and morphology—not in one privileged architecture.

A compact current scaffold is:

\[
\boxed{
\mathfrak B
\to \mathcal M_B
\to \mathcal F_B(E)
\leftarrow \Gamma
}
\]

with

\[
M_{t+1}=U(M_t,e_t).
\]

Known neural/symbolic/probabilistic/programmatic/OCM-like systems are candidate regions/equivalence classes within `M_B`, not presumed foundations.

# What would turn this from a framework into a scientific theory?

Minimum decisive evidence:

1. a frozen shared basis with non-vacuous family-scale derivations of several known morphology families;
2. bounded developmental compilation, not only finite representability;
3. a prospective quantitative morphology-frontier/phase prediction;
4. blind recovery on disjoint ecologies;
5. strong algorithm-selection/resource-rational/AutoML parent subtraction;
6. ideally a predicted phase-diagram hole followed by discovery of a non-parent-equivalent morphology.

Until then the correct top-level status is:

```text
GENERAL_MACHINE_INTELLIGENCE_GENERATIVE_FRAMEWORK_PROVISIONAL
UNIQUE_FUNDAMENTAL_ATOM_NOT_SUPPORTED
PREDICTIVE_MORPHOGENESIS_LAW_NOT_YET_ESTABLISHED
```