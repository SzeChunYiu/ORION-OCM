from __future__ import annotations
import argparse, json, os, urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
REG=HERE/'ISSUE_833_AF4_RECONCILIATION_V1.json'

def req(c,m):
    if not c: raise RuntimeError(m)
def load():
    o=json.loads(REG.read_text()); req(o['registry_id']=='ISSUE_833_AF4_RECONCILIATION_V1','registry drift'); req(len(o['tasks'])==7,'AF4 task count drift'); req(len(set(o['tasks']))==7,'duplicate task'); req(o['mode']=='CHECK_ONLY_NO_AUTOMATIC_ISSUE_MUTATION','mutation mode forbidden'); return o
def fetch(url):
    headers={'Accept':'application/vnd.github+json','User-Agent':'gmi-af4-reconcile-v1'}; t=os.environ.get('GITHUB_TOKEN');
    if t: headers['Authorization']=f'Bearer {t}'
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r:return json.loads(r.read().decode())
def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=('static-check','remote-check'),default='static-check');a=p.parse_args();o=load()
    if a.mode=='static-check': print(json.dumps({'status':'GREEN','tasks':7,'mode':a.mode},sort_keys=True));return
    obj=fetch(f"https://api.github.com/repos/SzeChunYiu/ORION-OCM/issues/comments/{o['comment_id']}"); body=obj['body']; found=[]
    for task in o['tasks']:
        checked=task.replace('- [ ] ','- [x] ',1); req(body.count(task)+body.count(checked)==1,f'missing/ambiguous task: {task}'); found.append('CHECKED' if checked in body else 'UNCHECKED')
    print(json.dumps({'status':'GREEN','mode':a.mode,'states':found},sort_keys=True))
if __name__=='__main__': main()
