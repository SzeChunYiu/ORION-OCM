"""One fresh Linux child, exact argv, retained stdout/stderr and wait4 costs."""
import datetime,os,subprocess,time
import life_common as C


def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()


def observe(script,output,receipt):
    request_before=C.identity(C.HERE/"RUN-REQUEST.json")
    before=C.check_sources();source_before=C.digest(before)
    argv=[C.read(C.HERE/"RUN-REQUEST.json")["python"],"-I","-S","-B",str(C.HERE/script),str(output)]
    started=time.perf_counter();start_utc=now()
    with open(str(receipt)+".stdout","xb") as stdout,open(str(receipt)+".stderr","xb") as stderr:
        child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,cwd=C.HERE)
        pid,status,usage=os.wait4(child.pid,0)
        child.returncode=os.waitstatus_to_exitcode(status)
    elapsed=time.perf_counter()-started;exit_utc=now()
    stable=True;error=None
    try:C.check_sources()
    except Exception as exc:stable=False;error=str(exc)
    result_path=output/"RESULT.json";failure_path=output/"FAILURE.json"
    result={"argv":argv,"pid":pid,"parent_pid":os.getpid(),"exit_code":child.returncode,"reaped":True,
        "start_utc":start_utc,"exit_utc":exit_utc,"wall_s":elapsed,"user_cpu_s":usage.ru_utime,
        "system_cpu_s":usage.ru_stime,"highwater_rss_kib":usage.ru_maxrss,
        "cost_scope":"fresh child through wait4; parent custody hashing excluded",
        "sources_unchanged":stable,"source_error":error,"source_freeze_sha256":source_before,
        "request_before":request_before,"request_after":C.identity(C.HERE/"RUN-REQUEST.json"),
        "request_unchanged":C.identity(C.HERE/"RUN-REQUEST.json")==request_before,
        "result":C.identity(result_path) if result_path.exists() else None,
        "failure":C.identity(failure_path) if failure_path.exists() else None,
        "stdout":C.identity(str(receipt)+".stdout"),"stderr":C.identity(str(receipt)+".stderr")}
    C.write(receipt,result)
    return result
