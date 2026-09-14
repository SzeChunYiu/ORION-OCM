"""Complete frozen unit membership; source and receipt anchors remain fixed."""
import hashlib
import json
import os
import stat
from pathlib import Path

HERE=Path(__file__).resolve().parent


def digest(data):return hashlib.sha256(data).hexdigest()


def verify(root=HERE):
    root=Path(root);observed={}
    if root.is_symlink():raise ValueError('linked unit root')
    def walk(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                p=Path(entry.path);mode=entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):raise ValueError('symlink member')
                if stat.S_ISDIR(mode):walk(p)
                elif stat.S_ISREG(mode):observed[p.relative_to(root).as_posix()]=p
                else:raise ValueError('nonregular member')
    walk(root)
    initial=observed['MANIFEST_V1.json'].read_bytes()
    manifest=json.loads(initial)
    if set(manifest)!={'schema','files'} or manifest['schema']!='CSG_MANIFEST_V1':
        raise ValueError('manifest schema')
    expected=manifest['files']
    if set(observed)!=set(expected)|{'MANIFEST_V1.json'}:
        raise ValueError('complete membership mismatch')
    for name,row in expected.items():
        data=observed[name].read_bytes()
        if set(row)!={'bytes','sha256'} or row!={'bytes':len(data),'sha256':digest(data)}:
            raise ValueError('bound payload differs: '+name)
    return initial,observed['RECEIPT_V1.json'].read_bytes()


def replay(root=HERE):
    root=Path(root)
    if root.resolve()!=HERE.resolve():raise ValueError('different imported source root')
    initial,expected=verify(root)
    from check_v1 import run,encoded
    actual=encoded(run())
    current,current_expected=verify(root)
    if current!=initial or current_expected!=expected:
        raise ValueError('authority changed during execution')
    if actual!=expected:raise ValueError('complete original-and-repaired payload mismatch')
    return actual
