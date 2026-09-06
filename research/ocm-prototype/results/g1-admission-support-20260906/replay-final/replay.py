from pathlib import Path
import sys,json,time,resource,hashlib
repo=Path(sys.argv[1]);state=Path(sys.argv[2]);sys.path.insert(0,str(repo/'research/ocm-prototype'));import g1_vessel as G
before={str(p.relative_to(state)):hashlib.sha256(p.read_bytes()).hexdigest() for p in state.rglob('*') if p.is_file()}
start=time.perf_counter();runtime=G.OCMRuntime(state,config=G.CONFIG);elapsed=time.perf_counter()-start
snapshot=runtime.state.snapshot(); chain=G.SV.__name__
from ocm.store.event import verify_chain
verified=verify_chain(runtime.events)
after={str(p.relative_to(state)):hashlib.sha256(p.read_bytes()).hexdigest() for p in state.rglob('*') if p.is_file()}
assert before==after
print(json.dumps({'snapshot':snapshot,'state_files_unchanged':True,'event_count':len(runtime.events),'chain':verified,'wall_reload_s':elapsed,'cpu_s':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,'source_identity':G.content_hash(G.identities())},sort_keys=True))
