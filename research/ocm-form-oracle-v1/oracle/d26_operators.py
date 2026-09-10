"""D26 — cross-domain operator transfer (#233 D26, folded into FO-V1).

A general-operator claim requires transfer of the operator's INVARIANT
CONTRACT, not reuse of its name.  The contract is stated once, as
domain-independent postconditions, and ONE abstract driver per operator runs
UNCHANGED across three materially different domains through thin adapters
(oracle/d26_adapters.py).  Transfer is conformance of the postconditions.

    DISTINGUISH(H, ctx) -> (obs, H')
      D1 progress    |H'| < |H|, or obs is None WITH a certificate that no
                     distinguishing observation exists
      D2 soundness   the true hypothesis is never eliminated

    REFINE(A, cex, ctx) -> A'
      R1 excludes    cex is not admitted by A'
      R2 sound over-approximation   nothing truly equivalent is separated

    REDUCE(p, ctx) -> (p', back)
      Q1 sound       back(solve(p')) solves p whenever solve(p') succeeds
      Q2 no invention  p unsolvable => p' unsolvable

    VERIFY(x, claim, ctx) -> ACCEPT | REJECT(witness)
      V1 soundness   never ACCEPT a false claim
      V2 witnessed   REJECT carries a checkable witness

DOMAINS (three materially different, all frozen on main):
    D_SEM  OW2   ambiguity / safe-action sets      (semantics)
    D_ABS  OW5S  finite transition systems         (abstraction / planning)
    D_ALG  OW6   expression rewriting / equality   (algebra)

SCOPE DEVIATION, recorded not hidden: #233 F specifies OW9 ("cross-domain
same-hypergraph") as the purpose-built world for this test.  OW9 does not exist
on main -- exact/worlds.py implements OW1..OW7 only, verified by enumeration
with a matching control.  D26 here therefore tests contract transfer across
INDEPENDENT domains, which is a weaker and more honest claim than OW9's
same-derivation design would support.

NEGATIVE TRANSFER is a result, not a bug.  A domain where an obligation FAILS
is reported as failing and kept: REDUCE over abstraction-based reachability is
expected to fail Q1/Q2 because over-approximation admits spurious
counterexamples, which is D20's phase boundary reappearing as a contract
violation rather than as a runtime cost.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

from oracle.d26_adapters import ADAPTERS, NotSupported

OPERATORS: Tuple[str, ...] = ("DISTINGUISH", "REFINE", "REDUCE", "VERIFY")
DOMAINS: Tuple[str, ...] = ("D_SEM", "D_ABS", "D_ALG")

CONTRACT: Dict[str, Dict[str, str]] = {
    "DISTINGUISH": {
        "D1": "|H'| < |H| or (obs is None and no-distinguisher certificate)",
        "D2": "the true hypothesis is never eliminated",
    },
    "REFINE": {
        "R1": "the counterexample is not admitted by the refined abstraction",
        "R2": "nothing truly equivalent is separated (sound over-approximation)",
    },
    "REDUCE": {
        "Q1": "back(solve(p')) solves p whenever solve(p') succeeds",
        "Q2": "p unsolvable implies p' unsolvable",
    },
    "VERIFY": {
        "V1": "never ACCEPT a false claim",
        "V2": "REJECT carries a checkable witness",
    },
}

CANNOT_CHECK = "CANNOT_CHECK"


# --------------------------------------------------------------- the drivers
# One implementation per operator.  These never mention a domain.

def drive_distinguish(ad: Any, w: Any) -> Dict[str, Any]:
    H0 = ad.hypotheses(w)
    truth = ad.truth(w)
    obs = ad.best_observation(w, H0)
    if obs is None:
        cert = bool(ad.no_distinguisher_certificate(w, H0))
        return {"obs": None, "n_before": len(H0), "n_after": len(H0),
                "D1": cert, "D2": _member(truth, H0), "certificate": cert}
    H1 = ad.filter(w, H0, obs)
    return {"obs": ad.render(obs), "n_before": len(H0), "n_after": len(H1),
            "D1": len(H1) < len(H0), "D2": _member(truth, H1),
            "certificate": None}


def _member(x: Any, xs: List[Any]) -> bool:
    for y in xs:
        if y is x or y == x:
            return True
    return False


def drive_refine(ad: Any, w: Any) -> Dict[str, Any]:
    A0 = ad.initial_abstraction(w)
    cex = ad.spurious_counterexample(w, A0)
    if cex is None:
        return {"status": "NO_SPURIOUS_CEX", "R1": None, "R2": None}
    A1 = ad.refine(w, A0, cex)
    if A1 is None:
        # No-progress refinement is DETECTED. R1 fails; R2 still assessed on A0.
        return {"status": "REFINE_NO_PROGRESS", "R1": False,
                "R2": bool(ad.sound_over_approx(w, A0))}
    return {"status": "OK",
            "R1": not bool(ad.admits(w, A1, cex)),
            "R2": bool(ad.sound_over_approx(w, A1)),
            "size_before": ad.abstraction_size(A0),
            "size_after": ad.abstraction_size(A1)}


def drive_reduce(ad: Any, w: Any) -> Dict[str, Any]:
    p = ad.problem(w)
    red = ad.reduce(w, p)
    if red is None:
        return {"status": "NO_REDUCTION", "Q1": None, "Q2": None}
    p2, back = red
    sol2 = ad.solve(w, p2)
    solvable_p = bool(ad.solvable(w, p))
    # Q2: p unsolvable => p' unsolvable.  p' is "solved" exactly when solve
    # returns something, so the obligation is checkable on every world.
    q2 = True if solvable_p else (sol2 is None)
    if sol2 is None:
        return {"status": "TARGET_UNSOLVED", "Q1": None, "Q2": q2,
                "p_solvable": solvable_p}
    mapped = back(sol2)
    return {"status": "OK", "Q1": bool(ad.checks(w, p, mapped)), "Q2": q2,
            "p_solvable": solvable_p}


def drive_verify(ad: Any, w: Any) -> Dict[str, Any]:
    cases = ad.verify_cases(w)
    v1 = True
    v2 = True
    n_true = n_false = n_rejected = 0
    for x, claim, is_true in cases:
        verdict, witness = ad.verify(w, x, claim)
        if is_true:
            n_true += 1
        else:
            n_false += 1
            if verdict == "ACCEPT":
                v1 = False           # accepted a false claim: soundness broken
        if verdict == "REJECT":
            n_rejected += 1
            if witness is None or not ad.check_witness(w, x, claim, witness):
                v2 = False
    return {"V1": v1, "V2": (v2 if n_rejected else None), "n_cases": len(cases),
            "n_true_claims": n_true, "n_false_claims": n_false,
            "n_rejected": n_rejected}


DRIVERS: Dict[str, Callable[[Any, Any], Dict[str, Any]]] = {
    "DISTINGUISH": drive_distinguish,
    "REFINE": drive_refine,
    "REDUCE": drive_reduce,
    "VERIFY": drive_verify,
}


def run_operator(domain: str, operator: str,
                 max_worlds: int = 24) -> Dict[str, Any]:
    """Run one abstract driver against one domain over its frozen worlds."""
    ad_cls = ADAPTERS.get(domain)
    if ad_cls is None:
        return {"domain": domain, "operator": operator,
                "status": "%s_UNKNOWN_DOMAIN" % CANNOT_CHECK}
    ad = ad_cls()
    try:
        worlds = ad.worlds()[:max_worlds]
    except NotSupported as e:
        return {"domain": domain, "operator": operator,
                "status": "%s_UNSUPPORTED" % CANNOT_CHECK, "reason": str(e)}
    except Exception as e:  # noqa: BLE001
        return {"domain": domain, "operator": operator,
                "status": "%s_WORLDS_UNAVAILABLE" % CANNOT_CHECK,
                "reason": repr(e)[:200]}

    driver = DRIVERS[operator]
    per_world: List[Dict[str, Any]] = []
    obligations: Dict[str, Dict[str, int]] = {k: {"pass": 0, "fail": 0, "na": 0}
                                              for k in CONTRACT[operator]}
    n_exceptions = 0
    for w in worlds:
        try:
            r = driver(ad, w)
        except NotSupported as e:
            return {"domain": domain, "operator": operator,
                    "status": "%s_UNSUPPORTED" % CANNOT_CHECK,
                    "reason": str(e)}
        except Exception as e:  # noqa: BLE001
            r = {"status": "EXCEPTION", "error": repr(e)[:200]}
            n_exceptions += 1
        r["world"] = ad.wid(w)
        per_world.append(r)
        for k in CONTRACT[operator]:
            v = r.get(k)
            b = obligations[k]
            if v is True:
                b["pass"] += 1
            elif v is False:
                b["fail"] += 1
            else:
                b["na"] += 1

    exercised = {k: (b["pass"] + b["fail"]) > 0 for k, b in obligations.items()}
    all_exercised = all(exercised.values())
    conforms = all(b["fail"] == 0 for b in obligations.values()) and all_exercised
    if n_exceptions:
        status = "%s_DRIVER_EXCEPTION" % CANNOT_CHECK
    elif not all_exercised:
        status = "%s_NO_OBLIGATION_EXERCISED" % CANNOT_CHECK
    else:
        status = "OK"
    return {
        "domain": domain, "operator": operator, "status": status,
        "n_worlds": len(per_world), "n_exceptions": n_exceptions,
        "contract": CONTRACT[operator],
        "obligations": obligations,
        "obligations_exercised": exercised,
        "conforms": (conforms if status == "OK" else None),
        "per_world": per_world[:40],
    }


def run_d26(max_worlds: int = 24) -> Dict[str, Any]:
    """The full 4-operator x 3-domain transfer matrix."""
    matrix: Dict[str, Dict[str, Any]] = {}
    for op in OPERATORS:
        matrix[op] = {dom: run_operator(dom, op, max_worlds=max_worlds)
                      for dom in DOMAINS}

    transfer: Dict[str, Any] = {}
    negative: List[Dict[str, Any]] = []
    for op in OPERATORS:
        confirmed, failed, unchecked = [], [], []
        for dom in DOMAINS:
            cell = matrix[op][dom]
            c = cell.get("conforms")
            if c is True:
                confirmed.append(dom)
            elif c is False:
                failed.append(dom)
                negative.append({
                    "operator": op, "domain": dom,
                    "failing_obligations": [k for k, b in
                                            (cell.get("obligations") or {}).items()
                                            if b.get("fail", 0) > 0],
                    "obligations": cell.get("obligations"),
                })
            else:
                unchecked.append(dom)
        transfer[op] = {
            "domains_conforming": confirmed,
            "domains_failing": failed,
            "domains_cannot_check": unchecked,
            # A general-operator claim needs the contract to hold in all three
            # materially different domains. Fewer is a SCOPED claim and is
            # labelled as one rather than rounded up.
            "verdict": ("CONTRACT_TRANSFERS" if len(confirmed) == len(DOMAINS)
                        else ("CONTRACT_FAILS_TRANSFER" if failed
                              else "SCOPED_%d_OF_%d_DOMAINS"
                                   % (len(confirmed), len(DOMAINS)))),
        }
    return {
        "study": "FO_D26_OPERATOR_TRANSFER_V1",
        "operators": list(OPERATORS),
        "domains": list(DOMAINS),
        "scope_deviation": (
            "OW9 (cross-domain same-hypergraph) does not exist on main; "
            "exact/worlds.py implements OW1..OW7 only. D26 therefore tests "
            "contract transfer across INDEPENDENT domains, a weaker claim than "
            "OW9's same-derivation design."),
        "matrix": matrix,
        "transfer": transfer,
        "negative_transfer": negative,
    }


def main(argv=None) -> int:
    import argparse
    import json
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-worlds", type=int, default=24)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    r = run_d26(max_worlds=a.max_worlds)
    tmp = a.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(r, fh, sort_keys=True, separators=(",", ":"), default=str)
    os.replace(tmp, a.out)
    with open(a.out + ".status", "w") as fh:
        fh.write("OK\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
