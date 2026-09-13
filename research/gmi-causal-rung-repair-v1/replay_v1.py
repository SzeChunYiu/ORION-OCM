from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from custody_v1 import replay
if __name__=='__main__': sys.stdout.buffer.write(replay())
