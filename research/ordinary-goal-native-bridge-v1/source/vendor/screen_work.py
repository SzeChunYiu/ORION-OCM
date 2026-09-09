"""Original matcher-state bound plus a shared soft wall checkpoint."""
import time
from syntax_engine import SyntaxUnknown
class Work(dict):
    def __init__(self, maximum=2000000, seconds=60, started=None):
        super().__init__()
        self.maximum=maximum;self.seconds=seconds
        self.started=time.perf_counter() if started is None else started
        self.exhausted=False;self.reason=None;self.rejected_token_state=None
    def checkpoint(self):
        if self.exhausted:raise SyntaxUnknown(self.reason)
        if time.perf_counter()-self.started>self.seconds:
            self.exhausted=True;self.reason="REGISTERED_SOFT_WALL_BOUND"
            raise SyntaxUnknown(self.reason)
    def __setitem__(self,key,value):
        if key=="token_states":
            self.checkpoint()
            if value>self.maximum:
                self.exhausted=True;self.reason="REGISTERED_TOKEN_STATE_BOUND"
                self.rejected_token_state=value
                raise SyntaxUnknown(self.reason)
        super().__setitem__(key,value)
    def add(self,key,value=1):self[key]=self.get(key,0)+value
    def snapshot(self):
        return {"counters":dict(self),"exhausted":self.exhausted,"reason":self.reason,
                "rejected_token_state":self.rejected_token_state}
