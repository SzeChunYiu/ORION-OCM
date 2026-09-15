#!/usr/bin/env python3
"""Exact-line reconciler for #833 mandatory addendum comment 5684607872."""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE=Path(__file__).resolve().parent
DEFAULT_SPEC=HERE/'ISSUE_833_ADDENDUM_RECONCILIATION_V1.json'
API='https://api.github.com'
class ReconcileError(RuntimeError): pass

def sha(text:str)->str: return hashlib.sha256(text.encode()).hexdigest()
def api_json(method:str,url:str,token:str,payload=None):
    data=None if payload is None else json.dumps(payload).encode()
    headers={'Accept':'application/vnd.github+json','Authorization':f'Bearer {token}','X-GitHub-Api-Version':'2022-11-28','User-Agent':'orion-ocm-833-addendum-reconciler-v1'}
    if data is not None: headers['Content-Type']='application/json'
    req=Request(url,data=data,method=method,headers=headers)
    try:
        with urlopen(req,timeout=30) as res: return json.loads(res.read().decode())
    except HTTPError as e:
        raise ReconcileError(f'GitHub API {method} {url} failed: {e.code}: {e.read().decode(errors="replace")}') from e

def heading_level(line:str)->int:
    if not line.startswith('#'): return 0
    n=len(line)-len(line.lstrip('#'))
    return n if len(line)>n and line[n]==' ' else 0

def section(lines:list[str],anchor:str)->tuple[int,int]:
    hits=[i for i,x in enumerate(lines) if x==anchor]
    if len(hits)!=1: raise ReconcileError(f'anchor {anchor!r} exact hits={len(hits)}')
    start=hits[0]; level=heading_level(lines[start])
    if not level: raise ReconcileError('anchor must be a Markdown heading')
    end=len(lines)
    for i in range(start+1,len(lines)):
        lv=heading_level(lines[i])
        if lv and lv<=level: end=i; break
    return start,end

def reconcile_body(body:str,spec:dict)->tuple[str,list[dict]]:
    if spec.get('schema')!='GMI_ISSUE_COMMENT_RECONCILIATION_V1' or spec.get('issue')!=833 or spec.get('comment_id')!=5684607872:
        raise ReconcileError('wrong reconciliation authority')
    trailing=body.endswith('\n'); lines=body.splitlines(); receipt=[]
    reps=spec.get('replacements')
    if not isinstance(reps,list) or not reps: raise ReconcileError('replacements required')
    for idx,row in enumerate(reps,1):
        a,o,n=(row.get(k) for k in ('anchor','old','new'))
        if not all(isinstance(x,str) and x and '\n' not in x for x in (a,o,n)): raise ReconcileError(f'malformed replacement {idx}')
        if not o.startswith('- [ ] ') or not n.startswith('- [x] '): raise ReconcileError(f'replacement {idx} is not checkbox transition')
        s,e=section(lines,a); inds=range(s+1,e)
        oh=[i for i in inds if lines[i]==o]; nh=[i for i in inds if lines[i]==n]
        if len(oh)==1 and not nh:
            lines[oh[0]]=n; status='READY_TO_APPLY'
        elif len(nh)==1 and not oh: status='ALREADY_RECONCILED'
        else: raise ReconcileError(f'replacement {idx} ambiguous: old={len(oh)} new={len(nh)}')
        receipt.append({'index':idx,'anchor':a,'status':status,'old':o,'new':n})
    updated='\n'.join(lines)+('\n' if trailing else '')
    return updated,receipt

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=('check','apply'),default='check'); ap.add_argument('--repository',default=os.getenv('GITHUB_REPOSITORY','')); ap.add_argument('--token-env',default='GITHUB_TOKEN'); ap.add_argument('--spec',type=Path,default=DEFAULT_SPEC); args=ap.parse_args()
    if '/' not in args.repository: raise ReconcileError('--repository owner/name required')
    token=os.getenv(args.token_env,'')
    if not token: raise ReconcileError(f'{args.token_env} required')
    spec=json.loads(args.spec.read_text()); cid=spec['comment_id']
    url=f'{API}/repos/{args.repository}/issues/comments/{cid}'
    obj=api_json('GET',url,token); body=obj.get('body') or ''
    updated,rows=reconcile_body(body,spec); changed=updated!=body
    if args.mode=='apply' and changed: api_json('PATCH',url,token,{'body':updated})
    print(json.dumps({'schema':'GMI_ISSUE_COMMENT_RECONCILIATION_RECEIPT_V1','mode':args.mode,'issue':833,'comment_id':cid,'replacement_count':len(rows),'body_changed':changed,'body_sha256_before':sha(body),'body_sha256_after':sha(updated),'rows':rows,'forbidden_promotions_preserved':spec.get('forbidden_promotions',[])},indent=2,sort_keys=True))
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except ReconcileError as e:
        print(json.dumps({'schema':'GMI_ISSUE_COMMENT_RECONCILIATION_RECEIPT_V1','verdict':'FAIL','error':str(e)},indent=2)); raise SystemExit(1)
