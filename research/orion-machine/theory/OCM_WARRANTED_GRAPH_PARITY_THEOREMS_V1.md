# Warranted Graph-Parity Learning and the Quadratic Warrant Gap

**Natural overlapping-proof theorem candidate V1 — communication lower bound and exact certificates; priority unresolved**

Date: 2026-09-03  
Scientific umbrella: ORION-V2 #194  
Execution master: ORION-V2 #197  
Focused lane: ORION-V2 #221  
Draft PR: ORION-V2 #226

## 1. Model

Let vertices be a root `r` and `n` learned objects. Hidden labels are binary, with anchored `theta_r=0`. A certified evidence edge `(u,v)` carries parity equation

```text
theta_u + theta_v = b_e mod 2.
```

The current function returns vertex labels. A label is warranted only when it is uniquely determined by surviving certified edges.

Primary star edges `(r,v)` are present during ordinary training, so the exact current function is learned. An arbitrary optional graph on non-root vertices supplies overlapping alternative proof paths. Optional edge presence does not change the current function.

## 2. Graphical warrant theorem

### Theorem WGPL-1

For any surviving certified graph, vertex `v`'s label is warranted iff `v` is connected to the anchored root.

- A root-to-`v` path is a positive certificate; XOR of edge labels yields `theta_v`.
- If `v` is disconnected, flip every hidden label in `v`'s connected component. All surviving edge labels remain unchanged, but `theta_v` changes. The component/cut is a negative disagreement certificate.

Thus root connectivity is exactly the lifecycle warrant relation.

## 3. Isolated-edge lifecycle challenges

Let the optional-edge universe be every pair among the `n` non-root vertices, with

```text
N = binom(n,2).
```

For optional edge `{u,v}`, issue a challenge that keeps primary `(r,u)`, revokes every other primary, revokes every optional edge except `{u,v}`, and asks whether `v` remains warranted.

The answer is RETAIN exactly when optional edge `{u,v}` exists. If present, path `r-u-v` is a two-edge certificate. If absent, `v` is disconnected.

The full batch of `N` lifecycle challenges recovers the entire optional graph, even though every optional graph gives the same exact current function for fixed `theta`.

## 4. Quadratic Warrant Gap

### Theorem WGPL-2

Conditioned on the exact current function,

```text
Warrant Lift = N = binom(n,2) = Theta(n^2).
```

The current function needs `n` label bits. Exact lifecycle warrant under the registered challenge family needs `N` additional bits. A compact exact predictor is therefore not automatically a compact safe lifelong learner.

## 5. Exact query and storage frontier

Current-function queries need exactly `n` bits. Edge-warrant queries need exactly `N` additional bits for the full challenge batch.

With compiled summary `B`, `Q` binary ledger queries across the batch and at most `A` abstained challenges, zero-error response requires

```text
B + Q + A >= N.
```

The bound is tight: store any `B` edge bits, query any `Q` remaining bits and abstain on the rest.

## 6. Communication lower bound

Let optional graph `Z` be uniform on `{0,1}^N`. A preprocessing algorithm creates a `B`-bit warrant summary; the original ledger is then unavailable. A decoder answers all isolated-edge challenges with average bit error at most `epsilon`.

### Theorem WGPL-3

```text
B >= N [1 - h_2(epsilon)],
```

where `h_2` is binary entropy.

**Proof.** Let `epsilon_i` be the error for optional edge `i`. Binary Fano gives `H(Z_i|S)<=h_2(epsilon_i)`. Subadditivity and concavity give

```text
H(Z|S) <= sum_i H(Z_i|S)
       <= sum_i h_2(epsilon_i)
       <= N h_2(epsilon).
```

Since `H(Z)=N`,

```text
B >= H(S) >= I(Z;S) >= N[1-h_2(epsilon)].
```

At zero error, `B>=N`, matching the adjacency-bitset upper bound.

This is a communication/information lower bound for a natural overlapping proof network, not a parameter-count comparison.

## 7. Useful repair

After arbitrary evidence deletion, maintain or recompute root connectivity:

- connected vertices retain labels with path certificates;
- disconnected vertices retract or abstain with cut/component certificates.

The naive algorithm is polynomial and preserves every still-supported label. Dynamic connectivity and graph provenance are strongest parents for faster bounds.

## 8. Exact validation

The primary witness uses `n=4`, hence `N=6`:

- 16 current functions;
- 64 optional proof graphs per function;
- 1,024 lifecycle concepts;
- 6,144 isolated-edge lifecycle challenges;
- 3,072 positive two-edge path certificates;
- 3,072 negative cut/flip certificates;
- zero current-function leakage of optional graph state;
- both false-retain and destructive-delete controls.

The checker also exhausts all 1,024 graphs on five vertices, all 16 root-anchored labelings and all four non-root query vertices: 65,536 graph/label/query checks of connectivity iff warrant.

## 9. Novelty boundary

Connectivity, path/cut certificates, graph provenance, dynamic connectivity, parity constraints, entropy and communication lower bounds are parent-owned.

The residual candidate is their integration into a learned lifecycle object:

- optional overlapping evidence paths do not affect the exact current predictor;
- future scope/revocation behavior reveals a quadratic amount of additional warrant state;
- Warrant Lift quantifies the gap;
- current-function learning is oracle-blind to it;
- positive and negative certificates support safe useful repair;
- the theorem is evaluated under a full lifecycle challenge language.

Priority remains open pending theorem-level subtraction against graph/matroid provenance, dynamic connectivity, deletion-robust learning, version-space certification, TMS/ATMS, knowledge compilation and certified/ticketed unlearning.

## 10. Architecture boundary

An equally provisioned recurrent Transformer can execute graph search and certificate checking. This is an architecture-neutral learning, representation and resource separation, not post-Transformer expressivity.

## 11. Next breakthrough target

Move from an explicit optional graph to a learned sparse proof network. Compare endpoint-only, raw local traces, positive path certificates and closure-certified graph/provenance state. Prove acquisition cost, compiled-summary lower bound and output-sensitive repair under partial, corrupt and scope-expiring certificates; then perform equal-interface recurrent-Transformer compilation.

## 12. Authority

Supported: graphical warrant characterization, quadratic Warrant Lift, exact query/storage/abstention frontier, communication lower bound, positive/negative certificates and exhaustive finite checks.

Not supported: literature priority, novelty, post-Transformer architecture, useful-task parameter efficiency, natural-language competence, quantum advantage or publication readiness.
