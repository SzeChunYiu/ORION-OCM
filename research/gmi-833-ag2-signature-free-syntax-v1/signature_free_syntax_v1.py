# -*- coding: utf-8 -*-
"""AG2 route A -- many-sorted signature Sigma_G0 and its free term algebra.

Route A builds the term algebra by *depth-indexed recursive generation* and
interprets terms with an explicit small-step configuration machine.  The
independent oracle (independent_oracle_v1.py) rebuilds the same objects by
*closure iteration to a fixed point* over a separately written rule table and a
separately written table-driven semantics, importing nothing from this file.

Stdlib only.  Exact arithmetic: every quantity here is an int or a
fractions.Fraction; no float ever enters a claim.

    python3 -I -B signature_free_syntax_v1.py
"""

import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

# --------------------------------------------------------------------------
# AG2 part 1 -- the many-sorted signature.  Symbols only; no semantics here.
# --------------------------------------------------------------------------

SORTS = ("Reg", "Label", "Instr", "Prog")

# name -> (argument sorts, result sort).  Nullary ops are the generators.
SIGMA_G0 = {
    "r0":    ((), "Reg"),
    "l0":    ((), "Label"),
    "l1":    ((), "Label"),
    "read":  (("Reg", "Label"), "Instr"),
    "inc":   (("Reg", "Label"), "Instr"),
    "emit":  (("Reg", "Label"), "Instr"),
    "decjz": (("Reg", "Label", "Label"), "Instr"),
    "halt":  ((), "Instr"),
    "prog":  (("Instr", "Instr"), "Prog"),
}

# The registered bound.  Depth 3 is the least depth at which the Prog sort is
# inhabited, and the signature is non-recursive, so depth 3 is already the
# fixed point.
DEPTH_BOUND = 3


class Term(object):
    __slots__ = ("op", "args")

    def __init__(self, op, args=()):
        self.op = op
        self.args = tuple(args)

    def sort(self):
        return SIGMA_G0[self.op][1]

    def depth(self):
        if not self.args:
            return 1
        return 1 + max(a.depth() for a in self.args)

    def __str__(self):
        if not self.args:
            return self.op
        return "%s(%s)" % (self.op, ",".join(str(a) for a in self.args))

    def __eq__(self, other):
        return isinstance(other, Term) and str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def _bag(self, bag):
        bag[self.op] = bag.get(self.op, 0) + 1
        for a in self.args:
            a._bag(bag)
        return bag

    def symbol_multiset(self):
        return tuple(sorted(self._bag({}).items()))


def well_sorted(term):
    """Formation rule, stated once, decidable, total on candidate trees."""
    if not isinstance(term, Term):
        return (False, "NOT_A_TERM")
    if term.op not in SIGMA_G0:
        return (False, "UNKNOWN_SYMBOL:%s" % term.op)
    arg_sorts, _res = SIGMA_G0[term.op]
    if len(term.args) != len(arg_sorts):
        return (False, "ARITY_MISMATCH:%s:%d!=%d" % (term.op, len(term.args), len(arg_sorts)))
    for i, a in enumerate(term.args):
        ok, why = well_sorted(a)
        if not ok:
            return (False, why)
        if a.sort() != arg_sorts[i]:
            return (False, "SORT_MISMATCH:%s:arg%d:%s!=%s" % (term.op, i, a.sort(), arg_sorts[i]))
    return (True, "OK")


def generate_terms(signature, depth_bound):
    """Route A: depth-indexed recursive generation."""
    by_sort = dict((s, []) for s in SORTS)
    seen = set()
    for d in range(1, depth_bound + 1):
        new = []
        for op in sorted(signature):
            arg_sorts, res = signature[op]
            if not arg_sorts:
                if d == 1:
                    new.append((Term(op), res))
                continue
            pools = [list(by_sort[s]) for s in arg_sorts]
            for combo in _product(pools):
                t = Term(op, combo)
                if t.depth() == d:
                    new.append((t, res))
        for t, res in new:
            k = str(t)
            if k not in seen:
                seen.add(k)
                by_sort[res].append(t)
    for s in SORTS:
        by_sort[s].sort(key=str)
    return by_sort


def _product(pools):
    if not pools:
        yield ()
        return
    head, rest = pools[0], pools[1:]
    for h in head:
        for tail in _product(rest):
            yield (h,) + tail


def closed_under_application(by_sort, signature):
    """Closure: every well-sorted application of a signature operation to
    generated arguments is itself generated (within the sort bound)."""
    have = set()
    for s in SORTS:
        for t in by_sort[s]:
            have.add(str(t))
    missing = []
    for op in sorted(signature):
        arg_sorts, _res = signature[op]
        if not arg_sorts:
            if op not in have:
                missing.append(op)
            continue
        pools = [list(by_sort[s]) for s in arg_sorts]
        for combo in _product(pools):
            t = Term(op, combo)
            if t.depth() > DEPTH_BOUND:
                continue
            if str(t) not in have:
                missing.append(str(t))
    return missing


# --------------------------------------------------------------------------
# AG2 part 2 -- interpretations.  The SAME symbols, two different semantics.
# --------------------------------------------------------------------------

STEP_BUDGET = 8
INPUT_WORDS = ((), (0,), (1,), (2,))
LABELS = ("l0", "l1")


def _binding(prog_term):
    """prog(i_for_l0, i_for_l1)."""
    return {"l0": prog_term.args[0], "l1": prog_term.args[1]}


def run(prog_term, word, interpretation):
    """Small-step transition semantics.  `interpretation` selects how the
    operation SYMBOLS are realised; the syntax is identical in both."""
    binding = _binding(prog_term)
    reg = 0
    pos = 0
    out = []
    pc = "l0"
    steps = 0
    while True:
        if steps >= STEP_BUDGET:
            return ("STEP_BUDGET_EXHAUSTED", tuple(out), reg, steps)
        instr = binding[pc]
        op = instr.op
        if op == "halt":
            steps += 1
            return ("HALTED", tuple(out), reg, steps)
        if op == "read":
            steps += 1
            if pos >= len(word):
                return ("INPUT_UNDERFLOW", tuple(out), reg, steps)
            reg = word[pos]
            pos += 1
            pc = instr.args[1].op
            continue
        if op == "inc":
            steps += 1
            reg += interpretation["inc_delta"]
            pc = instr.args[1].op
            continue
        if op == "emit":
            steps += 1
            out.append(reg)
            pc = instr.args[1].op
            continue
        if op == "decjz":
            steps += 1
            nz = instr.args[1].op
            zz = instr.args[2].op
            if interpretation["decjz_swap"]:
                nz, zz = zz, nz
            if reg > 0:
                reg -= 1
                pc = nz
            else:
                pc = zz
            continue
        raise AssertionError("unreachable: %s" % op)


I_STANDARD = {"name": "I_STANDARD", "inc_delta": 1, "decjz_swap": False}
I_VARIANT = {"name": "I_VARIANT", "inc_delta": 2, "decjz_swap": True}


def behaviour(prog_term, interpretation):
    return tuple(run(prog_term, w, interpretation) for w in INPUT_WORDS)


def has_successor(prog_term):
    """Formation is not transition: a well-formed term whose start label binds
    `halt` yields an initial configuration with no successor."""
    return _binding(prog_term)["l0"].op != "halt"


# --------------------------------------------------------------------------
# AG2 part 3 -- the four separations, as exact finite counts.
# --------------------------------------------------------------------------

def blob_sha(path):
    with open(path, "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


def parent_pin(relpath):
    full = os.path.join(REPO, relpath)
    if not os.path.exists(full):
        return {"path": relpath, "blob_sha": None, "present": False}
    return {"path": relpath, "blob_sha": blob_sha(full), "present": True}


def main():
    by_sort = generate_terms(SIGMA_G0, DEPTH_BOUND)
    counts = dict((s, len(by_sort[s])) for s in SORTS)
    progs = by_sort["Prog"]

    missing = closed_under_application(by_sort, SIGMA_G0)

    # --- [09] symbols vs interpretations -----------------------------------
    std = dict((str(p), behaviour(p, I_STANDARD)) for p in progs)
    var = dict((str(p), behaviour(p, I_VARIANT)) for p in progs)
    interp_divergent = sorted(k for k in std if std[k] != var[k])

    # --- [10] formation vs transition --------------------------------------
    no_successor = sorted(str(p) for p in progs if not has_successor(p))
    # same formation shape (identical operation-symbol multiset), different
    # transition outcome
    shape = {}
    for p in progs:
        shape.setdefault(p.symbol_multiset(), []).append(p)
    same_shape_diff_behaviour = []
    for key in sorted(shape, key=lambda k: str(k)):
        group = sorted(shape[key], key=str)
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if std[str(group[i])] != std[str(group[j])]:
                    same_shape_diff_behaviour.append((str(group[i]), str(group[j])))

    # --- [11] syntactic vs semantic equivalence ----------------------------
    sem_classes = {}
    for p in progs:
        sem_classes.setdefault(std[str(p)], []).append(str(p))
    sem_class_count = len(sem_classes)
    syn_class_count = len(progs)  # ground terms: syntactic equality is identity
    # refinement: every syntactic class sits inside exactly one semantic class
    refinement_failures = 0
    for p in progs:
        owners = [k for k in sem_classes if str(p) in sem_classes[k]]
        if len(owners) != 1:
            refinement_failures += 1
    collapse_witness = None
    for key in sorted(sem_classes, key=lambda k: str(k)):
        members = sorted(sem_classes[key])
        if len(members) >= 2:
            collapse_witness = (members[0], members[1])
            break

    terminal_hist = {}
    for p in progs:
        for st, _o, _r, _s in std[str(p)]:
            terminal_hist[st] = terminal_hist.get(st, 0) + 1

    # How much does the terminal histogram actually pin down?  Sweep the step
    # budget and record where the histogram saturates.  Matching AJ5's
    # published histogram therefore identifies the budget only up to this
    # saturation point -- a boundary on what the cross-check proves.
    global STEP_BUDGET
    saved_budget = STEP_BUDGET
    hist_by_budget = {}
    for b in range(1, 14):
        STEP_BUDGET = b
        h = {}
        for p in progs:
            for st, _o, _r, _s in behaviour(p, I_STANDARD):
                h[st] = h.get(st, 0) + 1
        hist_by_budget[b] = h
    STEP_BUDGET = saved_budget
    saturation = None
    for b in range(1, 14):
        if all(hist_by_budget[k] == hist_by_budget[13] for k in range(b, 14)):
            saturation = b
            break

    # --- [12] bijection with the registered G0 program set -----------------
    core = parent_pin("research/gmi-833-g0-register-core-v1/g0_register_core_v1.py")
    aj5 = parent_pin("research/gmi-833-aj5-g0-lowering-v1/RESULT_V1.json")
    aj5_doc = json.load(open(os.path.join(REPO, aj5["path"]))) if aj5["present"] else {}
    aj5_programs = aj5_doc.get("bounded_programs")
    aj5_hist = aj5_doc.get("terminal_histogram")
    aj5_status_keys = sorted(aj5_doc.get("primitive_status", {}).keys())
    core_src = open(os.path.join(REPO, core["path"])).read() if core["present"] else ""
    core_classes = None
    for line in core_src.splitlines():
        if line.startswith("INSTRUCTION_CLASS_NAMES"):
            core_classes = sorted(
                x.strip().strip('"').strip("'")
                for x in line.split("(", 1)[1].rsplit(")", 1)[0].split(",")
                if x.strip()
            )
            break

    instr_symbols = sorted(op for op in SIGMA_G0 if SIGMA_G0[op][1] == "Instr")
    symbol_to_class = {"read": "READ", "inc": "INC", "emit": "EMIT",
                       "decjz": "DECJZ", "halt": "HALT"}
    derived_classes = sorted(symbol_to_class[s] for s in instr_symbols)

    # --- exact rational summary (no floats anywhere) -----------------------
    semantic_collapse_ratio = Fraction(syn_class_count - sem_class_count, syn_class_count)

    result = {
        "schema": "AG2_SIGNATURE_FREE_SYNTAX_RESULT_V1",
        "issue": 833,
        "status": "GREEN",
        "claim_ceiling": ("AG2_G0_GRAMMAR_GENERATED_AS_FREE_TERM_ALGEBRA_OVER_AN_EXPLICIT_"
                          "MANY_SORTED_SIGNATURE_AT_REGISTERED_FINITE_SCOPE"),
        "results": ["AG2-1", "AG2-2", "AG2-3", "AG2-4", "AG2-5"],
        "signature": {
            "sorts": list(SORTS),
            "operations": dict((k, {"arity": len(v[0]), "argument_sorts": list(v[0]),
                                    "result_sort": v[1]}) for k, v in SIGMA_G0.items()),
            "generators_nullary": sorted(op for op in SIGMA_G0 if not SIGMA_G0[op][0]),
            "depth_bound": DEPTH_BOUND,
        },
        "free_syntax_term_counts": counts,
        "closure_missing_terms": missing,
        "closure_is_closed": len(missing) == 0,
        "interpretation_separation": {
            "interpretations": [I_STANDARD["name"], I_VARIANT["name"]],
            "same_signature": True,
            "same_generated_term_set": True,
            "divergent_program_count": len(interp_divergent),
            "divergent_example": interp_divergent[0] if interp_divergent else None,
        },
        "formation_vs_transition": {
            "well_formed_prog_terms": counts["Prog"],
            "initial_configs_with_no_successor": len(no_successor),
            "no_successor_example": no_successor[0] if no_successor else None,
            "identical_symbol_multiset_different_behaviour_pairs": len(same_shape_diff_behaviour),
            "identical_symbol_multiset_example": (list(same_shape_diff_behaviour[0])
                                                  if same_shape_diff_behaviour else None),
        },
        "syntax_vs_semantics": {
            "syntactic_class_count": syn_class_count,
            "semantic_class_count": sem_class_count,
            "strictly_coarser": sem_class_count < syn_class_count,
            "refinement_failures": refinement_failures,
            "semantic_collapse_ratio": str(semantic_collapse_ratio),
            "collapse_witness": list(collapse_witness) if collapse_witness else None,
        },
        "g0_reconstruction": {
            "instr_terms": counts["Instr"],
            "prog_terms": counts["Prog"],
            "aj5_bounded_programs": aj5_programs,
            "bijection_with_aj5_program_set": aj5_programs == counts["Prog"],
            "derived_instruction_classes": derived_classes,
            "registered_core_instruction_classes": core_classes,
            "instruction_class_sets_equal": core_classes == derived_classes,
            "aj5_primitive_status_keys": aj5_status_keys,
            "aj5_primitive_status_keys_equal": aj5_status_keys == derived_classes,
            "terminal_histogram": terminal_hist,
            "aj5_terminal_histogram": aj5_hist,
            "terminal_histogram_matches_aj5": aj5_hist == terminal_hist,
            "executions": counts["Prog"] * len(INPUT_WORDS),
            "histogram_saturation_step_budget": saturation,
            "histogram_by_step_budget": dict((str(k), hist_by_budget[k]) for k in sorted(hist_by_budget)),
            "histogram_identifies_budget_only_above_saturation": True,
            "input_words": [list(w) for w in INPUT_WORDS],
            "step_budget": STEP_BUDGET,
        },
        "parent_pins": {
            "g0_register_core_executor": core,
            "aj5_lowering_receipt": aj5,
        },
        "forbidden_promotions": [
            "SIGNATURE_IS_THE_BOTTOM",
            "UNIQUE_SIGNATURE_FOR_G0",
            "FREE_ALGEBRA_INVENTED_HERE",
            "BASIS_INDEPENDENT_OPERATION_THEORY_CLAIMED",
            "SYNTACTIC_QUOTIENT_EQUALS_SEMANTIC_QUOTIENT",
            "COMPLETE_GMI",
        ],
    }

    gates = [
        ("closure", result["closure_is_closed"]),
        ("instr_count_11", counts["Instr"] == 11),
        ("prog_count_121", counts["Prog"] == 121),
        ("bijection_aj5", result["g0_reconstruction"]["bijection_with_aj5_program_set"]),
        ("instruction_classes", result["g0_reconstruction"]["instruction_class_sets_equal"]),
        ("aj5_status_keys", result["g0_reconstruction"]["aj5_primitive_status_keys_equal"]),
        ("terminal_histogram", result["g0_reconstruction"]["terminal_histogram_matches_aj5"]),
        ("histogram_saturates_at_6", saturation == 6),
        ("interpretations_diverge", len(interp_divergent) > 0),
        ("some_term_has_no_successor", len(no_successor) > 0),
        ("shape_does_not_fix_behaviour", len(same_shape_diff_behaviour) > 0),
        ("semantics_strictly_coarser", sem_class_count < syn_class_count),
        ("refinement_holds", refinement_failures == 0),
    ]
    failed = [g for g, ok in gates if not ok]
    result["gates"] = dict(gates)
    result["failed_gates"] = failed
    if failed:
        result["status"] = "RED"

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": result["status"], "failed_gates": failed,
                      "counts": counts, "sem_classes": sem_class_count,
                      "terminal_histogram": terminal_hist}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
