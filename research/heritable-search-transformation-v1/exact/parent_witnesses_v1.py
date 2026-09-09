"""parent_witnesses_v1.py -- PARENT_SUFFICIENT instantiations for HST-T04 (Levin/OOPS
2^{-L} allocation) and HST-T08 (Blackwell dominance), at HST scope, tiny exact witnesses.
No new mathematics: parents own the theorems; this file only instantiates + checks the
arithmetic exactly. Generates PARENT_WITNESSES_T04_T08_V1.json.

T04: prefix code C0 = {m1:'0', m2:'10', m3:'110', m4:'111'} (Kraft sum = 1, complete).
Target solution encoded m3.m4 ('110111'), L=6, search share 2^-6. After admitting macro
m0 := m3.m4 and re-freezing a complete code C1 = {m0:'0', m2:'10', m3:'110', m4:'111'},
the same construction is encoded '0', L'=1, share 2^-1. Ratio = 2^(6-1) = 32 = 2^Delta.
Kraft inequality verified for both codes. Wall-time improvement stays conditional on
scheduler/execution/verification cost (allocation != runtime) -- stated, not claimed.

T08: hidden state w in {0,1} uniform; action a in {a0,a1}; utility U(w,a)=1 iff a=w
(disjoint correct actions). E1 reveals w exactly -> V(E1)=1. E0 = garbled evaluator
evidence: binary channel flip gamma=1/4 -> optimal value V(E0) = 1-gamma = 3/4.
VoI = 1/4 exactly. Cost correction: probe price c=0.3 > 0.25 -> do not buy.
"""
import json
from fractions import Fraction

import finite_world_v1 as fw  # noqa: F401  (world lineage only; witnesses standalone)


def t04() -> dict:
    c0 = {"m1": "0", "m2": "10", "m3": "110", "m4": "111"}
    c1 = {"m0": "0", "m2": "10", "m3": "110", "m4": "111"}
    def alloc(code):
        a = {m: Fraction(1, 2 ** len(w)) for m, w in code.items()}
        kraft = sum(a.values())
        assert all(not (w2.startswith(w) or w.startswith(w2)) or w == w2
                   for w in code.values() for w2 in code.values()), "not prefix-free"
        assert kraft <= 1
        return a, kraft
    a0, k0 = alloc(c0)
    a1, k1 = alloc(c1)
    sol0, sol1 = "110111", "0"
    share0, share1 = Fraction(1, 2 ** len(sol0)), Fraction(1, 2 ** len(sol1))
    delta = len(sol0) - len(sol1)
    return {"prefix_code_before": c0, "prefix_code_after": c1,
            "allocation_before": {m: str(v) for m, v in a0.items()},
            "allocation_after": {m: str(v) for m, v in a1.items()},
            "kraft_sum_before": [str(k0), float(k0)],
            "kraft_sum_after": [str(k1), float(k1)],
            "solution_encoding_before": {"bits": sol0, "L": len(sol0),
                                         "share_2^-L": [str(share0), float(share0)]},
            "solution_encoding_after": {"bits": sol1, "L": len(sol1),
                                        "share_2^-L": [str(share1), float(share1)]},
            "share_ratio": [str(share1 / share0), float(share1 / share0)],
            "Delta": delta, "ratio_equals_2^Delta": share1 / share0 == Fraction(2) ** delta,
            "conditionality": "allocation ratio is exact; wall-time gain remains "
                              "conditional on scheduler/execution/verification costs"}


def t08() -> dict:
    prior = {0: Fraction(1, 2), 1: Fraction(1, 2)}
    gamma = Fraction(1, 4)
    # E1: noiseless reveal -> follow observation, V(E1) = 1
    v1 = Fraction(1)
    # E0: garbled y = w XOR flip(gamma); P(y=w) = 1-gamma; best policy follows y
    p_correct = Fraction(1) - gamma
    v0 = p_correct
    voi = v1 - v0
    probe_price = Fraction(3, 10)
    return {"states": [0, 1], "prior": [str(v) for v in prior.values()],
            "utility": "U(w,a)=1 iff a==w else 0 (disjoint correct actions)",
            "E1": "evaluator evidence reveals w exactly (ungarbled)",
            "E0": "evaluator evidence garbled: y = w flipped with prob gamma=1/4",
            "V_E1": [str(v1), float(v1)], "V_E0": [str(v0), float(v0)],
            "value_of_information": [str(voi), float(voi)],
            "blackwell_relation": "E0 is an a.s. garbling of E1 => E1 dominates E0",
            "cost_correction_probe_price": [str(probe_price), float(probe_price)],
            "buy_information": probe_price < voi}


def main() -> dict:
    t4 = t04()
    t8 = t08()
    assert t4["ratio_equals_2^Delta"] and t4["Delta"] == 5
    assert t8["V_E0"][0] == "3/4" and t8["value_of_information"][0] == "1/4"
    assert t8["buy_information"] is False
    return {"certificate_id": "PARENT_WITNESSES_T04_T08_V1",
            "theorem_ids": ["HST-T04", "HST-T08"],
            "status_class": "PARENT_SUFFICIENT (Levin/OOPS; Blackwell own the theorems)",
            "T04_allocation_witness": t4, "T08_blackwell_witness": t8,
            "deterministic": True}


if __name__ == "__main__":
    doc = main()
    with open("PARENT_WITNESSES_T04_T08_V1.json", "w") as fh:
        json.dump(doc, fh, sort_keys=True, indent=1)
    print("T04/T08 OK: ratio=%s VoI=%s buy=%s" % (
        t04()["share_ratio"][0], t08()["value_of_information"][0], t08()["buy_information"]))
