from __future__ import annotations
import argparse,json,os,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load():
 o=json.loads((HERE/'ISSUE_833_AF5_RECONCILIATION_V1.json').read_text())
 if len(o['tasks'])!=6 or o['mode']!='CHECK_ONLY_NO_AUTOMATIC_ISSUE_MUTATION':raise RuntimeError('reconciliation drift')
 return o
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=('static-check','remote-check'),default='static-check');a=p.parse_args();o=load()
 if a.mode=='static-check':print(json.dumps({'status':'GREEN','tasks':6,'mode':a.mode},sort_keys=True));return
 h={'Accept':'application/vnd.github+json','User-Agent':'af5-reconcile'};t=os.environ.get('GITHUB_TOKEN')
 if t:h['Authorization']=f'Bearer {t}'
 with urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/SzeChunYiu/ORION-OCM/issues/comments/{o['comment_id']}",headers=h),timeout=30) as r:body=json.loads(r.read())['body']
 states=[]
 for x in o['tasks']:
  y=x.replace('- [ ] ','- [x] ',1)
  if body.count(x)+body.count(y)!=1:raise RuntimeError('missing/ambiguous AF5 row: '+x)
  states.append('CHECKED' if y in body else 'UNCHECKED')
 print(json.dumps({'status':'GREEN','states':states,'mode':a.mode},sort_keys=True))
if __name__=='__main__':main()
