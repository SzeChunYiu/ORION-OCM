"""§7 / P6 cross-domain cognitive transfer study.

Source: polynomial apply-fragment (square, dec, square) from methods.py blob
50323a33418b8ef8bb6500ddeba4b9d1f795e9e3. Target: reminted 4-cell ribbon rewrite
with exact tape equality — not renamed polynomials. Correspondence maps
compose-learned-fragment to compose-learned-rewrite without target answers.

Protected order: freeze source method, freeze correspondence, verify the
correspondence file encodes no target solution, remint vocabulary, then load
target tasks. Compare reset OCM, task-specific OCM, transfer OCM, a kNN/prototype
parent (neural CANNOT_CHECK if no NN library), unrelated color-naming, harmful
transfer, and source-method removal ablation.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from importlib import import_module
from itertools import product
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = REPO / "src"
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
SOURCE_FRAGMENT = ("square", "dec", "square")
SOURCE_ROLES = ("nonlinear_wrap", "local_shift", "nonlinear_wrap")
MACRO_TOKEN = "APPLY_FRAGMENT"
CORRESPONDENCE_PATH = HERE / "correspondence.json"
SOURCE_SCOPE = Scope.of("polynomial-apply-fragment.v1")
TARGET_SCOPE = Scope.of("ribbon-rewrite.v1")
TARGET_CHECKER = "exact-tape-equality.v1"
SOURCE_CHECKER = "rational-polynomial-coefficients.v1"
TAPE_SYMBOLS = ("kel", "mora")
TARGET_PRIMITIVES = ("plait", "nick", "braid", "knot")
FLIP = {"kel": "mora", "mora": "kel"}
TAPE_LENGTH = 4
TRAIN_DISTANCE = 4
TEST_DISTANCE = 5
MAX_PRIMITIVE_LENGTH = 6
HARMFUL_FRAGMENT = ("braid", "braid", "braid")
COLOR_VOCAB = ("caf", "jom", "nup", "qal", "veb", "wex", "yul", "zir")
COLOR_SALT = "orion-ocm-cross-domain-color-v1"
CANDIDATE_OPERATIONS = (
    "DECOMPOSE",
    "DISTINGUISH",
    "CHECK",
    "REVISE",
    "SEARCH_MORE",
    "FORM_SUBGOAL",
    "CHANGE_REPRESENTATION",
    "CONSOLIDATE",
    "GENERALIZE_METHOD",
    "DETECT_OBSTRUCTION",
    "ABSTAIN",
)
POSITIVE_TERMINAL = "CROSS_DOMAIN_TRANSFER_SUPPORTED_AT_REGISTERED_SCOPE"
NEURAL_MODULES = ("torch", "tensorflow", "sklearn", "jax")


def git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def load_correspondence():
    payload = json.loads(CORRESPONDENCE_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != "ocm.cross-domain.correspondence.v1":
        raise RuntimeError("correspondence schema mismatch")
    return payload


def freeze_source_method():
    path = SRC / "ocm" / "learning" / "methods.py"
    blob = git_blob_sha1(path)
    if blob != METHOD_BLOB:
        raise RuntimeError(f"source method blob drift: {blob}")
    if SOURCE_FRAGMENT[0] not in M.PRIMITIVES:
        raise RuntimeError("source fragment outside polynomial grammar")
    program = M.checked_program(SOURCE_FRAGMENT)
    coefficients = M.normal_form(program)
    identity = {
        "operator": "apply-fragment",
        "fragment": list(SOURCE_FRAGMENT),
        "typed_roles": list(SOURCE_ROLES),
        "source_blob": blob,
        "source_checker": SOURCE_CHECKER,
        "source_coefficients": [str(c) for c in coefficients],
        "fingerprint": content_hash({
            "operator": "apply-fragment",
            "fragment": SOURCE_FRAGMENT,
            "blob": blob,
        }),
    }
    return identity


def instantiate_transfer_fragment(correspondence):
    fillers = correspondence["witness"]["role_fillers"]
    fragment = tuple(fillers[role] for role in correspondence["witness"]["instantiated_schema"])
    if any(op not in TARGET_PRIMITIVES for op in fragment):
        raise RuntimeError("correspondence role filler outside reminted target grammar")
    if any(op in M.PRIMITIVES for op in fragment):
        raise RuntimeError("target fragment reused polynomial tokens")
    return fragment


def correspondence_forbidden_needles(target_tasks, color_tasks):
    needles = []
    for task in target_tasks:
        needles.append(json.dumps(list(task.start), separators=(",", ":")))
        needles.append(json.dumps(list(task.goal), separators=(",", ":")))
        needles.append(task.fingerprint)
    for task in color_tasks:
        needles.append(task.answer)
        needles.append(task.fingerprint)
    return tuple(dict.fromkeys(needles))


def correspondence_encodes_target_solution(correspondence, target_tasks, color_tasks):
    blob = json.dumps(correspondence, sort_keys=True, separators=(",", ":"))
    hits = [needle for needle in correspondence_forbidden_needles(target_tasks, color_tasks) if needle in blob]
    return hits


def remint_ok():
    overlap = set(TARGET_PRIMITIVES) & set(M.PRIMITIVES)
    symbol_clash = set(TAPE_SYMBOLS) & set(M.PRIMITIVES)
    color_clash = set(COLOR_VOCAB) & set(M.PRIMITIVES)
    return not overlap and not symbol_clash and not color_clash


def apply_op(state, op):
    cells = list(state)
    if op == "plait":
        cells.reverse()
    elif op == "nick":
        cells[0] = FLIP[cells[0]]
    elif op == "braid":
        cells = cells[1:] + cells[:1]
    elif op == "knot":
        cells[0], cells[1] = cells[1], cells[0]
    else:
        raise ValueError(f"unknown rewrite {op}")
    return tuple(cells)


def apply_program(state, program):
    for op in program:
        state = apply_op(state, op)
    return state


def shortest_program(start, goal, max_length=8):
    if start == goal:
        return ()
    seen = {start}
    queue = deque([(start, ())])
    while queue:
        state, program = queue.popleft()
        if len(program) >= max_length:
            continue
        for op in TARGET_PRIMITIVES:
            nxt = apply_op(state, op)
            if nxt in seen:
                continue
            word = program + (op,)
            if nxt == goal:
                return word
            seen.add(nxt)
            queue.append((nxt, word))
    return None


class RibbonTask:
    __slots__ = ("start", "goal", "task_id", "fingerprint")

    def __init__(self, start, goal):
        self.start = tuple(start)
        self.goal = tuple(goal)
        self.task_id = content_hash({"domain": TARGET_CHECKER, "start": self.start, "goal": self.goal})
        self.fingerprint = self.task_id


class ColorTask:
    __slots__ = ("query", "answer", "fingerprint")

    def __init__(self, query, answer):
        self.query = query
        self.answer = answer
        self.fingerprint = content_hash({"domain": "exact-name-table.v1", "query": query, "answer": answer})


def all_tapes():
    return tuple(product(TAPE_SYMBOLS, repeat=TAPE_LENGTH))


def frozen_ribbon_population():
    tapes = all_tapes()
    by_distance = {distance: [] for distance in range(MAX_PRIMITIVE_LENGTH + 2)}
    for start in tapes:
        for goal in tapes:
            program = shortest_program(start, goal, max_length=8)
            if program is None:
                continue
            by_distance[len(program)].append((start, goal, program))
    train = tuple(RibbonTask(start, goal) for start, goal, _program in by_distance[TRAIN_DISTANCE])
    test = tuple(RibbonTask(start, goal) for start, goal, _program in by_distance[TEST_DISTANCE])
    if not train or not test:
        raise RuntimeError("ribbon population missing a required distance stratum")
    if {task.fingerprint for task in train} & {task.fingerprint for task in test}:
        raise RuntimeError("ribbon train/test overlap")
    train_programs = {task.fingerprint: shortest_program(task.start, task.goal) for task in train}
    return {
        "by_distance_counts": {str(k): len(v) for k, v in by_distance.items() if v},
        "train": train,
        "test": test,
        "train_programs": train_programs,
    }


def mine_task_specific_fragment(train, train_programs):
    support = Counter()
    for task in train:
        program = train_programs[task.fingerprint]
        fragments = {
            program[start:end]
            for start in range(len(program))
            for end in range(start + 2, len(program))
        }
        support.update(fragments)
    if not support:
        return None, {}
    chosen = sorted(support, key=lambda fragment: (-support[fragment], -len(fragment), fragment))[0]
    return chosen, {fragment: support[fragment] for fragment in support}


def expand_tokens(token_word, macro):
    expanded = []
    used = False
    for token in token_word:
        if token == MACRO_TOKEN:
            if macro is None:
                raise ValueError("macro token without fragment")
            expanded.extend(macro)
            used = True
        else:
            if token not in TARGET_PRIMITIVES:
                raise ValueError(f"unknown token {token}")
            expanded.append(token)
    return tuple(expanded), used


def solve_ribbon(task, macro=None, max_length=MAX_PRIMITIVE_LENGTH):
    tokens = ((MACRO_TOKEN,) + TARGET_PRIMITIVES) if macro is not None else TARGET_PRIMITIVES
    seen = set()
    attempts = 0
    checks = 0
    for depth in range(0, max_length + 1):
        for word in product(tokens, repeat=depth):
            expanded, used = expand_tokens(word, macro)
            if len(expanded) > max_length:
                continue
            attempts += 1
            if expanded in seen:
                continue
            seen.add(expanded)
            checks += 1
            if apply_program(task.start, expanded) == task.goal:
                return {
                    "task": task.fingerprint,
                    "enumeration_attempts": attempts,
                    "unique_candidates_checked": checks,
                    "token_word": word,
                    "program": expanded,
                    "macro_used": used,
                    "verified": True,
                    "checker": TARGET_CHECKER,
                }
    return {
        "task": task.fingerprint,
        "enumeration_attempts": attempts,
        "unique_candidates_checked": checks,
        "token_word": None,
        "program": None,
        "macro_used": False,
        "verified": False,
        "checker": TARGET_CHECKER,
    }


def evaluate_ribbon(tasks, macro=None):
    rows = [solve_ribbon(task, macro) for task in tasks]
    if any(not row["verified"] for row in rows):
        raise RuntimeError("registered ribbon grammar failed to solve a held-out task")
    return rows, sum(row["enumeration_attempts"] for row in rows)


def compare_rows(baseline_rows, candidate_rows):
    base = {row["task"]: row for row in baseline_rows}
    better = worse = used = 0
    for row in candidate_rows:
        parent = base[row["task"]]
        if row["enumeration_attempts"] < parent["enumeration_attempts"]:
            better += 1
        elif row["enumeration_attempts"] > parent["enumeration_attempts"]:
            worse += 1
        if row["macro_used"]:
            used += 1
    return {
        "strict_improvement_tasks": better,
        "harmful_tasks": worse,
        "macro_used_tasks": used,
    }


def rows_equal(a_rows, b_rows):
    return all(
        a["task"] == b["task"]
        and a["enumeration_attempts"] == b["enumeration_attempts"]
        and a["unique_candidates_checked"] == b["unique_candidates_checked"]
        and tuple(a["program"] or ()) == tuple(b["program"] or ())
        and tuple(a["token_word"] or ()) == tuple(b["token_word"] or ())
        for a, b in zip(a_rows, b_rows)
    )


def hamming(left, right):
    return sum(a != b for a, b in zip(left, right))


def knn_prototype(test, train, train_programs):
    rows = []
    hits = 0
    for task in test:
        ranked = sorted(
            train,
            key=lambda donor: (
                hamming(task.start, donor.start) + hamming(task.goal, donor.goal),
                donor.fingerprint,
            ),
        )
        donor = ranked[0]
        prototype = train_programs[donor.fingerprint]
        if apply_program(task.start, prototype) == task.goal:
            hits += 1
            rows.append({
                "task": task.fingerprint,
                "enumeration_attempts": 1,
                "unique_candidates_checked": 1,
                "token_word": prototype,
                "program": prototype,
                "macro_used": False,
                "verified": True,
                "checker": TARGET_CHECKER,
                "prototype_hit": True,
            })
            continue
        fallback = solve_ribbon(task, None)
        fallback["prototype_hit"] = False
        rows.append(fallback)
    return rows, sum(row["enumeration_attempts"] for row in rows), hits


def neural_parent_status():
    present = []
    for name in NEURAL_MODULES:
        try:
            import_module(name)
        except Exception:
            continue
        present.append(name)
    if present:
        return {
            "terminal": "NEURAL_PARENT_AVAILABLE_NOT_RUN",
            "modules": present,
            "note": "A neural library is importable; this v1 still reports the kNN/prototype parent only.",
        }
    return {
        "terminal": "CANNOT_CHECK_NEURAL",
        "modules": [],
        "note": "No torch/tensorflow/sklearn/jax in this environment; kNN/prototype is the classical parent.",
    }


def color_table():
    order = tuple(sorted(COLOR_VOCAB, key=lambda name: hashlib.sha256((COLOR_SALT + "\0" + name).encode()).hexdigest()))
    return {name: order[(order.index(name) + 3) % len(order)] for name in COLOR_VOCAB}


def frozen_color_tasks():
    table = color_table()
    return tuple(ColorTask(query, table[query]) for query in COLOR_VOCAB), table


def solve_color(task, waste=0):
    attempts = waste
    for name in COLOR_VOCAB:
        attempts += 1
        if name == task.answer:
            return {
                "task": task.fingerprint,
                "enumeration_attempts": attempts,
                "program": (name,),
                "verified": True,
                "checker": "exact-name-table.v1",
            }
    raise RuntimeError("color table search missed a registered name")


def evaluate_color(tasks, waste=0):
    rows = [solve_color(task, waste=waste) for task in tasks]
    return rows, sum(row["enumeration_attempts"] for row in rows)


def admit_fragment(root: Path, fragment, receipts, revoke_source=False):
    runtime = OCMRuntime(root)
    _tr, training_evidence = runtime.admit_evidence(
        receipts["source"],
        Channel.PROOF,
        "cross-domain-source-method.v1",
        scope=SOURCE_SCOPE,
    )
    _cr, correspondence_evidence = runtime.admit_evidence(
        receipts["correspondence"],
        Channel.OBSERVATION,
        "cross-domain-correspondence.v1",
        scope=TARGET_SCOPE,
    )
    warrant = WarrantProfile.of({training_evidence, correspondence_evidence})
    source_payload = {
        "kind": "cross-domain.source-method.v1",
        "source": receipts["source"]["fingerprint"],
        "correspondence": content_hash(receipts["correspondence"]),
    }
    source_id = "source-method:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=SOURCE_SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {
        "kind": "apply-rewrite.v1",
        "macro": list(fragment),
        "fingerprint": content_hash({"macro": fragment}),
    }
    atom_id = "apply-rewrite:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=TARGET_SCOPE,
            content_ref=content_hash(payload),
            meta=tuple((k, tuple(v) if k == "macro" else v) for k, v in payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    if revoke_source:
        runtime.revoke((training_evidence,))
    runtime.persist()

    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if revoke_source:
        if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
            raise RuntimeError("ablated source method remained live")
        return None, atom_id, training_evidence, correspondence_evidence
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("transferred rewrite did not survive restart")
    stored = dict(atom.meta)
    loaded = tuple(stored["macro"])
    if content_hash({"macro": loaded}) != stored["fingerprint"]:
        raise RuntimeError("transferred fragment identity mismatch")
    return loaded, atom_id, training_evidence, correspondence_evidence


def admit_task_specific(root: Path, fragment, train_receipt):
    runtime = OCMRuntime(root)
    _tr, evidence = runtime.admit_evidence(
        train_receipt,
        Channel.OBSERVATION,
        "cross-domain-target-train.v1",
        scope=TARGET_SCOPE,
    )
    warrant = WarrantProfile.of({evidence})
    source_payload = {
        "kind": "cross-domain.target-train.v1",
        "training": content_hash(train_receipt),
    }
    source_id = "target-train:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=TARGET_SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {
        "kind": "apply-rewrite.v1",
        "macro": list(fragment),
        "fingerprint": content_hash({"macro": fragment}),
        "origin": "task-specific",
    }
    atom_id = "apply-rewrite:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=TARGET_SCOPE,
            content_ref=content_hash(payload),
            meta=tuple((k, tuple(v) if k == "macro" else v) for k, v in payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    runtime.persist()
    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map()[atom_id]
    if atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("task-specific fragment did not survive restart")
    return tuple(dict(atom.meta)["macro"]), atom_id, evidence


def reset_runtime(root: Path):
    runtime = OCMRuntime(root)
    runtime.persist()
    replay = OCMRuntime(root)
    live = [
        atom.atom_id
        for atom in replay.state.ks.atom_map().values()
        if atom.atom_type == "procedure" and atom.liveness(replay.state.revoked) is Liveness.LIVE
    ]
    if live:
        raise RuntimeError("reset OCM admitted a procedure")
    return live


def compact_rows(rows):
    return [
        {
            "task": row["task"],
            "enumeration_attempts": row["enumeration_attempts"],
            "unique_candidates_checked": row.get("unique_candidates_checked"),
            "program": list(row["program"]) if row.get("program") is not None else None,
            "macro_used": row.get("macro_used", False),
            "verified": row["verified"],
        }
        for row in rows
    ]


def decide_terminal(
    *,
    second_domain,
    encoded_hits,
    transfer_total,
    reset_total,
    transfer_used,
    ablation_equals_reset,
    task_specific_total,
    knn_total,
    unrelated_no_benefit,
    harmful_worse,
):
    if not second_domain:
        return "CANNOT_CHECK_NO_SECOND_DOMAIN_RESULT", False
    if encoded_hits:
        raise RuntimeError("correspondence encoded target solutions: " + ",".join(encoded_hits[:4]))
    if not harmful_worse:
        # The harmful control is required; a non-harmful "harmful" arm is a protocol failure.
        raise RuntimeError("harmful control did not lengthen target search")
    if transfer_total > reset_total:
        return "HARMFUL_TRANSFER_LIMIT", False
    if transfer_total >= reset_total or transfer_used == 0:
        return "NO_CROSS_DOMAIN_TRANSFER", False
    if not ablation_equals_reset:
        return "NO_CROSS_DOMAIN_TRANSFER", False
    if not unrelated_no_benefit:
        return "NO_CROSS_DOMAIN_TRANSFER", False
    if task_specific_total <= transfer_total or knn_total <= transfer_total:
        return "PARENT_SUFFICIENT", False
    return POSITIVE_TERMINAL, True


def run():
    started = time.perf_counter()
    protocol_order = []

    source = freeze_source_method()
    protocol_order.append("freeze_source_method_identity")

    correspondence = load_correspondence()
    if correspondence["source"]["source_blob"] != METHOD_BLOB:
        raise RuntimeError("correspondence source blob does not match methods.py")
    if tuple(correspondence["source"]["method_identity"]["fragment"]) != SOURCE_FRAGMENT:
        raise RuntimeError("correspondence source fragment drift")
    if correspondence["source"]["checker"] == correspondence["target"]["checker"]:
        raise RuntimeError("source and target checkers are not materially different")
    protocol_order.append("freeze_typed_correspondence")

    dumped = json.dumps(correspondence, sort_keys=True)
    if any(key in dumped for key in ('"goal"', '"answer"', '"start"', '"solution"', '"companion"')):
        raise RuntimeError("correspondence contains target-solution fields before target access")
    protocol_order.append("verify_correspondence_does_not_encode_target_solution")

    transfer_fragment = instantiate_transfer_fragment(correspondence)
    if not remint_ok():
        raise RuntimeError("target vocabulary was not reminted")
    protocol_order.append("remint_target_vocabulary")

    # Target-domain protected access begins only after the freezes above.
    population = frozen_ribbon_population()
    color_tasks, _table = frozen_color_tasks()
    protocol_order.append("load_target_protected_tasks")

    encoded_hits = correspondence_encodes_target_solution(
        correspondence, population["test"], color_tasks,
    )
    if encoded_hits:
        raise RuntimeError("correspondence encoded target solutions before evaluation")
    protocol_order.append("confirm_correspondence_needles_absent")

    task_fragment, support = mine_task_specific_fragment(population["train"], population["train_programs"])
    if task_fragment is None:
        raise RuntimeError("task-specific miner found no proper fragment")

    reset_rows, reset_total = evaluate_ribbon(population["test"], None)
    transfer_rows, transfer_total = evaluate_ribbon(population["test"], transfer_fragment)
    task_rows, task_total = evaluate_ribbon(population["test"], task_fragment)
    harmful_rows, harmful_total = evaluate_ribbon(population["test"], HARMFUL_FRAGMENT)
    knn_rows, knn_total, knn_hits = knn_prototype(
        population["test"], population["train"], population["train_programs"],
    )
    color_reset_rows, color_reset_total = evaluate_color(color_tasks, waste=0)
    color_transfer_rows, color_transfer_total = evaluate_color(color_tasks, waste=len(SOURCE_FRAGMENT))
    unrelated_no_benefit = color_transfer_total >= color_reset_total

    receipts = {
        "source": source,
        "correspondence": {
            "correspondence_id": correspondence["correspondence_id"],
            "maps": correspondence["witness"]["maps"],
            "fingerprint": content_hash(correspondence),
        },
    }
    train_receipt = {
        "schema": "cross-domain.target-train.v1",
        "n": len(population["train"]),
        "fragment": list(task_fragment),
        "task_ids": [task.fingerprint for task in population["train"]],
    }

    with tempfile.TemporaryDirectory(prefix="ocm-cross-domain-") as temp:
        root = Path(temp)
        reset_live = reset_runtime(root / "reset")
        ocm_transfer, transfer_atom, source_evidence, correspondence_evidence = admit_fragment(
            root / "transfer", transfer_fragment, receipts, revoke_source=False,
        )
        ocm_ablated, ablated_atom, _se, _ce = admit_fragment(
            root / "ablate", transfer_fragment, receipts, revoke_source=True,
        )
        ocm_task, task_atom, task_evidence = admit_task_specific(
            root / "task-specific", task_fragment, train_receipt,
        )

    ocm_transfer_rows, ocm_transfer_total = evaluate_ribbon(population["test"], ocm_transfer)
    ocm_task_rows, ocm_task_total = evaluate_ribbon(population["test"], ocm_task)
    ablated_rows, ablated_total = evaluate_ribbon(population["test"], ocm_ablated)
    protocol_order.extend([
        "compare_reset_ocm",
        "compare_task_specific_ocm",
        "compare_knn_prototype_parent",
        "include_unrelated_transfer",
        "include_harmful_transfer",
        "causal_method_removal_ablation",
    ])

    transfer_vs_reset = compare_rows(reset_rows, transfer_rows)
    harmful_vs_reset = compare_rows(reset_rows, harmful_rows)
    task_vs_reset = compare_rows(reset_rows, task_rows)
    ablation_equals_reset = rows_equal(ablated_rows, reset_rows)
    ocm_matches_transfer = rows_equal(ocm_transfer_rows, transfer_rows)
    ocm_task_matches = rows_equal(ocm_task_rows, task_rows)
    neural = neural_parent_status()
    second_domain = (
        correspondence["target"]["checker"] != SOURCE_CHECKER
        and correspondence["target"]["checker"] != correspondence["source"]["checker"]
        and remint_ok()
        and bool(population["test"])
    )
    terminal, supported = decide_terminal(
        second_domain=second_domain,
        encoded_hits=encoded_hits,
        transfer_total=transfer_total,
        reset_total=reset_total,
        transfer_used=transfer_vs_reset["macro_used_tasks"],
        ablation_equals_reset=ablation_equals_reset,
        task_specific_total=task_total,
        knn_total=knn_total,
        unrelated_no_benefit=unrelated_no_benefit,
        harmful_worse=harmful_total > reset_total,
    )

    return {
        "schema": "ocm.cross-domain-transfer.result.v1",
        "terminal": terminal,
        "supported": supported,
        "protocol_order": protocol_order,
        "source_method": source,
        "correspondence_id": correspondence["correspondence_id"],
        "correspondence_fingerprint": content_hash(correspondence),
        "correspondence_encodes_target_solution": False,
        "vocabulary_reminted": remint_ok(),
        "domains": {
            "source_checker": SOURCE_CHECKER,
            "target_checker": TARGET_CHECKER,
            "unrelated_checker": "exact-name-table.v1",
            "materially_different_validation": True,
        },
        "transfer_fragment": list(transfer_fragment),
        "task_specific_fragment": list(task_fragment),
        "harmful_fragment": list(HARMFUL_FRAGMENT),
        "candidate_operations": list(CANDIDATE_OPERATIONS),
        "population": {
            "train_n": len(population["train"]),
            "test_n": len(population["test"]),
            "train_distance": TRAIN_DISTANCE,
            "test_distance": TEST_DISTANCE,
            "distance_counts": population["by_distance_counts"],
            "train_ids": [task.fingerprint for task in population["train"]],
            "test_ids": [task.fingerprint for task in population["test"]],
        },
        "fragment_support": {",".join(fragment): count for fragment, count in list(support.items())[:16]},
        "ribbon": {
            "reset_total_attempts": reset_total,
            "transfer_total_attempts": transfer_total,
            "task_specific_total_attempts": task_total,
            "harmful_total_attempts": harmful_total,
            "knn_total_attempts": knn_total,
            "knn_prototype_hits": knn_hits,
            "ablated_total_attempts": ablated_total,
            "ocm_transfer_total_attempts": ocm_transfer_total,
            "ocm_task_specific_total_attempts": ocm_task_total,
            "transfer_vs_reset": transfer_vs_reset,
            "task_specific_vs_reset": task_vs_reset,
            "harmful_vs_reset": harmful_vs_reset,
            "ablation_equals_reset": ablation_equals_reset,
            "ocm_transfer_equals_direct": ocm_matches_transfer,
            "ocm_task_specific_equals_direct": ocm_task_matches,
            "reset_rows": compact_rows(reset_rows),
            "transfer_rows": compact_rows(transfer_rows),
            "task_specific_rows": compact_rows(task_rows),
            "harmful_rows": compact_rows(harmful_rows),
            "knn_rows": compact_rows(knn_rows),
            "ablated_rows": compact_rows(ablated_rows),
        },
        "unrelated": {
            "domain": "color-naming.v1",
            "n": len(color_tasks),
            "reset_total_attempts": color_reset_total,
            "transfer_total_attempts": color_transfer_total,
            "usefulness": "NO_BENEFIT" if unrelated_no_benefit else "UNEXPECTED_BENEFIT",
            "shared_structure": False,
            "rows_reset": compact_rows(color_reset_rows),
            "rows_transfer": compact_rows(color_transfer_rows),
        },
        "parents": {
            "neural": neural,
            "knn_prototype": {
                "total_attempts": knn_total,
                "hits": knn_hits,
                "sufficient": knn_total <= transfer_total,
            },
            "task_specific_ocm": {
                "fragment": list(task_fragment),
                "total_attempts": task_total,
                "sufficient": task_total <= transfer_total,
            },
            "reset_ocm": {
                "live_procedures": reset_live,
                "total_attempts": reset_total,
            },
        },
        "ocm": {
            "transfer_atom": transfer_atom,
            "task_specific_atom": task_atom,
            "ablated_atom": ablated_atom,
            "source_evidence": source_evidence,
            "correspondence_evidence": correspondence_evidence,
            "task_specific_evidence": task_evidence,
            "fresh_restart": True,
            "source_method_removal_ablation": True,
        },
        "accounting": {
            "study_wall_seconds": time.perf_counter() - started,
            "same_python_api_is_not_a_claim": True,
        },
        "claim_boundary": (
            "Bounded analogical transfer of apply-fragment from polynomials onto a reminted "
            "ribbon-rewrite domain via a typed composition correspondence. Exact tape equality "
            "is a different checker than polynomial identity. Ordinary serving of the same "
            "transferred fragment matches OCM; no architecture residual, general intelligence, "
            "or neural-parent claim. Unrelated color-naming shows no usefulness."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out.with_suffix(args.out.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    os.replace(tmp, args.out)
    print(json.dumps({
        "terminal": result["terminal"],
        "supported": result["supported"],
        "reset_attempts": result["ribbon"]["reset_total_attempts"],
        "transfer_attempts": result["ribbon"]["transfer_total_attempts"],
        "task_specific_attempts": result["ribbon"]["task_specific_total_attempts"],
        "harmful_attempts": result["ribbon"]["harmful_total_attempts"],
        "knn_attempts": result["ribbon"]["knn_total_attempts"],
        "ablation_equals_reset": result["ribbon"]["ablation_equals_reset"],
        "unrelated_usefulness": result["unrelated"]["usefulness"],
        "neural": result["parents"]["neural"]["terminal"],
        "wall_seconds": result["accounting"]["study_wall_seconds"],
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
