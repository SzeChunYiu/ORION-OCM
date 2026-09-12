#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt,hashlib,json,os,subprocess,time,urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,"GMI_K5_BH_PUBLIC_BEACON_V6.json");FREEZE_COMMIT="5c8380ceb1a4ff308c3e39f26d8e29d150948441";CHAIN_HASH="52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971";GENESIS,PERIOD,DELAY=1692803367,3,900;BASE=f"https://api.drand.sh/{CHAIN_HASH}/public"
def commit_unix():return int(subprocess.check_output(["git","show","-s","--format=%ct",FREEZE_COMMIT],cwd=ROOT,text=True).strip())
def round_for(t):return 0 if t<GENESIS else ((t-GENESIS)//PERIOD)+1
def main():
 if os.path.exists(OUT):raise SystemExit("K5 V6 beacon exists; no-reroll")
 ct=commit_unix();rnd=round_for(ct+DELAY);rt=GENESIS+(rnd-1)*PERIOD;now=int(time.time())
 if now<rt:raise SystemExit(f"target round {rnd} not public yet")
 url=f"{BASE}/{rnd}"
 with urllib.request.urlopen(url,timeout=30) as r:raw=r.read();status=getattr(r,"status",200)
 body=json.loads(raw);sig=body.get("signature")
 if int(body.get("round",-1))!=rnd or not isinstance(sig,str) or not sig:raise SystemExit("invalid drand response")
 rand=hashlib.sha256(bytes.fromhex(sig)).hexdigest();api=body.get("randomness")
 if api is not None and api!=rand:raise SystemExit("randomness mismatch")
 rec={"schema":"GMIK5BHPublicBeaconV6","status":"ACQUIRED_NO_REROLL","no_reroll":True,"execution_freeze_commit":FREEZE_COMMIT,"freeze_commit_unix":ct,"freeze_commit_iso_utc":dt.datetime.fromtimestamp(ct,dt.timezone.utc).isoformat(),"delay_seconds":DELAY,"network":"League of Entropy drand quicknet mainnet","chain_hash":CHAIN_HASH,"genesis_time":GENESIS,"period_seconds":PERIOD,"target_round":rnd,"target_round_time_unix":rt,"source_url":url,"retrieved_at_unix":now,"http_status":status,"signature":sig,"randomness":rand,"api_randomness":api,"sha256_signature_consistency_verified":True,"bls_signature_verified":False}
 with open(OUT,"x") as f:json.dump(rec,f,indent=1,sort_keys=True)
 print(json.dumps({"wrote":OUT,"round":rnd,"randomness":rand}))
if __name__=="__main__":main()
