"""One artifact relocation/custody check; external graders only, never actors."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

PACKET=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    dest=Path(sys.argv[1]).resolve();dest.mkdir(parents=True,exist_ok=False)
    source_manifest=json.loads((PACKET/"raw/attempt-2/source/MANIFEST.json").read_text())
    denied=["/home/billy/orion-director-work/20260906/exact-sparse-trial-20260906",
            "/home/billy/orion-director-work/20260906/g1-current-context-20260906",
            "/home/billy/orion-director-work/20260906/g1-current-context-v2-20260906",
            "/home/billy/orion-director-work/20260906/ocm-exact-sparse"]
    guard=dest/"guard.py"
    guard.write_text("""import os,runpy,sys
from pathlib import Path
denied=__import__('json').loads(sys.argv[1]);script=sys.argv[2];args=sys.argv[3:]
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
        p=str(Path(os.fsdecode(args[0])).resolve())
        if any(p==root or p.startswith(root+'/') for root in denied):raise PermissionError('ORIGINAL_PATH_READ_REFUSED:'+p)
sys.addaudithook(audit)
try:open(denied[0]+'/MANIFEST.json')
except PermissionError:print('AUDIT_ORIGINAL_PATH_BLOCKED',flush=True)
else:raise RuntimeError('audit negative control did not refuse')
sys.path.insert(0,str(Path(script).parent));sys.argv=[script]+args
runpy.run_path(script,run_name='__main__')
""")
    env=dict(os.environ);env.pop("PYTHONPATH",None);env["PYTHONDONTWRITEBYTECODE"]="1"
    reports=[]
    def run(label,source,capture,manifest_sha,expected_exit):
        output=dest/(label+".grade.json")
        argv=[sys.executable,str(guard),json.dumps(denied),str(source/"trial_grade.py"),
              "--capture",str(capture),"--manifest-sha256",manifest_sha,"--output",str(output)]
        start=time.monotonic()
        with (dest/(label+".stdout")).open("x") as out,(dest/(label+".stderr")).open("x") as err:
            child=subprocess.Popen(argv,cwd=dest,env=env,stdout=out,stderr=err);status=child.wait()
        elapsed=time.monotonic()-start
        assert status==expected_exit,(label,status)
        result=json.loads(output.read_text())
        reports.append({"label":label,"command":argv,"exit_code":status,"wall_seconds":elapsed,"pid":child.pid,
                        "pid_absent":not Path("/proc",str(child.pid)).exists(),"grade_sha256":sha(output),
                        "stdout_sha256":sha(dest/(label+".stdout")),"stderr_sha256":sha(dest/(label+".stderr"))})
        return result
    for i,code in ((1,2),(2,0)):
        incoming=PACKET/"raw"/f"attempt-{i}";target=dest/f"attempt-{i}"
        shutil.copytree(incoming,target)
        result=run(f"attempt-{i}",target/"source",target/"capture",sha(target/"source/MANIFEST.json"),code)
        assert result==json.loads((incoming/"grade.json").read_text())
    altered=dest/"attempt-2/capture/case-00/call-0.json"
    raw=json.loads(altered.read_text());values=raw["result"]["vectors"][0]["values"];values[next(iter(values))]="3/4"
    altered.write_text(json.dumps(raw))
    result=run("changed-raw-refusal",dest/"attempt-2/source",dest/"attempt-2/capture",
               sha(dest/"attempt-2/source/MANIFEST.json"),2)
    assert result["functional_terminal"]=="CANNOT_CHECK" and "CAPTURE_CUSTODY" in result["error"]
    record={"scope":"artifact relocation and external semantic regrade only; no actor/model/solver/performance run",
            "status":"PASS","raw_original_paths_open_blocked":denied,"runs":reports}
    (dest/"RECEIPT.json").write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print(json.dumps(record,sort_keys=True))
if __name__=="__main__":main()
