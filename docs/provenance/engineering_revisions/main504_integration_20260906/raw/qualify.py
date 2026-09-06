"""Post-merge engineering verification; no prospective study execution."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
BASE = Path("/home/billy/orion-director-work/20260906")
ROOT = BASE / "ocm-clia-reuse-study"
OUT = BASE / "clia-reuse-main504-integration"
sys.path.insert(0, str(ROOT / "tools"))
import engineering_receipts as E

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name, value):
    with (OUT / name).open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True); f.write("\n")

def run(label, argv, env):
    started = time.monotonic()
    with (OUT / (label + ".stdout")).open("xb") as stdout, (OUT / (label + ".stderr")).open("xb") as stderr:
        p = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
        code = p.wait()
    value = {"label": label, "argv": argv, "pid": p.pid, "exit_code": code,
             "wall_seconds": time.monotonic() - started}
    save(label + ".process.json", value)
    print(json.dumps(value), flush=True)
    if code: raise RuntimeError("qualification failed: " + label)
    return value

before = E.V4.source_inventory(ROOT)
assert E.source_id(before) == "c7cdd3a10a8274083e870c3ee9394b83d5bc49800743bee0928410e8da353963"
selected = E.verify(ROOT)
env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
executions = []
save("verification-start.json", {"started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "current": selected, "scope": "Engineering verification only; no frozen actor rerun"})
for name in ["m" + str(n) + "_receipt" for n in range(1, 13)] + ["m12_paired_v5_receipt"]:
    executions.append(run(name, [sys.executable, "tools/" + name + ".py", "--verify"], env))
research_env = dict(os.environ)
research_env.pop("PYTHONPATH", None)
research_env.pop("PYTEST_ADDOPTS", None)
dev = BASE / "language-g1-audit/data/en_ewt-ud-dev.conllu"
research_env["OCM_G1_DEV_PATH"] = str(dev)
argv = ["/usr/bin/timeout", "--kill-after=15s", "300s", str(BASE / "g1-env/bin/python"), "-m", "pytest",
        "research/ocm-n1", "research/ocm-prototype", "-q", "--ignore=research/ocm-prototype/results",
        "--ignore-glob=research/ocm-prototype/test_hosted_*.py", "--basetemp=" + str(OUT / "research-unit"),
        "--junitxml=" + str(OUT / "research.xml")]
save("research-launch.json", {"argv": argv, "cwd": str(ROOT), "ambient_PYTHONPATH": "REMOVED",
     "dev_path": str(dev), "dev_sha256": sha(dev), "source_inventory": E.source_id(before)})
executions.append(run("research", argv, research_env))
suites = list(ET.parse(OUT / "research.xml").iter("testsuite"))
counts = {k: sum(int(s.attrib[k]) for s in suites) for k in ["tests", "errors", "failures", "skipped"]}
assert counts["tests"] and not any(counts[k] for k in ["errors", "failures", "skipped"])
assert before == E.V4.source_inventory(ROOT)
provenance = {}
for ref in ["7c02ffa0bca54b92be0e8bf92906147b7e7b754b", "504c320e6a8c9fa8a2e593ded0b4846ce073021b"]:
    records = subprocess.check_output(["/usr/bin/git", "ls-tree", "-rz", ref, "--", "docs/provenance"], cwd=ROOT)
    found = 0
    for raw in records.split(b"\0"):
        if not raw: continue
        info, path = raw.split(b"\t", 1); path = path.decode()
        if path == E.CURRENT: continue
        data = (ROOT / path).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert actual == info.split()[2].decode(), path
        found += 1
    provenance[ref] = {"unchanged_blobs": found}
captures = {}
for v in [1, 2, 3]:
    capture = BASE / ("clia-reuse-capture-v" + str(v))
    manifest = json.loads((capture / "capture-manifest.json").read_text())
    for path, expected in manifest["files"].items(): assert sha(capture / path) == expected, path
    captures[str(v)] = {"files": len(manifest["files"]), "seal_sha256": sha(capture / "capture-manifest.json")}
packet = ROOT / "research/ocm-prototype/results/clia-reuse-study-result-20260906"
for line in (packet / "SHA256SUMS").read_text().splitlines():
    expected, path = line.split("  ", 1); assert sha(packet / path) == expected, path
result = {"status": "ENGINEERING_REGRESSION_ONLY", "scientific_promotion": "NOT_ESTABLISHED",
          "source_id": E.source_id(before), "current": E.verify(ROOT), "executions": executions,
          "research_junit": counts, "preserved_provenance": provenance, "preserved_captures": captures,
          "prior_packet_inventory_sha256": sha(packet / "SHA256SUMS"),
          "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
save("verification.json", result)
print(json.dumps({"status": result["status"], "counts": counts, "source_id": result["source_id"]}), flush=True)
