"""Issue #165 H5 lifetime ledger at polynomial + microworld scope.

H1 v2 already showed later compute falls while library capital is unrecouped.
This capsule treats that capital as an INPUT. It does not re-search H1 later
tasks and does not rerun the G2 9,010,526-attempt tournament.

Coordinates stay separate. No dollars. No sum of bytes with enumeration.
M12 lifetime V5 with N1/N2 corpus acquisition is CANNOT_CHECK; a miniature
language analog is labelled MINIATURE_ONLY.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
H1_DIR = REPO / "research" / "h1-amortized-rewrite-v2"
G2_DIR = REPO / "research" / "g2-acquisition-economics-v1"
N1_DIR = REPO / "research" / "ocm-n1"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(N1_DIR))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H1 = _load_module("h1_amortized_rewrite_v2", H1_DIR / "experiment.py")
N1 = _load_module("n1_language_lifetime_calibration", N1_DIR / "language_lifetime_calibration.py")

SCHEMA = "ocm.h5.lifetime-economics.v1"
METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
H1_RESULT = H1_DIR / "RESULT.json"
H1_V1_RESULT = REPO / "research" / "h1-amortized-acquisition-v1" / "RESULT.json"
G2_RESULT = G2_DIR / "G2_ACQUISITION_ECONOMICS_V1.json"
G5_SUMMARY = REPO / "research" / "g5-physical-denominator-v1" / "SUMMARY.json"

H1_RESULT_SHA256 = "78b0f33284a0e5817c71fc3259b42aee4bcc0caafd4ee7aae7c9411f7b506959"
G2_RESULT_SHA256 = "049760194d24078d05188e77d45a69c60012ef9726d75a274aef87887f018597"

# G2 length-8 ecology, cited not rerun.
G2_BREAK_EVEN_TOURNAMENT = 2136
G2_BREAK_EVEN_ZERO_SEARCH = 41
G2_TOURNAMENT_ENUMERATION = 9_010_526
G2_SEARCH_AWARE_ENUMERATION = 0
G2_SEARCH_AWARE_TOKEN_OPS = 4608

POSTING_N = 8
POSTING_K = 2
PRICE_LAMBDAS = (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 1_000_000)

COORDINATES = (
    "acquisition_compute",
    "later_inference_compute",
    "maintenance_work",
    "state_written",
    "scan_token_operations",
    "examples",
)

ALLOWED_TERMINALS = (
    "LIFETIME_NET_NEGATIVE_AT_POLYNOMIAL_HORIZON",
    "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION",
    "CANNOT_CHECK_H1_CAPITAL_DRIFT",
    "CANNOT_CHECK_G2_RECEIPT_DRIFT",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def ceil_pos(numer: int, denom: float) -> int | None:
    if denom <= 0:
        return None
    return int(math.ceil(numer / denom))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_h1_capital() -> dict[str, Any]:
    digest = sha256_file(H1_RESULT)
    if digest != H1_RESULT_SHA256:
        raise RuntimeError(f"H1 v2 RESULT.json drifted: {digest}")
    doc = load_json(H1_RESULT)
    later_k0 = int(doc["later"]["k0"]["compute"])
    later_kt = int(doc["later"]["kt"]["compute"])
    library = doc["library"]["cost"]
    expected = {
        "terminal": "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS",
        "later_k0": 59929,
        "later_kt": 36289,
        "library_compute": 132863,
        "training_compute": 3866,
        "tournament_compute": 128997,
        "examples": 16,
        "state_written": 14248,
        "admitted": ["square", "square"],
        "later_n": 16,
    }
    observed = {
        "terminal": doc["terminal"],
        "later_k0": later_k0,
        "later_kt": later_kt,
        "library_compute": int(library["compute"]),
        "training_compute": int(doc["library"]["training_compute"]),
        "tournament_compute": int(doc["library"]["tournament_compute"]),
        "examples": int(library["examples"]),
        "state_written": int(library["state_written"]),
        "admitted": list(doc["library"]["admitted"]),
        "later_n": int(doc["partition"]["later_n"]),
    }
    if observed != expected:
        raise RuntimeError(f"H1 capital vector drifted: {observed}")
    if later_kt >= later_k0:
        raise RuntimeError("H1 v2 later compute must be strictly cheaper than reset")
    return {
        "path": str(H1_RESULT.relative_to(REPO)),
        "sha256": digest,
        "terminal": doc["terminal"],
        "lifetime_terminal": doc["lifetime_terminal"],
        "denied": False,
        "later_k0_compute": later_k0,
        "later_kt_compute": later_kt,
        "later_saving_compute": later_k0 - later_kt,
        "library_compute": observed["library_compute"],
        "training_compute": observed["training_compute"],
        "tournament_compute": observed["tournament_compute"],
        "examples": observed["examples"],
        "state_written": observed["state_written"],
        "ordinary_bytes": int(doc["ocm"]["ordinary_bytes"]),
        "ocm_bytes": int(doc["ocm"]["ocm_bytes"]),
        "revoked_bytes": int(doc["ocm"]["revoked_bytes"]),
        "admitted": tuple(observed["admitted"]),
        "candidates": [tuple(row) for row in doc["library"]["candidates"]],
        "later_n": observed["later_n"],
        "parent_sufficient": bool(doc["parent_sufficient"]),
        "h1_vector_strictly_less": bool(doc["h1_vector_strictly_less"]),
        "note": (
            "H1 v2 later-task compute falls (59929 → 36289) but library capital "
            "132863 is unrecouped on the frozen 16 later-task horizon. This ledger "
            "includes that capital rather than denying it."
        ),
    }


def load_g2_cited() -> dict[str, Any]:
    digest = sha256_file(G2_RESULT)
    if digest != G2_RESULT_SHA256:
        raise RuntimeError(f"G2 acquisition-economics receipt drifted: {digest}")
    doc = load_json(G2_RESULT)
    verdict = doc["verdict"]
    if verdict["break_even_tasks_with_tournament"] != G2_BREAK_EVEN_TOURNAMENT:
        raise RuntimeError("G2 tournament break-even drifted")
    if verdict["break_even_tasks_with_zero_search_acquisition"] != G2_BREAK_EVEN_ZERO_SEARCH:
        raise RuntimeError("G2 zero-search break-even drifted")
    if verdict["tournament_acquisition_enumeration_attempts"] != G2_TOURNAMENT_ENUMERATION:
        raise RuntimeError("G2 tournament enumeration drifted")
    if verdict["zero_search_acquisition_enumeration_attempts"] != G2_SEARCH_AWARE_ENUMERATION:
        raise RuntimeError("G2 SEARCH_AWARE enumeration drifted")
    search_aware = next(row for row in doc["cheap_selectors"] if row["selector"] == "SEARCH_AWARE")
    if search_aware["acquisition_work"]["enumeration_attempts"] != 0:
        raise RuntimeError("SEARCH_AWARE must be zero enumeration")
    if search_aware["acquisition_work"]["token_operations"] != G2_SEARCH_AWARE_TOKEN_OPS:
        raise RuntimeError("SEARCH_AWARE token-operation pin drifted")
    if "SEARCH_AWARE" not in verdict["selectors_agreeing_with_the_tournament"]:
        raise RuntimeError("frozen G2 receipt must record SEARCH_AWARE agreement")
    return {
        "path": str(G2_RESULT.relative_to(REPO)),
        "sha256": digest,
        "terminal": verdict["terminal"],
        "cited_not_rerun": True,
        "break_even_tasks_with_tournament": G2_BREAK_EVEN_TOURNAMENT,
        "break_even_tasks_with_zero_search_acquisition": G2_BREAK_EVEN_ZERO_SEARCH,
        "tournament_acquisition_enumeration_attempts": G2_TOURNAMENT_ENUMERATION,
        "zero_search_acquisition_enumeration_attempts": G2_SEARCH_AWARE_ENUMERATION,
        "search_aware_token_operations": G2_SEARCH_AWARE_TOKEN_OPS,
        "per_task_saving": verdict["per_task_saving"],
        "tournament_test_saving": verdict["tournament_test_saving"],
        "note": (
            "Length-8 #192 ecology: break-even 2136 later tasks with tournament "
            "acquisition vs 41 with zero-search SEARCH_AWARE. The 9,010,526-attempt "
            "tournament is cited from the frozen receipt and is not rerun here."
        ),
    }


def load_g5_denominator() -> dict[str, Any]:
    doc = load_json(G5_SUMMARY)
    if doc["execution_terminal"] != "DATABASE_PARENT_SUFFICIENT":
        raise RuntimeError("G5 physical-denominator terminal drifted")
    n2048 = doc["scaling"]["n_2048"]
    return {
        "terminal": doc["execution_terminal"],
        "physical_denominator_clean": False,
        "cognitive_claim_if_jsonl_dominates": "NOT_CLEAN",
        "jsonl_cumulative_rewrite_bytes_at_2048": n2048["jsonl_cumulative_rewrite_bytes"],
        "jsonl_write_amplification_at_2048": n2048["jsonl_write_amplification"],
        "note": (
            "G5.1 parent is DATABASE_PARENT_SUFFICIENT. Cognitive lifetime claims "
            "are not clean if JSONL whole-file rewrite dominates the physical "
            "denominator. Persist bytes here are a state-written coordinate, not "
            "a cognitive-efficiency score, and are not converted to dollars."
        ),
    }


def reconstruct_h1_training():
    pop = H1.population(H1.TRAIN_LEN)
    train = H1.take(pop, H1.TRAIN_LEN, H1.TRAIN_SALT, H1.TRAIN_N)
    programs = tuple(program for _task, program in train)
    candidates, support = H1.mine(train)
    return train, programs, candidates, support


def scan_zero_enumeration(candidates, programs) -> dict[str, Any]:
    """Zero-enumeration rewrite-benefit scan over already-solved training programs.

    Token operations are incommensurable with enumeration attempts and are not
    added to compute. Grammar width stays 4 (H1 rewrite serving), so this scan
    has no G2-style widening term; G2 SEARCH_AWARE is the licensed zero-enum
    selector for the length-8 5-ary ecology, cited separately.
    """
    work = {"enumeration_attempts": 0, "unique_checks": 0, "token_operations": 0}
    scores: dict[tuple[str, ...], int] = {}
    for fragment in candidates:
        saved = 0
        for program in programs:
            work["token_operations"] += len(program)
            _word, _used, operator_cost = H1.greedy_rewrite(program, fragment)
            saved += len(program) - operator_cost
        scores[fragment] = saved
    frequency = max(candidates, key=lambda fragment: (sum(1 for p in programs if fragment in
        tuple(p[i:i + len(fragment)] for i in range(len(p) - len(fragment) + 1))), len(fragment), fragment))
    # Frequency via support is computed by the caller; here pick max rewrite saving.
    winner = max(candidates, key=lambda fragment: (scores[fragment], len(fragment), fragment))
    return {
        "enumeration_attempts": work["enumeration_attempts"],
        "unique_checks": work["unique_checks"],
        "token_operations": work["token_operations"],
        "scores": {" ".join(fragment): scores[fragment] for fragment in candidates},
        "chosen": list(winner),
        "frequency_chosen": list(frequency),
        "agrees_with_h1_admitted": False,  # filled by caller
    }


def miniature_posting(n: int = POSTING_N, k: int = POSTING_K) -> dict[str, int]:
    """Cheap index analog: construction scans N; incremental append is 1; rebuild is N+1."""
    if n < k:
        raise RuntimeError("posting n < k")
    posting = list(range(k))
    construction = n
    retrieval = len(posting)
    incremental = 1
    rebuild = n + 1
    return {
        "n": n,
        "k": k,
        "construction_units": construction,
        "retrieval_units": retrieval,
        "incremental_update_units": incremental,
        "rebuild_units": rebuild,
        "cheap_maintenance_units": incremental,
    }


def measure_revocation_restore(fragment) -> dict[str, Any]:
    training_receipt = {
        "schema": "h5.lifetime.training.v1",
        "fragment": list(fragment),
        "role": "maintenance-analog",
    }
    utility_receipt = {
        "schema": "h5.lifetime.utility.v1",
        "accepted": True,
        "role": "maintenance-analog",
    }
    with tempfile.TemporaryDirectory(prefix="ocm-h5-lifetime-") as temp_dir:
        root = Path(temp_dir)
        loaded, atom_id, _te, _ue, live_bytes = H1.admit_fragment(
            root / "live", fragment, training_receipt, utility_receipt, revoke=False
        )
        revoked_fragment, _rid, _rte, _rue, revoked_bytes = H1.admit_fragment(
            root / "revoked", fragment, training_receipt, utility_receipt, revoke=True
        )
        restored, _sid, _ste, _sue, restore_bytes = H1.admit_fragment(
            root / "restored", fragment, training_receipt, utility_receipt, revoke=False
        )
        persist_ops = 3
        warrant_checks = 3
    if tuple(loaded) != tuple(fragment) or tuple(restored) != tuple(fragment):
        raise RuntimeError("maintenance restore did not return the admitted fragment")
    if revoked_fragment is not None:
        raise RuntimeError("revoked arm remained live")
    return {
        "fragment": list(fragment),
        "atom_id": atom_id,
        "live_bytes": int(live_bytes),
        "revoked_bytes": int(revoked_bytes),
        "restore_bytes": int(restore_bytes),
        "persist_ops": persist_ops,
        "warrant_liveness_checks": warrant_checks,
        "restore_returned_fragment": True,
        "revoked_equals_absent": True,
        "work_units": persist_ops + warrant_checks,
    }


def n1_miniature() -> dict[str, Any]:
    raw = N1.run()
    ocm_obs = sum(raw["related_observation_curve_ocm"])
    reset_obs = sum(raw["related_observation_curve_reset"])
    return {
        "label": "MINIATURE_ONLY",
        "source": "research/ocm-n1/language_lifetime_calibration.py",
        "receipt": raw["receipt"],
        "study_role": raw["study_role"],
        "protected_claim_authority": False,
        "not_m12_v5": True,
        "not_corpus_n1_n2": True,
        "related_observation_curve_persistent": list(raw["related_observation_curve_ocm"]),
        "related_observation_curve_reset": list(raw["related_observation_curve_reset"]),
        "acquisition_observations_persistent": ocm_obs,
        "acquisition_observations_reset": reset_obs,
        "later_saving_observations": reset_obs - ocm_obs,
        "amortization_present_vs_reset": bool(raw["amortization_present_vs_reset"]),
        "strong_parent_matches_exactly": bool(raw["strong_parent_matches_exactly"]),
        "isolated_terminal": raw["isolated_terminal"],
        "meta_learning_terminal": raw["meta_learning_terminal"],
        "unit": "teacher pairwise order constraints (incommensurable with polynomial enumeration)",
        "note": (
            "Nested-family order miniature only. Corpus-scale N1/N2 language "
            "acquisition is locked and is not included. Observation counts are "
            "not added to H1 enumeration."
        ),
    }


def arm_vector(
    *,
    name: str,
    acquisition_compute: int,
    later_k0: int,
    later_kt: int,
    maintenance_work: int,
    state_written: int,
    scan_token_operations: int,
    examples: int,
    maintenance_state_written: int,
) -> dict[str, Any]:
    later_saving = later_k0 - later_kt
    compute_net = later_saving - acquisition_compute - maintenance_work
    # State and examples have no later saving on this microscope.
    nets = {
        "acquisition_compute": later_saving - acquisition_compute - maintenance_work,
        "later_inference_compute": later_saving,
        "maintenance_work": 0 - maintenance_work,
        "state_written": 0 - (state_written + maintenance_state_written),
        "scan_token_operations": 0 - scan_token_operations,
        "examples": 0 - examples,
    }
    return {
        "name": name,
        "acquisition_compute": acquisition_compute,
        "later_k0_compute": later_k0,
        "later_kt_compute": later_kt,
        "later_saving_compute": later_saving,
        "maintenance_work": maintenance_work,
        "state_written": state_written,
        "maintenance_state_written": maintenance_state_written,
        "scan_token_operations": scan_token_operations,
        "examples": examples,
        "compute_net_later_saving_minus_acquisition_minus_maintenance": compute_net,
        "compute_sign_positive": compute_net > 0,
        "per_coordinate_net": nets,
        "lifetime_compute_kt": acquisition_compute + later_kt + maintenance_work,
        "lifetime_compute_k0": later_k0,
    }


def price_one_coordinate(arm: dict[str, Any]) -> dict[str, Any]:
    """Vary a price on one coordinate at a time.

    Primary comparison is later-saving-minus-acquisition on compute (plus
    charged maintenance work, which is the same unit). Pricing compute itself
    cannot flip that sign for λ > 0. Pricing any extra-cost coordinate c
    yields net(λ) = compute_net − λ · extra_c and may flip when compute_net > 0.
    Bytes, token operations, and examples are never converted to a dollar.
    """
    compute_net = arm["compute_net_later_saving_minus_acquisition_minus_maintenance"]
    extras = {
        "acquisition_compute": 0,  # already inside compute_net
        "later_inference_compute": 0,
        "maintenance_work": 0,  # already inside compute_net
        "state_written": arm["state_written"] + arm["maintenance_state_written"],
        "scan_token_operations": arm["scan_token_operations"],
        "examples": arm["examples"],
    }
    out: dict[str, Any] = {}
    for coord, extra in extras.items():
        rows = []
        signs = []
        for lam in PRICE_LAMBDAS:
            if coord in {"acquisition_compute", "later_inference_compute", "maintenance_work"}:
                priced = lam * compute_net if lam else compute_net
            else:
                priced = compute_net - lam * extra
            positive = priced > 0
            signs.append(positive)
            rows.append({"lambda": lam, "priced_net": priced, "sign_positive": positive})
        unpriced_positive = compute_net > 0
        flipped = any(sign != unpriced_positive for sign in signs)
        lambda_star = None
        if extra > 0 and compute_net > 0 and coord not in {
            "acquisition_compute",
            "later_inference_compute",
            "maintenance_work",
        }:
            lambda_star = compute_net / extra
        elif extra > 0 and compute_net < 0 and coord not in {
            "acquisition_compute",
            "later_inference_compute",
            "maintenance_work",
        }:
            lambda_star = None  # extra cost cannot rescue a negative compute net
        out[coord] = {
            "extra": extra,
            "unpriced_compute_sign_positive": unpriced_positive,
            "sign_flips_for_some_lambda": flipped,
            "lambda_star_where_priced_net_zero": lambda_star,
            "sweep": rows,
            "unit_warning": (
                "λ is a hypothetical relative price, not a dollar. "
                f"{coord} is not commensurate with enumeration unless so declared."
            ),
        }
    any_flip = any(row["sign_flips_for_some_lambda"] for row in out.values())
    return {
        "compute_net": compute_net,
        "any_one_coordinate_price_flips_sign": any_flip,
        "survives_all_one_at_a_time_prices": (compute_net > 0) and not any_flip,
        "coordinates": out,
    }


def box_map(tournament: dict[str, Any], cheap: dict[str, Any],
            tournament_pareto: dict[str, Any], cheap_pareto: dict[str, Any],
            n1: dict[str, Any]) -> dict[str, Any]:
    cheap_positive = cheap["compute_sign_positive"]
    tournament_positive = tournament["compute_sign_positive"]
    return {
        "H5/001-lifetime_benefit_after_training_inference_update_maintenance": {
            "text": "lifetime benefit remains positive after training/inference/update/maintenance",
            "issue_checkbox": "G4.4 / lifetime benefit remains positive after training/inference/update/maintenance",
            "tournament_compute_positive": tournament_positive,
            "search_aware_compute_positive": cheap_positive,
            "vector_strictly_positive": False,
            "same_path_acquisition_payback": False,
            "status": (
                "CONDITIONAL_COST_SCENARIO_NOT_SAME_PATH"
                if cheap_positive
                else "NO_STRICT_SAVING"
            ),
            "unit": "enumeration attempts on the polynomial microscope; maintenance work units; persist bytes stay separate",
            "note": (
                "Conditional cost scenario: the cheap arm keeps H1 v2's admitted "
                "square square later-saving and substitutes G2-licensed zero extra "
                "enumeration. The reconstructed H1 rewrite scan does not select "
                "that fragment. A G2 selector result in another serving regime "
                "does not license H1 selection equivalence. Not H1 v3. Tournament "
                "capital remains net-negative. State written and examples have no "
                "later saving."
            ),
        },
        "H5/002-m12_lifetime_v5_n1_n2_acquisition": {
            "text": "M12 lifetime V5 with N1/N2 acquisition cost included",
            "issue_checkbox": "L3 / M12 lifetime V5 with N1/N2 acquisition cost included",
            "status": "CANNOT_CHECK_N1_N2_ACQUISITION_AT_CORPUS_SCALE",
            "claimed": False,
            "corpus_includes_language_acquisition": True,
            "locked": True,
            "miniature": {
                "label": "MINIATURE_ONLY",
                "status": "MEASURED_MINIATURE_ONLY",
                "amortization_present_vs_reset": n1["amortization_present_vs_reset"],
                "acquisition_observations_persistent": n1["acquisition_observations_persistent"],
                "acquisition_observations_reset": n1["acquisition_observations_reset"],
            },
            "note": (
                "M12 lifetime V5 with N1/N2 corpus-scale acquisition is locked and "
                "not claimed. The nested-order analog is MINIATURE_ONLY."
            ),
        },
        "H5/003-survives_pareto_resource_price": {
            "text": "result survives Pareto/resource-price analysis",
            "issue_checkbox": "G4.4 / result survives Pareto/resource-price analysis",
            "tournament_survives": tournament_pareto["survives_all_one_at_a_time_prices"],
            "search_aware_survives": cheap_pareto["survives_all_one_at_a_time_prices"],
            "search_aware_flips_if_state_or_examples_priced": cheap_pareto["any_one_coordinate_price_flips_sign"],
            "status": (
                "PRICE_REGIME_ONLY"
                if cheap_positive and cheap_pareto["any_one_coordinate_price_flips_sign"]
                else "SURVIVES_AT_SCOPE"
                if cheap_pareto["survives_all_one_at_a_time_prices"]
                else "NO_UNQUALIFIED_SURVIVAL"
            ),
            "note": (
                "One-at-a-time prices only. No dollar scalarization. A positive "
                "compute net after cheap acquisition is price-regime: it flips when "
                "state written or examples are given a high enough relative price."
            ),
        },
        "H5/004-crossover_horizon": {
            "text": "H5 lifetime economic regime m > m* on declared vectors",
            "g2_cited_break_even_tournament_length8": G2_BREAK_EVEN_TOURNAMENT,
            "g2_cited_break_even_zero_search_length8": G2_BREAK_EVEN_ZERO_SEARCH,
            "h1_horizon_later_tasks": tournament["later_n"] if "later_n" in tournament else None,
            "status": "MEASURED_AT_POLYNOMIAL_HORIZON",
        },
    }


def mechanism_comment(terminal: str, tournament: dict[str, Any], cheap: dict[str, Any],
                      scan: dict[str, Any], g2: dict[str, Any]) -> str:
    saved = tournament["later_saving_compute"]
    return (
        f"H1 v2 capital is included, not denied: tournament library compute "
        f"{tournament['acquisition_compute']} plus later K_t {tournament['later_kt_compute']} "
        f"exceeds reset later {tournament['later_k0_compute']} (later saving {saved}). "
        f"Tournament compute net after cheap maintenance is "
        f"{tournament['compute_net_later_saving_minus_acquisition_minus_maintenance']}. "
        f"SEARCH_AWARE acquisition (zero extra enumeration; G2 scan token ops "
        f"{g2['search_aware_token_operations']} cited, H1-training scan token ops "
        f"{scan['token_operations']} measured) drops acquisition compute to training "
        f"{cheap['acquisition_compute']}, so compute net becomes "
        f"{cheap['compute_net_later_saving_minus_acquisition_minus_maintenance']}. "
        f"That sign flip is a conditional cost scenario: the scan does not select "
        f"H1 v2's admitted fragment, and G2 agreement on another ecology does not "
        f"license H1 selection equivalence. Not H1 v3. G2 length-8 break-even "
        f"remains 2136 vs 41 and was not rerun. H1-horizon break-even is reported "
        f"from the frozen later saving and is not a salt retune. State written and "
        f"examples stay unrecouped. M12 V5 + N1/N2 corpus is CANNOT_CHECK. No "
        f"dollars. Terminal {terminal}."
    )


def run_study() -> dict[str, Any]:
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")
    if tuple(H1.M.PRIMITIVES) != ("inc", "dec", "double", "square"):
        raise RuntimeError("production primitive grammar drifted")

    try:
        h1 = load_h1_capital()
    except RuntimeError as exc:
        return {
            "schema": SCHEMA,
            "issue": 165,
            "head": git_head(),
            "terminal": "CANNOT_CHECK_H1_CAPITAL_DRIFT",
            "mechanism_comment": str(exc),
            "production_src_edited": False,
            "programme_wide_close": False,
        }
    try:
        g2 = load_g2_cited()
    except RuntimeError as exc:
        return {
            "schema": SCHEMA,
            "issue": 165,
            "head": git_head(),
            "terminal": "CANNOT_CHECK_G2_RECEIPT_DRIFT",
            "mechanism_comment": str(exc),
            "production_src_edited": False,
            "programme_wide_close": False,
        }

    g5 = load_g5_denominator()
    _train, programs, candidates, _support = reconstruct_h1_training()
    if tuple(candidates) != tuple(h1["candidates"]):
        raise RuntimeError("reconstructed H1 training candidates drifted from frozen RESULT")
    scan = scan_zero_enumeration(candidates, programs)
    scan["agrees_with_h1_admitted"] = tuple(scan["chosen"]) == h1["admitted"]
    if scan["enumeration_attempts"] != 0:
        raise RuntimeError("training scan charged enumeration")

    restore = measure_revocation_restore(h1["admitted"])
    posting = miniature_posting()
    maintenance_work = min(restore["work_units"], posting["cheap_maintenance_units"])
    maintenance_choice = (
        "incremental_posting_update"
        if posting["cheap_maintenance_units"] <= restore["work_units"]
        else "revocation_restore"
    )
    n1 = n1_miniature()

    later_k0 = h1["later_k0_compute"]
    later_kt = h1["later_kt_compute"]
    later_n = h1["later_n"]
    per_task = h1["later_saving_compute"] / later_n

    tournament = arm_vector(
        name="TOURNAMENT",
        acquisition_compute=h1["library_compute"],
        later_k0=later_k0,
        later_kt=later_kt,
        maintenance_work=maintenance_work,
        state_written=h1["state_written"],
        scan_token_operations=0,
        examples=h1["examples"],
        maintenance_state_written=restore["restore_bytes"],
    )
    cheap = arm_vector(
        name="SEARCH_AWARE",
        acquisition_compute=h1["training_compute"],
        later_k0=later_k0,
        later_kt=later_kt,
        maintenance_work=maintenance_work,
        state_written=h1["state_written"],
        scan_token_operations=scan["token_operations"],
        examples=h1["examples"],
        maintenance_state_written=restore["restore_bytes"],
    )
    tournament["later_n"] = later_n
    cheap["later_n"] = later_n
    tournament["break_even_later_tasks"] = ceil_pos(h1["library_compute"], per_task)
    cheap["break_even_later_tasks"] = ceil_pos(h1["training_compute"], per_task)
    tournament["horizon_meets_break_even"] = later_n >= (tournament["break_even_later_tasks"] or math.inf)
    cheap["horizon_meets_break_even"] = later_n >= (cheap["break_even_later_tasks"] or math.inf)

    tournament_pareto = price_one_coordinate(tournament)
    cheap_pareto = price_one_coordinate(cheap)

    if cheap["compute_sign_positive"] and not tournament["compute_sign_positive"]:
        terminal = "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION"
    elif not cheap["compute_sign_positive"] and not tournament["compute_sign_positive"]:
        terminal = "LIFETIME_NET_NEGATIVE_AT_POLYNOMIAL_HORIZON"
    elif cheap["compute_sign_positive"] and tournament["compute_sign_positive"]:
        terminal = "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION"
    else:
        terminal = "LIFETIME_NET_NEGATIVE_AT_POLYNOMIAL_HORIZON"

    boxes = box_map(tournament, cheap, tournament_pareto, cheap_pareto, n1)
    boxes["H5/004-crossover_horizon"]["h1_horizon_later_tasks"] = later_n
    boxes["H5/004-crossover_horizon"]["h1_break_even_tournament"] = tournament["break_even_later_tasks"]
    boxes["H5/004-crossover_horizon"]["h1_break_even_search_aware"] = cheap["break_even_later_tasks"]
    boxes["H5/004-crossover_horizon"]["per_task_later_saving_compute"] = per_task
    boxes["H5/004-crossover_horizon"]["note"] = (
        f"H1 frozen horizon is {later_n} length-6 tasks. Tournament break-even is "
        f"{tournament['break_even_later_tasks']} tasks; SEARCH_AWARE break-even is "
        f"{cheap['break_even_later_tasks']}. The registered horizon sits between them, "
        "which is why the compute sign flips. G2's 2136 vs 41 are the length-8 "
        "citation and are not recomputed."
    )

    comment = mechanism_comment(terminal, tournament, cheap, scan, g2)

    dollars_claimed = False
    scalarized = False

    return {
        "schema": SCHEMA,
        "issue": 165,
        "head": git_head(),
        "terminal": terminal,
        "tournament_arm_terminal": (
            "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION"
            if tournament["compute_sign_positive"]
            else "LIFETIME_NET_NEGATIVE_AT_POLYNOMIAL_HORIZON"
        ),
        "search_aware_arm_terminal": (
            "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION"
            if cheap["compute_sign_positive"]
            else "LIFETIME_NET_NEGATIVE_AT_POLYNOMIAL_HORIZON"
        ),
        "sign_flips_vs_tournament_capital": (
            cheap["compute_sign_positive"] != tournament["compute_sign_positive"]
        ),
        "programme_wide_close": False,
        "production_src_edited": False,
        "methods_blob": observed_blob,
        "evidence_class": "E3",
        "contribution_level": "L2",
        "scope": "polynomial-microworld-lifetime-only",
        "dollars_claimed": dollars_claimed,
        "scalarized_incommensurable_resources": scalarized,
        "m12_v5_n1_n2_corpus_claimed": False,
        "h1_v1_result_overwritten": False,
        "h1_v2_result_overwritten": False,
        "machine_epistemics_lifetime_v1_overwritten": False,
        "parent": "ordinary persistent rewrite/library + SEARCH_AWARE scan (G2) + SQLite/WAL physical parent (G5)",
        "parent_sufficient_on_serving": h1["parent_sufficient"],
        "mechanism_comment": comment,
        "same_path_acquisition_payback": False,
        "h1_v3_not_this_capsule": True,
        "g2_does_not_license_h1_selection_equivalence": True,
        "claim_ceiling": (
            "Conditional cost scenario on the frozen H1 v2 fragment/saving plus a "
            "G2-licensed cheaper acquisition coordinate. The reconstructed scan "
            "does not select square square; this is not executed same-path "
            "acquisition/payback and not H1 v3. Bounded polynomial+microworld "
            "ledger plus a labelled MINIATURE_ONLY language analog. Not M12 V5 "
            "with N1/N2 corpus cost, not programme-wide H5, not "
            "PHYSICAL_DENOMINATOR_CLEAN, not dollars."
        ),
        "h1_capital_input": h1,
        "g2_cited_not_rerun": g2,
        "g5_physical_denominator": g5,
        "scan": scan,
        "maintenance": {
            "choice": maintenance_choice,
            "work_units_charged": maintenance_work,
            "revocation_restore": restore,
            "posting": posting,
            "note": (
                "Charged maintenance is the cheaper of revocation-restore work units "
                "and incremental posting update. Full posting rebuild is reported "
                "and is not hidden in later inference."
            ),
        },
        "n1_n2_miniature": n1,
        "m12_lifetime_v5_n1_n2": {
            "status": "CANNOT_CHECK_N1_N2_ACQUISITION_AT_CORPUS_SCALE",
            "claimed": False,
            "label_if_measured": "MINIATURE_ONLY",
            "reason": (
                "Issue L3 M12 lifetime V5 with N1/N2 acquisition cost includes "
                "language acquisition at corpus scale, which is locked. This "
                "capsule is polynomial+microworld lifetime only."
            ),
        },
        "arms": {"tournament": tournament, "search_aware": cheap},
        "pareto": {"tournament": tournament_pareto, "search_aware": cheap_pareto},
        "coordinates": list(COORDINATES),
        "price_lambdas": list(PRICE_LAMBDAS),
        "boxes": boxes,
        "earned": sorted(k for k, v in boxes.items() if str(v["status"]).startswith("EARNED")),
        "not_earned": sorted(
            k for k, v in boxes.items()
            if v["status"] in {
                "NO_STRICT_SAVING",
                "NO_UNQUALIFIED_SURVIVAL",
                "PRICE_REGIME_ONLY",
                "CONDITIONAL_COST_SCENARIO_NOT_SAME_PATH",
            }
        ),
        "cannot_check": sorted(k for k, v in boxes.items() if str(v["status"]).startswith("CANNOT_CHECK")),
        "not_issued": [
            "PROGRAMME_WIDE_H5_CLOSE",
            "M12_LIFETIME_V5_WITH_N1_N2_CORPUS_COST",
            "PHYSICAL_DENOMINATOR_CLEAN",
            "DOLLARS",
            "SCALARIZED_INCOMMENSURABLE_RESOURCES",
            "P6_MATCHED_LIFETIME_RESIDUAL",
            "OCM_ARCHITECTURE_UNIQUENESS_OVER_LIBRARY_SEARCH",
            "SALT_RETUNE_OF_H1",
            "NEURAL_TRANSFORMER_LIFETIME",
            "SAME_PATH_H1_SELECTION_EQUIVALENCE",
            "H1_V3_CONFLATION",
        ],
        "negative_terminals_frozen": list(ALLOWED_TERMINALS),
        "h1_v1_terminal": load_json(H1_V1_RESULT)["terminal"] if H1_V1_RESULT.exists() else None,
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    return value


def main(out: Path) -> dict[str, Any]:
    result = _jsonable(run_study())
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out.write_text(text)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "tournament_arm_terminal": result.get("tournament_arm_terminal"),
                "search_aware_arm_terminal": result.get("search_aware_arm_terminal"),
                "sign_flips_vs_tournament_capital": result.get("sign_flips_vs_tournament_capital"),
                "earned": result.get("earned"),
                "cannot_check": result.get("cannot_check"),
                "m12_v5_n1_n2_corpus_claimed": result.get("m12_v5_n1_n2_corpus_claimed"),
                "dollars_claimed": result.get("dollars_claimed"),
                "g2_break_even": [
                    result.get("g2_cited_not_rerun", {}).get("break_even_tasks_with_tournament"),
                    result.get("g2_cited_not_rerun", {}).get("break_even_tasks_with_zero_search_acquisition"),
                ],
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
