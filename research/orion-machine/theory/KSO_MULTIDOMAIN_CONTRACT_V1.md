# KSO controlled multi-domain contract V1

Status: **integration theorem + executable controlled witness; scalability not established**.

## 1. Purpose

M3 and M6a already obey the same M0 warrant and typed-edge contracts, but before this artifact they
were instantiated in separately constructed test spaces. `kso_multidomain_v1.py` places both kinds
of learned structure into one `KnowledgeSpace`:

- a learned reusable procedure region;
- a Lean-kernel-verified formal-mathematics region;
- a neutral root that can navigate into both.

This is not yet the envisioned large open-world OCM. It is the first controlled witness that two
heterogeneous cognitive domains can inhabit one warranted graph without sharing a hidden global
truth flag or invalidating each other accidentally.

## 2. Construction

Let

\[
K_P=(V_P,H_P,\Lambda_P)
\]

be a procedure region and

\[
K_M=(V_M,H_M,\Lambda_M)
\]

be a formal-mathematics region. Require disjoint atom and edge identities except for an explicitly
registered joining root \(r\). The unified space is

\[
K = K_P \sqcup K_M \sqcup \{r\}
\]

plus neutral live `SUPPORT` edges

\[
r\to library_P,
\qquad
r\to library_M.
\]

The joins have profile `ONE`, so they add connectivity but no new evidential authority.

### Global evidence identities

The current M0 profile type is an integer evidence universe. Multi-domain integration therefore
must not reuse small local integers by accident. A registered evidence item is lifted to

\[
E(namespace,payload)=prefix_{60}(SHA256(namespace\parallel payload)).
\]

The implementation detects collisions among every evidence identity present in the registered
space. Cryptographic collision resistance is not treated as a mathematical theorem; collision
detection is the exact runtime guard.

Procedure lessons and Lean proof certificates use distinct namespaces.

## 3. Cross-domain non-interference theorem

Assume the procedure atom \(p\) has warrant support \(W_P\), the proof atom \(m\) has support
\(W_M\), and

\[
W_P\cap W_M=\varnothing.
\]

Then for every revocation \(R_P\subseteq W_P\),

\[
LIVE(m,R_P)=LIVE(m,\varnothing),
\]

and symmetrically for every \(R_M\subseteq W_M\),

\[
LIVE(p,R_M)=LIVE(p,\varnothing).
\]

**Proof.** M0 liveness is

\[
LIVE(x,R)\iff \exists W\in\Lambda(x): W\cap R=\varnothing.
\]

Every warrant of \(m\) contains only the math-domain evidence registered for that proof. Since
\(R_P\cap W_M=\varnothing\), each intersection used by the liveness predicate is unchanged. The
other direction is identical. QED.

The executable witness tests this in both directions on a learned AND procedure and one real
ME-X3 Lean proof certificate.

## 4. Navigation property

The root is structurally connected to both domain libraries and navigation uses positive typed
`SUPPORT` paths, so a restart walk seeded at `kso:root` has nonzero activation in both the learned
procedure region and the proof-certificate region.

This does **not** imply equal ranking, semantic comparability, or a learned domain router. It proves
only that the same navigation substrate can traverse both registered regions.

## 5. Controlled witness

`run_multidomain()` performs:

1. instantiate one KSO root with procedure library, math library and Lean kernel;
2. learn AND from an instruction and admit it as `proc:AND`;
3. ingest the frozen ME-X3 Lean receipt, admitting 20 kernel-verified proof certificates and
   excluding 20 registered corrupted proofs;
4. verify root reachability and positive activation into both regions;
5. revoke the procedure lesson and require the selected math proof to remain live;
6. reinstate the procedure, revoke the proof evidence, and require the procedure to remain
   executable;
7. record feedback in a fresh unified KSO and require that no procedure atom is created.

The executable terminal is intended to be

```text
CONTROLLED_MULTIDOMAIN_KSO_GREEN
```

only when every invariant above passes.

## 6. What this does not solve

A two-domain controlled union is not scalability. The following are still open:

- automatic routing among many learned domains;
- learned cross-domain relation discovery rather than fixed root/library bridges;
- collision-resistant/global provenance engineering at large scale;
- memory indexing and navigation complexity for millions/billions of atoms;
- consolidation without cross-domain semantic corruption;
- open-domain language atomization;
- genuine prospective frontier-math discovery.

The next major architecture question is therefore no longer whether heterogeneous objects can
share the same warrant graph—they can in this controlled construction—but whether a large KSO can
**learn its own useful cross-domain topology and routing policy** while retaining the same exact
warrant/revocation invariants.
