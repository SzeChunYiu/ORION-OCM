import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from hpc.gmi_beacon_verify import QUICKNET_CHAIN_HASH, round_for, verify_beacon


def git(cwd,*args):
    return subprocess.check_output(["git",*args],cwd=cwd,text=True).strip()


def build(tmp_path):
    git(tmp_path,"init")
    git(tmp_path,"config","user.email","test@example.invalid")
    git(tmp_path,"config","user.name","Beacon Test")
    freeze=tmp_path/"freeze.json"
    freeze.write_text(json.dumps({"public_beacon_rule":{"chain_hash":QUICKNET_CHAIN_HASH,"genesis_time":1692803367,"period_seconds":3,"delay_seconds":9}},sort_keys=True))
    git(tmp_path,"add","freeze.json");git(tmp_path,"commit","-m","freeze")
    commit=git(tmp_path,"rev-parse","HEAD");ct=int(git(tmp_path,"show","-s","--format=%ct",commit));rnd=round_for(ct+9);rt=1692803367+(rnd-1)*3
    sig=("01"*96);rand=hashlib.sha256(bytes.fromhex(sig)).hexdigest()
    b={"schema":"TESTBeacon","status":"ACQUIRED_NO_REROLL","no_reroll":True,"execution_freeze_commit":commit,"delay_seconds":9,"chain_hash":QUICKNET_CHAIN_HASH,"target_round":rnd,"target_round_time_unix":rt,"signature":sig,"randomness":rand,"api_randomness":rand,"sha256_signature_consistency_verified":True}
    return freeze,b


def test_exact_frozen_future_round_passes(tmp_path):
    freeze,b=build(tmp_path)
    out=verify_beacon(repo_root=str(tmp_path),freeze_path=str(freeze),beacon=b,expected_schema="TESTBeacon")
    assert out["target_round"]==b["target_round"]
    assert out["randomness"]==b["randomness"]


def test_one_round_reroll_fails_even_if_receipt_claims_no_reroll(tmp_path):
    freeze,b=build(tmp_path);b["target_round"]+=1;b["target_round_time_unix"]+=3
    with pytest.raises(RuntimeError,match="frozen unique round"):
        verify_beacon(repo_root=str(tmp_path),freeze_path=str(freeze),beacon=b,expected_schema="TESTBeacon")


def test_changed_freeze_blob_fails_declared_commit_membership(tmp_path):
    freeze,b=build(tmp_path);freeze.write_text(freeze.read_text()+"\n")
    with pytest.raises(RuntimeError,match="exact current execution freeze"):
        verify_beacon(repo_root=str(tmp_path),freeze_path=str(freeze),beacon=b,expected_schema="TESTBeacon")
