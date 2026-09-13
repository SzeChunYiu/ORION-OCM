"""Portable whole-payload replay."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody_v1 import replay
print(json.dumps(replay(), indent=2, sort_keys=True))
