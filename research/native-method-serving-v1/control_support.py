"""Explicit route/check doubles. None of these receipts is native evidence."""
from types import SimpleNamespace
from ocm.runtime.ocm_runtime import OCMRuntime
from native_engine import NativeEngine
from native_store import NativeStore
from native_runtime import NativeRuntime
from native_bundle import PINS
from native_contract import require
import native_data as D
TASK={"premises":[["|-","A","C_","B"]],"query":["|-","A","C_","B"]}
MID="test-only-method"
class RouteDouble(NativeEngine):
    def __init__(self):
        self.work={};self.source_map=D.sources(self.work);self.source_sha=D.hashed(self.source_map)
        self.inputs=SimpleNamespace(identity={"TEST_ONLY":"NO_NATIVE_QUALIFICATION"},methods={MID:{"TEST_ONLY":"payload"}})
        self.qualification={MID:{"TEST_ONLY":"NO_NATIVE_QUALIFICATION"}};self.seen=[];self.seen_checks=[]
    def check_environment(self):require(D.sources(self.work)==self.source_map,"SOURCE_CHANGED")
    def propose(self,request):
        self.validate_request(request);self.seen.append(D.parse(D.raw(request)))
        return {"schema":"TEST_ONLY_ROUTE_PACKET","request_sha256":D.hashed(request),"normal_proof":["search-hyp-0"],
                "selected_proof_method_ids":request["eligible_ids"] if request["invoke"] else [],
                "terminal":"PROVED","execution":{"TEST_ONLY":"NO_NATIVE_COMPUTATION"}}
    def check(self,request,packet):
        self.validate_request(request);require(packet["request_sha256"]==D.hashed(request),"DOUBLE_REQUEST")
        require(packet["normal_proof"]==["search-hyp-0"] and request["task"]["query"]==request["task"]["premises"][0],"DOUBLE_WRONG_HOLE_OR_TARGET")
        self.seen_checks.append(D.parse(D.raw(packet)))
        claims=[{"task":request["task"],"proof":packet["normal_proof"],"holes":["search-hyp-0"]}]
        native={"schema":"native.replay.v1","terminal":"NATIVE_VERIFIED","claims_sha256":D.hashed(claims),
                "database":{"TEST_ONLY":"NO_NATIVE_DATABASE"},"prefix":PINS["PREFIX.mm"],"error":None,
                "verified_count":4096,"trusted_count":96,"trusted_sha256":"TEST_ONLY","trace_sha256":"TEST_ONLY","wall_s":0}
        return {"status":"PASS","packet_sha256":D.hashed(packet),"request_sha256":D.hashed(request),"native":native,"work":{"TEST_ONLY":True}}
def populated(tmp_path):
    engine=RouteDouble();rt=OCMRuntime(tmp_path/"ocm");store=NativeStore(rt,engine,create=True)
    runtime=NativeRuntime(store);return rt,store,runtime,engine
