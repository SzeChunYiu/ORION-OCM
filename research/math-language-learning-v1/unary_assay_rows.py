"""Fixed per-row output custody; request/individual-record bounds are unchanged."""
import hashlib,math,os,stat,time
from pathlib import Path
from unary_contract import InputRefused,fields
import unary_method_plain as D

META=("index","observation_id","row_id","presentation","input_sha256","pid","terminal")
REF=("schema","path","bytes","sha256","write_wall_s","write_cpu_s",*META)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def sync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

class Writer:
    def __init__(self,root):
        self.root=Path(root)/"rows";self.root.mkdir(exist_ok=False)
        sync_dir(self.root.parent);self.next=0

    def __call__(self,item):
        start=time.monotonic();cpu=time.process_time();index=self.next
        if type(item.get("index")) is not int or item["index"]!=index:raise InputRefused("ROW_WRITE_ORDER")
        raw=D.raw(item);relative="rows/"+str(index).zfill(5)+".json"
        path=self.root/Path(relative).name
        with path.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
        sync_dir(self.root)
        out={"schema":"ocm.unary-presented-row.v1","path":relative,"bytes":len(raw),"sha256":digest(raw),
             "write_wall_s":time.monotonic()-start,"write_cpu_s":time.process_time()-cpu,
             **{k:item[k] for k in META}}
        self.next+=1
        return out

def read_row(root,ref,expected,*,pid,work):
    D.raw(ref);fields(ref,REF);index=ref["index"]
    if type(index) is not int or not 0<=index<128:raise InputRefused("ROW_INDEX")
    if ref["schema"]!="ocm.unary-presented-row.v1" or ref["path"]!="rows/"+str(index).zfill(5)+".json":
        raise InputRefused("ROW_PATH")
    if type(ref["bytes"]) is not int or not 0<=ref["bytes"]<=D.MAX_BYTES:raise InputRefused("ROW_BYTES")
    path=Path(root)/ref["path"];st=path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1:raise InputRefused("ROW_NOT_REGULAR")
    D.bump(work,"row_files_inspected")
    if st.st_size!=ref["bytes"] or st.st_size>D.MAX_BYTES:raise InputRefused("ROW_BYTES")
    with path.open("rb") as f:raw=f.read(D.MAX_BYTES+1)
    D.bump(work,"row_files_read");D.bump(work,"row_bytes_read",len(raw))
    if len(raw)>D.MAX_BYTES:raise InputRefused("ROW_BYTES")
    if len(raw)!=ref["bytes"] or digest(raw)!=ref["sha256"]:raise InputRefused("ROW_HASH")
    item=D.parse(raw);D.bump(work,"row_records_decoded")
    if type(item) is not dict or not set(META)<=set(item):raise InputRefused("ROW_SHAPE")
    if type(item.get("index")) is not int:raise InputRefused("ROW_INDEX")
    for key in ("write_wall_s","write_cpu_s"):
        if type(ref[key]) is not float or not math.isfinite(ref[key]) or ref[key]<0:
            raise InputRefused("ROW_WRITE_SPAN")
    if any(item.get(k)!=ref[k] for k in META):raise InputRefused("ROW_REFERENCE_METADATA")
    for key in ("observation_id","row_id","presentation"):
        if item[key]!=expected[key]:raise InputRefused("ROW_REQUEST_IDENTITY")
    if item["input_sha256"]!=D.hashed(expected) or type(item["pid"]) is not int or item["pid"]!=pid:
        raise InputRefused("ROW_REQUEST_BINDING")
    if item["terminal"] not in ("CHECKED","CANNOT_CHECK"):raise InputRefused("ROW_TERMINAL")
    return item

def audit(root,data,request,*,pid,work):
    start=time.monotonic();cpu=time.process_time();root=Path(root);folder=root/"rows"
    try:
        if type(data) is not dict or not {"pid","outcome"}<=set(data):raise InputRefused("ROW_SUMMARY")
        if type(request) is not dict or "rows" not in request:raise InputRefused("ROW_REQUEST")
        D.raw(data);D.raw(request)
        if folder.is_symlink() or not folder.is_dir():raise InputRefused("ROW_DIRECTORY")
        if type(data["pid"]) is not int or data["pid"]!=pid:raise InputRefused("ROW_PROCESS_BINDING")
        outcome=data["outcome"]
        if type(outcome) is not dict:raise InputRefused("ROW_OUTCOME")
        refs=outcome["rows"];rows=request["rows"]
        if type(rows) is not list:raise InputRefused("ROW_REQUEST")
        if type(outcome["terminal"]) is not str or outcome["terminal"] not in ("CHECKED","CANNOT_CHECK"):
            raise InputRefused("ROW_OUTCOME_TERMINAL")
        if type(refs) is not list or not 0<=len(refs)<=len(rows)<=128:raise InputRefused("ROW_COUNT")
        expected={str(i).zfill(5)+".json" for i in range(len(refs))}
        if {p.name for p in folder.iterdir()}!=expected:raise InputRefused("ROW_FILE_SET")
        terminals=[]
        for i,ref in enumerate(refs):
            fields(ref,REF)
            if type(ref["index"]) is not int or ref["index"]!=i:raise InputRefused("ROW_ORDER")
            item=read_row(root,ref,rows[i],pid=pid,work=work);terminals.append(item["terminal"])
        unreached=outcome["unreached_rows"]
        if type(unreached) is not list or any(type(i) is not int for i in unreached):
            raise InputRefused("UNREACHED_ROWS")
        if unreached!=list(range(len(refs),len(rows))):raise InputRefused("UNREACHED_ROWS")
        if any(t!="CHECKED" for t in terminals[:-1]):raise InputRefused("ROW_AFTER_FAILURE")
        if outcome["terminal"]=="CHECKED" and (len(refs)!=len(rows) or any(t!="CHECKED" for t in terminals)):
            raise InputRefused("ROW_FALSE_COMPLETE")
        if {p.name for p in folder.iterdir()}!=expected:raise InputRefused("ROW_FILE_SET_CHANGED")
        return {"terminal":"ROW_CUSTODY_PASS","rows":len(refs),"work":work}
    finally:
        work["readback_wall_s"]=time.monotonic()-start;work["readback_cpu_s"]=time.process_time()-cpu
