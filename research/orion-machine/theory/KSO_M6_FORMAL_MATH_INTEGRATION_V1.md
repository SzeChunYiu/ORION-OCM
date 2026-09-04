# KSO M6a — real formal-mathematics verifier integration V1

Status: **formal proof channel integrated; full frontier-math milestone remains open**.  
Parent: #284. Upstream protected study: ME-X3.

## 1. Why this is a real step beyond the Boolean M4/M5 calibration

The repository already contains a completed protected formal-mathematics campaign, ME-X3. It is
not a simulated result and is not rerun here.

ME-X3 executed 540 protected instances. On the registered joint endpoint the
Machine-Epistemics arm and the strongest faithful parent federation tied exactly:

```text
M  = 0.944
B5 = 0.944
paired discordance = 0 / 540
route = PARENT_SUFFICIENT
```

Therefore this integration **cannot** be used to claim a formal-math control advantage. The
scientific terminal stays `PARENT_SUFFICIENT`.

Separately, ME-X3 produced a protected Lean-kernel proof receipt over 40 proof-control files:

```text
20 expected-valid proof files -> VERIFIED_BY_LEAN_KERNEL
20 deliberately corrupted files -> REJECTED_FOR_THE_REGISTERED_REASON
CANNOT_CHECK = 0
Lean/oracle disagreements = 0
Lean 4.33.1, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6
```

The positive files are explicit `Derives` proof terms. The negative files corrupt a registered
proof step and count as a successful negative control only when Lean rejects them for the expected
`Derives` type mismatch. Parser failure, timeout, missing Lean, or another unrelated error is
`CANNOT_CHECK`, never a rejection success.

This gives KSO a genuine exact mathematical checker channel rather than a hand-labelled Boolean
oracle.

## 2. KSO integration rule

For a proof-certificate row `r`, define the evidence identity

\[
e(r)=H(\text{Lean commit},\text{Lean version},\text{task id},\text{proof file},\text{verdict}).
\]

The proof file is part of identity deliberately. ME-X3 has a good and corrupted proof for the same
theorem task; theorem identity alone cannot show that the corrupted certificate was excluded.

A certificate is eligible for KSO admission iff

\[
\operatorname{expect}(r)=ACCEPT
\land
\operatorname{verdict}(r)=VERIFIED\_BY\_LEAN\_KERNEL,
\]

and the enclosing receipt satisfies

\[
CANNOT\_CHECK=0,
\quad
DISAGREEMENTS=0,
\quad
AGREES\_WITH\_EXHAUSTIVE\_ORACLE=true.
\]

Each eligible proof becomes a connected KSO atom

\[
p_r=(\text{verified-proof-certificate},\ \Lambda_r=\{\{e(r)\}\}),
\]

with a typed `SUPPORT` edge from the registered Lean-kernel atom. Admission uses the already-frozen
M0 `CertificateKind.EXACT_CHECKER` path. No second proof-admission semantics is introduced.

A corrupted proof row never receives an atom. A receipt containing any unclassified row,
`CANNOT_CHECK`, count drift, or Lean/oracle disagreement blocks the integration.

## 3. Lifecycle theorem

For admitted proof atom `p_r`, let `R` be a revocation set.

By the M0 warrant law,

\[
LIVE(p_r,R) \iff e(r)\notin R.
\]

Therefore revoking the exact proof evidence makes its certified KSO path vanish without
renormalising that mass onto another proof path. The implementation checks both:

1. the proof atom is live before revocation and dead afterwards;
2. the navigation share `Lean kernel -> proof atom` is positive before revocation and exactly zero
   afterwards.

The frozen result checks this on the first protected accepted certificate
`ok_F1_0007_1cd7ba.lean`.

## 4. Hostile controls

The integration has four required negative controls.

1. **CANNOT_CHECK mutation** — changing the upstream receipt to `cannot_check=1` prevents
   admission.
2. **Oracle-disagreement mutation** — changing `disagreements=1` / agreement false prevents
   admission.
3. **Corrupted-proof promotion mutation** — relabelling an expected-reject row as
   `VERIFIED_BY_LEAN_KERNEL` is rejected because expectation and verdict no longer form a valid
   registered row.
4. **Receipt-size mutation** — deleting a row while leaving `n=40` is `CANNOT_CHECK`.

A positive-only test suite would be scientifically useless here: the 20 bad proof files are what
show that the Lean boundary can actually refuse invalid evidence.

## 5. Result

```text
M6A_FORMAL_MATH_VERIFIER_CHANNEL_INTEGRATED_PARENT_SUFFICIENT
Lean receipt rows                 = 40
kernel-verified certificates      = 20
registered corrupted rejections   = 20
KSO warranted proof atoms          = 20
rejected proof atoms               = 0
CANNOT_CHECK                       = 0
Lean/oracle disagreements          = 0
upstream ME-X3 terminal            = PARENT_SUFFICIENT
```

This is the first KSO milestone in this branch grounded in a real proof kernel rather than only an
exact finite Boolean checker.

## 6. What is still missing before `M6_FRONTIER_MATH` may be green

The following remains explicitly **not established**:

- selecting and freezing a genuinely open/nontrivial formal target before outcome access;
- populating KSO with relevant mathematics without importing a target solution;
- witnessing an actual search/representation obstruction on that target;
- prospectively choosing a minimum sufficient Jump;
- producing a new proof/counterexample through the KSO loop;
- having the proof assistant validate that newly produced artifact;
- comparing against the strongest current theorem-search / retrieval / lemma-generation parent at
  matched information and compute;
- independent replay of the whole discovery trace.

Accordingly:

```text
M6A_FORMAL_VERIFIER_CHANNEL = INTEGRATED
M6_FULL_FRONTIER_MATH       = NOT_RUN
OPEN_FRONTIER_PROBLEM_SOLVED = FALSE
FRONTIER_MATH_DISCOVERY      = NOT_ESTABLISHED
NOVELTY                      = NOT_ESTABLISHED
```

This separation is deliberate. A proof checker is a necessary part of the frontier-math loop, but
having a proof checker does not mean the machine has discovered new frontier mathematics.
