from __future__ import annotations

import importlib.util
import pathlib
from typing import Dict, Mapping

ROOT = pathlib.Path(__file__).resolve().parent
PREDICTOR_PATH = ROOT.parent / "gmi-capability-predictor-dev-v1" / "dev_predictor_v1.py"
SPEC = importlib.util.spec_from_file_location("dev_predictor_v1", PREDICTOR_PATH)
predictor_mod = importlib.util.module_from_spec(SPEC)
if SPEC.loader is None:
    raise RuntimeError("cannot load development predictor")
SPEC.loader.exec_module(predictor_mod)

BASE = {
    "memory_margin": 0,
    "planning_margin": 0,
    "communication_margin": 0,
    "routing_margin": 0,
    "verification_margin": 0,
}

SCIENCE_FACTS = {
    "speed_of_light_m_per_s": "299792458",
    "avogadro_constant_per_mol": "6.02214076e23",
    "element_79": "gold",
    "water_freezing_point_K_at_1atm": "273.15",
}

PROOF_CHAIN = (
    ("1+3+5+7", 16),
    ("4*4", 16),
    ("4**2", 16),
    ("n**2 when n=4", 16),
    ("sum_first_n_odd when n=4", 16),
)

PATCHES = (
    "def clamp(x, lo, hi):\n    return max(lo, min(x, hi))\n",
    "def clamp(x, lo, hi):\n    return min(lo, max(x, hi))\n",
    "def clamp(x, lo, hi):\n    return max(lo, x)\n",
)
PATCH_TESTS = ((-2, 0, 10, 0), (5, 0, 10, 5), (12, 0, 10, 10), (3, 3, 3, 3))

CONTROL_MODES = {
    "LEFT_DRIFT": "RIGHT_THRUST",
    "RIGHT_DRIFT": "LEFT_THRUST",
    "FAST": "BRAKE",
    "SLOW": "ACCELERATE",
}


def _validate_margins(margins: Mapping[str, int]) -> None:
    if set(margins) != set(BASE):
        raise ValueError("margins must contain exactly the five registered coordinates")
    for value in margins.values():
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("margins must be integers")


def factual_science_task(memory_margin: int) -> bool:
    required_slots = len(SCIENCE_FACTS)
    available_slots = required_slots + memory_margin
    if available_slots < required_slots:
        return False
    retrieved = {key: SCIENCE_FACTS[key] for key in SCIENCE_FACTS}
    return retrieved == SCIENCE_FACTS


def math_proof_task(memory_margin: int, planning_margin: int) -> bool:
    required_live_items = 2
    required_steps = len(PROOF_CHAIN) - 1
    if required_live_items + memory_margin < required_live_items:
        return False
    if required_steps + planning_margin < required_steps:
        return False
    values = [value for _, value in PROOF_CHAIN]
    return all(left == right for left, right in zip(values, values[1:]))


def _load_patch(source: str):
    namespace: Dict[str, object] = {}
    exec(source, {"__builtins__": {"min": min, "max": max}}, namespace)
    return namespace["clamp"]


def code_patch_task(routing_margin: int, verification_margin: int) -> bool:
    required_routes = len(PATCHES)
    required_tests = len(PATCH_TESTS)
    if required_routes + routing_margin < required_routes:
        return False
    if required_tests + verification_margin < required_tests:
        return False

    passing = []
    for index, source in enumerate(PATCHES):
        fn = _load_patch(source)
        ok = all(fn(x, lo, hi) == expected for x, lo, hi, expected in PATCH_TESTS)
        if ok:
            passing.append(index)
    return passing == [0]


def sensor_actuator_control_task(communication_margin: int) -> bool:
    required_symbols = len(CONTROL_MODES)
    symbols = required_symbols + communication_margin
    if symbols < required_symbols:
        return False
    alphabet = tuple(range(symbols))
    encoder = {mode: alphabet[i] for i, mode in enumerate(CONTROL_MODES)}
    decoder = {alphabet[i]: command for i, command in enumerate(CONTROL_MODES.values())}
    return all(decoder[encoder[mode]] == command for mode, command in CONTROL_MODES.items())


def executable_truth(domain_id: str, margins: Mapping[str, int]) -> int:
    _validate_margins(margins)
    if domain_id == "FACTUAL_SCIENCE_RETRIEVAL":
        return int(factual_science_task(margins["memory_margin"]))
    if domain_id == "MATH_PROOF_CHAIN":
        return int(math_proof_task(margins["memory_margin"], margins["planning_margin"]))
    if domain_id == "CODE_PATCH_VERIFICATION":
        return int(code_patch_task(margins["routing_margin"], margins["verification_margin"]))
    if domain_id == "SENSOR_ACTUATOR_CONTROL":
        return int(sensor_actuator_control_task(margins["communication_margin"]))
    raise ValueError("unknown real-regime domain")


def evaluate_case(domain_id: str, target: str, margins: Mapping[str, int]) -> Dict[str, object]:
    _validate_margins(margins)
    predictor = predictor_mod.fit_registered_development_predictor()
    prediction = predictor.predict_one(margins, target)
    truth = executable_truth(domain_id, margins)
    return {
        "domain_id": domain_id,
        "target": target,
        "prediction": prediction,
        "executable_truth": truth,
        "agree": prediction == truth,
    }
