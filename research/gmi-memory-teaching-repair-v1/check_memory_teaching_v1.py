"""Complete deterministic new-model/static-record payload; no old script execution."""
import json
import sys
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from memory_witnesses_v1 import run_memory
from teaching_witnesses_v1 import run_teaching
from retained_evidence_v1 import retained, boundary, rounded_difference
from sources_v1 import verify_sources, sha

def convert(x):
    if isinstance(x,F):
        return str(x)
    if isinstance(x,dict):
        return {str(k):convert(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):
        return [convert(v) for v in x]
    return x

def check(root=None):
    root=Path(root or Path(__file__).resolve().parent)
    sources=verify_sources(root)
    readout=retained(root)
    niche=readout["open_niche"]
    if niche["admitted"] != [["E_open4","compiled_search"],["E_open4","program_search"]]:
        raise ValueError("retained admission readout changed")
    if len(niche["search_top_including_ties"])!=8 or niche["minimum_search"]!=F(9062,10000):
        raise ValueError("retained score readout changed")
    lo,hi=rounded_difference(F(9688,10000),F(9271,10000))
    if not lo<F(1,24)<hi:
        raise ValueError("rounding boundary control")
    result=dict(schema="MEMORY_TEACHING_REPAIR_V1",status="PASS",
                source_blobs={kind+":"+path:sha(data) for (kind,path),data in sources.items()},
                memory=run_memory(),teaching=run_teaching(),retained=readout,
                boundaries=dict(exact_margin=F(1,24),baseline_boundary=F(23,24),
                                equality_not_excluded=not boundary(F(23,24)),
                                strict_above_excluded=boundary(F(23,24)+F(1,1000)),
                                rounded_difference_envelope=(lo,hi),
                                sample_max=F(9,10),compatible_extended_max=F(1),
                                nonattained_supremum=F(1,2)),
                scope="FINITE_EXECUTABLE_INTERFACES_AND_STATIC_RETAINED_RECORDS",
                old_native_or_protected_campaign_executions=0)
    return convert(result)

if __name__=="__main__":
    print(json.dumps(check(),sort_keys=True,indent=2))
