from __future__ import annotations

import json
from score_v1 import build_result

if __name__ == "__main__":
    print(json.dumps(build_result(), sort_keys=True, separators=(",", ":")))
