"""Authored offline Lake commissioning fixture; does not select or build corpus rows."""
from pathlib import Path
from hashlib import sha256
import json,os,subprocess,time
from resource_contract import record,write_json
from build_profile_policy import inventory

REQUIRED=("root-build/lib/lean/Fixture.olean","root-build/ir/Fixture.c",
          "dep-build/lib/lean/Authored.olean","dep-build/ir/Authored.c")

def git(root,cwd,*args):
 out=root/"setup";out.mkdir(exist_ok=True);index=len(list(out.glob("*.json")))
 argv=["/usr/bin/git","-c","core.hooksPath=/dev/null","-c","credential.helper=",*args]
 env={"PATH":"/usr/bin","HOME":str(root/"home"),"GIT_CONFIG_NOSYSTEM":"1","LANG":"C",
      "GIT_AUTHOR_DATE":"2000-01-01T00:00:00+0000","GIT_COMMITTER_DATE":"2000-01-01T00:00:00+0000"}
 start=time.monotonic();r={"argv":argv,"cwd":str(cwd),"environment":env}
 try:
  p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=10)
  r.update(returncode=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode())
  if p.returncode:raise ValueError("authored Git preparation failed")
  return p.stdout.decode().strip()
 except BaseException as e:
  r["error"]={"class":type(e).__name__,"message":str(e)}
  if isinstance(e,subprocess.TimeoutExpired):
   r.update(stdout=(e.stdout or b"").decode(errors="replace"),stderr=(e.stderr or b"").decode(errors="replace"))
  raise
 finally:
  r["wall_s"]=time.monotonic()-start;write_json(out/(str(index)+".json"),r)

def create_fixture(root):
 root=Path(root).resolve();root.mkdir();start=time.monotonic()
 source=root/"workspace";dep=source/".lake/packages/authored";dep.mkdir(parents=True)
 files={"Authored.lean":"def authoredValue : Nat := 7\ntheorem authoredIdentity (n : Nat) : n = n := rfl\n",
        "lakefile.lean":"import Lake\nopen Lake DSL\npackage authored\nlean_lib Authored\n",
        "lean-toolchain":"leanprover/lean4:v4.33.1\n",".gitignore":".lake/\n"}
 for name,value in files.items():(dep/name).write_text(value)
 git(root,dep,"init","--template=");git(root,dep,"add","--",".")
 git(root,dep,"-c","user.name=OCM Authored Fixture","-c","user.email=fixture@example.invalid","commit","-m","authored fixture")
 rev=git(root,dep,"rev-parse","HEAD");git(root,dep,"checkout","--detach",rev)
 (source/"lakefile.lean").write_text('import Lake\nopen Lake DSL\npackage fixture\nrequire authored from git "https://example.invalid/authored" @ "'+rev+'"\nlean_lib Fixture\n')
 (source/"Fixture.lean").write_text("import Authored\ntheorem fixtureIdentity (n : Nat) : n = n := authoredIdentity n\ndef fixtureValue : Nat := authoredValue\n")
 (source/"lean-toolchain").write_text(files["lean-toolchain"])
 write_json(source/"lake-manifest.json",{"version":"1.2.0","name":"fixture","packagesDir":".lake/packages",
  "packages":[{"name":"authored","scope":"","inherited":False,"type":"git","url":"https://example.invalid/authored",
               "rev":rev,"inputRev":rev,"subDir":None,"configFile":"lakefile.lean","manifestFile":"lake-manifest.json"}]})
 for path in (source/".lake/config",source/".lake/build",source/".lake/cache",dep/".lake/build"):path.mkdir(parents=True,exist_ok=True)
 for name in ("scratch","config","root-build","dep-build","cache"):(root/name).mkdir()
 (root/"scratch/home").mkdir()
 data={"schema":"ocm.authored-lake-fixture.v1","root":str(root),"workspace":str(source),
       "dependency_revision":rev,"source_inventory":inventory(source),"preparation_wall_s":time.monotonic()-start}
 write_json(root/"source-inventory.json",data["source_inventory"]);write_json(root/"fixture.json",data)
 return data

def make_profile(data,files,materials,bwrap,aa_exec):
 root=Path(data["root"])
 mounts=[("scratch","/work"),("config","/workspace/.lake/config"),("root-build","/workspace/.lake/build"),
         ("dep-build","/workspace/.lake/packages/authored/.lake/build"),("cache","/workspace/.lake/cache")]
 return {"schema":"ocm.f1.build-profile.v1","bwrap":bwrap,"aa_exec":aa_exec,"files":files,
  "materials":[*materials,{"path":data["workspace"],"guest":"/workspace","inventory":record(root/"source-inventory.json")}],
  "writable":[{"path":str(root/name),"guest":guest} for name,guest in mounts],
  "environment":{"PATH":"/lean/bin:/usr/bin","HOME":"/work/home","TMPDIR":"/tmp","LEAN_SYSROOT":"/lean",
                 "LEAN_NUM_THREADS":"2","LANG":"C.UTF-8","LC_ALL":"C.UTF-8"},
  "argv":["/lean/bin/lake","--dir","/workspace","--no-cache","--keep-toolchain","--rehash","--verbose","build","+Fixture:olean"]}

def assess(data,receipt):
 root=Path(data["root"]);errors=[];outputs={}
 try:
  if inventory(data["workspace"])!=data["source_inventory"]:errors.append("SOURCE_OR_GIT_DRIFT")
  d=receipt.get("dispatch",{});c=d.get("cleanup",{})
  if receipt.get("terminal")!="COMPLETED" or receipt.get("post_input_custody")!="UNCHANGED":errors.append("PROFILE_INCOMPLETE")
  if type(d.get("returncode")) is not int or d["returncode"]!=0:errors.append("RETURN_CODE")
  if not all(c.get(k) is True for k in ("members_empty","reaped","controllers_removed")):errors.append("CLEANUP")
  if d.get("evidence_complete") is not True:errors.append("EVIDENCE_INCOMPLETE")
  for name in REQUIRED:
   path=root/name
   if not path.is_file() or path.is_symlink() or path.stat().st_size==0:errors.append("MISSING_OUTPUT:"+name)
   else:outputs[name]=record(path)
 except (OSError,ValueError) as e:errors.append(type(e).__name__+":"+str(e))
 return {"schema":"ocm.authored-lake-result.v1","terminal":"LAKE_BUILD_REFUSED" if errors else "AUTHORED_LAKE_BUILD_PASS",
         "errors":errors,"required_outputs":outputs,"scope":"Authored two-package offline build only; no corpus, proof-search or whole-OCM qualification."}
