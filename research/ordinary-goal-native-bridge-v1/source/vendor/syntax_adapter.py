"""Detached immutable P1 namespace, one grammar and exact-result cache per context."""
import copy,hashlib,json,time
from types import MappingProxyType
from syntax_engine import SyntaxEngine,SyntaxUnknown
from syntax_memo import Context
def readonly(value):
    if type(value) is dict:return MappingProxyType({k:readonly(v) for k,v in value.items()})
    if type(value) is list:return tuple(readonly(x) for x in value)
    return value
class SyntaxPool:
    def __init__(self,contracts,work):
        started=time.perf_counter()
        self.work=work;self.contexts={}
        self._library=json.dumps(contracts,sort_keys=True,separators=(",",":"),allow_nan=False)
        decoded=json.loads(self._library)
        labels=[r["label"] for r in decoded]
        if len(set(labels))!=len(labels):raise SyntaxUnknown("duplicate P1 labels")
        self._contracts=readonly(decoded)
        self.library_sha256=hashlib.sha256(self._library.encode()).hexdigest()
        work.add("cache_library_snapshot_bytes",len(self._library.encode()))
        work.add("cache_library_preparation_wall_s",time.perf_counter()-started)
    @property
    def contracts(self):return self._contracts
    def context(self,parameters):
        key=json.dumps(parameters,sort_keys=True,separators=(",",":"),allow_nan=False)
        self.work.add("context_requests")
        if key not in self.contexts:
            self.work.checkpoint()
            self.work.add("grammar_construction_attempts")
            started=time.perf_counter()
            entry={"parameters":json.loads(key),"engine":None,"context":None,"error":None}
            self.contexts[key]=entry
            try:
                entry["engine"]=SyntaxEngine(json.loads(self._library),json.loads(key))
                self.work.add("grammar_constructions_completed")
                for name in ("grammar_contracts_read","syntax_contracts","compiled_syntax_contracts"):
                    self.work.add(name,entry["engine"].work[name])
                entry["context"]=Context(entry["engine"],self.work,(self.library_sha256,key))
                self.work.add("cache_context_key_bytes",len(key.encode()))
                self.work.checkpoint()
            except SyntaxUnknown as exc:
                entry["error"]=str(exc)
            finally:
                self.work.add("grammar_construction_wall_s",time.perf_counter()-started)
        entry=self.contexts[key]
        if entry["error"] is not None:raise SyntaxUnknown(entry["error"])
        return entry["context"]
    def report(self):
        return [{"parameters":copy.deepcopy(v["parameters"]),"error":v["error"],
                 "grammar_coverage_complete":bool(v["engine"] and not v["engine"].compiled["unsupported"]),
                 "unsupported_contracts":copy.deepcopy(v["engine"].compiled["unsupported"]) if v["engine"] else None,
                 "engine_work":dict(v["engine"].work) if v["engine"] else None,
                 "syntax_cache":v["context"].report() if v["context"] else None}
                for v in self.contexts.values()]
