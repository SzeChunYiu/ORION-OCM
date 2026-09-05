#!/usr/bin/env python3
"""Rebuild the fourth-revision ENGINEERING replay for the current source inventory.

Under the runtime_revision_20260905_v4 custody regime (tools/runtime_revision_receipts_v4.py) every
change to src/, tests/, tools/ or pyproject.toml drifts the recorded source inventory, so the
successor receipts refuse until the two named validation gates (full suite, focused suite) have
been executed on the current code and their JUnit artifacts recorded.  This script runs exactly
the gate commands declared in REVISION_V4.json, records exit codes and artifact digests, and
writes ENGINEERING_REPLAY_V4.json with the engineering-only scope labels.  It never touches
historical receipts and claims no scientific result.  Run it on a compute host, never the Mac:

    python tools/rebuild_engineering_replay_v4.py            # runs the gates, writes the replay
    python tools/rebuild_engineering_replay_v4.py --no-run   # re-derive inventory/digests from existing artifacts
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime_revision_receipts_v4 as R  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str]) -> int:
    config = R.read_json(ROOT, R.CONFIG_PATH)
    executions, artifacts = [], {}
    for label, spec in config["validation_requirements"].items():
        path = ROOT / spec["artifact_path"]
        if "--no-run" not in argv:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.unlink()
            proc = subprocess.run(spec["argv"], cwd=ROOT)
            code = proc.returncode
        else:
            code = 0 if path.exists() else 1
        if not path.exists():
            print(f"gate {label}: artifact missing after execution ({spec['artifact_path']})")
            return 1
        artifacts[spec["artifact_path"]] = R.sha(ROOT, spec["artifact_path"])
        executions.append({"label": label, "argv": spec["argv"], "exit_code": code, "artifact_path": spec["artifact_path"]})
        print(f"gate {label}: exit {code}, artifact {artifacts[spec['artifact_path']][:12]}")
    if any(e["exit_code"] != 0 for e in executions):
        print("a validation gate failed; replay not written")
        return 1
    replay = {"schema": "ocm.engineering-replay.v4", "revision": R.REVISION, "status": "ENGINEERING_REGRESSION_ONLY", "protected_reevaluation": "NOT_RUN",
              "scientific_promotion": "NOT_ESTABLISHED", "independent_replication": "NOT_RUN", "current_source_inventory": R.source_inventory(ROOT),
              "executions": executions, "validation_artifacts": artifacts}
    out = ROOT / config["engineering_replay_path"]
    out.write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", out.relative_to(ROOT), "inventory files:", len(replay["current_source_inventory"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
