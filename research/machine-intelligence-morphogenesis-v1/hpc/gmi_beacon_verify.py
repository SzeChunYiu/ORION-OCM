#!/usr/bin/env python3
"""Shared fail-closed verification of future-public-drand beacon receipts.

The receipt's `no_reroll` flag is not trusted.  We independently prove that its declared freeze
commit contains the exact execution-freeze blob currently being used, obtain that commit's timestamp
from Git, recompute the unique first drand round at `commit_time + delay`, and verify signature-hash
consistency.  A later convenient round therefore cannot masquerade as the preregistered one.
"""
from __future__ import annotations
import hashlib,json,os,subprocess

QUICKNET_CHAIN_HASH="52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
QUICKNET_GENESIS=1692803367
QUICKNET_PERIOD=3


def _git(repo_root,*args):
    return subprocess.check_output(["git",*args],cwd=repo_root)

def round_for(unix_time:int,genesis:int=QUICKNET_GENESIS,period:int=QUICKNET_PERIOD)->int:
    return 0 if unix_time<genesis else ((unix_time-genesis)//period)+1


def verify_beacon(*,repo_root:str,freeze_path:str,beacon:dict,expected_schema:str,freeze_commit_field:str="execution_freeze_commit",delay_seconds:int=900):
    if beacon.get("schema")!=expected_schema:raise RuntimeError(f"wrong beacon schema: {beacon.get('schema')}")
    if beacon.get("status")!="ACQUIRED_NO_REROLL" or not beacon.get("no_reroll"):raise RuntimeError("beacon not immutable/no-reroll")
    commit=beacon.get(freeze_commit_field)
    if not isinstance(commit,str) or len(commit)<7:raise RuntimeError("beacon missing freeze commit")
    # `git show <commit>:<path>` resolves a bare path against the repository toplevel, not the cwd;
    # repo_root here is the study directory (a subdirectory), so the path must be toplevel-relative.
    try:top=_git(repo_root,"rev-parse","--show-toplevel").decode().strip()
    except Exception as e:raise RuntimeError(f"cannot locate git toplevel from {repo_root}: {e}")
    rel=os.path.relpath(os.path.abspath(freeze_path),top).replace(os.sep,"/")
    current=open(freeze_path,"rb").read()
    try:committed=_git(repo_root,"show",f"{commit}:{rel}")
    except Exception as e:raise RuntimeError(f"cannot retrieve execution freeze from declared commit: {e}")
    if hashlib.sha256(committed).hexdigest()!=hashlib.sha256(current).hexdigest():raise RuntimeError("declared beacon freeze commit does not contain the exact current execution freeze")
    ct=int(_git(repo_root,"show","-s","--format=%ct",commit).decode().strip())
    freeze=json.loads(current);rule=freeze.get("public_beacon_rule",{})
    genesis=int(rule.get("genesis_time",QUICKNET_GENESIS));period=int(rule.get("period_seconds",QUICKNET_PERIOD));delay=int(rule.get("delay_seconds",delay_seconds))
    chain=rule.get("chain_hash",QUICKNET_CHAIN_HASH)
    target=round_for(ct+delay,genesis,period);target_time=genesis+(target-1)*period
    if beacon.get("chain_hash")!=chain:raise RuntimeError("beacon chain hash does not match frozen rule")
    if int(beacon.get("target_round",-1))!=target:raise RuntimeError(f"beacon round {beacon.get('target_round')} != frozen unique round {target}")
    if int(beacon.get("target_round_time_unix",-1))!=target_time:raise RuntimeError("beacon round timestamp mismatch")
    if int(beacon.get("delay_seconds",-1))!=delay:raise RuntimeError("beacon delay mismatch")
    sig=beacon.get("signature")
    if not isinstance(sig,str) or not sig:raise RuntimeError("beacon signature absent")
    try:rand=hashlib.sha256(bytes.fromhex(sig)).hexdigest()
    except Exception as e:raise RuntimeError(f"invalid beacon signature hex: {e}")
    if beacon.get("randomness")!=rand:raise RuntimeError("beacon randomness != SHA256(signature)")
    if beacon.get("api_randomness") is not None and beacon.get("api_randomness")!=rand:raise RuntimeError("beacon API randomness mismatch")
    if not beacon.get("sha256_signature_consistency_verified"):raise RuntimeError("receipt did not assert signature-hash check")
    return {"freeze_commit":commit,"freeze_commit_unix":ct,"delay_seconds":delay,"target_round":target,"target_round_time_unix":target_time,"chain_hash":chain,"randomness":rand}
