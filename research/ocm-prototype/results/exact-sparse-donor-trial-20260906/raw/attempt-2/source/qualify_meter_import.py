"""Import-only qualification of the actual meter; never load, bind or call a consumer."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback

def main():
    p=argparse.ArgumentParser();p.add_argument("--context",type=Path,required=True);a=p.parse_args()
    root=a.context.resolve();sys.path[:0]=[str(root/"source/src"),str(root/"source/research/ocm-prototype")]
    events=[];record={"scope":"ACTUAL_INVOCATION_METER_ENTER_EXIT_ONLY; no loader/bind/SV/model/backend call","context":str(root)}
    try:
        import clia_process
        from clia_reuse_apply import CompiledProgram
        from clia_reuse_study_common import InvocationMeter
        before=(clia_process.invoke,CompiledProgram.apply)
        with InvocationMeter(events):
            assert clia_process.invoke is not before[0] and CompiledProgram.apply is not before[1]
        assert (clia_process.invoke,CompiledProgram.apply)==before and not events
        from vendor import conll18_ud_eval
        path=Path(conll18_ud_eval.__file__).resolve()
        assert path==root/"source/research/ocm-prototype/vendor/conll18_ud_eval.py"
        record.update(status="PASS",hooks_restored=True,
                      vendor={"module":"vendor.conll18_ud_eval","path":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
        code=0
    except BaseException as exc:
        traceback.print_exc();record.update(status="ERROR",type=type(exc).__name__,message=str(exc));code=2
    record["events"]=events;print(json.dumps(record,sort_keys=True),flush=True);return code

if __name__=="__main__":raise SystemExit(main())
