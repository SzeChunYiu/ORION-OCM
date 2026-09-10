"""Evolvability (FO-V1 objective 4) — measurable and falsifiable.

Definition, frozen before any scored run:

    E(x) = [ cap_FOF1(x after k governed steps) - cap_FOF1(x) ] / B_steps(x)

  * FOF1 is the PROSPECTIVELY FROZEN future family minted in
    oracle/future_family.py.  It is not T3 and T3 is never read.
  * k = K_STEPS = 3 governed steps.
  * A GOVERNED step proposes at most P_MAX = 8 mutations and accepts the FIRST
    proposal that: compiles legally; passes every frozen hard gate at T0; and
    does not regress current-family capability by more than TAU = 0.0 (that is,
    no regression at all).  Governance is a gate, not a preference: an
    unaccepted proposal is still charged.
  * B_steps is the charged work of EVERY proposal made during the k steps,
    accepted or not, plus the charged work of the acceptance evaluations.  A
    step that accepts nothing is a no-op and still costs.
  * MATCHED CURRENT CAPABILITY is enforced by stratification, not regression:
    CAP_BINS partitions T2 capability into fixed-width bins and evolvability is
    only ever compared WITHIN a bin.  Bin edges are frozen here.

Falsifiers, frozen with the estimator:
  F1  E is not distinguishable from its shuffle-equal-n null within bins
      -> evolvability carries no signal; report as such, do not rescue.
  F2  E ranks forms identically to capability alone (Spearman >= 0.95 within
      bins) -> the objective is redundant and must be reported as redundant.
  F3  B_steps == 0 for a form -> E undefined, CANNOT_CHECK_ZERO_BURDEN.
      Never coerced to 0 or to +inf.

Cost note: E costs (1 + k) future-family evaluations plus up to k*P_MAX T0
proposals.  It is therefore computed ONLY on T2-promoted survivors -- which is
precisely why the multi-fidelity ladder is load-bearing here.
"""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

K_STEPS = 3
P_MAX = 8
TAU = 0.0
CAP_BIN_LO = 0.5   # == CAPABILITY_FLOOR_V1; nothing below the floor is viable
CAP_BIN_HI = 1.0
CAP_BIN_WIDTH = 0.05

ZERO_BURDEN = "CANNOT_CHECK_ZERO_BURDEN"
NO_COMPILE = "CANNOT_CHECK_NO_LEGAL_PROPOSAL"


def cap_bin(capability: float) -> Optional[int]:
    """Fixed-width capability bin index, or None below the viability floor."""
    c = float(capability)
    if c < CAP_BIN_LO:
        return None
    if c >= CAP_BIN_HI:
        return int(round((CAP_BIN_HI - CAP_BIN_LO) / CAP_BIN_WIDTH)) - 1
    return int((c - CAP_BIN_LO) / CAP_BIN_WIDTH)


def cap_bin_edges() -> List[Tuple[float, float]]:
    n = int(round((CAP_BIN_HI - CAP_BIN_LO) / CAP_BIN_WIDTH))
    return [(round(CAP_BIN_LO + i * CAP_BIN_WIDTH, 4),
             round(CAP_BIN_LO + (i + 1) * CAP_BIN_WIDTH, 4)) for i in range(n)]


def _t0_ok(cand: Any) -> Tuple[bool, Dict[str, Any]]:
    """Legal compile + every frozen hard gate at T0. Executes the gates."""
    from evaluation.evaluate import evaluate_genome
    try:
        r = evaluate_genome(cand, tier="T0")
    except Exception:  # noqa: BLE001 -- crash is a legitimate rejection
        return False, {}
    return bool(r.get("feasible")), r


def _t2_capability(cand: Any, ledger: Any):
    """T2 capability of a candidate, charged. None if it is not T2-feasible."""
    from evaluation.evaluate import evaluate_genome
    try:
        r = evaluate_genome(cand, tier="T2")
    except Exception:  # noqa: BLE001
        ledger.charge_crash("T2_governed")
        return None
    ledger.charge_eval("T2_governed", r.get("evaluation"))
    if not r.get("feasible"):
        return None
    return float(r["evaluation"].get("solved_fraction", 0.0))


def governed_step(g: Any, rng: random.Random, base_cap: float,
                  ledger: Any) -> Tuple[Any, Dict[str, Any]]:
    """One governed step. Returns (accepted_or_original, step_record).

    The no-regression test compares LIKE WITH LIKE: base_cap is the current
    family's T2 capability, so a candidate is scored at T2 too. Comparing a
    candidate's T0 solved_fraction against a T2 baseline compares a 15-task
    screen with an 88-task developmental battery; measured on 92 T2-feasible
    forms, T0 capability was below T2 capability in 92 of 92 cases, so such a
    test is not a no-regression gate at all.

    T0 remains a cheap PRE-FILTER: a candidate that fails the frozen hard gates
    at T0 is rejected before paying for T2. Both evaluations are charged.

    Every proposal is charged to `ledger` whether or not it is accepted.
    """
    from morphology.mutations import mutate
    proposals = 0
    for _ in range(P_MAX):
        proposals += 1
        cand = mutate(g, rng)
        ok, r = _t0_ok(cand)
        ledger.charge_eval("T0_governed", r.get("evaluation") if r else None)
        if not ok:
            continue
        cap = _t2_capability(cand, ledger)
        if cap is None:
            continue
        if cap + 1e-12 >= base_cap - TAU:
            return cand, {"accepted": True, "proposals": proposals,
                          "accepted_capability": round(cap, 6),
                          "capability_tier": "T2"}
    return g, {"accepted": False, "proposals": proposals,
               "accepted_capability": None, "capability_tier": "T2"}


def evolvability(genome: Any, base_capability: float, seed: int,
                 ledger: Any, fof_key: Optional[str] = None) -> Dict[str, Any]:
    """E(x) with its full provenance.

    `ledger` is an oracle.burden.RejectLedger; every proposal and every
    future-family evaluation made here is charged to it, so the work spent
    measuring evolvability is itself part of the arm's burden.
    """
    from oracle.future_family import FOF1_KEY, evaluate_future
    key = fof_key or FOF1_KEY
    rng = random.Random(seed)

    r0 = evaluate_future(genome, key)
    ledger.charge_eval("FOF1", r0.get("evaluation"))
    cap0 = float(r0["evaluation"].get("solved_fraction", 0.0))

    work_before = ledger.total_charged
    cur = genome
    steps: List[Dict[str, Any]] = []
    for i in range(K_STEPS):
        cur, rec = governed_step(cur, rng, base_capability, ledger)
        rec["step"] = i
        steps.append(rec)
    b_steps = ledger.total_charged - work_before

    rk = evaluate_future(cur, key)
    ledger.charge_eval("FOF1", rk.get("evaluation"))
    capk = float(rk["evaluation"].get("solved_fraction", 0.0))

    n_accepted = sum(1 for s in steps if s["accepted"])
    out: Dict[str, Any] = {
        "fof_key": key,
        "k_steps": K_STEPS,
        "n_accepted": n_accepted,
        # Discriminating signal. If every step accepts its FIRST proposal the
        # gate is not gating, and a zero delta is attributable to the mutation
        # operator being near-neutral on the future family rather than to
        # governance or to a saturated family.
        "proposals_per_step": [s["proposals"] for s in steps],
        "total_proposals": sum(s["proposals"] for s in steps),
        "steps": steps,
        "cap_fof_before": round(cap0, 6),
        "cap_fof_after": round(capk, 6),
        "delta_cap_fof": round(capk - cap0, 6),
        "b_steps": round(b_steps, 6),
        "cap_bin": cap_bin(base_capability),
    }
    if b_steps <= 0.0:
        out["evolvability"] = ZERO_BURDEN
        out["status"] = ZERO_BURDEN
        return out
    if n_accepted == 0:
        # Charged, but no legal governed move existed. This is a real and
        # informative outcome (a form at an evolutionary dead end), NOT an
        # error: E is defined and equals delta/burden, which will be 0/burden.
        out["status"] = "NO_ACCEPTED_PROPOSAL"
    else:
        out["status"] = "OK"
    out["evolvability"] = round((capk - cap0) / b_steps, 9)
    return out


def shuffle_null(records: List[Dict[str, Any]], seed: int,
                 n_perm: int = 1000) -> Dict[str, Any]:
    """Shuffle-equal-n null for a within-bin evolvability claim (falsifier F1).

    Within each capability bin, the observed statistic is the mean evolvability
    of the arm's members.  The null permutes the arm labels among the members
    of that bin, holding n per arm fixed.  Selectivity is not edge: an arm that
    merely picks high-capability forms cannot score here, because the bin holds
    capability fixed.
    """
    import statistics
    rng = random.Random(seed)
    by_bin: Dict[int, List[Dict[str, Any]]] = {}
    for r in records:
        b = r.get("cap_bin")
        e = r.get("evolvability")
        if b is None or not isinstance(e, (int, float)) or isinstance(e, bool):
            continue
        by_bin.setdefault(int(b), []).append(r)

    out: Dict[str, Any] = {"n_perm": n_perm, "bins": {}, "seed": seed}
    for b, rs in sorted(by_bin.items()):
        arms = sorted({r["arm"] for r in rs if "arm" in r})
        if len(arms) < 2 or len(rs) < 4:
            out["bins"][str(b)] = {"status": "CANNOT_CHECK_TOO_FEW",
                                   "n": len(rs), "n_arms": len(arms)}
            continue
        vals = [float(r["evolvability"]) for r in rs]
        labels = [r["arm"] for r in rs]
        obs = {}
        for a in arms:
            xs = [v for v, l in zip(vals, labels) if l == a]
            obs[a] = statistics.fmean(xs) if xs else None
        ref = arms[0]
        obs_stat = {a: (obs[a] - obs[ref]) for a in arms
                    if obs[a] is not None and obs[ref] is not None}
        ge = {a: 0 for a in obs_stat}
        for _ in range(n_perm):
            perm = labels[:]
            rng.shuffle(perm)
            pm = {}
            for a in arms:
                xs = [v for v, l in zip(vals, perm) if l == a]
                pm[a] = statistics.fmean(xs) if xs else None
            for a in obs_stat:
                if pm.get(a) is None or pm.get(ref) is None:
                    continue
                if abs(pm[a] - pm[ref]) >= abs(obs_stat[a]):
                    ge[a] += 1
        out["bins"][str(b)] = {
            "status": "OK", "n": len(rs), "reference_arm": ref,
            "per_arm_n": {a: sum(1 for l in labels if l == a) for a in arms},
            "observed_mean": {a: (round(v, 9) if v is not None else None)
                              for a, v in obs.items()},
            "observed_delta_vs_ref": {a: round(v, 9)
                                      for a, v in obs_stat.items()},
            "p_two_sided": {a: round((ge[a] + 1) / (n_perm + 1), 6)
                            for a in ge},
        }
    return out


def redundancy_check(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Falsifier F2: is evolvability just capability wearing another name?"""
    by_bin: Dict[int, List[Tuple[float, float]]] = {}
    for r in records:
        b, e, c = r.get("cap_bin"), r.get("evolvability"), r.get("capability")
        if b is None or not isinstance(e, (int, float)) or isinstance(e, bool):
            continue
        if not isinstance(c, (int, float)) or isinstance(c, bool):
            continue
        by_bin.setdefault(int(b), []).append((float(c), float(e)))
    out: Dict[str, Any] = {"threshold_spearman": 0.95, "bins": {}}
    for b, pairs in sorted(by_bin.items()):
        if len(pairs) < 5:
            out["bins"][str(b)] = {"status": "CANNOT_CHECK_TOO_FEW",
                                   "n": len(pairs)}
            continue
        rho = _spearman([p[0] for p in pairs], [p[1] for p in pairs])
        if rho is None:
            # Zero variance in one series (typically evolvability all-equal).
            # "could not check" is NOT "checked and not redundant": reporting
            # redundant=False here would read as a passed test.
            out["bins"][str(b)] = {"status": "CANNOT_CHECK_ZERO_VARIANCE",
                                   "n": len(pairs),
                                   "spearman_cap_vs_evolvability": None,
                                   "redundant": None}
            continue
        out["bins"][str(b)] = {
            "status": "OK", "n": len(pairs),
            "spearman_cap_vs_evolvability": round(rho, 6),
            "redundant": abs(rho) >= 0.95,
        }
    return out


def _rank(xs: List[float]) -> List[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _spearman(a: List[float], b: List[float]) -> Optional[float]:
    if len(a) != len(b) or len(a) < 2:
        return None
    ra, rb = _rank(a), _rank(b)
    n = len(ra)
    ma = sum(ra) / n
    mb = sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    if da == 0 or db == 0:
        return None
    return num / (da * db)
