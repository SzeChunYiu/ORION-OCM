"""Isolated standalone full payload replay; no output projection."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from custody_v1 import replay

if __name__=='__main__':sys.stdout.buffer.write(replay())
