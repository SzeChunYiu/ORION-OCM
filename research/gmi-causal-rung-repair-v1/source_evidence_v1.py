"""Pinned source custody plus an independent replay of its earned numbers."""
from pathlib import Path
import hashlib,json
from scm_v1 import from_units,law,evidence,necessity
from witnesses_v1 import rung_pairs

HERE=Path(__file__).resolve().parent
BINDING_SHA='c01cc905810ffa64cd1b2d1c4d4283b60a754ba676e1b6633936b5f9063dafd6'

def verified_sources(root=HERE):
    root=Path(root); data=(root/'SOURCE_BINDINGS_V1.json').read_bytes()
    if hashlib.sha256(data).hexdigest()!=BINDING_SHA:
        raise ValueError('source binding authority changed')
    binding=json.loads(data)
    for row in binding['records']:
        b=(root/row['path']).read_bytes()
        if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:
            raise ValueError('pinned source changed: '+row['path'])
    return binding

def observed_dict(weights):
    return {(x,y):p for (x,y),p in zip(((0,0),(0,1),(1,0),(1,1)),law(weights)) if p}

def original_results(root=HERE):
    root=Path(root); binding=verified_sources(root)
    src=root/'raw/pr603/research/gmi-causal-identifiability-v1'
    ns={'__name__':'archived_causal_rungs'}
    exec(compile((src/'causal_rungs_v1.py').read_bytes(),str(src/'causal_rungs_v1.py'),'exec'),ns)
    receipt=json.loads((src/'CAU5_RECEIPT_V1.json').read_bytes())
    anchors={}
    for name,row in receipt['source_and_evidence'].items():
        b=(src/name).read_bytes()
        anchors[name]={'matches':row=={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},
                       'actual_sha256':hashlib.sha256(b).hexdigest()}
    rows_a=((0,0,0),)*3+((1,0,0),)+((1,1,1),)*3+((0,1,1),)
    rows_b=((0,1,1),(1,0,0))
    separators=[]
    for name,rows in (('w4a',rows_a),('w4b',rows_b)):
        w=from_units(rows); obs,cond,intervention=ns[name]()
        p,q0,q1=evidence(w)
        if obs!=observed_dict(w) or cond!=p[3]/sum(p[2:]) or intervention!=q1:
            raise RuntimeError('original separator mismatch')
        separators.append({'name':name,'observed':p,'conditional':cond,'do1':q1})
    for world,rows in enumerate((((0,0,0),(1,1,1)),((0,0,1),(1,0,1)))):
        w=from_units(rows); obs,do1=ns['w1'](world)
        if obs!=observed_dict(w) or do1!=evidence(w)[2]:
            raise RuntimeError('original W1 mismatch')
    for symbol,rows in zip(('RA','RB'),rung_pairs()['six_original']):
        w=from_units(rows); table=ns[symbol]
        if (ns['observed_w5'](table)!=observed_dict(w)
                or tuple(ns['do_w5'](table,x) for x in (0,1))!=evidence(w)[1:]
                or ns['pn_w5'](table)!=necessity(w)):
            raise RuntimeError('original six-unit mismatch')
    return {'pinned_source_files':len(binding['records']),
            'original_receipt_anchors':anchors,'separators':separators,
            'w1_and_w5_independent_comparison':'MATCH',
            'historical_host_runs':'archived claims; not inferred from source digest'}
