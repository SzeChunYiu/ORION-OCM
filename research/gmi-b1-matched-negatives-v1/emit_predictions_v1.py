from __future__ import annotations

import json
from predict_v1 import build_predictions

if __name__ == "__main__":
    print(json.dumps(build_predictions(), sort_keys=True, separators=(",", ":")))
