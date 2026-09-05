"""KSO M2 — the solve loop on ME-X1 (design: theory/KSO_M2_SOLVE_DESIGN_V1.md, frozen).

atomize → navigate → fire → extract → compose → check → render, each an exact operator on the
populated knowledge space (M1 `populate(w1, request=…)` plus the request-level atoms added here),
scored per instance against ``mex1_oracle.Expected.decision()`` with a single-stage attribution
for every disagreement, a two-atomizer translator-invariance gate, and a matched budget.

The request semantics (which registered facts are checked, in which precedence, with which
on-failure action) are read from the ``World`` a second time here (``read_request_atoms``), never by
calling ``mex1_oracle.request_atoms``; the CHECK stage compares the two readings.  The shared
status readers for base facts (``source_status`` …) and the protocol constant ``MODULE_RANK`` are
imported as registered data and declared as such.

Exit codes: 0 all gates hold; 1 a gate fails; 2 could not check (incl. DESIGN_DRIFT).
NO NOVELTY OR BREAKTHROUGH CLAIM — the pre-registered expectation is exact agreement by
construction and PARENT_SUFFICIENT against the B5 ceiling.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN_MD = ROOT / "research" / "orion-machine" / "theory" / "KSO_M2_SOLVE_DESIGN_V1.md"
DESIGN_JSON = ROOT / "research" / "orion-machine" / "results" / "KSO_M2_SOLVE_DESIGN_V1.json"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


kso = _load("kso_math_v1", HERE / "kso_math_v1.py")
m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
m1 = _load("kso_m1_mex1_population_v1", HERE / "kso_m1_mex1_population_v1.py")
CannotCheck = kso.CannotCheck
Atom, Hyperedge, KnowledgeSpace = kso.Atom, kso.Hyperedge, kso.KnowledgeSpace
ONE, ZERO = m0.ONE, m0.ZERO
Cert = m0.CertificateKind
ALPHA = Fraction(1, 3)
STAGES = ("ATOMIZE", "NAVIGATE", "FIRE", "EXTRACT", "COMPOSE", "CHECK", "RENDER")

# registered protocol constant (ME_X1_TRANSITION_COUPLING_PROTOCOL_V1): precedence of modules
MODULE_RANK = {"IDENT": 0, "PROV": 1, "DEP": 2, "TRANS": 3, "EVAL": 4, "ATLAS": 5, "AUTH": 6}


def design_digest() -> str:
    return hashlib.sha256(DESIGN_MD.read_bytes()).hexdigest()


def check_design_drift() -> dict[str, str]:
    frozen = json.loads(DESIGN_JSON.read_text(encoding="utf-8"))
    now = design_digest()
    if frozen["design_sha256"] != now:
        raise CannotCheck(f"DESIGN_DRIFT: frozen {frozen['design_sha256'][:12]} != file {now[:12]}")
    return {"design_sha256": now, "ids_sha256": frozen["instances"]["ids_sha256"]}


def graph_sha256(ks: KnowledgeSpace) -> str:
    """Shared with the comparator receipt: sha256 over sorted ``A|id|type`` lines followed by sorted
    ``E|edge_id|tails,|heads,|relation_type`` lines (tails/heads comma-joined), newline-separated."""
    amap = ks.atom_map()
    a_lines = sorted(f"A|{x}|{amap[x].atom_type}" for x in ks.ids)
    e_lines = sorted(f"E|{e.edge_id}|{','.join(e.tails)}|{','.join(e.heads)}|{e.relation_type}" for e in ks.hyperedges)
    return hashlib.sha256("\n".join(a_lines + e_lines).encode()).hexdigest()


# ----------------------------------------------------------------------------------------------
# request-level atoms — the second reading of the registered request semantics
# ----------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ReqSpec:
    atom_id: str
    module: str
    status: str | None      # VALID / INVALID / UNKNOWN; None when derived from a claim's label
    action: str
    derived_claim: str = ""


def read_request_atoms(w, req) -> list[ReqSpec]:
    gen, model, oracle = m1._mex1()
    V, I, U = model.STATUS_VALID, model.STATUS_INVALID, model.STATUS_UNKNOWN
    T = w.claims[req.target_claim_id]
    out: list[ReqSpec] = []
    if req.kind == "ACCEPT_RESULT":
        R = w.results[req.result_id]
        ident = U if R.binding_status == model.IDENTITY_UNRECOVERABLE else (V if R.bound_claim_id == T.claim_id else I)
        out.append(ReqSpec(f"identity:{R.result_id}", "IDENT", ident, model.REVALIDATE))
        dc = req.decision_criterion_id or T.criterion_id
        if dc == T.criterion_id:
            crit = V
        else:
            eq = w.criterion_equivalence.get(w.pair_key(T.criterion_id, dc), "")
            crit = V if eq == model.EQUIV_EQUIVALENT else U if eq == model.EQUIV_CANNOT_CHECK else I
        out.append(ReqSpec(f"criterion:{T.claim_id}", "IDENT", crit, model.REFORMULATE_PROBLEM))
        if R.proved_spec_id:
            if R.proved_spec_id == T.intended_spec_id:
                fid = V
            else:
                f = w.spec_fidelity.get(w.pair_key(R.proved_spec_id, T.intended_spec_id), "")
                fid = V if f == model.FIDELITY_FAITHFUL else I if f == model.FIDELITY_UNFAITHFUL else U
            out.append(ReqSpec(f"spec:{R.result_id}", "IDENT", fid, model.REVALIDATE))
            chk = I if R.checker_status == model.CHECKER_INVALID else U if R.checker_status == model.CHECKER_UNKNOWN else V
            out.append(ReqSpec(f"checker:{R.result_id}", "IDENT", chk, model.REQUEST_NEW_EVIDENCE))
        for e in R.basis_evidence_ids:
            out.append(ReqSpec(f"src:{e}", "PROV", oracle.source_status(w, e), model.REQUEST_NEW_EVIDENCE))
            out.append(ReqSpec(f"ident:{e}", "PROV", oracle.identity_status(w, e), model.REVALIDATE))
            c = oracle.calibration_status(w, e)
            if c is not None:
                out.append(ReqSpec(f"cal:{e}", "PROV", c, model.REVALIDATE))
        if R.comparability_status:
            comp = I if R.comparability_status == model.COMP_NONCOMPARABLE else U if R.comparability_status == model.COMP_CANNOT_CHECK else V
            out.append(ReqSpec(f"comparability:{R.result_id}", "PROV", comp, model.REVALIDATE))
        s = oracle.independence_status(w, set(R.basis_evidence_ids), R.min_independent)
        if s is not None:
            out.append(ReqSpec(f"support:{R.result_id}", "DEP", s, model.REQUEST_NEW_EVIDENCE))
        s = oracle.transport_rank_status(w, R.context_id, T.context_id, R.required_relation)
        if s is not None:
            out.append(ReqSpec(f"transport:{R.result_id}", "TRANS", s, model.BLOCK_TRANSPORT))
        if R.evaluator_id:
            out.append(ReqSpec(f"evaluator:{R.result_id}", "EVAL", oracle.evaluator_atom_status(w, R.evaluator_id, T.failure_class), model.REPLACE_OR_CHALLENGE_EVALUATOR))
    elif req.kind == "CLOSE_GLOBAL":
        pieces = tuple(sorted({p for f in w.families_of(T.claim_id) for p in f.prerequisite_ids}))
        for c in pieces:
            out.append(ReqSpec(f"piece:{c}", "ATLAS", None, model.REQUEST_NEW_EVIDENCE, derived_claim=c))
        for o in sorted(w.overlaps.values(), key=lambda x: x.overlap_id):
            if o.left_claim_id in pieces and o.right_claim_id in pieces:
                st = V if o.compatible is True else I if o.compatible is False else U
                out.append(ReqSpec(f"overlap:{o.overlap_id}", "ATLAS", st, model.REFORMULATE_PROBLEM))
        out.append(ReqSpec(f"witness:{T.claim_id}", "ATLAS", V if T.global_witness_id else U, model.REFORMULATE_PROBLEM))
    elif req.kind == "PROPAGATE_DEFEAT":
        pass  # no request-level atoms; the answer is the reopened set over accepted claims
    else:
        raise CannotCheck(f"unknown request kind {req.kind}")
    auth = U if w.authority.status == model.AUTH_UNDER_REVIEW else (V if w.authority.ceiling_level >= req.required_authority_level else I)
    out.append(ReqSpec("authority", "AUTH", auth, model.ABSTAIN_AUTHORITY))
    ranks = [MODULE_RANK[a.module] for a in out]
    assert ranks == sorted(ranks), "request atoms must be emitted in precedence order"
    return out


def add_request_atoms(pop, w1, inst):
    """Return (new Population, added_atom_ids). Pure: ``pop`` is not mutated.

    Adds one atom per request-level status (fresh evidence index; VALID live, INVALID revoked,
    UNKNOWN censored) unless the atom already exists as an M1 base atom (src/ident/cal), the
    procedure atom ``proc:transition_rule`` and the decision atom ``decision:<id>`` whose label is
    the conjunctive product of every request atom (live ⇔ UPDATE), with DEPENDENCE edges from the
    goal atom and one COMPOSITION hyperedge (rule + request atoms, in precedence order) → decision."""
    specs = read_request_atoms(w1, inst.request)
    ks = pop.space
    rid = f"req:{inst.instance_id}"
    if rid not in ks.ids:
        raise CannotCheck("populate(..., request=) must precede add_request_atoms")
    amap = ks.atom_map()
    atoms = list(ks.atoms)
    edges = list(ks.hyperedges)
    certs = dict(pop.governed.certificates)
    base_index = dict(pop.base_index)
    base_status = dict(pop.base_status)
    revoked = set(pop.registered_revoked)
    unknown = list(pop.unknown)
    next_index = max(base_index.values(), default=-1) + 1
    added: list[str] = []
    tails: list[str] = []
    labels: dict[str, tuple] = {a.atom_id: a.profile for a in atoms}
    gen, model, oracle = m1._mex1()
    for spec in specs:
        if spec.atom_id in amap:
            tails.append(spec.atom_id)
            if not any(e.tails == (rid,) and e.heads == (spec.atom_id,) for e in edges):
                edges.append(Hyperedge(f"goal:{inst.instance_id}:{spec.atom_id}", (rid,), (spec.atom_id,), "DEPENDENCE", profile=ONE))
            continue
        if spec.derived_claim:
            label = labels[f"claim:{spec.derived_claim}"]
            atoms.append(Atom(spec.atom_id, "constraint", label))
            edges.append(Hyperedge(f"piece-support:{spec.derived_claim}", (f"claim:{spec.derived_claim}",), (spec.atom_id,), "SUPPORT", profile=ONE))
        else:
            i = next_index
            next_index += 1
            base_index[spec.atom_id] = i
            base_status[spec.atom_id] = spec.status
            label = (frozenset({i}),)
            if spec.status == model.STATUS_INVALID:
                revoked.add(i)
            elif spec.status == model.STATUS_UNKNOWN:
                unknown.append(i)
            atoms.append(Atom(spec.atom_id, "constraint", label))
        labels[spec.atom_id] = label
        certs[spec.atom_id] = Cert.INSTRUCTION
        edges.append(Hyperedge(f"goal:{inst.instance_id}:{spec.atom_id}", (rid,), (spec.atom_id,), "DEPENDENCE", profile=ONE))
        added.append(spec.atom_id)
        tails.append(spec.atom_id)
    proc = "proc:transition_rule"
    atoms.append(Atom(proc, "procedure", ONE))
    certs[proc] = Cert.INSTRUCTION
    added.append(proc)
    dec = f"decision:{inst.instance_id}"
    prof: tuple = ONE
    for t in tails:
        prof = kso.profile_and(prof, labels[t])
    atoms.append(Atom(dec, "procedure", prof))
    certs[dec] = Cert.INSTRUCTION
    added.append(dec)
    edges.append(Hyperedge(f"compose:{dec}", tuple([proc, *tails]), (dec,), "COMPOSITION", profile=ONE))
    edges.append(Hyperedge(f"goal:{inst.instance_id}:{proc}", (rid,), (proc,), "DEPENDENCE", profile=ONE))
    new_ks = KnowledgeSpace(tuple(atoms), tuple(edges))
    new_ks.validate()
    m0.check_edge_vocabulary(new_ks)
    n_comp = sum(1 for e in edges if e.relation_type == "COMPOSITION")
    governed = m0.GovernedSpace(new_ks, certs, evidence_atoms=next_index, meter=m0.Meter(admit=len(atoms), compose=n_comp), revoked=frozenset(revoked))
    new_pop = m1.Population(new_ks, governed, base_index, base_status, pop.claim_atom, pop.family_atom, frozenset(revoked), tuple(sorted(unknown)))
    return new_pop, tuple(added)


# ----------------------------------------------------------------------------------------------
# the loop
# ----------------------------------------------------------------------------------------------


def atomize_A(pop, w1, inst) -> tuple[tuple, list[Fraction]]:
    """From the TransitionRequest object: goal, target claim, result (if populated)."""
    req = inst.request
    parts = [m0.QuestionPart(f"transition {req.kind}", "goal", (f"req:{inst.instance_id}",)),
             m0.QuestionPart(f"target {req.target_claim_id}", "claim", (f"claim:{req.target_claim_id}",))]
    if getattr(req, "result_id", "") and f"res:{req.result_id}" in pop.space.ids:
        parts.append(m0.QuestionPart(f"result {req.result_id}", "observation", (f"res:{req.result_id}",)))
    return m0.atomize(pop.space, tuple(parts))


def atomize_B(pop, w1, inst) -> tuple[tuple, list[Fraction]]:
    """From the world's registered result binding and the instance id, parts in the opposite order."""
    ids = set(pop.space.ids)
    refs: list[str] = []
    res_ids = [r for r in sorted(w1.results) if f"res:{r}" in ids and r == getattr(inst.request, "result_id", "")]
    for r in res_ids:
        refs.append(f"res:{r}")
    bound = w1.results[res_ids[0]].bound_claim_id if res_ids else inst.request.target_claim_id
    target = inst.request.target_claim_id  # the request names the target; the binding may disagree (that is an IDENT atom)
    del bound
    refs.append(f"claim:{target}")
    refs.append(f"req:{inst.instance_id}")
    parts = tuple(m0.QuestionPart(f"¿{ref}?", "claim" if ref.startswith("claim") else "goal" if ref.startswith("req") else "observation", (ref,)) for ref in refs)
    return m0.atomize(pop.space, parts)


def _sources_differ() -> bool:
    return hashlib.sha256(inspect.getsource(atomize_A).encode()).hexdigest() != hashlib.sha256(inspect.getsource(atomize_B).encode()).hexdigest()


def reacting_subgraph_exact(ks: KnowledgeSpace, seed: Sequence[Fraction], revoked: frozenset[int]) -> tuple[frozenset[str], frozenset[str], dict[str, Fraction], int]:
    background = m1.activation(ks, m1.uniform(ks), ALPHA, revoked=revoked)
    query = m1.activation(ks, seed, ALPHA, revoked=revoked)
    rho = m0.reaction_surprise_vector(query, background)
    support = [x for x, v in zip(ks.ids, seed, strict=True) if v > 0]
    closure = m0.gated_closure(ks, support, revoked)
    atoms = frozenset(x for x in closure if rho[x] > 0 or x in support)
    edges = frozenset(e.edge_id for e in ks.hyperedges if kso.profile_live(e.profile, revoked) and set(e.tails) <= atoms and set(e.heads) <= atoms)
    # edge visits: one per hyperedge traversed with live mass (a hyperedge with k tails counts once);
    # the finer tail×head incidence count is reported alongside as ``incidence_visits``
    amap = ks.atom_map()
    traversed = [e for e in ks.hyperedges if kso.profile_live(e.profile, revoked) and any(query[t] > 0 for t in e.tails) and all(kso.profile_live(amap[t].profile, revoked) for t in e.tails)]
    edge_visits = len(traversed)
    incidences = sum(len(e.tails) * len(e.heads) for e in traversed)
    return atoms, edges, query, (edge_visits, incidences)


def canonical(atoms: Iterable[str], edges: Iterable[str]) -> str:
    return json.dumps({"atoms": sorted(atoms), "hyperedges": sorted(edges)}, sort_keys=True)


def compose_decision(pop, w1, inst, specs: list[ReqSpec]) -> tuple[str, tuple[str, ...], dict[str, object]]:
    """The precedence walk restated on labels (COMPOSE stage)."""
    gen, model, oracle = m1._mex1()
    amap = pop.space.atom_map()
    R = pop.registered_revoked
    RU = R | frozenset(pop.unknown)

    def tri(atom_id: str):
        live_r = kso.profile_live(amap[atom_id].profile, R)
        live_ru = kso.profile_live(amap[atom_id].profile, RU)
        return True if live_ru else (False if not live_r else None)  # None = censored

    if inst.request.kind == "PROPAGATE_DEFEAT":
        accepted = w1.accepted_ids()
        states = {c: tri(f"claim:{c}") for c in accepted}
        if any(v is None for v in states.values()):
            return model.DEFER_CANNOT_CHECK, (), {"censored_claims": sorted(c for c, v in states.items() if v is None)}
        reopened = tuple(c for c in accepted if states[c] is False)
        return (model.SELECTIVELY_REOPEN if reopened else model.PRESERVE), reopened, {}
    ordered = sorted(specs, key=lambda s: MODULE_RANK[s.module])  # stable: emission order within a module
    states = [(s, tri(s.atom_id)) for s in ordered]
    first_invalid = next((k for k, (s, v) in enumerate(states) if v is False), None)
    prefix = states[:first_invalid] if first_invalid is not None else states
    censored_actions = {s.action for s, v in prefix if v is None}
    terminal = states[first_invalid][0].action if first_invalid is not None else model.UPDATE
    action_set = censored_actions | {terminal}
    if len(action_set) > 1:
        return model.DEFER_CANNOT_CHECK, (), {"action_set": sorted(action_set)}
    return terminal, (), {"decisive_atom": states[first_invalid][0].atom_id if first_invalid is not None else ""}


def check_against_oracle(pop, w1, inst, specs: list[ReqSpec]) -> list[str]:
    """CHECK stage: the second reading vs the oracle's request atoms; claim labels vs support."""
    gen, model, oracle = m1._mex1()
    table = oracle.support_table(w1)
    tri = {a: oracle._tri(s) for a, s in table.atoms.items()}
    support = oracle.evaluate_support(w1, tri, table)
    mism: list[str] = []
    if inst.request.kind != "PROPAGATE_DEFEAT":
        theirs = oracle.request_atoms(w1, inst.request, support, table)
        mine = [(s.atom_id, s.module, s.status if s.status is not None else oracle._status(support[s.derived_claim]), s.action) for s in specs]
        them = [(a.atom_id, a.module, a.status, a.action) for a in theirs]
        if mine != them:
            mism.append(f"request atoms differ: mine={mine} oracle={them}")
    amap = pop.space.atom_map()
    R = pop.registered_revoked
    RU = R | frozenset(pop.unknown)
    for c in w1.claims:
        lab = amap[f"claim:{c}"].profile
        mine_tri = True if kso.profile_live(lab, RU) else (False if not kso.profile_live(lab, R) else None)
        if mine_tri != support[c]:
            mism.append(f"claim {c}: label {mine_tri} vs support {support[c]}")
    return mism


@dataclass(frozen=True)
class Budget:
    steps_cap: int
    edge_visits_cap: int
    restarts: int = 1


def solve_instance(pop, w1, inst, exp, *, planted_flip: str | None = None) -> dict[str, object]:
    gen, model, oracle = m1._mex1()
    ks = pop.space
    budget = Budget(steps_cap=2 * len(ks.atoms), edge_visits_cap=2 * len(ks.hyperedges))
    row: dict[str, object] = {"instance_id": inst.instance_id, "family": inst.family, "variant": inst.variant, "request_kind": inst.request.kind,
                              "oracle": {"action": exp.action, "reopened": list(exp.reopened)}, "graph_sha256": graph_sha256(ks)}
    stage_fail: dict[str, str] = {}
    specs = read_request_atoms(w1, inst.request)
    if planted_flip:
        # a planted label flip: revoke the named request atom's evidence (VALID → INVALID)
        i = pop.base_index.get(planted_flip)
        if i is None:
            raise CannotCheck(f"planted flip names an unknown atom {planted_flip}")
        pop = m1.Population(pop.space, pop.governed, pop.base_index, pop.base_status, pop.claim_atom, pop.family_atom, pop.registered_revoked | {i}, pop.unknown)
    R = pop.registered_revoked
    # ATOMIZE
    _, sA = atomize_A(pop, w1, inst)
    _, sB = atomize_B(pop, w1, inst)
    seed_set = frozenset(x for x, v in zip(ks.ids, sA, strict=True) if v > 0)
    expected_seed = {f"req:{inst.instance_id}", f"claim:{inst.request.target_claim_id}"} | ({f"res:{inst.request.result_id}"} if getattr(inst.request, "result_id", "") and f"res:{inst.request.result_id}" in ks.ids else set())
    if seed_set != frozenset(expected_seed) or sA != sB:
        stage_fail["ATOMIZE"] = f"seed set {sorted(seed_set)} vs {sorted(expected_seed)}; A==B {sA == sB}"
    # NAVIGATE (exact fixed point; FOUND iff the target claim carries activation)
    target = f"claim:{inst.request.target_claim_id}"
    atomsA, edgesA, act, (edge_visits, incidences) = reacting_subgraph_exact(ks, sA, R)
    steps_used = len(ks.atoms)
    if steps_used > budget.steps_cap or edge_visits > budget.edge_visits_cap:
        raise CannotCheck(f"budget overrun on {inst.instance_id}: steps {steps_used}/{budget.steps_cap} edge_visits {edge_visits}/{budget.edge_visits_cap}")
    if act[target] > 0:
        nav = "FOUND"
    else:
        support_atoms = sorted(seed_set)
        if target not in m0.ungated_closure(ks, support_atoms):
            nav = "OBSTRUCTION_WITNESSED"
        else:
            nav = "GAP_NOT_FOUND"
        stage_fail["NAVIGATE"] = f"target {target} {nav}"
    # FIRE: label-gated enabling equals the label-only prediction
    enabled = set(kso.enabled_hyperedges(ks, act, Fraction(0, 1), revoked=R))
    amap = ks.atom_map()
    predicted = {e.edge_id for e in ks.hyperedges if kso.profile_live(e.profile, R) and all(kso.profile_live(amap[t].profile, R) for t in e.tails)}
    if enabled != predicted:
        stage_fail["FIRE"] = f"{len(enabled ^ predicted)} hyperedges differ"
    # EXTRACT: every live request atom is in the reacting subgraph
    live_req = [s.atom_id for s in specs if kso.profile_live(amap[s.atom_id].profile, R)]
    missing = [a for a in live_req if a not in atomsA]
    if missing:
        stage_fail["EXTRACT"] = f"live request atoms outside G_Q: {missing}"
    # COMPOSE
    action, reopened, detail = compose_decision(pop, w1, inst, specs)
    # CHECK
    mism = check_against_oracle(pop, w1, inst, specs) if not planted_flip else []
    if mism:
        stage_fail["CHECK"] = mism[0][:300]
    # RENDER
    answer = {"action": action, "reopened": sorted(reopened)}
    if set(answer) != {"action", "reopened"} or action not in model.ACTIONS:
        stage_fail["RENDER"] = "bad shape"
    exact = (action, tuple(sorted(reopened))) == (exp.action, tuple(sorted(exp.reopened)))
    # attribution of an exact answer to the mechanic that produced it: NAVIGATION when every live
    # request atom the walk composes over was reached by extraction; STORE_READ when COMPOSE had to
    # read at least one of them from the store because the walk did not surface it
    exact_by = "" if not exact else ("FOUND_BY_NAVIGATION" if not missing else "FOUND_BY_STORE_READ")
    if not exact and "COMPOSE" not in stage_fail and not any(k in stage_fail for k in ("ATOMIZE", "NAVIGATE", "FIRE", "EXTRACT", "CHECK", "RENDER")):
        stage_fail["COMPOSE"] = f"composed {answer} vs oracle {row['oracle']} given agreeing statuses; detail {detail}"
    attribution = "" if exact else next((s for s in STAGES if s in stage_fail), "ATTRIBUTION_FAILED")
    # translator invariance: byte-identical canonical extraction from the two atomizers
    atomsB, edgesB, _, _ = reacting_subgraph_exact(ks, sB, R)
    invariant = canonical(atomsA, edgesA) == canonical(atomsB, edgesB)
    store_read = bool(missing)  # COMPOSE used >= 1 live request atom the walk did not surface into G_Q
    navigation_only_answer = None if store_read else answer
    row["arms"] = {"KSO_M2_SOLVE": {"answer": answer, "exact": exact, "exact_by": exact_by, "store_read": store_read, "navigation_only_answer": navigation_only_answer,
                                    "dead_request_atoms_read_through_fire": [s.atom_id for s in specs if not kso.profile_live(amap[s.atom_id].profile, R)], "status": "SCORED" if nav == "FOUND" else "OBSTRUCTION" if nav == "OBSTRUCTION_WITNESSED" else "SCORED",
                                    "budget": {"steps": steps_used, "edge_visits": edge_visits, "incidence_visits": incidences, "restarts": 1, "wall_ns": 0, "steps_cap": budget.steps_cap, "edge_visits_cap": budget.edge_visits_cap},
                                    "navigation_outcome": nav, "attribution": attribution, "translator_invariant": invariant,
                                    "extraction_sha256": hashlib.sha256(canonical(atomsA, edgesA).encode()).hexdigest(), "request_atoms": len(specs), "stage_failures": stage_fail, "compose_detail": detail}}
    return row


def prepare(inst):
    gen, model, oracle = m1._mex1()
    w1 = oracle.final_world(inst.world_v0, inst.events)
    pop0 = m1.populate(w1, request=inst.request, request_id=inst.instance_id)
    pop, added = add_request_atoms(pop0, w1, inst)
    return w1, pop0, pop, added


def run_fixtures() -> dict[str, object]:
    gen, model, oracle = m1._mex1()
    rows = []
    for f in gen.known_answer_fixtures():
        inst = model.Instance(f["case_id"], f["family"], "FIXTURE", "fixture", 0, f["world"], f["events"], f["request"])
        w1, exp = oracle.expected_for(f["world"], f["events"], f["request"])
        _, _, pop, _ = prepare(inst)
        row = solve_instance(pop, w1, inst, exp)
        want_re = tuple(f.get("expected_reopened", ())) if f["expected"] == model.SELECTIVELY_REOPEN else ()
        ans = row["arms"]["KSO_M2_SOLVE"]["answer"]
        rows.append({"case_id": f["case_id"], "expected": f["expected"], "expected_reopened": list(want_re), "answer": ans, "oracle_agrees_with_fixture": exp.action == f["expected"] and tuple(exp.reopened) == want_re,
                     "exact_vs_fixture": ans["action"] == f["expected"] and tuple(ans["reopened"]) == tuple(sorted(want_re)), "attribution": row["arms"]["KSO_M2_SOLVE"]["attribution"]})
    return {"n": len(rows), "exact": sum(1 for r in rows if r["exact_vs_fixture"]), "rows": rows}


def run(per_family: int = 5) -> dict[str, object]:
    gen, model, oracle = m1._mex1()
    digests = check_design_drift()
    if not _sources_differ():
        raise CannotCheck("VACUOUS_CONTRAST: the two atomizers share source")
    fixtures = run_fixtures()
    if fixtures["exact"] != fixtures["n"]:
        raise AssertionError(f"G0 known-answer fixtures: {fixtures['exact']}/{fixtures['n']}")
    pairs = gen.generate_split("dev", "ME-X1-DEV-20260902", {f: per_family for f in model.FAMILIES})
    ids = [inst.instance_id for inst, _ in pairs]
    ids_sha = hashlib.sha256("\n".join(ids).encode()).hexdigest()
    if per_family == 5 and ids_sha != digests["ids_sha256"]:
        raise CannotCheck("instance set differs from the seed commitment")
    rows = []
    graph_growth = []
    for inst, exp in pairs:
        w1, pop0, pop, added = prepare(inst)
        row = solve_instance(pop, w1, inst, exp)
        row["request_level_atoms_added"] = len(added)
        row["graph_sha256_before_request_atoms"] = graph_sha256(pop0.space)
        rows.append(row)
        graph_growth.append(len(added))
    n_exact = sum(1 for r in rows if r["arms"]["KSO_M2_SOLVE"]["exact"])
    n_nav = sum(1 for r in rows if r["arms"]["KSO_M2_SOLVE"]["exact_by"] == "FOUND_BY_NAVIGATION")
    n_store = sum(1 for r in rows if r["arms"]["KSO_M2_SOLVE"]["exact_by"] == "FOUND_BY_STORE_READ")
    n_inv = sum(1 for r in rows if r["arms"]["KSO_M2_SOLVE"]["translator_invariant"])
    attributions = {}
    for r in rows:
        a = r["arms"]["KSO_M2_SOLVE"]["attribution"]
        if a:
            attributions[a] = attributions.get(a, 0) + 1
    # G5 must-differ: a planted label flip changes the answer on ≥ 1 instance
    flipped_changes = 0
    flips = 0
    for inst, exp in pairs[:10]:
        w1, _, pop, _ = prepare(inst)
        cands = [s for s in read_request_atoms(w1, inst.request) if s.status == model.STATUS_VALID and s.atom_id in pop.base_index and s.atom_id != "authority"]
        if not cands:
            continue
        flips += 1
        base = solve_instance(pop, w1, inst, exp)["arms"]["KSO_M2_SOLVE"]["answer"]
        flipped = solve_instance(pop, w1, inst, exp, planted_flip=cands[0].atom_id)["arms"]["KSO_M2_SOLVE"]["answer"]
        if flipped != base:
            flipped_changes += 1
    if flips and flipped_changes == 0:
        raise AssertionError("G5: no planted label flip changed an answer")
    terminal = "M2_EXACT_ON_DEV" if (n_exact == len(rows) and n_inv == len(rows)) else ("M2_ATTRIBUTION_FAILED" if "ATTRIBUTION_FAILED" in attributions else "M2_DEFECT_ATTRIBUTED__" + "+".join(sorted(attributions)))
    # informational stage checks on exact instances: not attributions, but findings the design did not predict
    extract_misses = [r["instance_id"] for r in rows if "EXTRACT" in r["arms"]["KSO_M2_SOLVE"]["stage_failures"]]
    dead_targets = [r["instance_id"] for r in rows if r["arms"]["KSO_M2_SOLVE"]["navigation_outcome"] != "FOUND"]
    findings = {
        "EXTRACT_SURPRISE_MISSES_ONE_HOP_REQUEST_ATOMS": {"instances": len(extract_misses), "ids": extract_misses,
            "reading": "on a small graph a 3-seed question gives a one-hop child of the goal atom (fan-out ~13) activation a_Q = a(req)(1-alpha)/k below the uniform background pi, so its reaction surprise is 0 and it falls outside G_Q; COMPOSE reads the compose hyperedge's tails from the store, not G_Q, which is why the answer is still exact. Lever for M2.1: a seed-count-conditioned background or fan-out-aware surprise; not tuned post-outcome here"},
        "TARGET_CLAIM_DEAD_AT_REQUEST_TIME": {"instances": len(dead_targets), "ids": dead_targets,
            "reading": "GAP_NOT_FOUND:WARRANT by the four-valued rule (the target claim is non-live at v1); the decision is still composed from labels, as the registered rule requires"},
    }
    return {
        "schema": "orion.kso.m2-solve-receipt.v1",
        "contract": "KnowledgeSpace.v1-M2",
        "design": {**digests, "design_file": str(DESIGN_MD.relative_to(ROOT)), "frozen_json": str(DESIGN_JSON.relative_to(ROOT))},
        "provenance": {"command": "python research/orion-machine/reference/kso_m2_solve_v1.py --out research/orion-machine/results/KSO_M2_SOLVE_RECEIPT_V1.json", "python": sys.version.split()[0], "split": "dev", "split_seed": "ME-X1-DEV-20260902", "per_family": per_family,
                       "declared_nondeterminism": "none", "shared_with_oracle": "base status readers (source/identity/calibration/independence/transport/evaluator) and MODULE_RANK as registered data; request_atoms and the walk are re-implemented and cross-checked at the CHECK stage"},
        "G0_fixtures": fixtures,
        "G1_exact": {"n": len(rows), "exact": n_exact, "attributions": attributions,
                     "FOUND_BY_NAVIGATION": n_nav, "FOUND_BY_STORE_READ": n_store,
                     "reading": "exact = the store's exactness (labels + registered rule); FOUND_BY_NAVIGATION is the mechanic's own number — the walk surfaced every live request atom COMPOSE used; FOUND_BY_STORE_READ = COMPOSE read at least one live request atom the walk did not surface (EXTRACT finding)"},
        "headline": {"NAVIGATION_EXACT": f"{n_nav}/{len(rows)}", "STORE_EXACT": f"{n_exact}/{len(rows)}", "mechanic_terminal": f"M2_NAVIGATION_EXACT_{n_nav}_OF_{len(rows)}__EXTRACT_ATTRIBUTED" if n_store else "M2_NAVIGATION_EXACT_ALL"},
        "G2_translator_invariance": {"n": len(rows), "invariant": n_inv, "atomizer_sources_differ": True},
        "G3_budget": {"caps": "steps 2|atoms|, edge_visits 2|hyperedges|, restarts 1", "overruns": 0, "max_steps_used": max(r["arms"]["KSO_M2_SOLVE"]["budget"]["steps"] for r in rows), "max_edge_visits": max(r["arms"]["KSO_M2_SOLVE"]["budget"]["edge_visits"] for r in rows)},
        "G5_planted_flip": {"flips": flips, "answers_changed": flipped_changes},
        "request_level_atoms_added_total": sum(graph_growth),
        "findings_informational": findings,
        "instances": rows,
        "terminal": terminal,
        "comparator": "KSO_M2_COMPARATOR_RECEIPT_V1.json (guards lane) joins on instance_id and graph_sha256",
        "authority": "development split; exact agreement is expected by construction (design §0); no novelty, superiority or protected authority",
    }


def _default(o):
    if isinstance(o, Fraction):
        return str(o)
    if isinstance(o, (frozenset, set)):
        return sorted(o)
    raise TypeError(type(o).__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=5)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        result = run(per_family=args.per_family)
        body = lambda r: json.dumps({k: v for k, v in r.items() if k != "provenance"}, sort_keys=True, default=_default)  # noqa: E731
        second = run(per_family=args.per_family)
        result["provenance"]["byte_reproducible_in_process"] = body(result) == body(second)
        result["provenance"]["body_sha256"] = hashlib.sha256(body(result).encode()).hexdigest()
        assert result["provenance"]["byte_reproducible_in_process"]
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}, indent=2))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True, default=_default)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"terminal": result["terminal"], "G1": result["G1_exact"], "G2": result["G2_translator_invariance"], "G0": {"n": result["G0_fixtures"]["n"], "exact": result["G0_fixtures"]["exact"]}, "G5": result["G5_planted_flip"], "body_sha256": result["provenance"]["body_sha256"]}, sort_keys=True))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
