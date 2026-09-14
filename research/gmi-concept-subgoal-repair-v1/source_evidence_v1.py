"""Read exact source parents and reproduce only two finite nonnative scripts."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
PREFIX='research/machine-intelligence-morphogenesis-v1/'


def sha(data):return hashlib.sha256(data).hexdigest()


def verify_sources(root=HERE):
    root=Path(root);register=json.loads((root/'SOURCE_BINDINGS_V1.json').read_bytes())
    if set(register)!={'schema','sources'} or register['schema']!='CSR_SOURCE_BINDINGS_V1':
        raise ValueError('source schema')
    result={}
    for row in register['sources']:
        p=root/row['raw'];data=p.read_bytes()
        if len(data)!=row['bytes'] or sha(data)!=row['sha256']:
            raise ValueError('source changed: '+row['raw'])
        key=(row['group'],row['path'])
        if key in result:raise ValueError('duplicate source')
        result[key]=data
    return result


def original(sources):
    records={};replays={}
    for key,data in sources.items():
        if key[0]=='PR597_DELTA' and key[1].endswith('.json'):
            records[Path(key[1]).name]=json.loads(data)
    for filename,output in [('concept_formation_witness.py','STAGE_CONCEPT_FORMATION_V1.json'),
                             ('subgoal_witness.py','STAGE_SUBGOAL_WITNESS_V1.json')]:
        source=sources[('PR597_DELTA',PREFIX+'gmi_microscope/'+filename)]
        with tempfile.TemporaryDirectory(prefix='gmi-concept-source-') as temp:
            p=Path(temp);(p/'microscopes/results').mkdir(parents=True)
            script=p/filename;script.write_bytes(source)
            r=subprocess.run([sys.executable,'-I','-B',str(script)],cwd=p,capture_output=True,timeout=20)
            if r.returncode or r.stderr:raise ValueError('finite original replay failed')
            payload=json.loads((p/'microscopes/results'/output).read_bytes())
            if payload!=records[output]:raise ValueError('full original record mismatch')
            replays[filename]=dict(stdout=r.stdout.decode(),original_payload=payload)
    return dict(records=records,replays=replays,original_scripts=2,
                native_or_protected_campaign_calls=0)
