# -*- coding: utf-8 -*-
"""Build the map data files from adjudication_v1.py and the receipts on disk.

Writes: MTG_STRUCTURAL_MAP_V1.json, CITATION_TABLE_V1.json, ISSUE_833_COMMENT_RECONCILIATION_V1.json,
MTG_THEOREM_STACK_V1.json, STRUCTURAL_MAP.md.

Pinned field values are the canonical JSON (`json.dumps(value, sort_keys=True)`) of the value found in the
receipt at build time; blob shas are git blob shas computed from the file bytes.  The auditor
(mtg_map_v1.py) and the oracle (independent_oracle_v1.py) re-verify every pin from the files, so a receipt
that drifts after the build is detected.

    python3 -I -B build_map_v1.py [--repo ROOT]
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adjudication_v1 as ADJ  # noqa: E402

REPO = os.environ.get("MTG_REPO_ROOT") or os.path.dirname(os.path.dirname(HERE))
BUCKETS = ("HARNESS", "EXACT-FORMAL", "NEW-SCIENCE", "EXTERNAL-GATE")
DISPOSITIONS = ("EARNED", "EARNED_BY_COUNTEREXAMPLE", "OPEN", "GOVERNANCE_NOT_A_CLOSABLE_ROW")
CID = 5687604615


def blob_sha(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def resolve(doc, path):
    cur = doc
    for seg in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(seg)]
        else:
            cur = cur[seg]
    return cur


def load_pins():
    pins = json.load(open(os.path.join(HERE, "PARENT_PINS_V1.json")))["pins"]
    table = {p["alias"]: p for p in pins}
    for alias, path in ADJ.MANIFESTS.items():
        table[alias] = {"alias": alias, "package": path.split("/")[1], "receipt_path": path, "claim_ceiling": None}
    for pkg, path in ADJ.OWN.items():
        table[pkg] = {"alias": pkg, "package": pkg, "receipt_path": path, "claim_ceiling": None}
    table[ADJ.MAP] = {"alias": ADJ.MAP, "package": ADJ.MAP, "receipt_path": "research/%s/RESULT_V1.json" % ADJ.MAP,
                      "claim_ceiling": None}
    return table


def build():
    rows = json.load(open(os.path.join(HERE, "MTG_ROWS_V1.json")))["rows"]
    pins = load_pins()
    if not all(i in ADJ.ROWS for i in range(len(rows))) or len(ADJ.ROWS) != len(rows):
        raise SystemExit("adjudication does not cover exactly the pinned rows")
    smap_rows, replacements, not_closed, table_rows = [], [], [], []
    for i, r in enumerate(rows):
        a = ADJ.ROWS[i]
        if a["bucket"] not in BUCKETS or a["disposition"] not in DISPOSITIONS:
            raise SystemExit("row %d: bad vocabulary" % i)
        entry = {"row_index": i, "comment_id": CID, "anchor": r["anchor"], "row": r["row"], "bucket": a["bucket"],
                 "disposition": a["disposition"], "reason": a["reason"], "row_meaning_token": a["token"],
                 "built_by": a.get("built_by"), "cited_aliases": [c["alias"] for c in a.get("cites", [])]}
        smap_rows.append(entry)
        if a["disposition"] in ("EARNED", "EARNED_BY_COUNTEREXAMPLE"):
            cites = []
            for c in a["cites"]:
                pin = pins[c["alias"]]
                full = os.path.join(REPO, pin["receipt_path"])
                doc = json.load(open(full))
                fields = {}
                for fpath, expected in c["fields"].items():
                    got = resolve(doc, fpath)
                    if json.dumps(got, sort_keys=True) != json.dumps(expected, sort_keys=True):
                        raise SystemExit("row %d alias %s field %s: expected %r got %r" % (i, c["alias"], fpath, expected, got))
                    fields[fpath] = json.dumps(got, sort_keys=True)
                cites.append({"alias": c["alias"], "package": pin["package"], "receipt_path": pin["receipt_path"],
                              "blob_sha": blob_sha(full), "fields": fields})
            pkg_tag = a.get("built_by") or ADJ.MAP
            new = "- [x] " + r["row"][len("- [ ] "):] + " — ✅ " + a["evidence"]
            rep = {"comment_id": CID, "anchor": r["anchor"], "old": r["row"], "new": new,
                   "status": a["disposition"], "bucket": a["bucket"], "row_meaning_token": a["token"],
                   "row_index": i, "package": pkg_tag, "citations": cites}
            replacements.append(rep)
            table_rows.append(rep)
        else:
            not_closed.append({"comment_id": CID, "anchor": r["anchor"], "old": r["row"], "bucket": a["bucket"],
                               "disposition": a["disposition"], "reason": a["reason"], "row_index": i})
    bucket_hist, disp_hist = {}, {}
    for e in smap_rows:
        bucket_hist[e["bucket"]] = bucket_hist.get(e["bucket"], 0) + 1
        disp_hist[e["disposition"]] = disp_hist.get(e["disposition"], 0) + 1
    smap = {"schema": "GMI_833_MTG_STRUCTURAL_MAP_V1", "issue": 833, "comment_id": CID,
            "source_main": "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5", "buckets": list(BUCKETS),
            "dispositions": list(DISPOSITIONS), "total_open_rows": len(rows),
            "bucket_histogram": bucket_hist, "disposition_histogram": disp_hist, "rows": smap_rows}
    json.dump(smap, open(os.path.join(HERE, "MTG_STRUCTURAL_MAP_V1.json"), "w"), indent=1, sort_keys=True, ensure_ascii=False)
    json.dump({"schema": "GMI_833_MTG_CITATION_TABLE_V1", "issue": 833, "comment_id": CID, "replacements": table_rows},
              open(os.path.join(HERE, "CITATION_TABLE_V1.json"), "w"), indent=1, sort_keys=True, ensure_ascii=False)
    by_pkg = {}
    for rep in replacements:
        by_pkg[rep["package"]] = by_pkg.get(rep["package"], 0) + 1
    rec = {"schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1", "issue": 833, "comment_id": CID,
           "comment_sha256": json.load(open(os.path.join(HERE, "MTG_ROWS_V1.json")))["comment_sha256"],
           "source_main": "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5", "branch": "research/833-sec-mtg",
           "anchor_form_note": "the live comment's subsection headings use THREE hashes (### MTG-n — ...); every anchor below is the live heading verbatim; MTG-8 carries no checkbox",
           "packages": [{"package": p, "rows_closed": n} for p, n in sorted(by_pkg.items())],
           "rows_total_in_comment": len(rows), "rows_closed": len(replacements), "rows_not_closed": len(not_closed),
           "replacements": [{k: rep[k] for k in ("comment_id", "anchor", "old", "new", "status")} for rep in replacements],
           "not_closed": [{k: nc[k] for k in ("comment_id", "anchor", "old", "reason", "bucket", "disposition")} for nc in not_closed]}
    json.dump(rec, open(os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json"), "w"), indent=1, sort_keys=True, ensure_ascii=False)
    write_markdown(smap_rows, replacements, not_closed, bucket_hist, disp_hist)
    print(json.dumps({"rows": len(rows), "closed": len(replacements), "not_closed": len(not_closed),
                      "buckets": bucket_hist, "dispositions": disp_hist, "by_package": by_pkg}, sort_keys=True))


def write_markdown(smap_rows, replacements, not_closed, bucket_hist, disp_hist):
    rep_by_idx = {r["row_index"]: r for r in replacements}
    lines = ["# MTG structural map — all 61 rows of programme comment 5687604615", "",
             "Source: SzeChunYiu/ORION-OCM#833 comment `5687604615` at `source_main` `f1e150ea`. Row text pinned",
             "byte-exact in `MTG_ROWS_V1.json` (comment sha256 `bb5e9e8b…`). Every row below quotes its live text",
             "verbatim (as a checklist line) and states bucket, disposition and reason. Buckets: **HARNESS** an exact",
             "instrument over a result already frozen on `main` · **EXACT-FORMAL** provable now over an existing finite",
             "universe · **NEW-SCIENCE** genuine derivation required · **EXTERNAL-GATE** no model-only route exists.",
             "", "| bucket | rows |", "|---|---|"]
    for b in BUCKETS:
        lines.append("| `%s` | %d |" % (b, bucket_hist.get(b, 0)))
    lines += ["", "| disposition | rows |", "|---|---|"]
    for d in DISPOSITIONS:
        lines.append("| `%s` | %d |" % (d, disp_hist.get(d, 0)))
    lines.append("")
    last = None
    for e in smap_rows:
        if e["anchor"] != last:
            lines += ["", "## " + e["anchor"][4:], ""]
            last = e["anchor"]
        i = e["row_index"]
        if i in rep_by_idx:
            lines.append(rep_by_idx[i]["new"])
            lines.append("      *%s / %s* — %s" % (e["bucket"], e["disposition"], e["reason"]))
        else:
            lines.append(e["row"])
            lines.append("      *%s / %s* — %s" % (e["bucket"], e["disposition"], e["reason"]))
        lines.append("")
    lines += ["", "## Batching plan for the open rows", "",
              "1. `gmi-833-mtg-known-closure-v1` — COVER-1 (row 57) together with MTG-7 rows 39–43: a frozen registry",
              "   of known classes on one finite universe, its transform/reachability closure under the P04 antichain",
              "   algebra at a frozen budget, the `UNKNOWN` region as the complement, nearest-known directed burdens,",
              "   and holes as components disconnected from the registry; criteria frozen before candidate generation.",
              "2. `gmi-833-mtg-third-encoding-recovery-v1` — row 29: add a multiplexer-tree basis and a direct",
              "   truth-table encoding to the P05 `DELAY1`/`IDENTITY` recovery with an independently written synthesizer.",
              "3. `gmi-833-mtg-heldout-second-grammar-v1` — row 37: re-run the P11 protocol under a second low-level",
              "   encoding of the same 65,552-transducer universe, predictions frozen before outcomes.",
              "4. `gmi-833-mtg-developmental-recovery-v1` — row 58 (RECOVER-1's developmental half): reach the P05 form",
              "   by a registered update law from a neutral seed (P16 laws), frozen before outcomes.",
              "5. `gmi-833-mtg-lofo-v1` — row 60 (LOFO-1), after 1: freeze an architecture-name-free structural-pressure",
              "   prediction for one held-out family, then search under two grammars and two searchers.",
              "6. Row 44 waits on external ecologies (transfer to disjoint families); rows 46, 48, 49, 50, 52 are",
              "   governance rules recorded here and enforced per tranche, never checked off.", ""]
    open(os.path.join(HERE, "STRUCTURAL_MAP.md"), "w").write("\n".join(lines))


if __name__ == "__main__":
    build()
