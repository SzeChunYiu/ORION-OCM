"""Final-target natural-intelligence half V1.

Registers the dual schema (machine morphology half composed with natural
biological-bridge quadruples), freezes seven-taxon C_pred rows, and checks
L1–L3 / V7 composition at admissible formal scope.

Does NOT claim HUMAN_COGNITION_EXPLAINED, G10 empirical validation, or
neuroanatomy. CPython 3.8+ safe. No network.
"""

import json
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "PREDICTIONS_REGISTRY_V1.json"

TERMINAL = "FINAL_TARGET_NATURAL_HALF_ADMISSIBLE_V1"

FORBIDDEN_CLAIMS = frozenset(
    {
        "HUMAN_COGNITION_EXPLAINED",
        "G10_empirical_natural_intelligence",
        "neuroanatomy_identity",
        "592_40_b_ladder_ceiling",
    }
)

ADMISSIBLE_TICKS = frozenset(
    {
        "592_40_a_natural_half",
        "602_L1_descriptors_laws",
        "602_L2_seven_taxa",
        "602_L3_human_architecture",
        "602_V7_formal_holdout",
    }
)

DESCRIPTOR_IDS = ("D_mem", "D_tom", "D_meta", "D_plan", "D_comm", "D_pred")

# Descriptor -> derived-lesion id (gmi-derived-lesion-v1), formal V7 alignment.
LESION_ALIGNMENT = {
    "D_mem": "L_mem",
    "D_tom": "L_social",
    "D_meta": "L_att",
    "D_plan": "L_plan",
    "D_comm": "L_social",
    "D_pred": "L_causal",
}

# Soft-reuse of biology-predictions / phase-RV archetype burdens (inlined).
@dataclass(frozen=True)
class MorphologyArchetype:
    name: str
    build_cost: float
    kl_penalty: float
    storage_req: float
    compute_req: float
    comm_req: float
    adoption_cost: float
    complexity_penalty: float

    def burden(self, E, R, V, N=100, H=50.0, alpha_v=10.0):
        # E reserved for ecology label continuity with parents; burden uses R,V.
        _ = E
        amort = (N / H) * self.kl_penalty * (1.0 + V * alpha_v)
        total = self.storage_req + self.compute_req + self.comm_req
        resource_pressure = total / R if R > 0 else float("inf")
        return (
            self.build_cost
            + amort
            + resource_pressure
            + self.complexity_penalty * V
            + self.adoption_cost
        )


ARCHETYPES = (
    MorphologyArchetype("neural", 15.0, 0.1, 40.0, 30.0, 20.0, 4.0, 0.3),
    MorphologyArchetype("symbolic", 5.0, 1.0, 5.0, 5.0, 2.0, 1.0, 4.0),
    MorphologyArchetype("probabilistic", 10.0, 0.5, 20.0, 15.0, 10.0, 2.0, 2.0),
)


def phase_winner(E, R, V):
    """Machine-half morphology winner under phase-RV burden (composed)."""
    best = ARCHETYPES[0]
    best_b = best.burden(E, R, V)
    for m in ARCHETYPES[1:]:
        b = m.burden(E, R, V)
        if b < best_b:
            best, best_b = m, b
    return best.name


@dataclass(frozen=True)
class ProfileLaw:
    descriptor: str
    statement: str
    monotone_axis: str


PROFILE_LAWS = (
    ProfileLaw(
        "D_mem",
        "niche variability up -> episodic weight up; stable niche -> semantic-heavy",
        "niche_variability",
    ),
    ProfileLaw(
        "D_tom",
        "social interaction value must clear TOM recursion cost else depth stays low",
        "social_value",
    ),
    ProfileLaw(
        "D_meta",
        "stop iff common action; else confidence scales with candidate-set size",
        "candidate_set_size",
    ),
    ProfileLaw(
        "D_plan",
        "planning depth >=1 only where multi-step ecology pays EVC",
        "multi_step_payoff",
    ),
    ProfileLaw(
        "D_comm",
        "cumulative culture only if population x fidelity clears teaching break-even",
        "population_fidelity",
    ),
    ProfileLaw(
        "D_pred",
        "predator/prey tracking ecology selects high predictive-motor demand",
        "tracking_pressure",
    ),
)


@dataclass(frozen=True)
class TaxonEcology:
    name: str
    E: float
    R: float
    V: float
    social_structure: str
    niche: str


# Seven taxa (L2). First four soft-reuse biology-predictions regimes.
TAXA = (
    TaxonEcology("corvid", 8.0, 5.0, 7.0, "pair_plus_fission_fusion", "variable_caching_foraging"),
    TaxonEcology("cephalopod", 8.0, 3.0, 4.0, "mostly_solitary", "flexible_problem_solving"),
    TaxonEcology("rodent", 5.0, 7.0, 3.0, "colony_variable", "spatial_navigation"),
    TaxonEcology(
        "nonhuman_primate", 9.0, 8.0, 9.0, "multi_agent_hierarchy", "social_coordination"
    ),
    TaxonEcology("cetacean", 8.0, 6.0, 8.0, "pod_culture", "acoustic_social_foraging"),
    TaxonEcology("carnivore", 7.0, 5.0, 5.0, "solitary_or_pack", "predator_prey_tracking"),
    TaxonEcology("human", 9.0, 9.0, 9.0, "large_scale_protocol", "cumulative_culture"),
)

TAXA_BY_NAME = {t.name: t for t in TAXA}


@dataclass
class BridgeQuad:
    """Biological-bridge prediction quadruple."""

    id: str
    taxon: str
    E_bio: dict
    M: dict
    C_pred: dict
    D_holdout: dict


def load_registry(path=None):
    p = Path(path) if path is not None else REGISTRY_PATH
    data = json.loads(p.read_text())
    rows = []
    for raw in data["rows"]:
        rows.append(
            BridgeQuad(
                id=raw["id"],
                taxon=raw["taxon"],
                E_bio=dict(raw["E_bio"]),
                M=dict(raw["M"]),
                C_pred=dict(raw["C_pred"]),
                D_holdout=dict(raw["D_holdout"]),
            )
        )
    return data, rows


def quad_fields_complete(row):
    """True iff all four bridge fields are present and structurally sound."""
    if not row.id or not row.taxon:
        return False
    for key in ("E", "R", "V"):
        if key not in row.E_bio:
            return False
    if "phase_winner" not in row.M or "mechanisms" not in row.M:
        return False
    if "descriptors" not in row.C_pred or "failure_mode" not in row.C_pred:
        return False
    desc = row.C_pred["descriptors"]
    if any(d not in desc for d in DESCRIPTOR_IDS):
        return False
    if row.D_holdout.get("status") != "HELD_OUT":
        return False
    if row.D_holdout.get("content") is not None:
        return False
    return True


def profiles_distinct(rows):
    """L1/L2: at least two taxa must differ on descriptor vectors."""
    vectors = []
    for row in rows:
        desc = row.C_pred["descriptors"]
        vectors.append(tuple(desc[d] for d in DESCRIPTOR_IDS))
    return len(set(vectors)) >= 2


def human_architecture_ok(row):
    """L3: human row carries architecture profile without neuroanatomy."""
    if row.taxon != "human":
        return False
    arch = row.C_pred.get("architecture")
    if not isinstance(arch, dict):
        return False
    regimes = arch.get("memory_regimes") or []
    if set(regimes) != {"working", "episodic", "semantic", "procedural"}:
        return False
    if arch.get("neuroanatomy") is not None:
        return False
    stages = arch.get("developmental_stages") or []
    if len(stages) != 3:
        return False
    names = [s.get("name") for s in stages]
    if names != ["infant", "child", "adult"]:
        return False
    # R,V non-decreasing across development (biology-predictions soft-reuse).
    rs = [s["R"] for s in stages]
    vs = [s["V"] for s in stages]
    if rs != sorted(rs) or vs != sorted(vs):
        return False
    return True


def phase_winner_matches(row):
    """Machine half composition: registry M matches phase_winner(E,R,V)."""
    E = float(row.E_bio["E"])
    R = float(row.E_bio["R"])
    V = float(row.E_bio["V"])
    return row.M.get("phase_winner") == phase_winner(E, R, V)


def lesion_alignment_ok(registry_meta=None):
    """V7: descriptor→lesion map matches derived-lesion ids."""
    meta = registry_meta
    if meta is None:
        meta, _ = load_registry()
    alignment = meta.get("lesion_alignment") or {}
    if set(alignment.keys()) != set(DESCRIPTOR_IDS):
        return False
    allowed = {"L_mem", "L_att", "L_plan", "L_causal", "L_social", "L_consol"}
    for d, lesion in alignment.items():
        if lesion not in allowed:
            return False
        if LESION_ALIGNMENT.get(d) != lesion:
            return False
    return True


def claim_ceiling_ok(registry_meta=None):
    meta = registry_meta
    if meta is None:
        meta, _ = load_registry()
    ceiling = meta.get("claim_ceiling") or {}
    forbidden = set(ceiling.get("forbidden") or [])
    if not FORBIDDEN_CLAIMS.issubset(forbidden):
        return False
    admissible = set(ceiling.get("admissible") or [])
    return len(admissible) >= 5


def compose_natural_half():
    """Run full admissible composition; raise ValueError on failure."""
    meta, rows = load_registry()
    if len(rows) != 7:
        raise ValueError("expected 7 taxa rows, got %d" % len(rows))
    names = [r.taxon for r in rows]
    if sorted(names) != sorted(t.name for t in TAXA):
        raise ValueError("taxon set mismatch: %r" % (names,))
    for row in rows:
        if not quad_fields_complete(row):
            raise ValueError("incomplete quad: %s" % row.id)
        if not phase_winner_matches(row):
            raise ValueError("phase winner mismatch: %s" % row.id)
        # Ecology continuity with in-module taxa table.
        tax = TAXA_BY_NAME[row.taxon]
        if (
            float(row.E_bio["E"]) != tax.E
            or float(row.E_bio["R"]) != tax.R
            or float(row.E_bio["V"]) != tax.V
        ):
            raise ValueError("E_bio drift vs TAXA table: %s" % row.id)
    if not profiles_distinct(rows):
        raise ValueError("profiles not distinct across taxa")
    human = [r for r in rows if r.taxon == "human"][0]
    if not human_architecture_ok(human):
        raise ValueError("human L3 architecture profile invalid")
    if not lesion_alignment_ok(meta):
        raise ValueError("V7 lesion alignment failed")
    if not claim_ceiling_ok(meta):
        raise ValueError("claim ceiling incomplete")
    if meta.get("terminal") != TERMINAL:
        raise ValueError("terminal mismatch")
    if len(PROFILE_LAWS) != len(DESCRIPTOR_IDS):
        raise ValueError("profile law / descriptor count mismatch")
    return {
        "status": "PASS",
        "terminal": TERMINAL,
        "rows": len(rows),
        "descriptors": list(DESCRIPTOR_IDS),
        "admissible_ticks": sorted(ADMISSIBLE_TICKS),
        "forbidden_claims": sorted(FORBIDDEN_CLAIMS),
        "machine_half_composed": True,
        "phenotype_consulted": False,
    }


def honest_ticks():
    """What this capsule may honestly tick at registered formal scope."""
    compose_natural_half()
    return {
        "592.40(a)": "admissible — natural-intelligence half present",
        "602.L1": "admissible — descriptors + profile laws registered",
        "602.L2": "admissible — 7 taxa frozen; D_holdout HELD_OUT",
        "602.L3": "admissible — human architecture profile; neuroanatomy=null",
        "602.V7": "admissible — formal holdout + lesion/bridge/phase composition",
        "592.40(b)": "OPEN — ladder ceiling not claimed",
        "HUMAN_COGNITION_EXPLAINED": "NOT claimed",
        "G10_empirical": "NOT claimed",
    }


if __name__ == "__main__":
    print(json.dumps(compose_natural_half(), indent=2, sort_keys=True))
    print(json.dumps(honest_ticks(), indent=2, sort_keys=True))
