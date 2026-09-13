from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custody_v1 import replay

if __name__ == "__main__":
    if sys.argv[1:]:
        raise SystemExit("usage: replay_v1.py")
    sys.stdout.buffer.write(replay())
