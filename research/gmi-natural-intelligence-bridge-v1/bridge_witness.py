"""Bridge witness: machine-to-biology mapping consistency.

No network, no external dependencies. Python 3.8+.

Design:
  Mapping-consistency tests (morph_alpha/beta/gamma):
    alpha + beta share pressure class {planning, communication}.
    gamma has {prediction, error_correction}.
    2 ecologies: eco_social demands {planning, communication},
                 eco_predator demands {prediction, error_correction}.
    alpha+beta both satisfy eco_social -> consistency constraint.

  PVR-3 clean-bijection tests (named instances):
    Each morphology has a UNIQUE pressure pair. No two share a pressure class.
    3 ecologies match 1-to-1.  Every ecology is satisfied by exactly one morphology.
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
# Mapping-consistency morphologies share pressure classes.
# PVR-3 named morphologies each have a unique, disjoint pressure pair.

MORPHOLOGY_PRESSURES: Dict[str, frozenset] = {
    # Mapping tests: alpha and beta share {planning, communication}
    "morph_alpha": frozenset({"planning", "communication"}),
    "morph_beta":  frozenset({"planning", "communication"}),
    "morph_gamma": frozenset({"prediction", "error_correction"}),
    # PVR-3 clean-bijection tests: each unique
    "symbolic_manipulation": frozenset({"planning", "communication"}),
    "sequential_memory":     frozenset({"sequential_processing", "pattern_recognition"}),
    "predictive_modeling":   frozenset({"prediction", "error_correction"}),
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
    that satisfy ANY ecology in the group. All must map to the same taxon.
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
    """Different pressure classes must yield different taxon outcome sets.

    For each pressure class, compute the set of taxa that morphologies
    satisfying that class map to. Two different classes must produce
    different taxon sets.
    """
    eco_by_pressure: Dict[frozenset, List[Ecology]] = {}
    for eco in ecologies:
        eco_by_pressure.setdefault(frozenset(eco.pressures), []).append(eco)
    pressure_to_taxa: Dict[str, Set[str]] = {}
    for key, eco_list in eco_by_pressure.items():
        taxa = set()
        for m in morphologies:
            if any(pvr3_satisfied(m, e) for e in eco_list):
                t = mapping.morphology_to_taxon.get(m.name)
                if t:
                    taxa.add(t)
        pressure_to_taxa[str(key)] = taxa
    non_empty = [(k, v) for k, v in pressure_to_taxa.items() if v]
    for i, (_, t1) in enumerate(non_empty):
        for j, (_, t2) in enumerate(non_empty):
            if i != j and t1 == t2:
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

# --- Mapping-consistency morphologies (alpha+beta share pressure class) ---

MORPH_ALPHA = Morphology(
    state_carrier="discrete_tokens",
    native_operators="production_rules",
    control_update_law="rule_following",
    memory_organization="symbol_table",
    communication_protocol="social_protocol",
    verification_mechanism="logical_consistency",
    name="morph_alpha",
)

MORPH_BETA = Morphology(
    state_carrier="persistent_state",
    native_operators="sequence_encoding",
    control_update_law="temporal_reasoning",
    memory_organization="hippocampal_index",
    communication_protocol="spatial_gestures",
    verification_mechanism="forward_model",
    name="morph_beta",
)

MORPH_GAMMA = Morphology(
    state_carrier="internal_model",
    native_operators="prediction_networks",
    control_update_law="prediction_error_learning",
    memory_organization="cerebellar_internal",
    communication_protocol="visual_gestures",
    verification_mechanism="model_correction",
    name="morph_gamma",
)

# --- PVR-3 clean-bijection morphologies (each unique pressure pair) ---

SYMBOLIC_MANIPULATION = Morphology(
    state_carrier="discrete_symbols",
    native_operators="rewrite_systems",
    control_update_law="inference_rules",
    memory_organization="symbol_table_persistent",
    communication_protocol="structured_language",
    verification_mechanism="proof_checking",
    name="symbolic_manipulation",
)

SEQUENTIAL_MEMORY = Morphology(
    state_carrier="sequential_buffer",
    native_operators="temporal_encoding",
    control_update_law="sequence_completion",
    memory_organization="hippocampal_index",
    communication_protocol="temporal_gestures",
    verification_mechanism="pattern_matching",
    name="sequential_memory",
)

PREDICTIVE_MODELING = Morphology(
    state_carrier="generative_model",
    native_operators="prediction_networks",
    control_update_law="prediction_error_learning",
    memory_organization="cerebellar_internal",
    communication_protocol="anticipatory_gestures",
    verification_mechanism="model_correction",
    name="predictive_modeling",
)

# --- Ecologies for mapping-consistency tests ---

ECO_SOCIAL = Ecology(
    name="eco_social",
    pressures=frozenset({"planning", "communication"}),
)

ECO_PREDATOR = Ecology(
    name="eco_predator",
    pressures=frozenset({"prediction", "error_correction"}),
)

# --- Ecologies for PVR-3 clean-bijection tests ---

SOCIAL_COORDINATION = Ecology(
    name="social_coordination",
    pressures=frozenset({"planning", "communication"}),
)

VARIABLE_FORAGING = Ecology(
    name="variable_foraging",
    pressures=frozenset({"sequential_processing", "pattern_recognition"}),
)

PREDATOR_PREY = Ecology(
    name="predator_prey",
    pressures=frozenset({"prediction", "error_correction"}),
)

# --- Taxa ---

TAXON_1 = BiologicalTaxon(
    name="taxon_1",
    neural_architecture={"pathway": "social_cortex"},
)

TAXON_2 = BiologicalTaxon(
    name="taxon_2",
    neural_architecture={"pathway": "prediction_cortex"},
)

# --- Aggregated lists for mapping tests ---

ALL_MORPHOLOGIES = [MORPH_ALPHA, MORPH_BETA, MORPH_GAMMA]
ALL_ECOLOGIES = [ECO_SOCIAL, ECO_PREDATOR]


# --- Mapping builders ---

def build_valid_mapping() -> Mapping:
    """Consistent: alpha+beta share class -> same taxon. Non-trivial."""
    return Mapping(
        name="valid",
        morphology_to_taxon={
            "morph_alpha": "taxon_1",
            "morph_beta":  "taxon_1",
            "morph_gamma": "taxon_2",
        },
    )


def build_inconsistent_mapping() -> Mapping:
    """Inconsistent: alpha+beta share class but map to different taxa."""
    return Mapping(
        name="inconsistent",
        morphology_to_taxon={
            "morph_alpha": "taxon_1",
            "morph_beta":  "taxon_2",
            "morph_gamma": "taxon_2",
        },
    )


def build_trivial_mapping() -> Mapping:
    """Trivial: all map to same taxon. Fails content and non_trivial."""
    return Mapping(
        name="trivial",
        morphology_to_taxon={
            "morph_alpha": "taxon_1",
            "morph_beta":  "taxon_1",
            "morph_gamma": "taxon_1",
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
    print("\nPVR-3 satisfaction matrix (mapping ecologies):")
    for morph in ALL_MORPHOLOGIES:
        for eco in ALL_ECOLOGIES:
            print(f"  {morph.name} x {eco.name} = {pvr3_satisfied(morph, eco)}")
    print("\nPVR-3 clean-bijection matrix (named instances):")
    named_morphs = [SYMBOLIC_MANIPULATION, SEQUENTIAL_MEMORY, PREDICTIVE_MODELING]
    named_ecos = [SOCIAL_COORDINATION, VARIABLE_FORAGING, PREDATOR_PREY]
    for morph in named_morphs:
        for eco in named_ecos:
            print(f"  {morph.name} x {eco.name} = {pvr3_satisfied(morph, eco)}")
    print("\nWitness computation complete.")
