# H3 local revision v1

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) H3 boxes, planted
KSO oracle only.

**Terminal:** see [`RESULT.json`](RESULT.json) after the local run.

## Question

On a finite authored support world, using production
`ocm.kso.warrant` / `ocm.kso.revocation` (no `src/` edits):

1. Do true dependents reopen?
2. Does unrelated competence remain?
3. Does alternate support preserve valid competence?
4. Does restoration return exactly the pre-revocation justified state?
5. Can dependency precision/recall be measured?

## World

- `source` warranted by `ev:src`; `compose(source)→mid→deep` (true dependents).
- `dual` is a structural dependent of `source` with warrant `{ev:src} ⊕ {ev:alt}`.
- `alt` / `alt_answer` carry the same join, off the source chain.
- `unrelated` / `unrelated_answer` warranted only by `ev:unrel`.

Revoke `ev:src`. Restore by emptying the revoked set.

## Precision / recall

Measured against **authored oracle labels**, not by comparing `impact_cone` to
itself:

- predicted structural dependents = `impact_cone({source})`
- truth = `{source, mid, deep, dual}`
- predicted reopen = KS-T22 `reopen`
- truth reopen = `{source, mid, deep}` (atoms that must lose LIVE)

A planted shallow-cone mutant (`mutant_impact_cone_direct_only`) must miss
`deep`, so the metric is not inert.

**Induced or unknown support graphs:**
`CANNOT_CHECK_NO_INDEPENDENT_INDUCED_ORACLE`. There is no independent observed
dependency oracle outside this planted world.

## Parents

Production KSO warrant algebra (ATMS labels, de Kleer 1986) and KS-T22
reopening / JTMS impact cone (Doyle 1979). If the gates pass here, the
mechanism is `PARENT_SUFFICIENT` at this scope — not an OCM residual over TMS.

## Not claimed

Programme-wide H3 close. H4 exact revocation. H5 lifetime economics. M11/M12
scientific inheritance. Induced-graph P/R. Production adoption (already the
incumbent parent; this capsule does not switch anything).
