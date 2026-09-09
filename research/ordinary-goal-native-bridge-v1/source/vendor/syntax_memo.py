"""functools.cache over one immutable P1/context; UNKNOWN never becomes an entry."""
from functools import cache
import json,time
from syntax_engine import SyntaxUnknown
class Uncacheable(SyntaxUnknown):
    def __init__(self,result):self.result=result
class Context:
    def __init__(self,engine,work,namespace):
        self.engine=engine;self.work=work;self.namespace=namespace
        self._unsupported=json.dumps(engine.compiled["unsupported"],sort_keys=True,allow_nan=False)
        self._memo=cache(self._miss)
        self._last_parse_wall=0.0
        work.add("syntax_caches_constructed")
    def _miss(self,wanted,tokens):
        started=time.perf_counter();before=dict(self.engine.work)
        try:
            result=self.engine.prove(wanted,list(tokens),self.work.checkpoint)
            self._last_parse_wall=result["parse_emit_wall_s"]
            self.work.add("parse_emit_wall_s",result["parse_emit_wall_s"])
            status=result["status"]
            admissible=(status=="SYNTAX_PROVED" and result.get("structural_replay") is True
                        or status=="NOT_DERIVABLE_REGISTERED_GRAMMAR" and result["coverage_complete"] is True)
            if not admissible:raise Uncacheable(result)
            return (status,result["grammar_coverage_complete"],result["coverage_complete"],
                    tuple(result["proof"]) if result["proof"] is not None else None,
                    result.get("reason"),result.get("structural_replay"))
        finally:
            for key in ("parse_calls","input_tokens","emitted_proof_labels"):
                self.work.add(key,self.engine.work[key]-before[key])
            self.work.add("cache_compute_wall_s",time.perf_counter()-started)
    def _unknown(self,reason):
        return {"native_acceptance":False,"status":"UNKNOWN","proof":None,"coverage_complete":False,
                "grammar_coverage_complete":not self.engine.compiled["unsupported"],
                "unsupported_contracts":json.loads(self._unsupported),"reason":reason,"parse_emit_wall_s":self._last_parse_wall}
    def prove(self,wanted,tokens):
        started=time.perf_counter();info=self._memo.cache_info()
        compute_before=self.work.get("cache_compute_wall_s",0.0)
        self.work.add("syntax_requests");self._last_parse_wall=0.0
        lookup=False;packed=None
        try:
            self.work.checkpoint()
            if type(wanted) is not str or wanted not in ("wff","class","setvar") or type(tokens) is not list or not 0<len(tokens)<=512 or any(type(t) is not str for t in tokens):
                self.work.add("cache_input_bypasses")
                raise SyntaxUnknown("input outside registered type/token boundary")
            self.work.add("cache_lookup_key_tokens",len(tokens));lookup=True
            packed=self._memo(wanted,tuple(tokens))
            status,grammar,coverage,proof,reason,replayed=packed
            result={"native_acceptance":False,"status":status,"proof":list(proof) if proof is not None else None,
                    "grammar_coverage_complete":grammar,"coverage_complete":coverage,
                    "unsupported_contracts":json.loads(self._unsupported),"parse_emit_wall_s":self._last_parse_wall}
            if reason is not None:result["reason"]=reason
            if replayed is not None:result["structural_replay"]=replayed
            self.work.checkpoint()
        except Uncacheable as exc:
            result={**exc.result, "unsupported_contracts":json.loads(self._unsupported)}
            self.work.add("cache_uncacheable_results")
        except (SyntaxUnknown,ValueError,KeyError,TypeError,MemoryError) as exc:
            result=self._unknown(type(exc).__name__+": "+str(exc))
            self.work.add("cache_request_refusals")
        after=self._memo.cache_info()
        hits=after.hits-info.hits;misses=after.misses-info.misses;entries=after.currsize-info.currsize
        self.work.add("cache_hits",hits);self.work.add("cache_misses",misses)
        self.work.add("cache_entries",entries)
        if entries:
            self.work.add("cache_stored_key_tokens",len(tokens))
            self.work.add("cache_stored_proof_labels",len(packed[3]) if packed[3] is not None else 0)
        result["cache_hit"]=bool(hits);result["syntax_computation_performed"]=bool(misses)
        result["cache_lookup_performed"]=lookup
        if result["proof"] is not None:self.work.add("cache_returned_proof_labels",len(result["proof"]))
        self.work.add("syntax_status_"+result["status"])
        elapsed=time.perf_counter()-started
        self.work.add("cache_request_wall_s",elapsed)
        self.work.add("cache_management_wall_s",max(0.0,elapsed-(self.work.get("cache_compute_wall_s",0.0)-compute_before)))
        return result
    def checker(self,wanted,tokens):
        result=self.prove(wanted,tokens)
        if result["status"]=="SYNTAX_PROVED":return True
        if result["status"]=="NOT_DERIVABLE_REGISTERED_GRAMMAR":
            raise ValueError("not a member of registered syntax grammar")
        raise SyntaxUnknown(result.get("reason","syntax UNKNOWN"))
    def proof(self,wanted,tokens):
        result=self.prove(wanted,tokens)
        if result["status"]!="SYNTAX_PROVED":
            raise SyntaxUnknown("syntax proof: "+result.get("reason",result["status"]))
        return result["proof"]
    def report(self):
        return {"namespace":self.namespace,"primitive":type(self._memo).__module__+"."+type(self._memo).__name__,
                "cache_info":self._memo.cache_info()._asdict(),
                "scope":"Single-threaded finite attempt; entries retain immutable payloads until context release."}
