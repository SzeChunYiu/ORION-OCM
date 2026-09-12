#!/usr/bin/env python3
"""Acquire the one committed future drand quicknet beacon for K4 V2.

The successor freeze was committed before this value existed. This script computes the unique target
round from that commit timestamp + 900 seconds, refuses to run early, fetches exactly that round, and
refuses to overwrite an existing beacon receipt. It verifies the API randomness equals SHA-256 of the
returned signature when both fields are present. Full BLS verification requires a drand client and is
reported separately rather than fabricated.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "GMI_K4_PUBLIC_BEACON_V2.json")
SUCCESSOR_COMMIT = "00e48ec3a4809cc9af1bfb300b0b580b9e18e36b"
CHAIN_HASH = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
GENESIS = 1692803367
PERIOD = 3
DELAY = 900
BASE = f"https://api.drand.sh/{CHAIN_HASH}/public"


def commit_unix(sha):
    raw = subprocess.check_output(["git", "show", "-s", "--format=%ct", sha], cwd=ROOT, text=True).strip()
    return int(raw)


def round_for(t):
    if t < GENESIS:
        return 0
    return ((t - GENESIS) // PERIOD) + 1


def main():
    if os.path.exists(OUT):
        raise SystemExit("beacon receipt already exists; no-reroll rule forbids overwrite")
    ct = commit_unix(SUCCESSOR_COMMIT)
    target_time = ct + DELAY
    target_round = round_for(target_time)
    round_time = GENESIS + (target_round - 1) * PERIOD
    now = int(time.time())
    if now < round_time:
        raise SystemExit(f"target drand round {target_round} is still in the future; earliest unix={round_time}, now={now}")

    url = f"{BASE}/{target_round}"
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read(); status = getattr(r, "status", 200)
    body = json.loads(raw)
    if int(body.get("round", -1)) != target_round:
        raise SystemExit(f"relay returned wrong round: {body.get('round')} != {target_round}")
    sig = body.get("signature")
    if not isinstance(sig, str) or not sig:
        raise SystemExit("relay response has no signature")
    computed = hashlib.sha256(bytes.fromhex(sig)).hexdigest()
    api_randomness = body.get("randomness")
    hash_ok = api_randomness is None or api_randomness == computed
    if not hash_ok:
        raise SystemExit("API randomness does not equal SHA256(signature)")

    rec = {
        "schema": "GMIK4PublicBeaconV2",
        "status": "ACQUIRED_NO_REROLL",
        "successor_freeze_commit": SUCCESSOR_COMMIT,
        "successor_commit_unix": ct,
        "successor_commit_iso_utc": dt.datetime.fromtimestamp(ct, dt.timezone.utc).isoformat(),
        "delay_seconds": DELAY,
        "network": "League of Entropy drand quicknet mainnet",
        "chain_hash": CHAIN_HASH,
        "genesis_time": GENESIS,
        "period_seconds": PERIOD,
        "target_round": target_round,
        "target_round_time_unix": round_time,
        "source_url": url,
        "retrieved_at_unix": now,
        "http_status": status,
        "signature": sig,
        "randomness": computed,
        "api_randomness": api_randomness,
        "sha256_signature_consistency_verified": hash_ok,
        "bls_signature_verified": False,
        "bls_verification_note": "This zero-dependency script verifies round identity and SHA256(signature) consistency. Run an official drand client/BLS verifier separately if available and append that verification as a successor audit; do not rewrite this receipt.",
        "no_reroll": True
    }
    with open(OUT, "x") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({"wrote": OUT, "round": target_round, "randomness": computed, "hash_consistency": hash_ok}))


if __name__ == "__main__":
    main()
