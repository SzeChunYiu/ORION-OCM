"""Generate the sec-9 root registry JSONs FROM code (single source of truth).

Emits MORPHOLOGY_GENOME_V1.json, COGNITIVE_UNIT_CONTRACT_V1.json,
DESCRIPTOR_REGISTRY_V1.json, OBJECTIVE_REGISTRY_V1.json,
TASK_ECOLOGY_V1.json, PROTOCOL_V1.json at the capsule root.
Rerun after any vocabulary change; the emitted digest goes into PROTOCOL_V1.json.
Usage: python3 gen_registries.py <capsule_root>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

from morphology.schema import (EXECUTIVE_FAMILIES, FIELD_FAMILIES,  # noqa: E402
                               GENOME_SCHEMA_ID, LEARNING_FAMILIES,
                               MEMORY_FAMILIES, OPERATORS, REVISION_FAMILIES,
                               TOPOLOGY_FAMILIES, UNIT_CONTRACT_ID, UNIT_TYPES)
from morphology.direct_genome import CENSUS_BOUND_V1, census_size  # noqa: E402
from evaluation.descriptors import DESCRIPTOR_REGISTRY  # noqa: E402
from evaluation.invariants import CAPABILITY_FLOOR_V1  # noqa: E402
from evaluation.objectives import B_REF, MAXIMIZE, OBJECTIVE_NAMES, W_REF  # noqa: E402

CREATED = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def dump(name, obj):
    path = os.path.join(ROOT, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    return name


def jshash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


genome = {
    "schema_id": GENOME_SCHEMA_ID,
    "created_utc": CREATED,
    "genome": "G = (F_arch, U, T, O_basis, Pi_arch, L, R, K, theta); C excluded",
    "field_families": FIELD_FAMILIES,
    "unit_types": UNIT_TYPES,
    "topology_families": list(TOPOLOGY_FAMILIES),
    "operator_basis": list(OPERATORS),
    "pi_architectures": EXECUTIVE_FAMILIES,
    "learning_families": list(LEARNING_FAMILIES),
    "revision_families": list(REVISION_FAMILIES),
    "memory_families": list(MEMORY_FAMILIES),
    "theta": "bounded numeric parameters per organism; digested into genotype_digest",
}
contract = {
    "contract_id": UNIT_CONTRACT_ID,
    "created_utc": CREATED,
    "units": UNIT_TYPES,
    "rules": [
        "identity/warrant can only be minted by non-approximate units over non-approximate fields",
        "approximate units (assoc_similarity, approx_projection_vsa fields) emit proposals WITHOUT warrant",
        "every unit's prior is charged (bytes) at compile time; no free structure",
        "all work (acquisition/reasoning/verification/maintenance/revision) is metered and charged",
    ],
}
descriptors = {
    "registry_id": "DescriptorRegistryV1",
    "created_utc": CREATED,
    "archives": {k: {"dims": list(v["dims"]),
                     "bounds": ([list(b) for b in v["bounds"]]
                                if "bounds" in v else None),
                     "kind": v.get("kind", "grid")}
                 for k, v in DESCRIPTOR_REGISTRY.items()},
    "grid_resolution": 10,
    "cvt_k": 64,
}
objectives = {
    "registry_id": "ObjectiveRegistryV1",
    "created_utc": CREATED,
    "names": list(OBJECTIVE_NAMES),
    "maximized": sorted(MAXIMIZE),
    "dev_score": {"formula": "capability - 0.5*((work_total/w_ref + persistent_bytes/b_ref)/2)",
                  "w_ref": W_REF, "b_ref": B_REF, "frozen": "2026-09-09 pre-score"},
    "capability_floor": CAPABILITY_FLOOR_V1,
}
ecology = {
    "ecology_id": "TaskEcologyV1",
    "created_utc": CREATED,
    "world_families": ["method_acq", "composition", "scoped_failure", "repr_twin",
                       "revocation", "probe", "similarity_recall", "family_variant"],
    "note": "per-family solved/total in evaluation.per_family; lexicase cases = families + cost axes",
    "census_bound": {k: (list(v) if isinstance(v, (list, tuple)) else v)
                     for k, v in CENSUS_BOUND_V1.items()},
    "census_size": census_size(),
}
protocol = {
    "protocol_id": "ZOO221_PROTOCOL_V1",
    "created_utc": CREATED,
    "stages": ["MZ-D0 repo/literature freeze", "MZ-D1 genome/contract/compiler",
               "MZ-D2 census FIRST then optimizer calibration",
               "MZ-D3 QD generation campaign", "MZ-D5 alternate encodings",
               "MZ-D6 LUNARC harness", "MZ-D7 lifetime tranche",
               "MZ-D8 islands/open-ended", "MZ-D9 hostile tests"],
    "invariants": [
        "evaluation deterministic and receipt-chained (sha256 per record)",
        "hard gates executed not logged; infeasible genomes never enter archives",
        "denominators frozen prospectively (FREEZE_V1.json) before scored outcomes",
        "3+ seeds; same-eval-count and same-CPU-hour comparisons both reported",
        "elites never self-adopt; adoption only via #217 protocol",
    ],
    "component_digests": {
        "genome": jshash(genome), "contract": jshash(contract),
        "descriptors": jshash(descriptors), "objectives": jshash(objectives),
        "ecology": jshash(ecology),
    },
}
for name, obj in [("MORPHOLOGY_GENOME_V1.json", genome),
                  ("COGNITIVE_UNIT_CONTRACT_V1.json", contract),
                  ("DESCRIPTOR_REGISTRY_V1.json", descriptors),
                  ("OBJECTIVE_REGISTRY_V1.json", objectives),
                  ("TASK_ECOLOGY_V1.json", ecology),
                  ("PROTOCOL_V1.json", protocol)]:
    print(dump(name, obj))
