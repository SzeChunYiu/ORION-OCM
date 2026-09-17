# GMI #833 — Blind-Recovery Protocol v2 (closed task/basis channels, neutral battery)

v2 of the AJ9 blind-recovery protocol. The v1 no-smuggling contract closed only the
label/fingerprint channels; the audit on PRs #931-#934 found family morphology still enters
through (a) task authorship (K01's XOR choice and its basis embedding a threshold nonlinearity
under a neutral name; K03's requirement sentence writing the family transform into the task)
and (b) an under-specified adjudicator/screen. This package rebuilds the protocol so that every
input channel (task source, primitive basis, fingerprint clauses, cost model, adjudicator
thresholds) is frozen from a declared-in-advance neutral rule with a prior-disclosure manifest
and a per-channel blindness argument, then re-executes recovery per family. Contents (planned):
NEUTRAL_BATTERY_FREEZE_V1 (coverage-complete neutral generation rules), PRIOR_DISCLOSURE_V1,
adjudicator v2, A2 semantic-fingerprint screen binding, per-family recovery runs + revival chain.
