#!/usr/bin/env python3
"""M2-P2 stage-2 orchestrator: authored package -> entry-gate receipt.

Runs, in the frozen order (M2P2_FREEZE_V1.json entry_gates.order):

  1. taxonomy hostile (m2p2_taxa.py, 219 frozen tokens) over every authored
     artifact; any overlap -> AUTHORSHIP_CONTAMINATED (fail-closed);
  2. static pre-execution guard on emit_worlds.py: the frozen hard bounds forbid
     network / filesystem access / environment reads / threads / subprocesses;
     a forbidden import or call is rejected, never patched;
  3. determinism: emit_worlds.py run twice in a sandboxed subprocess (scratch cwd,
     wall-clock timeout, captured stdout/stderr); the two worlds.jsonl outputs must
     be byte-identical; non-determinism -> ASSAY_DEFECT class, recorded;
  4. authoring floors: >= 6 worlds, >= 2 distinct shapes (shape = chunk count,
     chunk-length multiset, min builder length, part fractions);
  5. compilation of every world via m2p2_compile (structural gates + viability);
     non-viable worlds are retained as CANNOT_CHECK_world, never dropped;
     < 4 viable worlds -> CANNOT_CHECK_TOO_FEW_VIABLE_WORLDS;
  6. G-SURF (m2p2_gsurf.py) on every viable world.

Emits M2P2_STAGE2_RECEIPT.json with the aggregate stage-2 verdict. This script
never scores: no arm, ladder or admission decision runs here.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, re, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import m2p2_compile as C      # noqa: E402
import m2p2_gsurf             # noqa: E402

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2P2_STAGE2_RECEIPT_V1"
EMIT_TIMEOUT_S = 120

# frozen hard bounds -> forbidden surface (review guard; complements line review)
FORBIDDEN_MODULES = {
    "socket", "http", "urllib", "requests", "ftplib", "smtplib", "telnetlib",
    "xmlrpc", "asyncio", "threading", "multiprocessing", "subprocess", "socketserver",
    "email", "ssl", "ctypes", "pickle", "shelve", "dbm", "sqlite3",
}
FORBIDDEN_CALLS = [
    r"\bos\.(system|popen|exec\w*|spawn\w*)\s*\(",
    r"\bopen\s*\(\s*['\"][^'\"]*['\"]\s*,\s*['\"][wax]",
    r"\bPath\s*\([^)]*\)\.write_text\s*\(",
    r"\bwrite_bytes\s*\(",
    r"\beval\s*\(", r"\bexec\s*\(", r"\b__import__\s*\(",
    r"\bos\.environ", r"\bgetenv\s*\(",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def taxonomy_scan(repo: Path, artifacts: list[Path]) -> dict:
    sys.path.insert(0, str(HERE))
    import m2p2_taxa as taxa
    tiers = taxa.build_token_list()
    scan = taxa.scan_paths(artifacts, tiers)
    ctrl = taxa.no_alarm_control(taxa._patterns(tiers))
    tamp = taxa.tamper_control(artifacts, tiers)
    return {"total_overlaps": scan["total_overlaps"],
            "per_file": scan["per_file"],
            "no_alarm_control": ctrl, "tamper_control": tamp,
            "verdict": "CLEAN" if (scan["total_overlaps"] == 0
                                   and ctrl["control_passed"]
                                   and tamp["alarm"]) else "AUTHORSHIP_CONTAMINATED"}


def static_guard(emit_path: Path) -> dict:
    src = emit_path.read_text()
    bad_modules = sorted({m for m in FORBIDDEN_MODULES
                          if re.search(r"(?<![A-Za-z0-9_])" + m + r"(?![A-Za-z0-9_])", src)})
    bad_calls = [pat for pat in FORBIDDEN_CALLS if re.search(pat, src)]
    ok = not bad_modules and not bad_calls
    return {"file": str(emit_path), "forbidden_modules": bad_modules,
            "forbidden_calls": bad_calls,
            "verdict": "ACCEPT" if ok else "REJECTED_CANNOT_CHECK"}


def determinism_double_run(emit_path: Path) -> dict:
    runs = []
    for i in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f"m2p2_emit{i}_") as td:
            td = Path(td)
            try:
                r = subprocess.run(
                    [sys.executable, str(emit_path)], cwd=str(td),
                    capture_output=True, text=True, timeout=EMIT_TIMEOUT_S)
                worlds = td / "worlds.jsonl"
                runs.append({"rc": r.returncode,
                             "worlds_found": worlds.is_file(),
                             "sha256": sha256_file(worlds) if worlds.is_file() else None,
                             "stdout_tail": r.stdout[-400:], "stderr_tail": r.stderr[-400:]})
            except subprocess.TimeoutExpired:
                runs.append({"rc": None, "timeout": True, "worlds_found": False,
                             "sha256": None, "stdout_tail": "", "stderr_tail": "TIMEOUT"})
    ok = (len(runs) == 2 and all(r["rc"] == 0 and r["worlds_found"] for r in runs)
          and runs[0]["sha256"] is not None and runs[0]["sha256"] == runs[1]["sha256"])
    return {"runs": runs, "byte_identical": ok,
            "verdict": "DETERMINISTIC" if ok else "ASSAY_DEFECT_NONDETERMINISTIC_EMIT"}


def floors_check(worlds: list[dict]) -> dict:
    chunk_sets = {tuple(sorted(tuple(c) for c in w["chunks"])) for w in worlds}
    shapes = {(len(w["chunks"]), tuple(sorted(len(c) for c in w["chunks"])),
               w["min_builder_length"],
               tuple(sorted(round(v, 4) for v in w["part_fractions"].values())))
              for w in worlds}
    return {"worlds_n": len(worlds), "unique_chunk_sets": len(chunk_sets),
            "distinct_shapes": len(shapes),
            "worlds_floor_met": len(worlds) >= 6,
            "shapes_floor_met": len(shapes) >= 2,
            "verdict": "FLOORS_MET" if (len(worlds) >= 6 and len(shapes) >= 2)
            else "AUTHOR_PACKAGE_BELOW_FLOORS"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--authored-dir", required=True, help="verbatim authored package copy")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260911)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo, adir, outdir = Path(a.repo), Path(a.authored_dir), Path(a.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    artifacts = sorted(p for p in adir.rglob("*") if p.is_file())

    tax = taxonomy_scan(repo, artifacts)
    emit = adir / "emit_worlds.py"
    guard = static_guard(emit) if emit.is_file() else {"verdict": "MISSING_EMITTER"}
    det = determinism_double_run(emit) if guard["verdict"] == "ACCEPT" else {
        "verdict": "SKIPPED_GUARD_REJECTED"}
    worlds_path = adir / "worlds.jsonl"

    worlds = []
    if worlds_path.is_file():
        worlds = [C.validate_world(w, i) for i, w in
                  enumerate(C.load_worlds_interface_only(worlds_path))]
    floors = floors_check(worlds)

    compiled, gsurf_files = [], []
    if tax["verdict"] == "CLEAN" and guard["verdict"] == "ACCEPT" \
       and det["verdict"] == "DETERMINISTIC" and floors["verdict"] == "FLOORS_MET":
        for i, w in enumerate(worlds):
            eco = C.compile_world(_load_methods(repo), w, a.seed + i)
            eco["bound_sources"] = {
                "methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
                "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip(),
                "worlds_jsonl": sha256_file(worlds_path)}
            p = outdir / f"M2P2_WORLD_{w['world_id']}.json"
            p.write_text(json.dumps(eco, indent=1, sort_keys=True))
            compiled.append(p)
    viable = []
    for p in compiled:
        eco = json.loads(p.read_text())
        if eco["viability"]["viable"]:
            viable.append(p)

    gsurf = []
    if viable:
        for p in viable:
            g = outdir / f"M2P2_GSURF_{json.loads(p.read_text())['world_id']}.json"
            r = subprocess.run([sys.executable, str(HERE / "m2p2_gsurf.py"),
                                "--repo", str(repo), "--world", str(p),
                                "--out", str(g), "--seed", str(a.seed)],
                               capture_output=True, text=True)
            gsurf.append({"file": str(g), "rc": r.returncode,
                          "stderr_tail": r.stderr[-300:] if r.returncode else None})

    gsurf_verdicts = []
    for g in gsurf:
        if g["rc"] == 0:
            gsurf_verdicts.append(json.loads(Path(g["file"]).read_text())["gsurf"]["verdict"])

    n_viable = len(viable)
    n_derivable = gsurf_verdicts.count("SURFACE_DERIVABLE")
    n_testable = n_viable - n_derivable
    gsurf_failed = [g for g in gsurf if g["rc"] != 0]
    if gsurf_failed:
        stage2 = "ASSAY_DEFECT_GSURF_RUN_FAILURE"
    elif tax["verdict"] != "CLEAN":
        stage2 = "AUTHORSHIP_CONTAMINATED"
    elif guard["verdict"] == "REJECTED_CANNOT_CHECK" or guard["verdict"] == "MISSING_EMITTER":
        stage2 = "CANNOT_CHECK_EMITTER_REJECTED"
    elif det["verdict"] != "DETERMINISTIC":
        stage2 = "ASSAY_DEFECT_NONDETERMINISTIC_EMIT"
    elif floors["verdict"] != "FLOORS_MET":
        stage2 = "AUTHOR_PACKAGE_BELOW_FLOORS"
    elif n_viable == 0:
        stage2 = "CANNOT_CHECK_TOO_FEW_VIABLE_WORLDS"
    elif n_testable == 0:
        stage2 = "SURFACE_DERIVABLE"          # every viable world is surface-derivable
    elif n_testable < 4:
        stage2 = "CANNOT_CHECK_TOO_FEW_VIABLE_WORLDS"
    else:
        stage2 = "ENTRY_GATES_PASS"

    receipt = {
        "schema": SCHEMA, "lane": LANE, "owner_issue": 165, "hardening_parent": 323,
        "status": "STAGE2_ENTRY_GATES_NOT_A_SCORED_RUN",
        "authored_dir": str(adir),
        "authored_files": {str(p): sha256_file(p) for p in artifacts},
        "taxonomy": tax, "static_guard": guard, "determinism": det, "floors": floors,
        "compiled_worlds": [str(p) for p in compiled],
        "viable_worlds": [str(p) for p in viable],
        "gsurf_runs": gsurf,
        "gsurf_verdicts": gsurf_verdicts,
        "worlds_viable": n_viable,
        "worlds_surface_derivable": n_derivable,
        "worlds_testable": n_testable,
        "stage2_verdict": stage2,
        "next": "stage 3 (scored arm set) may run ONLY if stage2_verdict == "
                "ENTRY_GATES_PASS, and runs on the testable worlds only; "
                "surface-derivable worlds are retained and reported per-world",
        "host": {"hostname": platform.node(), "python": platform.python_version()},
        "timing_seconds": round(time.perf_counter() - t0, 2),
    }
    (outdir / "M2P2_STAGE2_RECEIPT.json").write_text(
        json.dumps(receipt, indent=1, sort_keys=True))
    print(json.dumps({"stage2_verdict": stage2,
                      "viable_worlds": len(viable),
                      "gsurf_verdicts": gsurf_verdicts,
                      "timing": receipt["timing_seconds"]}, indent=1))
    return 0


_M = None
def _load_methods(repo: Path):
    global _M
    if _M is None:
        sys.path.insert(0, str(repo / "src"))
        import ocm.learning.methods as M
        _M = M
    return _M


if __name__ == "__main__":
    raise SystemExit(main())
