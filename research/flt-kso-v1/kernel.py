"""R1-only pinned Lean/Init checker. Not an arbitrary Lean-program evaluator.

The whole release archive is pinned; runtime files are hashed before and after
checks. Source is emitted only from the restricted native AST. Three fixed
negative fixtures are evaluator controls, not solver operators. Anthropic R2+
execution is deliberately NOT enabled by this checker.
"""
from __future__ import annotations
from pathlib import Path
import os
import re
import resource
import shutil
import signal
import subprocess
import tempfile
import time
import uuid

from native import emit_source
from substrate import PINS, Refusal, digest_json, sha256

ARCHIVE = {'name':'lean-4.33.1-linux.tar.zst','size':570405234,
           'sha256':'890afd185370f85666025b883914ab4f4b339136f8c96167b69cfb62aecaf235',
           'url':'https://github.com/leanprover/lean4/releases/download/v4.33.1/lean-4.33.1-linux.tar.zst'}
ENVIRONMENT = {'lean':PINS['lean'],'library_profile':'Lean.Init',
               'archive_sha256':ARCHIVE['sha256'],
               'mathlib':'NOT_IMPORTED_OR_REQUIRED_FOR_R1',
               'anthropic':'NO_ANTHROPIC_MODULE_IN_R1_INPUT_OR_SEARCH'}


def _hash_file(path, counter):
    h=__import__('hashlib').sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            counter['bytes_hashed']+=len(block); h.update(block)
    return h.hexdigest()


def clean_environment(home):
    return {'PATH':'/usr/bin:/bin','HOME':str(home),'TMPDIR':str(home),
            'LANG':'C.UTF-8','LC_ALL':'C.UTF-8','LEAN_PATH':str(home)}


def run_process(argv, cwd, timeout=60):
    """Capture an entire process-group deadline; no shell or inherited overrides."""
    before=resource.getrusage(resource.RUSAGE_CHILDREN); start=time.perf_counter()
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        proc=subprocess.Popen(argv,cwd=cwd,env=clean_environment(cwd),
                              stdout=out,stderr=err,start_new_session=True)
        timed_out=False
        try: proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True
            try: os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            proc.wait()
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        out.seek(0); err.seek(0)
        stdout,stderr=out.read(65537),err.read(65537)
    return {'argv':list(map(str,argv)), 'exit_code':proc.returncode,'timed_out':timed_out,
            'stdout':stdout[:65536].decode('utf-8',errors='replace'),
            'stderr':stderr[:65536].decode('utf-8',errors='replace'),
            'output_limit_exceeded':len(stdout)>65536 or len(stderr)>65536,
            'wall_seconds':time.perf_counter()-start,
            'child_cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            'peak_rss_bytes':None}


def accepted_capture(capture):
    return (capture['exit_code']==0 and not capture['timed_out'] and
            not capture['output_limit_exceeded'] and not capture['stderr'].strip() and
            capture['stdout'].strip()=="'FLTMicro.goal' does not depend on any axioms")


class KernelSession:
    def __init__(self, archive: Path | None):
        self.archive=archive; self.temp=None; self.ready=False
        self.metrics={'bytes_hashed':0,'runtime_tree_scans':0,'Lean_checker_calls':0,
                      'control_checker_calls':0,'candidate_checker_calls':0}
        self.report={'terminal':'CANNOT_CHECK_TOOLCHAIN','environment':dict(ENVIRONMENT),
                     'environment_id':digest_json(ENVIRONMENT),'controls':[],'processes':[]}
        self._issued={}

    def _inventory(self):
        self.metrics['runtime_tree_scans']+=1
        inventory={}
        for path in sorted(self.runtime.rglob('*')):
            relative=path.relative_to(self.runtime).as_posix()
            if path.is_symlink():
                resolved=path.resolve()
                if not resolved.is_relative_to(self.runtime):
                    raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH','external runtime symlink')
                inventory[relative]={'symlink':os.readlink(path)}
            elif path.is_file(): inventory[relative]={'sha256':_hash_file(path,self.metrics)}
        return digest_json(inventory)

    def __enter__(self):
        started=time.perf_counter()
        try:
            if self.archive is None or not self.archive.is_file():
                self.report['reason']='Registered Lean 4.33.1 archive unavailable'; return self
            if self.archive.is_symlink() or self.archive.stat().st_size!=ARCHIVE['size'] or _hash_file(self.archive,self.metrics)!=ARCHIVE['sha256']:
                raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH','release archive identity')
            self.temp=tempfile.TemporaryDirectory(prefix='ocm-flt-r1-')
            self.root=Path(self.temp.name)
            copied=self.root/'release.tar.zst'; shutil.copyfile(self.archive,copied)
            if _hash_file(copied,self.metrics)!=ARCHIVE['sha256']:
                raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH','copied archive drift')
            result=run_process(['/usr/bin/tar','--zstd','-xf',str(copied),'-C',str(self.root)],self.root,180)
            self.report['processes'].append(result)
            if result['exit_code'] or result['timed_out']:
                raise Refusal('CANNOT_CHECK_TOOLCHAIN_EXTRACTION')
            self.runtime=self.root/'lean-4.33.1-linux'
            self.lean=self.runtime/'bin/lean'
            self.runtime_digest=self._inventory()
            self.report['extracted_tree_sha256']=self.runtime_digest
            self.report['lean_binary_sha256']=_hash_file(self.lean,self.metrics)
            version=run_process([str(self.lean),'--version'],self.root,30)
            self.report['processes'].append(version)
            if version['exit_code'] or version['timed_out'] or not re.fullmatch(r'Lean \(version 4\.33\.1, [^\n]+\)\s*',version['stdout']):
                raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH','version')
            self.report['version']=version['stdout'].strip()
            fixtures={
                'false_statement': 'theorem goal : False := True.intro\n#print axioms goal\n',
                'injected_axiom': 'axiom injected : False\ntheorem goal : False := injected\n#print axioms goal\n',
                'sorry': 'theorem goal : False := by sorry\n#print axioms goal\n',
            }
            for name,source in fixtures.items():
                capture=self._execute('import Init\nnamespace FLTMicro\n'+source+'end FLTMicro\n',control=True)
                expected_exit=(capture['exit_code']!=0 if name=='false_statement' else capture['exit_code']==0)
                ok=expected_exit and not accepted_capture(capture) and not capture['timed_out'] and not capture['output_limit_exceeded']
                self.report['controls'].append({'id':name,'passed':ok,'capture':capture})
                if not ok: raise Refusal('CANNOT_CHECK_NEGATIVE_CONTROL',name)
            self.ready=True; self.report['terminal']='CHECKER_READY_R1_INIT_ONLY'
        except Refusal as exc:
            self.report['terminal']=exc.terminal; self.report['reason']=str(exc)
        except OSError as exc:
            self.report['terminal']='CANNOT_CHECK_TOOLCHAIN'; self.report['reason']=str(exc)
        finally:
            self.report['preparation_wall_seconds']=time.perf_counter()-started
        return self

    def _execute(self,source,*,control=False):
        if self._inventory()!=self.runtime_digest:
            raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH','runtime changed before call')
        with tempfile.TemporaryDirectory(prefix='candidate-',dir=self.root) as temp:
            work=Path(temp); (work/'Candidate.lean').write_text(source,encoding='utf-8')
            capture=run_process([str(self.lean),'Candidate.lean'],work,60)
        self.metrics['Lean_checker_calls']+=1
        self.metrics['control_checker_calls' if control else 'candidate_checker_calls']+=1
        if self._inventory()!=self.runtime_digest:
            raise Refusal('CHECKER_OR_ENVIRONMENT_MISMATCH','runtime changed after call')
        return capture

    def check(self,formula,term):
        source=emit_source(formula,term)
        if not self.ready:
            return {'terminal':self.report['terminal'],'source_sha256':sha256(source.encode()),
                    'environment_id':digest_json(ENVIRONMENT),'kernel_verified':False}
        try:
            capture=self._execute(source)
            terminal=('CANNOT_CHECK_CHECKER_TIMEOUT' if capture['timed_out'] else
                      'CANNOT_CHECK_CHECKER_OUTPUT_LIMIT' if capture['output_limit_exceeded'] else
                      'KERNEL_VERIFIED_R1_INIT' if accepted_capture(capture) else 'CHECKER_REJECTED')
            result={'terminal':terminal,'source_sha256':sha256(source.encode()),
                    'environment_id':digest_json(ENVIRONMENT),'run_id':uuid.uuid4().hex,
                    'kernel_verified':terminal=='KERNEL_VERIFIED_R1_INIT','capture':capture,
                    'runtime_tree_sha256':self.runtime_digest}
            if result['kernel_verified']:
                self._issued[result['run_id']]=(result,digest_json(result))
            return result
        except Refusal as exc:
            return {'terminal':exc.terminal,'source_sha256':sha256(source.encode()),
                    'environment_id':digest_json(ENVIRONMENT),'kernel_verified':False,'reason':str(exc)}

    def authentic_for(self,result,formula,term):
        if self.ready:
            try:
                if self._inventory()!=self.runtime_digest: return False
            except (Refusal,OSError): return False
        issued=self._issued.get(result.get('run_id'))
        return (self.ready and issued is not None and issued[0] is result and
                issued[1]==digest_json(result) and result['source_sha256']==sha256(emit_source(formula,term).encode()))

    def __exit__(self,*exc):
        self.ready=False; self._issued.clear()
        if self.temp is not None: self.temp.cleanup()
