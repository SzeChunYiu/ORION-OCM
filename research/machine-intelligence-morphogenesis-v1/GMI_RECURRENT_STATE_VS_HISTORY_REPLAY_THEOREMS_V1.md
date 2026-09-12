# GMI Recurrent State versus History Replay Theorems v1

Status: **ZERO-PRIOR INTERFACE HARDENING / EXACT STREAMING BASE CASE**

Status date: 2026-09-12.

Purpose:

> Correct an overly strong reading of recurrent-state necessity. A finite recurrent state is necessary only relative to an interface that does not provide the full past for free. If full history is externally available, a stateless program can recompute many history-dependent functions; the scientific question becomes lifecycle burden and authority over history.

---

# 1. Streaming parity obligation

Inputs are bits

\[
x_1,x_2,\ldots,x_T.
\]

At every time `t`, protected output is prefix parity

\[
y_t=x_1\oplus\cdots\oplus x_t.
\]

---

# 2. One-bit recurrent realization

Maintain state

\[
s_t=s_{t-1}\oplus x_t,
\qquad s_0=0,
\]

and output `y_t=s_t`.

## Theorem RH-1 — exact recurrent burden

The realization uses one bit of persistent sufficient state and exactly one XOR update per input symbol, hence `T` update operations over horizon `T`.

This is the exact future-response quotient for the parity process under a current-input-plus-state interface.

---

# 3. Stateless replay realization with full prefix access

Suppose each output query at time `t` is legally given the entire prefix

\[
(x_1,\ldots,x_t).
\]

A stateless program can compute `y_t` by XORing the prefix from scratch.

## Theorem RH-2 — replay burden for output at every time

If one input inspection/XOR step costs one unit, computing every prefix output from scratch requires

\[
\sum_{t=1}^{T}t
=\frac{T(T+1)}2
\]

input visits up to constant endpoint conventions.

Thus recurrent update has linear total work `Theta(T)` while repeated full replay has quadratic total work `Theta(T^2)`.

### Consequence

Recurrent state is not a computability necessity when history is supplied externally. It is a lifecycle compression of repeated history access.

---

# 4. Final-query negative twin

Suppose parity is queried only once, after the entire length-`T` sequence is available.

A stateless one-pass program computes it in `Theta(T)` work with no persistent internal state.

The recurrent machine also performs `Theta(T)` updates and carries persistent state throughout the stream.

### GMI consequence

The recurrence advantage depends on:

```text
online query frequency
whether history is legally retained externally
history-read price/latency
persistent-state price
update price
retention/authority requirements
```

It should not be predicted solely from “the task depends on history.”

---

# 5. General replay-versus-state amortization

Let a sufficient recurrent state cost `C_state` to maintain over horizon and `c_u` per new event. Let a stateless replay computation over history length `t` cost `c_r t` each time it is queried. Let query times be

\[
Q\subseteq\{1,\ldots,T\}.
\]

Then

\[
C_{rec}=C_{state}+Tc_u
\]

and

\[
C_{replay}=c_r\sum_{t\in Q}t.
\]

## Theorem RH-3 — exact replay/state phase law

Recurrent materialization is lifecycle-cheaper iff

\[
C_{state}+Tc_u
<
c_r\sum_{t\in Q}t.
\]

This is the generic state-materialization/reuse law for history-dependent computation.

---

# 6. External memory as a third realization

A system may retain full history in external memory and maintain no compressed recurrent state. This can be optimal when:

```text
history writes are already required for provenance/rollback
queries are rare
different future queries need different summaries
state compression would discard future-relevant distinctions
```

Thus GMI should compare:

```text
compressed recurrent state
full external history
on-demand replay/search over history
hybrid compressed state + authoritative log
```

rather than treating RNN-like recurrence as the only form of memory.

---

# 7. Semantic-authority correction

If the protected obligation includes audit, rollback or provenance, the one-bit parity state is semantically insufficient even though it suffices for future parity outputs.

The target quotient changes with the obligation.

This is another reason that architecture derivation must begin with the declared semantic obligation, not benchmark input/output alone.

---

# 8. Impact on exact zero-prior rediscovery microscope

The predecessor result

```text
cumulative parity -> minimal 2-state Mealy machine
current bit       -> minimal 1-state machine
```

remains exact for the **streaming current-input + internal-state grammar**.

It must not be promoted to the stronger claim

> every parity-capable machine intrinsically requires persistent internal state.

A full-history program is a valid parent under a different information interface.

Therefore broad K4 rediscovery must register history access and its burden explicitly.

---

# 9. Gap update

```text
minimal state under current-input streaming interface      CLOSED
full-history stateless computability                       CLOSED
replay-vs-materialized-state lifecycle crossover           CLOSED
history-interface/cost measurement in real systems         OPEN
predictive-state estimator                                 OPEN
```

---

# 10. Claim ceiling

These are exact streaming/replay cost laws for a simple parity family. They sharpen, rather than weaken, the recurrent-state derivation: recurrence is predicted when a reusable sufficient summary is cheaper than repeated access to the full legally available history.
