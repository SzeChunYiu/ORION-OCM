"""Issue #165 H1 remaining examples/state: demonstration-charging parent.

Predecessors charged training solutions as a count of 16 with later additional
examples 0=0. Demonstration bytes were free residue of mining. This capsule
makes examples first-class capital (count, bytes, later-task inequality) and
admits them on Channel.DEMONSTRATION.

v3 later-task search is cited, not rerun. The G2 9e6 tournament is cited, not
rerun. v3 salts are frozen inputs. Production methods.py is imported, not
copied. v3 experiment is loaded with spec_from_file_location, not copied.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
V3_DIR = REPO / "research" / "h1-amortized-lifetime-v3"
V2_DIR = REPO / "research" / "h1-amortized-rewrite-v2"
V1_DIR = REPO / "research" / "h1-amortized-acquisition-v1"
H5_DIR = REPO / "research" / "h5-lifetime-economics-v1"
G2_DIR = REPO / "research" / "g2-acquisition-economics-v1"
sys.path.insert(0, str(SRC))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V3 = _load_module("h1_amortized_lifetime_v3", V3_DIR / "experiment.py")

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.learning import methods as M
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

SCHEMA = "ocm.h1.examples-charge.v1"
METHOD_BLOB = "50323a33418b8ef8bb6500ddeba4b9d1f795e9e3"
V3_RESULT = V3_DIR / "RESULT.json"
V3_RESULT_SHA256 = "dd92c8dce7bec2340ee8832b934cb0cd9bfbdbf3affa6c0f03e1e17f40ce53e1"
G2_RESULT = G2_DIR / "G2_ACQUISITION_ECONOMICS_V1.json"
G2_RESULT_SHA256 = "049760194d24078d05188e77d45a69c60012ef9726d75a274aef87887f018597"
SCOPE = Scope.of("polynomial-h1-examples-charge.v1")

ALLOWED_TERMINALS = (
    "EXAMPLES_ARE_LIBRARY_CAPITAL",
    "H1_EXAMPLES_EARNED_AT_SCOPE",
    "CANNOT_CHECK_PREDECESSOR_DRIFT",
    "CANNOT_CHECK_PARTITION_RECONSTRUCTION",
    "CANNOT_CHECK_REVOCATION_ABLATION",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tree_bytes(root: Path) -> int:
    if not root.exists():
        return 0
    if root.is_file():
        return root.stat().st_size
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def canonical_dumps(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def demonstration_record(task, program) -> dict[str, Any]:
    return {
        "fingerprint": task.fingerprint,
        "program": list(program),
        "coefficients": [str(c) for c in task.coefficients],
        "length": len(program),
    }


def corpus_payload(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "kind": "demonstration.corpus.v1",
        "count": len(records),
        "records": records,
        "fingerprint": content_hash({"records": records}),
    }


def ordinary_persist_corpus(path: Path, payload: dict[str, Any]) -> int:
    temp = path.with_suffix(".tmp")
    raw = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    with temp.open("x", encoding="utf-8") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return path.stat().st_size


def ordinary_load_corpus(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload["records"]
    if content_hash({"records": records}) != payload["fingerprint"]:
        raise RuntimeError("ordinary demonstration corpus identity mismatch")
    return payload


def lookup_hits(later_rows, index: dict[str, dict[str, Any]]) -> list[str]:
    hits = []
    for task, _program in later_rows:
        if task.fingerprint in index:
            hits.append(task.fingerprint)
    return hits


def encoding_bytes(word) -> int:
    return len(canonical_dumps(list(word)))


def admit_demonstrations(root: Path, records: list[dict[str, Any]], revoke: bool = False):
    runtime = OCMRuntime(root)
    evidence_ids = []
    for index, record in enumerate(records):
        _admission, eid = runtime.admit_evidence(
            record,
            Channel.DEMONSTRATION,
            f"h1-examples-demo.{index}.v1",
            scope=SCOPE,
        )
        evidence_ids.append(eid)
    payload = {
        "kind": "demonstration.library.v1",
        "count": len(records),
        "fingerprints": [record["fingerprint"] for record in records],
        "fingerprint": content_hash({"records": records}),
        "channel": Channel.DEMONSTRATION.value,
    }
    atom_id = "demonstration-library:" + content_hash(payload)
    warrant = WarrantProfile.of(set(evidence_ids))
    source_payload = {"kind": "h1.examples.support.v1", "corpus": payload["fingerprint"]}
    source_id = "h1-examples-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "observation",
            warrant,
            scope=SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
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
        runtime.revoke(tuple(evidence_ids))
    runtime.persist()
    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    live_demo_records = [
        rec
        for rec in replay.state.evidence.records.values()
        if rec.channel == Channel.DEMONSTRATION
        and rec.evidence_id not in replay.state.revoked
    ]
    if revoke:
        if atom is not None and atom.liveness(replay.state.revoked) is Liveness.LIVE:
            raise RuntimeError("revoked demonstration library remained live")
        if live_demo_records:
            raise RuntimeError("revoked demonstration evidence remained live")
        return None, atom_id, evidence_ids, tree_bytes(root), 0
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("demonstration library did not survive restart")
    stored = dict(atom.meta)
    if int(stored["count"]) != len(records):
        raise RuntimeError("persisted demonstration count drifted")
    return list(stored["fingerprints"]), atom_id, evidence_ids, tree_bytes(root), len(live_demo_records)


def load_v3_capital() -> dict[str, Any]:
    digest = sha256_file(V3_RESULT)
    if digest != V3_RESULT_SHA256:
        raise RuntimeError(f"H1 v3 RESULT.json drifted: {digest}")
    doc = load_json(V3_RESULT)
    expected = {
        "terminal": "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE",
        "later_k0": 183463,
        "later_kt": 144623,
        "library_compute": 27919,
        "examples": 16,
        "state_written": 14426,
        "admitted": ["double", "square"],
        "later_n": 48,
        "train_n": 16,
        "train_salt": "orion-ocm-h1-lifetime-train-v3",
        "later_salt": "orion-ocm-h1-lifetime-later-v3",
    }
    observed = {
        "terminal": doc["terminal"],
        "later_k0": int(doc["later"]["k0"]["compute"]),
        "later_kt": int(doc["later"]["kt"]["compute"]),
        "library_compute": int(doc["library"]["cost"]["compute"]),
        "examples": int(doc["library"]["cost"]["examples"]),
        "state_written": int(doc["library"]["cost"]["state_written"]),
        "admitted": list(doc["library"]["admitted"]),
        "later_n": int(doc["partition"]["later_n"]),
        "train_n": int(doc["partition"]["train_n"]),
        "train_salt": doc["salts"]["train"],
        "later_salt": doc["salts"]["later"],
    }
    if observed != expected:
        raise RuntimeError(f"H1 v3 capital vector drifted: {observed}")
    if doc["boxes"]["H1/002-examples_demonstrations"]["status"] != "NO_STRICT_SAVING":
        raise RuntimeError("v3 examples box is no longer the remaining open")
    if doc["boxes"]["H1/008-state_written"]["status"] != "NO_STRICT_SAVING":
        raise RuntimeError("v3 state box is no longer the remaining open")
    return {
        "path": str(V3_RESULT.relative_to(REPO)),
        "sha256": digest,
        "denied": False,
        "cited_not_rerun": True,
        "terminal": doc["terminal"],
        "earned": list(doc["earned"]),
        "not_earned": list(doc["not_earned"]),
        "cannot_check": list(doc["cannot_check"]),
        "admitted": list(doc["library"]["admitted"]),
        "later_k0_compute": observed["later_k0"],
        "later_kt_compute": observed["later_kt"],
        "library_compute": observed["library_compute"],
        "library_examples_count_only": observed["examples"],
        "library_state_written": observed["state_written"],
        "ordinary_bytes": int(doc["ocm"]["ordinary_bytes"]),
        "ocm_bytes": int(doc["ocm"]["ocm_bytes"]),
        "revoked_bytes": int(doc["ocm"]["revoked_bytes"]),
        "train_ids": list(doc["partition"]["train_ids"]),
        "val_ids": list(doc["partition"]["val_ids"]),
        "later_ids": list(doc["partition"]["later_ids"]),
        "salts": dict(doc["salts"]),
        "note": (
            "v3 earned H1/001, H1/004, H1/005 at polynomial scope after SEARCH_AWARE "
            "scan plus single confirmation. H1/002 and H1/008 stayed NO_STRICT_SAVING "
            "because later additional examples and incremental persist were 0=0 and "
            "demonstration bytes were not charged."
        ),
    }


def load_g2_citation() -> dict[str, Any]:
    digest = sha256_file(G2_RESULT)
    if digest != G2_RESULT_SHA256:
        raise RuntimeError(f"G2 acquisition-economics receipt drifted: {digest}")
    doc = load_json(G2_RESULT)
    verdict = doc["verdict"]
    if verdict["terminal"] != "CHEAP_SEARCH_AWARE_SELECTION_REPRODUCES_THE_TOURNAMENT_CHOICE":
        raise RuntimeError("G2 terminal drifted")
    if verdict["tournament_acquisition_enumeration_attempts"] != 9_010_526:
        raise RuntimeError("G2 tournament size drifted")
    return {
        "path": str(G2_RESULT.relative_to(REPO)),
        "sha256": digest,
        "cited_not_rerun": True,
        "terminal": verdict["terminal"],
        "tournament_acquisition_enumeration_attempts": 9_010_526,
        "zero_search_acquisition_enumeration_attempts": 0,
        "break_even_tasks_with_tournament": 2136,
        "break_even_tasks_with_zero_search_acquisition": 41,
        "search_aware_token_operations": 4608,
        "note": (
            "Length-8 #192 ecology. The 9,010,526-attempt tournament is cited from "
            "research/g2-acquisition-economics-v1 and is not rerun here."
        ),
    }


def reconstruct_partitions(v3: dict[str, Any]):
    pop = V3.population(V3.LATER_LEN)
    train = V3.take(pop, V3.TRAIN_LEN, V3.TRAIN_SALT, V3.TRAIN_N)
    val = V3.take(pop, V3.VAL_LEN, V3.VAL_SALT, V3.VAL_N)
    later = V3.take(pop, V3.LATER_LEN, V3.LATER_SALT, V3.LATER_N)
    train_ids = [task.fingerprint for task, _ in train]
    val_ids = [task.fingerprint for task, _ in val]
    later_ids = [task.fingerprint for task, _ in later]
    if train_ids != v3["train_ids"] or val_ids != v3["val_ids"] or later_ids != v3["later_ids"]:
        raise RuntimeError("reconstructed v3 partition fingerprints drifted")
    overlapping = set(train_ids) & set(val_ids) or set(train_ids) & set(later_ids) or set(val_ids) & set(later_ids)
    if overlapping:
        raise RuntimeError("stratum overlap after reconstruction")
    return train, val, later


def examples_earned(later_kt: dict[str, int], later_k0: dict[str, int]) -> bool:
    return later_kt["count"] < later_k0["count"] and later_kt["bytes"] < later_k0["bytes"]


def box_status_later(later_kt_value: int, later_k0_value: int) -> str:
    if later_kt_value < later_k0_value:
        return "EARNED_AT_SCOPE"
    return "NO_STRICT_SAVING"


def run_study() -> dict[str, Any]:
    source_path = SRC / "ocm" / "learning" / "methods.py"
    observed_blob = git_blob_sha1(source_path)
    if observed_blob != METHOD_BLOB:
        raise RuntimeError(f"method source drift: {observed_blob}")
    if tuple(M.PRIMITIVES) != ("inc", "dec", "double", "square"):
        raise RuntimeError("production primitive grammar drifted")
    if V3.METHOD_BLOB != METHOD_BLOB:
        raise RuntimeError("v3 methods blob pin drifted")

    try:
        v3 = load_v3_capital()
        g2 = load_g2_citation()
    except RuntimeError as exc:
        return {
            "schema": SCHEMA,
            "issue": 165,
            "head": git_head(),
            "terminal": "CANNOT_CHECK_PREDECESSOR_DRIFT",
            "programme_wide_close": False,
            "production_src_edited": False,
            "methods_blob": observed_blob,
            "mechanism_comment": str(exc),
            "earned": [],
            "not_earned": [],
            "cannot_check": [
                "H1/002-examples_demonstrations",
                "H1/003-environment_interactions",
                "H1/006-io_tool_calls",
                "H1/007-human_instructional_burden",
                "H1/008-state_written",
            ],
            "m12_v5_claimed": False,
        }

    try:
        train, _val, later = reconstruct_partitions(v3)
    except RuntimeError as exc:
        return {
            "schema": SCHEMA,
            "issue": 165,
            "head": git_head(),
            "terminal": "CANNOT_CHECK_PARTITION_RECONSTRUCTION",
            "programme_wide_close": False,
            "production_src_edited": False,
            "methods_blob": observed_blob,
            "mechanism_comment": str(exc),
            "earned": [],
            "not_earned": [],
            "cannot_check": [
                "H1/002-examples_demonstrations",
                "H1/003-environment_interactions",
                "H1/006-io_tool_calls",
                "H1/007-human_instructional_burden",
                "H1/008-state_written",
            ],
            "m12_v5_claimed": False,
        }

    records = [demonstration_record(task, program) for task, program in train]
    payload = corpus_payload(records)
    canonical_size = len(canonical_dumps(payload))
    index = {record["fingerprint"]: record for record in records}
    hits = lookup_hits(later, index)
    fragment = tuple(v3["admitted"])

    teach_k0_count = len(later)
    teach_kt_count = len(later) - len(hits)
    teach_k0_bytes = sum(encoding_bytes(program) for _task, program in later)
    teach_kt_bytes = 0
    rewrite_shortened = 0
    for _task, program in later:
        operator_word, used, _cost = V3.greedy_rewrite(program, fragment)
        encoded = encoding_bytes(operator_word)
        teach_kt_bytes += encoded
        if used and encoded < encoding_bytes(program):
            rewrite_shortened += 1
    teach_later_would_appear_earned = teach_kt_count < teach_k0_count and teach_kt_bytes < teach_k0_bytes

    later_k0_examples = {"count": 0, "bytes": 0}
    later_kt_examples = {"count": 0, "bytes": 0}
    later_k0_state = 0
    later_kt_state = 0

    with tempfile.TemporaryDirectory(prefix="ocm-h1-examples-") as temp_dir:
        root = Path(temp_dir)
        ordinary_path = root / "demonstrations.json"
        ordinary_bytes = ordinary_persist_corpus(ordinary_path, payload)
        reloaded = ordinary_load_corpus(ordinary_path)
        ordinary_index = {record["fingerprint"]: record for record in reloaded["records"]}
        ordinary_hits = lookup_hits(later, ordinary_index)
        live_fps, atom_id, evidence_ids, ocm_bytes, live_count = admit_demonstrations(
            root / "ocm-live", records, revoke=False
        )
        dead_fps, dead_atom, _dead_eids, revoked_bytes, dead_live = admit_demonstrations(
            root / "ocm-revoked", records, revoke=True
        )

    ordinary_equals_ocm = ordinary_hits == hits and live_fps == [record["fingerprint"] for record in records]
    revoked_equals_empty = dead_fps is None and dead_live == 0
    if not revoked_equals_empty:
        terminal = "CANNOT_CHECK_REVOCATION_ABLATION"
        lifetime_terminal = "CANNOT_CHECK_REVOCATION_ABLATION"
        earned_examples = False
    else:
        earned_examples = examples_earned(later_kt_examples, later_k0_examples)
        terminal = "H1_EXAMPLES_EARNED_AT_SCOPE" if earned_examples else "EXAMPLES_ARE_LIBRARY_CAPITAL"
        lifetime_terminal = terminal

    library_examples_count = len(records)
    library_examples_bytes = canonical_size
    library_state = ocm_bytes
    lifetime_kt_examples_count = library_examples_count + later_kt_examples["count"]
    lifetime_k0_examples_count = later_k0_examples["count"]
    lifetime_kt_examples_bytes = library_examples_bytes + later_kt_examples["bytes"]
    lifetime_k0_examples_bytes = later_k0_examples["bytes"]
    lifetime_kt_state = library_state + later_kt_state
    lifetime_k0_state = later_k0_state

    examples_status = "EARNED_AT_SCOPE" if earned_examples else "NO_STRICT_SAVING"
    state_status = box_status_later(later_kt_state, later_k0_state)

    boxes = {
        "H1/001-new_information": {
            "text": "new information",
            "status": "CITED_EARNED_AT_SCOPE_FROM_V3",
            "cited_from": "research/h1-amortized-lifetime-v3",
            "later_k0": v3["later_k0_compute"],
            "later_kt": v3["later_kt_compute"],
            "note": "Cited from v3; this capsule does not re-search later tasks and does not re-earn 001.",
        },
        "H1/002-examples_demonstrations": {
            "text": "examples/demonstrations",
            "status": examples_status,
            "later_k0_count": later_k0_examples["count"],
            "later_kt_count": later_kt_examples["count"],
            "later_k0_bytes": later_k0_examples["bytes"],
            "later_kt_bytes": later_kt_examples["bytes"],
            "library_count": library_examples_count,
            "library_bytes": library_examples_bytes,
            "lifetime_k0_count": lifetime_k0_examples_count,
            "lifetime_kt_count": lifetime_kt_examples_count,
            "lifetime_k0_bytes": lifetime_k0_examples_bytes,
            "lifetime_kt_bytes": lifetime_kt_examples_bytes,
            "lookup_hits": len(hits),
            "unit": "demonstration count and canonical JSON bytes; later additional demonstrations after lookup-then-search",
            "note": (
                "Demonstrations are charged as library capital (count and bytes) on "
                "Channel.DEMONSTRATION. Later-task acquisition remains search. Lookup hits "
                f"were {len(hits)} because train/later strata are disjoint. Additional later "
                "examples are 0 in both arms, so there is no later-task example saving."
            ),
        },
        "H1/003-environment_interactions": {
            "text": "environment interactions",
            "status": "CANNOT_CHECK_NO_ENVIRONMENT_CHANNEL",
            "note": "Polynomial microscope has no external environment interaction channel.",
        },
        "H1/004-compute": {
            "text": "compute",
            "status": "CITED_EARNED_AT_SCOPE_FROM_V3",
            "cited_from": "research/h1-amortized-lifetime-v3",
            "later_k0": v3["later_k0_compute"],
            "later_kt": v3["later_kt_compute"],
            "library": v3["library_compute"],
            "note": "Cited from v3; later-task search is not rerun. G2 9e6 tournament is not rerun.",
        },
        "H1/005-verifier_calls": {
            "text": "verifier calls",
            "status": "CITED_EARNED_AT_SCOPE_FROM_V3",
            "cited_from": "research/h1-amortized-lifetime-v3",
            "later_k0": v3["later_k0_compute"],
            "later_kt": v3["later_kt_compute"],
            "note": "Cited from v3; unique-program checks track compute on this microscope.",
        },
        "H1/006-io_tool_calls": {
            "text": "IO/tool calls",
            "status": "CANNOT_CHECK_NO_IO_TOOL_CHANNEL",
            "note": "No external tool/IO channel; demonstration persist bytes are charged under state written.",
        },
        "H1/007-human_instructional_burden": {
            "text": "human instructional burden",
            "status": "CANNOT_CHECK_NO_HUMAN_INSTRUCTION_CHANNEL",
            "note": "No human teaching channel; training demonstrations are machine-solved identities.",
        },
        "H1/008-state_written": {
            "text": "state written",
            "status": state_status,
            "later_k0": later_k0_state,
            "later_kt": later_kt_state,
            "library": library_state,
            "lifetime_k0": lifetime_k0_state,
            "lifetime_kt": lifetime_kt_state,
            "ordinary_demo_bytes": ordinary_bytes,
            "canonical_demo_bytes": canonical_size,
            "ocm_demo_bytes": ocm_bytes,
            "revoked_demo_bytes": revoked_bytes,
            "cited_v3_library_ocm_bytes": v3["ocm_bytes"],
            "unit": "persist bytes of the demonstration corpus (ordinary JSON + OCM Channel.DEMONSTRATION snapshot)",
            "note": (
                "K_t writes the demonstration corpus; K_0 writes nothing. Later incremental "
                "persist is 0 in both arms. v3 library snapshot bytes remain cited capital "
                "and are not dropped from the programme ledger."
            ),
        },
    }

    if terminal == "CANNOT_CHECK_REVOCATION_ABLATION":
        comment = (
            "Revoking Channel.DEMONSTRATION evidence did not empty the live demonstration "
            "library; H1 examples cannot be checked."
        )
    elif terminal == "H1_EXAMPLES_EARNED_AT_SCOPE":
        comment = (
            "Later-task example count and bytes are both strictly smaller after charging "
            "demonstrations. That earning is bounded to this polynomial lookup parent. "
            "Not programme-wide H1, not human instructional burden, not M12 V5. v3 salts "
            "were not retuned."
        )
    else:
        comment = (
            "Demonstration-charging parent stores the v3 training solutions as first-class "
            f"capital: count {library_examples_count}, canonical bytes {library_examples_bytes}, "
            f"ordinary persist {ordinary_bytes}, OCM Channel.DEMONSTRATION persist {ocm_bytes}. "
            f"Later-task fingerprint lookup hits {len(hits)} of {len(later)} (strata disjoint), "
            "so additional later examples are 0 vs K_0 search 0. Examples remain library "
            "capital, not later-task savings. A teach-every-later-task parent would charge "
            f"K_0 later count {teach_k0_count} / bytes {teach_k0_bytes} vs rewrite-shortened "
            f"{teach_kt_count} / {teach_kt_bytes} ({rewrite_shortened} later identities shorter "
            "under the cited v3 fragment) and is rejected because K_0 actually searches. "
            "Predecessor free-residue accounting charged count 16 with bytes 0. State written "
            "is the demonstration persist; later incremental persist is 0=0. Ordinary JSON "
            "ties OCM lookup (PARENT_SUFFICIENT vs a persistent demonstration library). "
            "v3 later-task search and the G2 9e6 tournament were cited, not rerun. Salts "
            "were not retuned. Not M12 V5, not human instructional burden, not IO/tool calls."
        )

    return {
        "schema": SCHEMA,
        "issue": 165,
        "head": git_head(),
        "terminal": terminal,
        "lifetime_terminal": lifetime_terminal,
        "h1_vector_strictly_less": False,
        "programme_wide_close": False,
        "production_src_edited": False,
        "m12_v5_claimed": False,
        "methods_blob": observed_blob,
        "evidence_class": "E3",
        "contribution_level": "L2",
        "serving": "demonstration-lookup-then-search",
        "parent": "ordinary persistent demonstration corpus (JSON) + OCM Channel.DEMONSTRATION library",
        "parent_sufficient": ordinary_equals_ocm,
        "mechanism_comment": comment,
        "claim_ceiling": (
            "Bounded H1 examples/state comparison on the frozen v3 polynomial microscope "
            "after charging demonstrations as count, bytes, and later-task inequality. "
            "Later-task search vectors stay cited from v3. Not programme-wide H1, not "
            "human instructional burden, not IO/tool calls, not M12 V5, not a salt retune."
        ),
        "salts": dict(v3["salts"]),
        "salts_retuned": False,
        "v3_capital_input": v3,
        "g2_cited_not_rerun": g2,
        "predecessor_v1_terminal": "NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER",
        "predecessor_v2_terminal": "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS",
        "predecessor_v3_terminal": "AMORTIZED_ACQUISITION_SUPPORTED_AT_POLYNOMIAL_SCOPE",
        "predecessor_h5_terminal": "LIFETIME_NET_POSITIVE_AFTER_CHEAP_ACQUISITION",
        "h1_v1_result_overwritten": False,
        "h1_v2_result_overwritten": False,
        "h1_v3_result_overwritten": False,
        "h5_result_overwritten": False,
        "later_search_rerun": False,
        "tournament_rerun": False,
        "free_residue_parent": {
            "name": "V3_COUNT_ONLY",
            "library_count": 16,
            "library_bytes_charged": 0,
            "note": "Predecessor accounting treated demonstration bytes as free mining residue.",
        },
        "rejected_teach_later_parent": {
            "name": "TEACH_LATER",
            "rejected": True,
            "would_appear_earned": teach_later_would_appear_earned,
            "later_k0_count": teach_k0_count,
            "later_kt_count": teach_kt_count,
            "later_k0_bytes": teach_k0_bytes,
            "later_kt_bytes": teach_kt_bytes,
            "rewrite_shortened_identities": rewrite_shortened,
            "fragment": list(fragment),
            "reason": (
                "K_0 later-task acquisition is search, not teaching. Charging later_n "
                "demonstrations or rewrite-shortened operator encodings as later-task "
                "examples would fake-earn H1/002 by switching channel."
            ),
        },
        "demonstrations": {
            "channel": Channel.DEMONSTRATION.value,
            "count": library_examples_count,
            "canonical_bytes": canonical_size,
            "ordinary_bytes": ordinary_bytes,
            "ocm_bytes": ocm_bytes,
            "revoked_bytes": revoked_bytes,
            "fingerprint": payload["fingerprint"],
            "train_ids": [record["fingerprint"] for record in records],
            "lookup_hits": hits,
            "lookup_hit_count": len(hits),
            "later_n": len(later),
            "ordinary_equals_ocm": ordinary_equals_ocm,
            "revoked_equals_empty": revoked_equals_empty,
            "restart_before_lookup": True,
            "live_demo_records": live_count,
            "atom_id": atom_id,
            "evidence_n": len(evidence_ids),
            "revoked_atom_id": dead_atom,
        },
        "later": {
            "k0_examples": later_k0_examples,
            "kt_examples": later_kt_examples,
            "k0_state_written": later_k0_state,
            "kt_state_written": later_kt_state,
            "strict_example_count_saving": later_kt_examples["count"] < later_k0_examples["count"],
            "strict_example_bytes_saving": later_kt_examples["bytes"] < later_k0_examples["bytes"],
            "strict_state_saving": later_kt_state < later_k0_state,
            "cited_k0_compute": v3["later_k0_compute"],
            "cited_kt_compute": v3["later_kt_compute"],
        },
        "lifetime": {
            "k0_examples_count": lifetime_k0_examples_count,
            "kt_examples_count": lifetime_kt_examples_count,
            "k0_examples_bytes": lifetime_k0_examples_bytes,
            "kt_examples_bytes": lifetime_kt_examples_bytes,
            "k0_state_written": lifetime_k0_state,
            "kt_state_written": lifetime_kt_state,
            "note": (
                "K_0 lifetime examples/state are later-task only (reset, both 0). K_t lifetime "
                "is demonstration capital (count, canonical bytes, OCM persist) plus later-task "
                "additional examples/state (0)."
            ),
        },
        "boxes": boxes,
        "earned": sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_SCOPE"),
        "not_earned": sorted(k for k, v in boxes.items() if v["status"] == "NO_STRICT_SAVING"),
        "cannot_check": sorted(k for k, v in boxes.items() if str(v["status"]).startswith("CANNOT_CHECK")),
        "cited_earned_from_v3": sorted(k for k, v in boxes.items() if v["status"] == "CITED_EARNED_AT_SCOPE_FROM_V3"),
        "not_issued": [
            "PROGRAMME_WIDE_H1_CLOSE",
            "H1_001_RESEARCHED_HERE",
            "H1_004_RESEARCHED_HERE",
            "H1_005_RESEARCHED_HERE",
            "HUMAN_INSTRUCTIONAL_BURDEN",
            "IO_TOOL_CALLS",
            "ENVIRONMENT_INTERACTIONS",
            "M12_LIFETIME_V5",
            "SALT_RETUNE_OF_H1_V1_V2_V3",
            "TEACH_LATER_FAKE_EARNING",
            "OCM_UNIQUENESS_OVER_JSON_DEMONSTRATION_LIBRARY",
            "NINE_E6_TOURNAMENT_RERUN",
        ],
        "negative_terminals_frozen": list(ALLOWED_TERMINALS),
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
                "earned": result.get("earned", []),
                "not_earned": result.get("not_earned", []),
                "cannot_check": result.get("cannot_check", []),
                "cited_earned_from_v3": result.get("cited_earned_from_v3", []),
                "library_count": result.get("demonstrations", {}).get("count"),
                "canonical_bytes": result.get("demonstrations", {}).get("canonical_bytes"),
                "ordinary_bytes": result.get("demonstrations", {}).get("ordinary_bytes"),
                "ocm_bytes": result.get("demonstrations", {}).get("ocm_bytes"),
                "lookup_hit_count": result.get("demonstrations", {}).get("lookup_hit_count"),
                "parent_sufficient": result.get("parent_sufficient"),
                "m12_v5_claimed": result.get("m12_v5_claimed"),
                "later_search_rerun": result.get("later_search_rerun"),
                "tournament_rerun": result.get("tournament_rerun"),
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
