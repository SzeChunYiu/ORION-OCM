"""Stable checker custody; timing observations are not replay authority."""
from native_contract import fields,require
from native_bundle import PINS
import native_data as D
NATIVE_FIELDS=("schema","terminal","claims_sha256","database","prefix","error","verified_count","trusted_count","trusted_sha256","trace_sha256","wall_s")
def stable_check(check):
    fields(check,("status","packet_sha256","request_sha256","native","work"))
    fields(check["native"],NATIVE_FIELDS)
    return {**{k:check[k] for k in ("status","packet_sha256","request_sha256")},
            "native":{k:v for k,v in check["native"].items() if k!="wall_s"}}
def check_identity(request,packet,check):
    stable_check(check)
    require(check["status"]=="PASS" and check["packet_sha256"]==D.hashed(packet) and check["request_sha256"]==D.hashed(request),"CHECK_REQUEST_PACKET")
    claims=[{"task":request["task"],"proof":packet["normal_proof"],"holes":["search-hyp-"+str(i) for i in range(len(request["task"]["premises"]))]}]
    native=check["native"]
    require(native["schema"]=="native.replay.v1" and native["terminal"]=="NATIVE_VERIFIED" and native["error"] is None and
            native["claims_sha256"]==D.hashed(claims) and native["prefix"]==PINS["PREFIX.mm"] and
            native["verified_count"]==4096 and native["trusted_count"]==96,"CHECK_NATIVE_IDENTITY")
