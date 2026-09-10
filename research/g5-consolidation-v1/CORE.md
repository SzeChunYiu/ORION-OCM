# G5.4 cognitive consolidation v1

**Status:** prospectively frozen after useful learned schemas exist (#192 G2.4, #193 G3.1).  
**Owners:** #165 G5.4, #70, #62.  
**Claim ceiling:** bounded epistemically safe compression of explicit polynomial traces.

## Why this study is allowed now

G5.4 is locked until useful learned schemas exist. That lock is discharged at the
registered polynomial scope by:

```text
G2: square → dec → square
G3: square → inc → inc
    square → dec → dec
```

Those fragments are reused here **as schemas**, not as confirmatory test
outcomes. This capsule does not replay G2/G3 length-6/7/8 identities.

## Fresh population (do not reuse G2/G3 salts)

Training experiences are explicit program traces:

- primitive lengths **exactly 4 and 5** (disjoint from G2/G3 min-length 6/7/8);
- train salt `orion-ocm-g5-consolidation-train-v1`;
- held-out salt `orion-ocm-g5-consolidation-heldout-v1`;
- **40** training traces: 9 SDS + 8 SII + 8 SDD + 9 exceptions, then 6 duplicate
  episodes of already-chosen schema programs;
- **12** held-out traces: 4 per schema, excluding training programs and
  coefficient fingerprints.

N is small so CI stays under 10 minutes.

## Consolidation rule

```text
detailed experience
→ recurring pattern
→ scoped schema
→ residual exceptions
→ archive redundant detail
```

Schema+residual live state stores:

- the three scoped schemas with supporting episode lists;
- per-episode **residual identity** and residual context (prefix / suffix /
  occurrence), not only a schema id;
- full exception traces that no schema covers.

Redundant primitive expansions of schema-covered traces go to an **archive**.
Archive bytes are added into `total_bytes`. Archive is not serving authority.

## Required safety properties

| Property | Operationalization |
|---|---|
| Current task behavior | Every training episode reconstructs the original program and polynomial. |
| Future revision distinctions | Two currently co-schematic traces keep distinct residual identities and recoverable `(first, last, episode)` split keys. |
| Exceptions addressable | Non-schema episodes are keyed by `episode_id` in the live store. |
| Provenance recoverable | Live schemas list supporting episodes; archive restores schema-covered originals. |
| Archive bytes charged | `archive_bytes > 0` and `total_bytes = live_bytes + archive_bytes`. |
| Consolidation compute charged | Hash/match ops and process-time over all five parents. |
| Held-out capability | Schema tokens solve unseen wrappers after consolidation. |
| Revocation exact | Revoke all SDS-supporting episodes. SDS becomes non-live. SII, SDD, and exceptions remain. Held-out SDS answers are recomputed without SDS; not cached schema expansions. |

## Parents

1. **keep all traces** — verbatim episode list.
2. **simple fingerprint dedup** — one survivor per polynomial fingerprint; duplicate episodes are dropped.
3. **structural sharing** — prefix trie with episode ids at leaves.
4. **library-learn fragments** — support≥2 fragments of length 2–3, cap 8, greedy cover, fragments also served as search tokens.
5. **schema+residual** — the G2/G3 macros plus residual identities plus exceptions plus charged archive.

## Decisive comparison

Schema+residual must beat **structural sharing** on the joint criterion

```text
held-out method-use count
AND
exact SDS-support revocation
```

If it does not, the terminal is `PARENT_SUFFICIENT`. Do not weaken revocation
to manufacture a win. Structural sharing is allowed to keep duplicate episode
ids at trie leaves; it is not given schema tokens.

## Terminals

```text
EPISTEMICALLY_SAFE_COMPRESSION_SUPPORTED
STRUCTURAL_COMPRESSION_ONLY
CONSOLIDATION_COST_DOMINATES
REVOCATION_NOT_PRESERVED
PARENT_SUFFICIENT
CANNOT_CHECK_<reason>
```

Positive `EPISTEMICALLY_SAFE_COMPRESSION_SUPPORTED` is a bounded safety+held-out
result in this polynomial ecology. It is not an OCM architecture residual over
ordinary schema+residual memory, and not a whole-lifetime byte-win: archive is
charged, so live+archive may exceed keep-all.

## Result

**Terminal:** `EPISTEMICALLY_SAFE_COMPRESSION_SUPPORTED`

Machine receipt: [RESULT.json](RESULT.json).

Schema+residual used a schema on all **12/12** held-out traces (**12** strict
search-rank wins vs primitive). Structural sharing used **0** methods and stored
**0** held-out identities. SDS-support revocation was exact: SDS died, SII and
SDD remained in use, exceptions stayed addressable, and SDS was not reused from
cache. Ordinary persistent schemas tied OCM live search (1503 attempts);
primitive held-out search was 11679; post-SDS-revoke search was 5013.

Live+archive bytes (21154) exceed keep-all (12476) because archive is charged.
Structural sharing remains the smaller encoding (3726). The residual is
held-out schema capability plus exact revocation, not a total-byte win.

## Freeze rule

After the first result, do not change salts, counts, schema identities, token
order, residual-identity rule, parent constructions, or the structural-sharing
comparison to rescue v1.
