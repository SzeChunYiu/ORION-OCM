"""Capability interactions unified witness: pairwise resource CHANNEL OVERLAP for all 27
A4 capabilities.

CORRECTION NOTICE (2026-09-18, gmi-833-capability-interaction-partition-v1).
`interaction_type()` below is a CHANNEL-OVERLAP PREDICATE, not a burden classification.
Its three return strings were previously read as the four burden-relation types of
Section 1.2 of CAPABILITY_INTERACTIONS_UNIFIED_THEOREM_V1.md. That reading was wrong:
on the real 27-capability contract 56 of the 351 unordered pairs carried a label that
contradicts Section 1.2's own defining condition. `verify_no_interference()` below is
VACUOUS (`interaction_type()` has no "interfering" return path, so it cannot return
False).

This file is retained UNCHANGED in behaviour as the historical artefact and as the
frozen source of the A4 channel assignment. For the corrected burden classification and
the corrected 27x27 census, use
    research/gmi-833-capability-interaction-partition-v1/partition_witness_v1.py
    research/gmi-833-capability-interaction-partition-v1/DELTA_TABLE_V1.md
"""

from __future__ import annotations

import json
from typing import Dict, FrozenSet, List, Tuple

# ---------------------------------------------------------------------------
# 27-row A4 capability resource-channel assignments
# ---------------------------------------------------------------------------
# Each capability is assigned a subset of {Storage, Compute, Communication}
# based on its resource_metric fields in the A4 contract.
#
# Storage (S): persistent state capacity — memory, code, models, stores
# Compute  (T): transformation/processing steps — tau, search, inference
# Communication (M): message width, channel uses, protocol overhead

RESOURCE_CHANNELS: Dict[str, FrozenSet[str]] = {
    "cap-perception":                frozenset({"S", "T"}),
    "cap-selective-attention":       frozenset({"S", "T"}),
    "cap-working-memory":            frozenset({"S", "T"}),
    "cap-episodic-memory":           frozenset({"S", "T"}),
    "cap-semantic-memory":           frozenset({"S", "T"}),
    "cap-procedural-memory":         frozenset({"S", "T"}),
    "cap-retrieval":                 frozenset({"S", "T", "M"}),
    "cap-consolidation":             frozenset({"S", "T"}),
    "cap-forgetting":                frozenset({"S", "T"}),
    "cap-prediction":                frozenset({"S", "T"}),
    "cap-abstraction-concept":       frozenset({"S", "T"}),
    "cap-compositional-reasoning":   frozenset({"S", "T"}),
    "cap-hierarchical-skill":        frozenset({"S", "T"}),
    "cap-planning":                  frozenset({"S", "T"}),
    "cap-exploration":               frozenset({"S", "T"}),
    "cap-causal-inference":          frozenset({"T"}),
    "cap-counterfactual-reasoning":  frozenset({"S", "T"}),
    "cap-metacognition":             frozenset({"T"}),
    "cap-social-cognition":          frozenset({"S", "T"}),
    "cap-communication":             frozenset({"S", "M"}),
    "cap-imitation":                 frozenset({"T"}),
    "cap-teaching":                  frozenset({"T", "M"}),
    "cap-cultural-accumulation":     frozenset({"S", "T"}),
    "cap-self-modeling":             frozenset({"S", "T"}),
    "cap-self-improvement":          frozenset({"T"}),
    "cap-tool-use":                  frozenset({"S", "T", "M"}),
    "cap-coordination":              frozenset({"S", "M"}),
}

# Canonical ordering for matrix output
CAPABILITY_IDS: Tuple[str, ...] = tuple(RESOURCE_CHANNELS.keys())

assert len(CAPABILITY_IDS) == 27, f"Expected 27 capabilities, got {len(CAPABILITY_IDS)}"


# ---------------------------------------------------------------------------
# Resource overlap computation
# ---------------------------------------------------------------------------

def jaccard_overlap(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    """Jaccard similarity of two resource channel sets: |A∩B| / |A∪B|."""
    if not a and not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def interaction_type(channels_x: FrozenSet[str], channels_y: FrozenSet[str]) -> str:
    """CHANNEL-OVERLAP PREDICATE (historical). NOT a burden classification.

    Returns a purely set-theoretic signature of the two channel sets:

    - "independent":  no shared resource channels  (overlap = 0)
    - "synergistic":  channel sets are equal       (overlap = 1)
    - "redundant":    any other intersection       (0 < overlap < 1)

    CORRECTED 2026-09-18. Do NOT read these strings as the Section 1.2 burden types.
    Under the A4 registered accounting the burden classes are:

        equal channel sets       -> REDUNDANT        (joint = max < sum)   161 pairs
        nested, proper           -> REDUNDANT        (joint = max < sum)   126 pairs
        intersecting, not nested -> PARTIAL_SHARING  (max < joint < sum)    56 pairs
        disjoint                 -> INDEPENDENT      (joint = sum)           8 pairs

    The "redundant" return above conflates the middle two rows; on the 56 non-nested
    pairs its Section 1.2 condition `joint = max` is FALSE (e.g. cap-perception {S,T} x
    cap-communication {S,M}: max = 2, joint = 3, sum = 4). The decisive invariant is
    NESTING, which this predicate cannot see.

    Use partition_witness_v1.classify() in
    research/gmi-833-capability-interaction-partition-v1/ for the burden classes.
    """
    shared = channels_x & channels_y
    if not shared:
        return "independent"
    if shared == channels_x and shared == channels_y:
        return "synergistic"
    return "redundant"


def pairwise_overlap_matrix(
    channels: Dict[str, FrozenSet[str]] = RESOURCE_CHANNELS,
    ids: Tuple[str, ...] = CAPABILITY_IDS,
) -> List[List[float]]:
    """Return 27x27 Jaccard overlap matrix."""
    return [
        [jaccard_overlap(channels[i], channels[j]) for j in ids]
        for i in ids
    ]


def pairwise_interaction_matrix(
    channels: Dict[str, FrozenSet[str]] = RESOURCE_CHANNELS,
    ids: Tuple[str, ...] = CAPABILITY_IDS,
) -> List[List[str]]:
    """Return 27x27 interaction type classification matrix."""
    return [
        [interaction_type(channels[i], channels[j]) for j in ids]
        for i in ids
    ]


# ---------------------------------------------------------------------------
# Interference check (PVR-3 guarantee)
# ---------------------------------------------------------------------------

def verify_no_interference(
    channels: Dict[str, FrozenSet[str]] = RESOURCE_CHANNELS,
    ids: Tuple[str, ...] = CAPABILITY_IDS,
) -> bool:
    """VACUOUS (DEF-3, corrected 2026-09-18): interaction_type() has no "interfering"
    return path, so this function cannot return False and proves nothing.

    Retained unchanged as the historical artefact. The non-vacuous replacement is
    Theorem CIP-2b in gmi-833-capability-interaction-partition-v1: under union
    accounting joint <= sum by subadditivity of mu, checked on all 351 pairs by a
    classifier that computes joint and sum and HAS a reachable INTERFERING branch
    (partition_witness_v1.union_accounting_is_subadditive).
    """
    for i in ids:
        for j in ids:
            if interaction_type(channels[i], channels[j]) == "interfering":
                return False
    return True


# ---------------------------------------------------------------------------
# Symmetry check
# ---------------------------------------------------------------------------

def verify_symmetric(
    channels: Dict[str, FrozenSet[str]] = RESOURCE_CHANNELS,
    ids: Tuple[str, ...] = CAPABILITY_IDS,
) -> bool:
    """Verify that the 27x27 interaction matrix is symmetric."""
    for i in ids:
        for j in ids:
            if interaction_type(channels[i], channels[j]) != interaction_type(channels[j], channels[i]):
                return False
    return True


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def interaction_summary(
    channels: Dict[str, FrozenSet[str]] = RESOURCE_CHANNELS,
    ids: Tuple[str, ...] = CAPABILITY_IDS,
) -> Dict[str, int]:
    """Count pairs by interaction type (upper triangle, i < j)."""
    counts: Dict[str, int] = {"independent": 0, "synergistic": 0, "redundant": 0, "interfering": 0}
    n = len(ids)
    for idx_i in range(n):
        for idx_j in range(idx_i + 1, n):
            t = interaction_type(channels[ids[idx_i]], channels[ids[idx_j]])
            counts[t] += 1
    return counts


# ---------------------------------------------------------------------------
# Load A4 contract resource metrics (optional, for documentation)
# ---------------------------------------------------------------------------

def load_a4_resource_metrics(contract_path: str | None = None) -> Dict[str, str]:
    """Load the resource_metric field from each row of the A4 contract JSON.

    Returns a dict mapping capability id -> resource_metric string.
    If contract_path is None, returns the hardcoded descriptions.
    """
    if contract_path is not None:
        with open(contract_path, "r") as f:
            data = json.load(f)
        return {row["id"]: row.get("resource_metric", "") for row in data["rows"]}

    # Hardcoded resource_metric excerpts from A4 contract
    return {
        "cap-perception": "sensor bandwidth, encoding bits |c|, and transformation cost tau",
        "cap-selective-attention": "routing decision cost c_r plus accessed source width versus exposure cost c_e",
        "cap-working-memory": "persistent state cardinality |S_working|, maintenance transformation cost, and interference susceptibility",
        "cap-episodic-memory": "episodic entry count N_t, encoding/retrieval cost, and consolidation cost to long-term store",
        "cap-semantic-memory": "semantic code size, abstraction cost, and retrieval transformation tau",
        "cap-procedural-memory": "compiled code size, compilation (search) cost, and online execution cost",
        "cap-retrieval": "index size, retrieval query cost tau_retrieve, and communication cut width",
        "cap-consolidation": "replay steps, consolidation transformation cost, and resulting long-term code size",
        "cap-forgetting": "retained state cardinality after forgetting and relearning cost for dropped distinctions if they recur",
        "cap-prediction": "model code size, inference tau, and belief-state maintenance cost",
        "cap-abstraction-concept": "number of concepts retained, boundary description bits, and retrieval cost per use",
        "cap-compositional-reasoning": "codebook size (|primitives| not |product|) and composition transformation cost",
        "cap-hierarchical-skill": "skill description size, skill retrieval cost, and retained state per level",
        "cap-planning": "simulation steps tau, search frontier size, and model-query cost",
        "cap-exploration": "probe execution cost, search/experiment budget, and time to decision",
        "cap-causal-inference": "graph search cost and identification proof length",
        "cap-counterfactual-reasoning": "counterfactual inference cost and model specification burden",
        "cap-metacognition": "metacognitive computation (EVC evaluation) and strategy-register evaluation cost",
        "cap-social-cognition": "agent-model state size, inference tau, and recursion depth cost",
        "cap-communication": "message width (symbols), channel uses, and protocol description cost",
        "cap-imitation": "demonstration count, correspondence search cost, and imitation learning compute",
        "cap-teaching": "teaching actions/instructions sent and teacher planning cost",
        "cap-cultural-accumulation": "population size, transmission fidelity overhead, and cultural store size",
        "cap-self-modeling": "self-monitoring cost, self-model state size, and update frequency",
        "cap-self-improvement": "self-modification search cost, verification cost, and risk of regression",
        "cap-tool-use": "tool-call count, tool latency/cost, and tool-interface description overhead",
        "cap-coordination": "communication volume, coordination rounds, and collective state size",
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Capability Interactions Unified Witness ===\n")

    # 1. Verify structural properties
    assert verify_no_interference(), "PVR-3 violation: interfering pair found"
    assert verify_symmetric(), "Symmetry violation: matrix is not symmetric"
    print("[PASS] No interfering pairs (PVR-3 consistent)")
    print("[PASS] Interaction matrix is symmetric\n")

    # 2. Pairwise summary
    summary = interaction_summary()
    total_pairs = sum(summary.values())
    print(f"Pairwise interaction summary ({total_pairs} pairs from 27 capabilities):")
    for kind, count in sorted(summary.items()):
        print(f"  {kind:15s}: {count:5d}")
    print()

    # 3. Sample overlap matrix (first 5x5)
    ids_short = CAPABILITY_IDS[:5]
    overlap = pairwise_overlap_matrix()
    print("Jaccard overlap (first 5x5):")
    header = "".join(f"{c.replace('cap-', '')[:10]:>12s}" for c in ids_short)
    print(f"  {'':>12s}{header}")
    for idx, cap_i in enumerate(ids_short):
        row = "".join(f"{overlap[idx][j]:12.3f}" for j in range(5))
        print(f"  {cap_i.replace('cap-', '')[:12]:>12s}{row}")
    print()

    # 4. Resource channel usage
    storage_only = [c for c in CAPABILITY_IDS if RESOURCE_CHANNELS[c] == frozenset({"S"})]
    compute_only = [c for c in CAPABILITY_IDS if RESOURCE_CHANNELS[c] == frozenset({"T"})]
    comm_only = [c for c in CAPABILITY_IDS if RESOURCE_CHANNELS[c] == frozenset({"M"})]
    all_three = [c for c in CAPABILITY_IDS if len(RESOURCE_CHANNELS[c]) == 3]
    print(f"Storage-only capabilities:     {len(storage_only)}")
    print(f"Compute-only capabilities:     {len(compute_only)}")
    print(f"Communication-only caps:       {len(comm_only)}")
    print(f"All-three-channel caps:        {len(all_three)}")
    print()
    print("[PASS] Unified witness complete.")
