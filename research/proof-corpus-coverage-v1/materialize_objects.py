"""Deadline-bound local Git plumbing; all process streams retained. No repository commands."""
import hashlib,json,math,os,re,selectors,signal,subprocess,time
from pathlib import Path

def save(path,value):
 with Path(path).open("x") as f:json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write("\n")

def remaining(deadline):
 if type(deadline) not in (int,float) or not math.isfinite(deadline):raise ValueError("MATERIALIZE_DEADLINE")
 left=deadline-time.monotonic()
 if left<=0:raise TimeoutError("MATERIALIZE_DEADLINE")
 return left

def stamp(path):
 p=Path(path);h=hashlib.sha256();size=0
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1024**2),b""):h.update(b);size+=len(b)
 return {"sha256":h.hexdigest(),"bytes":size}

def file_map(root,deadline=None):
 root=Path(root);result={}
 if root.is_symlink() or not root.is_dir():raise ValueError("MATERIAL_KIND")
 def fail(exc):raise exc
 for base,dirs,files in os.walk(root,followlinks=False,onerror=fail):
  for n in dirs+files:
   p=Path(base)/n
   if deadline is not None:remaining(deadline)
   if p.is_symlink() or not (p.is_dir() or p.is_file()):raise ValueError("MATERIAL_KIND")
   if p.is_file():result[str(p.relative_to(root))]=stamp(p)
 return result

class Git:
 def __init__(self,git_dir,records,deadline,commands):
  self.git_dir,self.records,self.deadline,self.commands=Path(git_dir),Path(records),deadline,commands
  self.env={"PATH":"/usr/bin","HOME":str(records),"GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":"/dev/null",
   "GIT_CONFIG_SYSTEM":"/dev/null","GIT_NO_REPLACE_OBJECTS":"1","GIT_NO_LAZY_FETCH":"1",
   "GIT_OPTIONAL_LOCKS":"0","GIT_TERMINAL_PROMPT":"0","GIT_ALLOW_PROTOCOL":"","LC_ALL":"C"}
  self.base=["/usr/bin/git","--no-pager","--no-replace-objects","-c","protocol.allow=never",
   "-c","core.hooksPath=/dev/null","-c","core.fsmonitor=false","-c","core.autocrlf=false",
   "-c","credential.helper=","-c","gc.auto=0","--git-dir="+str(git_dir)]

 def start(self,args,pipe=False):
  remaining(self.deadline);folder=self.records/("%03d"%len(self.commands));folder.mkdir()
  c={"argv":self.base+list(args),"environment":self.env,"attempted":False,"pid":None,"returncode":None}
  self.commands.append(c);save(folder/"REQUEST.json",c)
  c["record"]=str(folder);streams=[(folder/(n+".bin")).open("xb") for n in ("stdin","stdout","stderr")]
  began=time.monotonic();p=None
  try:
   c["attempted"]=True
   if pipe:
    p=subprocess.Popen(c["argv"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=streams[2],
                       env=self.env,cwd=self.records,start_new_session=True)
   else:
    p=subprocess.Popen(c["argv"],stdin=subprocess.DEVNULL,stdout=streams[1],stderr=streams[2],
                       env=self.env,cwd=self.records,start_new_session=True)
   c["pid"]=p.pid
  except BaseException as e:
   c["error"]=type(e).__name__+":"+str(e);self.finish(p,c,streams,began)
   raise
  return p,c,streams,began

 def finish(self,p,c,streams,began):
  try:
   if p is not None:
    if p.poll() is None:
     try:p.wait(timeout=max(0.001,min(2,self.deadline-time.monotonic())))
     except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=2)
    c["returncode"]=p.returncode;c["reaped"]=p.poll() is not None
    try:os.killpg(p.pid,0)
    except ProcessLookupError:c["group_absent"]=True
    else:c["group_absent"]=False
  except BaseException as e:c["cleanup_error"]=type(e).__name__+":"+str(e)
  finally:
   c["stdout_tail_bytes"]=0;c["stdout_complete"]=p is not None and p.poll() is not None
   if p is not None and p.stdout is not None:
    os.set_blocking(p.stdout.fileno(),False);end=time.monotonic()+2
    while time.monotonic()<end:
     try:b=os.read(p.stdout.fileno(),65536)
     except BlockingIOError:c["stdout_complete"]=False;break
     if not b:break
     streams[1].write(b);c["stdout_tail_bytes"]+=len(b)
    else:c["stdout_complete"]=False
   for stream in streams:stream.close()
   c["wall_s"]=time.monotonic()-began
   folder=Path(c["record"]);c["streams"]={n:stamp(folder/(n+".bin")) for n in ("stdin","stdout","stderr")}
   save(folder/"RESULT.json",c)

 def run(self,*args):
  p,c,streams,began=self.start(args)
  try:p.wait(timeout=remaining(self.deadline))
  except BaseException as e:c["error"]=type(e).__name__+":"+str(e);raise
  finally:self.finish(p,c,streams,began)
  if c["returncode"]!=0 or not c.get("group_absent") or c.get("cleanup_error") or not c.get("stdout_complete"):raise ValueError("GIT_COMMAND_FAILED")
  return Path(c["record"])/"stdout.bin"

class Objects:
 def __init__(self,git):self.git=git;self.buffer=bytearray();self.objects=[]
 def __enter__(self):
  self.p,self.c,self.streams,self.began=self.git.start(["cat-file","--batch"],True)
  self.selector=None
  try:
   self.selector=selectors.DefaultSelector();self.selector.register(self.p.stdout,selectors.EVENT_READ)
  except BaseException as error:
   self.c["error"]=type(error).__name__+":"+str(error)
   try:self.p.stdin.close()
   except (BrokenPipeError,OSError):pass
   if self.selector is not None:
    try:self.selector.close()
    except BaseException as cleanup:self.c["selector_cleanup_error"]=type(cleanup).__name__+":"+str(cleanup)
   try:self.git.finish(self.p,self.c,self.streams,self.began)
   finally:self.p.stdout.close()
   raise
  return self
 def fill(self):
  if not self.selector.select(remaining(self.git.deadline)):raise TimeoutError("MATERIALIZE_DEADLINE")
  b=os.read(self.p.stdout.fileno(),65536)
  if not b:raise ValueError("OBJECT_STREAM_TRUNCATED")
  self.streams[1].write(b);self.buffer.extend(b)
 def take(self,n):
  while len(self.buffer)<n:self.fill()
  b=bytes(self.buffer[:n]);del self.buffer[:n];return b
 def line(self):
  while b"\n" not in self.buffer:
   if len(self.buffer)>256:raise ValueError("OBJECT_HEADER")
   self.fill()
  pos=self.buffer.index(10)+1
  if pos>256:raise ValueError("OBJECT_HEADER")
  return self.take(pos)
 def read(self,oid,kind,dest,maximum=None):
  if not re.fullmatch("[0-9a-f]{40}",oid):raise ValueError("OBJECT_ID")
  remaining(self.git.deadline);request=(oid+"\n").encode()
  self.streams[0].write(request);self.p.stdin.write(request);self.p.stdin.flush()
  header=self.line();match=re.fullmatch(rb"([0-9a-f]{40}) (blob|tree|commit) ([0-9]+)\n",header)
  if match is None or match[1].decode()!=oid or match[2].decode()!=kind:raise ValueError("OBJECT_HEADER")
  size=int(match[3])
  if maximum is not None and size>maximum:raise ValueError("METADATA_SIZE_BOUND")
  h=hashlib.sha1(kind.encode()+b" "+str(size).encode()+b"\0");s=hashlib.sha256();left=size
  with Path(dest).open("xb") as f:
   while left:
    remaining(self.git.deadline);b=self.take(min(left,65536));f.write(b);h.update(b);s.update(b);left-=len(b)
  if self.take(1)!=b"\n" or h.hexdigest()!=oid:raise ValueError("OBJECT_IDENTITY")
  value={"oid":oid,"kind":kind,"bytes":size,"sha256":s.hexdigest(),"path":str(dest)}
  self.objects.append(value);return value
 def __exit__(self,typ,error,tb):
  if error is not None:self.c["error"]=type(error).__name__+":"+str(error)
  try:self.p.stdin.close()
  except (BrokenPipeError,OSError):pass
  self.selector.close();self.git.finish(self.p,self.c,self.streams,self.began);self.p.stdout.close()
  if error is None and (self.c["returncode"]!=0 or self.c.get("cleanup_error") or not self.c.get("group_absent") or not self.c.get("stdout_complete") or self.buffer or self.c.get("stdout_tail_bytes")):
   raise ValueError("OBJECT_PROCESS_FAILED")
