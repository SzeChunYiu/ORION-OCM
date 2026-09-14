"""Bridge witness: machine-to-biology mapping consistency.

No network, no external dependencies. Python 3.8+.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set


# ========== Core types ==========

@dataclass(frozen=True)
class Morphology:
    state_carrier: str
    native_operators: str
    control_update_law: str
    memory_organization: str
    communication_protocol: str
    verification_mechanism: str
    name: str = ""


@dataclass(frozen=True)
class Ecology:
    name: str
    pressures: frozenset = field(default_factory=frozenset)


@dataclass(frozen=True)
class BiologicalTaxon:
    name: str
    neural_architecture: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Mapping:
    name: str
    morphology_to_taxon: Dict[str, str] = field(default_factory=dict)


# ========== Explicit pressure tables ==========
# Ground truth: each morphology declares which pressures it addresses.
# No keyword scanning. No false positives. No drift.

MORPHOLOGY_PRESSURES: Dict[str, frozenset] = {
    "symbolic":   frozenset({"planning", "communication"}),
    "sequential": frozenset({"planning", "prediction"}),
    "predictive": frozenset({"prediction", "error_correction"}),
}


def pvr3_satisfied(morphology: Morphology, ecology: Ecology) -> bool:
    """True iff morphology addresses all pressures ecology demands."""
    morph_p = MORPHOLOGY_PRESSURES.get(morphology.name, frozenset())
    return ecology.pressures.issubset(morph_p)


# ========== Mapping verification ==========

def verify_mapping_consistency(morphologies: List[Morphology],
                               ecologies: List[Ecology],
                               mapping: Mapping) -> bool:
    """Same pressure class must map to same morphological class.

    Group ecologies by pressure set. For each group find all morphologies
    that satisfy ANY ecology in the group. All those must map to the same taxon.
    """
    eco_by_pressure: Dict[frozenset, List[Ecology]] = {}
    for eco in ecologies:
        eco_by_pressure.setdefault(frozenset(eco.pressures), []).append(eco)
    for eco_list in eco_by_pressure.values():
        morphs = {m.name for m in morphologies
                  if any(pvr3_satisfied(m, e) for e in eco_list)}
        if len(morphs) <= 1:
            continue
        taxa = {mapping.morphology_to_taxon.get(n) for n in morphs}
        taxa.discard(None)
        if len(taxa) > 1:
            return False
    return True


def verify_mapping_content(morphologies: List[Morphology],
                           ecologies: List[Ecology],
                           mapping: Mapping) -> bool:
    """Different pressure classes must yield different morphology sets."""
    eco_by_pressure: Dict[frozenset, List[Ecology]] = {}
    for eco in ecologies:
        eco_by_pressure.setdefault(frozenset(eco.pressures), []).append(eco)
    pressure_to_morphs: Dict[str, Set[str]] = {}
    for key, eco_list in eco_by_pressure.items():
        morphs = {m.name for m in morphologies
                  if all(pvr3_satisfied(m, e) for e in eco_list)}
        pressure_to_morphs[str(key)] = morphs
    non_empty = [(k, v) for k, v in pressure_to_morphs.items() if v]
    for i, (_, ms1) in enumerate(non_empty):
        for j, (_, ms2) in enumerate(non_empty):
            if i != j and ms1 == ms2:
                return False
    return True


def verify_mapping_trivial(mapping: Mapping) -> bool:
    """True if non-trivial (not all morphologies map to same taxon)."""
    taxa = set(mapping.morphology_to_taxon.values())
    if len(taxa) <= 1:
        return False
    counts: Dict[str, int] = {}
    for t in mapping.morphology_to_taxon.values():
        counts[t] = counts.get(t, 0) + 1
    return all(c < len(mapping.morphology_to_taxon) for c in counts.values())


def verify_bridge_mapping(morphologies: List[Morphology],
                          ecologies: List[Ecology],
                          mapping: Mapping) -> Dict[str, bool]:
    return {
        "consistent": verify_mapping_consistency(morphologies, ecologies, mapping),
        "content": verify_mapping_content(morphologies, ecologies, mapping),
        "non_trivial": verify_mapping_trivial(mapping),
    }


# ==================== TEST DATA ====================

SYMBOLIC_MANIPULATION = Morphology(
    state_carrier="discrete_tokens",
    native_operators="production_rules",
    control_update_law="rule_following",
    memory_organization="symbol_table",
    communication_protocol="social_protocol",
    verification_mechanism="logical_consistency",
    name="symbolic",
)

SEQUENTIAL_MEMORY = Morphology(
    state_carrier="persistent_state",
    native_operators="sequence_encoding",
    control_update_law="temporal_learning",
    memory_organization="hippocampal_cortical",
    communication_protocol="spatial_gestures",
    verification_mechanism="error_correction",
    name="sequential",
)

PREDICTIVE_MODELING = Morphology(
    state_carrier="internal_model",
    native_operators="prediction_networks",
    control_update_law="prediction_error_learning",
    memory_organization="cerebellar_internal",
    communication_protocol="visual_gestures",
    verification_mechanism="model_correction",
    name="predictive",
)

SOCIAL_COORDINATION = Ecology(
    name="social_coordination",
    pressures=frozenset({"planning", "communication"}),
)

VARIABLE_FORAGING = Ecology(
    name="variable_foraging",
    pressures=frozenset({"planning", "prediction"}),
)

PREDATOR_PREY = Ecology(
    name="predator_prey",
    pressures=frozenset({"prediction", "error_correction"}),
)

PRIMATES = BiologicalTaxon(
    name="primates",
    neural_architecture={
        "state_carrier": "working_memory",
        "native_operators": "hardwired_circuits",
        "control_update_law": "hebbian_learning",
        "memory_organization": "hippocampal_cortical",
        "communication_protocol": "language",
        "verification_mechanism": "metacognition",
    },
)

CORVIDS = BiologicalTaxon(
    name="corvids",
    neural_architecture={
        "state_carrier": "working_memory",
        "native_operators": "hardwired_circuits",
        "control_update_law": "reinforcement_learning",
        "memory_organization": "hippocampal_cortical",
        "communication_protocol": "spatial_gestures",
        "verification_mechanism": "error_correction",
    },
)

CARNIVORES = BiologicalTaxon(
    name="carnivores",
    neural_architecture={
        "state_carrier": "working_memory",
        "native_operators": "hardwired_circuits",
        "control_update_law": "prediction_error_learning",
        "memory_organization": "cerebellar_internal",
        "communication_protocol": "visual_gestures",
        "verification_mechanism": "model_correction",
    },
)

ALL_MORPHOLOGIES = [SYMBOLIC_MANIPULATION, SEQUENTIAL_MEMORY, PREDICTIVE_MODELING]
ALL_ECOLOGIES = [SOCIAL_COORDINATION, VARIABLE_FORAGING, PREDATOR_PREY]


def build_valid_mapping() -> Mapping:
    return Mapping(
        name="valid",
        morphology_to_taxon={
            "symbolic": "primates",
            "sequential": "corvids",
            "predictive": "carnivores",
        },
    )


def build_inconsistent_mapping() -> Mapping:
    return Mapping(
        name="inconsistent",
        morphology_to_taxon={
            "symbolic": "primates",
            "sequential": "primates",
            "predictive": "carnivores",
        },
    )


def build_trivial_mapping() -> Mapping:
    return Mapping(
        name="trivial",
        morphology_to_taxon={
            "symbolic": "primates",
            "sequential": "primates",
            "predictive": "primates",
        },
    )


if __name__ == "__main__":
    print("Bridge Witness Computation")
    print("=" * 60)
    for label, builder in [
        ("Valid mapping", build_valid_mapping),
        ("Inconsistent mapping", build_inconsistent_mapping),
        ("Trivial mapping", build_trivial_mapping),
    ]:
        m = builder()
        results = verify_bridge_mapping(ALL_MORPHOLOGIES, ALL_ECOLOGIES, m)
        print(f"\n{label}:")
        for k, v in results.items():
            print(f"  {k}: {v}")
    print("\nPVR-3 satisfaction matrix:")
    for morph in ALL_MORPHOLOGIES:
        for eco in ALL_ECOLOGIES:
            print(f"  {morph.name} x {eco.name} = {pvr3_satisfied(morph, eco)}")
    print("\nWitness computation complete.")
