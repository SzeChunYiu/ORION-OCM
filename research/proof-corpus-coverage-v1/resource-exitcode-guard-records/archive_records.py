"""Create-only deterministic correction archives; all resource source remains inert data."""
from pathlib import Path
import gzip,hashlib,io,json,os,stat,tarfile,time
BASE=Path('/home/billy/orion-director-work/20260907')
PACKAGE=BASE/'ocm-proof-corpus-coverage/research/proof-corpus-coverage-v1'
DEST=PACKAGE/'resource-exitcode-records'
QUAL=BASE/'resource-exitcode-qualification-v1'
DEV=BASE/'resource-exitcode-development-v1'
PRIOR=PACKAGE/'resource-successor-records'

def raw(value):return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
def binding(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def put(name,data):
    p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data)
def inventory(root):
    files={};aliases=[]
    def fail(e):raise e
    for directory,dirs,names in os.walk(root,followlinks=False,onerror=fail):
        for name in dirs+names:
            path=Path(directory)/name;mode=path.lstat().st_mode;relative=path.relative_to(root).as_posix()
            if stat.S_ISLNK(mode):
                target=os.readlink(path);aliases.append({'path':relative,'target':target,'target_text_binding':binding(os.fsencode(target))})
            elif stat.S_ISREG(mode):files[relative]=binding(path.read_bytes())
            elif not stat.S_ISDIR(mode):raise ValueError('nonregular input '+str(path))
        dirs[:]=[name for name in dirs if not (Path(directory)/name).is_symlink()]
    return files,sorted(aliases,key=lambda x:x['path'])
def archive(name,root):
    start=time.monotonic();members,aliases=inventory(root);path=DEST/name
    with path.open('xb') as sink:
        with gzip.GzipFile(fileobj=sink,mode='wb',mtime=0,filename='') as compressed:
            with tarfile.open(fileobj=compressed,mode='w',format=tarfile.PAX_FORMAT) as tar:
                for relative,expected in sorted(members.items()):
                    data=(root/relative).read_bytes()
                    assert binding(data)==expected
                    item=tarfile.TarInfo(relative);item.size=len(data);item.mode=0o644;item.uid=item.gid=item.mtime=0
                    tar.addfile(item,io.BytesIO(data))
    with tarfile.open(path,mode='r:gz',ignore_zeros=True) as tar:
        observed={}
        for item in tar:
            assert item.isreg() and item.name not in observed
            observed[item.name]=binding(tar.extractfile(item).read())
    assert observed==members
    assert inventory(root)==(members,aliases)
    map_name=name.removesuffix('.tar.gz')+'.members.json';map_raw=raw(members);put(map_name,map_raw)
    return {'archive':name,**binding(path.read_bytes()),'members':len(members),
            'raw_bytes':sum(r['bytes'] for r in members.values()),
            'member_map':{'file':map_name,**binding(map_raw)},'original_root':str(root),
            'pack_and_verified_readback_wall_s':time.monotonic()-start},aliases

started=time.monotonic();DEST.mkdir(exist_ok=False)
prior_seal=(PRIOR/'SEAL.json').read_bytes()
assert binding(prior_seal)['sha256']=='3d900f8700445844c1b3c926a1ff150f702c43f841e94a208608ff171645d8c7'
prior_files=json.loads(prior_seal)['files']
for name,row in prior_files.items():assert binding((PRIOR/name).read_bytes())==row
prior_freeze=json.loads((PRIOR/'SOURCE_FREEZE.json').read_bytes())
prior_map=json.loads((PRIOR/'final-qualification.members.json').read_bytes())
reconstruction={}
with tarfile.open(PRIOR/'final-qualification.tar.gz',mode='r:gz',ignore_zeros=True) as tar:
    for name,row in prior_freeze['files'].items():
        member='source/'+name;data=tar.extractfile(member).read();expected={k:row[k] for k in ('bytes','sha256')}
        assert binding(data)==expected==prior_map[member]
        put('prior-source/'+name,data)
        reconstruction[name]={'archive':'resource-successor-records/final-qualification.tar.gz','member':member,**expected}
assert len(reconstruction)==22
put('PRIOR-SOURCE.json',raw({'schema':'ocm.f1.prior-source-reconstruction.v1','files':reconstruction,
    'prior_seal_sha256':binding(prior_seal)['sha256'],'scope':'Exact archived bytes; never relabeled as corrected current source'}))
rows=[];omitted={}
for name,root in [('final-qualification.tar.gz',QUAL),('development-history.tar.gz',DEV)]:
    row,aliases=archive(name,root);rows.append(row);omitted[str(root)]=aliases
assert [r['members'] for r in rows]==[496,385]
for source,name in [('SOURCE_FREEZE.json','SOURCE_FREEZE.json'),('QUALIFICATION-SUMMARY.json','RESULT.json'),
                    ('COSTS.json','COSTS.json'),('HOST-INPUTS.json','HOST-INPUTS.json')]:put(name,(QUAL/source).read_bytes())
freeze=json.loads((DEST/'SOURCE_FREEZE.json').read_bytes());assert freeze['count']==23
for name,row in freeze['files'].items():
    expected={k:row[k] for k in ('bytes','sha256')}
    assert binding((PACKAGE/name).read_bytes())==expected==binding((QUAL/'source'/name).read_bytes())
audit=BASE/'resource-exitcode-independent-audit-v1/AUDIT.json';audit_raw=audit.read_bytes()
assert binding(audit_raw)['sha256']=='589bb4a82e9caad4c79d01c9aef260fb0e6e7185bb82472b2edb6d4a811d23bf'
put('INDEPENDENT-AUDIT.json',audit_raw)
put('OMITTED-ALIASES.json',raw({'schema':'ocm.f1.omitted-symlink-aliases.v1','roots':omitted,
    'scope':'Symlink metadata retained; never followed or archived as executable paths. All regular files retained.'}))
put('INDEX.json',raw({'schema':'ocm.f1.resource-exitcode-index.v1','archives':rows,
    'historical':{'seal_sha256':binding(prior_seal)['sha256'],'source_dir':'prior-source','source_count':22},
    'source_freeze':binding((DEST/'SOURCE_FREEZE.json').read_bytes()),'result':binding((DEST/'RESULT.json').read_bytes()),
    'omissions':{'file':'HOST-INPUTS.json',**binding((DEST/'HOST-INPUTS.json').read_bytes()),
                'scope':'External host inputs are metadata only and not revalidated by portable custody; prior fixture binaries remain in the original resource development archive.'}}))
for name,row in prior_files.items():assert binding((PRIOR/name).read_bytes())==row
assert (PRIOR/'SEAL.json').read_bytes()==prior_seal
put('PACKAGING.json',raw({'schema':'ocm.f1.exitcode-packaging.v1','source':binding(Path(__file__).read_bytes()),
    'archive_members':sum(r['members'] for r in rows),'archive_raw_bytes':sum(r['raw_bytes'] for r in rows),
    'archive_compressed_bytes':sum(r['bytes'] for r in rows),'archived_originals_rehashed_after_copy':True,
    'prior_package_unchanged':True,'omitted_symlink_aliases':sum(map(len,omitted.values())),
    'packaging_wall_s_before_record_and_seal':time.monotonic()-started,
    'scope':'Packaging and byte verification only; no resource/native/corpus dispatch. Native C fixture execution belongs to the earlier recorded qualification.'}))
print(json.dumps({'destination':str(DEST),'archives':rows,'omitted_aliases':sum(map(len,omitted.values())),
                  'source_freeze':binding((DEST/'SOURCE_FREEZE.json').read_bytes()),'seal_written':False},sort_keys=True))
