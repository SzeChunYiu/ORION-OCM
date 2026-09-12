"""RV-377-069 (gap G8) — exhaustive size census over the typed IR, with canonical-form deduplication, response classes on
a registered ecology, and EXACT OBSTRUCTION results for a declared property vector.

G8: "the new-form criterion needs lower bounds, not only occupancy; exhaustive size census gives exact bounds only to
size 4." Occupancy is an existence statement; a lower bound is a non-existence statement, and only exhaustive enumeration
over a declared alphabet can produce one. "We did not find a genotype realizing P" is not a result; "no genotype of size
at most n over this alphabet realizes P" is.

Three counts are reported at each size, and they are three different things:

  * TYPE-CORRECT GENOTYPES  -- configurations: (slot -> kind) assignments with a typed wiring, over the declared slot
    order. A configuration count, never a count of forms and never a species count.
  * CANONICAL FORMS         -- isomorphism classes of typed parameterized port graphs, by morph.fingerprint. Two
    configurations with the same fingerprint are the same form written twice.
  * RESPONSE CLASSES        -- distinct developmental responses R_{E,J} on the registered ecology: the served trace of
    the whole protocol. Two forms in one response class are developmentally indistinguishable on that ecology.

The three are nested: response classes <= canonical forms <= type-correct genotypes.

Declared alphabet (frozen, with fixed parameters, so the census is over STRUCTURE and not over parameter values), declared
servability filter and declared property vector are all in the constants below. Every obstruction is relative to that
alphabet and those parameters, and the receipt says so.

Writes microscopes/results/STAGE_G8_SIZE_CENSUS_LOWER_BOUNDS_V1.json.
"""
from __future__ import annotations

import itertools
import json
import os
import time

from . import bases, morph, smooth
from .core import FX_ONE, Machine, sha256_of
from .vm import VM

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")

# ------------------------------------------------------------------------------------------ the declared alphabet Sigma
# kind -> frozen parameter assignment. A genotype over Sigma is a typed port graph whose nodes carry these kinds with
# these exact parameters; enlarging Sigma or changing a parameter changes every bound below.
SIGMA = {
    "INPUT": {"width": 4},
    "TARGET": {},
    "OUTPUT": {},
    "CONST": {"value": 0},
    "DENSE": {"width": 4},
    "TABLE": {"keybits": 4},
    "KVSTORE": {"cap": 16},
    "PROGRAM": {"grammar": 0},
    "EDGE": {},
    "LOOKUP": {},
    "NEAREST": {"k": 1, "metric": 0},
    "LINEAR": {},
    "NONLIN1": {"fn": 0},
    "SUM": {},
    "PROGEXEC": {},
    "EVIDENCE": {"cap": 16},
    "GRAD": {"lr": 4},
    "INSERT": {},
    "SEARCH": {"budget": 256},
}
FILLERS = tuple(k for k in SIGMA if k not in ("INPUT", "OUTPUT"))
AT_MOST_ONCE = ("TARGET",)          # the feedback signal is a single interface node

SERVABILITY = ("exactly one INPUT and exactly one OUTPUT; every input port of every node bound (no dangling port); "
               "every node either is the OUTPUT, or is an update-class (U) node, or has at least one outgoing edge "
               "(no dead node); the graph is acyclic and passes morph.typecheck")

# ------------------------------------------------------------------------------------------- the registered ecology
ECOLOGY = {"name": "E_sym5", "coeffs": (5 / 16,) * 4, "n_events": 8, "seed": 0,
           "column": "B0_LOCAL_ADAPTIVE_TRANSDUCERS", "criterion": "unseen", "theta": 0.85,
           "note": "the registered symmetric ecology of the D'/E' microscopes at half the registered development length, "
                   "declared here so that an exhaustive census over tens of thousands of genotypes is affordable; the "
                   "response class is the full served trace of that protocol"}

# --------------------------------------------------------------------------------------- the declared property vector
PROPERTY_VECTOR = {
    "P1_DISTINGUISHES": "the machine's final served answers are not all equal across the 16 inputs (it realizes at least "
                        "one semantic distinction)",
    "P2_LEARNS": "its served answers after development differ from its served answers before any feedback (experience "
                 "changes what it serves)",
    "P3_GENERALIZES": "after development it serves the exactly correct target value on at least one UNSEEN input",
    "P4_ADMISSIBLE": "capability >= theta = 0.85 on the unseen criterion of the registered ecology",
}


# ------------------------------------------------------------------------------------------------------ enumeration
def _ports(kind):
    return morph.KINDS[kind][1]


def _out_type(kind):
    return morph.KINDS[kind][2]


def _multisets(n_fill):
    """every multiset of n_fill filler kinds, with the at-most-once kinds respected."""
    for combo in itertools.combinations_with_replacement(FILLERS, n_fill):
        if any(combo.count(k) > 1 for k in AT_MOST_ONCE): continue
        yield combo


def _wirings(kinds):
    """every forward-only typed wiring of the slot sequence `kinds` in which every input port is bound and no node is dead.

    Slots are 0..n-1 and every edge runs from a lower slot to a higher one, so the graph is acyclic by construction and
    every DAG over these kinds appears under at least one slot order; isomorphic duplicates are removed afterwards by the
    canonical fingerprint. The search is depth first over nodes with two exact prunes: a port whose type no earlier slot
    produces kills the branch immediately, and a branch is abandoned as soon as the number of earlier nodes still lacking
    a consumer exceeds the number of input ports left in the remaining slots."""
    n = len(kinds)
    needs_consumer = [i for i in range(n) if kinds[i] != "OUTPUT" and morph.CLASS_OF[kinds[i]] != "U"]
    ports_left_from = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        ports_left_from[i] = ports_left_from[i + 1] + len(_ports(kinds[i]))
    srcs_by_slot = []
    for i, k in enumerate(kinds):
        per_port = []
        for t in _ports(k):
            cand = [j for j in range(i) if _out_type(kinds[j]) == t]
            if not cand: return
            per_port.append(cand)
        srcs_by_slot.append(per_port)

    edges = []
    used = [False] * n

    def walk(i):
        if i == n:
            if all(used[j] for j in needs_consumer): yield list(edges)
            return
        pending = sum(1 for j in needs_consumer if j < i and not used[j])
        if pending > ports_left_from[i]: return
        per_port = srcs_by_slot[i]
        if not per_port:
            yield from walk(i + 1); return
        for choice in itertools.product(*per_port):
            flipped = []
            for pt, src in enumerate(choice):
                edges.append((str(src), str(i), pt))
                if not used[src]: used[src] = True; flipped.append(src)
            yield from walk(i + 1)
            for src in flipped: used[src] = False
            del edges[len(edges) - len(choice):]

    yield from walk(0)


def _alive(kinds, edges):
    """the declared no-dead-node filter, re-checked on the finished genotype."""
    outdeg = {i: 0 for i in range(len(kinds))}
    for a, b, _ in edges: outdeg[int(a)] += 1
    for i, k in enumerate(kinds):
        if k == "OUTPUT" or morph.CLASS_OF[k] == "U": continue
        if outdeg[i] == 0: return False
    return True


def enumerate_size(n, budget_s=None, t0=None):
    """every type-correct, servable genotype of exactly n nodes over SIGMA, as (fingerprint, genotype) pairs, plus the
    configuration count. Returns (n_typed, {fingerprint: genotype}, completed)."""
    n_typed = 0; forms = {}
    for fill in _multisets(n - 2):
        # the OUTPUT must be able to sit last: place INPUT first and OUTPUT last, fillers in between in every order that
        # the slot ordering can realize. Distinct orders of the same multiset are distinct slot assignments.
        for perm in set(itertools.permutations(fill)):
            kinds = ("INPUT",) + perm + ("OUTPUT",)
            for edges in _wirings(kinds):
                if not _alive(kinds, edges): continue
                g = morph.make({i: (k, SIGMA[k]) for i, k in enumerate(kinds)}, edges)
                try:
                    morph.typecheck(g)
                except morph.MorphError:
                    continue
                n_typed += 1
                fp = morph.fingerprint(g)
                if fp not in forms: forms[fp] = g
        if budget_s is not None and t0 is not None and time.time() - t0 > budget_s:
            return n_typed, forms, False
    return n_typed, forms, True


# ---------------------------------------------------------------------------------------------------- response class
def _target():
    return smooth.make_target(ECOLOGY["coeffs"])


def response_of(g):
    """the developmental response R_{E,J} of a genotype on the registered ecology: the served trace over the protocol,
    plus the capability and the property vector. Returns None if the genotype cannot be executed at all."""
    target = _target(); basis = bases.ALL[ECOLOGY["column"]]
    M = Machine(basis, seed=ECOLOGY["seed"])
    try:
        vm = VM(g, M, seed=ECOLOGY["seed"])
        M.phase("exec"); vm.init()
        M.phase("exec"); trace = [tuple(_served(vm, x) for x in smooth.ALL_X)]
        for t in range(1, ECOLOGY["n_events"] + 1):
            x = smooth.TRAIN[(t - 1) % len(smooth.TRAIN)]; y = target[x]
            M.phase("upd"); vm.feedback(x, y); M.end_event()
            M.phase("exec"); trace.append(tuple(_served(vm, xx) for xx in smooth.ALL_X))
    except Exception:                                    # noqa: BLE001 - an unrunnable genotype is data, not a crash
        return None
    final = trace[-1]
    err = sum(abs((final[x] if final[x] is not None else 0) - target[x]) for x in smooth.UNSEEN) / FX_ONE / len(smooth.UNSEEN)
    cap = round(max(0.0, 1 - err / 1.5), 4)
    props = {
        "P1_DISTINGUISHES": len({v for v in final}) > 1,
        "P2_LEARNS": final != trace[0],
        "P3_GENERALIZES": any(final[x] == target[x] for x in smooth.UNSEEN),
        "P4_ADMISSIBLE": cap >= ECOLOGY["theta"],
    }
    return {"response": trace, "capability": cap, "properties": props}


def _served(vm, x):
    """the served answer, or None when the genotype abstains (no value reaches the OUTPUT)."""
    v = vm.query(x)
    return None if vm.abstained else int(v)


# ------------------------------------------------------------------------------------ obstruction diagnostics
DEV_LENGTHS = (8, 16, 32)            # declared: is an obstruction a SIZE bound or a development-length bound?
K_VARIANTS = (1, 3, 5)               # declared: NEAREST's k, the one SIGMA parameter the registered memory carrier tunes
METRIC_VARIANTS = (0, 1)


def capability_of(g, n_events):
    """capability on the registered ecology at a declared development length; None if the genotype cannot run."""
    target = _target(); M = Machine(bases.ALL[ECOLOGY["column"]], seed=ECOLOGY["seed"])
    try:
        vm = VM(g, M, seed=ECOLOGY["seed"]); M.phase("exec"); vm.init()
        for t in range(1, n_events + 1):
            x = smooth.TRAIN[(t - 1) % len(smooth.TRAIN)]
            M.phase("upd"); vm.feedback(x, target[x]); M.end_event()
        M.phase("exec"); final = {xx: _served(vm, xx) for xx in smooth.ALL_X}
    except Exception:                                    # noqa: BLE001
        return None
    err = sum(abs((final[x] if final[x] is not None else 0) - target[x]) for x in smooth.UNSEEN) / FX_ONE / len(smooth.UNSEEN)
    return {"n_events": n_events, "capability": round(max(0.0, 1 - err / 1.5), 4),
            "exact_on_unseen": sum(1 for x in smooth.UNSEEN if final[x] == target[x])}


def diagnose(g):
    """two declared diagnostics on one genotype, reported and never used to rescue a clause.

    (a) DEVELOPMENT LENGTH: capability at 8, 16 and 32 events. A ceiling that does not move with development length is a
        size/alphabet bound; one that does is a development-length bound wearing a size bound's clothes.
    (b) ALPHABET PARAMETER: the same structure with NEAREST's k and metric varied off their frozen SIGMA values. Every
        obstruction here is relative to SIGMA, and this says how much of it is the structure and how much is one frozen
        parameter (GMI-DA1: what exists is a property of the alphabet)."""
    out = {"by_development_length": [capability_of(g, n) for n in DEV_LENGTHS], "by_alphabet_parameter": []}
    near = [i for i, (k, _) in g["nodes"].items() if k == "NEAREST"]
    if not near: return out
    for k in K_VARIANTS:
        for m in METRIC_VARIANTS:
            nodes = {i: (kk, dict(pp)) for i, (kk, pp) in g["nodes"].items()}
            for i in near: nodes[i] = ("NEAREST", {"k": k, "metric": m})
            gv = {"nodes": nodes, "edges": list(g["edges"]), "meta": dict(g["meta"])}
            c = capability_of(gv, ECOLOGY["n_events"])
            out["by_alphabet_parameter"].append({"k": k, "metric": m, "in_sigma": (k == SIGMA["NEAREST"]["k"] and m == SIGMA["NEAREST"]["metric"]),
                                                 "capability": None if c is None else c["capability"],
                                                 "admissible": None if c is None else c["capability"] >= ECOLOGY["theta"]})
    return out


# ------------------------------------------------------------------------------------------------------------ driver
def main(max_size=7, budget_s=1800, tag="V1"):
    t0 = time.time()
    sizes = {}; witnesses = {p: None for p in PROPERTY_VECTOR}; largest_exact = 0
    for n in range(3, max_size + 1):
        n_typed, forms, complete = enumerate_size(n, budget_s=budget_s, t0=t0)
        entry = {"n_nodes": n, "type_correct_genotypes": n_typed, "canonical_forms": len(forms),
                 "enumeration_complete": complete}
        if not complete:
            entry["note"] = ("enumeration budget exhausted at this size: the counts above are LOWER BOUNDS and no "
                             "obstruction is claimed at this size or above")
            sizes[n] = entry
            break
        resp = {}; runnable = 0; props_here = {p: [] for p in PROPERTY_VECTOR}; best = (None, None)
        for fp, g in forms.items():
            r = response_of(g)
            if r is None: continue
            runnable += 1
            key = sha256_of(r["response"])
            if key not in resp: resp[key] = {"fingerprint": fp, "capability": r["capability"], "properties": r["properties"]}
            if best[0] is None or r["capability"] > best[0]: best = (r["capability"], fp)
            for p, v in r["properties"].items():
                if v: props_here[p].append(fp)
        if best[1] is not None:
            bg = forms[best[1]]
            entry["best_capability_form"] = {"fingerprint": best[1], "capability": best[0],
                                             "kinds": sorted(k for k, _ in bg["nodes"].values()),
                                             "genotype": morph.to_json(bg), "diagnostics": diagnose(bg)}
        entry.update({"runnable_forms": runnable, "response_classes": len(resp),
                      "forms_realizing": {p: len(v) for p, v in props_here.items()},
                      "best_capability": max((v["capability"] for v in resp.values()), default=0.0)})
        for p in PROPERTY_VECTOR:
            if witnesses[p] is None and props_here[p]:
                witnesses[p] = {"size": n, "fingerprint": props_here[p][0],
                                "genotype": morph.to_json(forms[props_here[p][0]])}
        sizes[n] = entry
        largest_exact = n
        if time.time() - t0 > budget_s:
            break

    # ------------------------------------------------------------------- the obstruction results, stated exactly
    obstructions = []
    for p, text in sorted(PROPERTY_VECTOR.items()):
        w = witnesses[p]
        if w is not None:
            obstructions.append({
                "property": p, "statement_kind": "EXACT_LOWER_BOUND",
                "result": f"no genotype of size at most {w['size'] - 1} over this alphabet realizes {p}; size {w['size']} does",
                "minimum_realizing_size": w["size"], "witness_fingerprint": w["fingerprint"],
                "witness_genotype": w["genotype"],
                "proof": f"exhaustive enumeration of every type-correct servable genotype of sizes 3..{w['size']} over the "
                         f"declared alphabet, each executed on the registered ecology; none below size {w['size']} realizes "
                         f"the property and at least one at size {w['size']} does"})
        else:
            obstructions.append({
                "property": p, "statement_kind": "EXACT_LOWER_BOUND",
                "result": f"no genotype of size at most {largest_exact} over this alphabet realizes {p}",
                "minimum_realizing_size": None, "witness_fingerprint": None,
                "proof": f"exhaustive enumeration of every type-correct servable genotype of sizes 3..{largest_exact} over "
                         f"the declared alphabet, each executed on the registered ecology; none realizes the property. This "
                         f"is a non-existence result over the enumerated sizes, not a failure to find one",
                "not_a_result_if_misread": f"it does NOT say the property is unrealizable: it says the minimum realizing "
                                           f"size over this alphabet is at least {largest_exact + 1}"})

    receipt = {
        "schema": "StageG8SizeCensusLowerBoundsV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": 422,
        "revival_record": "RV-377-069", "gap": "G8", "run_tag": tag,
        "alphabet_sigma": SIGMA, "n_kinds": len(SIGMA), "fillers": list(FILLERS), "at_most_once": list(AT_MOST_ONCE),
        "servability_filter": SERVABILITY,
        "ecology": {k: (list(v) if isinstance(v, tuple) else v) for k, v in ECOLOGY.items()},
        "property_vector": PROPERTY_VECTOR,
        "counts_by_size": sizes,
        "largest_size_enumerated_exactly": largest_exact,
        "obstructions": obstructions,
        "obstruction_diagnostics_note":
            "each size's best-capability form carries two declared diagnostics under counts_by_size[...].best_capability_form."
            "diagnostics. They are REPORTED, never used to rescue a clause: (a) capability at 8, 16 and 32 development "
            "events, which separates a size/alphabet bound from a development-length bound, and (b) the same structure with "
            "NEAREST's k and metric varied off their frozen SIGMA values, which says how much of an obstruction is the "
            "structure and how much is one frozen parameter",
        "three_counts_are_three_things": {
            "type_correct_genotypes": "CONFIGURATIONS: (slot -> kind) assignments with a typed wiring under the declared "
                                      "slot order. This is a configuration count. It is NOT a count of forms and it is NOT "
                                      "a species count",
            "canonical_forms": "ISOMORPHISM CLASSES of typed parameterized port graphs (morph.fingerprint). This is the "
                               "count of distinct FORMS over the alphabet at that size. It is still not a species count: a "
                               "species-level claim would need a developmental-equivalence and a reproduction criterion, "
                               "neither of which a static enumeration supplies",
            "response_classes": "distinct developmental responses R_{E,J} on the registered ecology. Two forms in one "
                                "response class are developmentally indistinguishable ON THAT ECOLOGY, which is weaker "
                                "than bounded reduction and weaker still than being the same species",
            "nesting": "response classes <= canonical forms <= type-correct genotypes, at every size"},
        "claim_ceiling": "every count and every obstruction is relative to the declared alphabet SIGMA with its frozen "
                         "parameter values, the declared servability filter, and the registered ecology. Enlarging the "
                         "alphabet, changing a parameter, relaxing servability or changing the ecology changes every number "
                         "here. The bounds are exact over what was enumerated and say nothing about larger sizes",
    }
    receipt["elapsed_s"] = round(time.time() - t0, 1)
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k not in ("receipt_sha256", "elapsed_s")})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_G8_SIZE_CENSUS_LOWER_BOUNDS_{tag}.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    import sys
    rc = main(max_size=int(sys.argv[1]) if len(sys.argv) > 1 else 7,
              budget_s=float(sys.argv[2]) if len(sys.argv) > 2 else 1800)
    print("receipt", rc["receipt_sha256"][:16], "elapsed", rc["elapsed_s"], "s")
    for n, e in sorted(rc["counts_by_size"].items()):
        print(f"  size {n}: typed {e['type_correct_genotypes']:>9}  forms {e['canonical_forms']:>8}  "
              f"responses {e.get('response_classes', '-'):>6}  best cap {e.get('best_capability', '-')}  "
              f"complete {e['enumeration_complete']}")
    for o in rc["obstructions"]:
        print(f"  {o['property']:18s} min size {o['minimum_realizing_size']}  {o['result']}")
