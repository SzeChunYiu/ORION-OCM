"""Statistics for the M1B missing-link-attribution assay (machinery only).

Frozen per M1B_MISSING_LINK_ATTRIBUTION_FREEZE_V1.json and the DEV-CAL-2 idiom set:
  recovery_i = (B_RESET - B_arm) / (B_RESET - B_KNOWN_STRUCTURE_ORACLE), paired at
  matched keys (target@budget); bootstrap CIs (frozen seed); sign-flip permutation
  null on the NULL anchor never on the recovering arm (DEV-CAL-1 construction);
  NULL_BAND_GATED direction tests (per-stratum sign-flip bands: determinate agreement
  or indeterminate silence -- two determinate disagreements are an assay defect);
  Holm family across the three attribution hypotheses; 20% registered margin.

Deterministic: every random construct uses the frozen seed 20260910.
"""
from __future__ import annotations

import random

MARGIN = 0.20                 # registered materiality margin (freeze)
FROZEN_SEED = 20260910        # matches the frozen DEV-CAL pattern
BOOT_N = 2000                 # bootstrap resamples
PERM_N = 2000                 # sign-flip permutations
CI_LO, CI_HI = 0.025, 0.975   # 95% interval

ATTRIBUTION_ORACLES = ("APPL_ORACLE", "RETR_ORACLE", "INTG_ORACLE")
KO_ARMS = ("APPL_KO", "RETR_KO", "INTG_KO")
_ALL_ARMS = ("RESET", "CONTINUED", "STRONG_ADAPTIVE_PARENT") + ATTRIBUTION_ORACLES + KO_ARMS + \
            ("KNOWN_STRUCTURE_ORACLE",)
CHANNEL = {"APPL_ORACLE": "APPL", "RETR_ORACLE": "RETR", "INTG_ORACLE": "INTG",
           "APPL_KO": "APPL", "RETR_KO": "RETR", "INTG_KO": "INTG"}


def _mean(xs):
    xs = list(xs)
    return (sum(xs) / len(xs)) if xs else None


def bootstrap_ci(values, stat=_mean, seed=FROZEN_SEED):
    """Percentile bootstrap CI of stat over values (frozen seed; deterministic)."""
    values = list(values)
    if not values:
        return None
    rng = random.Random(seed)
    n = len(values)
    stats = []
    for _ in range(BOOT_N):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        s = stat(sample)
        if s is not None:
            stats.append(s)
    if not stats:
        return None
    stats.sort()
    lo = stats[max(0, int(CI_LO * len(stats)) - 1)]
    hi = stats[min(len(stats) - 1, int(CI_HI * len(stats)))]
    return [lo, hi]


def signflip_p(diffs, seed=FROZEN_SEED):
    """Two-sided sign-flip permutation p-value for the mean of paired diffs."""
    diffs = [d for d in diffs if d is not None]
    if not diffs:
        return None
    obs = abs(_mean(diffs))
    rng = random.Random(seed)
    ge = 0
    for _ in range(PERM_N):
        d = [x if rng.random() < 0.5 else -x for x in diffs]
        if abs(_mean(d)) >= obs - 1e-12:
            ge += 1
    return ge / PERM_N


# ------------------------------------------------------------------ paired tables

def paired_vs_reset(keyed: dict, arm: str) -> dict:
    """Paired treatment effect of arm vs RESET at matched keys (target@budget)."""
    if arm == "RESET" or arm not in keyed or "RESET" not in keyed:
        return {"n_pairs": 0}
    a, r = keyed[arm], keyed["RESET"]
    keys = sorted(set(a) & set(r))
    diffs = [r[k] - a[k] for k in keys]  # positive = arm cheaper than RESET
    reds = [d / r[k] for k, d in zip(keys, diffs) if r[k] > 0]
    ci = bootstrap_ci(diffs)
    return {"n_pairs": len(keys), "mean_reduction": _mean(reds),
            "mean_diff": _mean(diffs), "ci_diff": ci,
            "ci_excludes_zero": bool(ci and ci[0] > 0),
            "p_signflip": signflip_p(diffs)}


def recovery_share(keyed: dict, arm: str, dev_slots: int = 0, n_targets: int = 1,
                   oracle: str = "KNOWN_STRUCTURE_ORACLE") -> dict:
    """PRIMARY endpoint: recovery_i = (B_RESET - B_arm)/(B_RESET - B_oracle) at matched
    keys; material iff mean >= MARGIN and bootstrap CI excludes 0.  With dev_slots
    charged, the arm's burden additionally carries its amortised dev enumeration
    (dev_slots / n_targets per target): the lifetime-charged reading."""
    if arm not in keyed or "RESET" not in keyed or oracle not in keyed:
        return {"n_pairs": 0, "material": False}
    a, r, o = keyed[arm], keyed["RESET"], keyed[oracle]
    keys = sorted(set(a) & set(r) & set(o))
    charge = (dev_slots / n_targets) if (dev_slots and n_targets) else 0.0
    shares, wins = [], []
    for k in keys:
        denom = r[k] - o[k]
        if denom <= 0:
            continue
        burden_arm = a[k] + charge
        shares.append((r[k] - burden_arm) / denom)
        wins.append(burden_arm < r[k])
    ci = bootstrap_ci(shares)
    material = bool(shares and _mean(shares) is not None and
                    _mean(shares) >= MARGIN and ci and ci[0] > 0)
    return {"n_pairs": len(shares), "mean": _mean(shares), "ci": ci,
            "ci_excludes_zero": bool(ci and ci[0] > 0),
            "dev_charge_per_target": charge, "material": material,
            "share_positive_pairs": sum(1 for s in shares if s > 0)}


# --------------------------------------------------------------- control checks

def ko_collapse_check(recovery: dict | None, vs_reset: dict | None) -> dict:
    """A KO arm must COLLAPSE toward RESET: material recovery in a KO arm means the
    knockout did not remove the capability (forced-fragment-style defect)."""
    material = bool(recovery and recovery.get("material"))
    return {"collapsed": not material, "recovery_mean": (recovery or {}).get("mean"),
            "alarm_non_collapse": material}


def forced_fragment_check(report: dict) -> dict:
    """FORCED_FRAGMENT_NEGATIVE: APPL_KO must serve NOTHING.  Any guided check,
    retrieval event, or non-empty served set in its rows is the planted defect
    firing (a fragment forced into the serving path)."""
    rows = report.get("acquisition_rows", [])
    guided = sum((r.get("search_behavior") or {}).get("guided_checked", 0) for r in rows)
    events = sum((r.get("search_behavior") or {}).get("retrieval_events", 0) for r in rows)
    served = (report.get("capability_state") or {}).get("fragments_served", 0)
    fired = bool(guided or events or served)
    return {"guided_checked": guided, "retrieval_events": events, "fragments_served": served,
            "alarm_forced_fragment": fired, "negative_confirmed": not fired}


def refusal_correctness_check(arms: dict) -> dict:
    """REFUSAL_CORRECTNESS: the learner's dev-time refusal is DATA, never tuned away.
    CONTINUED must either record the refusal AND show no guided serving, or serve a
    generator the dev phase actually admitted.  Refused-but-served (refusal silently
    overridden = fragment forced into the registered serving path) and not-refused-
    but-never-served are both assay defects."""
    continued = arms.get("CONTINUED")
    if continued is None:
        return {"refusal_recorded": None, "generator_served": None,
                "intact": True, "alarm_refusal_tuned_away": False,
                "note": "CONTINUED arm not present: check not applicable"}
    rows = continued.get("acquisition_rows", [])
    refusal = (continued.get("capability_state") or {}).get("refusal_reason")
    guided = sum((r.get("search_behavior") or {}).get("guided_checked", 0) for r in rows)
    served = bool(guided)
    intact = bool(refusal) != served  # refused XOR served -- never both, never neither
    return {"refusal_recorded": bool(refusal), "generator_served": served,
            "intact": intact, "alarm_refusal_tuned_away": not intact}


def direction_tests(keyed: dict, arm: str, strata: tuple = ("ladder",)) -> dict:
    """NULL_BAND_GATED direction tests: per-stratum (budget rung) sign-flip bands on
    the arm-vs-RESET paired diffs.  A stratum is DETERMINATE when its band excludes
    zero; determinate strata must AGREE in sign -- two determinate disagreements are
    an assay defect; all-indeterminate is NULL_EFFECT_INDETERMINATE (a legitimate,
    non-defective outcome: the null straddle)."""
    if arm == "RESET" or arm not in keyed or "RESET" not in keyed:
        return {"strata": {}, "verdict": "NO_DATA"}
    a, r = keyed[arm], keyed["RESET"]
    keys = sorted(set(a) & set(r))
    per: dict[str, dict] = {}
    for k in keys:
        rung = k.rsplit("@", 1)[-1]
        per.setdefault(rung, {"diffs": []})["diffs"].append(r[k] - a[k])
    strata_out, signs = {}, []
    for rung in sorted(per):
        diffs = per[rung]["diffs"]
        p = signflip_p(diffs)
        band = bootstrap_ci(diffs)
        determinate = bool(band and (band[0] > 0 or band[1] < 0))
        sign = 1 if (_mean(diffs) or 0) > 0 else (-1 if (_mean(diffs) or 0) < 0 else 0)
        if determinate and sign:
            signs.append(sign)
        strata_out[rung] = {"mean_diff": _mean(diffs), "ci": band, "p_signflip": p,
                            "determinate": determinate, "sign": sign or None}
    if len(signs) >= 2 and len(set(signs)) > 1:
        verdict = "DIRECTION_CONFLICT_ASSAY_DEFECT"
    elif not signs:
        verdict = "NULL_EFFECT_INDETERMINATE"
    else:
        verdict = f"DIRECTION_{'REDUCES' if signs[0] > 0 else 'INCREASES'}_BURDEN"
    return {"strata": strata_out, "verdict": verdict}


def holm(pvalues: dict) -> dict:
    """Holm step-down adjustment across a named family of p-values."""
    items = sorted(((p, name) for name, p in pvalues.items() if p is not None))
    m = len(items)
    out, running = {}, 0.0
    for i, (p, name) in enumerate(items):
        adj = (m - i) * p
        running = max(running, adj)
        out[name] = {"p": p, "p_holm": min(1.0, running), "reject": min(1.0, running) < 0.05}
    return out


def map_terminal(summary: dict) -> str:
    """Frozen M1B precedence:
    ASSAY_DEFECT > LEAKAGE_ALARM > INSUFFICIENT_HISTORY > LINK_ATTRIBUTED_{APPL|RETR|
    INTG|MULTIPLE|NONE} > AMORTISATION_DOMINATED > PARENT_EQUIVALENT > CANNOT_CHECK_*.
    """
    if summary.get("assay_defect"):
        return "ASSAY_DEFECT"
    if summary.get("leakage_alarm"):
        return "LEAKAGE_ALARM"
    if summary.get("insufficient_history"):
        return "INSUFFICIENT_HISTORY"
    if not summary.get("refusal_correctness", {}).get("intact", True):
        return "ASSAY_DEFECT"
    present = summary.get("arms_present", [])
    if len(present) < 10:
        return f"CANNOT_CHECK_MISSING_ARM_DATA({sorted(set(_ALL_ARMS) - set(present))})"
    if summary.get("censored_arms") or summary.get("censored_rows"):
        return (f"CANNOT_CHECK_CENSORED_ROWS({summary.get('censored_rows', 0)})"
                if not summary.get("censored_arms")
                else f"CANNOT_CHECK_CENSORED_ARMS({summary.get('censored_arms')})")
    recovery = summary.get("recovery_share_vs_known_structure_oracle", {})
    attributing = [arm for arm in ATTRIBUTION_ORACLES
                   if (recovery.get(arm) or {}).get("material")]
    if any(check.get("alarm_non_collapse") or check.get("alarm_forced_fragment")
           for check in list(summary.get("ko_collapse", {}).values()) +
               list(summary.get("forced_fragment_negative", {}).values())):
        return "ASSAY_DEFECT"  # a KO failed to collapse: the assay itself is broken
    conflicts = [arm for arm in ATTRIBUTION_ORACLES
                 if (summary.get("direction_tests", {}).get(arm) or {}).get("verdict")
                 == "DIRECTION_CONFLICT_ASSAY_DEFECT"]
    if conflicts:
        return "ASSAY_DEFECT"
    if not attributing:
        return "LINK_ATTRIBUTED_NONE"
    lifetime = summary.get("recovery_share_lifetime_charged", {})
    if not any((lifetime.get(arm) or {}).get("material") for arm in attributing):
        return "AMORTISATION_DOMINATED"
    parent_recovery = recovery.get("STRONG_ADAPTIVE_PARENT") or {}
    best = max(((recovery.get(a) or {}).get("mean") or 0.0) for a in attributing)
    if parent_recovery.get("material") and \
            (parent_recovery.get("mean") or 0.0) >= best - MARGIN:
        return "PARENT_EQUIVALENT"
    if len(attributing) > 1:
        return "LINK_ATTRIBUTED_MULTIPLE(" + "+".join(CHANNEL[a] for a in attributing) + ")"
    return "LINK_ATTRIBUTED_" + CHANNEL[attributing[0]]
    if len(attributing) > 1:
        return "LINK_ATTRIBUTED_MULTIPLE(" + "+".join(CHANNEL[a] for a in attributing) + ")"
    return "LINK_ATTRIBUTED_" + CHANNEL[attributing[0]]
