"""Repository integration check; a standalone source packet is not a live VM."""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parent

def verify(repository):
    repository=Path(repository)
    rows=json.loads((ROOT/'ACTIVE_RUNTIME_BINDING_V1.json').read_text())['files']
    for name,row in rows.items():
        path=repository/name
        if not path.is_file() or path.is_symlink():raise ValueError('active runtime member unavailable: '+name)
        data=path.read_bytes()
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
            raise ValueError('active runtime differs from the corrected version: '+name)
    return {'status':'ACTIVE_NATIVE_ADJOINT_SOURCE_MATCH','files':rows}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('supply repository root')
    print(json.dumps(verify(sys.argv[1]),indent=2,sort_keys=True))
