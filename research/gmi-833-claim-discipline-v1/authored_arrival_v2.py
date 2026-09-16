#!/usr/bin/env python3
"""Arrival absorbed under the frozen mechanical re-run rule (SUCCESSOR_TRANCHE_V2.md section 4).

gmi-833-blind-recovery-v2-v1 (PR #974, merged after the v1 scan base ed736cd3 and
before this tranche's ship): a claim-bearing results package (per-family RECOVERED /
NOT_RECOVERED_AT_SCOPE terminals). Its primary claim object enters the universe as
the ninth U-NEW arrival; every discipline field is EXTRACTED at file:line from the
package. The typed non-claim arrivals (this package's own v1 self-exclusion and
gmi-833-progress-ledger-v1, an audit/tracking object with NO PRIMARY THEOREM) are
enumerated in RESULT_V2.json arrivals, not silently dropped.
"""

ARRIVAL = {
    "result_id": "GMI833_CD_NEW_gmi-833-blind-recovery-v2-v1",
    "object_id": "BLIND_RECOVERY_V2_SEPARABILITY_RECOVERY_BOUNDARY_WITH_ALL_INPUT_CHANNELS_CLOSED_AT_REGISTERED_FINITE_SCOPE",
    "package": "gmi-833-blind-recovery-v2-v1",
    "tranche": "U-NEW",
    "fields": {
        "scope_quantifiers": {
            "status": "EXTRACTED",
            "content": [
                "gmi-833-blind-recovery-v2-v1/THEORY_V2.md:L5: 'Can a family-hidden search recover a known machine-intelligence family's morphology when EVERY input channel - including the two the audited v1 left open, task authorship and basis authorship - is closed by a declared neutral rule? And what does the recovery boundary look like across a complete neutral battery rather than one authored task?'",
                "gmi-833-blind-recovery-v2-v1/THEORY_V2.md:L20: 'v2 replaces the choice with a class: B_BOOL2 = ALL 16 two-input boolean functions ... B_DELAY = ALL lags ... B_LOCAL = ALL 256 elementary local rules; B_BOOL3 = ALL 256 three-input functions' (coverage-complete neutral battery; registered finite scopes)",
            ],
        },
        "assumptions": {
            "status": "EXTRACTED",
            "content": [
                "gmi-833-blind-recovery-v2-v1/PRIOR_DISCLOSURE_V1.md:L3: 'Frozen BEFORE any v2 search implementation, outcome, or adjudication. This manifest declares every input channel of the v2 protocol and states a blindness argument for each.'",
                "gmi-833-blind-recovery-v2-v1/PRIOR_DISCLOSURE_V1.md:L56: '## Channel manifest and blindness arguments' (task source, primitive basis, fingerprint clauses, cost model, adjudicator thresholds - each frozen from a declared-in-advance neutral rule)",
                "gmi-833-blind-recovery-v2-v1/NEUTRAL_BATTERY_FREEZE_V1.json:L3: B_BOOL2 battery class frozen (amended pre-outcome battery blob b7b358b55435ac0932e7e72318e189b59e10e5cf; no outcome or adjudication ever consumed the defective first battery - PRIOR_DISCLOSURE_V1.md:L9-L18 erratum, freeze custody asserted by check_v2.py:L53-L66)",
            ],
        },
        "falsifiers": {
            "status": "EXTRACTED",
            "content": [
                "gmi-833-blind-recovery-v2-v1/THEORY_V2.md:L35: 'Every linearly-separable function of two inputs (14 of 16) has a SINGLE-gate minimal construction and honestly FAILS the frozen K01 fingerprint - the protocol is not a rubber stamp' (a battery task of the honestly-failing separable class passing the frozen fingerprint would refute the measured boundary)",
                "gmi-833-blind-recovery-v2-v1/POSTHOC_RESULT_V2.json:L2: 'adjudication_started_after_blind_outcomes_frozen': true (any adjudication preceding the frozen blind outcomes would refute the blindness ordering)",
                "gmi-833-blind-recovery-v2-v1/POSTHOC_RESULT_V2.json:L31000: no_hardcoded_solution_selftest - battery_vector_literals_in_adjudicator must stay empty; any hardcoded expected solution/state encoding would refute the closed-channel claim",
            ],
        },
        "strongest_parents": {
            "status": "EXTRACTED",
            "content": [
                "gmi-833-blind-recovery-v2-v1/PARENT_LEDGER.md:L3: gmi-833-aj9a-known-family-benchmark-v1 (PR #931) - frozen benchmark + prospective no-smuggling contract; v2 keeps the frozen fingerprint clauses VERBATIM as the posthoc adjudication standard and closes the two channels that contract left open",
                "gmi-833-blind-recovery-v2-v1/PARENT_LEDGER.md:L6: gmi-833-aj9b..aj9g blind-recovery v1 series (PRs #932-#937) - the audited v1; v2 reproduces the OR-task counterfactual with the REAL v1 adjudicator (motivation receipt), generalizes it to the complete battery, and repairs the adjudicator defects",
                "gmi-833-blind-recovery-v2-v1/PARENT_LEDGER.md:L10: gmi-833-no-smuggling-audit-v1 (#855) - the A2 semantic fingerprint standard, wired in (screen_v2.py) rather than reimplemented as a lexical denylist alone",
            ],
        },
        "forbidden_extrapolations": {
            "status": "EXTRACTED",
            "content": [
                "gmi-833-blind-recovery-v2-v1/THEORY_V2.md:L139: 'DOES NOT PROVE: all-family recovery (K05-K08, K10, K11 out of scope; K09 untouched); learning/training extensions; PREDICTED_SELECTED (not claimed); that the order-test tier is the uniquely neutral basis (bounded by the U_ALL3 ablation where feasible); real-scale usefulness.'",
            ],
        },
    },
}
