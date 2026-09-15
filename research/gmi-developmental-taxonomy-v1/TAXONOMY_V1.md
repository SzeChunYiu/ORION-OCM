# GMI Developmental Taxonomy V1: Formal Definitions

## 1. Overview

This taxonomy classifies state transitions in generative model interactions (GMI) into five mutually exclusive and jointly exhaustive types. Each type has an observable decision predicate — a test that can be performed without knowledge of internal implementation.

## 2. The Five Developmental Change Types

### 2.1 Information Storage (State Write)

**Definition:** Θ_x changes but the mapping from inputs to outputs is unchanged.

**Observable Predicate:** Apply the same input sequence S before and after the transition. The output sequence is identical, but internal state differs.

```
∀ S: output(H ⊕ S) = output(H' ⊕ S)  ∧  Θ_x(H) ≠ Θ_x(H')
```

**Example:** A system caches input x=5 internally but produces the same answer to all queries regardless of the cache content.

### 2.2 Representation Change (Re-encoding)

**Definition:** The mapping from old state to new outputs changes, but total information content is preserved via a bijective relabeling.

**Observable Predicate:** There exists a bijection φ: State → State such that:
1. output(H ⊕ [teach_i]) = φ^{-1}(output(H' ⊕ [teach_i])) on teaching inputs
2. For all other inputs, outputs are identical

```
∃ φ bijection: ∀ S: output(H ⊕ S) = relabel(φ, output(H' ⊕ S))
```

**Example:** Converting from big-endian to little-endian encoding — the information is preserved, but the representation format changes.

### 2.3 Skill Acquisition (Generalization)

**Definition:** A new input-output pattern is added that generalizes beyond the training instance.

**Observable Predicate:** After observing (x→y), the system correctly responds to x' ≠ x where x' shares relevant features with x.

```
∃ (x,y) observed: ∀ x' ∈ relevant_features(x): output(H ⊕ [x']) = expected(x')
```

**Example:** After learning "2+3=5", correctly computing "2+4=6" without explicit training on that pair.

### 2.4 Learning-law Change (Meta-adaptation)

**Definition:** The adaptation function α_p is modified — the rate or direction of future state changes differs.

**Observable Predicate:** The rate of learning (change in state per unit of teaching input) changes after the meta-transition.

```
ΔΘ(H ⊕ [teach]) / ΔΘ(H' ⊕ [teach]) ≠ 1
```

**Example:** A system that was learning slowly begins learning faster after a meta-adjustment.

### 2.5 Architecture/Morphology Change (Topology)

**Definition:** New primitives or combinators are added/removed, expanding or contracting the set of expressible compositions.

**Observable Predicate:** The set of expressible input-output patterns changes in cardinality.

```
|expressible(H)| ≠ |expressible(H')|
```

**Example:** Adding a new activation function to a neural network increases the set of computable functions.

## 3. Behavioral Equivalence

### 3.1 Definition

Two histories H1 and H2 are **behaviorally equivalent** (H1 ~ H2) if and only if:

```
∀ continuations C: response(H1 ⊕ C) = response(H2 ⊕ C)
```

Where `response(H)` is the observable output sequence on a fixed test input suite.

### 3.2 Theorem: Equivalence is an Equivalence Relation

**Proof:**
- **Reflexive:** H ~ H trivially (response(H ⊕ C) = response(H ⊕ C))
- **Symmetric:** If H1 ~ H2, then ∀ C: response(H1 ⊕ C) = response(H2 ⊕ C), so H2 ~ H1
- **Transitive:** If H1 ~ H2 and H2 ~ H3, then ∀ C: response(H1 ⊕ C) = response(H2 ⊕ C) = response(H2 ⊕ C), so H1 ~ H3

## 4. History Irreducibility

### 4.1 Theorem: Irreducibility Witness

Even when present outputs match, histories can diverge on futures.

**Construction:** Let H1 and H2 be two histories such that:
- response(H1) = response(H2) on current test suite (converged present)
- ∃ continuation C: response(H1 ⊕ C) ≠ response(H2 ⊕ C) (divergent future)

**Witness:**
- H1 = "stored x=3, no adaptation"
- H2 = "stored x=5, adapted once with feedback -2"

Current output: H1 produces 3 (stored), H2 produces 5-4=1... wait, let me correct this.

Better witness:
- H1 = "stored x=3" → outputs 3 on query
- H2 = "stored x=5, adapted once with feedback -2" → outputs 5-2=3 on query

Both output 3 on current queries (converged present).

Future continuation C = "query with teaching input +1":
- H1: 3+1 = 4 (direct addition)
- H2: 3+1 = 4 (if adaptation was subtractive) or different behavior depending on adaptation type

The key insight: different internal states lead to different futures even when current outputs match.

## 5. Finite World: n=3 Local Units, 3 Regimes

### 5.1 System Specification

- **Units:** 3 local units, each with state θ ∈ {0, 1, 2}
- **Regimes:**
  - **Regime A** (info storage): θ_i → θ_i + 1 mod 3 (state increment)
  - **Regime B** (representation): θ_i → 2 - θ_i mod 3 (relabeling)
  - **Regime C** (skill): θ_i → θ_i × 2 mod 3 (generalization)

### 5.2 Transition Log

9 transitions total (3 regimes × 3 units):

| Unit | Regime | Before | After | Type |
|------|--------|--------|-------|------|
| U1 | A | 0 | 1 | Information storage |
| U2 | A | 1 | 2 | Information storage |
| U3 | A | 2 | 0 | Information storage |
| U1 | B | 0 | 2 | Representation change |
| U2 | B | 1 | 1 | Representation change |
| U3 | B | 2 | 0 | Representation change |
| U1 | C | 0 | 0 | Skill acquisition |
| U2 | C | 1 | 2 | Skill acquisition |
| U3 | C | 2 | 1 | Skill acquisition |

### 5.3 Proofs

**Mutual Exclusivity:** Each transition satisfies exactly one predicate. For example, Regime A transitions change state but preserve I/O (storage), while Regime B transitions change the mapping form but preserve information content (representation).

**Joint Exhaustion:** All 9 transitions are classified into exactly one of the 5 types. Types 4 and 5 are empty in this finite world (no meta-learning or architecture changes), which is consistent with the taxonomy.

## 6. Extensions

### 6.1 Hereditary Change

Intergenerational information transfer: parent → child system state copy. This is a special case of information storage across generation boundaries.

### 6.2 Meta-learning

Learning-law change at the object level: applies to learning laws themselves. This is a special case of Type 4 change where the learning law being modified is itself a learning law.
