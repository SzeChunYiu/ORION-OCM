# Donor-mapping review receipt

Date: 2026-09-08. **Outcome: corrected mapping supported within its stated scope.**

Reviewed successor: `OCM-METAREASONING-DONORS.md`, SHA256
`8befee0e7e2ec65b0fc509899f0d8ed96e89c090ce668e836d1e56665c4d6aed`.
Original retained as `OCM-METAREASONING-DONORS-01.md`, SHA256
`4b2300bdf6e3551a6f914bfaccce8eee1fa09becbf6dd392751ae0500524e65b`.

## Hay et al.

Independent read: definitions 1/3, theorems 4/5, example 3 (PDF pages 2–4),
and section 6.2 (page 8). The mapping's bounded-utility/positive-cost conditions
and expected-count distinction are supported. More precisely, bounded utilities
are assumed after Definition 1; Definition 3 fixes `c>0`.
Theorem 5 also gives almost-sure stopping, while Example 3 allows arbitrarily
long computation sequences. Section 6.2 identifies future reuse value but leaves
its full valuation as an extension. The mapping does not misrepresent that as a
proved optimal reusable-state controller.
[Primary source, 2012 v1](https://arxiv.org/pdf/1207.5879v1).

## Bertsekas

Two corrections requested on the original mapping are now present at successor
lines 27–30 and 40–43: the complete properness definition and explicit reliance
on the corrected revision. Readback verified both.

Independent read: introduction, Eq. (7), propositions 2/7 and their stated
conditions, Example 1, conclusion; v1 proposition 7 for version comparison.
Proposition 7 additionally needs bounded stage costs and a uniformly proper
policy; the successor correctly preserves its other conditions rather than
claiming Eq. (16) alone suffices.
[Corrected primary source, 2020 v2](https://arxiv.org/pdf/1711.10129v2);
[version history](https://arxiv.org/abs/1711.10129v2).

## Lotker et al.

Independent read: title/version, introduction, sections 2–3 including the
decomposition and combination proofs; section 4 opening only.
The May 3, 2010 expanded manuscript identifies the STACS 2008 antecedent.
The stated setup-difference and constant-rate model is accurate. The conditional
OCM mapping appropriately withholds a transferred competitive guarantee.

For a later implementation, preserve forward-only investment and the ordered
break-even times used in section 3, rather than treating an arbitrary frontier
graph as the same model. Its performance comparison is expected algorithm cost
against the offline optimum for each fixed duration. This is follow-up
specification, not an additional required correction to the current mapping.
[Author-hosted primary source](https://www.eng.biu.ac.il/~rawitzd/Papers/ski.pdf).

## Scope

No further correction is required for the three reviewed donor entries.
The Russell–Wefald background sentence was outside this requested re-review.
This receipt qualifies the correspondence between stated claims and inspected
source sections; it is not a full theorem-proof audit, empirical reproduction,
or OCM transfer theorem. No studies, learners, verifiers, or tests were run.

[Changed-PR boundary](THEORY-HEAD-BOUNDARY-ADDENDUM.md).
