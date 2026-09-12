#!/usr/bin/env python3
"""Acquire the unique future drand quicknet beacon committed by the K4 V5 null-aware freeze."""
from __future__ import annotations
import datetime as dt,hashlib,json,os,subprocess,time,urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"GMI_K4_PUBLIC_BEACON_V5.json")
FREEZE_COMMIT="b88d91b9f16eecd3733807abc1ddc82a9483475e"
CHAIN_HASH="52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"; GENESIS,PERIOD,DELAY=1692803367,3,900
BASE=f"https://api.drand.sh/{CHAIN_HASH}/public"
def commit_unix():return int(subprocess.check_output(["git","show","-s","--format=%ct",FREEZE_COMMIT],cwd=ROOT,text=True).strip())
def round_for(t):return 0 if t<GENESIS else ((t-GENESIS)//PERIOD)+1
def main():
    if os.path.exists(OUT):raise SystemExit("V5 beacon receipt exists; no-reroll rule forbids overwrite")
    ct=commit_unix();target=ct+DELAY;rnd=round_for(target);rtime=GENESIS+(rnd-1)*PERIOD;now=int(time.time())
    if now<rtime:raise SystemExit(f"V5 target beacon round {rnd} not public yet: target_unix={rtime}, now={now}")
    url=f"{BASE}/{rnd}"
    with urllib.request.urlopen(url,timeout=30) as r:raw=r.read();status=getattr(r,"status",200)
    body=json.loads(raw)
    if int(body.get("round",-1))!=rnd:raise SystemExit("drand relay returned wrong round")
    sig=body.get("signature")
    if not isinstance(sig,str) or not sig:raise SystemExit("drand response missing signature")
    randomness=hashlib.sha256(bytes.fromhex(sig)).hexdigest();api_rand=body.get("randomness")
    if api_rand is not None and api_rand!=randomness:raise SystemExit("drand API randomness != SHA256(signature)")
    rec={"schema":"GMIK4PublicBeaconV5","status":"ACQUIRED_NO_REROLL","no_reroll":True,"v5_freeze_commit":FREEZE_COMMIT,
         "freeze_commit_unix":ct,"freeze_commit_iso_utc":dt.datetime.fromtimestamp(ct,dt.timezone.utc).isoformat(),"delay_seconds":DELAY,
         "network":"League of Entropy drand quicknet mainnet","chain_hash":CHAIN_HASH,"genesis_time":GENESIS,"period_seconds":PERIOD,
         "target_round":rnd,"target_round_time_unix":rtime,"source_url":url,"retrieved_at_unix":now,"http_status":status,"signature":sig,
         "randomness":randomness,"api_randomness":api_rand,"sha256_signature_consistency_verified":True,"bls_signature_verified":False,
         "bls_verification_note":"Hash/round consistency verified; immutable receipt. Optional BLS audit may be separate."}
    with open(OUT,"x") as f:json.dump(rec,f,indent=1,sort_keys=True)
    print(json.dumps({"wrote":OUT,"round":rnd,"randomness":randomness}))
if __name__=="__main__":main()
