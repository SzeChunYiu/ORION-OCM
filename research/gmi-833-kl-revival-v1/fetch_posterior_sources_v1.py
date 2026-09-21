"""Posterior source rule PS-1 (FREEZE_V1.md section 4.5) -- the ONLY network
step of this package.  Runs once, on laptop-billy, after the freeze commit.

It never chooses: candidates are taken in ascending creation order from the
Wikimedia recentchanges record starting 60 s after the freeze committer time,
and the first k that pass the mechanical admission test are kept.  The full
wikitext bytes are written OFF-repository (``--sources-dir``); the committed
record carries ids, timestamps, Wikimedia's own content sha1, this lane's
sha256, the byte length and an 80-byte prefix.

Usage:
  python3 -B fetch_posterior_sources_v1.py --freeze-time 2026-09-19T07:16:31Z \
      --freeze-commit <sha> --sources-dir ~/ocm-scratch/revive-kl/sources --k 6
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
UA = ("ORION-OCM-833-revive-kl/1.0 (research custody of posterior-dated sources; "
      "contact: sze-chun.yiu@fysik.su.se)")
MIN_NEWLEN = 2000
MIN_BYTES = 410
GUARD_SECONDS = 60


def get(params):
    params = dict(params)
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            raw = urllib.request.urlopen(req, timeout=60).read()
            return url, raw, json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            if attempt == 4:
                raise
            time.sleep(3 * (attempt + 1))
            sys.stderr.write("retry %d after %r\n" % (attempt + 1, exc))
    raise RuntimeError("unreachable")


def iso_plus(iso, seconds):
    t = datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
    return (t + datetime.timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def list_new_pages(rcstart):
    out = []
    cont = {}
    while True:
        params = dict(action="query", list="recentchanges", rctype="new",
                      rcnamespace="0", rcshow="!redirect", rcdir="newer",
                      rcstart=rcstart, rcprop="title|ids|timestamp|sizes|sha1",
                      rclimit="500")
        params.update(cont)
        _url, _raw, data = get(params)
        out.extend(data["query"]["recentchanges"])
        if "continue" in data:
            cont = data["continue"]
        else:
            break
    return out


def fetch_revision(revid):
    params = dict(action="query", prop="revisions", revids=str(revid),
                  rvprop="ids|timestamp|sha1|size|content", rvslots="main")
    url, raw, data = get(params)
    pages = data["query"].get("pages", {})
    for _pid, page in pages.items():
        revs = page.get("revisions") or []
        if revs:
            rev = revs[0]
            content = rev["slots"]["main"].get("*")
            return url, raw, page, rev, content
    return url, raw, None, None, None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze-time", required=True)
    ap.add_argument("--freeze-commit", required=True)
    ap.add_argument("--sources-dir", required=True)
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "POSTERIOR_SOURCES_V1.json"))
    args = ap.parse_args(argv)
    os.makedirs(args.sources_dir, exist_ok=True)
    rcstart = iso_plus(args.freeze_time, GUARD_SECONDS)
    t_fetch = now_iso()
    rc = list_new_pages(rcstart)
    rc.sort(key=lambda e: (e["timestamp"], e["revid"]))
    candidates = []
    admitted = []
    for e in rc:
        if len(admitted) >= args.k:
            break
        rec = {"rc": dict((k, e.get(k)) for k in ("title", "pageid", "revid", "timestamp",
                                                   "newlen", "oldlen", "sha1", "type")),
               "verdict": None}
        if e.get("newlen", 0) < MIN_NEWLEN:
            rec["verdict"] = "SKIPPED_NEWLEN_BELOW_%d" % MIN_NEWLEN
            candidates.append(rec)
            continue
        if e["timestamp"] <= rcstart:
            rec["verdict"] = "REJECTED_CLAUSE2_NOT_POSTERIOR"
            candidates.append(rec)
            continue
        url, raw, page, rev, content = fetch_revision(e["revid"])
        rec["revision_query_url"] = url
        rec["revision_response_sha256"] = hashlib.sha256(raw).hexdigest()
        if rev is None or content is None:
            rec["verdict"] = "REJECTED_CLAUSE1_REVISION_UNAVAILABLE"
            candidates.append(rec)
            continue
        data = content.encode("utf-8")
        sha1 = hashlib.sha1(data).hexdigest()
        rec["revision"] = {"revid": rev["revid"], "parentid": rev.get("parentid"),
                           "timestamp": rev["timestamp"], "sha1": rev.get("sha1"),
                           "size": rev.get("size"), "pageid": page.get("pageid"),
                           "title": page.get("title")}
        rec["bytes"] = len(data)
        rec["sha1_of_bytes"] = sha1
        rec["sha256_of_bytes"] = hashlib.sha256(data).hexdigest()
        if rev.get("parentid") not in (0, None):
            rec["verdict"] = "REJECTED_NOT_A_CREATION_REVISION"
            candidates.append(rec)
            continue
        if rev.get("sha1") != sha1:
            rec["verdict"] = "REJECTED_CLAUSE4_OUTSIDE_HASH_MISMATCH"
            candidates.append(rec)
            continue
        if rev["timestamp"] <= rcstart:
            rec["verdict"] = "REJECTED_CLAUSE2_NOT_POSTERIOR"
            candidates.append(rec)
            continue
        if len(data) < MIN_BYTES:
            rec["verdict"] = "REJECTED_TOO_SHORT"
            candidates.append(rec)
            continue
        sid = "P%02d" % (len(admitted) + 1)
        path = os.path.join(args.sources_dir, "%s_rev%d.txt" % (sid, rev["revid"]))
        with open(path, "wb") as handle:
            handle.write(data)
        rec["verdict"] = "ADMITTED"
        rec["source_id"] = sid
        rec["local_path"] = path
        rec["prefix80_hex"] = data[:80].hex()
        candidates.append(rec)
        admitted.append({
            "source_id": sid,
            "title": page.get("title"),
            "pageid": page.get("pageid"),
            "revid": rev["revid"],
            "creation_timestamp": rev["timestamp"],
            "wikimedia_sha1": rev.get("sha1"),
            "sha1_of_bytes": sha1,
            "sha256": rec["sha256_of_bytes"],
            "bytes": len(data),
            "prefix80_hex": data[:80].hex(),
            "permalink": "https://en.wikipedia.org/w/index.php?oldid=%d" % rev["revid"],
            "attestation_url": ("https://en.wikipedia.org/w/api.php?action=query&prop=revisions"
                                "&revids=%d&rvprop=ids|timestamp|sha1|size&format=json"
                                % rev["revid"]),
            "local_path": path,
            "licence": "CC BY-SA 4.0 (Wikipedia); bytes not redistributed here",
        })
    out = {
        "schema": "GMI_833_KL_REVIVAL_POSTERIOR_SOURCES_V1",
        "rule": "PS-1 (FREEZE_V1.md 4.5)",
        "freeze_commit": args.freeze_commit,
        "freeze_committer_time_utc": args.freeze_time,
        "guard_seconds": GUARD_SECONDS,
        "rcstart": rcstart,
        "T_fetch_utc": t_fetch,
        "api": API,
        "user_agent": UA,
        "min_newlen": MIN_NEWLEN,
        "min_bytes": MIN_BYTES,
        "k_requested": args.k,
        "k_admitted": len(admitted),
        "recentchanges_entries_scanned": len(candidates),
        "recentchanges_entries_total": len(rc),
        "candidates": candidates,
        "admitted": admitted,
    }
    with open(args.out, "w") as handle:
        json.dump(out, handle, indent=1, sort_keys=True)
        handle.write("\n")
    sys.stdout.write(json.dumps({"admitted": len(admitted), "scanned": len(candidates),
                                 "total_new_pages": len(rc), "T_fetch": t_fetch},
                                indent=1))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
