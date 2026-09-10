"""Issue #165 H1 amortized-acquisition successor: recoup library capital.

v1 (research/h1-amortized-acquisition-v1) added MACRO as a 5th BFS token.
Grammar width 4→5 made later compute rise (NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER).
Frozen; salts were not retuned.

v2 (research/h1-amortized-rewrite-v2) served the fragment as a greedy-leftmost
rewrite inside the same four primitives. Later compute fell (59929→36289) but
the validation tournament's capital exceeded that saving
(LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS). Frozen; salts were not retuned.

This capsule keeps v2's 4-primitive rewrite serving and attacks CAPITAL:
  (a) SEARCH_AWARE cheap selector from research/g2-acquisition-economics-v1
      (scan, not tournament) as the acquisition path, with the G2 grammar-
      widening term zeroed because rewrite serving does not add a token;
  (b) charge that acquisition once, then serve many related later identities
      without re-running selection;
  (c) prune the library to the single SCAN-selected rewrite.

A single disjoint confirmation search (primitive vs the one selected fragment)
remains, so admission is still earned, not a hidden 8-candidate tournament.
Token-scan work is never added to enumeration compute. Library capital stays
on the ledger. A negative with an honest break-even horizon is first-class.

Production methods.py is imported, not copied. No src edits. New salts.
"""
from __future__ import annotations

import hashlib
import json
import math
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

SCHEMA = "ocm.h1.amortized-lifetime.v3"
METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
TRAIN_SALT = "orion-ocm-h1-lifetime-train-v3"
VAL_SALT = "orion-ocm-h1-lifetime-val-v3"
LATER_SALT = "orion-ocm-h1-lifetime-later-v3"
TRAIN_N = 16
VAL_N = 16
LATER_N = 48
TRAIN_LEN = 4
VAL_LEN = 5
LATER_LEN = 6
CANDIDATE_CAP = 8
MIN_SUPPORT = 2
FRAGMENT_MIN_LENGTH = 2
FRAGMENT_MAX_LENGTH = 4
SCOPE = Scope.of("polynomial-h1-amortized-lifetime.v3")
REWRITE_MARK = "REWRITE"
FOREIGN_SALTS = (
    "orion-ocm-h1-amortized-train-v1",
    "orion-ocm-h1-amortized-val-v1",
    "orion-ocm-h1-amortized-later-v1",
    "orion-ocm-h1-rewrite-train-v2",
    "orion-ocm-h1-rewrite-val-v2",
    "orion-ocm-h1-rewrite-later-v2",
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


def greedy_rewrite(program, fragment):
    """Collapse leftmost non-overlapping fragment occurrences to one operator each.

    The underlying word stays in the 4-primitive alphabet. Rewrite is a cost
    function / serving order, not a 5th BFS token.
    """
    program = tuple(program)
    if fragment is None:
        return program, False, len(program)
    fragment = tuple(fragment)
    if not fragment:
        return program, False, len(program)
    width = len(fragment)
    operator_word = []
    used = False
    index = 0
    while index < len(program):
        window = program[index:index + width]
        if window == fragment:
            operator_word.append(REWRITE_MARK)
            used = True
            index += width
        else:
            operator_word.append(program[index])
            index += 1
    return tuple(operator_word), used, len(operator_word)


def four_primitive_words(max_primitive_length: int):
    """Exact 4-ary BFS order. Never introduces a MACRO/rewrite token."""
    original_index = 0
    for token_depth in range(max_primitive_length + 1):
        for token_word in product(M.PRIMITIVES, repeat=token_depth):
            original_index += 1
            yield original_index, token_word


def build_search_index(fragment, max_primitive_length: int):
    """4-primitive grammar index; fragment rewrites serving order only.

    Each 4-primitive word is generated once. Operator-cost is greedy-rewrite
    length. Visit order is (operator-cost, rewritten-first, original 4-ary
    index). Primitive (fragment is None) reduces to ordinary 4-ary BFS.
    """
    fragment = tuple(fragment) if fragment is not None else None
    entries = []
    for original_index, token_word in four_primitive_words(max_primitive_length):
        operator_word, rewrite_used, operator_cost = greedy_rewrite(token_word, fragment)
        entries.append(
            {
                "original_index": original_index,
                "operator_cost": operator_cost,
                "rewrite_rank": 0 if rewrite_used else 1,
                "token_word": token_word,
                "operator_word": operator_word,
                "program": token_word,
                "rewrite_used": rewrite_used,
            }
        )
    entries.sort(key=lambda row: (row["operator_cost"], row["rewrite_rank"], row["original_index"]))

    seen_programs = set()
    first_by_coefficients = {}
    enumeration_attempts = 0
    unique_candidates_checked = 0
    for entry in entries:
        enumeration_attempts += 1
        program = entry["program"]
        if program in seen_programs:
            continue
        seen_programs.add(program)
        unique_candidates_checked += 1
        coefficients = M.normal_form(program)
        first_by_coefficients.setdefault(
            coefficients,
            {
                "enumeration_attempts": enumeration_attempts,
                "unique_candidates_checked": unique_candidates_checked,
                "token_word": entry["token_word"],
                "operator_word": entry["operator_word"],
                "program": program,
                "rewrite_used": entry["rewrite_used"],
                "macro_used": entry["rewrite_used"],
                "operator_cost": entry["operator_cost"],
            },
        )
    if enumeration_attempts != unique_candidates_checked:
        raise RuntimeError("rewrite index charged a duplicate 4-primitive word")
    return {
        "fragment": fragment,
        "grammar_tokens": list(M.PRIMITIVES),
        "grammar_width": len(M.PRIMITIVES),
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
        raise RuntimeError("rewrite index exact verification failed")
    if any(token not in M.PRIMITIVES for token in hit["program"]):
        raise RuntimeError("winning program left the 4-primitive grammar")
    return {
        "task": task.fingerprint,
        "enumeration_attempts": hit["enumeration_attempts"],
        "unique_candidates_checked": hit["unique_candidates_checked"],
        "token_word": hit["token_word"],
        "operator_word": hit["operator_word"],
        "program": hit["program"],
        "rewrite_used": hit["rewrite_used"],
        "macro_used": hit["macro_used"],
        "operator_cost": hit["operator_cost"],
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
        and tuple(a["operator_word"]) == tuple(b["operator_word"])
        and a["rewrite_used"] == b["rewrite_used"]
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


def cumulative_words(max_depth: int, primitives: int = 4) -> int:
    """Closed-form 4-ary complete-word count of length 0..max_depth. No search."""
    if max_depth < 0:
        return 0
    return sum(primitives ** depth for depth in range(max_depth + 1))


def score_search_aware(candidates, train_programs):
    """G2 SEARCH_AWARE scan with the grammar-widening term zeroed.

    research/g2-acquisition-economics-v1 prices two closed-form terms:

      BENEFIT  rewriting shortens the token word, so the program is reached
               at a shallower BFS depth;
      COST     adding a MACRO token widens every depth.

    v2 rewrite serving never adds a token, so COST is identically 0. The
    remaining term is estimated 4-ary BFS volume saved by reducing operator-cost
    depth on already-solved training programs. This is a scan: token operations
    only, zero enumeration attempts, never added to compute.
    """
    scores = {}
    token_operations = 0
    for fragment in candidates:
        gain = 0.0
        for program in train_programs:
            token_operations += len(program)
            _word, _used, operator_cost = greedy_rewrite(program, fragment)
            baseline = cumulative_words(len(program))
            rewritten = cumulative_words(operator_cost)
            gain += baseline - rewritten
        scores[fragment] = gain
    return scores, token_operations


def select_search_aware(candidates, train_programs):
    if not candidates:
        return None, {}, 0
    scores, token_operations = score_search_aware(candidates, train_programs)
    winner = min(candidates, key=lambda fragment: (-scores[fragment], fragment))
    if scores[winner] <= 0:
        return None, scores, token_operations
    return winner, scores, token_operations


def ordinary_persist(path: Path, fragment) -> None:
    payload = {"fragment": list(fragment), "fingerprint": content_hash({"fragment": fragment})}
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
    fragment = tuple(payload["fragment"])
    if content_hash({"fragment": fragment}) != payload["fingerprint"]:
        raise RuntimeError("ordinary fragment persistence identity mismatch")
    return fragment


def admit_fragment(root: Path, fragment, training_receipt, utility_receipt, revoke=False):
    runtime = OCMRuntime(root)
    _tr, training_evidence = runtime.admit_evidence(
        training_receipt, Channel.PROOF, "h1-lifetime-training.v3", scope=SCOPE
    )
    _ur, utility_evidence = runtime.admit_evidence(
        utility_receipt, Channel.OBSERVATION, "h1-lifetime-utility.v3", scope=SCOPE
    )
    warrant = WarrantProfile.of({training_evidence, utility_evidence})
    source_payload = {
        "kind": "h1.rewrite.support.v3",
        "training": content_hash(training_receipt),
        "utility": content_hash(utility_receipt),
    }
    source_id = "h1-lifetime-support:" + content_hash(source_payload)
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
        "kind": "rewrite.operator.v3",
        "fragment": fragment,
        "fingerprint": content_hash({"fragment": fragment}),
        "grammar": list(M.PRIMITIVES),
        "serving": "greedy-leftmost-rewrite-in-4-primitive-grammar",
        "acquisition": "search-aware-scan-plus-single-confirmation",
    }
    atom_id = "rewrite-operator:" + content_hash(payload)
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
            raise RuntimeError("revoked rewrite remained live")
        return None, atom_id, training_evidence, utility_evidence, tree_bytes(root)
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("rewrite did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("rewrite content identity mismatch")
    loaded = tuple(stored["fragment"])
    if content_hash({"fragment": loaded}) != stored["fingerprint"]:
        raise RuntimeError("rewrite fingerprint mismatch")
    if tuple(stored["grammar"]) != M.PRIMITIVES:
        raise RuntimeError("persisted rewrite left the 4-primitive grammar")
    return loaded, atom_id, training_evidence, utility_evidence, tree_bytes(root)


def box_status(later_kt: dict[str, int], later_k0: dict[str, int], coord: str) -> str:
    if later_kt[coord] < later_k0[coord]:
        return "EARNED_AT_SCOPE"
    return "NO_STRICT_SAVING"


def break_even_n(library_compute: int, later_k0_compute: int, later_kt_compute: int, later_n: int):
    saved = later_k0_compute - later_kt_compute
    if later_n <= 0 or saved <= 0:
        return None, 0.0
    saving_per_task = saved / later_n
    return int(math.ceil(library_compute / saving_per_task)), saving_per_task


def mechanism_comment(
    terminal: str,
    admitted,
    later_kt,
    later_k0,
    library,
    lifetime_kt,
    lifetime_k0,
    break_even,
    saving_per_task,
    scan_ops,
    confirmation_compute,
    later_n: int,
) -> str:
    if terminal == "UTILITY_GATE_SELECTS_NO_METHOD":
        return (
            "No rewrite earned: SEARCH_AWARE scan found no positive-gain fragment, or the "
            "single disjoint confirmation lost aggregate validation search to the primitive "
            "4-ary index. H1 later-task comparison was not run under an earned library. "
            "The 8-candidate validation tournament was not run. Salts and predecessor "
            "counts were not retuned."
        )
    if terminal == "CANNOT_CHECK_COMPONENT_TRANSPLANT_PARITY":
        return "Ordinary persistent JSON and OCM-live restart disagreed on later-task search; H1 cannot be checked."
    if terminal == "CANNOT_CHECK_REVOCATION_ABLATION":
        return "Revoking training evidence did not restore primitive later-task search; H1 cannot be checked."
    horizon = (
        f"registered later horizon n={later_n} length-{LATER_LEN} related identities; "
        f"SEARCH_AWARE scan {scan_ops} token ops (not added to compute); "
        f"single confirmation compute {confirmation_compute}; "
        f"training+confirmation library compute {library['compute']}"
    )
    if terminal == "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER":
        extra_compute = later_kt["compute"] - later_k0["compute"]
        return (
            f"Earned rewrite {list(admitted) if admitted else []} was admitted by SEARCH_AWARE "
            f"plus a single confirmation but did not strictly reduce later related-task compute "
            f"({later_kt['compute']} vs K_0 {later_k0['compute']}, extra {extra_compute}). "
            "Mechanism: greedy-leftmost rewrite inside the same 4-primitive grammar "
            "(v2 serving, not a 5th BFS token). v1's 5-ary MACRO product and v2's "
            f"8-candidate tournament are closed. {horizon}. Ordinary persistent library "
            "ties OCM (PARENT_SUFFICIENT vs program-library rewrite). Salts and predecessor "
            "counts were not retuned."
        )
    if terminal == "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS":
        saved = later_k0["compute"] - later_kt["compute"]
        be = "undefined (no positive per-task saving)" if break_even is None else str(break_even)
        return (
            "SEARCH_AWARE 4-primitive rewrite reduces later related-task search against reset, "
            f"but remaining library capital does not pay back on this registered n={later_n} "
            f"length-{LATER_LEN} horizon: training+confirmation compute {library['compute']} "
            f"plus later K_t {later_kt['compute']} = {lifetime_kt['compute']} >= K_0 later "
            f"{lifetime_k0['compute']} (later-task compute saving {saved}, "
            f"{saving_per_task:.3f} per later identity). Honest break-even horizon is "
            f"{be} length-{LATER_LEN} related identities at the observed per-task saving. "
            "Acquisition was a scan plus one confirmation, not an 8-candidate tournament; "
            "that capital was not dropped from the ledger. Ordinary persistent library "
            "ties OCM (PARENT_SUFFICIENT vs program-library rewrite). Salts and predecessor "
            "counts were not retuned."
        )
    if terminal == "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE":
        be = "undefined" if break_even is None else str(break_even)
        return (
            "Later related-task C_acquire is strictly cheaper given the earned 4-primitive "
            "rewrite, and library capital (training search + SEARCH_AWARE scan + single "
            f"confirmation + persist + demonstrations) is recouped on the frozen compute "
            f"coordinate at n={later_n} (break-even {be} at the observed per-task saving). "
            "Ordinary parent ties OCM. Not a programme-wide H1 close and not an OCM residual "
            "over library rewrite. v1's 5-ary MACRO token is not used. v2's tournament "
            "is not re-run. Salts and predecessor counts were not retuned."
        )
    return terminal


def run_study() -> dict[str, Any]:
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")
    if tuple(M.PRIMITIVES) != ("inc", "dec", "double", "square"):
        raise RuntimeError("production primitive grammar drifted")
    for salt in (TRAIN_SALT, VAL_SALT, LATER_SALT):
        if salt in FOREIGN_SALTS:
            raise RuntimeError(f"H1 lifetime salt collides with a frozen predecessor salt: {salt}")

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
    frequency_selected = candidates[0] if candidates else None
    selected, search_aware_scores, scan_token_operations = select_search_aware(candidates, train_programs)

    confirmation_compute = 0
    confirmation_info = 0
    primitive_val_compute = 0
    primitive_val_info = 0
    selected_val_compute = 0
    selected_val_info = 0
    val_indexes_built = 0
    beats_primitive = False
    admitted = None
    if selected is not None:
        primitive_val_index = build_search_index(None, VAL_LEN)
        if primitive_val_index["grammar_width"] != 4:
            raise RuntimeError("primitive index left 4-ary grammar")
        _primitive_val_rows, primitive_val_compute, primitive_val_info = evaluate_index(
            val_tasks, primitive_val_index
        )
        selected_val_index = build_search_index(selected, VAL_LEN)
        if selected_val_index["grammar_width"] != 4 or selected_val_index["grammar_tokens"] != list(M.PRIMITIVES):
            raise RuntimeError("rewrite index widened the grammar")
        if selected_val_index["total_enumeration_attempts"] != selected_val_index["total_unique_candidates_checked"]:
            raise RuntimeError("rewrite index charged duplicate tokenizations")
        _selected_val_rows, selected_val_compute, selected_val_info = evaluate_index(
            val_tasks, selected_val_index
        )
        val_indexes_built = 2
        confirmation_compute = primitive_val_compute + selected_val_compute
        confirmation_info = primitive_val_info + selected_val_info
        beats_primitive = selected_val_compute < primitive_val_compute
        if beats_primitive:
            admitted = selected

    library = {
        "new_information": train_info + confirmation_info,
        "examples": TRAIN_N,
        "compute": train_compute + confirmation_compute,
        "verifier_calls": train_info + confirmation_info,
        "state_written": 0,
    }

    primitive_later_index = build_search_index(None, LATER_LEN)
    k0_rows, k0_compute, k0_info = evaluate_index(later_tasks, primitive_later_index)
    later_k0 = later_cost(k0_rows)

    training_receipt = {
        "schema": "h1.lifetime.training.v3",
        "source_blob": METHOD_BLOB,
        "training_ids": [task.fingerprint for task in train_tasks],
        "training_programs": [list(program) for program in train_programs],
        "candidate_order": [list(fragment) for fragment in candidates],
        "selected_fragment": list(admitted) if admitted is not None else None,
        "selector": "SEARCH_AWARE",
        "serving": "greedy-leftmost-rewrite-in-4-primitive-grammar",
        "grammar": list(M.PRIMITIVES),
        "tournament_run": False,
    }
    utility_receipt = {
        "schema": "h1.lifetime.utility.v3",
        "accepted": admitted is not None,
        "selector": "SEARCH_AWARE",
        "confirmation_only": True,
        "primitive_val_compute": primitive_val_compute,
        "selected_val_compute": selected_val_compute,
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
        if selected_index["grammar_width"] != 4:
            raise RuntimeError("later rewrite index widened the grammar")
        selected_rows, _selected_compute, _selected_info = evaluate_index(later_tasks, selected_index)
        with tempfile.TemporaryDirectory(prefix="ocm-h1-lifetime-") as temp_dir:
            root = Path(temp_dir)
            ordinary_path = root / "ordinary-fragment.json"
            ordinary_persist(ordinary_path, admitted)
            ordinary_fragment = ordinary_load(ordinary_path)
            ocm_fragment, ocm_atom_id, training_evidence, utility_evidence, ocm_bytes = admit_fragment(
                root / "ocm-live", admitted, training_receipt, utility_receipt, revoke=False
            )
            revoked_fragment, _revoked_atom, _rte, _rue, revoked_bytes = admit_fragment(
                root / "ocm-revoked", admitted, training_receipt, utility_receipt, revoke=True
            )
            ordinary_bytes = ordinary_path.stat().st_size
        ordinary_rows, _o_compute, _o_info = evaluate_index(
            later_tasks, build_search_index(ordinary_fragment, LATER_LEN)
        )
        ocm_rows, _c_compute, _c_info = evaluate_index(
            later_tasks, build_search_index(ocm_fragment, LATER_LEN)
        )
        revoked_rows, _r_compute, _r_info = evaluate_index(
            later_tasks, build_search_index(revoked_fragment, LATER_LEN)
        )
        if not rows_equal(selected_rows, ordinary_rows):
            raise RuntimeError("ordinary persisted rewrite changed exact search behavior")
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
                "rewrite_used": row["rewrite_used"],
                "macro_used": row["macro_used"],
                "operator_word": list(row["operator_word"]),
                "strict_compute_saving": row["enumeration_attempts"] < base["enumeration_attempts"],
                "causal_rewrite_win": bool(
                    row["rewrite_used"] and row["enumeration_attempts"] < base["enumeration_attempts"]
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
    causal_wins = sum(1 for row in per_task if row["causal_rewrite_win"])
    horizon_n, saving_per_task = break_even_n(
        library["compute"], later_k0["compute"], later_kt["compute"], LATER_N
    )

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
            "unit": "unique 4-primitive programs checked until threshold",
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
            "lifetime_compute_recouped": library_pays_back,
            "break_even_n": horizon_n,
            "unit": "4-primitive programs visited in rewrite-cost order until first verified identity",
        },
        "H1/005-verifier_calls": {
            "text": "verifier calls",
            "status": box_status(later_kt, later_k0, "verifier_calls"),
            "later_kt": later_kt["verifier_calls"],
            "later_k0": later_k0["verifier_calls"],
            "library": library["verifier_calls"],
            "lifetime_kt": lifetime_kt["verifier_calls"],
            "lifetime_k0": lifetime_k0["verifier_calls"],
            "unit": "normal_form polynomial-identity checks on unique 4-primitive programs",
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
        terminal,
        admitted,
        later_kt,
        later_k0,
        library,
        lifetime_kt,
        lifetime_k0,
        horizon_n,
        saving_per_task,
        scan_token_operations,
        confirmation_compute,
        LATER_N,
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
        "serving": "greedy-leftmost-rewrite-in-4-primitive-grammar",
        "acquisition": "search-aware-scan-plus-single-confirmation",
        "grammar_tokens": list(M.PRIMITIVES),
        "grammar_width": 4,
        "predecessor_v1_terminal": "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER",
        "predecessor_v1_mechanism": "MACRO as 5th BFS token expanded grammar width so later compute rose",
        "predecessor_v2_terminal": "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS",
        "predecessor_v2_mechanism": (
            "4-primitive rewrite made later compute fall (59929→36289) but the 8-candidate "
            "validation tournament left library capital unrecouped"
        ),
        "parent": "ordinary persistent rewrite/library operator inside the 4-primitive grammar (DreamCoder/Stitch/#192 replacement, no 5th token, SEARCH_AWARE scan acquisition)",
        "parent_sufficient": parent_tied and admitted is not None,
        "mechanism_comment": comment,
        "claim_ceiling": (
            "Bounded H1 later-task and lifetime-compute comparison on one exact polynomial "
            "microscope after a SEARCH_AWARE-selected 4-primitive rewrite, charged once and "
            f"served across {LATER_N} related later identities. Ordinary parent parity and "
            "restart/revocation are required. Library capital stays on the ledger. Not "
            "programme-wide H1, not P6 residual, not language meta-learning, not an OCM "
            "architecture uniqueness claim, not a salt retune of H1 v1 or v2."
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
            "search_aware_selected": list(selected) if selected else [],
            "admitted": list(admitted) if admitted else [],
            "gate_refused_frequency": bool(
                frequency_selected is not None and admitted is not None and admitted != frequency_selected
            ),
            "tournament_run": False,
            "val_indexes_built": val_indexes_built,
            "scan_token_operations": scan_token_operations,
            "scan_enumeration_attempts": 0,
            "search_aware_scores": {str(fragment): scores for fragment, scores in search_aware_scores.items()},
            "confirmation": {
                "primitive_val_compute": primitive_val_compute,
                "selected_val_compute": selected_val_compute,
                "beats_primitive": beats_primitive,
            },
            "cost": library,
            "training_compute": train_compute,
            "confirmation_compute": confirmation_compute,
            "tournament_compute": None,
        },
        "later": {
            "k0": later_k0,
            "kt": later_kt,
            "ordinary": later_ordinary,
            "revoked": later_revoked,
            "strict_compute_saving": later_strict_compute,
            "strict_new_information_saving": later_strict_new_information,
            "strict_verifier_saving": later_strict_verifier,
            "causal_rewrite_wins": causal_wins,
            "ordinary_equals_ocm": ordinary_equal_ocm,
            "revoked_equals_primitive": revoked_equal_primitive,
            "per_task": per_task,
        },
        "lifetime": {
            "kt": lifetime_kt,
            "k0": lifetime_k0,
            "library_pays_back_compute": library_pays_back,
            "break_even_n": horizon_n,
            "saving_per_later_identity": saving_per_task,
            "observed_later_n": LATER_N,
            "note": (
                "K_0 lifetime is later-task C_acquire only (reset). K_t lifetime is library capital "
                "(training search + SEARCH_AWARE token scan, not added to compute, + single "
                "confirmation search + persist bytes + demonstrations) plus later-task C_acquire "
                f"across {LATER_N} related identities. Acquisition is charged once. The 8-candidate "
                "tournament is not run and is not silently omitted from a ledger that still includes it."
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
            "SALT_RETUNE_OF_H1_V1_5ARY_MACRO",
            "SALT_RETUNE_OF_H1_V2_TOURNAMENT",
            "DROPPED_ACQUISITION_COST_FROM_LEDGER",
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
                "search_aware_selected": result["library"]["search_aware_selected"],
                "grammar_width": result["grammar_width"],
                "serving": result["serving"],
                "acquisition": result["acquisition"],
                "tournament_run": result["library"]["tournament_run"],
                "later_n": result["partition"]["later_n"],
                "later_k0_compute": result["later"]["k0"]["compute"],
                "later_kt_compute": result["later"]["kt"]["compute"],
                "library_compute": result["library"]["cost"]["compute"],
                "training_compute": result["library"]["training_compute"],
                "confirmation_compute": result["library"]["confirmation_compute"],
                "scan_token_operations": result["library"]["scan_token_operations"],
                "lifetime_kt_compute": result["lifetime"]["kt"]["compute"],
                "lifetime_k0_compute": result["lifetime"]["k0"]["compute"],
                "library_pays_back_compute": result["lifetime"]["library_pays_back_compute"],
                "break_even_n": result["lifetime"]["break_even_n"],
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
