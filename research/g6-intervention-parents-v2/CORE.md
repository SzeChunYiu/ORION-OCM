# G6.1 remaining parent comparison v2

**Frozen v1:** `research/g6-intervention-lab-v1/` (`SELF_EVOLUTION_SUPPORTED_BOUNDED`).
That capsule is not retuned or overwritten.

**This successor** runs the remaining G6.1 *compare against* arms on the same
synthetic plant (imported, not copied):

| Bullet | This capsule |
|---|---|
| system-identification | GF(2) observation map `s = A f`, min-weight invert |
| structured surrogate | per-bit main-effect 2-factor ANOVA |
| ATMS/change-impact | learned DEPENDENCE graph + production `impact_cone` |
| evolutionary search | permutation GA on unlabeled training transcripts |
| program repair | GenProg-style mutate of replace-patches from traces |
| AutoML/BO | `CANNOT_CHECK_NO_BO_LIBRARY` — no package, none invented |
| learned selector | v1 OCM comparator, matched permissions |
| human-designed repair | not this capsule |

Claim ceiling: bounded synthetic plant; not production self-evolution.
No root-cause labels enter parent fit functions.
