"""Evaluate candidates from a frozen EVAL_MANIFEST.json (fail closed).

Used by later tranches (MZ-D9 hostile tests, cross-domain).  The manifest
must list candidates with genotype digests; each task evaluates its slice,
receipts every outcome, never overwrites a crash.
"""
from __future__ import annotations

import json
import os
import sys

ROOT, TASK = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, ROOT)
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402
from evaluation.evaluate import evaluate_genome  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402

with open(os.path.join(ROOT, "manifests", "EVAL_MANIFEST.json")) as f:
    MAN = json.load(f)
N_SHARDS = MAN.get("shards", 1)
items = MAN["candidates"][TASK::N_SHARDS]
receipt = make_receipt("eval-%s-t%d" % (MAN["manifest_id"], TASK),
                       MAN["created_utc"], os.environ.get("ZOO_HOST", "local"),
                       MAN["tier"], MAN["config_digest"])
for it in items:
    g = OCMMorphologyGenomeV1.from_json_obj(it["genome"])
    r = evaluate_genome(g, use_cache=False)
    append_record(receipt, it["index"], {
        "g": r["genotype_digest"][:16], "p": r["phenotype_digest"][:16],
        "f": int(r["feasible"]), "dev": None if not r["feasible"]
        else round(r["evaluation"]["solved_fraction"], 4)})
assert verify_receipt(receipt)
out = os.path.join(ROOT, "results", "EVAL_%s_t%d.json" % (MAN["manifest_id"], TASK))
with open(out, "w") as f:
    json.dump(receipt, f)
print("task %d evaluated %d candidates head=%s" % (TASK, len(items), receipt["head_sha256"]))
