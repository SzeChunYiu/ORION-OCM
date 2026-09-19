# FREEZE_V1 - gmi-833-ag2-signature-free-syntax-v1

## Claim ceiling

`AG2_G0_GRAMMAR_GENERATED_AS_FREE_TERM_ALGEBRA_OVER_AN_EXPLICIT_MANY_SORTED_SIGNATURE_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions: `SIGNATURE_IS_THE_BOTTOM`, `UNIQUE_SIGNATURE_FOR_G0`, `FREE_ALGEBRA_INVENTED_HERE`,
`BASIS_INDEPENDENT_OPERATION_THEORY_CLAIMED`, `SYNTACTIC_QUOTIENT_EQUALS_SEMANTIC_QUOTIENT`, `COMPLETE_GMI`.

## What this package is

An exact finite construction, at a registered bound, of

    Sigma_G0 = (Sorts, Ops, arity)      ->      G0 = FreeSyntax(Sigma_G0)

for the merged `gmi-833-g0-register-core-v1` instruction set, plus four separations each carrying an
exact finite witness:

1. operation **symbols** vs their **interpretations** (one signature, two interpretations, different semantics);
2. **formation** rules vs **transition**/reduction rules (a well-formed term with no successor);
3. **syntactic** equivalence vs **semantic** equivalence (strict refinement, exact class counts);
4. the registered G0 program set is exactly the well-sorted term set at the bound (bijection, exact count).

Universal algebra owns signatures, term algebras, free algebras, Birkhoff's theorems and equational
logic; Lawvere owns algebraic theories and presentation-independent operations. This package claims
no novelty in any of that and claims **no** basis-independent operation theory.

## Rows this package may reconcile

- comment `5693520829` / anchor `### AG2 — Signature before grammar`
  - `- [ ] Formalize `G = FreeSyntax(Sigma)` for the registered finite GMI setting.`
- comment `5693520829` / anchor `### AG2 — Signature before grammar`
  - `- [ ] Separate operation symbols from their interpretations.`
- comment `5693520829` / anchor `### AG2 — Signature before grammar`
  - `- [ ] Separate formation rules from transition/reduction/equational rules.`
- comment `5693520829` / anchor `### AG2 — Signature before grammar`
  - `- [ ] Separate syntax equivalence from semantic equivalence.`
- comment `5693520829` / anchor `### AG2 — Signature before grammar`
  - `- [ ] Reconstruct the existing `G0` grammar from an explicit lower signature rather than taking its syntax as primitive.`
- comment `5693520829` / anchor `### AG3 — Presentation is not theory`
  - `- [ ] Parent-subtract Lawvere theories/universal algebra before claiming a new “basis-independent operation theory.”`

## Rows this package may NOT reconcile

Every AG/AH row not listed above. In particular AG2 does **not** earn AG2 row
"Audit every `G0` instruction ... stochastic/local/channel/self-change extensions ..." (that row needs
the extension-lowering ledger, which this package does not build), nor any AG3 presentation-equivalence
row beyond the parent-subtraction row listed above.

## Frozen source

- `source_main` commit: `91c6d2876ba80c517a186e28fce3bdbe4e3fc218`
- Issue: SzeChunYiu/ORION-OCM#833
- Checklist comments in scope: `5693520829` (sections AG, AG0-AG13) and `5693590252` (sections AH, AH0-AH10).
- Row texts are pinned byte-exact in `research/gmi-833-agah-map-v1/AGAH_ROWS_V1.json` (75 open rows at freeze time: 55 in comment 5693520829, 20 in comment 5693590252).

## Order discipline

This freeze is committed **before** any executor, test, receipt or workflow of this package exists. `git log --follow` over this package must show this file in a commit strictly earlier than every implementation commit. An audit (#976) filed a POST_HOC_SUSPECT because a freeze postdated its result by 89 minutes; the ordering gate here is the direct remedy.

## No neighboring row is earned here.

Only the rows listed above may be reconciled by this package. Any other AG/AH row, any row in the #833 body sections A-M, and any row in comments Z / AA-AF / AI / AJ remain open and untouched by this tranche.
