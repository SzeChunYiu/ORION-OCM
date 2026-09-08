"""Independent full native replay of the exact issued normal proof context."""
from pathlib import Path
import contextlib,io,time
from vendor import common as C
from native_bundle import PINS
from native_contract import require,task as validate_task
import native_data as D
S=C.load("trace_source");A=C.load("trace_adapter")
class NativeChecker:
    def __init__(self,bundle,archive,work):
        self.bundle=Path(bundle);self.archive=Path(archive);self.archive.mkdir(parents=True,exist_ok=True);self.work=work
    def verify(self,claims):
        start=time.monotonic();prefix=(self.bundle/"PREFIX.mm").read_bytes()
        require(C.raw_id(prefix)==PINS["PREFIX.mm"],"CHECKER_LIBRARY_CHANGED")
        require(type(claims) is list and len(claims)==1,"CHECKER_CLAIM_BOUND")
        suffix=[];selected=[]
        for i,claim in enumerate(claims):
            validate_task(claim["task"]);proof=claim["proof"]
            require(type(proof) is list and 0<len(proof)<=4096 and all(type(x) is str and x and all(c.isalnum() or c in "-_." for c in x) for x in proof),"PROOF_TOKENS")
            names=claim["holes"]
            require(names==["search-hyp-"+str(j) for j in range(len(claim["task"]["premises"]))],"EXACT_HOLE_NAMES")
            label="native-serving-result-"+str(i);selected.append(label);suffix.append("${")
            for h,statement in zip(names,claim["task"]["premises"]):suffix.append(h+" $e "+" ".join(statement)+" $.")
            suffix.append(label+" $p "+" ".join(claim["task"]["query"])+" $= "+" ".join(proof)+" $.");suffix.append("$}")
        raw=prefix+("\n"+"\n".join(suffix)+"\n").encode("ascii");digest=C.raw_id(raw)
        db=self.archive/(digest["sha256"]+".mm")
        if db.exists():require(db.read_bytes()==raw,"CHECKER_ARCHIVE_COLLISION")
        else:
            with db.open("xb") as f:f.write(raw);f.flush();__import__("os").fsync(f.fileno())
        rows,_=S.index(raw);trusted=[r["label"] for r in rows.values() if r["kind"]=="$a"]
        expected=[r["label"] for r in rows.values() if r["kind"]=="$p"]
        require(len(trusted)==96 and len(expected)==4095+len(claims) and expected[-len(claims):]==selected,"NATIVE_POPULATION")
        N=C.load("mmverify");log=io.StringIO();N.verbosity,N.logfile=2,log
        class Tokens(N.Toks):
            def __init__(self,file):super().__init__(file);self.recent=[]
            def readc(self):
                word=super().readc();self.recent=(self.recent+[word])[-2:];return word
        mm=A.traced_class(N,rows)(selected,None);error=None
        try:
            with db.open(encoding="ascii") as stream,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):mm.read(Tokens(stream))
            require(mm.verified==expected and set(mm.traces)==set(selected),"NATIVE_REPLAY_POPULATION")
        except Exception as exc:error={"type":type(exc).__name__,"message":str(exc)}
        require(db.read_bytes()==raw and C.raw_id((self.bundle/"PREFIX.mm").read_bytes())==PINS["PREFIX.mm"],"NATIVE_CONSUMED_DRIFT")
        result={"schema":"native.replay.v1","terminal":"NATIVE_VERIFIED" if error is None else "NATIVE_REJECTED",
                "claims_sha256":D.hashed(claims),"database":digest,"prefix":PINS["PREFIX.mm"],"error":error,
                "verified_count":len(mm.verified),"trusted_count":len(trusted),"trusted_sha256":D.hashed(trusted),
                "trace_sha256":D.hashed(mm.traces),"wall_s":time.monotonic()-start}
        # Each invocation is retained even for identical claim bytes.
        stem=str(len(list(self.archive.glob("replay-*.json")))).zfill(6)
        with (self.archive/("replay-"+stem+".json")).open("xb") as f:f.write(C.canonical(result))
        (self.archive/("replay-"+stem+".log")).write_text(log.getvalue())
        D.bump(self.work,"native_calls");D.bump(self.work,"native_database_bytes",len(raw));D.bump(self.work,"native_wall_s",result["wall_s"])
        return result
