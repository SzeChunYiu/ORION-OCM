"""Source-bound, deterministic static readout; imports no campaign code."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from records_v1 import analyze, load_scores, prose_comparison, require
from finite_controls_v1 import controls


def run():
    bindings = json.loads((HERE / "raw/SOURCE_BINDINGS_V1.json").read_text())
    for item in bindings["records"]:
        raw = (HERE / item["path"]).read_bytes()
        require(len(raw) == item["bytes"] and hashlib.sha256(raw).hexdigest() == item["sha256"],
                "source binding mismatch")
    data = load_scores()
    tip = HERE / "raw/tip"
    comparison = prose_comparison(data,
        (tip / "GMI_CAPABILITY_MAP_PROSPECTIVE_TEST_V1.md").read_text(),
        (tip / "GMI_ECOLOGY_REGISTRY_SAMPLING_BIAS_V1.md").read_text())
    return {"status": "PASS", "schema": "FreshEcologyEvidenceCorrectionV1",
            "claim_ceiling": "RETAINED_SUMMARY_ARITHMETIC_AND_FINITE_INFERENCE_CONTROLS",
            "source_tip": bindings["source_tip"], "source_blobs": len(bindings["records"]),
            "source_bindings_sha256": hashlib.sha256(
                (HERE / "raw/SOURCE_BINDINGS_V1.json").read_bytes()).hexdigest(),
            "record_audit": analyze(data), "source_comparison": comparison,
            "finite_controls": controls(data),
            "new_ecology_candidate_or_timing_executions": 0}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
