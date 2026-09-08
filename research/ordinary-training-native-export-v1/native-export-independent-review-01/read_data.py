"""Independent standard-library retained-data reader; never imports target sources."""
from pathlib import Path
import hashlib, json, re
ROOT=Path('/home/billy/orion-director-work/20260908/ordinary-training-trace-export-v1')
OUT=ROOT/'native-export-01'
OBS=ROOT/'native-export-observer-01'
READS={}
CHECKS=[]
def identity(b): return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def small(d): return {k:d[k] for k in ('bytes','sha256')}
def read(p):
    p=Path(p)
    if p.name=='set.mm': raise RuntimeError('FULL_CORPUS_READ_FORBIDDEN')
    b=p.read_bytes(); READS[str(p)]=identity(b); return b
def pairs(xs):
    d={}
    for k,v in xs:
        if k in d: raise ValueError('duplicate JSON key')
        d[k]=v
    return d
def parse(b): return json.loads(b,object_pairs_hook=pairs)
def load(p): return parse(read(p))
def canonical(v): return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def equal(name,a,b):
    if a!=b: raise AssertionError(name)
    CHECKS.append(name)
def require(name,ok): equal(name,ok,True)
def bound(p,d): equal('file-binding:'+str(p),identity(read(p)),small(d))
def canon_bound(name,value,d): equal(name,identity(canonical(value)),small(d))
def lexical_records(raw):
    # Only declaration labels, token payloads and byte spans; no scope/proof evaluation.
    tokens=[]; in_comment=False
    for m in re.finditer(rb'\S+',raw):
        t=m[0].decode('ascii')
        if in_comment:
            if t=='$)': in_comment=False
        elif t=='$(' : in_comment=True
        else: tokens.append((t,m.start(),m.end()))
    require('lexical-comments-closed',not in_comment)
    records={}; order=[]; i=0
    while i<len(tokens):
        label=None; t,start,end=tokens[i]; i+=1
        if t in ('${','$}'): continue
        if not t.startswith('$'):
            label=t; label_start=start; t,start,end=tokens[i]; i+=1
        require('lexical-supported-directive',t in ('$c','$v','$d','$f','$e','$a','$p'))
        statement=[]; proof=None; split=None; body_start=end
        while i<len(tokens):
            word,a,b=tokens[i]; i+=1
            if word=='$.': break
            if word=='$=': split=(a,b); proof=[]
            elif proof is None: statement.append(word)
            else: proof.append(word)
        else: raise AssertionError('unterminated lexical declaration')
        if label:
            require('lexical-unique-label',label not in records)
            row={'label':label,'kind':t,'statement':statement,'span':[label_start,b],
                 'raw':identity(raw[label_start:b]),
                 'statement_raw':identity(raw[body_start:split[0] if split else a])}
            if proof is not None: row.update(proof=proof,proof_raw=identity(raw[split[1]:a]))
            records[label]=row; order.append(label)
    return records,order
