"""Ledger Tradeoffs: a seal needing several vouchers, each from a priced menu.

Fixed seed 1110. Six instances; voucher count, menu widths, shared menu lines,
and one forbidden omni-stamp vary. Menus are explicit OR alternatives, and the
seal demands one pick per voucher, so the ledger has to be paid in full.
"""

from families._common import make_instance

FAMILY_NAME = "Ledger Tradeoffs"
FAMILY_BLURB = ("A ledger seal stamped only when every voucher line is covered; "
                "each voucher can be bought from a small menu at posted prices, "
                "some lines appear on two vouchers, and one tempting omni-stamp "
                "is forbidden outright.")
SEED = 1110

# vouchers: name -> list of menu options; option = (label, price, arity)
LEDGERS = [
    {"vouchers": {"v_bond": [("b_single", 5), ("b_pair_a", 2)],
                  "v_tax": [("t_single", 4)]}, "shared": []},
    {"vouchers": {"v_bond": [("b_pair_a", 2), ("b_pair_b", 2)],
                  "v_tax": [("t_single", 3), ("t_pair_a", 1)]},
     "shared": ["b_pair_a"]},
    {"vouchers": {"v_bond": [("b_single", 6), ("b_tri_a", 1)],
                  "v_tax": [("t_single", 6), ("t_tri_a", 1)],
                  "v_fee": [("f_single", 5)]},
     "shared": [], "omni": ("omni_stamp", 3)},
    {"vouchers": {"v_bond": [("b_pair_a", 1), ("b_pair_b", 3)],
                  "v_tax": [("t_pair_a", 1), ("t_pair_b", 3)],
                  "v_fee": [("f_single", 5)]},
     "shared": ["b_pair_a", "t_pair_a"], "omni": ("omni_stamp", 2)},
    {"vouchers": {"v_bond": [("b_single", 9), ("b_alt", 4)],
                  "v_tax": [("t_single", 9), ("t_alt", 4)]},
     "shared": [], "omni": ("omni_stamp", 8)},
    {"vouchers": {"v_bond": [("b_pair_a", 2), ("b_pair_b", 2), ("b_pair_c", 2)],
                  "v_tax": [("t_single", 7)],
                  "v_fee": [("f_pair_a", 3), ("f_pair_b", 3)]},
     "shared": ["b_pair_b"]},
]


def emit(seed: int) -> list:
    assert seed == SEED, "family seed is pinned"
    out = []
    for idx, spec in enumerate(LEDGERS, 1):
        elements, weights, implications = ["ledger_seal"], {"ledger_seal": 99}, []
        vnames = sorted(spec["vouchers"])
        for v in vnames:
            elements.append(v)
            weights[v] = 99
            for label, price in spec["vouchers"][v]:
                if label.startswith("b_pair") or label.startswith("t_pair") \
                        or label.startswith("f_pair"):
                    twin = label + "x"
                    elements += [label, twin]
                    weights[label] = price
                    weights[twin] = price
                    implications.append({"if": [label, twin], "then": [v]})
                elif label.endswith("_tri_a"):
                    helpers = [label + "1", label + "2", label + "3"]
                    elements += [label] + helpers
                    weights[label] = price
                    for h in helpers:
                        weights[h] = price
                    implications.append({"if": [label] + helpers, "then": [v]})
                else:
                    elements.append(label)
                    weights[label] = price
                    implications.append({"if": [label], "then": [v]})
        omni = spec.get("omni")
        excluded = []
        if omni:
            elements.append(omni[0])
            weights[omni[0]] = omni[1]
            excluded.append(omni[0])
            for v in vnames:
                implications.append({"if": [omni[0]], "then": [v]})
        implications.append({"if": vnames, "then": ["ledger_seal"]})
        core = {
            "elements": elements,
            "implications": implications,
            "base": [],
            "excluded": excluded,
            "weights": weights,
            "goals": ["ledger_seal"],
        }
        out.append(make_instance(FAMILY_NAME, "ledger_%02d" % idx, core, {
            "voucher_menus": spec["vouchers"],
            "shared_lines": spec["shared"],
            "forbidden_omni": omni[0] if omni else None,
            "tier": idx,
            "intent_note": "pair lines need both halves; tri lines need all four atoms",
        }))
    return out
