#!/usr/bin/env python3
"""Render REGISTRATIONS_V1.json -> REGISTRATIONS_TABLE_V1.md (human-readable).

One row per object: locator | six status letters | gap count. Status legend:
S=scope/quantifiers, A=assumptions, F=falsifiers, P=strongest parents,
X=forbidden extrapolations. Letters: C1/C2=carried from v1/v2 scores,
E=extracted with citation, D=derived (basis recorded), G=REGISTERED_GAP.
Full content lives in REGISTRATIONS_V1.json; this table is the index.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["scope_quantifiers", "assumptions", "falsifiers", "strongest_parents", "forbidden_extrapolations"]
LET = {"scope_quantifiers": "S", "assumptions": "A", "falsifiers": "F", "strongest_parents": "P", "forbidden_extrapolations": "X"}
ST = {"CARRIED_SCORES_V1": "C1", "CARRIED_SCORES_V2": "C2", "EXTRACTED": "E", "DERIVED": "D", "REGISTERED_GAP": "G"}


def main():
    d = json.load(open(os.path.join(HERE, "REGISTRATIONS_V1.json")))
    objs = d["objects"]
    by_pkg = {}
    for o in objs:
        by_pkg.setdefault(o["package"], []).append(o)
    lines = [
        "# REGISTRATIONS TABLE V1 — claim-discipline status per object",
        "",
        "Machine-readable authority: `REGISTRATIONS_V1.json`. Legend per field letter (S/A/F/P/X): "
        "`C1`/`C2` carried verbatim from THEOREM_SCORES_V1/V2 (already stated), `E` extracted from the "
        "object's own package docs with `file:line` citation, `D` derived from the object's own "
        "statement/support/proof (basis recorded), `G` REGISTERED_GAP (reason in JSON).",
        "",
    ]
    order = {"U-V1": 0, "U-LEGACY": 1, "U-ARRIVALS": 2, "U-NEW": 3}
    for pkg in sorted(by_pkg, key=lambda p: (order[by_pkg[p][0]["tranche"]], p)):
        rows = by_pkg[pkg]
        lines.append("## `%s` (%d object%s)" % (pkg, len(rows), "s" if len(rows) != 1 else ""))
        lines.append("")
        lines.append("| object | tranche | S | A | F | P | X | gaps |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for o in sorted(rows, key=lambda r: r["object_id"]):
            cells = []
            gaps = 0
            for f in FIELDS:
                fd = o["fields"][f]
                cells.append(ST[fd["status"]])
                if fd["status"] == "REGISTERED_GAP":
                    gaps += 1
            lines.append("| `%s` | %s | %s |" % (o["object_id"], o["tranche"], " | ".join(cells)) + " %d |" % gaps)
        lines.append("")
    path = os.path.join(HERE, "REGISTRATIONS_TABLE_V1.md")
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote", path, "objects:", len(objs), "packages:", len(by_pkg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
