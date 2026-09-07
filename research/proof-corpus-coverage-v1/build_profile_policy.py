"""Closed mount inventories and a named non-executable-output AppArmor profile."""
from pathlib import Path
import os,re
from resource_contract import record
def guest_path(value):
 if type(value) is not str or not re.fullmatch(r"/[A-Za-z0-9_./+-]+",value):raise ValueError("unsafe guest path")
 if value=="/" or Path(value).as_posix()!=value or any(x in ("",".","..") for x in value.split("/")[1:]):raise ValueError("noncanonical guest path")
 return value
def scan_error(exc):raise exc
def inventory(root):
 root=Path(root).resolve(strict=True);result={}
 for base,dirs,files in os.walk(root,followlinks=False,onerror=scan_error):
  for name in sorted(dirs+files):
   p=Path(base)/name;rel=str(p.relative_to(root))
   if p.is_symlink():
    if not p.resolve(strict=True).is_relative_to(root):raise ValueError("material symlink escapes root")
    result[rel]={"type":"symlink","target":os.readlink(p)}
   elif p.is_dir():result[rel]={"type":"directory"}
   elif p.is_file():
    r=record(p);result[rel]={"type":"file","sha256":r["sha256"],"bytes":r["bytes"]}
   else:raise ValueError("special material file")
 return result
def verify_inventory(root,expected):
 if inventory(root)!=expected:raise ValueError("material inventory drift")
def apparmor_policy(name,files,materials,writable):
 if not re.fullmatch("[a-z][a-z0-9-]{5,63}",name):raise ValueError("invalid profile token")
 lines=["profile ocm-f1-"+name+" flags=(attach_disconnected,mediate_deleted) {",
  "  deny network,","  signal (send, receive),","  /proc/** r,","  /dev/null rw,",
  "  /dev/urandom r,","  /dev/random r,","  /tmp/ rw,","  /tmp/** rwkl,"]
 for item in files:
  access={"executable":"rmix","library":"mr","read":"r"}[item["access"]]
  lines.append("  "+guest_path(item["guest"])+" "+access+",")
 for path in materials:
  path=guest_path(path);lines.extend(["  "+path+"/ r,","  "+path+"/** r,"])
 for path in writable:
  path=guest_path(path);lines.extend(["  "+path+"/ rw,","  "+path+"/** rwkl,"])
 return "\n".join(lines+["}",""])
