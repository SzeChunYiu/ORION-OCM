"""L1 meaning-graph bound: historical MAX_EXACT_CANONICAL vs production graphs.

Independent bound is production ``ocm.language.meaning.MAX_EXACT_CANONICAL`` (7).
This capsule does not invent a bound. ``src/`` is not edited. L2/L3 stay locked.
No corpus N1. No NN. Frozen L1 G2 RESULT.json files are not overwritten.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.kso.warrant import CannotCheck, WarrantProfile
from ocm.language.bootstrap import microworld_lexicon
from ocm.language.constructions import (
    Construction,
    Slot,
    match_constructions,
    realise_candidate,
    seed_constructions,
)
from ocm.language.field_bridge import canonical_bound_meaning
from ocm.language.interpret import Verdict, interpret, tokenize
from ocm.language.lexicon import Category, Lexeme, Sense
from ocm.language.meaning import (
    MAX_EXACT_CANONICAL,
    MEdge,
    MNode,
    MeaningGraph,
    _encoding,
    canonical,
    example_meanings,
    isomorphic,
    wl_collision_witness,
    wl1_hash,
)
from ocm.language.meaning_tree import canonical_any, is_tree
from ocm.language.microworld import generate as generate_microworld

SCHEMA = "ocm.l1.meaning-graph-bound.v1"
ISSUE = 165
SALT = "orion-ocm-l1-meaning-graph-bound-v1"
SCOPE_ID = "l1-microworld.meaning-graph-bound.v1"

PERM_BUDGET = math.factorial(MAX_EXACT_CANONICAL)
TREE_MEASURED_NODES = 16
DISTINCT_MEASURED_NODES = 16

PLANTED_ADJS = ("amber", "ivory", "ochre", "umber", "violet", "saffron", "pewter")
SEED_PROBE = "the robot opened the red door"
PLANTED_UTTERANCE = "amber ivory ochre umber violet saffron pewter robot opened the door"

V1_SURFACES = frozenset({"red", "blue", "green", "cube", "sphere", "pyramid", "two"})
V2_CONTENT_SURFACES = frozenset(
    {"otter", "heron", "lantern", "casket", "inspect", "lynx", "goblet", "conceal", "bank"}
)
V3_CONTENT_SURFACES = frozenset(
    {"ibis", "stoat", "chalice", "amulet", "reveal", "unseal", "jackal", "reliquary", "bury"}
)

LEGAL_TERMINALS = (
    "GRAPH_BOUND_EXCEEDED_AT_SCOPE",
    "GRAPHS_INSIDE_HISTORICAL_BOUND_AT_SCOPE",
    "CANNOT_CHECK_NO_HISTORICAL_BOUND",
)

HISTORICAL_CITATIONS = (
    "src/ocm/language/meaning.py:MAX_EXACT_CANONICAL",
    "docs/theorems/OCM_LANGUAGE_OBLIGATION_REGISTRY_V1.json:KS-T34",
    "research/l0-bootstrap-audit-v1:G5_canonical_max",
    "tests/m3/test_meaning_graph.py",
)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def git_blob_sha1(path: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "hash-object", str(path)], cwd=REPO, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return hashlib.sha1(path.read_bytes()).hexdigest()


def graph_stats(g: MeaningGraph) -> dict[str, Any]:
    return {
        "n_nodes": len(g.nodes),
        "n_edges": len(g.edges),
        "is_tree": is_tree(g),
        "colour_perm_count": colour_perm_count(g),
        "labels": [n.label for n in g.nodes],
    }


def colour_perm_count(g: MeaningGraph) -> int:
    counts: dict[str, int] = {}
    for n in g.nodes:
        counts[n.colour()] = counts.get(n.colour(), 0) + 1
    n = 1
    for k in counts.values():
        n *= math.factorial(k)
    return n


def canonical_under_perm_budget(g: MeaningGraph) -> tuple[MeaningGraph, str]:
    """Same enumerator as production ``canonical``, gated by historical 7! work, not |V|."""
    work = colour_perm_count(g)
    if work > PERM_BUDGET:
        raise CannotCheck(
            f"colour-class permutation budget {PERM_BUDGET} exceeded; fragment needs {work}"
        )
    by_colour: dict[str, list[str]] = {}
    for n in g.nodes:
        by_colour.setdefault(n.colour(), []).append(n.node_id)
    classes = [by_colour[c] for c in sorted(by_colour)]
    best: tuple[str, tuple[str, ...]] | None = None
    for perms in itertools.product(*(itertools.permutations(c) for c in classes)):
        order = tuple(v for block in perms for v in block)
        enc = _encoding(g, order)
        if best is None or enc < best[0]:
            best = (enc, order)
    assert best is not None
    enc, order = best
    mapping = {v: f"n{i}" for i, v in enumerate(order)}
    return g.relabel(mapping), hashlib.sha256(enc.encode("utf-8")).hexdigest()


def try_call(fn, *args) -> dict[str, Any]:
    try:
        value = fn(*args)
        return {"ok": True, "error": None, "value": value}
    except CannotCheck as exc:
        return {"ok": False, "error": "CannotCheck", "detail": str(exc)}
    except Exception as exc:  # pragma: no cover — unexpected production errors
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)}


def identical_colour_graph(n: int) -> MeaningGraph:
    nodes = tuple(MNode(f"e{i}", "entity", "x") for i in range(n))
    return MeaningGraph(nodes, ())


def distinct_colour_graph(n: int) -> MeaningGraph:
    nodes = tuple(MNode(f"e{i}", "entity", f"lab{i}") for i in range(n))
    return MeaningGraph(nodes, ())


def modifier_chain_tree(n: int) -> MeaningGraph:
    nodes = [MNode(f"n{i}", "entity", f"chain{i}") for i in range(n)]
    edges = [MEdge("MODIFIES", (f"n{i}",), (f"n{i + 1}",)) for i in range(n - 1)]
    return MeaningGraph(tuple(nodes), tuple(edges), root="n0")


def stacked_adj_construction() -> Construction:
    def stack(b: Mapping[str, Any]) -> MeaningGraph:
        ph = b["np"]
        adj = b["a"]
        mapping = {
            n.node_id: ("x" if n.node_id == ph.head_node else f"x.{n.node_id}")
            for n in ph.meaning.nodes
        }
        g = ph.meaning.relabel(mapping)
        label = adj.sense.concept if adj.sense else adj.lemma
        prop = MNode("p", "property", label)
        return MeaningGraph(
            (prop,) + g.nodes,
            (MEdge("MODIFIES", ("p",), ("x",)),) + g.edges,
            root="x",
        )

    return Construction(
        "planted:stack-adj",
        "stacked_np",
        (Slot("a", Category.ADJ), Slot("np", Category.NOUN, phrase="NP")),
        stack,
        WarrantProfile.of({f"{SALT}:stack-adj"}),
        produces="NP",
        head_slot="a",
        head_node="x",
    )


def planted_lexicon():
    lx = microworld_lexicon()
    for adj in PLANTED_ADJS:
        ev = f"{SALT}:lex:{adj}"
        lx.add(
            Lexeme(
                adj,
                Category.ADJ,
                (Sense(f"l1mgb:{adj}", adj, "property", WarrantProfile.of({ev})),),
                warrant=WarrantProfile.of({ev}),
            )
        )
    return lx


def frozen_result_intact(name: str, schema: str) -> bool:
    path = REPO / "research" / name / "RESULT.json"
    if not path.exists():
        return name.endswith("v4")
    data = json.loads(path.read_text())
    return data.get("schema") == schema


def measure_examples() -> dict[str, Any]:
    rows = {}
    max_nodes = 0
    max_edges = 0
    for utt, g in example_meanings().items():
        st = graph_stats(g)
        rows[utt] = st
        max_nodes = max(max_nodes, st["n_nodes"])
        max_edges = max(max_edges, st["n_edges"])
        if st["n_nodes"] <= MAX_EXACT_CANONICAL:
            canonical(g)
    return {"rows": rows, "max_nodes": max_nodes, "max_edges": max_edges, "n": len(rows)}


def measure_microworld() -> dict[str, Any]:
    corpus = generate_microworld(seed=SALT)
    max_nodes = max(len(e.meaning.nodes) for e in corpus)
    max_edges = max(len(e.meaning.edges) for e in corpus)
    families = sorted({e.family for e in corpus})
    for e in corpus:
        if len(e.meaning.nodes) <= MAX_EXACT_CANONICAL:
            canonical(e.meaning)
    return {
        "n": len(corpus),
        "max_nodes": max_nodes,
        "max_edges": max_edges,
        "families": families,
    }


def measure_seed_interpret() -> dict[str, Any]:
    lx = microworld_lexicon()
    cons = seed_constructions()
    r = interpret(SEED_PROBE, lx, cons)
    assert r.verdict is Verdict.INTERPRETED and r.meaning is not None
    st = graph_stats(r.meaning)
    canonical(r.meaning)
    two_adj = interpret("the big robot opened the small door", lx, cons)
    assert two_adj.verdict is Verdict.INTERPRETED and two_adj.meaning is not None
    st2 = graph_stats(two_adj.meaning)
    return {
        "probe": SEED_PROBE,
        "verdict": r.verdict.value,
        **st,
        "two_adj_nodes": st2["n_nodes"],
        "max_nodes": max(st["n_nodes"], st2["n_nodes"]),
    }


def planted_clause_meanings() -> list[MeaningGraph]:
    lx = planted_lexicon()
    cons = list(seed_constructions()) + [stacked_adj_construction()]
    toks = tokenize(PLANTED_UTTERANCE)
    per = [list(lx.analyse(t).readings) for t in toks]
    matches = match_constructions(cons, per)
    return [realise_candidate(m).meaning for m in matches]


def measure_planted_exceed() -> dict[str, Any]:
    meanings = planted_clause_meanings()
    sizes = [len(m.nodes) for m in meanings]
    max_nodes = max(sizes) if sizes else 0
    max_edges = max((len(m.edges) for m in meanings), default=0)
    sample = max(meanings, key=lambda g: len(g.nodes)) if meanings else None
    prod = try_call(canonical, sample) if sample is not None else {"ok": False, "error": "no_parse"}
    tree = (
        try_call(canonical_any, sample)
        if sample is not None
        else {"ok": False, "error": "no_parse"}
    )
    budget = (
        try_call(canonical_under_perm_budget, sample)
        if sample is not None
        else {"ok": False, "error": "no_parse"}
    )
    interp = try_call(interpret, PLANTED_UTTERANCE, planted_lexicon(), list(seed_constructions()) + [stacked_adj_construction()])
    interp_exceeded = (not interp["ok"]) and interp.get("error") == "CannotCheck"
    if sample is not None:
        bindings = {n.node_id: f"atom:{n.node_id}" for n in sample.nodes}
        bridge = try_call(canonical_bound_meaning, sample, bindings)
    else:
        bridge = {"ok": False, "error": "no_parse"}
    digest = budget["value"][1] if budget.get("ok") else None
    return {
        "utterance": PLANTED_UTTERANCE,
        "n_candidates": len(meanings),
        "max_nodes": max_nodes,
        "max_edges": max_edges,
        "sample_is_tree": is_tree(sample) if sample is not None else None,
        "sample_colour_perm_count": colour_perm_count(sample) if sample is not None else None,
        "production_canonical": {k: prod[k] for k in ("ok", "error") if k in prod},
        "production_canonical_detail": prod.get("detail"),
        "tree_canonical_any": {k: tree[k] for k in ("ok", "error") if k in tree},
        "perm_budget_canonical": {"ok": budget.get("ok"), "error": budget.get("error"), "digest": digest},
        "interpret_cannot_check": interp_exceeded,
        "interpret_error": interp.get("error"),
        "interpret_detail": interp.get("detail"),
        "field_bridge": {k: bridge[k] for k in ("ok", "error") if k in bridge},
        "exceeds_historical_node_bound": max_nodes > MAX_EXACT_CANONICAL,
    }


def measure_bound_probes() -> dict[str, Any]:
    at = identical_colour_graph(MAX_EXACT_CANONICAL)
    over = identical_colour_graph(MAX_EXACT_CANONICAL + 1)
    distinct = distinct_colour_graph(DISTINCT_MEASURED_NODES)
    tree = modifier_chain_tree(TREE_MEASURED_NODES)
    relabelled_tree = tree.relabel(
        {f"n{i}": f"m{(i * 3 + 1) % TREE_MEASURED_NODES}" for i in range(TREE_MEASURED_NODES)}
    )
    at_ok = try_call(canonical, at)
    over_ok = try_call(canonical, over)
    distinct_prod = try_call(canonical, distinct)
    distinct_budget = try_call(canonical_under_perm_budget, distinct)
    tree_prod = try_call(canonical, tree)
    tree_any = try_call(canonical_any, tree)
    tree_any_relabel = try_call(canonical_any, relabelled_tree)
    over_budget = try_call(canonical_under_perm_budget, over)
    at_budget = try_call(canonical_under_perm_budget, at)
    at_digest = canonical(at)[1] if at_ok["ok"] else None
    at_budget_digest = at_budget["value"][1] if at_budget.get("ok") else None
    wl_a, wl_b = wl_collision_witness()
    return {
        "at_bound_nodes": MAX_EXACT_CANONICAL,
        "at_bound_production_canonical": at_ok["ok"],
        "at_bound_relabel_invariant": isomorphic(at, at.relabel({f"e{i}": f"z{i}" for i in range(MAX_EXACT_CANONICAL)})),
        "beyond_identical_production_cannot_check": (not over_ok["ok"]) and over_ok.get("error") == "CannotCheck",
        "beyond_identical_perm_budget_cannot_check": (not over_budget["ok"]) and over_budget.get("error") == "CannotCheck",
        "beyond_identical_perm_count": colour_perm_count(over),
        "distinct_colour_nodes": DISTINCT_MEASURED_NODES,
        "distinct_production_cannot_check": (not distinct_prod["ok"]) and distinct_prod.get("error") == "CannotCheck",
        "distinct_perm_budget_ok": distinct_budget.get("ok") is True,
        "distinct_perm_count": colour_perm_count(distinct),
        "tree_nodes": TREE_MEASURED_NODES,
        "tree_is_tree": is_tree(tree),
        "tree_production_cannot_check": (not tree_prod["ok"]) and tree_prod.get("error") == "CannotCheck",
        "tree_ahu_ok": tree_any.get("ok") is True,
        "tree_ahu_relabel_invariant": tree_any.get("ok") and tree_any_relabel.get("ok") and tree_any["value"] == tree_any_relabel["value"],
        "tree_digest_prefix": (tree_any["value"][:5] if tree_any.get("ok") else None),
        "perm_budget_agrees_at_bound": at_ok["ok"] and at_budget.get("ok") and at_digest == at_budget_digest,
        "wl_collides": wl1_hash(wl_a) == wl1_hash(wl_b),
        "wl_not_isomorphic": not isomorphic(wl_a, wl_b),
    }


def historical_bound_record() -> dict[str, Any]:
    meaning_src = (REPO / "src" / "ocm" / "language" / "meaning.py").read_text()
    registry = json.loads((REPO / "docs" / "theorems" / "OCM_LANGUAGE_OBLIGATION_REGISTRY_V1.json").read_text())
    ks_t34 = next(o for o in registry["obligations"] if o["id"] == "KS-T34")
    l0 = json.loads((REPO / "research" / "l0-bootstrap-audit-v1" / "INVENTORY.json").read_text())
    g5 = next(x for x in l0["items"] if x.get("id") == "G5_canonical_max")
    present = (
        "MAX_EXACT_CANONICAL = 7" in meaning_src
        and MAX_EXACT_CANONICAL == 7
        and ks_t34.get("limitation") == "exact only up to the registered bound MAX_EXACT_CANONICAL = 7"
        and g5.get("max_exact_canonical") == 7
    )
    return {
        "independent": present,
        "kind": "max_nodes",
        "value": MAX_EXACT_CANONICAL if present else None,
        "edge_bound_invented": False,
        "citations": list(HISTORICAL_CITATIONS),
        "ks_t34_limitation": ks_t34.get("limitation"),
        "l0_max_exact_canonical": g5.get("max_exact_canonical"),
        "meaning_blob": git_blob_sha1(REPO / "src" / "ocm" / "language" / "meaning.py"),
    }


def decide_terminal(
    historical: dict[str, Any],
    examples: dict[str, Any],
    microworld: dict[str, Any],
    seed: dict[str, Any],
    planted: dict[str, Any],
    probes: dict[str, Any],
) -> str:
    if not historical["independent"] or historical["value"] is None:
        return "CANNOT_CHECK_NO_HISTORICAL_BOUND"
    bound = historical["value"]
    production_max = max(examples["max_nodes"], microworld["max_nodes"], seed["max_nodes"], planted["max_nodes"])
    exceeded = (
        planted["exceeds_historical_node_bound"]
        or production_max > bound
        or planted["interpret_cannot_check"]
    )
    if exceeded:
        return "GRAPH_BOUND_EXCEEDED_AT_SCOPE"
    if not probes["at_bound_production_canonical"] or not probes["beyond_identical_production_cannot_check"]:
        return "GRAPH_BOUND_EXCEEDED_AT_SCOPE"
    return "GRAPHS_INSIDE_HISTORICAL_BOUND_AT_SCOPE"


def main(out: Path) -> dict[str, Any]:
    historical = historical_bound_record()
    examples = measure_examples()
    microworld = measure_microworld()
    seed = measure_seed_interpret()
    planted = measure_planted_exceed()
    probes = measure_bound_probes()
    v1_ok = frozen_result_intact("l1-linguistic-g2-v1", "ocm.l1.linguistic-g2.v1")
    v2_ok = frozen_result_intact("l1-linguistic-g2-v2", "ocm.l1.linguistic-g2.v2")
    v3_ok = frozen_result_intact("l1-linguistic-g2-v3", "ocm.l1.linguistic-g2.v3")
    v4_path = REPO / "research" / "l1-linguistic-g2-v4" / "RESULT.json"
    v4_ok = (not v4_path.exists()) or frozen_result_intact("l1-linguistic-g2-v4", "ocm.l1.linguistic-g2.v4")
    terminal = decide_terminal(historical, examples, microworld, seed, planted, probes)
    seed_max = max(examples["max_nodes"], microworld["max_nodes"], seed["max_nodes"])
    earned = "EARNED_AT_SCOPE"
    checklist = {
        "historical_bound_independent": earned if historical["independent"] else "CANNOT_CHECK_NO_HISTORICAL_BOUND",
        "exact_canonicalization": earned if probes["at_bound_production_canonical"] and probes["at_bound_relabel_invariant"] and probes["wl_not_isomorphic"] else "OPEN",
        "exact_canonicalization_fail_closed_beyond_bound": earned if probes["beyond_identical_production_cannot_check"] else "OPEN",
        "meaning_graphs_beyond_bound": (
            "GRAPH_BOUND_EXCEEDED_AT_SCOPE"
            if planted["exceeds_historical_node_bound"]
            else "CANNOT_CHECK_MICROWORLD_SMALL"
            if seed_max <= historical["value"]
            else "OPEN"
        ),
        "seed_inventory_inside_bound": earned if seed_max <= historical["value"] else "GRAPH_BOUND_EXCEEDED_AT_SCOPE",
        "tree_ahu_bound_raised": earned if probes["tree_ahu_ok"] and probes["tree_ahu_relabel_invariant"] else "OPEN",
        "perm_budget_restatement": earned if probes["perm_budget_agrees_at_bound"] and probes["distinct_perm_budget_ok"] and probes["beyond_identical_perm_budget_cannot_check"] else "OPEN",
        "wl_not_canonical": earned if probes["wl_collides"] and probes["wl_not_isomorphic"] else "OPEN",
        "acquire_corpus_scale_lexicon": "CANNOT_CHECK_MINIATURE_MICROWORLD",
        "ud_alignment": "CANNOT_CHECK_NO_UD_IN_THIS_STUDY",
        "open_weight_lm_reference": "CANNOT_CHECK_NO_MODEL_WEIGHTS",
        "l2": "LOCKED",
        "l3": "LOCKED",
    }
    result = {
        "schema": SCHEMA,
        "issue": ISSUE,
        "terminal": terminal,
        "git_head": git_head(),
        "salt": SALT,
        "scope": SCOPE_ID,
        "historical_bound": historical,
        "raised_bounds": {
            "colour_class_permutation_budget": {
                "kind": "max_colour_class_permutations",
                "value": PERM_BUDGET,
                "mechanism": "exhaustive colour-class enumeration identical to canonical(); node-count gate replaced by historical worst-case work 7!",
                "worst_case_nodes_unchanged": MAX_EXACT_CANONICAL,
                "distinct_colour_nodes_measured": DISTINCT_MEASURED_NODES,
                "production_node_cutoff_unchanged": True,
            },
            "tree_ahu": {
                "kind": "max_nodes_trees_measured",
                "value": TREE_MEASURED_NODES,
                "mechanism": "production ocm.language.meaning_tree.canonical_any AHU encoding",
                "production_module": "ocm.language.meaning_tree",
                "digest_prefix_above_bound": "tree:",
            },
        },
        "examples": {k: examples[k] for k in ("n", "max_nodes", "max_edges")},
        "microworld": microworld,
        "seed_interpret": seed,
        "planted_recursive_np": planted,
        "bound_probes": probes,
        "seed_inventory_max_nodes": seed_max,
        "production_pipeline_max_nodes": max(seed_max, planted["max_nodes"]),
        "l2_started": False,
        "l3_started": False,
        "neural_net": False,
        "corpus_n1": False,
        "production_src_edited": False,
        "v1_result_intact": v1_ok,
        "v2_result_intact": v2_ok,
        "v3_result_intact": v3_ok,
        "v4_result_intact": v4_ok,
        "v4_present": v4_path.exists(),
        "checklist": checklist,
        "claim_ceiling": (
            "Planted recursive stacked-NP graphs through production interpret/canonical "
            "exceed MAX_EXACT_CANONICAL=7 and fail closed. Seed inventory stays inside. "
            "AHU raises a finite measured tree bound. Permutation-budget restatement is "
            "recorded, not patched into src/. Not corpus-scale N1. L2/L3 locked."
        ),
        "not_issued": ["L2", "L3", "N1_CORPUS", "NN"],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "terminal": terminal,
                "historical_bound": historical["value"],
                "seed_max_nodes": seed_max,
                "planted_max_nodes": planted["max_nodes"],
                "interpret_cannot_check": planted["interpret_cannot_check"],
                "tree_ahu": probes["tree_ahu_ok"],
                "perm_budget_distinct": probes["distinct_perm_budget_ok"],
            }
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
