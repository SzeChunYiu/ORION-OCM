"""Bounded authored subprocess recorder, with raw failure retention."""
import hashlib,json,os,resource,signal,subprocess,time
from pathlib import Path
from unary_contract import InputRefused
import unary_method_outer as D
import unary_method_profile as B

PYTHON=B.DEFAULT["executable"]

def stamp(path):
    b=Path(path).read_bytes()
    return {"path":str(path),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}

def absent(pid):
    try:os.killpg(pid,0);return False
    except ProcessLookupError:return True

def launch(root,mode,request,*,timeout=30,profile=None,arm="ocm"):
    root=Path(root);root.mkdir(parents=True,exist_ok=False)
    from unary_method_arm import MODES
    if mode not in MODES:raise InputRefused("PROCESS_MODE")
    if type(arm) is not str or arm not in ("ocm","conventional"):raise InputRefused("PROCESS_ARM")
    packet=D.raw(request);(root/"request.json").write_bytes(packet)
    entry=Path(__file__).with_name("unary_method_episode.py").resolve()
    supplied=D.parse(D.raw(B.DEFAULT if profile is None else profile))
    argv=None
    env={"PATH":"/usr/bin:/bin","LANG":"C.UTF-8","OCM_UNARY_ARM":arm}
    before=D.sources();start=time.monotonic();cpu=resource.getrusage(resource.RUSAGE_CHILDREN)
    p=None;error=None
    receipt={"arm":arm,"argv":argv,"profile":supplied,"environment":env,"source_before":before,"python":None,
             "entry":stamp(entry),"request":stamp(root/"request.json"),"started_monotonic":start}
    with (root/"stdout.bin").open("xb") as out,(root/"stderr.bin").open("xb") as err:
        try:
            selected=B.validate(supplied);receipt["python"]=B.verify(selected)
            argv=[selected["executable"],"-I","-S","-B",str(entry),mode,str(root/"request.json"),str(root/"result.json")]
            env["OCM_UNARY_PYTHON_PROFILE"]=D.raw(selected).decode();receipt["argv"]=argv
            p=subprocess.Popen(argv,cwd=root,env=env,stdout=out,stderr=err,start_new_session=True)
            p.wait(timeout=timeout)
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
    except Exception as exc:postcheck_error=type(exc).__name__+": "+str(exc)
    receipt.update(pid=None if p is None else p.pid,returncode=None if p is None else p.returncode,
        reaped=p is not None and p.returncode is not None,group_absent=p is not None and absent(p.pid),
        ended_monotonic=ended,outer_wall_s=ended-start,waited_child_user_s=usage.ru_utime-cpu.ru_utime,
        waited_child_system_s=usage.ru_stime-cpu.ru_stime,error=error,source_after=after,postcheck_error=postcheck_error,
        stdout=stamp(root/"stdout.bin"),stderr=stamp(root/"stderr.bin"),
        scope="Authored CPU process execution; not closed-host containment or a scientific study.")
    receipt["terminal"]="PROCESS_REFUSED"
    try:
        raw=(root/"result.json").read_bytes();data=D.parse(raw)
        receipt["result"]=stamp(root/"result.json")
        if (p is not None and p.returncode==0 and error is None and receipt["group_absent"]
            and postcheck_error is None and before==receipt["source_after"] and not (root/"stderr.bin").read_bytes()
            and raw==(root/"stdout.bin").read_bytes() and data["terminal"]=="COMPLETED"
            and data["arm"]==arm and data["profile"]==supplied and data["python"]==receipt["python"]
            and data["input_sha256"]==hashlib.sha256(packet).hexdigest()
            and data["source_before"]==data["source_after"]==before):
            receipt["terminal"]="COMPLETED"
    except (OSError,ValueError,KeyError) as exc:receipt["result_refusal"]=type(exc).__name__+": "+str(exc)
    with (root/"PROCESS.json").open("xb") as f:f.write(D.raw(receipt))
    return receipt
