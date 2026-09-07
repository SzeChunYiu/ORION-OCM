"""Trusted file entry / parent source-loaded bootstrap; never imports owned bytecode."""
from pathlib import Path
from hashlib import sha256
import json,sys,types,importlib.util
HERE=Path(__file__).resolve().parent
MODULES=("resource_contract","resource_pidfd","resource_cgroup","resource_monitor",
 "resource_runner","build_profile_policy","build_profile","resource_install")
def binding(path,data):
 return {"path":str(path),"sha256":sha256(data).hexdigest(),"bytes":len(data)}
def load():
 sys.modules["resource_boot"]=sys.modules[__name__]
 sources={name:(HERE/(name+".py")).read_bytes() for name in MODULES}
 result={}
 for name,data in sources.items():
  path=HERE/(name+".py");module=types.ModuleType(name);module.__file__=str(path)
  module.__spec__=importlib.util.spec_from_loader(name,loader=None,origin=str(path))
  module.__source_record__=binding(path,data);sys.modules[name]=module
  exec(compile(data,str(path),"exec"),module.__dict__);result[name]=module
 return result
def loaded_sources(namespace):
 expected=namespace.get("__source_record__")
 if expected is None:raise ValueError("SOURCE_ONLY_ENTRY_REQUIRED")
 own=Path(namespace["__file__"])
 if binding(own,own.read_bytes())!=expected:raise ValueError("loaded source drift")
 records={}
 for name in MODULES:
  module=sys.modules.get(name);r=getattr(module,"__source_record__",None)
  path=HERE/(name+".py")
  if r is None or r!=binding(path,path.read_bytes()):raise ValueError("loaded module binding drift: "+name)
  records[name]=r
 records["resource_boot"]=binding(Path(__file__),Path(__file__).read_bytes())
 return records
def main():
 import argparse
 parser=argparse.ArgumentParser()
 parser.add_argument("mode",choices=("check-sources","run","install"))
 parser.add_argument("--profile");parser.add_argument("--limits");parser.add_argument("--output")
 args=parser.parse_args();modules=load()
 if args.mode=="check-sources":
  value={"loaded_from":"RAW_SOURCE_BYTES","sources":loaded_sources(modules["build_profile"].__dict__)}
 elif args.mode=="install":value=modules["resource_install"].install(args.output)
 else:
  profile=json.loads(Path(args.profile).read_bytes());limits=json.loads(Path(args.limits).read_bytes())
  value=modules["build_profile"].run(profile,limits,args.output)
 print(json.dumps(value,sort_keys=True))
 if args.mode!="check-sources" and value["terminal"] not in ("COMPLETED","SCOPED_HELPER_INSTALLED"):return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
