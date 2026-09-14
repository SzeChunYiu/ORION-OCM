from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
from experiment_v1 import run as experiment
from cost_oracle_v1 import check as costs
from certificate_v1 import certify
from record_audit_v1 import run as records
from countercontrols_v1 import run as controls


def run():
    result = experiment()
    return {"schema": "GMI_CAPITAL_ACQUISITION_REPAIR_V1", "status": "PASS",
            "experiment": result, "certificate": certify(result),
            "independent_cost_oracle": costs(result),
            "original_record_audit": records(), "countercontrols": controls()}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
