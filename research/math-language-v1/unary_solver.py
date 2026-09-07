"""Cached exact region parent with bound, immutable premise-only preparation."""
from dataclasses import dataclass
import hashlib
import json
from unary_contract import (COUNTERS, InputRefused, RESULT_SCHEMA, negate,
                            predicate_registry, task_digest, validate_task)


BINDING_COUNTERS=("nodes_checked","bytes_hashed","decode_input_bytes",
                  "task_validation_calls","task_digest_calls","json_parse_calls","json_encode_calls")


@dataclass(frozen=True)
class Prepared:
    task_bytes: bytes
    constraints: tuple
    allowed: int
    universals: tuple
    existentials: tuple
    base: tuple
    counters: tuple


def _freeze(cert):
    return ("model",tuple(cert["world"])) if cert["kind"]=="model" else (
        "unsat",cert["obligation"],tuple(cert["cover"]))


def _thaw(cert):
    return {"kind":"model","world":list(cert[1])} if cert[0]=="model" else {
        "kind":"unsat","obligation":cert[1],"cover":list(cert[2])}


class RegionSolver:
    """Only the most recently issued preparation can be reused on its issuing engine."""
    def __init__(self,predicates):
        self.predicates=predicate_registry(predicates)
        self.regions=1<<len(self.predicates);self.full=(1<<self.regions)-1
        self.cache={};self.counters={};self._active=None
        self.binding_work=dict.fromkeys(BINDING_COUNTERS,0)

    def _mask(self, expr):
        self.counters["expression_nodes"] += 1
        key = self._key(expr)
        if key in self.cache:
            self.counters["cache_hits"] += 1
            return self.cache[key]
        self.counters["cache_misses"] += 1
        if expr[0] == "pred":
            bit = self.predicates.index(expr[1])
            self.counters["predicate_region_tests"] += self.regions
            mask = sum(1 << region for region in range(self.regions) if region & (1 << bit))
        elif expr[0] == "not":
            mask = self.full ^ self._mask(expr[1])
            self.counters["mask_operations"] += 1
        else:
            a, b = self._mask(expr[1]), self._mask(expr[2])
            mask = a & b if expr[0] == "and" else a | b
            self.counters["mask_operations"] += 1
        self.cache[key] = mask
        return mask

    def _key(self, expr):
        self.counters["cache_key_nodes"] += 1
        return tuple(expr) if expr[0] == "pred" else (expr[0], *(self._key(x) for x in expr[1:]))

    def _constraint(self, statement):
        a, b = self._mask(statement["left"]), self._mask(statement["right"])
        if statement["kind"] in ("every", "not_every"):
            b = self.full ^ b
            self.counters["mask_operations"] += 1
        self.counters["mask_operations"] += 1
        return statement["kind"] in ("every", "no"), a & b

    def _aggregate(self,constraints):
        allowed=self.full;universals=[];existentials=[]
        for index,(universal,mask) in enumerate(constraints):
            self.counters["constraints_checked"]+=1
            if universal:
                universals.append(index);allowed&=self.full^mask
                self.counters["mask_operations"]+=2
            else:existentials.append((index,mask))
        return allowed,tuple(universals),tuple(existentials)

    def _model(self,allowed,universals,existentials):
        self.counters["satisfiability_checks"]+=1
        if not allowed:return {"kind":"unsat","obligation":"domain","cover":list(universals)}
        world=set()
        for index,mask in existentials:
            available=allowed&mask;self.counters["mask_operations"]+=1
            if not available:return {"kind":"unsat","obligation":index,"cover":list(universals)}
            world.add((available&-available).bit_length()-1);self.counters["witness_selections"]+=1
        if not world:
            world.add((allowed&-allowed).bit_length()-1);self.counters["witness_selections"]+=1
        return {"kind":"model","world":sorted(world)}

    def _binding(self,p):
        def plain(value,depth=0):
            self.binding_work["nodes_checked"]+=1
            if depth>8:raise InputRefused("PREPARED_SHAPE")
            if type(value) is tuple:
                if len(value)>128:raise InputRefused("PREPARED_SHAPE")
                for v in value:plain(v,depth+1)
            elif type(value) not in (str,int,bool):raise InputRefused("PREPARED_SHAPE")
        values=tuple(getattr(p,n) for n in Prepared.__dataclass_fields__)
        plain(values[1:])
        if type(p.task_bytes) is not bytes or len(p.task_bytes)>65536:raise InputRefused("PREPARED_SHAPE")
        self.binding_work["decode_input_bytes"]+=len(p.task_bytes)
        try:task_text=p.task_bytes.decode("ascii")
        except UnicodeDecodeError as exc:raise InputRefused("PREPARED_SHAPE") from exc
        self.binding_work["json_encode_calls"]+=1
        raw=json.dumps((task_text,*values[1:]),separators=(",",":")).encode()
        self.binding_work["bytes_hashed"]+=len(raw)
        return hashlib.sha256(raw).digest()

    def _validate(self,value):
        self.binding_work["task_validation_calls"]+=1
        return validate_task(value)

    def _digest(self,value):
        self.binding_work["task_validation_calls"]+=1
        self.binding_work["task_digest_calls"]+=1;self.binding_work["json_encode_calls"]+=1
        return task_digest(value)

    def prepare(self,value):
        self._active=None;self.counters=dict.fromkeys(COUNTERS,0)
        self.binding_work=dict.fromkeys(BINDING_COUNTERS,0)
        task=self._validate(value)
        if task["predicates"]!=self.predicates:raise InputRefused("CACHE_VOCABULARY_MISMATCH")
        constraints=tuple(self._constraint(s) for s in task["premises"])
        allowed,u,e=self._aggregate(constraints)
        base=self._model(allowed,u,e)
        self.binding_work["json_encode_calls"]+=1
        p=Prepared(json.dumps(task,sort_keys=True,separators=(",",":")).encode(),constraints,
                   allowed,u,e,_freeze(base),tuple(self.counters.items()))
        self._active=(p,self._binding(p));return p

    def inspect_prepared(self,p,value=None):
        if type(p) is not Prepared or self._active is None or p is not self._active[0]:
            raise InputRefused("PREPARED_ISSUER_OR_STALE")
        if self._binding(p)!=self._active[1]:raise InputRefused("PREPARED_BINDING")
        self.binding_work["decode_input_bytes"]+=len(p.task_bytes)
        self.binding_work["json_parse_calls"]+=1
        task=self._validate(json.loads(p.task_bytes))
        if value is not None and self._digest(value)!=self._digest(task):raise InputRefused("PREPARED_TASK")
        return task,_thaw(p.base)

    def _branch(self,p,query):
        universal,mask=self._constraint(query);self.counters["constraints_checked"]+=1
        if universal:
            allowed=p.allowed&(self.full^mask);self.counters["mask_operations"]+=2
            return self._model(allowed,p.universals+(len(p.constraints),),p.existentials)
        # Existing witnesses remain valid under an added existential requirement.
        self.counters["satisfiability_checks"]+=1
        available=p.allowed&mask;self.counters["mask_operations"]+=1
        if not available:return {"kind":"unsat","obligation":len(p.constraints),"cover":list(p.universals)}
        witness=(available&-available).bit_length()-1;self.counters["witness_selections"]+=1
        return {"kind":"model","world":sorted(set(p.base[1])|{witness})}

    def _result(self,task,base,yes,no,counters):
        status="INCONSISTENT" if base["kind"]=="unsat" else (
            "CONTRADICTED" if yes["kind"]=="unsat" else "ENTAILED" if no["kind"]=="unsat" else "UNKNOWN")
        return {"schema":RESULT_SCHEMA,"task_sha256":self._digest(task),"status":status,
                "premises":base,"query_true":yes,"query_false":no,"counters":counters}

    def result_from_certificates(self,p,yes,no):
        """Proposal assembly only: the independent verifier remains acceptance authority."""
        task,base=self.inspect_prepared(p)
        return self._result(task,base,yes,no,dict.fromkeys(COUNTERS,0))

    def complete(self,p):
        before=dict(self.counters)
        task,base=self.inspect_prepared(p);yes=no=None
        if base["kind"]!="unsat":
            yes=self._branch(p,task["query"]);no=self._branch(p,negate(task["query"]))
        delta={k:v-before[k] for k,v in self.counters.items()}
        return self._result(task,base,yes,no,delta)

    def solve(self,value):
        try:
            p=self.prepare(value);result=self.complete(p)
            result["counters"]=dict(self.counters)
            return result
        except InputRefused as exc:return {"schema":RESULT_SCHEMA,"status":"INPUT_REFUSED","reason":str(exc)}


def solve(value):
    try:task=validate_task(value)
    except InputRefused as exc:return {"schema":RESULT_SCHEMA,"status":"INPUT_REFUSED","reason":str(exc)}
    return RegionSolver(task["predicates"]).solve(task)
