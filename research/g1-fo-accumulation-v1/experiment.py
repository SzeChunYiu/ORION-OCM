"""G1 architecture box: intelligence accumulates in F and O, not in Π.

Research-only. Production ``src/`` is not modified. Competence is admitted
as one G2 macro plus one L1 construction into ledger F/O state. Controller
nloc is measured, not edited.

If Π nloc stays constant and ledger F/O bytes grow, the capsule terminal is
``FO_ACCUMULATION_AT_MICRO_SCOPE``. Otherwise the terminal is an honest
negative. ``MINIMUM_SELF_EXTENDING_VESSEL`` is not issued.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

from ocm.kso.ids import content_hash
from ocm.kso.space import Atom, Hyperedge
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.runtime.ocm_runtime import OCMRuntime
from ocm.store.evidence import Channel

G2_PATH = REPO / "research" / "g2-macro-operator-v1" / "experiment.py"
L1_PATH = REPO / "research" / "l1-linguistic-g2-v1" / "experiment.py"
FREEZE_COUNTS = REPO / "research" / "g1-vessel-freeze-v1" / "G1_3_COUNTS.json"
PARENT_FO = REPO / "research" / "g1-fo-competence-v2" / "RESULT.json"
PARENT_PI_SMALL = REPO / "research" / "g1-pi-small-v1" / "RESULT.json"
PARENT_GROWTH = REPO / "research" / "g1-controller-growth-v1" / "RESULT.json"
PARENT_CORES = REPO / "research" / "g1-duplicate-cores-v1" / "RESULT.json"
L1_SCOPE = Scope.of("l1-microworld.v1")

SCHEMA = "ocm.g1.fo-accumulation.result.v1"
SALT = "orion-ocm-g1-fo-accumulation-v1"
ISSUE = 165
GATE = "INTELLIGENCE_IN_F_AND_O"
BOX_TEXT = (
    "Machine intelligence accumulates primarily in F and O, not in an "
    "ever-growing hard-coded controller."
)

G2_SPEC = importlib.util.spec_from_file_location("g1_fo_acc_g2_parent", G2_PATH)
G2 = importlib.util.module_from_spec(G2_SPEC)
assert G2_SPEC is not None and G2_SPEC.loader is not None
sys.modules[G2_SPEC.name] = G2
G2_SPEC.loader.exec_module(G2)

L1_SPEC = importlib.util.spec_from_file_location("g1_fo_acc_l1_parent", L1_PATH)
L1 = importlib.util.module_from_spec(L1_SPEC)
assert L1_SPEC is not None and L1_SPEC.loader is not None
sys.modules[L1_SPEC.name] = L1
L1_SPEC.loader.exec_module(L1)

CONTROLLER_SPECS = (
    {
        "path": "src/ocm/runtime/solve.py",
        "justification": (
            "Canonical domain-general Π_exec. Freeze role Π. Reads the field; "
            "must not grow when competence is admitted."
        ),
        "freeze_role": "Π",
        "counted_as": "Π_exec",
    },
    {
        "path": "src/ocm/runtime/ocm_runtime.py",
        "justification": (
            "Shared Admit_C executive. Freeze role Π. Both admits go through "
            "this one class."
        ),
        "freeze_role": "Π",
        "counted_as": "Π_exec",
    },
    {
        "path": "src/ocm/dialogue/planner.py",
        "justification": (
            "G1.3 domain-control. Freeze role PRIOR. Must not grow or fork "
            "when the L1 construction lands in the ledger."
        ),
        "freeze_role": "PRIOR",
        "counted_as": "domain-control Π",
    },
)

PROTECTED_RESULTS = (
    PARENT_GROWTH,
    PARENT_FO,
    PARENT_PI_SMALL,
    PARENT_CORES,
)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def git_tracked(path: Path) -> bool:
    if not path.is_file():
        return False
    rel = str(path.relative_to(REPO))
    listed = subprocess.check_output(["git", "ls-files", "--", rel], cwd=REPO, text=True).strip()
    return bool(listed)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nloc_text(text: str) -> int:
    n = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        n += 1
    return n


def nloc_path(path: Path) -> int:
    return nloc_text(path.read_text(encoding="utf-8"))


def dir_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def file_snapshot(rel: str) -> dict[str, Any]:
    path = REPO / rel
    raw = path.read_bytes()
    return {
        "path": rel,
        "exists": path.is_file(),
        "nloc": nloc_text(raw.decode("utf-8")),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def snapshot_controllers() -> list[dict[str, Any]]:
    rows = []
    for spec in CONTROLLER_SPECS:
        row = file_snapshot(spec["path"])
        row.update({k: spec[k] for k in ("justification", "freeze_role", "counted_as")})
        rows.append(row)
    return rows


def freeze_role_inventory(role: str) -> dict[str, Any]:
    data = json.loads(FREEZE_COUNTS.read_text())
    freeze_files = [row for row in data["files"] if row["role"] == role]
    live = []
    for row in freeze_files:
        snap = file_snapshot(row["path"])
        snap["freeze_nloc"] = row["nloc"]
        snap["freeze_bytes"] = row["bytes"]
        snap["freeze_sha256"] = row["sha256"]
        snap["matches_freeze_sha256"] = snap["sha256"] == row["sha256"]
        live.append(snap)
    return {
        "role": role,
        "nloc_definition": data["nloc_definition"],
        "freeze_git_head": data["git_head"],
        "freeze_nloc": data["by_role"][role]["nloc"],
        "freeze_files": data["by_role"][role]["files"],
        "live_nloc": sum(r["nloc"] for r in live),
        "live_bytes": sum(r["bytes"] for r in live),
        "files": live,
    }


def compare_snapshots(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    after_by = {row["path"]: row for row in after}
    rows = []
    for left in before:
        right = after_by[left["path"]]
        identical = left["sha256"] == right["sha256"]
        nloc_constant = left["nloc"] == right["nloc"]
        grew = right["nloc"] > left["nloc"] or right["bytes"] > left["bytes"]
        rows.append(
            {
                "path": left["path"],
                "nloc_before": left["nloc"],
                "nloc_after": right["nloc"],
                "bytes_before": left["bytes"],
                "bytes_after": right["bytes"],
                "sha256_before": left["sha256"],
                "sha256_after": right["sha256"],
                "nloc_constant": nloc_constant,
                "byte_identical": identical,
                "grew": grew,
            }
        )
    return {
        "files": rows,
        "all_nloc_constant": all(r["nloc_constant"] for r in rows),
        "all_byte_identical": all(r["byte_identical"] for r in rows),
        "any_grew": any(r["grew"] for r in rows),
        "nloc_before": sum(r["nloc_before"] for r in rows),
        "nloc_after": sum(r["nloc_after"] for r in rows),
    }


def live_procedures(runtime: OCMRuntime) -> list[str]:
    revoked = runtime.state.revoked
    out = []
    for atom in runtime.state.ks.atoms:
        if atom.atom_type == "procedure" and atom.liveness(revoked) is Liveness.LIVE:
            out.append(atom.atom_id)
    return sorted(out)


def admit_l1_construction(root: Path) -> dict[str, Any]:
    train_pairs = [(a, n) for a in L1.TRAIN_ADJ for n in L1.TRAIN_NOUN]
    runtime = OCMRuntime(root)
    lesson_ids = []
    for adj, noun in train_pairs:
        _rec, eid = runtime.admit_evidence(
            {"schema": "g1.fo-accumulation.l1-lesson", "adj": adj, "noun": noun},
            Channel.OBSERVATION,
            "l1-adj-noun.v1",
            scope=L1_SCOPE,
        )
        lesson_ids.append(eid)
    warrant = WarrantProfile.of(set(lesson_ids))
    source_payload = {
        "kind": "l1.construction.support.v1",
        "lessons": [content_hash({"adj": a, "noun": n}) for a, n in train_pairs],
    }
    source_id = "l1-construction-support:" + content_hash(source_payload)
    runtime.admit_object(
        Atom(
            source_id,
            "proof",
            warrant,
            scope=L1_SCOPE,
            quarantined=True,
            content_ref=content_hash(source_payload),
            meta=tuple(source_payload.items()),
        ),
        (),
        "OBSERVATION",
    )
    payload = {
        "kind": "l1.construction.v1",
        "construction_id": "adj-noun-intersective.v1",
        "pattern": ["ADJ", "NOUN"],
        "fingerprint": content_hash({"id": "adj-noun-intersective.v1", "pattern": ["ADJ", "NOUN"]}),
    }
    atom_id = "l1-construction:" + content_hash(payload)
    edge = Hyperedge("support:" + atom_id, (source_id,), (atom_id,), "SUPPORT", warrant=warrant)
    runtime.admit_object(
        Atom(
            atom_id,
            "procedure",
            warrant,
            scope=L1_SCOPE,
            content_ref=content_hash(payload),
            meta=tuple(payload.items()),
        ),
        (edge,),
        "OBSERVATION",
    )
    runtime.persist()
    replay = OCMRuntime(root)
    atom = replay.state.ks.atom_map().get(atom_id)
    if atom is None or atom.liveness(replay.state.revoked) is not Liveness.LIVE:
        raise RuntimeError("L1 construction did not survive restart")
    stored = dict(atom.meta)
    if atom.content_ref != content_hash(stored):
        raise RuntimeError("L1 construction content identity mismatch")
    skill = L1.ConstructionSkill(
        stored["construction_id"],
        tuple(stored["pattern"]),
        tuple(lesson_ids),
        tuple(lesson_ids),
    )
    words = {
        **{w: (L1.Category.ADJ, w) for w in L1.TRAIN_ADJ + L1.HELD_ADJ},
        **{w: (L1.Category.NOUN, w) for w in L1.TRAIN_NOUN + L1.HELD_NOUN},
        **{w: (L1.Category.DET, w) for w in L1.NUMBERS},
    }
    lex = L1.teach_lexicon(words)
    fresh = [(a, n) for a in L1.HELD_ADJ for n in L1.HELD_NOUN]
    fresh += [(L1.TRAIN_ADJ[0], L1.HELD_NOUN[0]), (L1.HELD_ADJ[0], L1.TRAIN_NOUN[0])]
    invoked_rows = []
    for pair in fresh:
        rec = L1.parse_with_skill(pair, skill, lex, set())
        invoked_rows.append({"tokens": list(pair), "invoked": rec["invoked"], "status": rec["status"]})
    reset_rows = [L1.parse_with_skill(pair, None, lex, set()) for pair in fresh]
    return {
        "atom_id": atom_id,
        "lesson_evidence": lesson_ids,
        "held_out_invoked": all(r["invoked"] for r in invoked_rows),
        "reset_has_no_construction": all(not r["invoked"] for r in reset_rows),
        "held_out_rows": invoked_rows,
        "live_after_restart": True,
        "construction_id": stored["construction_id"],
    }


def parent_citation(path: Path, expected_terminal: str | None = None) -> dict[str, Any]:
    rel = str(path.relative_to(REPO))
    tracked = git_tracked(path)
    if not tracked:
        return {
            "path": rel,
            "present": False,
            "git_tracked": False,
            "expected_terminal": expected_terminal,
            "not_rewritten": True,
        }
    digest = sha256_file(path)
    data = json.loads(path.read_text())
    return {
        "path": rel,
        "present": True,
        "git_tracked": True,
        "terminal": data.get("terminal"),
        "schema": data.get("schema"),
        "sha256": digest,
        "expected_terminal": expected_terminal,
        "matches_expected_terminal": (
            expected_terminal is None or data.get("terminal") == expected_terminal
        ),
        "not_rewritten": True,
    }


def src_tree_intact() -> dict[str, Any]:
    diff = subprocess.run(
        ["git", "diff", "--exit-code", "--", "src"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return {
        "git_diff_src_clean": diff.returncode == 0,
        "returncode": diff.returncode,
        "deleted": False,
        "note": "This capsule writes only under research/g1-fo-accumulation-v1/ and the workflow file.",
    }


def protected_result_digests() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for path in PROTECTED_RESULTS:
        key = path.parent.name
        out[key] = sha256_file(path) if git_tracked(path) else None
    return out


def measure_microworld() -> dict[str, Any]:
    controllers_before = snapshot_controllers()
    freeze_pi_before = freeze_role_inventory("Π")
    freeze_f_before = freeze_role_inventory("F")
    freeze_o_before = freeze_role_inventory("O")
    parents_before = protected_result_digests()

    with tempfile.TemporaryDirectory(prefix="g1-fo-acc-") as tmp:
        root = Path(tmp) / "ledger"
        root.mkdir()
        bytes_empty = dir_bytes(root)
        loaded, atom_id, training_ev, utility_ev = G2.admit_macro(
            root,
            ("inc", "inc"),
            {"schema": "g1.fo-accumulation.training", "fragment": ["inc", "inc"]},
            {"schema": "g1.fo-accumulation.utility", "accepted": True},
        )
        after_g2 = OCMRuntime(root)
        bytes_after_g2 = dir_bytes(root)
        procs_after_g2 = live_procedures(after_g2)
        l1 = admit_l1_construction(root)
        after_both = OCMRuntime(root)
        bytes_after_both = dir_bytes(root)
        procs_after_both = live_procedures(after_both)
        macro_live = atom_id in procs_after_both
        l1_live = l1["atom_id"] in procs_after_both

        controllers_after = snapshot_controllers()
        freeze_pi_after = freeze_role_inventory("Π")
        freeze_f_after = freeze_role_inventory("F")
        freeze_o_after = freeze_role_inventory("O")
        compared = compare_snapshots(controllers_before, controllers_after)
        freeze_pi_compared = compare_snapshots(
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_pi_before["files"]],
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_pi_after["files"]],
        )
        freeze_f_compared = compare_snapshots(
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_f_before["files"]],
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_f_after["files"]],
        )
        freeze_o_compared = compare_snapshots(
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_o_before["files"]],
            [{k: r[k] for k in ("path", "nloc", "bytes", "sha256")} for r in freeze_o_after["files"]],
        )
        parents_after = protected_result_digests()

        g2_delta = bytes_after_g2 - bytes_empty
        l1_delta = bytes_after_both - bytes_after_g2
        fo_delta = bytes_after_both - bytes_empty
        fo_bytes_grew = bytes_after_both > bytes_after_g2 > bytes_empty
        pi_nloc_constant = (
            compared["all_nloc_constant"]
            and freeze_pi_compared["all_nloc_constant"]
            and freeze_pi_before["live_nloc"] == freeze_pi_after["live_nloc"]
        )
        authored_fo_nloc_constant = (
            freeze_f_compared["all_nloc_constant"]
            and freeze_o_compared["all_nloc_constant"]
        )
        parent_unchanged = {
            key: parents_before[key] == parents_after[key] for key in parents_before
        }
        return {
            "controllers_before": controllers_before,
            "controllers_after": controllers_after,
            "controller_compare": compared,
            "pi_nloc_before": compared["nloc_before"],
            "pi_nloc_after": compared["nloc_after"],
            "pi_nloc_constant": pi_nloc_constant,
            "freeze_pi_before": {
                "live_nloc": freeze_pi_before["live_nloc"],
                "freeze_nloc": freeze_pi_before["freeze_nloc"],
                "freeze_files": freeze_pi_before["freeze_files"],
                "nloc_definition": freeze_pi_before["nloc_definition"],
            },
            "freeze_pi_after_nloc": freeze_pi_after["live_nloc"],
            "freeze_pi_compare": freeze_pi_compared,
            "freeze_f_nloc_before": freeze_f_before["live_nloc"],
            "freeze_f_nloc_after": freeze_f_after["live_nloc"],
            "freeze_o_nloc_before": freeze_o_before["live_nloc"],
            "freeze_o_nloc_after": freeze_o_after["live_nloc"],
            "authored_fo_nloc_constant": authored_fo_nloc_constant,
            "admitted_macro": list(loaded),
            "macro_atom_id": atom_id,
            "macro_training_evidence": training_ev,
            "macro_utility_evidence": utility_ev,
            "macro_live_after_both_admits": macro_live,
            "l1": l1,
            "l1_live_after_both_admits": l1_live,
            "ledger_bytes_empty": bytes_empty,
            "ledger_bytes_after_g2": bytes_after_g2,
            "ledger_bytes_after_g2_and_l1": bytes_after_both,
            "fo_delta_bytes": fo_delta,
            "g2_delta_bytes": g2_delta,
            "l1_delta_bytes": l1_delta,
            "fo_bytes_grew": fo_bytes_grew,
            "live_procedure_atoms_after_g2": procs_after_g2,
            "live_procedure_atoms_after_both": procs_after_both,
            "two_domains_in_fo_state": macro_live and l1_live,
            "parent_result_sha256_unchanged": parent_unchanged,
        }


def decide_terminal(world: dict[str, Any]) -> str:
    admits_landed = (
        world["macro_live_after_both_admits"]
        and world["l1_live_after_both_admits"]
        and world["l1"]["held_out_invoked"]
        and world["l1"]["reset_has_no_construction"]
    )
    if not world["pi_nloc_constant"] or world["controller_compare"]["any_grew"]:
        return "CONTROLLER_GREW_AT_SCOPE"
    if not admits_landed:
        return "FO_ACCUMULATION_INCOMPLETE_AT_SCOPE"
    if not world["fo_bytes_grew"]:
        return "NO_FO_BYTE_GROWTH_AT_SCOPE"
    return "FO_ACCUMULATION_AT_MICRO_SCOPE"


def run_study() -> dict[str, Any]:
    world = measure_microworld()
    terminal = decide_terminal(world)
    micro_ok = terminal == "FO_ACCUMULATION_AT_MICRO_SCOPE"
    result = {
        "schema": SCHEMA,
        "salt": SALT,
        "issue": ISSUE,
        "gate": GATE,
        "head": git_head(),
        "production_code_deleted": False,
        "terminal": terminal,
        "programme_terminal": "COMPACT_VESSEL_PARTIAL",
        "claim_ceiling": (
            "At this polynomial + L1 microworld, measured Π nloc stays constant "
            "while G2 macro and L1 construction competence increase ledger F/O "
            "bytes. Authored freeze F/O source nloc is a control and also stays "
            "constant. Not programme-wide intelligence-in-F-and-O close: "
            "procedural work operators remain authored. Not "
            "MINIMUM_SELF_EXTENDING_VESSEL. Programme-level terminal stays "
            "COMPACT_VESSEL_PARTIAL."
        ),
        "not_issued": [
            "MINIMUM_SELF_EXTENDING_VESSEL",
            "MINIMUM_SELF_EXTENDING_VESSEL_SUPPORTED_AT_SCOPE",
            "CONTROLLER_GROWTH_DOMINATES",
            "STATE_SIZE_DOMINATES",
            "DOMAIN_CORE_FORK_REQUIRED",
            "PI_REMAINS_SMALL",
            "INTELLIGENCE_IN_F_AND_O",
        ],
        "not_issued_reasons": {
            "MINIMUM_SELF_EXTENDING_VESSEL": (
                "G1.2 subtraction is not a minimality proof; nothing deleted."
            ),
            "INTELLIGENCE_IN_F_AND_O": (
                "Unscoped programme claim. This capsule issues only the "
                "micro-scope terminal FO_ACCUMULATION_AT_MICRO_SCOPE when earned."
            ),
            "PI_REMAINS_SMALL": (
                "Paired architecture box; measured here only as the Π-nloc "
                "control. Programme close belongs to g1-pi-small-v1 if present."
            ),
        },
        "parents": {
            "g1-fo-competence-v2": parent_citation(
                PARENT_FO, "COMPETENCE_IN_FO_STATE_AT_MICRO_SCOPE"
            ),
            "g1-pi-small-v1": parent_citation(PARENT_PI_SMALL, "PI_REMAINS_SMALL_AT_MICRO_SCOPE"),
            "g1-controller-growth-v1": parent_citation(PARENT_GROWTH, "COMPACT_VESSEL_PARTIAL"),
            "g1-duplicate-cores-v1": parent_citation(PARENT_CORES, "SINGLE_CORE_AT_SCOPE"),
        },
        "src_custody": src_tree_intact(),
        "microworld": world,
        "architecture_boxes": {
            "intelligence_in_f_and_o": {
                "text": BOX_TEXT,
                "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else terminal,
                "capsule_terminal": terminal,
                "programme_status": "PARTIAL",
                "note": (
                    "New competence this run is G2 macro + L1 construction "
                    "procedure atoms / ledger bytes. Π nloc does not grow. "
                    "Procedural work operators remain authored. Cite "
                    "g1-fo-competence-v2 for G1.3.2; cite g1-pi-small-v1 when "
                    "that RESULT is tracked."
                ),
            }
        },
        "architecture_rules_empirical": {
            "INTELLIGENCE_IN_F_AND_O": (
                "EARNED_AT_POLYNOMIAL_AND_L1_MICRO_SCOPE" if micro_ok else terminal
            ),
            "INTELLIGENCE_IN_F_AND_O_PROGRAMME": "PARTIAL",
            "PI_SMALL_DOMAIN_GENERAL": "PARTIAL",
        },
        "G1_checkboxes": {
            "section_2": [
                {
                    "id": "INTELLIGENCE_IN_F_AND_O",
                    "text": BOX_TEXT,
                    "status": "EARNED_AT_MICRO_SCOPE" if micro_ok else terminal,
                    "capsule_terminal": terminal,
                    "programme_status": "PARTIAL",
                    "pi_nloc_constant": world["pi_nloc_constant"],
                    "fo_bytes_grew": world["fo_bytes_grew"],
                    "fo_delta_bytes": world["fo_delta_bytes"],
                }
            ],
            "G1.3": [
                {
                    "id": "G1.3.2",
                    "text": (
                        "Demonstrate new competence predominantly appears in "
                        "learned/imported field/operator state."
                    ),
                    "status": "CITED_FROM_G1_FO_COMPETENCE_V2",
                    "predominantly_across_three_domains": False,
                    "cite": "research/g1-fo-competence-v2/RESULT.json",
                }
            ],
        },
    }
    return result


def write_outputs(out: Path | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or run_study()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    capsule = HERE / "RESULT.json"
    capsule.write_text(text)
    if out is not None and out.resolve() != capsule.resolve():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    return payload


def main(out: Path | None = None) -> dict[str, Any]:
    result = write_outputs(out)
    world = result["microworld"]
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "programme_terminal": result["programme_terminal"],
                "pi_nloc": world["pi_nloc_after"],
                "pi_nloc_constant": world["pi_nloc_constant"],
                "fo_delta_bytes": world["fo_delta_bytes"],
                "g2_delta_bytes": world["g2_delta_bytes"],
                "l1_delta_bytes": world["l1_delta_bytes"],
                "fo_bytes_grew": world["fo_bytes_grew"],
                "parents_present": {
                    name: row["present"] for name, row in result["parents"].items()
                },
                "not_issued_minimum_vessel": "MINIMUM_SELF_EXTENDING_VESSEL"
                in result["not_issued"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)
