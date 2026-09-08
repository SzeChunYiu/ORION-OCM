# R0A prospective pure-checker binding V1

**Status:** constructive research parent / fail-closed replay identity / no production integration.

The R0A provenance audit found an exact aliasing problem in the current runtime:
operator metadata and persistent manifests do not bind checker implementation or
effect semantics.  The frozen-source forensic then showed that all 20 historical
test-tail opportunities happen to reconstruct to trivial `PASS` checker factories,
but source forensics is not runtime authority.

This tranche closes only the **prospective identity** subproblem.  It does not
change the production runtime and does not authorize early exit.

## Binding object

`r0a_prospective_checker_binding.py` combines the current operator semantic
manifest with a recomputed `pure_checker_contract.py` certificate and constructs:

```text
schema                    ocm.r0a.pure-checker.operator-binding.v1
binding algorithm         sha256-canonical-json-v1
execution mode            PURE_CHECKER_DSL_ONLY
implementation identity   PURE_CHECKER_CERTIFIED
checker certificate       schema + language + AST SHA-256 + empty effect set
binding SHA-256            hash(canonical prospective manifest)
```

The operator must already be checker-bearing and must not declare nonempty
expected checker effects.  The pure checker certificate is independently
revalidated before binding.

## Fail-closed replay controls

The additive tests require rejection under every one of these changes:

```text
operator version/semantic metadata drift;
a different but valid checker AST;
checker AST tampering without certificate regeneration;
checker language-version drift;
checker claimed-effect drift;
binding digest tampering;
an operator that declares checker effects.
```

The important control is execution, not merely serialization.  The demo operator
contains an arbitrary host checker that would mutate host-visible state and return
`FAIL` if called.  The bound research path verifies the content binding and then
executes the restricted checker DSL directly.  The result is the certificate's
`PASS`, and the host checker call count remains exactly zero.

Therefore a future migration must replace the host-callback execution mode, not
attach a certificate beside a callback that is still authoritative.

## Accounting

The binding receipt reports raw work rather than assigning a price:

```text
certificate validation AST nodes;
certificate literal bytes;
certificate SHA-256 recomputations;
binding SHA-256 recomputations;
canonical binding SHA-256 input bytes;
persistent identity bytes.
```

These are adoption costs.  Any later early-exit result must charge them against
the exact CHECK work removed over the effective lifetime of the binding.

## What remains open

This construction deliberately does not resolve the trace/lifecycle gate in
`R0A_TRACE_EQUIVALENCE_PROTOCOL_V1.md`.  A certified pure checker can be
state-effect-free while its literal CHECK occurrence is still visible to an audit
contract.  The protected observation alphabet / stuttering projection must be
frozen prospectively; it cannot be chosen after observing an optimization win.

Nor does this establish a production checker population.  The next empirical
tranche is:

```text
1. freeze a non-test checker population;
2. prospectively translate/register the subset expressible in the pure DSL;
3. bind certificate identity before execution;
4. freeze the protected trace projection;
5. run incumbent and suffix-elision variants from identical checkpoints;
6. replay revocation/reset/restore/failure lifecycle hostiles;
7. charge binding, validation, storage and replay work;
8. report certified-pure coverage and net work removed.
```

Current terminal:

```text
PROSPECTIVE_PURE_CHECKER_BINDING_CONSTRUCTIVE_PARENT_ONLY
```

No ML, learned checker, learned router, or production early-exit policy is
authorized.
