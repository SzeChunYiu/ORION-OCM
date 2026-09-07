"""Portable retained-evidence audit; no Lean, Linux runtime, extraction or dispatch.

Run: python -I -S research/proof-environment-v1/audit_evidence.py
Success means archived bytes, recorded controls and current source bindings agree.
Omitted external ELF payloads and historical host state are not revalidated.
"""
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
if __name__ == "__main__":
    for name in ("audit_data", "audit_process", "audit_receipts"):
        path = HERE / (name + ".py")
        if path.resolve(strict=True) != path: raise ImportError("noncanonical audit source")
        module = ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
        exec(compile(path.read_bytes(), str(path), "exec", dont_inherit=True), module.__dict__)
from audit_data import bound, canonical, file_bytes, inventory, load_json, member_name, read_archive, record, require, same
from audit_receipts import audit_rows

FINAL_SEAL_SHA256 = "67476a9394ad8ebe945ca3f1105ad893574ba0712df8a0e7ceb238ae42867fc9"
RUNTIME_SHA256 = "c9acc789908a216809a509facfc06c5aaf02206197fbc2f9f1531d3ae1c6d4e8"
MATRIX_SHA256 = "e2a0e9d62f06d8bf7b0e6017fd1e41aad38035b264103007656aa37076e8a065"


def source_bindings(runtime, matrix):
    bindings = {"research/" + member_name(n): v for n, v in runtime["driver_sources"].items()}
    for name, binding in {**runtime["build"]["sources"], "commission.py": matrix["recorder"],
                          **matrix["recorder_dependencies"]}.items():
        path = "research/proof-environment-v1/" + member_name(name)
        require(path not in bindings, "overlapping source binding")
        bindings[path] = {k: binding[k] for k in ("sha256", "bytes")}
    require(len(bindings) == 36, "source closure differs")
    return bindings


def verify_sources(repo, bindings):
    require(type(bindings) is dict and bindings, "source bindings required")
    for name, binding in bindings.items():
        bound(file_bytes(Path(repo) / member_name(name)), binding, "current source " + name)


def validate_final(data, freeze):
    require(freeze["schema"] == "ocm.proof-environment.portable-evidence-freeze.v1", "audit freeze schema differs")
    require(freeze["final_seal"]["sha256"] == FINAL_SEAL_SHA256, "final seal authority differs")
    seal = load_json(bound(data["seal.json"], freeze["final_seal"], "final complete seal"))
    require(seal["schema"] == "ocm.proof-environment.commission-seal.v1" and
            seal["terminal"] == "CONTROLS_PASSED" and seal["evidence_complete"] is True and
            seal["error"] is None, "final seal incomplete")
    require(same(inventory({n: v for n, v in data.items() if n != "seal.json"}), seal["files"]),
            "final complete membership differs")
    require(len(data) == freeze["final_member_count"] == 681 and
            sum(len(raw) for raw in data.values()) == freeze["final_member_bytes"] == 66843845,
            "final retained counts differ")
    result = load_json(data["result.json"]); matrix = load_json(data["matrix.json"])
    require(same(result["files"], inventory({n: v for n, v in data.items() if n not in {"result.json", "seal.json"}})),
            "provisional result inventory differs")
    require(record(data["matrix.json"])["sha256"] == freeze["matrix_sha256"] == MATRIX_SHA256, "registered matrix differs")
    runtime_raw = data["cases/composition/prepare/runtime.json"]
    require(record(runtime_raw)["sha256"] == freeze["runtime_sha256"] == RUNTIME_SHA256, "registered runtime differs")
    require(type(freeze["denominator"]) is int and freeze["denominator"] == 47, "registered denominator differs")
    runtime = load_json(runtime_raw)
    return result, matrix, runtime


def audit(package):
    package = Path(package).resolve(strict=True)
    freeze = load_json(file_bytes(package / "SOURCE_FREEZE.json"))
    records = package / "records"
    sealed = load_json(bound(file_bytes(records / "ARCHIVE_PACKAGE_SEAL.json"), freeze["records_seal"], "archive package seal"))
    require(sealed["schema"] == "ocm.proof-environment.archive-package-seal.v1" and
            sealed["terminal"] == "EVIDENCE_ARCHIVES_BYTE_VERIFIED", "archive seal incomplete")
    require({p.name for p in records.iterdir()} == set(sealed["files"]) | {"ARCHIVE_PACKAGE_SEAL.json"},
            "archive package membership differs")
    for name, binding in sealed["files"].items():
        bound(file_bytes(records / member_name(name)), binding, "archive artifact " + name)
    manifest = load_json(file_bytes(records / "MANIFEST.json")); final = None; archived_count = 0
    require(manifest["schema"] == "ocm.proof-environment.evidence-archives.v1" and
            manifest["terminal"] == "ARCHIVED_AND_BYTE_VERIFIED", "archive manifest incomplete")
    for name, group in manifest["groups"].items():
        archive = records / member_name(group["archive"]["path"])
        bound(file_bytes(archive), group["archive"], "compressed archive")
        members = load_json(bound(file_bytes(records / member_name(group["members"]["path"])), group["members"], "member map"))
        data = read_archive(archive, members)
        bound(file_bytes(archive), group["archive"], "post-read compressed archive")
        require(len(data) == group["member_count"] and sum(len(v) for v in data.values()) == group["member_bytes"],
                "archive group counts differ")
        archived_count += len(data)
        if name == "final-commissioning": final = data
    require(final is not None, "final commissioning archive missing")
    result, matrix, runtime = validate_final(final, freeze)
    bindings = source_bindings(runtime, matrix)
    require(same(freeze["source_files"], bindings), "registered source membership differs")
    verify_sources(package.parent.parent, bindings)
    outcome = audit_rows(final, result, matrix, runtime, freeze["original_root"])
    return {"terminal": "RETAINED_EVIDENCE_AND_SOURCE_BINDINGS_PASS", **outcome,
            "archives": len(manifest["groups"]), "archived_members": archived_count, "current_source_files": len(bindings),
            "final_files": len(final), "final_seal_sha256": FINAL_SEAL_SHA256,
            "scope": "Retained record integrity and source correspondence only; no native rerun or omitted-runtime validation."}


if __name__ == "__main__":
    try: print(canonical(audit(HERE)).decode())
    except (ValueError, KeyError, TypeError, OSError, EOFError) as exc:
        print(canonical({"terminal": "CANNOT_CHECK", "reason": type(exc).__name__ + ": " + str(exc)}).decode())
        raise SystemExit(2)
