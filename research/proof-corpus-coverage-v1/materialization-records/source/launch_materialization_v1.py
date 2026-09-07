"""One source-bound materialization launch continuing the original V2 episode."""
from pathlib import Path
from hashlib import sha256
import json,os,resource,subprocess,sys,time
import xml.etree.ElementTree as ET

BASE=Path('/home/billy/orion-director-work/20260907')
PACKAGE=BASE/'ocm-corpus-material/research/proof-corpus-coverage-v1'
EPISODE=BASE/'coverage-material-episode-v2'
OUT=BASE/'coverage-materialization-v1'
ENV=BASE/'coverage-materialization-envelope-v1'
PYTHON='/home/billy/.local/share/uv/python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11'
def record(path):
    path=Path(path);raw=path.read_bytes()
    return dict(path=str(path),sha256=sha256(raw).hexdigest(),bytes=len(raw))
def save(name,value):
    with (ENV/name).open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n')
def verify(value):
    assert record(value['path'])==value,value['path']

ENV.mkdir();qualified={};evidence=[]
qroot=BASE/'materialize-entry-qualification-v1/01-focused'
proc=json.loads((qroot/'PROCESS.json').read_bytes())
assert record(qroot/'PROCESS.json')['sha256']=='3023297111e03879604cca62142348487450f7ec2316bf2c551ed91aebf1f1d4'
assert proc['returncode']==0 and proc['source_unchanged'] is True
assert proc['counts']==dict(tests=47,errors=0,failures=0,skipped=0)
for r in proc['raw'].values():verify(r);evidence.append(r)
before=json.loads((qroot/'SOURCE-BEFORE.json').read_bytes())
assert (qroot/'SOURCE-BEFORE.json').read_bytes()==(qroot/'SOURCE-AFTER.json').read_bytes()
assert len(before)==23
for name,r in before.items():verify(r);qualified[name+'.py']=r
for directory,count in [(qroot,47),(BASE/'materialize-review-repair-v1/02-green',26)]:
    xml=directory/'tests.xml';suites=list(ET.parse(xml).getroot().iter('testsuite'))
    assert sum(int(s.attrib['tests']) for s in suites)==count
    assert all(int(s.attrib.get(k,0))==0 for s in suites for k in ('errors','failures','skipped'))
    evidence.extend([record(directory/'PROCESS.json'),record(xml)])
old=json.loads((BASE/'materialize-review-repair-v1/02-green/PROCESS.json').read_bytes())
assert old['returncode']==0 and old['sources_before']==old['sources_after']
for n,b in old['sources_before'].items():
    r=record(PACKAGE/n);assert {k:r[k] for k in ('sha256','bytes')}==b
    qualified[n]=r
start_record=record(EPISODE/'STARTED.json')
assert start_record['sha256']=='735f3bca0600a55cd5ddc6c7678f79ea5399ef7b1fd0ce6ba007958e73b4f3af'
start=json.loads((EPISODE/'STARTED.json').read_bytes())
def clock_ok():
    verify(start_record)
    assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==start['boot_id']
    assert start['monotonic_seconds']<=time.monotonic()<start['whole_deadline_monotonic']
clock_ok()
argv=[PYTHON,'-I','-S',str(PACKAGE/'materialize_run.py'),
      str(BASE/'proof-corpus-coverage-registration-20260907-v1'),str(EPISODE),
      str(BASE/'proof-corpus-source-aa2d8b3.git'),str(OUT)]
assert not OUT.exists()
save('PRELAUNCH.json',dict(argv=argv,environment={},source=qualified,qualification=evidence,
     python=record(PYTHON),launcher=record(__file__),original_start=start_record,
     original_whole_deadline_monotonic=start['whole_deadline_monotonic'],
     review='Root reviewed current boot/run/worker/phase/custody; bootstrap and stream/command custody repairs are included in47 controls.26 original materializer controls retain separate qualification.',
     scope='One actual shared cold preparation; no new episode, no reset/retry or semantic build credit. All waiting/preparation consumes original V2clock.'))
wait_start=time.monotonic();eligible=False
with (ENV/'scheduling.jsonl').open('x') as f:
    while time.monotonic()-wait_start<=300:
        clock_ok()
        memory=next(int(x.split()[1])*1024 for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
        stat=os.statvfs(BASE);free=stat.f_bavail*stat.f_frsize
        eligible=memory>=24*2**30 and free>=224*2**30
        f.write(json.dumps(dict(unix_seconds=time.time(),elapsed_s=time.monotonic()-wait_start,
                    memory_available_bytes=memory,disk_free_bytes=free,eligible=eligible))+'\n');f.flush()
        if eligible:break
        time.sleep(min(5,max(.001,start['whole_deadline_monotonic']-time.monotonic())))
save('SCHEDULING.json',dict(eligible=eligible,wall_s=time.monotonic()-wait_start,raw=record(ENV/'scheduling.jsonl')))
if not eligible:
    save('NO-LAUNCH.json',dict(state='NOT_DISPATCHED',cause='REGISTERED_INITIAL_HEADROOM_UNAVAILABLE',
         materialization_created=OUT.exists(),episode_clock_reset=False))
    print('Materialization not dispatched; retained headroom scheduling record.',flush=True);sys.exit(2)
for r in qualified.values():verify(r)
clock_ok();began=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
print('Starting one exact materialization continuation.',flush=True)
with (ENV/'stdout.bin').open('xb') as so,(ENV/'stderr.bin').open('xb') as se:
    p=subprocess.run(argv,env={},stdin=subprocess.DEVNULL,stdout=so,stderr=se,check=False)
after=resource.getrusage(resource.RUSAGE_CHILDREN)
save('PROCESS.json',dict(returncode=p.returncode,wall_including_phase_receipts_s=time.monotonic()-began,
     child_user_s=after.ru_utime-before.ru_utime,child_system_s=after.ru_stime-before.ru_stime,
     nonaggregate_child_peak_rss_kib=after.ru_maxrss,stdout=record(ENV/'stdout.bin'),stderr=record(ENV/'stderr.bin'),
     phase=record(OUT/'MATERIALIZATION.json') if (OUT/'MATERIALIZATION.json').is_file() else None,
     original_start_after=record(EPISODE/'STARTED.json')))
print((ENV/'stdout.bin').read_text(),flush=True)
sys.exit(p.returncode)
