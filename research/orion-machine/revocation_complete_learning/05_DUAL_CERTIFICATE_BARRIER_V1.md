# Dual-Certificate Barrier for Revocation-Complete Learning V1

**Date:** 2026-09-03  
**Status:** `HAND_PROVED_CONDITIONAL_NO_GO_THEOREM__MECHANIZATION_OPEN__NOVELTY_NOT_CLAIMED`

## 1. Warrant relation

Let `x` encode a learned skill, execution obligation, checker/version state, authority state, and evidence state. Let `r` encode a later admitted intervention or revocation. Let `w` be a candidate surviving warrant. Assume a polynomial-time decidable relation

\[
V(x,r,w)\in\{0,1\}
\]

with polynomially bounded witnesses.

Define

\[
LIVE=\{(x,r):\exists w\;V(x,r,w)=1\}
\]

and

\[
DEAD=\{(x,r):\forall w\;V(x,r,w)=0\}=\overline{LIVE}.
\]

A surviving warrant `w` is an independently checkable **retention certificate**.

An **extinction certificate system** is a polynomial-time relation `D(x,r,c)` with polynomially bounded certificates such that

\[
(x,r)\in DEAD \Longleftrightarrow \exists c\;D(x,r,c)=1.
\]

## 2. RCL-7 — dual-certificate barrier

### Theorem

If `LIVE` is NP-complete and a polynomially bounded, polynomial-time checkable extinction certificate system exists for every `DEAD` instance, then `NP = coNP`.

### Proof

`LIVE` is in NP by the warrant relation. Since it is NP-complete, `DEAD` is coNP-complete. The assumed extinction certificate system places `DEAD` in NP. Therefore a coNP-complete language lies in NP, so `coNP` is contained in `NP`. Taking complements gives `NP` contained in `coNP`; hence `NP = coNP`. ∎

### Non-consequence

The theorem does not prove `NP != coNP`. It proves that a universal RCL design may not assume efficient noninteractive certificates for both survival and extinction over arbitrary NP witness systems without accepting a major complexity collapse or changing the verification model.

## 3. RCL-7a — asymmetric proof obligation

For general polynomial witness relations:

- `RETAIN` is existential and has a direct positive witness;
- `RETRACT` is a no-surviving-warrant assertion and is complementary;
- failure of one displayed proof is not an extinction certificate;
- a safe system must obtain a complete compiled representation, run a potentially hard search/proof, use a stronger interactive/probabilistic proof system with its own assumptions and costs, restrict the warrant language, or abstain.

This formalizes why current proof soundness and future retraction authority are different certification problems.

## 4. RCL-8 — knowledge-compilation escape and cost transfer

Suppose a warrant formula is compiled offline into a representation supporting conditioning on `r` and deciding satisfiability in polynomial time. Then `LIVE` and `DEAD` can both be decided online in polynomial time by testing whether the conditioned representation has a model.

This moves work into:

- compilation time;
- compiled representation size;
- certificate/checker size and trust;
- recompilation or repair after changes to the warrant semantics themselves.

Knowledge-compilation lower bounds show that this compiled state can be exponential on unrestricted natural classes, while bounded-width classes admit constructive singly-exponential compilation in the width. Thus the escape is a resource trade, not a universal free certificate.

## 5. RCL-9 — exact two-sided revision trilemma

For general NP-complete warrant-existence families, an exact revocation-complete learner cannot assume all three without a qualifying theorem:

1. compact polynomial retained/compiled warrant state;
2. polynomial-time independently checkable noninteractive certificates for both retain and retract on every intervention;
3. no expensive online reproof, interaction, privileged oracle, or abstention.

A valid architecture must state which coordinate is relaxed and why:

- **restricted class:** bounded treewidth, decomposable circuits, Horn/2-CNF, or another tractable warrant language;
- **large offline state:** compile enough of the warrant space;
- **online proof/search:** pay after the intervention;
- **interactive/probabilistic certification:** charge soundness, communication, repetition, and trust assumptions;
- **abstention/escalation:** preserve `CANNOT_CHECK` rather than fabricate retraction authority.

## 6. Strongest-parent boundary

The theorem is built from standard NP/coNP reasoning and established knowledge-compilation trade-offs. No novelty is claimed for the complexity implication itself.

The candidate scientific residual is a theorem that couples this barrier to learning:

> characterize when independently checked execution traces let a learner acquire a compact warrant representation for reusable operators, and prove the complete offline-acquisition / compiled-state / online-proof / recourse / collateral-loss / false-authority / abstention frontier under future semantic and authority changes.

That stronger theorem must compare against complete reasons, exact monotone-DNF learning, knowledge compilation, provenance-guided rule-shift repair, exact unlearning, truth maintenance, proof-carrying execution, and the recurrent-Transformer implementation.

## 7. Mechanization target

Encode:

- finite witness relation and intervention;
- `LIVE` and `DEAD` complementarity;
- certificate-system implication `DEAD in NP`;
- the reduction premise that `LIVE` is NP-complete;
- the class-collapse conclusion as a conditional theorem;
- finite SAT/CNF examples separating survival witnesses from extinction checks.

No Boolean checker proved only by reflexivity will count as a proof of the complexity statement.
