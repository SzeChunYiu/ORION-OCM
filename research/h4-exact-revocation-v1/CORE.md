# H4 exact revocation v1

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) H4 boxes,
planted method / cache / composition oracle.

**Terminal:** see [`RESULT.json`](RESULT.json) after the local run.

H3 at `research/h3-local-revision-v1/` remains the atom-liveness capsule
(`PARENT_SUFFICIENT_AT_PLANTED_KSO_SCOPE`). This directory does not overwrite
it. H4 is a different mechanism: derived-artifact exactness after source
removal, not merely LIVE/DEAD on atoms that stay in the space.

## Question

On a finite authored world, using production `ocm.kso` (no `src/` edits):

1. Does `prune` actually remove dead sources and their composition edges?
2. Is warrant invalidation evaluation against the revoked set, not label rewrite?
3. Do learned methods become unusable under the recorded reading?
4. Do snapshot indexes and per-query liveness memos refuse stale use?
5. Do conjunctive compositions reopen even when a sibling tail stays live?
6. Does alternate support keep the corresponding method, cache hits, and
   composition?
7. Does gated restoration return the pre-revocation artefacts, and does a
   pruned store require re-admission / re-composition (relearning)?

## World

- `src_skill` warranted by `ev:src`; `compose(src)→composed_from_src→composed_deep`.
- `alt_skill` warranted `{ev:src} ⊕ {ev:alt}`; `compose(alt)→composed_from_alt`.
- `unrel_skill` warranted by `ev:unrel`; `compose(unrel)→composed_from_unrel`.
- `composed_src_and_unrel` is `src ⊗ unrel` (KS-T20 meet), so it must die when
  `ev:src` is revoked even though `unrel_skill` stays live.
- Methods are `LearnedProcedure` objects, not KSO atoms: STATIC src, certified
  `Alt` src⊕alt, STATIC unrelated, TRACE `If` (even→src, odd→unrel).
- Caches: `ExtractionIndex` snapshot-bound to one `KnowledgeSpace`;
  `ExtractionRun` liveness memos do not cross queries; `cached_property`
  indexes do not survive `compose` / `prune` `replace`.

Revoke `ev:src`. Restore by emptying the revoked set on the original space.
Relearn by admitting `src_skill` back onto the pruned store and composing
again.

## Distinct from H3

| | H3 local revision | H4 exact revocation |
|---|---|---|
| Object | atom liveness / activation | methods, caches, composition receipts, pruned store |
| Dead dependents | remain in the space as DEAD | physically absent after `prune` |
| Restoration | empty revoked set | gated restore on original **and** re-admit on pruned store |
| Mutants | shallow `impact_cone` | stale liveness memo; `strip_all_warrants`; STATIC-for-TRACE; `compose` as ⊕ |

## Parents

Production KSO warrant algebra (ATMS labels, de Kleer 1986), KS-T22 reopening /
JTMS impact cone (Doyle 1979), prune/removal (KS-T04), procedure readings
(KAT, Kozen 1997), Petri enabling (Reisig), snapshot-bound indexes /
self-adjusting computation (Acar 2005). If the gates pass here, the mechanism
is `PARENT_SUFFICIENT` at this planted method/cache/composition scope — not an
OCM residual over TMS plus a skill library plus an index.

## Not claimed

Programme-wide H4 close. H3 overwrite or H3 programme-wide close. H5 lifetime
economics. Induced-graph P/R. Production adoption (already the incumbent
parent; this capsule does not switch anything).
