"""AMENDMENT-3 cross-host replicate comparison (PDEV-9 receipt extension).

Compares each replicate claim row against the LUNARC frozen eval row of the
same candidate_id on the frozen vector (status, n, success, work,
persistent_bytes).  Pure measurement receipt: replicates NEVER enter
selection; this only documents cross-host cross-version agreement.

Usage: cross_host_compare.py RUN_ROOT
Writes RUN_ROOT/results/CROSS_HOST_REPLICATES.json
"""
import json
import platform
import sys
import time
from pathlib import Path

run_root = Path(sys.argv[1])
rep_dir = run_root / "replicates"
FIELDS = ("status", "n", "success", "work", "persistent_bytes")


def frozen_rows(gen, wave):
    d = run_root / "generations" / ("g%d" % gen) / "waves" / ("w%d" % wave) / "eval"
    out = {}
    for p in d.glob("*.json"):
        if p.name.endswith(".full.json"):
            continue
        row = json.loads(p.read_text())
        out[row["candidate_id"]] = row
    return out


report = {"schema": "pdev217.cross_host_replicates.v1",
          "amendment": "AMENDMENT-3",
          "hosts": {}, "written_unix": time.time()}
total_match = total_cmp = 0
for host_dir in sorted(p for p in rep_dir.iterdir() if p.is_dir()):
    host = host_dir.name
    host_stat = {"claims": [], "mismatches": []}
    for claim_path in sorted(host_dir.glob("claim_g*.json")):
        claim = json.loads(claim_path.read_text())
        frozen = frozen_rows(claim["generation"], claim["wave"])
        match = cmp_n = 0
        for row in claim["rows"]:
            cid = row["candidate_id"]
            base = frozen.get(cid)
            if base is None:
                host_stat["mismatches"].append(
                    {"candidate_id": cid, "reason": "not in frozen wave"})
                cmp_n += 1
                continue
            cmp_n += 1
            if all(row.get(f) == base.get(f) for f in FIELDS):
                match += 1
            else:
                host_stat["mismatches"].append({
                    "candidate_id": cid,
                    "frozen": {f: base.get(f) for f in FIELDS},
                    "replicate": {f: row.get(f) for f in FIELDS}})
        host_stat["claims"].append({
            "generation": claim["generation"], "wave": claim["wave"],
            "index_range": claim["index_range"],
            "rows": claim["row_count"],
            "vector_exactly_reproduced": match,
            "compared": cmp_n})
        total_match += match
        total_cmp += cmp_n
    report["hosts"][host] = host_stat

report["total_vector_exactly_reproduced"] = total_match
report["total_compared"] = total_cmp
report["verdict"] = ("ALL_REPRODUCED" if total_match == total_cmp and total_cmp
                     else "MISMATCH_PRESENT")
out = run_root / "results" / "CROSS_HOST_REPLICATES.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print("verdict=%s reproduced=%d/%d hosts=%s"
      % (report["verdict"], total_match, total_cmp,
         ",".join(sorted(report["hosts"]))))
