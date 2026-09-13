"""Full source-bound deterministic calculation output; no campaign execution."""
import json
import sys
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sources_v1 import verify_sources,sha
from historical_v1 import original_suite,old_controls,parent_readout
from successor_controls_v1 import run as successor_controls
from checks_v1 import witnesses,descent_census,cover_census,table_census,gate_census

def run(root=None):
    root=Path(root or Path(__file__).resolve().parent)
    sources=verify_sources(root)
    bindings=json.loads((root/"SOURCE_BINDINGS_V1.json").read_bytes())
    return dict(schema="LST_REPAIR_RECEIPT_V1",status="PASS",
                scope="CONDITIONAL_THEOREMS_AND_PINNED_STATIC_CALCULATIONS",
                sources=bindings,original_no_alarm=original_suite(sources),
                original_countercontrols=old_controls(sources),
                capital_parent_readout=parent_readout(sources),
                pr594=successor_controls(sources),
                constructive_witnesses=witnesses(),descent=descent_census(),
                covers=cover_census(),tables=table_census(),thresholds=gate_census())

def encode(value):
    if isinstance(value,Fraction):
        return str(value)
    raise TypeError(type(value).__name__)

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2,default=encode))
