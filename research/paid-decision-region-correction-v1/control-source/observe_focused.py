"""One child process observer; no imported target/donor code."""
import hashlib,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parent
DEST=ROOT/'records/FOCUSED-01';DEST.mkdir()
argv=[sys.executable,'-I','-S','-B',str(ROOT/'controls/run_focused.py')]
freeze=ROOT/'SOURCE-FREEZE.json'
def ident(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
pins=json.loads(freeze.read_bytes())['files']
def matches(): return {n:ident(ROOT/n)==d for n,d in pins.items()}
before=matches();assert all(before.values())
start=time.perf_counter()
with (DEST/'stdout.log').open('xb') as out,(DEST/'stderr.log').open('xb') as err:
 p=subprocess.Popen(argv,cwd=ROOT,env={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1'},stdout=out,stderr=err)
 pid,status,ru=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
wall=time.perf_counter()-start;after=matches()
receipt={'schema':'paid-drd.dev6-path-focused-process.v1','pid':p.pid,'observer_pid':os.getpid(),
 'reaped':pid==p.pid,'exit_code':p.returncode,'argv':argv,'cwd':str(ROOT),
 'before':before,'after':after,'source_unchanged':before==after and all(after.values()),
 'source_freeze':ident(freeze),'wall_s':wall,'user_s':ru.ru_utime,'system_s':ru.ru_stime,'max_rss_kib':ru.ru_maxrss,
 'stdout':ident(DEST/'stdout.log'),'stderr':ident(DEST/'stderr.log'),
 'child_receipt':ident(DEST/'child/RECEIPT.json') if (DEST/'child/RECEIPT.json').exists() else None}
(DEST/'PROCESS.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(json.dumps({'pid':p.pid,'exit_code':p.returncode,'reaped':pid==p.pid,'source_unchanged':receipt['source_unchanged']}))
raise SystemExit(p.returncode or (0 if receipt['source_unchanged'] else 2))
