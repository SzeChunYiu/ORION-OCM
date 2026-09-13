"""Portable isolated entrypoint; complete original payload retained."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from custody_v1 import replay

if __name__ == "__main__":
    sys.stdout.buffer.write(replay())
