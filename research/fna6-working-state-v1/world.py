"""FNA-6 world: population, two-obligation stream, oracle.

Population = production ``ocm.kso.checks.random_space`` (salt-seeded, same generator and
scale as the #216 MSC world — nothing here is authored to favour an arm). The stream is a
frozen interleave of per-obligation serves, admissions, evidence revocations and one
mid-stream catalogue drift. Ground truth for every serve is production ``gated_closure``
at the stream state where the serve runs; the judge is never charged to arms.

Python 3.8-compatible syntax; imports production ocm.kso (3.10+ at runtime).
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

from ocm.kso import checks as prod_checks  # noqa: E402
from ocm.kso.navigation import gated_closure  # noqa: E402
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace  # noqa: E402
from ocm.kso.warrant import WarrantProfile  # noqa: E402

SALT_POP = "ocm-fna6-v1-20260909/pop-01"
SALT_SEEDS = "ocm-fna6-v1-20260909/seeds-02"
SALT_TARGETS = "ocm-fna6-v1-20260909/targets-03"
SALT_UPDATES = "ocm-fna6-v1-20260909/updates-04"
SALT_DRIFT = "ocm-fna6-v1-20260909/drift-05"
SALT_LOCNULL = "ocm-fna6-v1-20260909/locnull-06"

N_ATOMS = 480
N_EDGES = 1280
N_EVIDENCE = 24
SERVES_PER_OB = 24
N_UPDATES = 12
DRIFT_AFTER_SERVE = 23

RELS = ("DEPENDENCE", "SUPPORT", "CONSTRAINT", "RESTRICTION",
        "EMBEDDING", "SCALE_CHANGE", "BOUNDARY_CHANGE",
        "REPRESENTATION_TRANSPORT", "DECISION_TRANSPORT", "COMPOSITION")


def stable_seed(salt: str) -> int:
    return int(hashlib.sha256(salt.encode("utf-8")).hexdigest(), 16) % (2 ** 32)


def build_field(n_atoms: int = N_ATOMS, n_edges: int = N_EDGES,
                n_evidence: int = N_EVIDENCE, salt: str = SALT_POP
                ) -> Tuple[KnowledgeSpace, Dict[str, object]]:
    rng = random.Random(stable_seed(salt))
    ks = prod_checks.random_space(rng, n_atoms=n_atoms, n_edges=n_edges, n_evidence=n_evidence)
    meta = {"salt": salt, "n_atoms": len(ks.atoms), "n_edges": len(ks.hyperedges),
            "evidence_universe": sorted(int(x) for x in ks.evidence_universe())}
    return ks, meta


def oracle(ks: KnowledgeSpace, seed: str, target: str, revoked) -> bool:
    """External judge: production gated_closure. Never charged to any arm."""
    return target in gated_closure(ks, [seed], revoked)


def _pick_target(rng: random.Random, ks: KnowledgeSpace, seed: str, ids: List[str],
                 quotas: List[int], revoked) -> Tuple[str, bool]:
    """Bounded rejection sampling with a deterministic fallback (terminates always).

    Polarity is best-effort balanced; if one polarity is exhausted in the whole
    population the actual counts are whatever they are (recorded in the stream).
    """
    for _ in range(1000):
        t = rng.choice(ids)
        if t == seed:
            continue
        truth = oracle(ks, seed, t, revoked)
        if quotas[0 if truth else 1] > 0:
            return t, truth
    for t in ids:  # deterministic fallback
        if t == seed:
            continue
        truth = oracle(ks, seed, t, revoked)
        if quotas[0 if truth else 1] > 0:
            return t, truth
    t = rng.choice([x for x in ids if x != seed])
    return t, oracle(ks, seed, t, revoked)


# ---------------------------------------------------------------------------
# Stream construction: frozen once by salts, replayed identically by every arm.
# ---------------------------------------------------------------------------

def _pick_seeds(ks: KnowledgeSpace, salt: str) -> List[str]:
    rng = random.Random(stable_seed(salt))
    live = [a.atom_id for a in ks.atoms if a.is_live(())]
    return rng.sample(live, 2)


def build_stream(field: KnowledgeSpace, seeds: List[str] = None,
                 serves_per_ob: int = SERVES_PER_OB, n_updates: int = N_UPDATES,
                 drift_after: int = DRIFT_AFTER_SERVE,
                 salt_seeds: str = SALT_SEEDS, salt_targets: str = SALT_TARGETS,
                 salt_updates: str = SALT_UPDATES, salt_drift: str = SALT_DRIFT
                 ) -> Dict[str, object]:
    if seeds is None:
        seeds = _pick_seeds(field, salt_seeds)
    rng_t = random.Random(stable_seed(salt_targets))
    rng_u = random.Random(stable_seed(salt_updates))
    rng_d = random.Random(stable_seed(salt_drift))
    ks = field
    revoked = set()
    ids = list(ks.ids)
    ev_universe = sorted(int(x) for x in field.evidence_universe())
    events: List[Dict[str, object]] = []
    quotas = {0: [serves_per_ob // 2, serves_per_ob - serves_per_ob // 2],
              1: [serves_per_ob // 2, serves_per_ob - serves_per_ob // 2]}
    served = {0: 0, 1: 0}
    n_serves = 2 * serves_per_ob
    update_slot = 0
    drift_done = False
    idx = 0
    while idx < n_serves:
        ob = idx % 2
        # choose a target balancing polarity at the CURRENT stream state
        t, truth = _pick_target(rng_t, ks, seeds[ob], ids, quotas[ob], frozenset(revoked))
        quotas[ob][0 if truth else 1] -= 1
        events.append({"kind": "serve", "idx": idx, "ob": ob, "seed": seeds[ob],
                       "target": t, "truth": bool(truth),
                       "revoked_at_serve": sorted(revoked)})
        served[ob] += 1
        idx += 1
        if idx - 1 == drift_after and not drift_done:
            # catalogue drift: retract one salt-chosen edge, kill one salt-chosen
            # non-seed atom's warrant
            edge = rng_d.choice(list(ks.hyperedges))
            cand = [a.atom_id for a in ks.atoms if a.atom_id not in seeds]
            atom_id = rng_d.choice(cand)
            events.append({"kind": "drift", "after": idx - 1,
                           "edge_id": edge.edge_id, "atom_id": atom_id})
            ks = ks.without(edge_ids=[edge.edge_id])
            old = ks.atom(atom_id)
            ks = ks.replace_atom(Atom(atom_id, old.atom_type, WarrantProfile.zero(),
                                      quarantined=old.quarantined))
            drift_done = True
        if (idx - 1) % 4 == 3 and update_slot < n_updates:
            if update_slot % 2 == 0:
                n_new = rng_u.randint(3, 7)
                new_edges = []
                for j in range(n_new):
                    tail = rng_u.choice(ids)
                    head = rng_u.choice([x for x in ids if x != tail])
                    rel = rng_u.choice(RELS)
                    wp = WarrantProfile.certified([frozenset([rng_u.choice(ev_universe)])])
                    new_edges.append(Hyperedge("adm_%d_%d" % (update_slot, j),
                                               (tail,), (head,), rel, warrant=wp))
                events.append({"kind": "admission", "after": idx - 1,
                               "edges": [{"id": e.edge_id, "tails": list(e.tails),
                                          "heads": list(e.heads), "rel": e.relation_type}
                                         for e in new_edges],
                               "_edges": new_edges})
                ks = ks.with_edges(*new_edges)
            else:
                cand = rng_u.sample(ev_universe, min(8, len(ev_universe)))
                pick = None
                for c in cand:
                    if any(not a.is_live(revoked | {c}) and a.is_live(revoked)
                           for a in ks.atoms):
                        pick = c
                        break
                if pick is None:
                    pick = rng_u.choice(cand)
                events.append({"kind": "revocation", "after": idx - 1, "evidence": int(pick)})
                revoked = revoked | {pick}
            update_slot += 1
    return {"seeds": seeds, "events": events,
            "final_revoked": sorted(revoked),
            "n_serves": n_serves, "drift_done": drift_done,
            "n_updates_used": update_slot}


def replay(field: KnowledgeSpace, stream: Dict[str, object]) -> Iterator[Tuple[str, Dict[str, object], KnowledgeSpace, frozenset]]:
    """Yield (kind, event, ks, revoked) in frozen stream order."""
    ks = field
    revoked = set()
    for ev in stream["events"]:
        if ev["kind"] == "serve":
            yield ("serve", ev, ks, frozenset(revoked))
        elif ev["kind"] == "admission":
            ks = ks.with_edges(*ev["_edges"])
            yield ("update", ev, ks, frozenset(revoked))
        elif ev["kind"] == "revocation":
            revoked = revoked | {ev["evidence"]}
            yield ("update", ev, ks, frozenset(revoked))
        else:  # drift
            ks = ks.without(edge_ids=[ev["edge_id"]])
            old = ks.atom(ev["atom_id"])
            ks = ks.replace_atom(Atom(ev["atom_id"], old.atom_type, WarrantProfile.zero(),
                                      quarantined=old.quarantined))
            yield ("update", ev, ks, frozenset(revoked))


def static_stream(field: KnowledgeSpace, seeds: List[str],
                  serves_per_ob: int = SERVES_PER_OB, salt: str = SALT_TARGETS
                  ) -> Dict[str, object]:
    """No-alarm control: same serve structure, zero updates, zero drift."""
    rng = random.Random(stable_seed(salt + "/static"))
    ids = list(field.ids)
    events = []
    quotas = {0: [serves_per_ob // 2, serves_per_ob - serves_per_ob // 2],
              1: [serves_per_ob // 2, serves_per_ob - serves_per_ob // 2]}
    idx = 0
    while idx < 2 * serves_per_ob:
        ob = idx % 2
        t, truth = _pick_target(rng, field, seeds[ob], ids, quotas[ob], frozenset())
        quotas[ob][0 if truth else 1] -= 1
        events.append({"kind": "serve", "idx": idx, "ob": ob, "seed": seeds[ob],
                       "target": t, "truth": bool(truth), "revoked_at_serve": []})
        idx += 1
    return {"seeds": seeds, "events": events, "final_revoked": [],
            "n_serves": 2 * serves_per_ob, "drift_done": False, "n_updates_used": 0}


def measure_bytes(obj) -> int:
    return len(json.dumps(obj, sort_keys=True, default=_json_default).encode("utf-8"))


def _json_default(o):
    if isinstance(o, frozenset):
        return sorted(str(x) for x in o)
    if isinstance(o, (set, tuple)):
        return list(o)
    return str(o)
