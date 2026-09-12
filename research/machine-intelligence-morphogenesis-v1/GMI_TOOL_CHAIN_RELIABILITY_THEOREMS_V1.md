# GMI Tool-Chain Reliability Theorems v1

Status: **FORMAL AGENT/TOOL HARDENING / INDEPENDENT FAILURE BASE CASE**

Status date: 2026-09-12.

Purpose:

> Extend typed tool-composition theory to uncertain tool outcomes. Derive the exact base law for independent step reliability and show how reliability becomes an additive path coordinate after a log transform.

---

# 1. Typed path with uncertain steps

Let a legal tool chain be path

\[
P=(e_1,\ldots,e_k)
\]

through the registered semantic type graph.

Tool edge `e_i` has:

```text
resource burden c_i >= 0
success probability q_i in (0,1]
```

Assume, for this base theorem:

1. step success events are independent conditional on the registered inputs;
2. the overall obligation succeeds iff every step succeeds;
3. a failed step cannot accidentally produce an admissible equivalent result unless that possibility is included in `q_i`.

---

# 2. Exact path reliability

## Theorem TR-1

Under the independence assumptions,

\[
P(\text{path success})
=
\prod_{i=1}^kq_i.
\]

Therefore path failure probability is

\[
1-\prod_iq_i.
\]

This is elementary but must be charged explicitly in multi-tool species.

---

# 3. Additive reliability length

Define reliability length

\[
r_i=-\log q_i\ge0.
\]

## Theorem TR-2 — log reliability composes additively

\[
-\log P(\text{path success})
=
\sum_ir_i.
\]

Thus a required minimum success probability

\[
P_{succ}\ge1-\delta
\]

is equivalent to path constraint

\[
\sum_ir_i
\le
-\log(1-\delta).
\]

### GMI consequence

Typed tool composition under independent failures becomes a multi-resource path problem with additive coordinates:

```text
resource cost     sum c_i
reliability cost  sum -log q_i
latency           additive or registered composition law
evidence/authority compatibility
```

---

# 4. Expected failure-loss objective

Let protected failure incur scalar loss `L`. Then chain objective is

\[
C(P)
=
\sum_ic_i
+
L\left(1-\prod_iq_i\right).
\]

## Theorem TR-3 — a cheaper raw path can be worse after reliability

For two legal paths `P,Q`, raw resource inequality

\[
\sum_{e\in P}c_e<\sum_{e\in Q}c_e
\]

does not imply

\[
C(P)<C(Q)
\]

when success probabilities differ.

Therefore raw cheapest-path routing is not generally admissible under protected failure costs.

---

# 5. Redundancy/retry of one tool

Suppose a tool call succeeds independently with probability `q>0` and costs `c` per attempt. Repeat until success or indefinitely.

## Theorem TR-4 — geometric retry burden

Expected attempts until success are

\[
\frac1q,
\]

so expected raw call burden is

\[
\frac cq.
\]

If at most `n` attempts are permitted, success probability is

\[
1-(1-q)^n.
\]

This creates the same reliability-versus-resource phase seen in inference-time search.

---

# 6. Verification changes reliability semantics

Suppose a tool's output can be checked by a sound verifier. Then a failed/incorrect output need not become an authoritative state transition; it may instead trigger retry/alternate routing.

Thus the relevant quantities split into:

```text
proposal success probability
verifier false-positive probability
verifier false-negative probability
retry/alternate-path cost
false-adoption loss
```

A nominal tool accuracy is not enough to predict agent reliability.

---

# 7. Correlated failures are a separate atom

If tool errors are correlated, TR-1/TR-2 need not hold.

Examples:

```text
two tools rely on the same stale database
two APIs share one upstream model
a planning chain propagates one early semantic error
tools are conditionally correlated through query difficulty
```

GMI must model a joint failure law or use conservative bounds.

The independence base case is still valuable because any broader theory must recover it.

---

# 8. Semantic error propagation

Even if each tool is individually “correct” under its local contract, composition can fail if output semantics do not satisfy the next tool's assumed input contract.

Therefore type/evidence compatibility remains a hard prerequisite before applying reliability multiplication.

Reliability cannot repair a type error.

---

# 9. Gap update

`GKF-14 tool composition` now has:

```text
typed shortest-path composition                         CLOSED
single-tool insufficiency / multi-step necessity        CLOSED
authority-constrained path legality                     CLOSED
independent chain reliability                           CLOSED
additive log-reliability path coordinate                CLOSED
retry expected burden                                   CLOSED

semantic type/contract discovery                        OPEN
correlated failures                                     OPEN-BLOCKING
query-dependent reliability estimation                  OPEN-BLOCKING
protected multi-tool chain prediction                   OPEN-BLOCKING
```

---

# 10. Claim ceiling

These are exact independent-failure laws. Real tool ecosystems have shared dependencies, adversarial failures, changing APIs and query-dependent performance; those require measured joint reliability rather than multiplication by assumption.
