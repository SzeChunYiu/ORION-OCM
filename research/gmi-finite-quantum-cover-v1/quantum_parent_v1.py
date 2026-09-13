"""Source-bound archived quantum parent, independently checked new compilation."""
from pathlib import Path
import hashlib
import importlib.util
import json
from classical_parent_v1 import graph_colorable
from quantum_witness_v1 import verify
from rational_matrix_v1 import dot, require
from itertools import combinations

HERE = Path(__file__).resolve().parent
BINDING = "47a4449fcd946b4e7df9a0f1fa884f20c7978a4766ca7d710b4e117c474c2f0a"


def verify_sources(base=HERE):
    raw = (base / "SOURCE_PARENTS_V1.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == BINDING, "parent binding drift")
    data = json.loads(raw)
    for name, row in data["files"].items():
        raw = (base / "raw" / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"]
                and len(raw) == row["bytes"], "archived parent drift")
    return data


def quantum_parent():
    verify_sources()
    source = HERE / "raw/grand_gmi_quantum_cut_scope_checks_v1.py"
    spec = importlib.util.spec_from_file_location("archived_quantum_scope", source)
    parent = importlib.util.module_from_spec(spec)
    exec(compile(source.read_bytes(), str(source), "exec"), parent.__dict__)
    # Only construct its rational data; legacy assert-based proof checks are not the new verifier.
    rays, edges, states, effects = parent.witness_data()
    require(len(rays) == 14 and len(edges) == 37, "wrong inherited graph")
    clique = (0, 2, 8, 13)
    require(all(dot(rays[i], rays[j]) == 0 for i, j in combinations(clique, 2)),
            "missing dimension-four lower certificate")
    allowed = tuple(tuple(frozenset((0 if x == i else 1,)) if x in (i, j) else None
                          for i, j in edges) for x in range(14))
    task = {"actions": 2, "allowed": allowed}
    result = verify(task, rays, tuple(effects[e] for e in edges))
    native = parent.verify_edge_protocol(states, effects, edges)
    require(native == result["promised_pairs_checked"] == 74, "native Born parent differs")
    colorable, _, visits = graph_colorable(14, edges, 4)
    require(not colorable, "classical lower certificate failed")
    old = json.loads((HERE / "raw/GRAND_GMI_QUANTUM_CUT_SCOPE_RECEIPT_V1.json").read_bytes())
    colors = old["separation"]["classical_five_coloring"]
    require(len(colors) == 14 and set(colors) == set(range(5))
            and all(colors[i] != colors[j] for i, j in edges), "classical upper failed")
    require(result["dimension"] == old["separation"]["quantum_minimum_dimension"] == 4,
            "quantum parent dimension differs")
    return {"classical_minimum_alphabet": 5, "quantum_minimum_dimension": 4,
            "promised_pairs_checked": 74, "compiled_isometries": len(result["isometries"]),
            "receiver_composite_dimension": result["receiver_composite_dimension"],
            "four_color_partial_assignments_visited": visits,
            "parent_result": "MATCH", "new_quantum_advantage_claim": False}
