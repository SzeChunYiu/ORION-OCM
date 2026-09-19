#!/usr/bin/env python3
"""REV-L47-CUSTODY-GAPS mechanical custody-repair checker (v1).

For each MECHANICAL-class package (TRIAGE_V1.json; specs in
mechanical_specs_v1.json) this script re-derives the custody demonstration
from surviving git objects + the live tree, and emits a per-package receipt.

Legs (see mechanical_specs_v1.json note):
  L1 ORDER        freeze first-add commit is a git ancestor of every cited
                  outcome first-add commit (merge-base --is-ancestor);
  L2 SEPARATION   every cited outcome first-add lies > 120 s after the freeze
                  first-add (the registered demonstrability bar of the L47
                  screen, PASS_L47_V1.md);
  L3 IMMOBILITY   frozen artifacts unmodified between first-add and the last
                  cited outcome first-add; all post-window edits typed
                  (corpus-wide sweeps / metadata packages / per-spec typed
                  events) - untyped post-window edits fail the leg;
  L4 CONTENT PINS blob identity of the pinned artifacts across the window
                  (first-add blob == blob at last-outcome commit), and live
                  blob == window blob (post-window typed edits to text files
                  are listed; JSON manifests must remain live-identical);
  extra legs      per spec: upstream_producer, digest_binding,
                  absence_of_outcomes, repo_wide_earliest_holdout_impl.

Exit 0 iff every package's demonstration is complete.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PKG_DIR = Path(__file__).resolve().parent

TYPED_EVENT_NOTES = {
    1789415102: "capability-transfer-freeze digest canonicalization repair (24b9ffbfd; freeze_digest line only)",
    1789558080: "corpus-wide terminology migration (interaction-channels/local renames)",
    1789561929: "corpus-wide terminology migration v2 (remaining 236 gate hits)",
}

METADATA_PACKAGES = {
    "gmi-833-corpus-census-v1", "gmi-833-corpus-passes-v2-v1",
    "gmi-833-depgraph-adjudication-v1", "gmi-833-maturity-rescore-v1",
    "gmi-833-maturity-rescore-v2-v1", "gmi-833-terminology-migration-v1",
    "gmi-833-claim-discipline-v1", "gmi-833-progress-ledger-v1",
    "gmi-833-rev-l47-custody-gaps-v1",
}


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(["/usr/bin/git", "-C", str(REPO), *args],
                          capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])} failed: {proc.stderr[:200]}")
    return proc.stdout


def is_ancestor(a: str, b: str) -> bool:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), "merge-base",
                           "--is-ancestor", a, b],
                          capture_output=True).returncode == 0


def first_add(path: str) -> dict:
    """oldest commit that added `path` -> {ct, sha, subject}."""
    out = git("log", "--diff-filter=A", "--format=__CT__%ct %H %s", "--", path)
    ct = sha = subject = None
    for line in out.splitlines():
        if line.startswith("__CT__"):
            _, rest = line.split("__CT__", 1)
            ct_s, sha, subject = rest.split(" ", 2)
            ct, subject = int(ct_s), subject.strip()
    if ct is None:
        raise KeyError(path)
    return {"ct": ct, "sha": sha, "subject": subject}


def events_under(pkg: str) -> list[dict]:
    base = f"research/{pkg}"
    out = git("log", "--reverse", "--format=__CT__%ct %H %s", "--name-status",
              "--", base)
    evs, cur = [], None
    for line in out.splitlines():
        if line.startswith("__CT__"):
            _, rest = line.split("__CT__", 1)
            ct_s, sha, subject = rest.split(" ", 2)
            cur = {"ct": int(ct_s), "sha": sha, "subject": subject.strip()}
        elif line.strip() and cur is not None and line[0] in "AM":
            status, _, f = line.partition("\t")
            if f.startswith(base + "/"):
                evs.append({"op": status[0], "file": f, **cur})
    return evs


def blob_at(commit: str, path: str):
    """blob sha of `path` at `commit`, or None if the path does not exist
    there (a missing pinned blob fails the leg; it never crashes it)."""
    out = git("rev-parse", f"{commit}:{path}", check=False)
    return out.strip() if out.strip() and not out.startswith("fatal") else None


def repo_wide_first_adds(pattern_glob: str) -> list[dict]:
    """first-add event for every path matching a git pathspec glob."""
    out = git("log", "--diff-filter=A", "--format=__CT__%ct %H %s", "--name-only",
              "--", pattern_glob)
    adds, cur = {}, None
    for line in out.splitlines():
        if line.startswith("__CT__"):
            _, rest = line.split("__CT__", 1)
            ct_s, sha, subject = rest.split(" ", 2)
            cur = {"ct": int(ct_s), "sha": sha, "subject": subject.strip()}
        elif line.strip() and cur is not None:
            adds.setdefault(line.strip(), dict(cur))
    return [{"path": p, **meta} for p, meta in sorted(adds.items(),
                                                      key=lambda kv: kv[1]["ct"])]


def check_package(spec: dict) -> dict:
    pkg = spec["package"]
    base = f"research/{pkg}"
    fz = {f: first_add(f"{base}/{f}") for f in spec["freeze"]}
    fz_t = min(m["ct"] for m in fz.values())
    fz_commit = min(fz.values(), key=lambda m: m["ct"])["sha"]

    legs: dict[str, object] = {"freeze_first_adds": fz}

    # ---- L1 + L2 over cited outcomes
    oc_checks = []
    for oc in spec["outcomes"]:
        opath = f"research/{oc['pkg']}/{oc['file']}"
        try:
            oa = first_add(opath)
        except KeyError:
            oc_checks.append({"cited": oc, "found": False})
            continue
        oc_checks.append({"cited": oc, "found": True, "ct": oa["ct"],
                          "sha": oa["sha"], "dt_s": oa["ct"] - fz_t,
                          "ancestor": is_ancestor(fz_commit, oa["sha"])})
    legs["outcomes"] = oc_checks
    found = [c for c in oc_checks if c["found"]]
    legs["L1_order"] = all(c["ancestor"] for c in found) if found else None
    legs["L2_separation_over_120s"] = (all(c["dt_s"] > 120 for c in found)
                                       if found else None)
    last_outcome = max((c["ct"] for c in found), default=None)
    # anchor the window end only at a DESCENDANT outcome commit; a non-
    # descendant cited outcome already fails L1 and must not anchor anything.
    descendants = [c for c in found if c["ancestor"]]
    last_outcome_commit = max(
        (c for c in descendants), key=lambda c: c["ct"], default=None)

    # ---- L3 window immobility
    # With outcomes: NO freeze-file edit may fall inside (fz_t, last_outcome];
    #   post-window freeze edits must all be typed.
    # Without outcomes (prospective registration, nothing scored yet): ALL
    #   freeze-file edits after first add must be typed.
    evs = events_under(pkg)
    freeze_M = [
        {"file": e["file"].rsplit("/", 1)[-1], "ct": e["ct"], "sha": e["sha"],
         "subject": e["subject"]}
        for e in evs
        if e["op"] == "M" and e["file"].rsplit("/", 1)[-1] in spec["freeze"]
        and e["ct"] > fz_t]
    for e in freeze_M:
        if e["ct"] in TYPED_EVENT_NOTES:
            e["typed"] = TYPED_EVENT_NOTES[e["ct"]]
    if last_outcome is not None:
        in_window = [e for e in freeze_M if e["ct"] <= last_outcome]
        post_window = [e for e in freeze_M if e["ct"] > last_outcome]
    else:
        in_window, post_window = [], freeze_M
    legs["L3_window_freeze_edits"] = in_window
    legs["L3_post_window_freeze_edits"] = post_window
    legs["L3_immobile"] = (not in_window
                           and all("typed" in e for e in post_window))

    # ---- L4 content pins: blob identity across the window and to live tree
    end_commit = (last_outcome_commit["sha"] if last_outcome_commit else "HEAD")
    pins = {}
    for f in spec.get("blob_pin_files", spec["freeze"]):
        path = f"{base}/{f}"
        first_blob = blob_at(fz[f]["sha"] if f in fz else first_add(path)["sha"],
                             path)
        end_blob = blob_at(end_commit, path)
        live_blob = git("hash-object", str(REPO / path)).strip()
        pins[f] = {}
        if end_blob is None:
            # pinned artifact absent at the window anchor: fail the leg
            pins[f].update({"first_add_blob": first_blob,
                            "window_end_blob": None, "live_blob": live_blob,
                            "invariant_across_window": False,
                            "live_state_ok": False})
            continue
        if last_outcome is not None:
            window_ok = first_blob == end_blob
            live_ok = (live_blob == end_blob
                       or all("typed" in e for e in post_window))
        else:
            # no outcomes: the blob may change only at typed event commits
            chain = [{"ct": e["ct"], "sha": e["sha"], "typed": e.get("typed")}
                     for e in freeze_M if e["file"] == f]
            blobs = [{"stage": "first_add", "commit": fz[f]["sha"] if f in fz
                      else first_add(path)["sha"], "blob": first_blob}]
            for c in chain:
                blobs.append({"stage": f"typed_event_{c['ct']}",
                              "commit": c["sha"],
                              "blob": blob_at(c["sha"], path)})
            blobs.append({"stage": "head", "commit": "HEAD",
                          "blob": end_blob})
            transitions = []
            for a, b in zip(blobs, blobs[1:]):
                if a["blob"] != b["blob"]:
                    transitions.append({"from": a["stage"], "to": b["stage"],
                                        "typed": "typed" in b["stage"]})
            window_ok = all(t["typed"] for t in transitions)
            live_ok = live_blob == end_blob
            pins[f]["blob_chain"] = blobs
            pins[f]["transitions"] = transitions
        pins[f].update({"first_add_blob": first_blob, "window_end_blob": end_blob,
                        "live_blob": live_blob,
                        "invariant_across_window": window_ok,
                        "live_state_ok": live_ok})
    legs["L4_pins"] = pins
    legs["L4_blob_invariant"] = all(p["invariant_across_window"]
                                    and p["live_state_ok"]
                                    for p in pins.values())

    # ---- extra legs
    extra = {}
    if "upstream_producer" in spec.get("extra_legs", []):
        up = spec["upstream"]
        ua = first_add(f"research/{up['pkg']}/{up['file']}")
        extra["upstream_producer"] = {
            "pkg": up["pkg"], "ct": ua["ct"],
            "dt_before_freeze_s": fz_t - ua["ct"],
            "ok": (fz_t - ua["ct"]) > 120 and is_ancestor(ua["sha"], fz_commit)}
    if "digest_binding" in spec.get("extra_legs", []):
        db = spec["digest_binding"]
        art = REPO / "research" / db["artifact"]
        freeze_art = REPO / base / spec["freeze"][0]
        fm = json.loads(freeze_art.read_text())
        score_text = art.read_text()
        digest = fm.get("freeze_digest", "")
        extra["digest_binding"] = {
            "freeze_digest": digest,
            "bound_in_consumer_artifact": digest in score_text,
            "ok": bool(digest) and digest in score_text}
    if "absence_of_outcomes" in spec.get("extra_legs", []):
        target = spec["freeze"][0]
        proc = subprocess.run(
            ["grep", "-rl", "--include=*.py", "--include=*.json", target,
             str(REPO / "research")],
            capture_output=True, text=True)
        hits = [Path(h).relative_to(REPO).as_posix()
                for h in proc.stdout.splitlines()]
        foreign = [h for h in hits
                   if Path(h).parent.name not in METADATA_PACKAGES
                   and not h.startswith(f"{base}/")]
        extra["absence_of_outcomes"] = {
            "referencing_files": hits, "foreign_non_metadata_referencers": foreign,
            "ok": not foreign}
    if "repo_wide_earliest_holdout_impl" in spec.get("extra_legs", []):
        impls = []
        for pat in ("research/gmi-833-aj9*/blind_*.py",):
            impls.extend(repo_wide_first_adds(pat))
        impls = [i for i in impls if Path(i["path"]).parent.name != pkg]
        earliest = min(impls, key=lambda i: i["ct"]) if impls else None
        extra["repo_wide_earliest_holdout_impl"] = {
            "n_implementations": len(impls),
            "earliest": earliest,
            "earliest_dt_after_freeze_s":
                (earliest["ct"] - fz_t) if earliest else None,
            "all_after": [{"path": i["path"], "dt_s": i["ct"] - fz_t}
                          for i in impls],
            "ok": bool(earliest) and all(i["ct"] - fz_t > 120 for i in impls)}

    legs["extra"] = extra
    extra_ok = all(v.get("ok", True) for v in extra.values())

    demonstration = {
        "L1_order": legs["L1_order"] is True
        or (legs["L1_order"] is None and not spec["outcomes"]),
        "L2_separation": legs["L2_separation_over_120s"] is True
        or (legs["L2_separation_over_120s"] is None and not spec["outcomes"]),
        "L3_immobile": legs["L3_immobile"],
        "L4_blob_invariant": legs["L4_blob_invariant"],
        "extra_legs": extra_ok,
    }
    return {
        "package": pkg,
        "claim": spec["claim"],
        "freeze_ct": fz_t,
        "legs": legs,
        "demonstration": demonstration,
        "verdict": ("MECHANICAL_CUSTODY_DEMONSTRATED"
                    if all(demonstration.values())
                    else "DEMONSTRATION_INCOMPLETE"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    specs = json.loads((PKG_DIR / "mechanical_specs_v1.json").read_text())
    receipts = {"schema": "REV_L47_CUSTODY_REPAIR_RECEIPTS_V1",
                "typed_events": TYPED_EVENT_NOTES, "packages": {}}
    ok = True
    for spec in specs["packages"]:
        rec = check_package(spec)
        receipts["packages"][spec["package"]] = rec
        d = rec["demonstration"]
        flag = "OK " if rec["verdict"] == "MECHANICAL_CUSTODY_DEMONSTRATED" else "FAIL"
        print(f"[{flag}] {spec['package']}: "
              f"L1={d['L1_order']} L2={d['L2_separation']} "
              f"L3={d['L3_immobile']} L4={d['L4_blob_invariant']} "
              f"extra={d['extra_legs']}")
        ok = ok and rec["verdict"] == "MECHANICAL_CUSTODY_DEMONSTRATED"
    if args.write:
        out = PKG_DIR / "CUSTODY_REPAIR_RECEIPTS_V1.json"
        out.write_text(json.dumps(receipts, indent=2) + "\n")
        print(f"wrote {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
