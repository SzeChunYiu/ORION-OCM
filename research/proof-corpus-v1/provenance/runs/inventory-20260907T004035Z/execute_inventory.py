import datetime, json, resource, subprocess, sys, time
from pathlib import Path
root=Path("/home/billy/orion-director-work/20260907/ocm-proof-runtime/research/proof-corpus-v1")
run=root/"provenance/runs/inventory-20260907T004035Z"
launch=json.loads((run/"PRELAUNCH.json").read_text())
sys.path.insert(0,str(root))
from corpus_contract import digest, encoded, sha256
from corpus_receipt import code_inventory
assert digest(code_inventory())==launch["source_inventory_sha256"]
acquired=json.loads((run/"ACQUISITION.json").read_text())
assert acquired["terminal"]=="PINNED_BARE_SOURCE_ACQUIRED"
out=Path(launch["inventory_output"])
assert not out.exists()
(run/"AUDIT_LAUNCH.json").write_bytes(encoded({
"source_inventory_sha256":launch["source_inventory_sha256"],
"source_commit":launch["public_source_commit"],"source_tree":launch["public_source_tree"],
"source_repo":launch["public_source_local_path"],"command":launch["inventory_command"],
"started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
"acquisition_receipt_sha256":sha256((run/"ACQUISITION.json").read_bytes()),
"execution":"Exactly one inventory-only invocation; frozen source; no target selection or solver."}))
started=time.perf_counter()
child0=resource.getrusage(resource.RUSAGE_CHILDREN)
with (run/"AUDIT.stdout").open("xb") as stdout, (run/"AUDIT.stderr").open("xb") as stderr:
    result=subprocess.run(launch["inventory_command"],cwd=root,stdout=stdout,stderr=stderr)
elapsed=time.perf_counter()-started
child=resource.getrusage(resource.RUSAGE_CHILDREN)
report=json.loads((out/"REPORT.json").read_text()) if (out/"REPORT.json").exists() else None
verification_started=time.perf_counter()
valid={}
if report is not None:
    for name,expected in report["artifact_sha256"].items():
        valid[name]=sha256((out/name).read_bytes())==expected
unchanged=digest(code_inventory())==launch["source_inventory_sha256"]
sizes={str(p.relative_to(out)):p.stat().st_size for p in out.rglob("*") if p.is_file()} if out.exists() else {}
envelope={"schema":"OCM_CORPUS_FULL_PROCESS_V1","exit_code":result.returncode,
"wall_seconds":elapsed,"child_cpu_seconds":child.ru_utime+child.ru_stime-child0.ru_utime-child0.ru_stime,
"finished_child_lifetime_max_rss_bytes":child.ru_maxrss*1024,
"process_tree_peak_rss_bytes":None,"cost_scope":"Entire inventory command, including initial imports and final REPORT serialization.",
"verification_wall_seconds":time.perf_counter()-verification_started,
"source_code_unchanged":unchanged,"artifact_bindings":valid,"raw_artifact_bytes":sizes,
"raw_artifact_total_bytes":sum(sizes.values()),"report_sha256":sha256((out/"REPORT.json").read_bytes()) if report else None,
"output_path":str(out),"terminal":report["terminal"] if report else "CANNOT_CHECK_NO_REPORT",
"rows_accounted":report["rows_accounted"] if report else None,
"inventory_resources":report["resources"] if report else None}
(run/"FULL_PROCESS.json").write_bytes(encoded(envelope))
print(json.dumps(envelope,indent=2),flush=True)
raise SystemExit(0 if report is not None and all(valid.values()) and unchanged else 4)
