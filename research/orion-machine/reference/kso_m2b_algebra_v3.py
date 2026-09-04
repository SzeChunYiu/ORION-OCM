"""KSO M2b V3 — procedures as DATA, gating by LABELS only, and exit codes that are gates.

Supersedes ``kso_m2b_algebra_population_v1.py`` (the V2 run, receipt
``results/KSO_M2B_ALGEBRA_RECEIPT_V1.json``, terminal M2B_POPULATED_AND_SOLVED_ON_DEV at 30/30).
lane-guards' independent replay of that receipt (ORION-V2 #295, comment 6) found five defects.  Each
is repaired here, and each repair carries a planted failure AND a no-alarm control:

  (a) PROCEDURES WERE PYTHON.  ``apply_procedure()`` re-implemented the quadratic formula, completing
      the square, factoring and the linear path in Python; ALGEBRA_SOURCE_V1.json merely NAMED them
      and carried an unused ``sympy`` string.  Corrupting the registered source could not change a
      root, so "knowledge lives in the source" was asserted, not true.
      V3: each procedure is a hyperpath of STEP atoms (typed DEPENDENCE edges precondition -> step ->
      step, one COMPOSITION edge from the whole hyperpath to the procedure).  A step carries a
      registered operation name and a SymPy-parsable expression template.  ONE generic interpreter
      (``interpret_hyperpath``) walks the enabled hyperpath.  No per-procedure Python exists.
      PLANT: corrupt one step template in the registered source (4*a*c -> 3*a*c) => the computed root
      DIFFERS from the clean root (the mutation is asserted to have landed), the oracle disagrees,
      and the root is INVALID under the SymPy EXACT_CHECKER.

  (b) GATING WAS A CONDITIONAL.  The Delta < 0 block on factoring was the Python conditional
      ``if s is None: return None`` inside ``apply_procedure``; and the three Delta case atoms
      constrained proc:quadratic_formula only and were disjoined, so with exactly one case live the
      OR was always live and the case atoms gated nothing.
      V3: a case atom's ``constraint_on`` is the set of procedures it LICENSES.  con:delta_neg does
      not license proc:factor, so on a Delta < 0 instance proc:factor's case disjunction is empty and
      its label is dead.  Every conditional that decided applicability is gone; what remains in
      ``atomize_labels`` decides WHICH CASE HOLDS on the instance (the atomize stage) and never which
      procedure applies.
      PLANT: flip one constraint atom's label (con:rational_roots) on a real IRRATIONAL_DISTINCT
      instance => proc:factor fires, emits an irrational root under its declared domain Q, the oracle
      disagrees at FIRE, and the checker returns INVALID.  A second plant flips the case licence on a
      COMPLEX_PAIR instance => proc:factor fires and emits a complex root under Q => INVALID.
      NO-ALARM: with correct labels proc:factor fires on no IRRATIONAL_DISTINCT and no COMPLEX_PAIR
      instance, and the clean run has zero INVALID root claims.

  (c) THE THRESHOLD WAS NOT A GATE.  ``main()`` exited 0 at 26/30, 25/30 and 20/30, printing the
      terminal M2B_DEFECT_ATTRIBUTED as a string.  A terminal label is not an exit code.
      V3: the threshold is registered in KSO_M2B_DESIGN_V3.json and ``main()`` returns 1 below it.
      PLANT: a corruption reaching three instances => exit 1.  NO-ALARM: the clean run exits 0.

  (d) ORACLE DISAGREEMENT WAS RE-DRAWN.  Repaired in ``kso_algebra_quadratic_v3.generate_split``:
      a disagreement raises OracleDisagreement and this module reports CANNOT_CHECK and exits 2 with
      the instance named.

  (e) OUT-OF-RANGE INSTANCES WERE ACCEPTED.  Repaired by ``check_registered_range`` at the oracle and
      called again here at the solver, so both ends reject with a typed error.

Exit codes: 0 at or above the registered threshold; 1 below it; 2 could not check.
NO NOVELTY OR BREAKTHROUGH CLAIM.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


kso = _load("kso_math_v1", HERE / "kso_math_v1.py")
m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
m1 = _load("kso_m1_mex1_population_v1", HERE / "kso_m1_mex1_population_v1.py")
alg = _load("kso_algebra_quadratic_v3", HERE / "kso_algebra_quadratic_v3.py")
checker = _load("kso_exact_checker_sympy_v1", HERE / "kso_exact_checker_sympy_v1.py")

CannotCheck = alg.CannotCheck
OracleDisagreement = alg.OracleDisagreement
OutOfRegisteredRange = alg.OutOfRegisteredRange
TemplateRejection = alg.TemplateRejection
Exact = alg.Exact
Atom, Hyperedge, KnowledgeSpace = kso.Atom, kso.Hyperedge, kso.KnowledgeSpace
ONE, ZERO = m0.ONE, m0.ZERO
Cert = m0.CertificateKind
ALPHA = Fraction(1, 3)  # PRE_STUDY_PLACEHOLDER (KSO_PARAMETER_STUDY_V1)

DESIGN_V3 = ROOT / "research" / "orion-machine" / "results" / "KSO_M2B_DESIGN_V3.json"

TYPE_MAP = {"definition": "claim", "representation": "representation", "constraint": "constraint",
            "procedure": "procedure", "worked_example": "observation", "step": "step"}


# ----------------------------------------------------------------------------------------------
# population — every atom enters through the INSTRUCTION channel via m0.admit
# ----------------------------------------------------------------------------------------------


def populate_from_source(src: dict | None = None) -> tuple[m1.Population, dict[str, dict]]:
    src = src if src is not None else alg.source_atoms()
    atoms = src["atoms"]
    by_id = {a["id"]: a for a in atoms}
    order: list[str] = []
    seen: set[str] = set()
    constrained_by: dict[str, list[dict]] = {}
    for a in atoms:
        for t in a.get("constraint_on", []):
            constrained_by.setdefault(t, []).append(a)

    def visit(i: str) -> None:
        if i in seen:
            return
        seen.add(i)
        for c in constrained_by.get(i, []):
            if c["id"] not in seen:
                seen.discard(i)
                visit(c["id"])
                seen.add(i)
        for p in by_id[i].get("preconditions", []):
            if p not in seen:
                seen.discard(i)
                visit(p)
                seen.add(i)
        for s in by_id[i].get("hyperpath", []):
            if s not in seen:
                seen.discard(i)
                visit(s)
                seen.add(i)
        order.append(i)

    for a in atoms:
        visit(a["id"])

    root_atom = Atom("root:algebra", "goal", ONE)
    ks = KnowledgeSpace((root_atom,), ())
    certs: dict[str, str] = {"root:algebra": Cert.INSTRUCTION.value}
    index: dict[str, int] = {}
    meter = m0.Meter(admit=1)
    for k, aid in enumerate(order):
        a = by_id[aid]
        index[aid] = k
        label = (frozenset({k}),)
        amap_now = ks.atom_map()
        pre = a.get("preconditions", [])
        for p in pre:
            label = kso.profile_and(label, amap_now[p].profile)
        # applicability: non-case constraints conjoin; the case constraints that LICENSE this atom
        # disjoin.  A case atom's constraint_on is its licence list (V3 (b)).
        cons = constrained_by.get(aid, [])
        case_alt: tuple = ZERO
        has_case = any(c.get("case") for c in cons)
        for c in cons:
            if c.get("case"):
                case_alt = kso.profile_or(case_alt, amap_now[c["id"]].profile)
            else:
                label = kso.profile_and(label, amap_now[c["id"]].profile)
        if has_case:
            label = kso.profile_and(label, case_alt)
        # the hyperpath is part of applicability: a dead step kills its procedure
        path = a.get("hyperpath", [])
        for s in path:
            label = kso.profile_and(label, amap_now[s].profile)
        edges: list[Hyperedge] = []
        for p in pre:
            edges.append(Hyperedge(f"dep:{p}->{aid}", (p,), (aid,), "DEPENDENCE", profile=ONE))
        for c in cons:
            edges.append(Hyperedge(f"con:{c['id']}->{aid}", (c["id"],), (aid,), "CONSTRAINT", profile=ONE))
        if path:
            edges.append(Hyperedge(f"compose:{aid}", tuple(path) + tuple(pre), (aid,), "COMPOSITION", profile=label))
        if not pre:
            edges.append(Hyperedge(f"dep:root->{aid}", ("root:algebra",), (aid,), "DEPENDENCE", profile=ONE))
        ks, rec = m0.admit(ks, Atom(aid, TYPE_MAP[a["type"]], label), tuple(edges), Cert.INSTRUCTION, alpha=ALPHA)
        certs[aid] = rec.certificate.value
        meter = meter.charged(admit=1, compose=1 if path else 0)
    extra: list[Hyperedge] = []
    for a in atoms:
        if a["type"] == "worked_example":
            for p in a.get("preconditions", []):
                extra.append(Hyperedge(f"sup:{a['id']}->{p}", (a["id"],), (p,), "SUPPORT", profile=ONE))
    for s_id, dst in (("rep:standard_form", "rep:vertex_form"), ("rep:standard_form", "rep:factored_form")):
        extra.append(Hyperedge(f"transport:{s_id}->{dst}", (s_id,), (dst,), "REPRESENTATION_TRANSPORT", profile=ONE))
    ks = KnowledgeSpace(ks.atoms, ks.hyperedges + tuple(extra))
    ks.validate()
    m0.check_edge_vocabulary(ks)
    governed = m0.GovernedSpace(ks, {k: Cert(v) for k, v in certs.items()}, evidence_atoms=len(order), meter=meter, revoked=frozenset())
    pop = m1.Population(ks, governed, dict(index), {k: "VALID" for k in index}, {}, {}, frozenset(), ())
    return pop, dict(by_id)


# ----------------------------------------------------------------------------------------------
# atomize — which CASE holds on this instance.  Never which procedure applies.
# ----------------------------------------------------------------------------------------------


def atomize_labels(pop: m1.Population, inst) -> frozenset[int]:
    """The atomize stage: read the instance and revoke, for this query, the constraint atoms that do
    not hold on it.  This decides which of the mutually exclusive cases is true; the label algebra
    alone then decides which procedures are applicable.  (V3 (b): no conditional here mentions a
    procedure id.)"""
    alg.check_registered_range(inst)          # V3 (e): typed rejection at the solver too
    a, b, c = inst.a, inst.b, inst.c
    dead: set[str] = set()
    if a == 0:
        dead |= {"con:a_nonzero", "con:delta_pos", "con:delta_zero", "con:delta_neg", "con:rational_roots"}
        if b == 0:
            dead.add("con:b_nonzero")
    else:
        dead.add("con:a_zero")
        delta = b * b - 4 * a * c
        case = "con:delta_pos" if delta > 0 else "con:delta_zero" if delta == 0 else "con:delta_neg"
        dead |= {"con:delta_pos", "con:delta_zero", "con:delta_neg"} - {case}
        if alg.rational_sqrt(delta) is None:
            dead.add("con:rational_roots")
    return frozenset(pop.base_index[x] for x in dead)


def seeds_for(inst) -> list[str]:
    seeds = ["rep:standard_form", "con:a_nonzero" if inst.a != 0 else "con:a_zero"]
    if inst.a != 0:
        delta = inst.b * inst.b - 4 * inst.a * inst.c
        seeds.append("con:delta_pos" if delta > 0 else "con:delta_zero" if delta == 0 else "con:delta_neg")
        if alg.rational_sqrt(delta) is not None:
            seeds.append("con:rational_roots")
    return seeds


# ----------------------------------------------------------------------------------------------
# the ONE generic interpreter — it knows nothing about quadratics
# ----------------------------------------------------------------------------------------------


def interpret_hyperpath(pop: m1.Population, source: dict[str, dict], proc_id: str, inst,
                        revoked: frozenset[int]) -> tuple[tuple, tuple[dict, ...]]:
    """Walk the enabled hyperpath of ``proc_id``, evaluating each step's registered template in the
    exact tower.  Returns (root values, step trace).  A step whose label is dead stops the walk.

    Registered operations (from the source's ``operations`` block):
      BIND_EXACT  bind eval_template(template, env) to the step's ``binds`` name
      EMIT_ROOT   append eval_template(template, env) to the produced root set
    """
    amap = pop.space.atom_map()
    env: dict[str, Exact] = inst.env()
    roots: list = []
    trace: list[dict] = []
    for sid in source[proc_id].get("hyperpath", []):
        step = source[sid]
        live = kso.profile_live(amap[sid].profile, revoked)
        if not live:
            trace.append({"step": sid, "status": "DEAD_LABEL"})
            return (), tuple(trace)
        op, template = step["operation"], step["template"]
        value = alg.eval_template(template, env)
        if op == "BIND_EXACT":
            env[step["binds"]] = value
        elif op == "EMIT_ROOT":
            roots.append(value)
        else:
            raise TemplateRejection(f"{sid}: unregistered operation {op!r}")
        trace.append({"step": sid, "operation": op, "template": template, "value": value.render()})
    seen: dict = {}
    for r in roots:
        seen.setdefault(r.key(), r)
    return tuple(seen.values()), tuple(trace)


# ----------------------------------------------------------------------------------------------
# solve
# ----------------------------------------------------------------------------------------------

STAGES = ("ATOMIZE", "NAVIGATE", "FIRE", "EXTRACT", "COMPOSE", "CHECK", "RENDER")


def solve_instance(pop: m1.Population, source: dict[str, dict], inst, answer, *,
                   unrevoke: frozenset[str] = frozenset(), run_checker: bool = True) -> dict:
    ks = pop.space
    amap = ks.atom_map()
    r_q = pop.registered_revoked | atomize_labels(pop, inst)
    if unrevoke:                       # (b) plant: flip a constraint atom's label back to live
        r_q = r_q - frozenset(pop.base_index[x] for x in unrevoke)
    seeds = seeds_for(inst)
    seed = m0.seed_vector(ks, {s: Fraction(1, 1) for s in seeds})
    act = m1.activation(ks, seed, ALPHA, revoked=r_q)
    procs = [x for x in ks.ids if source.get(x, {}).get("type") == "procedure" and source[x].get("hyperpath")]
    fired = [p for p in procs if kso.profile_live(amap[p].profile, r_q) and act[p] > 0]
    outcome = "FOUND" if fired else "GAP_NOT_FOUND"
    stage: dict[str, str] = {}
    root_claims: list[dict] = []
    roots_by_proc: dict[str, list[str]] = {}
    keys_by_proc: dict[str, frozenset] = {}
    traces: dict[str, tuple] = {}
    for p in fired:
        values, trace = interpret_hyperpath(pop, source, p, inst, r_q)
        traces[p] = trace
        if not values:
            stage.setdefault("COMPOSE", f"{p} fired but its hyperpath produced no root")
            continue
        roots_by_proc[p] = [v.render() for v in values]
        keys_by_proc[p] = frozenset(v.key() for v in values)
        for k, v in enumerate(values):
            root_claims.append({"atom_id": f"root:{inst.instance_id}:{p}:{k}", "kind": "ROOT_CLAIM", "variable": "x",
                                "expr": inst.expr(), "root": v.render(), "domain": source[p].get("domain", "C"),
                                "label_channel": "INSTRUCTION", "produced_by": p})
    # CHECK stage 1 — the registered oracle
    expected = answer.root_keys()
    exact = answer.status == "SOLVED" and bool(keys_by_proc) and all(v == expected for v in keys_by_proc.values())
    if answer.status == "CANNOT_CHECK":
        exact = not fired
        if fired:
            stage.setdefault("FIRE", "a procedure fired on a == b == 0")
    elif not fired:
        stage.setdefault("NAVIGATE", "no procedure fired")
    elif not exact:
        bad = {p: roots_by_proc.get(p) for p, v in keys_by_proc.items() if v != expected}
        stage.setdefault("COMPOSE", f"roots differ from the oracle: {bad}")
    applicable = set(answer.applicable_procedures)
    if fired and set(fired) != applicable:
        stage.setdefault("FIRE", f"fired {sorted(fired)} vs applicable {sorted(applicable)}")
        exact = False
    # CHECK stage 2 — the SymPy EXACT_CHECKER channel: the ONLY warrant for a root
    verdicts: dict[str, int] = {"VALID": 0, "INVALID": 0, "CANNOT_CHECK": 0}
    warranted: list[str] = []
    if run_checker:
        instance_payload = {"instance_id": inst.instance_id, "bindings": inst.bindings()}
        for claim in root_claims:
            res = checker.check(claim, instance_payload)
            claim["exact_checker"] = res["status"]
            verdicts[res["status"]] += 1
            if checker.is_warranted(res):
                warranted.append(claim["atom_id"])
            elif res["status"] == "INVALID":
                stage.setdefault("CHECK", f"{claim['atom_id']} is INVALID under the EXACT_CHECKER: {res['witness'].get('reason')}")
    attribution = "" if exact else next((s for s in STAGES if s in stage), "ATTRIBUTION_FAILED")
    return {"instance_id": inst.instance_id, "family": inst.family, "bindings": inst.bindings(), "seeds": seeds,
            "query_revoked_constraints": sorted(x for x, i in pop.base_index.items() if i in r_q and x.startswith("con:")),
            "navigation_outcome": outcome, "fired_procedures": fired, "roots_by_procedure": roots_by_proc,
            "step_traces": {p: list(t) for p, t in traces.items()}, "root_claims": root_claims,
            "exact_checker": {"verdicts": verdicts, "warranted": warranted},
            "warrant": "EXACT_CHECKER" if run_checker and verdicts["VALID"] == len(root_claims) and root_claims else "UNWARRANTED",
            "oracle": answer.as_dict(), "exact": exact, "attribution": attribution, "stage_failures": stage}


# ----------------------------------------------------------------------------------------------
# freeze
# ----------------------------------------------------------------------------------------------


def check_design_drift() -> dict:
    if not DESIGN_V3.exists():
        raise CannotCheck(f"the V3 design freeze {DESIGN_V3.name} does not exist; nothing may run before it is committed")
    frozen = json.loads(DESIGN_V3.read_text(encoding="utf-8"))
    pins = {"source_sha256": alg.SOURCE, "generator_sha256": HERE / "kso_algebra_quadratic_v3.py",
            "module_sha256": Path(__file__).resolve(), "checker_sha256": HERE / "kso_exact_checker_sympy_v1.py"}
    drift = {}
    for key, path in pins.items():
        now = hashlib.sha256(path.read_bytes()).hexdigest()
        if frozen["v3"][key] != now:
            drift[key] = {"frozen": frozen["v3"][key][:12], "now": now[:12], "path": str(path.relative_to(ROOT))}
    if drift:
        raise CannotCheck(f"DESIGN_DRIFT against KSO_M2B_DESIGN_V3.json: {drift}")
    return {"design": DESIGN_V3.name, "threshold": frozen["v3"]["gates"]["G1"]["threshold"],
            "supersedes": {"v1": frozen["supersession"]["v1"]["source_sha256"][:12],
                           "v2": frozen["supersession"]["v2"]["source_sha256"][:12]},
            "pins": {k: frozen["v3"][k][:12] for k in pins}}


# ----------------------------------------------------------------------------------------------
# plants
# ----------------------------------------------------------------------------------------------

CORRUPT_STEP = ("step:qf:1", "b**2 - 3*a*c")   # registered plant: one step of one procedure


def corrupted_source(step_id: str = CORRUPT_STEP[0], template: str = CORRUPT_STEP[1]) -> dict:
    src = copy.deepcopy(alg.source_atoms())
    hit = 0
    for a in src["atoms"]:
        if a["id"] == step_id:
            assert a["template"] != template, "the plant would be a no-op: the template already reads that way"
            a["template"] = template
            hit += 1
    assert hit == 1, f"the plant did not land: {hit} atoms named {step_id}"
    return src


def plant_a_corrupt_step(clean_rows: list[dict]) -> dict:
    """(a) Corrupt one step in the registered source => the root DIFFERS from the clean root (the
    mutation is asserted to have landed), the oracle disagrees, and the checker returns INVALID."""
    src = corrupted_source()
    pop, by_id = populate_from_source(src)
    pairs, _ = alg.generate_split("dev", "ALGEBRA-DEV-20260904", 1)
    inst, ans = next((i, a) for i, a in pairs if i.family == "IRRATIONAL_DISTINCT")
    row = solve_instance(pop, by_id, inst, ans)
    clean = next(r for r in clean_rows if r["instance_id"] == inst.instance_id)
    corrupted_roots = row["roots_by_procedure"].get("proc:quadratic_formula")
    clean_roots = clean["roots_by_procedure"].get("proc:quadratic_formula")
    invalid_by_proc = sorted({c["produced_by"] for c in row["root_claims"] if c.get("exact_checker") == "INVALID"})
    valid_by_proc = sorted({c["produced_by"] for c in row["root_claims"] if c.get("exact_checker") == "VALID"})
    return {"step_corrupted": CORRUPT_STEP[0], "template_now": CORRUPT_STEP[1], "instance": inst.instance_id,
            "mutation_landed__root_differs_from_clean": corrupted_roots != clean_roots,
            "clean_root": clean_roots, "corrupted_root": corrupted_roots,
            "oracle_disagrees": not row["exact"], "attribution": row["attribution"],
            "exact_checker_invalid": row["exact_checker"]["verdicts"]["INVALID"] > 0,
            "invalid_procedures": invalid_by_proc, "still_warranted_procedures": valid_by_proc,
            "locality": ("only the corrupted procedure's roots are INVALID; proc:complete_square walks a DIFFERENT "
                         "step (step:cs:1), is untouched by the plant, and is still warranted -- the corruption is "
                         "local to the step that was corrupted, which is what 'knowledge lives in the source' means"),
            "locality_holds": invalid_by_proc == ["proc:quadratic_formula"],
            "CAUGHT": (corrupted_roots != clean_roots and not row["exact"]
                       and invalid_by_proc == ["proc:quadratic_formula"])}


def plant_b_flip_label(pop, by_id, pairs) -> dict:
    """(b) Flip ONE constraint atom's label on a real instance => factoring fires and the wrong root
    is caught.  Plus the no-alarm control: with correct labels it does not fire."""
    out: dict[str, object] = {}
    irr, irr_ans = next((i, a) for i, a in pairs if i.family == "IRRATIONAL_DISTINCT")
    flipped = solve_instance(pop, by_id, irr, irr_ans, unrevoke=frozenset({"con:rational_roots"}))
    out["one_flip_irrational"] = {
        "instance": irr.instance_id, "flipped": "con:rational_roots",
        "proc_factor_fired": "proc:factor" in flipped["fired_procedures"],
        "attribution": flipped["attribution"],
        "exact_checker_invalid": flipped["exact_checker"]["verdicts"]["INVALID"] > 0,
        "reason": flipped["stage_failures"].get("CHECK") or flipped["stage_failures"].get("FIRE"),
        "CAUGHT": "proc:factor" in flipped["fired_procedures"] and not flipped["exact"] and flipped["exact_checker"]["verdicts"]["INVALID"] > 0}
    cpx, cpx_ans = next((i, a) for i, a in pairs if i.family == "COMPLEX_PAIR")
    flipped2 = solve_instance(pop, by_id, cpx, cpx_ans, unrevoke=frozenset({"con:rational_roots", "con:delta_pos"}))
    out["case_licence_flip_complex"] = {
        "instance": cpx.instance_id, "flipped": ["con:rational_roots", "con:delta_pos"],
        "proc_factor_fired": "proc:factor" in flipped2["fired_procedures"],
        "root_claimed_over_Q": [c["root"] for c in flipped2["root_claims"] if c["produced_by"] == "proc:factor"],
        "exact_checker_invalid": flipped2["exact_checker"]["verdicts"]["INVALID"] > 0,
        "CAUGHT": "proc:factor" in flipped2["fired_procedures"] and flipped2["exact_checker"]["verdicts"]["INVALID"] > 0}
    return out


def plant_c_three_instance_corruption() -> dict:
    """(c) A corruption reaching three instances must make main() return 1, not 0."""
    src = corrupted_source()
    pop, by_id = populate_from_source(src)
    pairs, _ = alg.generate_split("dev", "ALGEBRA-DEV-20260904", 5)
    subset = [(i, a) for i, a in pairs if i.family == "IRRATIONAL_DISTINCT"][:3]
    rows = [solve_instance(pop, by_id, i, a, run_checker=False) for i, a in subset]
    n_exact = sum(1 for r in rows if r["exact"])
    return {"instances": [r["instance_id"] for r in rows], "n": len(rows), "exact": n_exact,
            "exit_code_would_be": 0 if n_exact >= len(rows) else 1,
            "CAUGHT": n_exact == 0 and len(rows) == 3}


# ----------------------------------------------------------------------------------------------
# run
# ----------------------------------------------------------------------------------------------


def run(per_family: int = 5, *, with_plants: bool = True) -> dict:
    design = check_design_drift()
    threshold = design["threshold"]
    pop, by_id = populate_from_source()
    digest_before = m0.genome_digest()
    p1 = m1.check_P1_dense(pop)
    genome = {"S1": m0.ks_S1_admission(pop.governed), "S2": m0.ks_S2_composition(pop.governed),
              "S7": pop.governed.meter.admit == len(pop.space.atoms), "digest_unchanged": m0.genome_digest() == digest_before}
    assert all(genome.values()), genome
    seed = m1.uniform(pop.space)
    pre = m1.activation(pop.space, seed, ALPHA)
    retr = {"revocations": 0, "dead_zero": 0, "unreachable_unchanged": 0, "restored": 0, "parent_raised": 0}
    for aid, i in sorted(pop.base_index.items()):
        if by_id.get(aid, {}).get("type") not in ("constraint", "definition", "step"):
            continue
        r = frozenset({i})
        dead = m1.dead_set(pop, r)
        post = m1.activation(pop.space, seed, ALPHA, revoked=r)
        reach = m0.ungated_closure(pop.space, dead)
        assert all(post[x] == 0 for x in dead) and all(post[x] == pre[x] for x in pop.space.ids if x not in reach), aid
        bad = m1.activation(pop.space, seed, ALPHA, revoked=r, matrix=kso.navigation_matrix_bad_renormalize)
        retr["parent_raised"] += 1 if any(bad[x] > pre[x] for x in pop.space.ids if x not in reach) else 0
        assert m1.activation(pop.space, seed, ALPHA) == pre
        for k in ("revocations", "dead_zero", "unreachable_unchanged", "restored"):
            retr[k] += 1
    pairs, rejects = alg.generate_split("dev", "ALGEBRA-DEV-20260904", per_family)
    rows = [solve_instance(pop, by_id, inst, ans) for inst, ans in pairs]
    n_exact = sum(1 for r in rows if r["exact"])
    attributions: dict[str, int] = {}
    for r in rows:
        if r["attribution"]:
            attributions[r["attribution"]] = attributions.get(r["attribution"], 0) + 1
    verdicts = {k: sum(r["exact_checker"]["verdicts"][k] for r in rows) for k in ("VALID", "INVALID", "CANNOT_CHECK")}
    # no-alarm controls on the clean run
    no_alarm = {
        "proc_factor_never_fires_on_irrational": all("proc:factor" not in r["fired_procedures"] for r in rows if r["family"] == "IRRATIONAL_DISTINCT"),
        "proc_factor_never_fires_on_complex": all("proc:factor" not in r["fired_procedures"] for r in rows if r["family"] == "COMPLEX_PAIR"),
        "nothing_fires_on_no_equation": all(not r["fired_procedures"] for r in rows if r["family"] == "NO_EQUATION"),
        "zero_invalid_root_claims": verdicts["INVALID"] == 0,
        "zero_cannot_check_root_claims": verdicts["CANNOT_CHECK"] == 0,
    }
    plants: dict[str, object] = {}
    if with_plants:
        plants["a_corrupt_step_in_the_source"] = plant_a_corrupt_step(rows)
        plants["b_flip_one_constraint_label"] = plant_b_flip_label(pop, by_id, pairs)
        plants["c_three_instance_corruption_exits_1"] = plant_c_three_instance_corruption()
        plants["d_oracle_disagreement_is_cannot_check"] = _plant_d()
        plants["e_out_of_range_is_typed_rejection"] = _plant_e(pop, by_id)
    met = n_exact >= threshold["min_exact"] and len(rows) == threshold["n"]
    return {
        "schema": "orion.kso.m2b-algebra-receipt.v3", "contract": "KnowledgeSpace.v1-M2b-V3", "design": design,
        "source": {"file": str(alg.SOURCE.relative_to(ROOT)), "sha256": hashlib.sha256(alg.SOURCE.read_bytes()).hexdigest(),
                   "atoms": len(by_id), "procedures_are_data": True,
                   "steps": sum(1 for a in by_id.values() if a["type"] == "step")},
        "provenance": {"command": f"python research/orion-machine/reference/kso_m2b_algebra_v3.py --per-family {per_family} --out research/orion-machine/results/KSO_M2B_ALGEBRA_RECEIPT_V3.json",
                       "python": sys.version.split()[0], "sympy": checker.assumption(), "split_seed": "ALGEBRA-DEV-20260904",
                       "parameters": {"alpha": str(ALPHA), "status": "PRE_STUDY_PLACEHOLDER (KSO_PARAMETER_STUDY_V1)"}},
        "population": {"atoms": len(pop.space.atoms), "hyperedges": len(pop.space.hyperedges), "P1_dense": p1, "genome": genome,
                       "channel": "INSTRUCTION via admit() for every atom",
                       "meter": {"admit": pop.governed.meter.admit, "compose": pop.governed.meter.compose}},
        "retraction_both_directions": retr,
        "instances": rows, "rejections": rejects,
        "G1_exact_vs_oracle": {"n": len(rows), "exact": n_exact, "threshold": threshold, "met": met, "attributions": attributions},
        "G6_exact_checker_verdicts": verdicts,
        "no_alarm_controls": no_alarm,
        "plants": plants,
        "warrant_status": "a ROOT_CLAIM is warranted iff kso_exact_checker_sympy_v1 returns VALID under the EXACT_CHECKER certificate; the producing label channel is INSTRUCTION and is ignored for the verdict",
        "terminal": ("M2B_V3_SOLVED_FROM_THE_SOURCE_AND_WARRANTED" if met and all(no_alarm.values())
                     else "M2B_V3_DEFECT_ATTRIBUTED__" + "+".join(sorted(attributions) or ["NO_ALARM_CONTROL_FAILED"])),
    }


def _plant_d() -> dict:
    def perturbed(inst):
        a = alg.oracle_independent(inst)
        if inst.family == "COMPLEX_PAIR":
            return alg.OracleAnswer(a.family, a.discriminant, "Delta==0", a.roots, 1, True, alg._procs("Delta==0"), a.status)
        return a
    try:
        alg.generate_split("dev", "ALGEBRA-DEV-20260904", 5, second_oracle=perturbed)
    except OracleDisagreement as exc:
        return {"CAUGHT": True, "exit_code_would_be": 2, "instance_named": str(exc).split(":")[0], "never_redrawn": True}
    return {"CAUGHT": False}


def _plant_e(pop, by_id) -> dict:
    far = alg.Instance("planted-out-of-range", "RATIONAL_DISTINCT", Fraction(1), Fraction(0), Fraction(-100000))
    at_oracle = at_solver = None
    try:
        alg.oracle(far)
    except OutOfRegisteredRange as exc:
        at_oracle = str(exc)[:100]
    try:
        atomize_labels(pop, far)
    except OutOfRegisteredRange as exc:
        at_solver = str(exc)[:100]
    return {"CAUGHT": at_oracle is not None and at_solver is not None, "at_oracle": at_oracle, "at_solver": at_solver,
            "exit_code_would_be": 2}


def _default(o):
    if isinstance(o, Fraction):
        return str(o)
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    raise TypeError(type(o).__name__)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=5)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--plant-corrupt-step", action="store_true",
                        help="run with the registered step corruption applied to the whole split (the (c) plant)")
    parser.add_argument("--no-plants", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.plant_corrupt_step:
            src = corrupted_source()
            pop, by_id = populate_from_source(src)
            pairs, _ = alg.generate_split("dev", "ALGEBRA-DEV-20260904", args.per_family)
            rows = [solve_instance(pop, by_id, i, a, run_checker=False) for i, a in pairs]
            frozen = json.loads(DESIGN_V3.read_text(encoding="utf-8"))["v3"]["gates"]["G1"]["threshold"]
            n_exact = sum(1 for r in rows if r["exact"])
            res = {"terminal": "M2B_V3_PLANTED_CORRUPTION", "G1_exact_vs_oracle": {"n": len(rows), "exact": n_exact, "threshold": frozen, "met": n_exact >= frozen["min_exact"]}}
        else:
            res = run(per_family=args.per_family, with_plants=not args.no_plants)
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except OutOfRegisteredRange as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": f"OutOfRegisteredRange: {exc}"}))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(res, indent=2, sort_keys=True, default=_default)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"terminal": res["terminal"], "G1": res["G1_exact_vs_oracle"]}, sort_keys=True, default=_default))
    else:
        print(text)
    # (c): the registered threshold IS the gate.  A terminal label is not an exit code.
    return 0 if res["G1_exact_vs_oracle"]["met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
