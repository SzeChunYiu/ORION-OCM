"""One cold grammar per exact canonical parameter descriptor; no syntax-result cache."""
import copy,json,time
from syntax_engine import SyntaxEngine,SyntaxUnknown
class SyntaxPool:
    def __init__(self,contracts,work):
        self.contracts=copy.deepcopy(contracts);self.work=work;self.contexts={}
        labels=[r["label"] for r in self.contracts]
        if len(set(labels))!=len(labels):raise SyntaxUnknown("duplicate P1 labels")
    def context(self,parameters):
        key=json.dumps(parameters,sort_keys=True,separators=(",",":"),allow_nan=False)
        self.work.add("context_requests")
        if key not in self.contexts:
            self.work.checkpoint()
            self.work.add("grammar_construction_attempts")
            started=time.perf_counter()
            entry={"parameters":copy.deepcopy(parameters),"engine":None,"error":None}
            self.contexts[key]=entry
            try:
                entry["engine"]=SyntaxEngine(self.contracts,parameters)
                self.work.add("grammar_constructions_completed")
                for name in ("grammar_contracts_read","syntax_contracts","compiled_syntax_contracts"):
                    self.work.add(name,entry["engine"].work[name])
                self.work.checkpoint()
            except SyntaxUnknown as exc:
                entry["error"]=str(exc)
            finally:
                self.work.add("grammar_construction_wall_s",time.perf_counter()-started)
        entry=self.contexts[key]
        if entry["error"] is not None:raise SyntaxUnknown(entry["error"])
        return Context(entry["engine"],self.work)
    def report(self):
        return [{"parameters":v["parameters"],"error":v["error"],
                 "grammar_coverage_complete":bool(v["engine"] and not v["engine"].compiled["unsupported"]),
                 "unsupported_contracts":v["engine"].compiled["unsupported"] if v["engine"] else None,
                 "engine_work":dict(v["engine"].work) if v["engine"] else None}
                for v in self.contexts.values()]
class Context:
    def __init__(self,engine,work):self.engine=engine;self.work=work
    def prove(self,wanted,tokens):
        self.work.add("syntax_requests")
        before=dict(self.engine.work)
        result=self.engine.prove(wanted,tokens,self.work.checkpoint)
        for key in ("parse_calls","input_tokens","emitted_proof_labels"):
            self.work.add(key,self.engine.work[key]-before[key])
        self.work.add("parse_emit_wall_s",result["parse_emit_wall_s"])
        self.work.add("syntax_status_"+result["status"])
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
