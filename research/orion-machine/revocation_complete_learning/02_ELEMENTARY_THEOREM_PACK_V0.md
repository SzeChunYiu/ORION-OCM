# Revocation-Complete Learning V0 — theorem pack

## 4. Elementary theorem pack

### RCL-0 — canonical-profile injectivity

For antichain profiles, equal revocation signatures imply equal profiles.

**Proof.** `f_mathcal J` is a monotone Boolean function. Its inclusion-minimal positive inputs are exactly the sets in `mathcal J`. The truth table, equivalently the revocation signature under complementation, therefore recovers the antichain uniquely. ∎

### RCL-1 — zero-query storage lower bound

For any finite profile class `Phi`, a deterministic zero-query exact summary needs at least

\[
\left\lceil\log_2 |\Phi/{\equiv_{rev}}|\right\rceil
\]

bits, where profiles are equivalent when their admitted revocation signatures agree.

**Proof.** Distinct equivalence classes must map to distinct summaries. Counting the summaries gives the bound. Storing the class index is sufficient. ∎

### RCL-1b — exponential counterfactual-warrant gap

Let `d=floor(n/2)`, let `M={J subseteq E: |J|=d}`, let `C_n=|M|`, and fix `J_0 in M`. Consider

\[
\Phi_n=\{\{J_0\}\cup S:S\subseteq M\setminus\{J_0\}\}.
\]

Every profile in `Phi_n` has the same current valid certificate `J_0`; nevertheless `Phi_n` has `2^(C_n-1)` distinct future signatures. Thus any zero-query exact post-revocation summary needs at least `C_n-1` bits.

**Proof.** Every profile is an antichain because all warrants have size `d`. There are `2^(C_n-1)` choices of `S`. RCL-0 makes their signatures distinct. For a more explicit witness, for each `J_i != J_0` choose `R_i=E\setminus J_i`. Since all warrants have equal size, `J subseteq J_i` iff `J=J_i`; hence `Live(R_i)=1` exactly when `J_i` is present. The `C_n-1` revocations therefore expose independent bits. ∎

**Interpretation.** Identical current behavior and identical valid proof do not bound future revision complexity.

### RCL-1c — exact storage–query frontier

In the coordinate-query model for `Phi_n`, where one charged query reveals whether a named alternative warrant `J_i` is present, any protocol that becomes complete for all admitted revocations satisfies

\[
S+Q\ge C_n-1,
\]

where `S` is retained summary bits and `Q` is worst-case binary queries. Equality is achievable at every integer split.

**Proof.** `Phi_n` contains `2^N` profiles with `N=C_n-1`. A summary has at most `2^S` values and a depth-`Q` binary decision tree has at most `2^Q` leaves, so exact identification needs `2^(S+Q) >= 2^N`. For achievability, store any `S` coordinate bits and query the other `N-S`. ∎

### RCL-1d — direct sum across reusable skills

For `m` independently warranted skills, each drawn from `Phi_n` and sharing the same current proof form, the joint RSD and exact storage–query lower bound are `m(C_n-1)`.

**Proof.** Use the disjoint union of the per-skill revocation coordinates. Every joint bit vector is realized by the Cartesian product of profiles. The counting proof for RCL-1c is additive. ∎

### RCL-2 — positive-witness omission theorem

Let `W` be a proper subset of a nonempty antichain `mathcal J`. Some revocation kills every emitted witness in `W` while preserving an omitted warrant.

**Proof.** Choose omitted `K in mathcal J\setminus W`. For every `J in W`, antichainness gives an atom `x_J in J\setminus K`. Let `R={x_J:J in W}`. Then `R cap K` is empty, while `R cap J` is nonempty for every emitted witness. ∎

### RCL-2a — bounded positive witnesses remain incomplete

For every `k`, there is a profile with `k+1` pairwise incomparable warrants for which any positive-only transcript exposing only `k` of them admits the RCL-2 distinguishing revocation.

A concrete family uses disjoint pairs `J_i={a_i,b_i}`. Revoke one atom from each exposed pair and none from the omitted pair.

### RCL-2b — single-proof over-retraction

With warrants `{a,b}` and `{c,d}`, expose only `{a,b}`. Revoking `a` invalidates the displayed proof but the skill remains live through `{c,d}`. A system that equates “proof failed” with “skill dead” commits collateral skill loss.

### RCL-3 — one-warrant exact information

If the profile contains exactly one unknown `d`-subset of an `n`-atom universe, zero-query exact arbitrary revocation requires and suffices with

\[
\lceil\log_2 {n\choose d}\rceil
\]

bits.

**Proof.** There are `C(n,d)` distinct signatures by RCL-0. A combinatorial rank/unrank code achieves the ceiling. ∎

### RCL-4 — full-antichain sufficiency

The complete minimal-warrant antichain decides every revocation by scanning whether any warrant is disjoint from the revoked set. This is standard provenance/truth-maintenance territory, not a novelty claim.

### RCL-5 — false-retain / false-retract / abstain trilemma

Any deterministic summary that is not revocation-complete has two compatible profiles and a revocation requiring opposite decisions. It must falsely retain on one, falsely retract on the other, or abstain on a decidable case.

### RCL-6 — semantic-learning/revision separation

There are classes in which the reusable operator semantics and one valid local proof are identical across every training transcript, while the post-revocation library state ranges over `2^(C_n-1)` possibilities per skill.

**Proof.** Attach one fixed operator transition table to every profile in `Phi_n`; vary only its hidden alternative warrants. Static semantic identification is unchanged, while RCL-1b and RCL-1d give the revision family. ∎

This theorem formalizes the intended split: learning what an operator does and learning when it remains warranted are different information problems.

## 5. Exact oracle

`revocation_complete_oracle.py` independently checks liveness two ways, enumerates every antichain on four atoms, verifies signature injectivity, checks every proper positive-witness subtranscript, realizes the RCL-1b shattering coordinates through `n=5`, checks every storage/query split in that finite family, checks the direct-sum construction, rank/unrank round trips, and both positive and no-alarm controls.

Finite enumeration is a sanity and counterexample instrument. The all-size authority for RCL-0–RCL-6 is the hand proof above; mechanization remains open.

