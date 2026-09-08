# Issue #165 P0 / G4 exact-decision disposition

**Terminal for #71: `LEARNED_ROUTER_NOT_YET_AUTHORIZED`.**
No residual after the exact parents is large enough to unlock a learned router.
Unmerged PRs still own most G4 evidence, so the stronger closed terminal
`LEARNED_ROUTER_NOT_NEEDED` is not claimed.

This capsule maps every #165 P0 / G4.1–G4.4 checkbox and qualifies the one
named exact parent those PRs left implicit: linear cache-admission / ski-rental.
It does not modify PR154, PR158, PR161 or PR163 sources.

## Decision

- Do not train an ML router for current compose reordering.
  The unmerged R0 donor is `EXACT_POLICY_SUFFICIENT` (`rho_R = 0`).
- Preserve incumbent compose/check order until a lifecycle-equivalent early
  exit exists. PR154 rejects unrestricted first-PASS suffix elision.
- Adopt the linear cache-admission parent (Karlin ski rental / Lotker
  rent-vs-buy). On nonlinear lifetime curves, label the same parent `ADAPT`
  and keep PR154's exact one-way threshold.
- Leave #71 unauthorized. Oracle/legal-feature residuals reported in PR154
  are an upper bound, not a learner case.

Read [the checkbox map](CHECKLIST.json), [this run](RESULT.md),
[the linear parent](cache_admission_parent.py), and [cited PRs](REFERENCES.json).

No production change, native run, frozen 142-target replay or novelty claim.
