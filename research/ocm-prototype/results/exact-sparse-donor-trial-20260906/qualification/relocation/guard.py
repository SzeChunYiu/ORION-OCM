import os,runpy,sys
from pathlib import Path
denied=__import__('json').loads(sys.argv[1]);script=sys.argv[2];args=sys.argv[3:]
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
        p=str(Path(os.fsdecode(args[0])).resolve())
        if any(p==root or p.startswith(root+'/') for root in denied):raise PermissionError('ORIGINAL_PATH_READ_REFUSED:'+p)
sys.addaudithook(audit)
try:open(denied[0]+'/MANIFEST.json')
except PermissionError:print('AUDIT_ORIGINAL_PATH_BLOCKED',flush=True)
else:raise RuntimeError('audit negative control did not refuse')
sys.path.insert(0,str(Path(script).parent));sys.argv=[script]+args
runpy.run_path(script,run_name='__main__')
