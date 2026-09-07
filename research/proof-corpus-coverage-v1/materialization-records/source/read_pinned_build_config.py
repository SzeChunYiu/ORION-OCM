"""Read pinned build configuration as data; no package or semantic execution."""
from pathlib import Path
import hashlib,json,os,resource,subprocess,time

BASE=Path('/home/billy/orion-director-work/20260907')
EPISODE=BASE/'coverage-material-episode-v2'
OUT=BASE/'coverage-build-config-review-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,v):
    with p.open('x') as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n')
def main():
    began=time.monotonic();cpu=resource.getrusage(resource.RUSAGE_CHILDREN)
    start_raw=(EPISODE/'STARTED.json').read_bytes();start=json.loads(start_raw)
    phase_raw=(EPISODE/'ACQUISITION.json').read_bytes()
    assert sha(phase_raw)=='ae12fc94b684efe07dbb0dc41bb2f5d451fbeafed86220947df2d2ffd2b3e636'
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    assert boot==start['boot_id'] and start['monotonic_seconds']<began<start['whole_deadline_monotonic']
    lock_raw=(EPISODE/'lake-manifest.json').read_bytes()
    assert sha(lock_raw)=='435fe2ab2550e2b82c0a93fd421c96d197d6dd55bc739481e2a4a07e04b979bf'
    packages=json.loads(phase_raw)['worker']['packages']
    assert len(packages)==9 and json.loads(phase_raw)['terminal']=='MATERIAL_READY'
    OUT.mkdir();(OUT/'home').mkdir();(OUT/'commands').mkdir();(OUT/'data').mkdir()
    commands=[];records={};result={'terminal':'CONFIG_READ_REFUSED','semantic_checks':0,
      'episode_start_sha256':sha(start_raw),'acquisition_sha256':sha(phase_raw),
      'whole_deadline_monotonic':start['whole_deadline_monotonic'],'started_monotonic':began,
      'reader_sha256':sha(Path(__file__).read_bytes()),'records':records,'commands':commands,
      'scope':'Read-only engineering inspection of exact Lake configuration data. No package code, proof body, acquisition, materialization or build executed. Existing episode clock continues; this is not a qualified semantic-stage receipt.'}
    def read(repo,commit,path,oidx):
        env={'PATH':'/usr/bin','HOME':str(OUT/'home'),'GIT_CONFIG_NOSYSTEM':'1',
             'GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null',
             'GIT_NO_REPLACE_OBJECTS':'1','GIT_NO_LAZY_FETCH':'1','GIT_OPTIONAL_LOCKS':'0',
             'GIT_ALLOW_PROTOCOL':'','GIT_TERMINAL_PROMPT':'0','LC_ALL':'C'}
        base=['/usr/bin/git','--no-replace-objects','-c','protocol.allow=never',
              '-c','core.hooksPath=/dev/null','-c','core.fsmonitor=false','--git-dir='+str(repo)]
        def call(args):
            index=len(commands);raw=OUT/'commands'/('%03d.out'%index);err=raw.with_suffix('.err')
            record={'argv':base+args,'environment':env};t=time.monotonic();commands.append(record)
            with raw.open('xb') as so,err.open('xb') as se:
                p=subprocess.run(base+args,env=env,cwd=OUT,stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                                 timeout=min(20,start['whole_deadline_monotonic']-time.monotonic()))
            record.update(returncode=p.returncode,wall_s=time.monotonic()-t,
                          stdout={'path':str(raw),'sha256':sha(raw.read_bytes()),'bytes':raw.stat().st_size},
                          stderr={'path':str(err),'sha256':sha(err.read_bytes()),'bytes':err.stat().st_size})
            save(OUT/'commands'/('%03d.json'%index),record)
            assert p.returncode==0,(repo,path,p.returncode)
            return raw.read_bytes()
        oid=call(['rev-parse','--verify',commit+':'+path]).decode().strip()
        assert len(oid)==40 and set(oid)<=set('0123456789abcdef')
        size=int(call(['cat-file','-s',oid]));assert 0<=size<=262144
        data=call(['cat-file','blob',oid])
        assert len(data)==size and hashlib.sha1(('blob '+str(size)+'\0').encode()+data).hexdigest()==oid
        dest=OUT/'data'/('%02d-'%oidx+path);dest.write_bytes(data)
        return {'repo':str(repo),'commit':commit,'source_path':path,'oid':oid,
                'path':str(dest),'sha256':sha(data),'bytes':size}
    try:
        records['corpus']=read(BASE/'proof-corpus-source-aa2d8b3.git','aa2d8b34692b16c70f699536de0d8e75b9a3e9ef','lakefile.lean',0)
        for i,(spec,pkg) in enumerate(zip(json.loads(lock_raw)['packages'],packages),1):
            assert spec['name']==pkg['name'] and spec['rev']==pkg['commit']
            records[spec['name']]=read(Path(pkg['bare_path']),pkg['commit'],spec['configFile'],i)
        assert (EPISODE/'STARTED.json').read_bytes()==start_raw and (EPISODE/'ACQUISITION.json').read_bytes()==phase_raw
        assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
        assert time.monotonic()<start['whole_deadline_monotonic']
        result['terminal']='PINNED_CONFIG_DATA_READ'
    except BaseException as e:result['error']=type(e).__name__+': '+str(e)
    result['wall_before_receipt_s']=time.monotonic()-began
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    result['child_cpu_s']=(after.ru_utime-cpu.ru_utime)+(after.ru_stime-cpu.ru_stime)
    result['git_sha256']=sha(Path('/usr/bin/git').read_bytes())
    save(OUT/'RESULT.json',result)
    print(json.dumps({'terminal':result['terminal'],'configs':len(records),'commands':len(commands),'output':str(OUT),'error':result.get('error')}))
    return 0 if result['terminal']=='PINNED_CONFIG_DATA_READ' else 2
if __name__=='__main__':raise SystemExit(main())
