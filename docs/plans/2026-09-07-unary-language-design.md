# Unary language semantic contract

Prospective implementation decision, 7 September 2026. Conventional exact symbolic
parent and supplied controlled language; no learned transfer or novelty claim.

- Scope: one to four distinct predicate identifiers, nonempty domain, possibly empty
  predicates; Boolean expressions have explicit parentheses. No equality, cardinality,
  pronouns, morphology, external facts, learner, persistence or OCM integration.
- Data: versioned strict JSON task with sorted exactly-used predicate names, ordered
  premises and one query. Expressions: pred/not/and/or. Statements: every/no/some/not_every.
- Surface: zero or more statements ending in periods, then `query STATEMENT?`.
  Example: `every A is B. no B is C. query some A is C?`.
  Groups: `(not A)`, `(A and B)`, `(A or B)`. Names retain exact identity.
- Solver: cached masks over all 2^n membership regions. Universals forbid regions;
  each existential independently requires a remaining region. Domain needs one region.
  Query and its negation are checked separately after premise consistency.
- Results: ENTAILED, CONTRADICTED, UNKNOWN (both models), INCONSISTENT.
  Invalid/outside grammar inputs are INPUT_REFUSED, not semantic negatives.
- Certificates: nonempty finite region-world models, or an impossible existential/domain
  obligation plus universal-constraint cover. Result binds the exact validated task digest.
- Independent verifier interprets ASTs directly, never imports/calls the optimized solver.
  It verifies both polarity certificates and rejects malformed/tampered payloads.
- Bounds: 4 predicates, 32 premises, expression depth 16, total 512 expression nodes,
  32 ASCII identifier characters, 16 KiB text. Bounds are registered engineering scope.
- Counters report optimized mask/cache/constraint/witness work only; they do not prove
  total CPU/RSS or include all validation/serialization work.
- Qualification: meaningful authored hostiles plus exhaustive nonempty worlds with up
  to three predicates for a declared generated task family. This is a semantic oracle,
  not untouched scientific evaluation. Preserve all attempts and source generations.
