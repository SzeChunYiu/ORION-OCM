"""Retained population/custody checks only; no syntax, alias or native validation."""
from pathlib import Path
import hashlib,json
def identity(raw):return {"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
def read_bound(pin):
 raw=Path(pin["path"]).read_bytes()
 if identity(raw)!={k:pin[k] for k in ("bytes","sha256")}:raise ValueError("bound prior input")
 return json.loads(raw)
def expected_occurrences(previous):
 rows=[]
 for ri,root in enumerate(previous["roots"]):
  for ci,cut in enumerate(root.get("cuts",[])):
   if cut["status"]=="CUT_PROPOSAL":
    body=json.dumps(cut["body"],sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    rows.append({"occurrence_index":len(rows),"root_index":ri,"root_ordinal":root["ordinal"],
     "root_label":root["label"],"cut_index":ci,"canonical_id":cut["canonical_id"],
     "body_sha256":hashlib.sha256(body).hexdigest()})
 return rows
def imports_ok(imports,request,root):
 expected={"__main__":str(root/"run_screening.py")}
 expected.update({Path(n).stem:str(root/n) for n in request["sources"] if n.startswith("source/")})
 if any(imports.get(n)!=p for n,p in expected.items()):return False
 allowed=set(expected.values())|{str(Path(request["runtime"]["path"])/n) for n in request["runtime"]["files"]}
 stdlib=Path(request["python"]["path"]).parent.parent/"lib/python3.11"
 for path in imports.values():
  p=Path(path)
  if path not in allowed and not p.is_relative_to(stdlib):return False
 return imports.get("lark")==str(Path(request["runtime"]["path"])/"lark/__init__.py")
def inspect_outputs(folder,pid,request_pin,request,root):
 entries=list(folder.iterdir()) if folder.exists() else []
 raw={p.name:p.read_bytes() for p in entries if p.is_file() and not p.is_symlink()}
 report={"files":{n:identity(v) for n,v in raw.items()},"entries":[p.name for p in entries],
  "population_ok":False,"completed_contract":False,"errors":[],"status_counts":{}}
 try:
  if set(raw)!={p.name for p in entries}:raise ValueError("nonregular output")
  if "RESULT.json" not in raw:raise ValueError("missing RESULT; partial files retained")
  result=json.loads(raw["RESULT.json"]);report["recorded_terminal"]=result.get("terminal")
  previous=read_bound(request["inputs"]["previous_result"])
  contracts=read_bound(request["inputs"]["P1_contracts"])
  if previous["P1_contracts"]!={k:request["inputs"]["P1_contracts"][k] for k in ("bytes","sha256")}:
   raise ValueError("exact original full P1")
  if len(contracts)!=request["P1_count"] or len({x["label"] for x in contracts})!=len(contracts):
   raise ValueError("full declared P1 population")
  expected=expected_occurrences(previous)
  if len(expected)!=request["proposal_occurrences"]:raise ValueError("bound occurrence population")
  rows=result["rows"]
  if type(rows) is not list or len(rows)>len(expected):raise ValueError("recorded rows")
  for row,reference in zip(rows,expected):
   if {k:v for k,v in row.items() if k!="screen"}!=reference:raise ValueError("ordered occurrence identity")
   screen=row["screen"];status=screen["status"]
   if screen.get("native_acceptance") is not False or screen.get("new_native_admissions")!=0:
    raise ValueError("native scope")
   if screen.get("P1_total")!=len(contracts) or type(screen.get("P1_visited")) is not int or not 0<=screen["P1_visited"]<=len(contracts):
    raise ValueError("screen P1 counts")
   if status not in {"ALIAS_FOUND_PROOF_READY","SCREENED_NEGATIVE_IN_DOMAIN","UNKNOWN"}:
    raise ValueError("screen disposition")
   if status=="UNKNOWN" and screen.get("coverage_complete") is not False:raise ValueError("UNKNOWN coverage")
   if status=="SCREENED_NEGATIVE_IN_DOMAIN" and not (
       screen.get("coverage_complete") is True and screen.get("grammar_coverage_complete") is True and screen["P1_visited"]==len(contracts)):
    raise ValueError("negative coverage")
   if status=="ALIAS_FOUND_PROOF_READY" and not screen.get("aliases"):raise ValueError("positive witness absent")
   report["status_counts"][status]=report["status_counts"].get(status,0)+1
  emitted=[]
  for name in raw:
   if name=="RESULT.json":continue
   if not name.startswith("SCREEN-") or not name.endswith(".json"):raise ValueError("unexpected output")
   number=int(name[7:-5])
   if name!="SCREEN-"+str(number)+".json" or number<0 or number>=len(rows):raise ValueError("emitted row index")
   if json.loads(raw[name])!=rows[number]:raise ValueError("SCREEN differs from RESULT")
   emitted.append(number)
  if sorted(emitted)!=list(range(len(emitted))):raise ValueError("emitted prefix")
  report.update(recorded_rows=len(rows),emitted_rows=len(emitted),missing_emitted_rows=list(range(len(emitted),len(rows))),
                not_recorded_occurrences=list(range(len(rows),len(expected))),population_ok=True)
  costs=result.get("previous_costs",{})
  cost_match=(costs.get("driver_wall_s")==previous["wall_s"] and costs.get("work")==previous["work"]
   and costs.get("outer_process")==read_bound(request["inputs"]["previous_outer_process"])
   and costs.get("caller_process")==read_bound(request["inputs"]["previous_caller_process"]))
  prior_screen=read_bound(request["inputs"]["prior_screen_result"])
  prior_costs=result.get("prior_screen_costs",{})
  screen_cost_match=(prior_costs.get("driver_wall_s")==prior_screen["measured_driver_wall_s"]
   and prior_costs.get("work")==prior_screen["work"] and prior_costs.get("contexts")==prior_screen["contexts"]
   and prior_costs.get("outer_process")==read_bound(request["inputs"]["prior_screen_outer_process"])
   and prior_costs.get("caller_process")==read_bound(request["inputs"]["prior_screen_caller_process"]))
  report["prior_screen_costs_preserved"]=screen_cost_match
  contexts=result.get("contexts")
  cache_reports=(type(contexts) is list and all(type(c) is dict and (c.get("error") is not None or
   (type(c.get("syntax_cache")) is dict and c["syntax_cache"].get("primitive")=="functools._lru_cache_wrapper"
    and type(c["syntax_cache"].get("cache_info")) is dict and type(c["syntax_cache"].get("namespace")) is list))
   for c in contexts))
  report["cache_reports_present"]=cache_reports
  imported=imports_ok(result.get("imported_modules",{}),request,root)
  report["declared_import_paths_ok"]=imported;report["previous_costs_preserved"]=cost_match
  report["completed_contract"]=(result.get("schema")=="ordinary.retained-screening-result.v1"
   and result.get("terminal")=="ALL_RETAINED_SCREENING_OCCURRENCES_RECORDED"
   and len(rows)==len(expected)==len(emitted) and type(result.get("pid")) is int and result["pid"]==pid
   and result.get("request")==request_pin and result.get("cwd")==str(root)
   and result.get("inputs")==request["inputs"] and result.get("P1_count")==len(contracts)
   and result.get("occurrence_count")==len(expected) and result.get("native_calls")==0
   and result.get("new_native_admissions")==0 and imported and cost_match and screen_cost_match and cache_reports
   and result.get("syntax_method")==request.get("syntax_method")=="functools.cache.completed-syntax-results.v1"
   and all(result.get(k) is True for k in ("inputs_unchanged","sources_unchanged","runtime_unchanged","request_unchanged")))
 except (OSError,ValueError,KeyError,TypeError,IndexError) as error:
  report["errors"].append(type(error).__name__+": "+str(error))
 return report
