# WHAT_IS_ACTUALLY_NEW — template v1 (issue #833, section AC)

Surviving-literature table template. Every flagship claim is logged here before it may be asserted as
new. The template is executed by the parent-literature check protocol in
`EXPERT_LITERATURE_LANES_V1.md`: a new claim must pass all 11 lanes, name its strongest parent, and be
typed into exactly one contribution kind.

Claim kinds (AC box: "Record whether GMI contribution is theorem, synthesis, generalization, new
selection law, new empirical result, or only terminology"):

- theorem — a statement proved from explicit premises (state the proof apparatus)
- synthesis — unification of existing results under one construction
- generalization — extends a parent result to a wider class (state the parent)
- new selection law — a covarying relationship under which one option beats others in a defined
  regime (state the resource/ecology conditions)
- new empirical result — a reproducible measurement not previously recorded
- terminology — a naming/reorganization contribution only (no new result; must cite the operand
  terms' canonical definitions)

Fill one row per claim. A claim survives as *actually new* only if at least one difference cell is
non-empty after all 11 lanes have searched.

## Template

| claim (exact statement) | parent literature (earliest/strongest per idea) | difference (what the parent does NOT already assert / predict) | kind (theorem / synthesis / generalization / new selection law / new empirical / terminology) | evidence status (which maturity/evidence level; E0–E6 or M0–M6) | falsifier | remaining gap (AA ledger ref) |

## Worked example

| claim | parent literature | difference | kind | evidence | falsifier | remaining gap |
|---|---|---|---|---|---|---|
| (unknown-form selection law, P3-candidate) | Rice 1976 algorithm selection; Wolpert–Macready 1997 NFL | Rice selects among labeled algorithm portfolio with feature vectors; NFL rules out uniform optimality. GMI claims prediction of *unseen* candidate families from ecology descriptors plus resource crossover | new selection law (candidate) | M2 exact witness on synthetic ecologies; M3 not yet | an ecology from the task-distribution generator where the predicted winner loses to uniform random baseline under honest fills | AA-gap id tbd |

## Use rules

1. Type first, then claim. A claim with no kind is not assertable.
2. Parent-first: name the strongest parent before writing the difference cell.
3. Difference honesty: an empty difference cell means the row is `terminology` at most.
4. Terminology rows must cite the canonical definitions of the terms they rename.
5. New-empirical rows must state the measurement protocol and its reproducibility.
6. Re-run all lanes at manuscript freeze (AC box on re-running literature search).
