"""Future native sessions; validity stays with unchanged mmverify and donor observer."""
import io

def token_class(native):
    class Tokens(native.Toks):
        def __init__(self,stream):
            super().__init__(stream);self.recent=[]
        def readc(self):
            word=super().readc();self.recent=(self.recent+[word])[-2:];return word
    return Tokens

def read_exact(mm,native,raw,name):
    stream=io.StringIO(raw.decode("ascii"));stream.name=name
    mm.read(token_class(native)(stream))

def verify_prefix(native,adapter,source,raw,name,released,progress):
    Base=adapter.traced_class(native,source)
    class AuthorityMM(Base):
        def __init__(self):
            super().__init__((),None);self.scope_bindings={};self.native_calls=0
        def verify(self,*args):
            label=self.pending
            if label in released:
                actual={"active_variables":sorted(set().union(*(fr.v for fr in self.fs))),
                        "active_dv":sorted([list(p) for p in set().union(*(fr.d for fr in self.fs))])}
                if any(actual[k]!=source[label][k] for k in actual):raise ValueError("fresh active proof/DV context mismatch")
                self.scope_bindings[label]=actual
            self.native_calls+=1
            super().verify(*args)
            progress({"stage":"native_prefix","label":label,"status":"FRESH_NATIVE_VERIFIED"})
    mm=AuthorityMM()
    try:
        read_exact(mm,native,raw,name)
        expected=[label for label,row in source.items() if row["kind"]=="$p"]
        if mm.verified!=expected:raise ValueError("proof skipping/order mismatch")
        return mm,None
    except BaseException as exc:
        return mm,{"type":type(exc).__name__,"message":str(exc),"label":getattr(mm,"pending",None)}

def observe_traces(native,adapter,source,raw,name,released,progress):
    Base=adapter.traced_class(native,source)
    class ObservedMM(Base):
        def __init__(self):
            super().__init__(released,None);self.unusable={};self.native_calls=0
        def verify(self,*args):
            label=self.pending;self.native_calls+=1
            try:
                super().verify(*args)
            except (ValueError,KeyError,IndexError,TypeError,RecursionError) as exc:
                if label not in released:raise
                self.active=None;self.traces.pop(label,None)
                self.unusable[label]={"type":type(exc).__name__,"message":str(exc)}
                # Retry validity with the unchanged verifier, with observation off.
                self.native_calls+=1
                native.MM.verify(self,*args)
                self.verified.append(label)
            if label in released:
                progress({"stage":"trace_observer","label":label,
                          "status":"TRACE_UNUSABLE" if label in self.unusable else "TRACE_READY"})
    mm=ObservedMM()
    try:
        read_exact(mm,native,raw,name)
        expected=[label for label,row in source.items() if row["kind"]=="$p"]
        if mm.verified!=expected:raise ValueError("observer proof order mismatch")
        return mm,None
    except BaseException as exc:
        return mm,{"type":type(exc).__name__,"message":str(exc),"label":getattr(mm,"pending",None)}
