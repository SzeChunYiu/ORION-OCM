"""Create-only coordinator evidence and faithful independent store copies."""
import hashlib,os,re,stat,time
from pathlib import Path
from unary_contract import InputRefused,fields
from unary_assay_service import remaining
from unary_assay_rows import sync_dir
import unary_method_plain as D

def digest(raw):return hashlib.sha256(raw).hexdigest()

def inventory(root,*,deadline=None,work=None):
    work={} if work is None else work;root=Path(root)
    if root.is_symlink() or not root.is_dir():raise InputRefused("STORE_ENTRY")
    result={".":{"kind":"directory","mode":stat.S_IMODE(root.stat().st_mode)}}
    def walk(folder):
        for p in sorted(folder.iterdir()):
            if deadline is not None:remaining(deadline)
            st=p.lstat();rel=str(p.relative_to(root));D.bump(work,"inventory_entries")
            if stat.S_ISDIR(st.st_mode):
                result[rel]={"kind":"directory","mode":stat.S_IMODE(st.st_mode)};walk(p)
            elif stat.S_ISREG(st.st_mode) and st.st_nlink==1:
                h=hashlib.sha256();size=0
                with p.open("rb") as f:
                    while chunk:=f.read(65536):
                        if deadline is not None:remaining(deadline)
                        h.update(chunk);size+=len(chunk)
                if size!=st.st_size:raise InputRefused("STORE_CHANGED")
                D.bump(work,"inventory_bytes_hashed",size)
                result[rel]={"kind":"file","mode":stat.S_IMODE(st.st_mode),"bytes":size,"sha256":h.hexdigest()}
            else:raise InputRefused("STORE_ENTRY")
    walk(root)
    if deadline is not None:remaining(deadline)
    return result

def copy_store(source,target,*,deadline,work=None):
    start=time.monotonic();cpu=time.process_time();work={} if work is None else work
    source=Path(source);target=Path(target);remaining(deadline)
    if target.exists() or target.is_symlink():raise FileExistsError(target)
    src=source.resolve(strict=True);dst=target.resolve()
    if src==dst or src.is_relative_to(dst) or dst.is_relative_to(src):raise InputRefused("COPY_OVERLAP")
    before=inventory(source,deadline=deadline,work=work)
    try:
        target.mkdir(parents=True,exist_ok=False)
        for rel,meta in before.items():
            remaining(deadline)
            if rel==".":continue
            p=target/rel
            if meta["kind"]=="directory":p.mkdir()
            else:
                with (source/rel).open("rb") as a,p.open("xb") as b:
                    while chunk:=a.read(65536):
                        remaining(deadline);b.write(chunk);D.bump(work,"copy_bytes",len(chunk))
                    b.flush();os.fsync(b.fileno())
                p.chmod(meta["mode"]);D.bump(work,"files_copied")
        for folder in sorted((p for p in target.rglob("*") if p.is_dir()),reverse=True):
            folder.chmod(before[str(folder.relative_to(target))]["mode"]);sync_dir(folder)
        target.chmod(before["."]["mode"])
        sync_dir(target);sync_dir(target.parent)
        after=inventory(source,deadline=deadline,work=work);copied=inventory(target,deadline=deadline,work=work)
        if before!=after or before!=copied:raise InputRefused("COPY_IDENTITY")
        remaining(deadline)
        return {"source":str(src),"target":str(dst),"before":before,"after":after,"copied":copied,"work":work}
    finally:
        work["copy_wall_s"]=time.monotonic()-start;work["copy_cpu_s"]=time.process_time()-cpu

def write(root,name,value):
    if type(name) is not str or re.fullmatch(r"[A-Za-z0-9_.-]+",name) is None:raise InputRefused("RECORD_PATH")
    root=Path(root);raw=D.raw(value);path=root/name
    with path.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
    sync_dir(root)
    return {"path":name,"bytes":len(raw),"sha256":digest(raw)}

def read(root,ref):
    fields(ref,("path","bytes","sha256"))
    if type(ref["path"]) is not str or re.fullmatch(r"[A-Za-z0-9_.-]+",ref["path"]) is None:raise InputRefused("RECORD_PATH")
    if type(ref["bytes"]) is not int or not 0<=ref["bytes"]<=D.MAX_BYTES:raise InputRefused("RECORD_BYTES")
    p=Path(root)/ref["path"];st=p.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1:raise InputRefused("RECORD_ENTRY")
    if st.st_size!=ref["bytes"]:raise InputRefused("RECORD_HASH")
    with p.open("rb") as f:raw=f.read(D.MAX_BYTES+1)
    if len(raw)!=ref["bytes"] or digest(raw)!=ref["sha256"]:raise InputRefused("RECORD_HASH")
    return D.parse(raw)

class Ledger:
    def __init__(self,root,*,deadline):
        remaining(deadline);self.root=Path(root);self.root.mkdir(parents=True,exist_ok=False)
        sync_dir(self.root.parent);self.deadline=deadline;self.head=None;self.count=0
    def append(self,kind,body):
        row={"sequence":self.count,"previous":self.head,"kind":kind,"body":body,
             "observed_monotonic":time.monotonic(),"deadline_monotonic":self.deadline}
        ref=write(self.root,f"{self.count:08d}.json",row)
        self.head=ref["sha256"];self.count+=1
        return ref

def replay(root):
    root=Path(root);names=sorted(p.name for p in root.iterdir())
    if names!=[f"{i:08d}.json" for i in range(len(names))]:raise InputRefused("LEDGER_MEMBERSHIP")
    result=[];head=None
    for i,name in enumerate(names):
        p=root/name;st=p.lstat()
        if st.st_size>D.MAX_BYTES:raise InputRefused("RECORD_BYTES")
        with p.open("rb") as f:raw=f.read(D.MAX_BYTES+1)
        ref={"path":name,"bytes":len(raw),"sha256":digest(raw)}
        row=read(root,ref);fields(row,("sequence","previous","kind","body","observed_monotonic","deadline_monotonic"))
        if type(row["sequence"]) is not int or row["sequence"]!=i or row["previous"]!=head:raise InputRefused("LEDGER_CHAIN")
        head=ref["sha256"];result.append(row)
    if names!=sorted(p.name for p in root.iterdir()):raise InputRefused("LEDGER_MEMBERSHIP")
    return result
