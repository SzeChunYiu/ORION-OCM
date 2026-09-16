# Cognitive re-audit theorems v1

## Theorem MEMORY-1 — functional separation, anatomical non-identification

Fix a registered probe family. Two memory roles are operationally
distinguishable iff at least one probe response differs. Hence the four frozen
working/episodic/semantic/procedural profiles are pairwise distinguishable at
that interface. This conclusion is exactly about functions: a separated-store
implementation and a tagged unified-store implementation can induce the same
complete protected responses and charged traces. No observation restricted to
that interface can identify which physical partition generated them.

## Theorem ATTENTION-1 — admissibility before resource preference

Let `T` be the required item set, `S` the selected set, `n` the full item count,
`c>0` the per-item materialization cost, and `d_F,d_S>=0` the full/selective
discovery costs. If `T` is not a subset of `S`, selection is inadmissible
regardless of cost. Otherwise

`C_S=|S|c+d_S < C_F=nc+d_F`

iff `d_S-d_F < (n-|S|)c`. Thus discovery overhead can erase the selective
advantage. For singleton queries, a fixed blind selection of `k<n` items is
exact on only `k/n` of the registered queries, so equal-size selection alone is
not an attention theorem.

## Theorem CONCEPT-1 — static quotient and partial-interface abstention

For a complete finite response table, define `x ~ y` iff their response rows
are equal on every registered query. The quotient is exact because each query
response is constant on every class. Any exact encoding must separate unequal
rows, so it refines this quotient; the response-row quotient is therefore the
coarsest exact encoding. If two completions agree on every observed response
but induce different full equivalence signatures, the full quotient is not
identified and the only sound result is `CANNOT_IDENTIFY_FROM_PARTIAL_INTERFACE`.

## Proposition ADOPT-1 — amortized adoption is not concept formation

For `r>=1`, fresh cost `f`, installation cost `i`, and lookup cost `l`, repeated
fresh work costs `rf`; retaining an already verified abstraction costs
`f+i+(r-1)l`. Retention is strictly cheaper iff `(r-1)(f-l)>i`. This comparison
does not create semantics, verify a quotient, or learn a concept from samples.

## Scope

The theorems are finite-interface, architecture-neutral statements. They do
not establish anatomical modules, a unique attention mechanism, concept
learning from partial data, or any later Section-M row.
