"""KSO M2b — populate the knowledge space from the registered algebra source THROUGH THE INSTRUCTION
CHANNEL, run the M0 invariants on it, and solve the registered quadratic instances by navigation
+ label-gated firing, producing ROOT_CLAIM proposals for the EXACT_CHECKER channel.

Population (every atom enters via ``kso_m0_freeze_checks_v1.admit`` — edges > 0, reachable,
certificate INSTRUCTION — nothing is written to the store any other way):
  atom  id = source id, type = source type, label = {{i}} (fresh evidence index per source atom:
        an instruction is an assumption until the checker warrants what it produces)
  edges DEPENDENCE  P -> A for every precondition P of A
        CONSTRAINT  C -> T for every T the constraint atom C constrains
        COMPOSITION (preconditions) -> procedure   (joint tails; label = ⊗ of the preconditions ⊗ own)
        REPRESENTATION_TRANSPORT standard -> vertex, standard -> factored
        SUPPORT     example -> each procedure/constraint it exercises

Solve (per registered instance a*x**2 + b*x + c = 0):
  atomize   seeds = {rep:standard_form, con:a_nonzero or proc:linear (by a), the discriminant case
            atom (by Delta), con:rational_roots when Delta is a rational square}
  navigate  exact restart fixed point; FOUND iff the applicable procedure atoms carry activation
  fire      a procedure fires iff all its preconditions are live AND the case constraint atoms that
            apply to this instance are live; a constraint that does NOT hold on the instance is
            revoked for the query (its evidence index enters R_Q) — that is how "Delta < 0 blocks
            proc:factor" is a label gate, not an if-statement
  extract   reacting subgraph; the fired procedures are the candidate methods
  compose   apply each fired procedure's registered SymPy-free exact form (the oracle's rational
            arithmetic is NOT called; the procedure's own formula in exact rationals is evaluated)
            -> ROOT_CLAIM atoms with label_channel INSTRUCTION (UNWARRANTED until the checker)
  check     the produced roots vs the registered oracle (kso_algebra_quadratic_v1.oracle): exact
            agreement per instance, single-stage attribution otherwise
  render    {"instance_id", "roots", "method", "root_claims": [schema of ALGEBRA_SOURCE_V1]}

Exit codes 0/1/2.  NO NOVELTY CLAIM.  Roots are UNWARRANTED_PENDING_EXACT_CHECKER in this receipt;
warrant is conferred only by ``kso_exact_checker_sympy_v1`` (guards lane).
"""
from __future__ import annotations

import argparse
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
alg = _load("kso_algebra_quadratic_v1", HERE / "kso_algebra_quadratic_v1.py")
CannotCheck = kso.CannotCheck
Atom, Hyperedge, KnowledgeSpace = kso.Atom, kso.Hyperedge, kso.KnowledgeSpace
ONE, ZERO = m0.ONE, m0.ZERO
Cert = m0.CertificateKind
ALPHA = Fraction(1, 3)  # PRE_STUDY_PLACEHOLDER (KSO_PARAMETER_STUDY_V1)

TYPE_MAP = {"definition": "claim", "representation": "representation", "constraint": "constraint", "procedure": "procedure", "worked_example": "observation"}


def _constraint_profile(cons: list[dict], amap: dict) -> tuple:
    """The gate a set of constraint atoms puts on a target: non-case ones conjoin, case ones disjoin."""
    prof: tuple = ONE
    alt: tuple = ZERO
    for c in cons:
        if c.get("case"):
            alt = kso.profile_or(alt, amap[c["id"]].profile)
        else:
            prof = kso.profile_and(prof, amap[c["id"]].profile)
    return kso.profile_and(prof, alt) if alt != ZERO else prof


def populate_from_source() -> tuple[m1.Population, dict[str, str]]:
    src = alg.source_atoms()
    atoms = src["atoms"]
    by_id = {a["id"]: a for a in atoms}
    # topological order by preconditions so every admission finds its edges' tails present
    order: list[str] = []
    seen: set[str] = set()

    def visit(i: str) -> None:
        if i in seen:
            return
        for p in by_id[i].get("preconditions", []):
            visit(p)
        seen.add(i)
        order.append(i)

    constrained_by: dict[str, list[dict]] = {}
    for a in atoms:
        for t in a.get("constraint_on", []):
            constrained_by.setdefault(t, []).append(a)
    # constraints of a target are admitted before it so its applicability label can be composed
    _visit = visit

    def visit(i: str) -> None:  # noqa: F811
        if i in seen:
            return
        for c in constrained_by.get(i, []):
            visit(c["id"])
        _visit(i)

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
        for p in a.get("preconditions", []):
            label = kso.profile_and(label, amap_now[p].profile)
        # applicability: non-case constraints conjoin; case constraints (exactly one holds) disjoin
        cons = constrained_by.get(aid, [])
        case_alt: tuple = ZERO
        for c in cons:
            if c.get("case"):
                case_alt = kso.profile_or(case_alt, amap_now[c["id"]].profile)
            else:
                label = kso.profile_and(label, amap_now[c["id"]].profile)
        if case_alt != ZERO:
            label = kso.profile_and(label, case_alt)
        edges: list[Hyperedge] = []
        pre = a.get("preconditions", [])
        for p in pre:
            edges.append(Hyperedge(f"dep:{p}->{aid}", (p,), (aid,), "DEPENDENCE", profile=ONE))
        for c in cons:
            edges.append(Hyperedge(f"con:{c['id']}->{aid}", (c["id"],), (aid,), "CONSTRAINT", profile=ONE))
        if a["type"] == "procedure" and pre:
            # the composite's tails are its preconditions; the constraint gate lives in the head label
            edges.append(Hyperedge(f"compose:{aid}", tuple(pre), (aid,), "COMPOSITION", profile=kso.profile_and((frozenset({k}),), _constraint_profile(cons, amap_now))))
        if not pre:
            edges.append(Hyperedge(f"dep:root->{aid}", ("root:algebra",), (aid,), "DEPENDENCE", profile=ONE))
        ks, rec = m0.admit(ks, Atom(aid, TYPE_MAP[a["type"]], label), tuple(edges), Cert.INSTRUCTION, alpha=ALPHA)
        certs[aid] = rec.certificate.value
        meter = meter.charged(admit=1, compose=1 if a["type"] == "procedure" and pre else 0)
    # constraint, transport and support edges after every atom exists (edges only; no new atoms)
    extra: list[Hyperedge] = []
    for a in atoms:
        if a["type"] == "worked_example":
            for p in a.get("preconditions", []):
                extra.append(Hyperedge(f"sup:{a['id']}->{p}", (a["id"],), (p,), "SUPPORT", profile=ONE))
    for src_id, dst in (("rep:standard_form", "rep:vertex_form"), ("rep:standard_form", "rep:factored_form")):
        extra.append(Hyperedge(f"transport:{src_id}->{dst}", (src_id,), (dst,), "REPRESENTATION_TRANSPORT", profile=ONE))
    ks = KnowledgeSpace(ks.atoms, ks.hyperedges + tuple(extra))
    ks.validate()
    m0.check_edge_vocabulary(ks)
    governed = m0.GovernedSpace(ks, {k: Cert(v) for k, v in certs.items()}, evidence_atoms=len(order), meter=meter, revoked=frozenset())
    pop = m1.Population(ks, governed, dict(index), {k: "VALID" for k in index}, {}, {}, frozenset(), ())
    return pop, {a["id"]: a["type"] for a in atoms}


# ----------------------------------------------------------------------------------------------
# solve
# ----------------------------------------------------------------------------------------------

CASE_ATOM = {"Delta>0 rational": "con:delta_pos", "Delta>0 irrational": "con:delta_pos", "Delta==0": "con:delta_zero", "Delta<0": "con:delta_neg"}


def query_revocations(pop: m1.Population, inst) -> frozenset[int]:
    """Constraint atoms that do not hold on this instance are revoked for the query: the case atoms
    other than the instance's case, con:a_nonzero when a == 0, con:rational_roots when Delta is not a
    rational square.  This is the label gate that blocks a procedure, not a conditional."""
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
        if delta < 0 or alg.rational_sqrt(delta) is None:
            dead.add("con:rational_roots")
    return frozenset(pop.base_index[x] for x in dead)


def constraint_gate(ks: KnowledgeSpace, proc_id: str, revoked: frozenset[int]) -> bool:
    amap = ks.atom_map()
    for e in ks.hyperedges:
        if e.relation_type == "CONSTRAINT" and e.heads == (proc_id,):
            if not kso.profile_live(amap[e.tails[0]].profile, revoked):
                return False
    return True


def apply_procedure(proc_id: str, inst) -> tuple[str, ...] | None:
    """The procedure's own registered exact form in rational arithmetic (no oracle call)."""
    a, b, c = inst.a, inst.b, inst.c
    if proc_id == "proc:linear":
        return None if b == 0 else (str(-c / b),)
    if a == 0:
        return None
    delta = b * b - 4 * a * c
    if proc_id in ("proc:quadratic_formula", "proc:complete_square"):
        s = alg.rational_sqrt(delta) if delta >= 0 else None
        if delta == 0:
            return (str(-b / (2 * a)),)
        if s is not None:
            return (str((-b + s) / (2 * a)), str((-b - s) / (2 * a)))
        if delta > 0:
            return (f"({-b} + sqrt({delta}))/({2 * a})", f"({-b} - sqrt({delta}))/({2 * a})")
        return (f"({-b} + I*sqrt({-delta}))/({2 * a})", f"({-b} - I*sqrt({-delta}))/({2 * a})")
    if proc_id == "proc:factor":
        s = alg.rational_sqrt(delta)
        if s is None:
            return None  # Q-domain: not applicable
        r1, r2 = (-b + s) / (2 * a), (-b - s) / (2 * a)
        assert r1 + r2 == -b / a and r1 * r2 == c / a
        return (str(r1), str(r2)) if r1 != r2 else (str(r1),)
    return None


def solve_instance(pop: m1.Population, inst, answer) -> dict:
    ks = pop.space
    amap = ks.atom_map()
    r_q = pop.registered_revoked | query_revocations(pop, inst)
    seeds = ["rep:standard_form", "con:a_nonzero" if inst.a != 0 else "con:a_zero"]
    if inst.a != 0:
        delta = inst.b * inst.b - 4 * inst.a * inst.c
        seeds.append("con:delta_pos" if delta > 0 else "con:delta_zero" if delta == 0 else "con:delta_neg")
        if delta > 0 and alg.rational_sqrt(delta) is not None:
            seeds.append("con:rational_roots")
    seed = m0.seed_vector(ks, {s: Fraction(1, 1) for s in seeds})
    act = m1.activation(ks, seed, ALPHA, revoked=r_q)
    procs = [x for x in ks.ids if amap[x].atom_type == "procedure" and x != "proc:vieta_check"]
    fired = [p for p in procs if kso.profile_live(amap[p].profile, r_q) and act[p] > 0]
    outcome = "FOUND" if fired else "GAP_NOT_FOUND"
    stage: dict[str, str] = {}
    root_claims = []
    roots_by_proc: dict[str, tuple[str, ...]] = {}
    for p in fired:
        roots = apply_procedure(p, inst)
        if roots is None:
            stage.setdefault("COMPOSE", f"{p} fired but produced nothing")
            continue
        roots_by_proc[p] = roots
        for k, r in enumerate(roots):
            root_claims.append({"atom_id": f"root:{inst.instance_id}:{p}:{k}", "kind": "ROOT_CLAIM", "variable": "x", "expr": inst.expr(), "root": r, "domain": "Q" if p in ("proc:factor", "proc:linear") else "C", "label_channel": "INSTRUCTION", "produced_by": p})
    # CHECK against the registered oracle
    expected = set(answer.roots)
    exact = answer.status == "SOLVED" and bool(roots_by_proc) and all(set(v) == expected for v in roots_by_proc.values())
    if answer.status == "CANNOT_CHECK":
        exact = not fired  # nothing must fire on a non-equation
        if fired:
            stage.setdefault("FIRE", "a procedure fired on a == b == 0")
    elif not fired:
        stage.setdefault("NAVIGATE", "no procedure fired")
    elif not exact:
        bad = {p: v for p, v in roots_by_proc.items() if set(v) != expected}
        stage.setdefault("COMPOSE", f"roots differ from the oracle: {bad}")
    applicable = set(answer.applicable_procedures)
    if fired and set(fired) != applicable:
        stage.setdefault("FIRE", f"fired {sorted(fired)} vs applicable {sorted(applicable)}")
        exact = False
    attribution = "" if exact else next((s for s in ("ATOMIZE", "NAVIGATE", "FIRE", "EXTRACT", "COMPOSE", "CHECK", "RENDER") if s in stage), "ATTRIBUTION_FAILED")
    return {"instance_id": inst.instance_id, "family": inst.family, "bindings": inst.bindings(), "seeds": seeds, "query_revoked_constraints": sorted(x for x, i in pop.base_index.items() if i in r_q),
            "navigation_outcome": outcome, "fired_procedures": fired, "roots_by_procedure": roots_by_proc, "root_claims": root_claims, "warrant": "UNWARRANTED_PENDING_EXACT_CHECKER",
            "oracle": answer.as_dict(), "exact": exact, "attribution": attribution, "stage_failures": stage}


DESIGN_V2 = ROOT / "research" / "orion-machine" / "results" / "KSO_M2B_DESIGN_V2.json"


def check_design_drift() -> dict:
    frozen = json.loads(DESIGN_V2.read_text(encoding="utf-8"))
    now = hashlib.sha256(alg.SOURCE.read_bytes()).hexdigest()
    if frozen["v2"]["source_sha256"] != now:
        raise CannotCheck(f"DESIGN_DRIFT: algebra source {now[:12]} != frozen {frozen['v2']['source_sha256'][:12]}")
    return {"design": "KSO_M2B_DESIGN_V2.json", "source_sha256": now, "supersedes": frozen["supersession"]["v1"]["source_sha256"]}


def run(per_family: int = 5) -> dict:
    design = check_design_drift()
    pop, types = populate_from_source()
    digest_before = m0.genome_digest()
    p1 = m1.check_P1_dense(pop)
    genome = {"S1": m0.ks_S1_admission(pop.governed), "S2": m0.ks_S2_composition(pop.governed), "S7": pop.governed.meter.admit == len(pop.space.atoms), "digest_unchanged": m0.genome_digest() == digest_before}
    assert all(genome.values()), genome
    # retraction both directions on the algebra graph: revoke each constraint atom's evidence
    seed = m1.uniform(pop.space)
    pre = m1.activation(pop.space, seed, ALPHA)
    retr = {"revocations": 0, "dead_zero": 0, "unreachable_unchanged": 0, "restored": 0, "parent_raised": 0}
    for aid, i in sorted(pop.base_index.items()):
        if types.get(aid) not in ("constraint", "definition"):
            continue
        r = frozenset({i})
        dead = m1.dead_set(pop, r)
        post = m1.activation(pop.space, seed, ALPHA, revoked=r)
        reach = m0.ungated_closure(pop.space, dead)
        assert all(post[x] == 0 for x in dead) and all(post[x] == pre[x] for x in pop.space.ids if x not in reach), aid
        bad = m1.activation(pop.space, seed, ALPHA, revoked=r, matrix=kso.navigation_matrix_bad_renormalize)
        retr["parent_raised"] += 1 if any(bad[x] > pre[x] for x in pop.space.ids if x not in reach) else 0
        assert m1.activation(pop.space, seed, ALPHA) == pre
        retr["revocations"] += 1
        retr["dead_zero"] += 1
        retr["unreachable_unchanged"] += 1
        retr["restored"] += 1
    pairs, rejects = alg.generate_split("dev", "ALGEBRA-DEV-20260904", per_family)
    rows = [solve_instance(pop, inst, ans) for inst, ans in pairs]
    n_exact = sum(1 for r in rows if r["exact"])
    attributions: dict[str, int] = {}
    for r in rows:
        if r["attribution"]:
            attributions[r["attribution"]] = attributions.get(r["attribution"], 0) + 1
    # planted: revoking con:a_nonzero for a normal instance must stop the quadratic procedures from firing
    inst0, ans0 = next((i, a) for i, a in pairs if i.family == "RATIONAL_DISTINCT")
    plant = m1.Population(pop.space, pop.governed, pop.base_index, pop.base_status, {}, {}, frozenset({pop.base_index["con:a_nonzero"]}), ())
    planted_row = solve_instance(plant, inst0, ans0)
    assert not planted_row["fired_procedures"] or set(planted_row["fired_procedures"]) <= {"proc:linear"}, planted_row["fired_procedures"]
    return {
        "schema": "orion.kso.m2b-algebra-receipt.v1", "contract": "KnowledgeSpace.v1-M2b", "design": {**design, "run": "V2 (V1 outcome M2B_V1_GATING_DEFECT recorded in KSO_M2B_ALGEBRA_OUTCOME_V1.md)"},
        "source": {"file": str(alg.SOURCE.relative_to(ROOT)), "sha256": hashlib.sha256(alg.SOURCE.read_bytes()).hexdigest(), "atoms": len(types)},
        "provenance": {"command": f"python research/orion-machine/reference/kso_m2b_algebra_population_v1.py --per-family {per_family} --out research/orion-machine/results/KSO_M2B_ALGEBRA_RECEIPT_V1.json", "python": sys.version.split()[0], "split_seed": "ALGEBRA-DEV-20260904", "parameters": {"alpha": str(ALPHA), "status": "PRE_STUDY_PLACEHOLDER (KSO_PARAMETER_STUDY_V1)"}},
        "population": {"atoms": len(pop.space.atoms), "hyperedges": len(pop.space.hyperedges), "P1_dense": p1, "genome": genome, "channel": "INSTRUCTION via admit() for every atom", "meter": {"admit": pop.governed.meter.admit, "compose": pop.governed.meter.compose}},
        "retraction_both_directions": retr,
        "instances": rows, "rejections": rejects,
        "G1_exact_vs_oracle": {"n": len(rows), "exact": n_exact, "attributions": attributions},
        "planted_constraint_revocation_blocks_quadratic_procedures": "CAUGHT",
        "warrant_status": "every ROOT_CLAIM is UNWARRANTED_PENDING_EXACT_CHECKER; warrant is conferred only by kso_exact_checker_sympy_v1 (guards lane); this receipt establishes population, invariants, gating and agreement with the registered oracle",
        "terminal": "M2B_POPULATED_AND_SOLVED_ON_DEV" if n_exact == len(rows) else "M2B_DEFECT_ATTRIBUTED__" + "+".join(sorted(attributions)),
    }


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
    args = parser.parse_args(argv)
    try:
        res = run(per_family=args.per_family)
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(res, indent=2, sort_keys=True, default=_default)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"terminal": res["terminal"], "G1": res["G1_exact_vs_oracle"], "population": {k: v for k, v in res["population"].items() if k in ("atoms", "hyperedges")}, "retraction": res["retraction_both_directions"]}, sort_keys=True))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
