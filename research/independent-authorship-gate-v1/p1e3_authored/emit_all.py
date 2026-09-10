"""Run every family emitter and write instances.jsonl deterministically."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from families import FAMILY_MODULES  # noqa: E402
import importlib  # noqa: E402


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    rows = []
    for mod_name in FAMILY_MODULES:
        mod = importlib.import_module("families." + mod_name)
        insts = mod.emit(mod.SEED)
        assert len(insts) >= 5, "%s emitted too few" % mod.FAMILY_NAME
        rows.extend(insts)
    ids = [r["instance_id"] for r in rows]
    assert len(set(ids)) == len(ids), "duplicate instance_id"
    path = os.path.join(here, "instances.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    print("families=%d instances=%d -> %s"
          % (len(FAMILY_MODULES), len(rows), path))


if __name__ == "__main__":
    main()
