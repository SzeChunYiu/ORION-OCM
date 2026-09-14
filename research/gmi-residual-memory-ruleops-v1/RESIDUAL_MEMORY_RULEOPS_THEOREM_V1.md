# RESIDUAL_MEMORY_RULEOPS_THEOREM_V1

Formal theorems for residual memory conditions, retrieval frequency laws, index cost laws, and rule operators derived from generic transformations.

## Residual Memory Condition

**Theorem (When External Memory is Required):**

Let \( T \) be a task requiring \( N \) distinct facts, and let \( C \) be the parametric capacity of a model (maximum facts storable in parameters). Let \( r \) be the retrieval cost per query (in tokens/operations) and \( p \) be the parametric expansion cost per fact.

External memory is retained iff:
\[ r < p \cdot (N - C) \]

**Intuition:** When the task's obligation grows with context length \( N \) beyond the parametric capacity \( C \), external memory is beneficial when the retrieval cost per query is less than the cost of expanding the parameters to absorb the additional facts.

## Predictive-Target Residual Quotient

**Theorem (Residual Quotient):**

For a predictive target \( Y \) with \( N \) relevant facts, the residual memory quotient is:
\[ Q = \frac{\text{freq}(Y) \cdot N}{C + \text{retrieval\_count} \cdot r} \]

where:
- \( \text{freq}(Y) \) = frequency of target \( Y \) in the task distribution
- \( C \) = parametric capacity
- \( \text{retrieval\_count} \) = number of retrievals per query
- \( r \) = retrieval cost per fact

When \( Q > 1 \), external memory provides a net advantage.

## Retrieval Frequency Law

**Theorem (Square-Root Scaling):**

Given \( K \) distinct facts accessed with frequency \( p_i \) (where \( \sum p_i = 1 \)), the optimal retrieval frequency for fact \( i \) scales as:
\[ f_i \propto \sqrt{p_i} \]

This is the classic square-root law: more frequently accessed facts should be retrieved more often, but at a sublinear rate.

**Proof sketch:** Minimize total cost \( \sum_i p_i \cdot c(f_i) \) subject to retrieval budget, where \( c(f_i) \) is the cost of accessing fact \( i \) at frequency \( f_i \). The optimal solution yields \( f_i \propto \sqrt{p_i} \).

## Index Cost Law

**Theorem (Index Building Cost):**

Building a retrieval index for \( K \) facts costs \( O(K \log K) \) operations (dominated by sorting/hashing).

**Amortization condition:** The index cost is amortized when:
\[ \text{retrieval\_count} > \frac{K \log K}{C} \]

where \( C \) is the parametric cost equivalent (the number of facts that could be absorbed into parameters for the same cost).

## Rule/Rewrite Operators from Generic Transformations

**Theorem (Minimal Rewrite System):**

Given a set of input-output pairs \( \{(x_i, y_i)\}_{i=1}^n \), the minimal rewrite system that captures all transformations has complexity:
\[ \text{complexity} = \frac{K(x, y)}{\alpha} \]

where:
- \( K(x, y) \) = Kolmogorov complexity of the pair set
- \( \alpha \) = alphabet size

This is derived from PVR-3 applied to description length: the minimal program size is bounded by the information content of the pairs divided by the encoding efficiency.

**Emission vs Selection:**
- **Emitter rule:** \( \text{emit}(x) = \text{transform}(x, \text{context}) \) — produces output from input + context
- **Selector rule:** \( \text{select}(x, Y) = \arg\max_{y \in Y} \text{sim}(x, y) \) — chooses from a set of candidates

The minimal rewrite system requires both emitters (for novel outputs) and selectors (for choosing among existing options).

## Comparison with Existing Systems

| System | Type | Memory | Retrieval | Policy |
|--------|------|--------|-----------|--------|
| **Residual Memory** | Hybrid | External + Parametric | Adaptive | Frequency-based |
| **RAG** | External only | External | Fixed (top-k) | None (always retrieve) |
| **Adapters** | Parametric only | Internal | None (all in params) | None (always use) |
| **Caches** | Working memory | External | Exact match | LRU/LFU |
| **Databases** | Storage only | External | Query-based | Manual |

**Key differences:**
- RAG retrieves but never consolidates (no forgetting)
- Adapters change laws but have no memory (no retrieval)
- Caches have working memory but no index (no frequency-based retrieval)
- Databases have storage but no policy (manual retrieval decisions)

## Neutral Recovery of Residual-Memory Behavior

**Theorem (Recovery Condition):**

A system exhibits residual-memory behavior iff it satisfies:
1. **Parametric bound:** Has a finite capacity \( C \)
2. **External storage:** Can store facts outside parameters
3. **Adaptive retrieval:** Retrieval frequency depends on access pattern
4. **Consolidation:** Can periodically absorb frequently accessed facts into parameters

**Neutral recovery:** Any system satisfying these four properties will converge to residual-memory behavior under the cost model above, regardless of its specific implementation.

---

**Parent capsules:** MEMORY_REGIME_PARTITION, CONSOLIDATION_FORGETTING
**Ceiling:** G2
