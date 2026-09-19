from __future__ import annotations
import runpy,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
runpy.run_path(str(HERE/'check_ai1_ai8.py'),run_name='__main__')
