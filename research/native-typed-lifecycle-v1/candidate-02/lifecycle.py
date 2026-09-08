"""Once-only typed qualification supervisor; all failures remain in place."""
from pathlib import Path
import copy,importlib.util,os,resource,sys,time
spec=importlib.util.spec_from_file_location("life_common",Path(__file__).with_name("life_common.py"))
C=importlib.util.module_from_spec(spec);sys.modules["life_common"]=C;spec.loader.exec_module(C)


def controls(out):
    records=[]
    for name,source in (("source_tamper","life_common.py"),("request_tamper","RUN-REQUEST.json")):
        path=out/(name+".json");original=(C.HERE/source).read_bytes()
        path.write_bytes(original);pin=C.identity(path)
        C.require(C.identity(path)==pin,"CONTROL_CLEAN_BINDING")
        path.write_bytes(original+b" ")
        try:C.checked(path,pin)
        except ValueError as exc:
            C.require(str(exc)=="FILE_BINDING_CHANGED","CONTROL_WRONG_REFUSAL")
            records.append({"control":name,"terminal":"STRUCTURAL_REFUSAL","error":str(exc),
                            "original":pin,"changed":C.identity(path),"native_calls":0})
        else:raise ValueError("CONTROL_FALSE_ACCEPT")
    return records


def main():
    started=time.perf_counter();cpu=resource.getrusage(resource.RUSAGE_SELF)
    output=C.HERE/"lifecycle-01";output.mkdir(exist_ok=False)
    result={"terminal":"INCOMPLETE","native_gate":"root","pid":os.getpid()}
    try:
        request=C.gate()
        C.require(request["argv"]==[request["python"],"-I","-S","-B",str(C.HERE/"lifecycle.py")],
                  "ENTRY_ARGV_CONTRACT")
        io=controls(output);C.write(output/"IO-CONTROLS.json",io)
        observer=C.load("life_process","life_process.py")
        producer=C.HERE/"producer-01"
        process=observer.observe("run_a.py",producer,output/"A-PROCESS.json")
        C.require(process["exit_code"]==0 and process["sources_unchanged"] and process["request_unchanged"],
                  "PRODUCER_PROCESS_FAILED")
        a=C.checked(producer/"RESULT.json",process["result"])
        result["producer"]=a;result["producer_process"]=C.identity(output/"A-PROCESS.json")
        if a["terminal"]!="ADMITTED_AND_PERSISTED":
            C.require(a["terminal"] in ("NO_SUPPORTED_CANDIDATE","ALIAS_CHECK_UNKNOWN"),"UNKNOWN_A_TERMINAL")
            result["terminal"]=a["terminal"];return
        engine=C.engine();P=C.load("life_payload","life_payload.py")
        # A fake interrupted receipt must refuse before any state is interpreted.
        interrupted=copy.deepcopy(process);interrupted["reaped"]=False
        C.write(output/"INTERRUPTED-PROCESS.json",interrupted)
        try:P.project(producer/"STATE.json",output/"INTERRUPTED-PROCESS.json",
                      producer/"RESULT.json",output/"MUST-NOT-EXIST.json",engine)
        except ValueError as exc:
            C.require(str(exc)=="PRODUCER_NOT_CLEANLY_EXITED","INTERRUPTION_WRONG_REFUSAL")
            C.write(output/"INTERRUPTION-CONTROL.json",{"terminal":"STRUCTURAL_REFUSAL","error":str(exc),
                                                       "native_calls":0})
        else:raise ValueError("INTERRUPTED_PRODUCER_ACCEPTED")
        projection_start=time.perf_counter()
        projection=P.project(producer/"STATE.json",output/"A-PROCESS.json",
                             producer/"RESULT.json",C.HERE/"PROJECTION.json",engine)
        payload=C.checked(C.HERE/"PROJECTION.json",projection)
        R=C.load("life_requests","life_requests.py")
        packet=R.requests(payload,P.class_witness(engine))
        request_pin=C.write(C.HERE/"B-REQUEST.json",packet)
        b_input={"projection":projection,"request":request_pin,
                 "source_freeze":C.identity(C.HERE/"SOURCE-FREEZE.json")}
        b_pin=C.write(C.HERE/"B-INPUT.json",b_input)
        C.write(C.HERE/"B-GATE.json",{"input":b_pin,"exited_producer":C.identity(output/"A-PROCESS.json")})
        result["projection"]={"identity":projection,"wall_s":time.perf_counter()-projection_start,
            "cost_scope":"exited-state projection, class conversion, direct issued-request construction and bindings",
            "state_bytes_read":C.identity(producer/"STATE.json")["bytes"],"projection_bytes":projection["bytes"],
            "requests_bytes":request_pin["bytes"]}
        # Tamper a copy, preserve actual serving projection unchanged.
        tampered=output/"TAMPERED-PROJECTION.json"
        tampered.write_bytes((C.HERE/"PROJECTION.json").read_bytes()+b" ")
        try:C.checked(tampered,projection)
        except ValueError as exc:
            C.require(str(exc)=="FILE_BINDING_CHANGED","PAYLOAD_WRONG_REFUSAL")
            C.write(output/"PAYLOAD-CONTROL.json",{"terminal":"STRUCTURAL_REFUSAL","error":str(exc),"native_calls":0})
        else:raise ValueError("TAMPERED_PAYLOAD_ACCEPTED")
        consumer=C.HERE/"consumer-01"
        bprocess=observer.observe("run_b.py",consumer,output/"B-PROCESS.json")
        C.require(bprocess["exit_code"]==0 and bprocess["sources_unchanged"] and bprocess["request_unchanged"],
                  "CONSUMER_PROCESS_FAILED")
        b=C.checked(consumer/"RESULT.json",bprocess["result"])
        C.require(b["pid"]==bprocess["pid"] and b["parent_pid"]==os.getpid() and
                  b["request"]==request_pin and b["projection"]==projection,"B_RESULT_BINDING")
        C.require(a["pid"]==process["pid"] and a["parent_pid"]==os.getpid() and
                  process["pid"]!=bprocess["pid"] and process["exit_utc"]<bprocess["start_utc"],"A_EXIT_FRESH_B")
        C.check_sources(expected_freeze=request["source_freeze"])
        result.update(terminal=b["terminal"],consumer=b,consumer_process=C.identity(output/"B-PROCESS.json"))
        C.require(C.identity(C.HERE/"PROJECTION.json")==projection and
                  C.identity(C.HERE/"B-REQUEST.json")==request_pin,"FINAL_SERVING_CUSTODY")
    except Exception as exc:
        result.update(terminal="LIFECYCLE_FAILED",error={"type":type(exc).__name__,"message":str(exc)})
        raise
    finally:
        after=resource.getrusage(resource.RUSAGE_SELF)
        result["costs"]={"wall_s":time.perf_counter()-started,"supervisor_user_cpu_s":after.ru_utime-cpu.ru_utime,
             "supervisor_system_cpu_s":after.ru_stime-cpu.ru_stime,"supervisor_highwater_rss_kib":after.ru_maxrss,
             "scope":"lifecycle through final custody; final receipt write excluded; child CPU separate"}
        result["common_io"]=dict(C.IO)
        C.write(output/"RESULT.json",result)


if __name__=="__main__":main()
