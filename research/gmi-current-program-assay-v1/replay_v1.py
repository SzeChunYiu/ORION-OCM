"""Default is retained-evidence audit; --native explicitly reruns exposed controls."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evidence_v1 import encoded, replay

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--native"]):
        raise SystemExit("usage: replay_v1.py [--native]")
    sys.stdout.buffer.write(encoded(replay(native=bool(sys.argv[1:]))))
