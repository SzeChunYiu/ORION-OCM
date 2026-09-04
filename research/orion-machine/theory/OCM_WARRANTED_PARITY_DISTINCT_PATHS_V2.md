# Warranted Parity Learning with Distinct Proof Paths

**Natural-class theorem candidate V2 — duplicate-evidence shortcut removed; priority unresolved**

Date: 2026-09-03  
Umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Focused lane: ORION-V2 #221  
Draft PR: ORION-V2 #226

## 1. Target class

Let the current predictor be parity

```text
f_theta(x) = x^T theta mod 2,
```

with `theta,x in F_2^p`. Certified records are labeled linear equations with record identity, provenance, authority/scope and revocation status.

For surviving ledger `(A,b)`, query `x` is warranted exactly when `x` lies in `rowspan(A)`. A positive certificate is `lambda` with `lambda^T A=x` and label `lambda^T b`. When `x` is outside the row span, a disagreement certificate is `v` with `A v=0` and `x^T v=1`.

## 2. Distinct scoped proof paths

For each coordinate `i`, a primary record states

```text
P_i: e_i^T theta = theta_i.
```

For each context `j`, choose bridge coordinate `s(i,j) != i`. Optional backup bit `z[i,j]=1` creates a distinct scoped equation

```text
B_i,j: (e_i + e_s)^T theta = theta_i + theta_s.
```

The backup differs from the primary in vector, content, record identity and scope. During challenge `(i,j)`, only this scoped backup is eligible; other scoped backups are inactive. Revoking `P_i` leaves `P_s`, so when `B_i,j` exists:

```text
e_i = (e_i + e_s) + e_s.
```

The positive warrant certificate must use both `B_i,j` and surviving `P_s`. When the backup is absent, surviving global primaries span only coordinates other than `i`, so `e_i` is not warranted.

## 3. Exact query complexity

Current parity learning has deterministic exact membership-query complexity `p`. The independent scoped backup profile contains `p*h` bits invisible to the entire current function. Therefore the lifecycle concept `(theta,z)` has exact binary-query complexity

```text
p + p*h = p(h+1),
```

with additional warrant complexity exactly `p*h`.

The lower bound is information-theoretic and interface-specific: `2^p` parity functions and `2^(p*h)` independent scoped proof-path profiles; current-function queries contain zero information about the latter. The upper bound queries every standard-basis label and every scoped proof-path bit.

## 4. Sound useful repair

After revocation or scope change:

- retain only if a row-span certificate exists in the surviving scope-valid ledger;
- otherwise produce a disagreement witness and abstain/retract;
- a surviving distinct proof path prevents destructive delete-everything behavior;
- the old predictor output never self-authorizes after its support vanishes.

This provides both soundness and useful retention on the registered class.

## 5. Exact validation

The V2 checker uses `p=3`, `h=2`:

- 8 current parity functions;
- 64 scoped warrant profiles per function;
- 512 lifecycle concepts;
- 3 current-function queries;
- 6 additional warrant queries;
- 9 total lifecycle queries;
- 3,072 coordinate-context revocation challenges;
- every positive certificate verified to include the distinct mixed backup and its bridge primary;
- every absent-backup case carries a valid disagreement witness;
- false-retain and false-retract controls both fire.

It also exhausts every binary matrix with zero through three rows in dimension three, every consistent `theta`, and every query vector—37,440 matrix/parameter/query cases—checking the row-span iff warrant criterion and both certificate types.

## 6. Scientific effect

V2 removes the strongest artificiality objection to the first Warranted Parity construction: future warrant is not encoded by a duplicate of the primary record. It is encoded by the presence of a distinct, independently scoped proof path that becomes useful only when combined with another surviving record.

The result remains architecture-neutral. A recurrent/looped Transformer with the same certified ledger and arithmetic can implement it.

## 7. Parent and novelty boundary

Parity learning, Gaussian elimination, linear dependence, matroid closure, provenance and exact query counting are parent-owned. The current residual is the lifecycle-learning object:

- exact current function and full current oracle remain blind to future proof-path availability;
- scope and provenance alter future warrant without changing current behavior;
- positive and negative certificates support non-destructive repair;
- Warrant Lift measures the extra lifecycle state;
- endpoint, raw-trace, positive-support and closure-certified interfaces are strictly separated.

Priority remains open pending theorem-level comparison with version-space certification, matroid/linear provenance, dynamic rank, exact/deletion learning, TMS/ATMS, knowledge compilation and certified/ticketed unlearning.

## 8. Next theorem

Generalize from isolated two-record paths to sparse representable-matroid circuits with overlapping support. Characterize minimum compiled warrant state and deletion/scope-change revalidation complexity; prove a non-cardinality lower bound and an output-sensitive upper bound under equal information.

## 9. Authority

Supported: natural-class exact query separation, distinct proof paths, row-span warrant characterization, positive/negative certificates and useful-retention controls.

Not supported: literature priority, novelty, post-Transformer architecture, parameter efficiency, natural-language competence, quantum advantage or publication readiness.
