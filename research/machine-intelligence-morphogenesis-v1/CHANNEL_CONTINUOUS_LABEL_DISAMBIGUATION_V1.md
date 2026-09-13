# Channel and continuous-lift labels

Date: 2026-09-13. Resolves the collision identified by
[issue #543](https://github.com/SzeChunYiu/ORION-OCM/issues/543) and
[PR #544 at 1ea21ceb](https://github.com/SzeChunYiu/ORION-OCM/pull/544/commits/1ea21cebc42cc51e05709dd3ffe88ae32753a988).

The established **CL-1–7** labels name the channel capability laws in
[the channel atlas](GMI_CHANNEL_CAPABILITY_ATLAS_V1.md).
The [continuous-lift theorem](../gmi-grand-unification-v1/CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md)
now uses **CLB-1–5** for its distinct clauses. Its five headings and one
internal cross-reference are renamed. Existing channel-law references retain
their meaning. Historical commits and receipt bytes remain preserved.

The current continuous-lift document is an input to the finite replay capsule,
so its reviewed SHA-256 binding changes even though the clause content and
checker output do not. The older assertion that no digest needs to move does
not apply to this source-bound capsule. No theorem has been added by relabelling.
