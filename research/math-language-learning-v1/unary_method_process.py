"""Bounded authored subprocess recorder, with raw failure retention."""
import hashlib,json,os,resource,signal,subprocess,time
from pathlib import Path
from unary_contract import InputRefused
from unary_method_plain import MAX_BYTES
import unary_method_outer as D
import unary_method_profile as B

PYTHON=B.DEFAULT["executable"]

def stamp(path):
    h=hashlib.sha256();size=0
    with Path(path).open("rb") as f:
        while chunk:=f.read(65536):h.update(chunk);size+=len(chunk)
    return {"path":str(path),"bytes":size,"sha256":h.hexdigest()}

def absent(pid):
    try:os.killpg(pid,0);return False
    except ProcessLookupError:return True

def launch(root,mode,request,*,timeout=30,profile=None,arm="ocm",deadline=None):
    root=Path(root);root.mkdir(parents=True,exist_ok=False)
    from unary_method_arm import MODES
    if mode not in MODES:raise InputRefused("PROCESS_MODE")
    if type(arm) is not str or arm not in ("ocm","conventional","exact"):raise InputRefused("PROCESS_ARM")
    packet=D.raw(request);(root/"request.json").write_bytes(packet)
    entry=Path(__file__).with_name("unary_method_episode.py").resolve()
    supplied=D.parse(D.raw(B.DEFAULT if profile is None else profile))
    argv=None
    env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8","OCM_UNARY_ARM":arm}
    before=None;start=time.monotonic();cpu=resource.getrusage(resource.RUSAGE_CHILDREN)
    p=None;error=None
    receipt={"arm":arm,"argv":argv,"profile":supplied,"environment":env,"source_before":before,"python":None,
             "deadline_monotonic":deadline,"entry":stamp(entry),"request":stamp(root/"request.json"),"started_monotonic":start}
    with (root/"stdout.bin").open("xb") as out,(root/"stderr.bin").open("xb") as err:
        try:
            from unary_assay_service import remaining
            if deadline is not None:remaining(deadline)
            if mode=="presented_batch":
                if deadline is None or request.get("deadline_monotonic")!=deadline:
                    raise InputRefused("PRESENTED_LAUNCH_DEADLINE")
                env["OCM_UNARY_DEADLINE"]=D.raw(deadline).decode()
            receipt["stage"]="SOURCE_PREFLIGHT";before=D.sources();receipt["source_before"]=before
            selected=B.validate(supplied);receipt["python"]=B.verify(selected)
            argv=[selected["executable"],"-I","-S","-B",str(entry),mode,str(root/"request.json"),str(root/"result.json")]
            env["OCM_UNARY_PYTHON_PROFILE"]=D.raw(selected).decode();receipt["argv"]=argv
            receipt["stage"]="PRELAUNCH"
            if deadline is not None:remaining(deadline)
            receipt["dispatch_monotonic"]=time.monotonic()
            p=subprocess.Popen(argv,cwd=root,env=env,stdout=out,stderr=err,start_new_session=True)
            receipt["stage"]="WAITING"
            wait=timeout if deadline is None else min(timeout,remaining(deadline))
            receipt["wait_timeout_s"]=wait;p.wait(timeout=wait)
            if deadline is not None:remaining(deadline)
            receipt["stage"]="CHILD_EXITED"
        except BaseException as exc:
            error=type(exc).__name__+": "+str(exc)
        finally:
            if p is not None and p.poll() is None:
                try:os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                p.wait()
    ended=time.monotonic();usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    after=None;postcheck_error=None
    try:
        after=D.sources()
        if receipt["python"] is not None:receipt["python_after"]=B.verify(supplied)
        if deadline is not None:remaining(deadline)
    except Exception as exc:postcheck_error=type(exc).__name__+": "+str(exc)
    receipt.update(pid=None if p is None else p.pid,returncode=None if p is None else p.returncode,
        reaped=p is not None and p.returncode is not None,group_absent=p is not None and absent(p.pid),
        ended_monotonic=ended,outer_wall_s=ended-start,waited_child_user_s=usage.ru_utime-cpu.ru_utime,
        waited_child_system_s=usage.ru_stime-cpu.ru_stime,error=error,source_after=after,postcheck_error=postcheck_error,
        stdout=stamp(root/"stdout.bin"),stderr=stamp(root/"stderr.bin"),
        scope="Authored CPU process execution; not closed-host containment or a scientific study.")
    receipt["terminal"]="PROCESS_REFUSED"
    try:
        if (root/"result.json").stat().st_size>MAX_BYTES:raise InputRefused("RESULT_DATA_BOUND")
        with (root/"result.json").open("rb") as f:raw=f.read(MAX_BYTES+1)
        data=D.parse(raw)
        receipt["result"]={"path":str(root/"result.json"),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
        if mode=="presented_batch":
            from unary_assay_rows import audit
            receipt["row_readback_work"]={}
            receipt["row_custody"]=audit(root,data,request,pid=None if p is None else p.pid,
                                       work=receipt["row_readback_work"])
            if deadline is not None:remaining(deadline)
        receipt["result_after"]=stamp(root/"result.json")
        receipt["stdout_after"]=stamp(root/"stdout.bin");receipt["stderr_after"]=stamp(root/"stderr.bin")
        if (p is not None and p.returncode==0 and error is None and receipt["group_absent"]
            and postcheck_error is None and before==receipt["source_after"] and receipt["stderr_after"]["bytes"]==0
            and receipt["result"]==receipt["result_after"] and receipt["stdout"]==receipt["stdout_after"]
            and receipt["stderr"]==receipt["stderr_after"]
            and receipt["stdout"]["bytes"]==len(raw) and receipt["stdout"]["sha256"]==hashlib.sha256(raw).hexdigest()
            and data["terminal"]=="COMPLETED"
            and (mode!="presented_batch" or data["deadline_monotonic"]==deadline)
            and data["arm"]==arm and data["profile"]==supplied and data["python"]==receipt["python"]
            and data["input_sha256"]==hashlib.sha256(packet).hexdigest()
            and data["source_before"]==data["source_after"]==before):
            receipt["terminal"]="COMPLETED"
    except (OSError,ValueError,KeyError) as exc:receipt["result_refusal"]=type(exc).__name__+": "+str(exc)
    with (root/"PROCESS.json").open("xb") as f:f.write(D.raw(receipt))
    return receipt
