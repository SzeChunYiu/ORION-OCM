"""D22 heterogeneous-logic transport lab (OW7 + derived finite fragments).

Protocol frozen in D21_D22_PROTOCOL_V1.md before this file existed. Everything is
finite and exhaustively enumerated: no solver, no Lean, no SMT. N4 stays LOCKED.

Institution shape (Goguen-Burstall, concretised finitely):
  Sen   a frozen finite sentence set
  Mod   a frozen finite model set
  |=    a decidable satisfaction relation

Comorphism (alpha, beta):
  alpha  Sen(I) -> Sen(J)
  beta   Mod(J) -> Mod(I)
satisfaction condition   M' |=_J alpha(phi)  <=>  beta(M') |=_I phi     (T84)
preservation             Gamma |=_I phi      =>   alpha(Gamma) |=_J alpha(phi)
reflection               the converse, which needs beta model-expansive (T85)
"""
from __future__ import annotations
import itertools
import time

from . import worlds as W

# ------------------------------------------------------------- institution --
class Institution:
    def __init__(self, name, sentences, models, sat, describe=repr, show=repr):
        self.name = name
        self.sentences = tuple(sentences)
        self.models = tuple(models)
        self.sat = sat
        self.describe = describe          # renders a MODEL
        self.show = show                  # renders a SENTENCE

    def mod(self, phi):
        return frozenset(m for m in self.models if self.sat(m, phi))

class Comorphism:
    def __init__(self, name, src, tgt, alpha, beta, target_models=None, expect=None):
        self.name = name
        self.src, self.tgt = src, tgt
        self.alpha, self.beta = alpha, beta
        self.target_models = tuple(tgt.models if target_models is None else target_models)
        self.expect = expect or {}

# ------------------------------------------------- exhaustive premise sets --
def achievable_premise_sets(inst, cap=4096):
    """Every model set expressible as Mod(Gamma) for some Gamma subseteq Sen.

    Semantic consequence depends on Gamma only through Mod(Gamma), and
    Mod(Gamma) = intersection of Mod(phi) over phi in Gamma. So the intersection
    closure of {Mod(phi)} together with Mod(empty) = Mod is EXACTLY the set of
    achievable premise sets. Quantifying over it is therefore exhaustive over all
    Gamma, not a sample of them. Returns [(gamma_sentences, model_set)].
    """
    base = {frozenset(inst.models): ()}
    for phi in inst.sentences:
        m = inst.mod(phi)
        if m not in base:
            base[m] = (phi,)
    frontier = dict(base)
    while frontier and len(base) < cap:
        nxt = {}
        for ms, g in frontier.items():
            for phi in inst.sentences:
                inter = ms & inst.mod(phi)
                if inter not in base:
                    nxt[inter] = g + (phi,)
                    base[inter] = g + (phi,)
                    if len(base) >= cap:
                        break
            if len(base) >= cap:
                break
        frontier = nxt
    return [(g, ms) for ms, g in base.items()], len(base) < cap

# ------------------------------------------------------------------- tests --
def t_sat(com, max_witnesses=3):
    """Satisfaction condition, exhaustively over every (target model, sentence)."""
    checked, n_bad, bad = 0, 0, []
    for mp in com.target_models:
        bm = com.beta(mp)
        for phi in com.src.sentences:
            checked += 1
            lhs = com.tgt.sat(mp, com.alpha(phi))
            rhs = com.src.sat(bm, phi)
            if lhs != rhs:
                n_bad += 1                       # true count, never capped
                if len(bad) < max_witnesses:
                    bad.append({"target_model": com.tgt.describe(mp),
                                "beta_model": com.src.describe(bm),
                                "sentence": com.src.show(phi),
                                "target_sat_alpha_phi": lhs, "source_sat_phi": rhs})
    return {"n_pairs_checked": checked, "n_violations": n_bad,
            "holds": n_bad == 0, "witnesses_shown": bad,
            "n_witnesses_shown": len(bad), "witness_display_cap": max_witnesses,
            "coverage": "EXHAUSTIVE"}

def t_exp(com):
    """Model-expansiveness: is beta surjective onto Mod(I)?"""
    image = {com.beta(mp) for mp in com.target_models}
    missing = [com.src.describe(m) for m in com.src.models if m not in image]
    return {"image_size": len(image), "source_models": len(com.src.models),
            "surjective": not missing, "missing_source_models": missing,
            "coverage": "EXHAUSTIVE"}

def _entails_src(inst, premise_models, phi):
    return all(inst.sat(m, phi) for m in premise_models)

def t_pres_refl(com, premise_sets, max_witnesses=3):
    """Preservation and reflection, exhaustively over achievable Gamma x every phi.

    Target satisfaction is precomputed once per source sentence as an index set over
    the (possibly restricted) target models, so entailment is a subset test rather
    than a rescan. Same quantification, same exhaustiveness, far less time.
    """
    tgt_mask = {}
    for phi in com.src.sentences:
        a = com.alpha(phi)
        tgt_mask[phi] = frozenset(i for i, mp in enumerate(com.target_models)
                                  if com.tgt.sat(mp, a))
    allt = frozenset(range(len(com.target_models)))
    n, pres_bad, refl_bad = 0, [], []
    n_pres_bad, n_refl_bad = 0, 0
    for gamma, pmods in premise_sets:
        g_models = allt
        for g in gamma:
            g_models &= tgt_mask[g]
        for phi in com.src.sentences:
            n += 1
            src_ent = _entails_src(com.src, pmods, phi)
            tgt_ent = g_models <= tgt_mask[phi]
            if src_ent and not tgt_ent:
                n_pres_bad += 1                  # true count, never capped
                if len(pres_bad) < max_witnesses:
                    pres_bad.append({"gamma": [com.src.show(g) for g in gamma],
                                     "phi": com.src.show(phi)})
            if tgt_ent and not src_ent:
                n_refl_bad += 1                  # true count, never capped
                if len(refl_bad) < max_witnesses:
                    cm = [com.src.describe(m) for m in pmods if not com.src.sat(m, phi)]
                    refl_bad.append({"gamma": [com.src.show(g) for g in gamma],
                                     "phi": com.src.show(phi),
                                     "source_counter_models": cm[:3]})
    return {"n_pairs_checked": n,
            "preservation_holds": n_pres_bad == 0,
            "n_preservation_violations": n_pres_bad,
            "preservation_witnesses_shown": pres_bad,
            "reflection_holds": n_refl_bad == 0,
            "n_reflection_violations": n_refl_bad,
            "reflection_witnesses_shown": refl_bad,
            "witness_display_cap": max_witnesses,
            "coverage": "EXHAUSTIVE over achievable premise sets"}

def run_comorphism(com):
    t0 = time.process_time()
    ps, complete = achievable_premise_sets(com.src)
    sat = t_sat(com)
    exp = t_exp(com)
    pr = t_pres_refl(com, ps)
    alarms = []
    if not sat["holds"]:
        alarms.append("T-SAT")
    if not exp["surjective"]:
        alarms.append("T-EXP")
    if not pr["preservation_holds"]:
        alarms.append("T-PRES")
    if not pr["reflection_holds"]:
        alarms.append("T-REFL")
    got = {"T-SAT": sat["holds"], "T-EXP": exp["surjective"],
           "T-PRES": pr["preservation_holds"], "T-REFL": pr["reflection_holds"]}
    matches = all(got[k] == v for k, v in com.expect.items()) if com.expect else None
    return {"comorphism": com.name, "source": com.src.name, "target": com.tgt.name,
            "n_source_sentences": len(com.src.sentences),
            "n_source_models": len(com.src.models),
            "n_target_models": len(com.target_models),
            "n_achievable_premise_sets": len(ps),
            "premise_enumeration_complete": complete,
            "t_sat": sat, "t_exp": exp, "t_pres_refl": pr,
            "alarms": alarms, "n_alarms": len(alarms),
            "expected": com.expect, "observed": got, "expectation_met": matches,
            "cpu_s": round(time.process_time() - t0, 4)}

# ------------------------------------------------------- propositional core --
def peval(f, val):
    k = f[0]
    if k == "atom":
        return bool(val[f[1]])
    if k == "not":
        return not peval(f[1], val)
    if k == "and":
        return peval(f[1], val) and peval(f[2], val)
    if k == "or":
        return peval(f[1], val) or peval(f[2], val)
    if k == "imp":
        return (not peval(f[1], val)) or peval(f[2], val)
    if k == "true":
        return True
    if k == "false":
        return False
    raise KeyError(k)

def pshow(f):
    k = f[0]
    if k == "atom":
        return f[1]
    if k == "not":
        return "~" + pshow(f[1])
    if k == "true":
        return "T"
    if k == "false":
        return "F"
    op = {"and": "&", "or": "|", "imp": "->"}[k]
    return f"({pshow(f[1])}{op}{pshow(f[2])})"

def subst(f, mapping):
    """Structural extension of an atom translation to all connectives."""
    k = f[0]
    if k == "atom":
        return mapping[f[1]]
    if k in ("true", "false"):
        return f
    if k == "not":
        return ("not", subst(f[1], mapping))
    return (k, subst(f[1], mapping), subst(f[2], mapping))

def _dnf(atoms, rows):
    if not rows:
        return ("false",)
    disj = None
    for row in rows:
        conj = None
        for a, v in zip(atoms, row):
            lit = ("atom", a) if v else ("not", ("atom", a))
            conj = lit if conj is None else ("and", conj, lit)
        disj = conj if disj is None else ("or", disj, conj)
    return disj

def all_truth_functions(atoms):
    """Every sentence over `atoms` up to logical equivalence, in canonical DNF.

    Exhaustive by construction: each propositional sentence over these atoms is
    logically equivalent to exactly one member.
    """
    valuations = [tuple(r) for r in itertools.product((0, 1), repeat=len(atoms))]
    out = []
    for k in range(len(valuations) + 1):
        for rows in itertools.combinations(valuations, k):
            out.append(_dnf(atoms, rows))
    return out

def _prop_inst(name, atoms, models):
    def sat(m, phi):
        return peval(phi, dict(zip(atoms, m)))
    return Institution(name, all_truth_functions(atoms), models, sat,
                       describe=lambda m: "".join(str(b) for b in m), show=pshow)

# ------------------------------------------------------------ L1 (frozen OW7)
L1_ATOMS = ("p", "q")
J1_ATOMS = ("p1", "q1", "e")
ALPHA_FROZEN = {"p": ("atom", "p1"),
                "q": ("and", ("atom", "p1"), ("atom", "q1"))}   # frozen ow7 translation
ALPHA_ID = {"p": ("atom", "p1"), "q": ("atom", "q1")}

def _beta_drop(mp):
    return (mp[0], mp[1])

def _beta_induced(tgt, alpha_map, atoms):
    def beta(mp):
        return tuple(int(tgt.sat(mp, subst(("atom", a), alpha_map))) for a in atoms)
    return beta

def l1_arms(world):
    src = _prop_inst("L1-prop{p,q}", L1_ATOMS, [tuple(m) for m in world["imodels"]])
    tgt = _prop_inst("J1-prop{p',q',e}", J1_ATOMS, [tuple(m) for m in world["jmodels"]])
    a_frozen = lambda f: subst(f, ALPHA_FROZEN)
    a_id = lambda f: subst(f, ALPHA_ID)
    b_ind_frozen = _beta_induced(tgt, ALPHA_FROZEN, L1_ATOMS)
    b_ind_id = _beta_induced(tgt, ALPHA_ID, L1_ATOMS)
    restricted = [m for m in tgt.models if m[0] == 1]
    return [
        Comorphism("L1-CLEAN", src, tgt, a_id, b_ind_id,
                   expect={"T-SAT": True, "T-EXP": True,
                           "T-PRES": True, "T-REFL": True}),
        Comorphism("L1-HOSTILE-SAT", src, tgt, a_frozen, _beta_drop,
                   expect={"T-SAT": False}),
        Comorphism("L1-HOSTILE-IMAGE-frozen-alpha", src, tgt, a_frozen, b_ind_frozen,
                   expect={"T-SAT": True, "T-EXP": False,
                           "T-PRES": True, "T-REFL": False}),
        Comorphism("L1-HOSTILE-IMAGE-restricted", src, tgt, a_id, b_ind_id,
                   target_models=restricted,
                   expect={"T-SAT": True, "T-EXP": False,
                           "T-PRES": True, "T-REFL": False}),
    ]

def ow7_surjectivity_note(worlds):
    """Pre-registered check: does removing (0,0,1) break the drop-extra reduct?

    The protocol recorded before running that it does not, because (0,0,0) still
    maps onto (0,0). This verifies that claim on every frozen world instead of
    asserting it.
    """
    rows = []
    for w in worlds:
        img = {_beta_drop(tuple(m)) for m in w["jmodels"]}
        missing = [m for m in w["imodels"] if tuple(m) not in img]
        rows.append({"world": w["id"], "n_jmodels": len(w["jmodels"]),
                     "model_001_removed": (0, 0, 1) not in
                                          [tuple(m) for m in w["jmodels"]],
                     "drop_reduct_surjective": not missing,
                     "missing": [list(m) for m in missing]})
    return {"rows": rows,
            "all_surjective": all(r["drop_reduct_surjective"] for r in rows),
            "pre_registered_claim": "removing (0,0,1) does NOT break surjectivity of the "
                                    "drop-extra reduct because (0,0,0) still maps onto (0,0)",
            "claim_verified": all(r["drop_reduct_surjective"] for r in rows)}

# ------------------------------------------------------------------ L2 Horn --
L2_ATOMS = ("p", "q", "r")
L2X_ATOMS = ("p", "q", "r", "s")

def horn_sentences(atoms=L2_ATOMS):
    """All definite Horn clauses body -> head with |body| <= 2, plus the facts."""
    out = []
    for head in atoms:
        for k in (0, 1, 2):
            for body in itertools.combinations(atoms, k):
                if not body:
                    out.append(("atom", head))
                    continue
                b = None
                for a in body:
                    lit = ("atom", a)
                    b = lit if b is None else ("and", b, lit)
                out.append(("imp", b, ("atom", head)))
    return out

def _val_inst(name, atoms, models, sentences):
    return Institution(name, sentences, models,
                       lambda m, phi: peval(phi, dict(zip(atoms, m))),
                       describe=lambda m: "".join(str(b) for b in m), show=pshow)

def l2_arms():
    models = [tuple(v) for v in itertools.product((0, 1), repeat=3)]
    xmodels = [tuple(v) for v in itertools.product((0, 1), repeat=4)]
    src = _val_inst("L2-Horn{p,q,r}", L2_ATOMS, models, horn_sentences())
    tgt = _val_inst("L2x-Horn{p,q,r,s}", L2X_ATOMS, xmodels, horn_sentences(L2X_ATOMS))
    a_id = lambda f: f                        # atoms carry over unchanged
    beta = lambda mp: mp[:3]
    restricted = [m for m in xmodels if m[0] == 1]
    return [
        Comorphism("L2-CLEAN", src, tgt, a_id, beta,
                   expect={"T-SAT": True, "T-EXP": True,
                           "T-PRES": True, "T-REFL": True}),
        Comorphism("L2-HOSTILE-IMAGE", src, tgt, a_id, beta, target_models=restricted,
                   expect={"T-SAT": True, "T-EXP": False,
                           "T-PRES": True, "T-REFL": False}),
    ]

# ----------------------------------------------------------- L3 equational --
L3_TERMS = ("x", "y", ("f", "x", "x"), ("f", "x", "y"), ("f", "y", "x"), ("f", "y", "y"))

def _teval(t, table, env):
    if isinstance(t, str):
        return env[t]
    return table[_teval(t[1], table, env) * 2 + _teval(t[2], table, env)]

def _tshow(t):
    return t if isinstance(t, str) else f"f({_tshow(t[1])},{_tshow(t[2])})"

def _eqshow(eq):
    return _tshow(eq[0]) + " = " + _tshow(eq[1])

def l3_sentences():
    return [(a, b) for i, a in enumerate(L3_TERMS) for b in L3_TERMS[i + 1:]]

def _l3_sat(table, eq):
    return all(_teval(eq[0], table, {"x": x, "y": y})
               == _teval(eq[1], table, {"x": x, "y": y})
               for x in (0, 1) for y in (0, 1))

def l3_arms():
    tables = [tuple(v) for v in itertools.product((0, 1), repeat=4)]
    src = Institution("L3-equational(1 binary op on {0,1})", l3_sentences(), tables,
                      _l3_sat, describe=lambda m: "f=" + "".join(str(b) for b in m),
                      show=_eqshow)
    xmodels = [t + (c,) for t in tables for c in (0, 1)]      # add an unused constant
    tgt = Institution("L3x-equational + constant", l3_sentences(), xmodels,
                      lambda m, eq: _l3_sat(m[:4], eq),
                      describe=lambda m: "f=" + "".join(str(b) for b in m[:4]) + f",c={m[4]}",
                      show=_eqshow)
    a_id = lambda f: f
    beta = lambda mp: mp[:4]
    commutative = [m for m in xmodels if m[1] == m[2]]        # f(0,1) == f(1,0)
    return [
        Comorphism("L3-CLEAN", src, tgt, a_id, beta,
                   expect={"T-SAT": True, "T-EXP": True,
                           "T-PRES": True, "T-REFL": True}),
        Comorphism("L3-HOSTILE-IMAGE", src, tgt, a_id, beta, target_models=commutative,
                   expect={"T-SAT": True, "T-EXP": False,
                           "T-PRES": True, "T-REFL": False}),
    ]

# ------------------------------------------- L4 first-order finite fragment --
def _reval(b, rel, env):
    k = b[0]
    if k == "R":
        return bool(rel[env[b[1]] * 2 + env[b[2]]])
    if k == "not":
        return not _reval(b[1], rel, env)
    if k == "and":
        return _reval(b[1], rel, env) and _reval(b[2], rel, env)
    if k == "or":
        return _reval(b[1], rel, env) or _reval(b[2], rel, env)
    if k == "imp":
        return (not _reval(b[1], rel, env)) or _reval(b[2], rel, env)
    raise KeyError(k)

_CONN = {"and": "&", "or": "|", "imp": "->"}

def _rshow(b):
    k = b[0]
    if k == "R":
        return "R(" + b[1] + "," + b[2] + ")"
    if k == "not":
        return "~" + _rshow(b[1])
    return "(" + _rshow(b[1]) + _CONN[k] + _rshow(b[2]) + ")"

_L4_ATOMS = (("R", "x", "x"), ("R", "x", "y"), ("R", "y", "x"), ("R", "y", "y"))
_L4_BODIES = (list(_L4_ATOMS)
              + [("not", a) for a in _L4_ATOMS]
              + [("imp", ("R", "x", "y"), ("R", "y", "x")),
                 ("and", ("R", "x", "y"), ("R", "y", "x")),
                 ("and", ("R", "x", "x"), ("R", "y", "y")),
                 ("or", ("not", ("R", "x", "y")), ("R", "y", "x"))])

def l4_sentences():
    return [("Q", q1, q2, b) for q1 in ("A", "E") for q2 in ("A", "E")
            for b in _L4_BODIES]

def _l4_sat(rel, s):
    _, q1, q2, body = s
    def inner(x):
        vals = [_reval(body, rel, {"x": x, "y": y}) for y in (0, 1)]
        return all(vals) if q2 == "A" else any(vals)
    vals = [inner(x) for x in (0, 1)]
    return all(vals) if q1 == "A" else any(vals)

def _l4_show(s):
    return f"{'forall' if s[1]=='A' else 'exists'}x.{'forall' if s[2]=='A' else 'exists'}y.{_rshow(s[3])}"

def l4_arms():
    rels = [tuple(v) for v in itertools.product((0, 1), repeat=4)]
    src = Institution("L4-FO(1 binary relation, |U|=2)", l4_sentences(), rels, _l4_sat,
                      describe=lambda m: "R=" + "".join(str(b) for b in m), show=_l4_show)
    xmodels = [(r, sr) for r in rels for sr in rels]           # add a second relation S
    tgt = Institution("L4x-FO(R and S)", l4_sentences(), xmodels,
                      lambda m, s: _l4_sat(m[0], s),
                      describe=lambda m: "R=" + "".join(str(b) for b in m[0])
                                         + ",S=" + "".join(str(b) for b in m[1]),
                      show=_l4_show)
    a_id = lambda f: f
    beta = lambda mp: mp[0]
    reflexive = [m for m in xmodels if m[0][0] == 1 and m[0][3] == 1]
    return [
        Comorphism("L4-CLEAN", src, tgt, a_id, beta,
                   expect={"T-SAT": True, "T-EXP": True,
                           "T-PRES": True, "T-REFL": True}),
        Comorphism("L4-HOSTILE-IMAGE", src, tgt, a_id, beta, target_models=reflexive,
                   expect={"T-SAT": True, "T-EXP": False,
                           "T-PRES": True, "T-REFL": False}),
    ]

def preregistered_witness_check(worlds):
    """Check the EXACT witness the protocol named, not merely 'some violation'.

    Protocol section 2.3 registered, before running, that HOSTILE-SAT must fail at
    target model (p1=0, q1=1, e) on the sentence q. A capped witness list can hide
    that specific pair behind other violations, so it is searched for by name.
    """
    rows = []
    for w in worlds:
        src = _prop_inst("L1", L1_ATOMS, [tuple(m) for m in w["imodels"]])
        tgt = _prop_inst("J1", J1_ATOMS, [tuple(m) for m in w["jmodels"]])
        want = frozenset(m for m in src.models if m[1] == 1)          # Mod(q)
        q_sent = next((phi for phi in src.sentences if src.mod(phi) == want), None)
        if q_sent is None:
            rows.append({"world": w["id"], "status": "CANNOT_CHECK: no sentence for q"})
            continue
        hits = []
        for mp in tgt.models:
            if mp[0] != 0 or mp[1] != 1:
                continue
            lhs = tgt.sat(mp, subst(q_sent, ALPHA_FROZEN))
            rhs = src.sat(_beta_drop(mp), q_sent)
            if lhs != rhs:
                hits.append({"target_model": "".join(str(b) for b in mp),
                             "beta_model": "".join(str(b) for b in _beta_drop(mp)),
                             "target_sat_alpha_q": lhs, "source_sat_q": rhs})
        rows.append({"world": w["id"], "sentence": pshow(q_sent),
                     "registered_witness_found": bool(hits), "hits": hits})
    return {"rows": rows,
            "all_worlds_show_registered_witness":
                all(r.get("registered_witness_found") for r in rows),
            "registered_as": "HOSTILE-SAT fails at (p1=0, q1=1, e) on phi = q"}

# ----------------------------------------------------------------- driver ---
def run_d22():
    t0w, t0c = time.time(), time.process_time()
    ow7 = W.ow7_worlds()
    surj = ow7_surjectivity_note(ow7)
    prereg = preregistered_witness_check(ow7)

    results = []
    for w in ow7:
        for com in l1_arms(w):
            r = run_comorphism(com)
            r["world"] = w["id"]
            r["fragment"] = "L1"
            results.append(r)
    for frag, arms in (("L2", l2_arms()), ("L3", l3_arms()), ("L4", l4_arms())):
        for com in arms:
            r = run_comorphism(com)
            r["world"] = frag + "-derived"
            r["fragment"] = frag
            results.append(r)

    clean = [r for r in results if "CLEAN" in r["comorphism"]]
    hostile = [r for r in results if "HOSTILE" in r["comorphism"]]
    sat_host = [r for r in hostile if "HOSTILE-SAT" in r["comorphism"]]
    img_host = [r for r in hostile if "HOSTILE-IMAGE" in r["comorphism"]]

    # F2: preservation must hold wherever the satisfaction condition holds (T85 half 1)
    f2_bad = [r["comorphism"] + "@" + r["world"] for r in results
              if r["observed"]["T-SAT"] and not r["observed"]["T-PRES"]]
    # F3: reflection holds exactly where beta is model-expansive, given T-SAT
    f3_bad = [r["comorphism"] + "@" + r["world"] for r in results
              if r["observed"]["T-SAT"]
              and r["observed"]["T-REFL"] != r["observed"]["T-EXP"]]

    summary = {
        "F1_t_sat_pairs_checked": sum(r["t_sat"]["n_pairs_checked"] for r in results),
        "F1_all_premise_enumerations_complete":
            all(r["premise_enumeration_complete"] for r in results),
        "F1_consequence_pairs_checked":
            sum(r["t_pres_refl"]["n_pairs_checked"] for r in results),
        "F2_preservation_failures_under_satisfying_comorphisms": f2_bad,
        "F3_reflection_expansiveness_mismatches": f3_bad,
        "F4_hostile_sat_fired": all(not r["observed"]["T-SAT"] for r in sat_host)
                                and bool(sat_host),
        "F4_hostile_image_fired": all((not r["observed"]["T-EXP"])
                                      and (not r["observed"]["T-REFL"])
                                      for r in img_host) and bool(img_host),
        "F4_registered_sat_witness_found_on_every_world":
            prereg["all_worlds_show_registered_witness"],
        "F4_total_sat_violations_hostile_sat":
            sum(r["t_sat"]["n_violations"] for r in sat_host),
        "F4_total_reflection_violations_hostile_image":
            sum(r["t_pres_refl"]["n_reflection_violations"] for r in img_host),
        "F4_both_hostiles_fired": (bool(sat_host) and bool(img_host)
                                   and all(not r["observed"]["T-SAT"] for r in sat_host)
                                   and all((not r["observed"]["T-EXP"])
                                           and (not r["observed"]["T-REFL"])
                                           for r in img_host)),
        "F5_clean_alarms": sum(r["n_alarms"] for r in clean),
        "F5_clean_arms": len(clean),
        "n_comorphisms": len(results),
        "n_expectations_met": sum(1 for r in results if r["expectation_met"]),
        "n_expectations_total": len(results),
        "ow7_drop_reduct_surjective_on_all_worlds": surj["all_surjective"],
        "ow7_pre_registered_claim_verified": surj["claim_verified"],
        "n4_lock": "LOCKED: no Lean, no SMT, no solver; z3-solver/python-sat/pysmt "
                   "install on this host and were deliberately not used",
    }
    out = {"experiment": "D22", "evidence_class": "CONFIRMATORY_FIXED",
           "protocol": "D21_D22_PROTOCOL_V1.md",
           "worlds": "OW7 (frozen, SEED 20260910) + derived L2/L3/L4 fragments",
           "fragments": {"L1": "propositional {p,q}, frozen ow7_worlds models",
                         "L2": "Horn {p,q,r}, 8 valuations, 21 definite clauses",
                         "L3": "equational, one binary op on {0,1}, 16 algebras",
                         "L4": "FO finite-model, one binary relation on |U|=2, "
                               "16 structures, 64 quantified sentences"},
           "ow7_surjectivity": surj, "preregistered_witness": prereg,
           "comorphisms": results, "summary": summary,
           "certificate_ceiling": "P2 finite certificate over enumerated models; "
                                  "never a universal proof",
           "wall_s": round(time.time() - t0w, 3),
           "cpu_s": round(time.process_time() - t0c, 3)}
    receipts = []
    for r in results:
        receipts.append({"job": "D22", "world_id": r["world"], "fragment": r["fragment"],
                         "comorphism": r["comorphism"],
                         "theorem_or_atom_id": "T85" if "IMAGE" in r["comorphism"] else "T84",
                         "observed": r["observed"], "expected": r["expected"],
                         "expectation_met": r["expectation_met"],
                         "alarms": r["alarms"],
                         "t_sat_pairs": r["t_sat"]["n_pairs_checked"],
                         "consequence_pairs": r["t_pres_refl"]["n_pairs_checked"],
                         "premise_enumeration_complete": r["premise_enumeration_complete"],
                         "seed_freeze": W.SEED,
                         "certificate_ceiling": "P2 finite certificate, not universal proof"})
    return out, receipts
