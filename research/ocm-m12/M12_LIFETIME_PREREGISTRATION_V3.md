# M12 pre-registration V3 — eight paired lifetimes on per-lifetime protected streams

Frozen before any V3 outcome is read. Design: `research/ocm-m12/M12_V3_PAIRED_LIFETIMES_DESIGN_V1.md`
(theory batch 6 F2; batch 7 G8 pending). Code: `src/ocm/lifetime/streams.py`,
`src/ocm/evaluation/m12_paired_eval.py`. This document's SHA-256 and the stream-manifest hash are
recorded in the evaluation receipt.

## Frozen items

| Item | Value |
|---|---|
| Unit of inference | the lifetime: one paired (OCM, whole-system parent) run on one protected stream |
| Lifetimes | 8, seeds `OCM-M12-V3|lifetime|k`, k = 0…7; ordering O(k mod 3)+1 of the V2 orderings |
| Stream manifest | `research/ocm-m12/M12_V3_STREAM_MANIFEST_V1.json`, SHA-256 `900959ec47e770b84f4b30df6646508bdc013f1d4e22d651a7be7c8c71e04b86` (per-stream hashes inside; leak check passed for all 8) |
| Streams | seeded substitution of the M7 V2 suites inside the bounded world (agents↔agents, objects↔objects, regular↔regular and irregular↔irregular verbs, verified facts↔verified facts of the same relation, out-of-scope↔out-of-scope, lesson words → nonce words absent from lexicon and manifest); expected patterns rewritten with the same maps; work task ids 500+20k…, withheld 700+3k…, science datasets 200+12k… |
| Arms | `ocm` (PersistentOCM, M11.2 build), `whole_system_parent`; the open-weight reference arm runs separately on the same language streams and is labelled REFERENCE (F8) |
| Per-lifetime score | success rate per V2 family + F_integrity (stale 0, reopened 3, intact 2) + G_self_repair + unknown_no_action |
| Primary test | exact two-sided sign test over the 8 lifetime differences per family, ties dropped, α = 0.05 |
| Secondary | exact paired test inside each lifetime, reported per lifetime, never pooled |
| Decision | OCM_LIFETIME_RESIDUAL_SUPPORTED iff ≥ 1 family rejects in OCM's favour, none in the parent's, kill gates 0; PARENT_SUFFICIENT iff no family rejects; MIXED otherwise; CANNOT_CHECK on any gate hit |
| Kill gates | V2 gates + ledger-chain identity (F5: the chain head recorded at each phase boundary must be present at its position later) + stream leak check |
| Replication | second host, deterministic block byte-equal |
| Stopping rule | one run; any code change after outcome access relabels this run DEV_CALIBRATION and requires V4 |

## What V3 can and cannot show

With 8 pairs the sign test rejects only when all 8 (or 7 of 8 with p = 0.07 — not enough) differences
have one sign: a family reaches OCM_LIFETIME_RESIDUAL only if OCM beats the parent in every lifetime.
Families where both arms are perfect in every lifetime are TIES_ONLY (no evidence either way).
