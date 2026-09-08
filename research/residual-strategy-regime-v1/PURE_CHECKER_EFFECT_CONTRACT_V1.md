# Certified pure checker calculus — constructive R0A parent

**Status:** research-only restricted language / no production integration / no ML authorization.

`R0A_SUFFIX_ELISION_AUDIT_V1.md` proves that an arbitrary dynamically guarded Python checker cannot be omitted safely: the guard discovers a forbidden effect only by executing the callback.  This note gives the constructive parent implied by effect systems and proof-carrying code: replace omission-time guessing with admission-time proof by construction.

The goal is deliberately small.  We do not try to prove arbitrary Python pure.  We define a finite checker language whose semantics has no capability to mutate OCM runtime state, and whose certificate is mechanically checkable before any solve.

## 1. Checker language

A checker program is a finite syntax tree over detached candidate data:

```text
Predicate ::= TRUE
            | FALSE
            | HAS(path)
            | TYPE(path, kind)
            | EQ(path, literal)
            | AND(Predicate, Predicate)
            | OR(Predicate, Predicate)
            | NOT(Predicate)

Checker ::= STATUS(PASS | FAIL | CANNOT_CHECK)
          | IF(Predicate, Checker, Checker)
```

where:

- `path` is a bounded tuple of plain string mapping keys / integer sequence indices;
- `kind` is one of the closed detached-data kinds accepted by the runtime candidate boundary;
- `literal` is canonical detached data with a prospectively bounded size;
- syntax depth and node count are bounded at admission.

The interpreter receives only the detached candidate value and immutable checker AST.  It receives no runtime object, ledger, file/network handle, arbitrary Python callable, reflection primitive, import primitive, clock, randomness, or external authority.

## 2. Static effect judgment

Use the judgment

```text
Gamma |- e : T ! epsilon
```

with only one admissible effect set for certified programs:

```text
epsilon = empty.
```

Every primitive above is a total read-only operation on bounded detached data.  Composition rules union child effects; because every leaf has `empty`, every well-formed AST has `empty`.

### Theorem 1 — effect soundness by structural induction

For every AST accepted by the validator,

```text
Gamma |- checker : Status ! empty.
```

### Proof

Induct on syntax.

Base predicates (`TRUE`, `FALSE`, `HAS`, `TYPE`, `EQ`) only inspect their supplied detached values and contain no effectful primitive.  `STATUS` returns a literal registered status.  Hence each leaf has effect `empty`.

For `NOT`, `AND`, `OR`, the induction hypothesis gives empty effects for children; the only composition operation is pure Boolean combination, so the parent effect is their union, still empty.

For `IF`, the predicate and both branches have empty effects by induction.  Evaluation selects one branch without adding a capability; the union remains empty.  Thus every admitted checker has empty effects. QED.

The proof is relative to the small interpreter implementation and the candidate-data boundary.  A bug in either must be handled by ordinary code review/testing or a stronger mechanical proof; the theorem does not magically prove the Python VM.

## 3. Termination and resource bound

The language has no loops, recursion, dynamic code generation, or user callback.  Every AST is finite and every candidate-data traversal is bounded by the already-materialized detached value.

Let:

```text
N = AST node count
D = maximum admitted path length
V = total detached candidate-data nodes visited by resolved paths/literal comparison
```

Then a direct interpreter has a finite work bound of order

```text
O(N * D + V)
```

with a tighter exact counter available from the executable interpreter.  The admission validator prospectively caps `N`, path length, literal size and AST depth.

### Theorem 2 — totality on admitted detached data

Every admitted checker evaluation terminates with exactly one registered status.

### Proof

Structural recursion strictly descends a finite AST.  Path resolution iterates a bounded finite tuple over already-finite detached data.  Literal comparison uses the closed canonical data comparison.  There is no recursive call on dynamically generated syntax or unbounded loop. QED.

## 4. Omission theorem for certified-pure tail checkers

Suppose `check_stage` has obtained its first PASS from candidate `f`, and every tail candidate `j>f` has a checker admitted under this calculus.  Assume the protected trace contract has prospectively declared the execution of redundant certified-pure tail checkers to be silent, or records a contract-equivalent summary event rather than each concrete verdict.

Then omitting those tail checker evaluations preserves:

```text
runtime persistent state;
callback event position;
revocation/evidence/operator epochs;
selected first passing candidate;
answer/decision under current passed[0] semantics;
all future lifecycle behavior attributable to runtime state.
```

### Proof

By Theorem 1 the omitted checkers have no runtime capability/effect, so their execution cannot alter protected persistent state or event position.  By Proposition 1 in `R0A_SUFFIX_ELISION_AUDIT_V1.md`, ordinary tail verdicts after an existing first PASS cannot change the selected first PASS or CHECK PASS status.  The prospective trace refinement discharges the remaining audit-observation difference.  Thus the omitted suffix is silent at the registered contract scope. QED.

Without the trace-refinement premise, literal current `CHECKER_RESULT` equality still fails; purity alone is not enough.

## 5. Certificate

A certificate is not a probabilistic score.  It contains the complete bounded AST and admission metadata:

```text
schema
language_version
ast
ast_sha256
node_count
max_depth
max_path_length
literal_bytes
claimed_effects = []
```

The verifier recomputes every field and rejects unknown syntax, malformed literals, oversized programs, nonempty claimed effects, or hash mismatch.  No trust is placed in a producer's `pure=true` assertion.

This is closer to proof-carrying code than to learned purity classification: the consumer checks a compact, deterministic proof object under a fixed policy before admission.

## 6. Capability boundary

The interpreter API must remain capability-minimal:

```text
evaluate(certified_checker, detached_candidate) -> Status
```

It must not accept `OCMRuntime`, `KnowledgeSpace`, an operator callback, host object, closure, module namespace, filesystem/network handle or arbitrary comparator.  Otherwise the effect theorem's premise is false.

## 7. Economic gate

A certified checker is useful for R0A only if its lifecycle cost repays omitted work.

Let:

```text
B     = one-time certificate validation/build cost
M     = retained manifest/storage/update cost over one operator lifecycle
u     = per-use interpreter/dispatch overhead relative to incumbent checker
s     = expected tail-check work removed per eligible query
H     = eligible repeated uses before invalidation/re-registration
```

Then even after semantic authorization the optimization requires

```text
H * s > B + M + H * u.
```

Equivalently, if `s<=u`, no lifetime can amortize the certificate path.  If `s>u`, a necessary break-even horizon is

```text
H > (B+M)/(s-u).
```

Publish raw resource vectors before choosing scalar prices.

The old frozen R0 test population provides at most 20 removable CHECK-stage callbacks total and does not establish repeated operational demand, so it cannot by itself justify a production certificate mechanism.

## 8. Migration rule

Existing arbitrary Python checkers do **not** become certified because they happen to look simple or passed a finite test corpus.  Migration requires expressing the intended predicate in the restricted language and separately proving observational equivalence between the old checker and the new checker on its declared domain, or changing the operator contract prospectively.

The host-supplied old callback remains authoritative until that migration proof exists.

## 9. Current terminal

The restricted calculus demonstrates that the R0A gap is solvable by conventional semantics/capability design without ML, but it does not authorize a current runtime patch.

```text
PURE_CHECKER_EFFECT_PARENT_AVAILABLE_R0A
PRODUCTION_MIGRATION_AND_TRACE_CONTRACT_NOT_ESTABLISHED
LEARNED_ROUTER_NOT_AUTHORIZED
```
