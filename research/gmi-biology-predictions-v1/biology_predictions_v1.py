"""
biology_predictions_v1.py -- GMI morphology phase law applied to biological
parameter regimes.

Implements SpeciesParams, Morphology archetypes, predict_morphology(),
negative_twin(), and predict_developmental_trajectory() for corvid,
cephalopod, rodent, and primate species.  Python 3.8 safe, no network.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Parameter dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SpeciesParams:
    """Ecology (E), resource (R), verifier (V) parameter tuple for a species."""
    E: float
    R: float
    V: float
    name: str = "unknown"


@dataclass
class DevelopmentalStage:
    """A single stage in a developmental trajectory."""
    name: str
    R: float
    V: float
    predicted_morphology: str = ""


# ---------------------------------------------------------------------------
# Morphology archetypes (matching the phase-law registration)
# ---------------------------------------------------------------------------

class Morphology:
    """A morphology archetype with parameterized burden."""

    def __init__(
        self,
        name: str,
        build_cost: float,
        kl_penalty: float,
        storage_req: float,
        compute_req: float,
        comm_req: float,
        adoption_cost: float,
        complexity_penalty: float,
    ):
        self.name = name
        self.build_cost = build_cost
        self.kl_penalty = kl_penalty
        self.storage_req = storage_req
        self.compute_req = compute_req
        self.comm_req = comm_req
        self.adoption_cost = adoption_cost
        self.complexity_penalty = complexity_penalty

    def burden(
        self,
        E: float,
        R: float,
        V: float,
        N: int = 100,
        H: float = 50.0,
        alpha_v: float = 10.0,
    ) -> float:
        """Compute total burden B_M(E, R, V)."""
        amort = (N / H) * self.kl_penalty * (1.0 + V * alpha_v)
        total_resources = self.storage_req + self.compute_req + self.comm_req
        if R > 0:
            resource_pressure = total_resources / R
        else:
            resource_pressure = float("inf")
        ver_pressure = self.complexity_penalty * V
        return self.build_cost + amort + resource_pressure + ver_pressure + self.adoption_cost


def _register_archetypes() -> List[Morphology]:
    """Register three morphology archetypes."""
    return [
        Morphology(
            name="neural",
            build_cost=15.0,
            kl_penalty=0.1,
            storage_req=40.0,
            compute_req=30.0,
            comm_req=20.0,
            adoption_cost=4.0,
            complexity_penalty=0.3,
        ),
        Morphology(
            name="symbolic",
            build_cost=5.0,
            kl_penalty=1.0,
            storage_req=5.0,
            compute_req=5.0,
            comm_req=2.0,
            adoption_cost=1.0,
            complexity_penalty=4.0,
        ),
        Morphology(
            name="probabilistic",
            build_cost=10.0,
            kl_penalty=0.5,
            storage_req=20.0,
            compute_req=15.0,
            comm_req=10.0,
            adoption_cost=2.0,
            complexity_penalty=2.0,
        ),
    ]


# ---------------------------------------------------------------------------
# Species parameter tuples
# ---------------------------------------------------------------------------

CORVID = SpeciesParams(E=8.0, R=5.0, V=7.0, name="corvid")
CEPHALOPOD = SpeciesParams(E=8.0, R=3.0, V=4.0, name="cephalopod")
RODENT = SpeciesParams(E=5.0, R=7.0, V=3.0, name="rodent")
PRIMATE = SpeciesParams(E=9.0, R=8.0, V=9.0, name="primate")

HUMAN_E = 9.0
HUMAN_DEVELOPMENT = [
    DevelopmentalStage(name="infant", R=2.0, V=2.0),
    DevelopmentalStage(name="child", R=5.0, V=6.0),
    DevelopmentalStage(name="adult", R=9.0, V=9.0),
]


# ---------------------------------------------------------------------------
# Core prediction
# ---------------------------------------------------------------------------

def predict_morphology(sp: SpeciesParams) -> str:
    """Return the name of the morphology with lowest burden at (E, R, V)."""
    archetypes = _register_archetypes()
    best_name = archetypes[0].name
    best_burden = archetypes[0].burden(sp.E, sp.R, sp.V)
    for m in archetypes[1:]:
        b = m.burden(sp.E, sp.R, sp.V)
        if b < best_burden:
            best_burden = b
            best_name = m.name
    return best_name


def predict_morphology_with_burden(sp: SpeciesParams) -> Tuple[str, Dict[str, float]]:
    """Return (winner_name, {morphology: burden_value})."""
    archetypes = _register_archetypes()
    burdens = {}  # type: Dict[str, float]
    for m in archetypes:
        burdens[m.name] = m.burden(sp.E, sp.R, sp.V)
    winner = min(burdens, key=burdens.get)
    return winner, burdens


# ---------------------------------------------------------------------------
# Negative twin construction
# ---------------------------------------------------------------------------

def negative_twin(sp: SpeciesParams, predicted_morphology: str) -> Optional[SpeciesParams]:
    """Construct an ecology (E, R, V) where predicted_morphology LOSES.

    Strategy: flip R and V so the predicted morphology becomes the worst
    choice.  If no flip works (degenerate case), return None.
    """
    archetypes = _register_archetypes()
    predicted = [m for m in archetypes if m.name == predicted_morphology]
    if not predicted:
        return None

    candidates = [
        SpeciesParams(E=sp.E, R=2.0, V=0.5, name=sp.name + "_neg"),
        SpeciesParams(E=sp.E, R=1.0, V=0.2, name=sp.name + "_neg"),
        SpeciesParams(E=sp.E, R=9.0, V=0.3, name=sp.name + "_neg"),
        SpeciesParams(E=sp.E, R=3.0, V=9.0, name=sp.name + "_neg"),
    ]

    for candidate in candidates:
        winner = predict_morphology(candidate)
        if winner != predicted_morphology:
            return candidate
    return None


# ---------------------------------------------------------------------------
# Developmental ordering
# ---------------------------------------------------------------------------

def predict_developmental_trajectory(
    stages: List[DevelopmentalStage],
    E: float,
) -> List[DevelopmentalStage]:
    """Predict morphology for each developmental stage and attach it."""
    result = []
    for stage in stages:
        sp = SpeciesParams(E=E, R=stage.R, V=stage.V, name=stage.name)
        morph = predict_morphology(sp)
        result.append(
            DevelopmentalStage(
                name=stage.name,
                R=stage.R,
                V=stage.V,
                predicted_morphology=morph,
            )
        )
    return result


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for sp in [CORVID, CEPHALOPOD, RODENT, PRIMATE]:
        winner, burdens = predict_morphology_with_burden(sp)
        print("%s: E=%.1f R=%.1f V=%.1f -> %s" % (sp.name, sp.E, sp.R, sp.V, winner))
        for name, b in burdens.items():
            marker = " *" if name == winner else ""
            print("  %s: %.4f%s" % (name, b, marker))

    print("\nNegative twins:")
    for sp in [CORVID, CEPHALOPOD, RODENT, PRIMATE]:
        predicted = predict_morphology(sp)
        twin = negative_twin(sp, predicted)
        if twin is not None:
            twin_winner = predict_morphology(twin)
            print("  %s: %s at (%.1f,%.1f,%.1f) -> twin (%.1f,%.1f) winner=%s" % (
                sp.name, predicted, sp.E, sp.R, sp.V, twin.R, twin.V, twin_winner))
        else:
            print("  %s: no negative twin found" % sp.name)

    print("\nHuman developmental trajectory:")
    traj = predict_developmental_trajectory(HUMAN_DEVELOPMENT, HUMAN_E)
    for s in traj:
        print("  %s: R=%.1f V=%.1f -> %s" % (s.name, s.R, s.V, s.predicted_morphology))
