"""Run byte-exact whole-unit replay; all outputs stay outside the frozen unit."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from custody_v1 import replay
if __name__ == '__main__':
    print(json.dumps(replay(Path(__file__).resolve().parent),indent=2,sort_keys=True))
