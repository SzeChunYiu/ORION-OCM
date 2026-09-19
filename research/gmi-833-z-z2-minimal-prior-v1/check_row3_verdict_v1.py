"""Assert the row-3 verdict on whatever the live corpus currently is.

The site-audit receipt's counts are corpus-timestamped: any lane that adds or
removes a `prior-free` token anywhere under `research/gmi-833-*` moves them.
The verdict is what must hold, and this file is what CI runs instead of a
byte-comparison of that receipt.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(HERE, "PRIOR_FREE_SITE_AUDIT_V1.json")) as fh:
        d = json.load(fh)
    v = d["validation"]
    problems = []
    if not v["recall_ok"]:
        problems.append("planted live-flagship shapes did not all fire")
    if not v["no_false_alarm_ok"]:
        problems.append("the classifier alarms on clean text")
    if v["planted_positives"] < 4 or v["planted_negatives"] < 6:
        problems.append("the validation gate no longer covers amendment 4")
    live = d["by_category"].get("LIVE_FLAGSHIP", 0)
    if live:
        problems.append("live flagship sites: %r" % d["live_flagship_sites"])
    if d["occurrences"] != sum(d["by_category"].values()):
        problems.append("category counts do not sum to the occurrence count")
    if problems:
        for p in problems:
            sys.stderr.write("FAIL: %s\n" % p)
        return 1
    print("row-3 verdict holds: 0 live flagship sites of %d occurrences "
          "over %d markdown files"
          % (d["occurrences"], d["markdown_files_scanned"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
