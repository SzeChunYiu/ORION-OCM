"""Fixed harmless engineering cases; never generates registered task draws."""
import ctypes,errno,json,os,socket,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for folder in reversed((ROOT/"src",ROOT/"research/math-language-v1",ROOT/"research/math-language-learning-v1")):sys.path.insert(0,str(folder))
import unary_assay_launch_contract as L

def observation():
    tasks={}
    for p in sorted(Path("/proc/self/task").iterdir()):
        tasks[p.name]=sorted(os.sched_getaffinity(int(p.name)))
    maps=Path("/proc/self/maps").read_text()
    return {"pid":os.getpid(),"ppid":os.getppid(),"affinity":sorted(os.sched_getaffinity(0)),
            "threads":tasks,"maps":maps,"cgroup":Path("/proc/self/cgroup").read_text()}

def run(value,deadline):
    if type(value) is not dict or set(value)!={"case"} or value["case"] not in L.CASES:raise ValueError("AUTHORED_PROBE_CASE")
    root=Path(L.WORK);case=value["case"];out={"case":case,"initial":observation()}
    L.write(root/"probe-start.json",out)
    if case=="normal":
        L.write(root/"ordinary.json",{"ordinary_file_work":True})
        argv=[sys.executable,"-I","-S","-B",str(Path(__file__).resolve()),"child"]
        p=subprocess.run(argv,capture_output=True,timeout=max(.001,deadline-time.monotonic()))
        out.update(child_returncode=p.returncode,child=json.loads(p.stdout),child_stderr=p.stderr.decode())
        if p.returncode or out["child"]["affinity"]!=out["initial"]["affinity"]:raise ValueError("PROBE_CHILD")
    elif case=="network":
        try:socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except PermissionError as exc:out["denied"]=type(exc).__name__
        else:raise ValueError("NETWORK_NOT_DENIED")
    elif case=="source_write":
        try:Path(__file__).write_bytes(b"authored write must be refused")
        except OSError as exc:out["denied"]={"class":type(exc).__name__,"errno":exc.errno}
        else:raise ValueError("SOURCE_WRITE_NOT_DENIED")
    elif case in ("native_exec","native_map"):
        p=root/"undeclared-native"
        with Path(sys.executable).open("rb") as src,p.open("xb") as dst:
            for b in iter(lambda:src.read(1<<20),b""):dst.write(b)
        p.chmod(0o700)
        if case=="native_exec":
            try:
                child=subprocess.run([str(p),"-I","-S","-B","-c","raise SystemExit(0)"],capture_output=True)
            except PermissionError as exc:
                if exc.errno not in (errno.EACCES,errno.EPERM):raise
                out["denied"]={"class":type(exc).__name__,"errno":exc.errno,"message":str(exc)}
                L.write(root/"probe-native-attempt.json",out["denied"])
            else:
                L.write(root/"probe-native-attempt.json",{"returncode":child.returncode,
                    "stdout":child.stdout.decode(errors="replace"),"stderr":child.stderr.decode(errors="replace")})
                raise ValueError("UNDECLARED_NATIVE_EXECUTED")
        else:
            ctypes.CDLL("/lib/x86_64-linux-gnu/libc.so.6");p.unlink()
            with Path("/lib/x86_64-linux-gnu/libc.so.6").open("rb") as src,p.open("xb") as dst:dst.write(src.read())
            out["authorized_libc"]=L.stamp(Path("/lib/x86_64-linux-gnu/libc.so.6").resolve(strict=True))
            out["copied_libc"]=L.stamp(p)
            try:ctypes.CDLL(str(p))
            except OSError as exc:
                out["mapping_error"]={"class":type(exc).__name__,"errno":exc.errno,"message":str(exc)}
                L.write(root/"probe-native-attempt.json",out)
                if "failed to map segment from shared object" not in str(exc):raise ValueError("UNCLASSIFIED_NATIVE_MAP_FAILURE") from exc
                out["denied"]=out["mapping_error"]
            else:raise ValueError("UNDECLARED_NATIVE_MAP_SUCCEEDED")
    elif case=="deadline":
        pid=os.fork()
        if pid==0:
            L.write(root/"descendant.json",observation())
            while True:time.sleep(.1)
        out["descendant_pid"]=pid;L.write(root/"descendant-parent.json",out)
        while True:time.sleep(.1)
    else:
        held=[]
        while True:
            b=bytearray(32<<20)
            for i in range(0,len(b),4096):b[i]=1
            held.append(b)
    out["final"]=observation();return out

if __name__=="__main__":
    if sys.argv[1:]!=["child"]:raise SystemExit(2)
    print(json.dumps(observation(),sort_keys=True))
