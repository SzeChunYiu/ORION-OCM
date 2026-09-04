# Warranted Parity Learning

**Natural-class theorem candidate V1 — exact query and certificate results; priority unresolved**

Date: 2026-09-03  
Scientific umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Focused lane: ORION-V2 #221  
Draft implementation: ORION-V2 PR #226

## 1. Natural class

The current target is a parity function

```text
f_theta(x) = x^T theta mod 2,
```

with `theta,x in F_2^p`. A certified training ledger contains labeled linear equations with record identity, provenance scope and revocation state. A prediction is warranted only when every parameter vector consistent with the surviving certified equations gives that label.

## 2. Exact linear warrant

Let surviving records form matrix `A` and labels `b=A theta`. For query `x`:

### Theorem WPL-1

The label `x^T theta` is determined by the surviving ledger iff

```text
x in rowspan(A).
```

When warranted, coefficients `lambda` with `lambda^T A=x` give a positive certificate and label `y=lambda^T b`. When not warranted, there exists disagreement witness `v` with

```text
A v = 0,
x^T v = 1.
```

Then `theta` and `theta+v` are both consistent with the ledger but disagree on `x`.

This gives a tractable natural class with short positive and negative witnesses, unlike unrestricted implicit support where RETAIN/RETRACT is NP/coNP asymmetric.

## 3. Provenance-redundancy family

For each coordinate `i`, the ledger contains primary certified equation

```text
P_i: e_i^T theta = theta_i.
```

For every authority/scope context `j`, an independent backup record with the same equation and a distinct provenance identity is present exactly when hidden bit `z[i,j]=1`. All primaries are live during ordinary training, so the current parity function is exactly identified for every backup profile.

The lifecycle challenge revokes primary `P_i` and asks whether coordinate claim `i` remains warranted in context `j`. Other coordinate primaries cannot span `e_i`; the correct response is RETAIN exactly when the scoped backup exists, otherwise ABSTAIN or RETRACT under the registered policy.

## 4. Exact query-complexity separation

A current-function membership query returns one bit `f_theta(x)`. A warrant query returns one backup-provenance bit `z[i,j]`.

### Theorem WPL-2

The deterministic exact query complexity of learning the current parity function is exactly

```text
p.
```

The deterministic exact query complexity of the lifecycle concept `(theta,z)` is exactly

```text
p + p*h = p(h+1).
```

The additional lifecycle query complexity is exactly

```text
p*h.
```

Lower bound: there are `2^p` parity functions and independently `2^(p*h)` warrant profiles; each binary query contributes at most one bit, and current-function queries are independent of `z`. Upper bound: query standard basis vectors to recover `theta`, then query every coordinate-context backup bit.

### Corollary WPL-2A

Even the complete current parity function gives no information about the `p*h` future-warrant bits. Within each exact `theta` fiber remain `2^(p*h)` lifecycle-distinct worlds. Thus

```text
Warrant Lift(lifecycle | exact current function) = p*h bits.
```

## 5. Sound useful repair

After evidence revocation, apply WPL-1 to surviving scope-valid records.

- If `x` is in the row span, retain the claim with certificate `lambda`.
- Otherwise produce disagreement witness `v` and abstain or retract.
- A surviving independent support prevents needless deletion.
- Missing support never authorizes retaining the old model output.

This blocks both degenerate policies:

```text
retain everything -> false authority when support vanished
delete everything -> destroys still-supported useful knowledge
```

## 6. Exact finite validation

The primary witness uses `p=3`, `h=2`:

- 8 current parity functions;
- 64 warrant profiles per function;
- 512 lifecycle concepts;
- current exact query complexity 3;
- additional warrant query complexity 6;
- total lifecycle query complexity 9;
- every coordinate-context primary-revocation challenge checked;
- positive row-span certificates and negative disagreement witnesses checked;
- both false-retention and delete-everything controls fired.

The checker also exhausts every binary matrix with zero through three rows in dimension three, every `theta`, and every query vector, validating the row-space iff warrant theorem and both certificate types.

## 7. Novelty boundary

Parity learning, Gaussian elimination, linear-algebra certificates, redundant evidence, data provenance, exact query lower bounds and dynamic rank maintenance are parent-owned.

The residual candidate is the lifecycle-learning formulation that separates exact learned behavior from future provenance/authority warrant, integrates positive and negative certificates, demands useful retention under revocation, and embeds the class inside Warrant Lift and the strict-interface frontier.

Priority remains unresolved until robust/deletion learning, version-space certification, provenance, truth maintenance, knowledge compilation and certified/ticketed unlearning are reconstructed at theorem level.

## 8. Equal-architecture boundary

A recurrent/looped Transformer supplied with the same ledger, scopes, revocation events and arithmetic precision can implement the finite algorithm. This is an architecture-neutral interface/resource theorem, not a post-Transformer expressivity result.

## 9. Next strengthening

Replace duplicate coordinate records with nontrivial distinct proof paths, such as sparse linear combinations or representable-matroid circuits. Then characterize minimum compiled warrant representation and dynamic revalidation complexity under deletions.

## 10. Authority

Supported: exact natural-class separation between current-function and lifecycle query complexity; row-space warrant characterization; constructive positive/negative certificates; useful-retention controls; exhaustive finite checks.

Not supported: literature priority, novelty, post-Transformer architecture, parameter efficiency, natural-language competence, quantum advantage or publication readiness.
