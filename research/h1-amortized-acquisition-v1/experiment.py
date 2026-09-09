"""Issue #165 H1 amortized-acquisition capsule.

Polynomial microscope only. Production methods.py is imported, not copied.
No src/ edits. New salts. Ordinary-parent parity and restart/revocation.
Library capital that exceeds later-task savings is a first-class negative.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

SCHEMA = "ocm.h1.amortized-acquisition.v1"
METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-h1-amortized-train-v1"
VAL_SALT = "orion-ocm-h1-amortized-val-v1"
LATER_SALT = "orion-ocm-h1-amortized-later-v1"
TRAIN_N = 16
VAL_N = 16
LATER_N = 16
TRAIN_LEN = 4
VAL_LEN = 5
LATER_LEN = 6
CANDIDATE_CAP = 8
MIN_SUPPORT = 2
FRAGMENT_MIN_LENGTH = 2
FRAGMENT_MAX_LENGTH = 4
SCOPE = Scope.of("polynomial-h1-amortized.v1")
MACRO_TOKEN = "MACRO"
FOREIGN_SALTS = (
    "orion-ocm-g2-macro-training-v1",
    "orion-ocm-g2-macro-validation-v1",
    "orion-ocm-g2-macro-test-v1",
    "orion-ocm-g2-strong-parents-train-v1",
    "orion-ocm-g2-strong-parents-test-v1",
    "orion-ocm-g2-ugate-train-v2",
    "orion-ocm-g2-ugate-val-v2",
    "orion-ocm-g2-ugate-test-v2",
)
CHARGED = (
    "new_information",
    "examples",
    "compute",
    "verifier_calls",
    "state_written",
)


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def zero_cost() -> dict[str, int]:
    return {k: 0 for k in CHARGED}


def add_cost(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {k: a[k] + b[k] for k in CHARGED}


def tree_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    if root.is_file():
        return root.stat().st_size
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def population(max_length: int):
    best = {}
    for length in range(max_length + 1):
        for program in product(M.PRIMITIVES, repeat=length):
            task = M.PolynomialTask(f"len-{length}", M.normal_form(program))
            best.setdefault(task.fingerprint, (length, task, program))
    return best


def take(pop, length: int, salt: str, n: int):
    pool = [(task, program) for _fp, (minimum, task, program) in pop.items() if minimum == length]
    chosen = tuple(
        sorted(pool, key=lambda item: (stable_rank(salt, item[0].fingerprint), item[0].fingerprint))[:n]
    )
    if len(chosen) != n:
        raise RuntimeError(f"stratum too small: {len(chosen)} < {n}")
    return chosen


def proper_fragments(program):
    out = set()
    for start in range(len(program)):
        stop = min(len(program), start + FRAGMENT_MAX_LENGTH)
        for end in range(start + FRAGMENT_MIN_LENGTH, stop + 1):
            fragment = tuple(program[start:end])
            if len(fragment) < len(program):
                out.add(fragment)
    return out


def mine(train_rows):
    support = Counter()
    for _task, program in train_rows:
        for fragment in proper_fragments(program):
            support[fragment] += 1
    candidates = tuple(
        sorted(
            (fragment for fragment, count in support.items() if count >= MIN_SUPPORT),
            key=lambda fragment: (-support[fragment], -len(fragment), fragment),
        )[:CANDIDATE_CAP]
    )
    return candidates, {fragment: support[fragment] for fragment in candidates}


def expand_tokens(token_word, macro):
    expanded = []
    used = False
    for token in token_word:
        if token == MACRO_TOKEN:
            if macro is None:
                raise ValueError("macro token without macro")
            expanded.extend(macro)
            used = True
        else:
            if token not in M.PRIMITIVES:
                raise ValueError(f"unknown token {token}")
            expanded.append(token)
    return tuple(expanded), used


def build_search_index(macro, max_primitive_length: int):
    """Exact BFS grammar index. Duplicate tokenizations are charged; verifier once per program."""
    macro = tuple(macro) if macro is not None else None
    tokens = ((MACRO_TOKEN,) + M.PRIMITIVES) if macro is not None else M.PRIMITIVES
    seen_programs = set()
    first_by_coefficients = {}
    enumeration_attempts = 0
    unique_candidates_checked = 0
    for token_depth in range(max_primitive_length + 1):
        for token_word in product(tokens, repeat=token_depth):
            expanded, macro_used = expand_tokens(token_word, macro)
            if len(expanded) > max_primitive_length:
                continue
            enumeration_attempts += 1
            if expanded in seen_programs:
                continue
            seen_programs.add(expanded)
            unique_candidates_checked += 1
            coefficients = M.normal_form(expanded)
            first_by_coefficients.setdefault(
                coefficients,
                {
                    "enumeration_attempts": enumeration_attempts,
                    "unique_candidates_checked": unique_candidates_checked,
                    "token_word": token_word,
                    "program": expanded,
                    "macro_used": macro_used,
                },
            )
    return {
        "macro": macro,
        "max_primitive_length": max_primitive_length,
        "total_enumeration_attempts": enumeration_attempts,
        "total_unique_candidates_checked": unique_candidates_checked,
        "first_by_coefficients": first_by_coefficients,
    }


def solve_from_index(task, index):
    hit = index["first_by_coefficients"].get(task.coefficients)
    if hit is None:
        raise RuntimeError(f"registered grammar failed to solve {task.fingerprint}")
    if M.normal_form(tuple(hit["program"])) != task.coefficients:
        raise RuntimeError("macro index exact verification failed")
    return {
        "task": task.fingerprint,
        "enumeration_attempts": hit["enumeration_attempts"],
        "unique_candidates_checked": hit["unique_candidates_checked"],
        "token_word": hit["token_word"],
        "program": hit["program"],
        "macro_used": hit["macro_used"],
        "verified": True,
    }


def evaluate_index(tasks, index):
    rows = [solve_from_index(task, index) for task in tasks]
    compute = sum(row["enumeration_attempts"] for row in rows)
    new_information = sum(row["unique_candidates_checked"] for row in rows)
    return rows, compute, new_information


def rows_equal(a_rows, b_rows) -> bool:
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and tuple(a["program"]) == tuple(b["program"])
        and tuple(a["token_word"]) == tuple(b["token_word"])
        for a, b in zip(a_rows, b_rows)
    )


def later_cost(rows, examples: int = 0, state_written: int = 0) -> dict[str, int]:
    """Online search until first verified identity. Index materialization is not this vector."""
    return {
        "new_information": sum(row["unique_candidates_checked"] for row in rows),
        "examples": examples,
        "compute": sum(row["enumeration_attempts"] for row in rows),
        "verifier_calls": sum(row["unique_candidates_checked"] for row in rows),
        "state_written": state_written,
    }


def ordinary_persist(path: Path, macro) -> None:
    payload = {"macro": list(macro), "fingerprint": content_hash({"macro": macro})}
    temp = path.with_suffix(".tmp")
    with temp.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def ordinary_load(path: Path):
    payload = json.loads(path.read_text())
    macro = tuple(payload["macro"])
    if content_hash({"macro": macro}) != payload["fingerprint"]:
        raise RuntimeError("ordinary macro persistence identity mismatch")
    return macro


def admit_macro(root: Path, macro, training_receipt, utility_receipt, revoke=False):
    runtime = OCMRuntime(root)
    _tr, training_evidence = runtime.admit_evidence(
        training_receipt, Channel.PROOF, "h1-amortized-training.v1", scope=SCOPE
    )
    _ur, utility_evidence = runtime.admit_evidence(
        utility_receipt, Channel.OBSERVATION, "h1-amortized-utility.v1", scope=SCOPE
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})
    source_payload = {
        "kind": "h1.macro.support.v1",
        "training": content_hash(training_receipt),
        "utility": content_hash(utility_receipt),
    }
    source_id = "h1-macro-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {
        "kind": "macro.operator.v1",
        "macro": macro,
        "fingerprint": content_hash({"macro": macro}),
    }
    atom_id = "macro-operator:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    if revoke:
        runtime.revoke((training_evidence,))
    runtime.persist()
    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if revoke:
        if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
            raise RuntimeError("revoked macro remained live")
        return None, atom_id, training_evidence, utility_evidence, tree_bytes(root)
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("macro did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("macro content identity mismatch")
    loaded = tuple(stored["macro"])
    if content_hash({"macro": loaded}) != stored["fingerprint"]:
        raise RuntimeError("macro fingerprint mismatch")
    return loaded, atom_id, training_evidence, utility_evidence, tree_bytes(root)


def box_status(later_kt: dict[str, int], later_k0: dict[str, int], coord: str) -> str:
    if later_kt[coord] < later_k0[coord]:
        return "EARNED_AT_SCOPE"
    return "NO_STRICT_SAVING"


def mechanism_comment(terminal: str, admitted, later_kt, later_k0, library, lifetime_kt, lifetime_k0) -> str:
    if terminal == "UTILITY_GATE_SELECTS_NO_METHOD":
        return (
            "No G2 macro earned: every training-derived fragment lost aggregate validation "
            "search to the primitive index. H1 later-task comparison was not run under an earned library."
        )
    if terminal == "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY":
        return "Ordinary persistent JSON and OCM-live restart disagreed on later-task search; H1 cannot be checked."
    if terminal == "CANNOT_CHECK_REVOCATION_ABLATION":
        return "Revoking training evidence did not restore primitive later-task search; H1 cannot be checked."
    if terminal == "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER":
        saved_info = later_k0["new_information"] - later_kt["new_information"]
        extra_compute = later_kt["compute"] - later_k0["compute"]
        return (
            f"Earned macro {list(admitted) if admitted else []} was admitted by a length-5 validation "
            f"utility gate but did not strictly reduce later length-6 related-task compute "
            f"({later_kt['compute']} vs K_0 {later_k0['compute']}, extra {extra_compute}). "
            "Mechanism: the MACRO token expands BFS from a 4-ary to a 5-ary grammar; duplicate "
            "tokenizations are charged as compute, so aggregate enumeration attempts rose even "
            f"while unique programs / verifier calls fell by {saved_info} "
            f"({later_kt['new_information']} vs {later_k0['new_information']}). "
            f"Library capital is also unrecouped: training+tournament compute {library['compute']} "
            f"plus later K_t {later_kt['compute']} = {lifetime_kt['compute']} vs K_0 later "
            f"{lifetime_k0['compute']}. Frequency's winner was not deployed. Ordinary persistent "
            "library ties OCM (PARENT_SUFFICIENT vs program-library search). Salts and counts "
            "were not retuned."
        )
    if terminal == "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS":
        saved = later_k0["compute"] - later_kt["compute"]
        return (
            "Utility-gated G2 macros reduce later related-task search against reset, but library capital "
            f"does not pay back on this frozen 16/16/16 length-4/5/6 horizon: training+tournament compute "
            f"{library['compute']} plus later K_t {later_kt['compute']} = {lifetime_kt['compute']} "
            f">= K_0 later {lifetime_k0['compute']} (later-task compute saving {saved}). "
            "The dominant mechanism is the validation tournament: every candidate is fully searched on "
            "the disjoint validation stratum before admission, and that selection work exceeds later "
            "savings. Training demonstrations and persist bytes are additional unrecouped capital. "
            "Ordinary persistent library ties OCM (PARENT_SUFFICIENT vs program-library search). "
            "Salts and counts were not retuned."
        )
    if terminal == "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE":
        return (
            "Later related-task C_acquire is strictly cheaper given the earned library, and library "
            "capital is recouped on the frozen compute coordinate. Ordinary parent ties OCM. "
            "Not a programme-wide H1 close and not an OCM residual over library search."
        )
    return terminal


def run_study() -> dict[str, Any]:
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")
    for salt in (TRAIN_SALT, VAL_SALT, LATER_SALT):
        if salt in FOREIGN_SALTS:
            raise RuntimeError(f"H1 salt collides with a frozen G2 salt: {salt}")

    pop = population(LATER_LEN)
    train = take(pop, TRAIN_LEN, TRAIN_SALT, TRAIN_N)
    val = take(pop, VAL_LEN, VAL_SALT, VAL_N)
    later = take(pop, LATER_LEN, LATER_SALT, LATER_N)
    train_fp = {task.fingerprint for task, _ in train}
    val_fp = {task.fingerprint for task, _ in val}
    later_fp = {task.fingerprint for task, _ in later}
    if train_fp & val_fp or train_fp & later_fp or val_fp & later_fp:
        raise RuntimeError("stratum overlap")

    train_tasks = tuple(task for task, _ in train)
    val_tasks = tuple(task for task, _ in val)
    later_tasks = tuple(task for task, _ in later)
    train_programs = tuple(program for _, program in train)

    train_index = build_search_index(None, TRAIN_LEN)
    train_rows, train_compute, train_info = evaluate_index(train_tasks, train_index)
    for row, (_task, program) in zip(train_rows, train):
        if tuple(row["program"]) != tuple(program) and M.normal_form(tuple(row["program"])) != _task.coefficients:
            raise RuntimeError("training solve mismatch")

    candidates, support = mine(train)
    primitive_val_index = build_search_index(None, VAL_LEN)
    primitive_val_rows, primitive_val_compute, primitive_val_info = evaluate_index(
        val_tasks, primitive_val_index
    )
    evaluations = []
    for candidate in candidates:
        index = build_search_index(candidate, VAL_LEN)
        rows, attempts, info = evaluate_index(val_tasks, index)
        evaluations.append(
            {
                "fragment": candidate,
                "support": support[candidate],
                "val_compute": attempts,
                "val_new_information": info,
                "beats_primitive": attempts < primitive_val_compute,
                "rows": rows,
            }
        )
    useful = [row for row in evaluations if row["beats_primitive"]]
    admitted = None
    if useful:
        admitted = min(useful, key=lambda row: (row["val_compute"], row["fragment"]))["fragment"]
    frequency_selected = candidates[0] if candidates else None
    tournament_compute = primitive_val_compute + sum(row["val_compute"] for row in evaluations)
    tournament_info = primitive_val_info + sum(row["val_new_information"] for row in evaluations)

    library = {
        "new_information": train_info + tournament_info,
        "examples": TRAIN_N,
        "compute": train_compute + tournament_compute,
        "verifier_calls": train_info + tournament_info,
        "state_written": 0,
    }

    primitive_later_index = build_search_index(None, LATER_LEN)
    k0_rows, k0_compute, k0_info = evaluate_index(later_tasks, primitive_later_index)
    later_k0 = later_cost(k0_rows)

    training_receipt = {
        "schema": "h1.amortized.training.v1",
        "source_blob": METHOD_BLOB,
        "training_ids": [task.fingerprint for task in train_tasks],
        "training_programs": [list(program) for program in train_programs],
        "candidate_order": [list(fragment) for fragment in candidates],
        "selected_macro": list(admitted) if admitted is not None else None,
    }
    utility_receipt = {
        "schema": "h1.amortized.utility.v1",
        "accepted": admitted is not None,
        "primitive_val_compute": primitive_val_compute,
        "admitted": list(admitted) if admitted is not None else None,
        "validation_ids": [task.fingerprint for task in val_tasks],
    }

    ordinary_bytes = ocm_bytes = revoked_bytes = 0
    ocm_atom_id = training_evidence = utility_evidence = None
    if admitted is None:
        ordinary_rows = ocm_rows = revoked_rows = k0_rows
        ordinary_equal_ocm = revoked_equal_primitive = True
    else:
        selected_index = build_search_index(admitted, LATER_LEN)
        selected_rows, _selected_compute, _selected_info = evaluate_index(later_tasks, selected_index)
        with tempfile.TemporaryDirectory(prefix="ocm-h1-amortized-") as temp_dir:
            root = Path(temp_dir)
            ordinary_path = root / "ordinary-macro.json"
            ordinary_persist(ordinary_path, admitted)
            ordinary_macro = ordinary_load(ordinary_path)
            ordinary_bytes = tree_bytes(ordinary_path)
            ocm_macro, ocm_atom_id, training_evidence, utility_evidence, ocm_bytes = admit_macro(
                root / "ocm-live", admitted, training_receipt, utility_receipt, revoke=False
            )
            revoked_macro, _revoked_atom, _rte, _rue, revoked_bytes = admit_macro(
                root / "ocm-revoked", admitted, training_receipt, utility_receipt, revoke=True
            )
        ordinary_rows, _oc, _oi = evaluate_index(
            later_tasks, build_search_index(ordinary_macro, LATER_LEN)
        )
        ocm_rows, _kc, _ki = evaluate_index(later_tasks, build_search_index(ocm_macro, LATER_LEN))
        revoked_rows, _rc, _ri = evaluate_index(
            later_tasks, build_search_index(revoked_macro, LATER_LEN)
        )
        if not rows_equal(selected_rows, ordinary_rows):
            raise RuntimeError("ordinary persisted macro changed exact search behavior")
        ordinary_equal_ocm = rows_equal(ordinary_rows, ocm_rows)
        revoked_equal_primitive = rows_equal(revoked_rows, k0_rows)

    later_kt = later_cost(ocm_rows)
    later_ordinary = later_cost(ordinary_rows)
    later_revoked = later_cost(revoked_rows)
    library["state_written"] = ocm_bytes
    lifetime_kt = add_cost(library, later_kt)
    lifetime_k0 = add_cost(zero_cost(), later_k0)

    per_task = []
    k0_by_task = {row["task"]: row for row in k0_rows}
    for row in ocm_rows:
        base = k0_by_task[row["task"]]
        per_task.append(
            {
                "task": row["task"],
                "k0_compute": base["enumeration_attempts"],
                "kt_compute": row["enumeration_attempts"],
                "k0_new_information": base["unique_candidates_checked"],
                "kt_new_information": row["unique_candidates_checked"],
                "macro_used": row["macro_used"],
                "strict_compute_saving": row["enumeration_attempts"] < base["enumeration_attempts"],
                "causal_macro_win": bool(
                    row["macro_used"] and row["enumeration_attempts"] < base["enumeration_attempts"]
                ),
            }
        )
    later_strict_compute = later_kt["compute"] < later_k0["compute"]
    later_strict_new_information = later_kt["new_information"] < later_k0["new_information"]
    later_strict_verifier = later_kt["verifier_calls"] < later_k0["verifier_calls"]
    h1_vector_strictly_less = (
        later_strict_new_information
        and later_strict_compute
        and later_strict_verifier
        and later_kt["examples"] < later_k0["examples"]
        and later_kt["state_written"] < later_k0["state_written"]
    )
    library_pays_back = lifetime_kt["compute"] < lifetime_k0["compute"]
    causal_wins = sum(1 for row in per_task if row["causal_macro_win"])

    if admitted is None:
        terminal = "UTILITY_GATE_SELECTS_NO_METHOD"
    elif not ordinary_equal_ocm:
        terminal = "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY"
    elif not revoked_equal_primitive:
        terminal = "CANNOT_CHECK_REVOCATION_ABLATION"
    elif not later_strict_compute:
        terminal = "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER"
    elif not library_pays_back:
        terminal = "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS"
    else:
        terminal = "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE"

    if library_pays_back and later_strict_compute:
        lifetime_terminal = "LIFETIME_LIBRARY_PAYBACK_ON_COMPUTE"
    else:
        lifetime_terminal = "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS"

    boxes = {
        "H1/001-new_information": {
            "text": "new information",
            "status": box_status(later_kt, later_k0, "new_information"),
            "later_kt": later_kt["new_information"],
            "later_k0": later_k0["new_information"],
            "library": library["new_information"],
            "lifetime_kt": lifetime_kt["new_information"],
            "lifetime_k0": lifetime_k0["new_information"],
            "unit": "unique expanded programs checked until threshold",
        },
        "H1/002-examples_demonstrations": {
            "text": "examples/demonstrations",
            "status": box_status(later_kt, later_k0, "examples"),
            "later_kt": later_kt["examples"],
            "later_k0": later_k0["examples"],
            "library": library["examples"],
            "lifetime_kt": lifetime_kt["examples"],
            "lifetime_k0": lifetime_k0["examples"],
            "unit": "training demonstrations charged as library capital; later additional examples are 0 in both arms",
            "note": (
                "Later-task acquisition is search, not extra teaching examples. Training demonstrations "
                "are library capital and are not recouped as a later-task example saving."
            ),
        },
        "H1/003-environment_interactions": {
            "text": "environment interactions",
            "status": "CANNOT_CHECK_NO_ENVIRONMENT_CHANNEL",
            "note": "Polynomial microscope has no external environment interaction channel.",
        },
        "H1/004-compute": {
            "text": "compute",
            "status": box_status(later_kt, later_k0, "compute"),
            "later_kt": later_kt["compute"],
            "later_k0": later_k0["compute"],
            "library": library["compute"],
            "lifetime_kt": lifetime_kt["compute"],
            "lifetime_k0": lifetime_k0["compute"],
            "unit": "token-word enumeration attempts until first verified identity",
        },
        "H1/005-verifier_calls": {
            "text": "verifier calls",
            "status": box_status(later_kt, later_k0, "verifier_calls"),
            "later_kt": later_kt["verifier_calls"],
            "later_k0": later_k0["verifier_calls"],
            "library": library["verifier_calls"],
            "lifetime_kt": lifetime_kt["verifier_calls"],
            "lifetime_k0": lifetime_k0["verifier_calls"],
            "unit": "normal_form polynomial-identity checks on unique expanded programs",
        },
        "H1/006-io_tool_calls": {
            "text": "IO/tool calls",
            "status": "CANNOT_CHECK_NO_IO_TOOL_CHANNEL",
            "note": "No external tool/IO channel on this microscope; persist bytes are charged under state written.",
        },
        "H1/007-human_instructional_burden": {
            "text": "human instructional burden",
            "status": "CANNOT_CHECK_NO_HUMAN_INSTRUCTION_CHANNEL",
            "note": "No human teaching channel; training demonstrations are machine-solved identities.",
        },
        "H1/008-state_written": {
            "text": "state written",
            "status": box_status(later_kt, later_k0, "state_written"),
            "later_kt": later_kt["state_written"],
            "later_k0": later_k0["state_written"],
            "library": library["state_written"],
            "lifetime_kt": lifetime_kt["state_written"],
            "lifetime_k0": lifetime_k0["state_written"],
            "ordinary_bytes": ordinary_bytes,
            "ocm_bytes": ocm_bytes,
            "revoked_bytes": revoked_bytes,
            "unit": "persist bytes of the earned library; later incremental persist is 0",
            "note": "K_t writes ordinary JSON and an OCM snapshot; K_0 writes nothing. Later incremental state is equal (0).",
        },
    }

    comment = mechanism_comment(
        terminal, admitted, later_kt, later_k0, library, lifetime_kt, lifetime_k0
    )
    parent_tied = ordinary_equal_ocm and later_ordinary["compute"] == later_kt["compute"]

    return {
        "schema": SCHEMA,
        "issue": 165,
        "head": git_head(),
        "terminal": terminal,
        "lifetime_terminal": lifetime_terminal,
        "h1_vector_strictly_less": h1_vector_strictly_less,
        "programme_wide_close": False,
        "production_src_edited": False,
        "methods_blob": observed_blob,
        "evidence_class": "E3",
        "contribution_level": "L2",
        "parent": "ordinary persistent macro-library BFS (DreamCoder/Stitch/program-library search)",
        "parent_sufficient": parent_tied and admitted is not None,
        "mechanism_comment": comment,
        "claim_ceiling": (
            "Bounded H1 later-task comparison on one exact polynomial microscope after a utility-gated "
            "G2 macro. Ordinary parent parity and restart/revocation are required. Library capital is "
            "first-class. Not programme-wide H1, not P6 residual, not language meta-learning, not an "
            "OCM architecture uniqueness claim."
        ),
        "salts": {"train": TRAIN_SALT, "val": VAL_SALT, "later": LATER_SALT},
        "partition": {
            "train_n": TRAIN_N,
            "val_n": VAL_N,
            "later_n": LATER_N,
            "train_min_length": TRAIN_LEN,
            "val_min_length": VAL_LEN,
            "later_min_length": LATER_LEN,
            "train_ids": [task.fingerprint for task in train_tasks],
            "val_ids": [task.fingerprint for task in val_tasks],
            "later_ids": [task.fingerprint for task in later_tasks],
        },
        "library": {
            "candidates": [list(fragment) for fragment in candidates],
            "support": {str(fragment): count for fragment, count in support.items()},
            "frequency_selected": list(frequency_selected) if frequency_selected else [],
            "admitted": list(admitted) if admitted else [],
            "gate_refused_frequency": bool(
                frequency_selected is not None and admitted is not None and admitted != frequency_selected
            ),
            "cost": library,
            "training_compute": train_compute,
            "tournament_compute": tournament_compute,
            "primitive_val_compute": primitive_val_compute,
            "evaluations": [
                {
                    "fragment": list(row["fragment"]),
                    "support": row["support"],
                    "val_compute": row["val_compute"],
                    "beats_primitive": row["beats_primitive"],
                }
                for row in evaluations
            ],
        },
        "later": {
            "k0": later_k0,
            "kt": later_kt,
            "ordinary": later_ordinary,
            "revoked": later_revoked,
            "strict_compute_saving": later_strict_compute,
            "strict_new_information_saving": later_strict_new_information,
            "strict_verifier_saving": later_strict_verifier,
            "causal_macro_wins": causal_wins,
            "ordinary_equals_ocm": ordinary_equal_ocm,
            "revoked_equals_primitive": revoked_equal_primitive,
            "per_task": per_task,
        },
        "lifetime": {
            "kt": lifetime_kt,
            "k0": lifetime_k0,
            "library_pays_back_compute": library_pays_back,
            "note": (
                "K_0 lifetime is later-task C_acquire only (reset). K_t lifetime is library capital "
                "(training search + every candidate validation search + persist bytes + demonstrations) "
                "plus later-task C_acquire."
            ),
        },
        "ocm": {
            "atom_id": ocm_atom_id,
            "training_evidence": training_evidence,
            "utility_evidence": utility_evidence,
            "restart_before_later": admitted is not None,
            "support_withdrawal_ablation": admitted is not None,
            "ordinary_bytes": ordinary_bytes,
            "ocm_bytes": ocm_bytes,
            "revoked_bytes": revoked_bytes,
        },
        "boxes": boxes,
        "earned": sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_SCOPE"),
        "not_earned": sorted(k for k, v in boxes.items() if v["status"] == "NO_STRICT_SAVING"),
        "cannot_check": sorted(k for k, v in boxes.items() if str(v["status"]).startswith("CANNOT_CHECK")),
        "not_issued": [
            "PROGRAMME_WIDE_H1_CLOSE",
            "P6_MATCHED_LIFETIME_RESIDUAL",
            "LANGUAGE_META_LEARNING",
            "OCM_ARCHITECTURE_UNIQUENESS_OVER_LIBRARY_SEARCH",
            "H2_SPARSE_RELEVANT_COGNITION",
            "H5_LIFETIME_ECONOMICS_CROSSOVER",
        ],
        "negative_terminals_frozen": [
            "UTILITY_GATE_SELECTS_NO_METHOD",
            "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER",
            "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS",
            "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY",
            "CANNOT_CHECK_REVOCATION_ABLATION",
        ],
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
                "earned": result["earned"],
                "not_earned": result["not_earned"],
                "cannot_check": result["cannot_check"],
                "admitted": result["library"]["admitted"],
                "later_k0_compute": result["later"]["k0"]["compute"],
                "later_kt_compute": result["later"]["kt"]["compute"],
                "library_compute": result["library"]["cost"]["compute"],
                "lifetime_kt_compute": result["lifetime"]["kt"]["compute"],
                "lifetime_k0_compute": result["lifetime"]["k0"]["compute"],
                "library_pays_back_compute": result["lifetime"]["library_pays_back_compute"],
                "lifetime_terminal": result["lifetime_terminal"],
                "parent_sufficient": result["parent_sufficient"],
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
