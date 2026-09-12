"""RV-377-101 / gap DG-9 — the best-constant control, computed for every ecology the corpus uses.

WHY. `RV-377-100` recovered a genotype the descriptor called DENSE, admissible, robust under all six registered
interventions and surviving full-set atrophy. Its wiring was `DENSE(width 1) -> LINEAR -> OUTPUT` with the INPUT node
and the TARGET node BOTH UNWIRED: it read neither the query nor the feedback and emitted a constant. It cleared
theta = 0.85 on `E_sym3` because the best constant clears theta on `E_sym3`.

An admissibility threshold only means something if a machine that ignores its input and its feedback fails it. This
module computes, for every ecology in the corpus, the capability of the BEST CONSTANT ANSWER, and marks any ecology
whose best constant reaches theta as NON_DISCRIMINATING at that theta.

The constant is optimised over the full fixed-point grid the instrument admits, so this is the strongest constant
available to an adversary, not a convenient one.
"""
import json
import os

from . import ecology, smooth

THETA = smooth.THETA
FX = smooth.FX_ONE
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")


def best_constant(target, eval_set):
    """capability of the best single fx constant, and the constant attaining it."""
    best = (-1.0, None)
    for c in range(-128, 128):
        err = sum(abs(c - target[x]) for x in eval_set) / FX / len(eval_set)
        cap = max(0.0, 1 - err / 1.5)
        if cap > best[0]:
            best = (round(cap, 4), c)
    return best


def audit(theta=THETA):
    rows = {}
    # the five registered ecologies, under both evaluation criteria
    for name, spec in ecology.REGISTRY.items():
        t = ecology.target_of(spec)
        for crit, ev in (("unseen", smooth.UNSEEN), ("all", smooth.ALL_X)):
            cap, c = best_constant(t, ev)
            rows[f"{name}|{crit}"] = {"family": "registered", "best_constant_capability": cap, "constant_fx": c,
                                      "theta": theta, "discriminating": cap < theta}
    # the E_sym(k) family: k/16 in all four coefficients, k = 0..16. Used by RV-377-021/025 for the
    # three-class admissible-set work, and never checked against a constant.
    for k in range(0, 17):
        t = smooth.make_target((k / 16,) * 4)
        for crit, ev in (("unseen", smooth.UNSEEN), ("all", smooth.ALL_X)):
            cap, c = best_constant(t, ev)
            rows[f"E_sym{k}|{crit}"] = {"family": "E_sym(k) sweep", "k": k, "best_constant_capability": cap,
                                        "constant_fx": c, "theta": theta, "discriminating": cap < theta}
    bad = sorted(k for k, v in rows.items() if not v["discriminating"])
    receipt = {"schema": "GMIConstantControlAuditV1", "revival_record": "RV-377-101", "gap": "DG-9",
               "theta": theta, "constant_grid": "every fx value in [-128, 127] on the registered 8-bit instrument",
               "n_ecology_criterion_pairs": len(rows), "rows": rows,
               "non_discriminating": bad, "n_non_discriminating": len(bad),
               "claim_ceiling": "this measures only whether a constant clears theta. An ecology that IS "
                                "discriminating by this test may still be weak for other reasons; passing it is "
                                "necessary, not sufficient."}
    receipt["receipt_sha256"] = ecology.sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, "STAGE_DG9_CONSTANT_CONTROL_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    r = audit()
    print(f"theta = {r['theta']}   pairs audited = {r['n_ecology_criterion_pairs']}")
    print(f"\n{'ecology|criterion':22s} {'best const':>10s} {'c':>5s}  discriminating")
    for k in sorted(r["rows"], key=lambda x: (r["rows"][x]["discriminating"], x)):
        v = r["rows"][k]
        print(f"  {k:20s} {v['best_constant_capability']:10.4f} {v['constant_fx']:5d}  "
              f"{'yes' if v['discriminating'] else 'NO  <-- NON_DISCRIMINATING'}")
    print(f"\nNON-DISCRIMINATING: {r['n_non_discriminating']} of {r['n_ecology_criterion_pairs']}")
    print(f"  {r['non_discriminating']}")
