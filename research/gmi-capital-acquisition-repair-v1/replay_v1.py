from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
from custody_v1 import replay

if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True, indent=2))
