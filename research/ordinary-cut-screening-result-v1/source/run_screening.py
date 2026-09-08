"""Gated fresh process entry; source qualification does not authorize execution."""
from pathlib import Path
import hashlib,json,os,sys,time
ROOT=Path(__file__).resolve().parent
def identity(path):
 raw=Path(path).read_bytes();return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def main(request_path,output):
 started=time.perf_counter()
 raw=request_path.read_bytes();request_id={"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
 request=json.loads(raw)
 if request.get("schema")!="ordinary.retained-screening-request.v1":raise ValueError("screening request schema")
 if request.get("gate_path") is None:raise ValueError("missing root screening gate")
 gate_path=Path(request["gate_path"]);gate_id=identity(gate_path);gate=json.loads(gate_path.read_bytes())
 if gate.get("authorization")!="ROOT_RETAINED_SCREENING_GATE" or gate.get("request")!=request_id:
  raise ValueError("root screening authorization")
 if (request["max_token_states"],request["max_wall_s"],request["syntax_token_limit"],
     request["syntax_proof_limit"],request["P1_count"],request["proposal_occurrences"])!=(2000000,60,512,4096,4323,76):
  raise ValueError("registered unchanged bounds/population")
 pins=request["sources"]
 for name,pin in pins.items():
  if identity(ROOT/name)!=pin:raise ValueError("source freeze")
 runtime=request["runtime"]
 for name,pin in runtime["files"].items():
  if identity(Path(runtime["path"])/name)!=pin:raise ValueError("Lark runtime")
 if output.exists():raise ValueError("create-only output")
 output.mkdir()
 sys.path[:0]=[str(ROOT/"source"),runtime["path"]]
 from retained_inputs import read_bound,validate,write
 from screen_work import Work
 from syntax_adapter import SyntaxPool
 from screen import screen
 result={"schema":"ordinary.retained-screening-result.v1","terminal":"RUNNING","pid":os.getpid(),
  "cwd":os.getcwd(),"request":request_id,"native_calls":0,"new_native_admissions":0,"rows":[]}
 work=Work(request["max_token_states"],request["max_wall_s"],started);pool=None
 try:
  previous=read_bound(request["inputs"]["previous_result"])
  contracts=read_bound(request["inputs"]["P1_contracts"])
  rows=validate(previous,contracts,request["inputs"]["P1_contracts"],4323,76)
  result["previous_costs"]={"driver_wall_s":previous["wall_s"],"work":previous["work"],
   "outer_process":read_bound(request["inputs"]["previous_outer_process"]),
   "caller_process":read_bound(request["inputs"]["previous_caller_process"]),
   "scope":"Earlier disjoint attempt retained; nested intervals must not be summed as independent totals."}
  result["inputs"]=request["inputs"];result["P1_count"]=len(contracts);result["occurrence_count"]=len(rows)
  pool=SyntaxPool(contracts,work)
  for row in rows:
   record={k:v for k,v in row.items() if k!="body"}
   record["screen"]=screen(row["body"],pool,work)
   result["rows"].append(record)
   write(output/("SCREEN-"+str(row["occurrence_index"])+".json"),record)
  result["terminal"]="ALL_RETAINED_SCREENING_OCCURRENCES_RECORDED"
 except BaseException as exc:
  result.update(terminal="SCREENING_FAILED",error={"type":type(exc).__name__,"message":str(exc)})
 finally:
  result.update(work=work.snapshot(),contexts=pool.report() if pool else [],
                measured_driver_wall_s=time.perf_counter()-started)
  try:
   result["inputs_unchanged"]=all(identity(pin["path"])=={k:pin[k] for k in ("bytes","sha256")} for pin in request["inputs"].values())
   result["sources_unchanged"]=all(identity(ROOT/n)==p for n,p in pins.items())
   result["runtime_unchanged"]=all(identity(Path(runtime["path"])/n)==p for n,p in runtime["files"].items())
   result["request_unchanged"]=identity(request_path)==request_id and identity(gate_path)==gate_id
  except BaseException as exc:
   result.update(inputs_unchanged=False,sources_unchanged=False,runtime_unchanged=False,request_unchanged=False,
                 custody_error=type(exc).__name__+": "+str(exc))
  result["imported_modules"]={n:str(Path(m.__file__).resolve()) for n,m in sorted(sys.modules.items()) if getattr(m,"__file__",None)}
  write(output/"RESULT.json",result)
 return 0 if result["terminal"]=="ALL_RETAINED_SCREENING_OCCURRENCES_RECORDED" and all(
  result[k] for k in ("inputs_unchanged","sources_unchanged","runtime_unchanged","request_unchanged")) else 1
if __name__=="__main__":raise SystemExit(main(Path(sys.argv[1]),Path(sys.argv[2])))
