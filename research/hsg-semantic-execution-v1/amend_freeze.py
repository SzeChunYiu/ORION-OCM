"""Append supersession S1 to FREEZE_D19_D20_V1.json, keeping the original
manifest in place -- the same discipline FREEZE_V1 uses for its amendments,
and the discipline make_freeze_d19_d20.py enforces when reading a prior freeze."""
import collections, hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "FREEZE_D19_D20_V1.json")
d = json.load(open(p), object_pairs_hook=collections.OrderedDict)
if any(a.get("id") == "S1" for a in d.get("amendments", [])):
    print("S1 already recorded"); sys.exit(0)
def sha(rel):
    return hashlib.sha256(open(os.path.join(HERE, rel), "rb").read()).hexdigest()
new = collections.OrderedDict(d["manifest_sha256"])
new["D19_D20_PROTOCOL_V1.json"] = sha("D19_D20_PROTOCOL_V1.json")
d["amendments"] = [collections.OrderedDict([
    ("id", "S1"),
    ("utc", "2026-09-10"),
    ("cause", "D20 hostile H-D20b: the frozen instantiation has an empty drop-candidate set on any world whose initial block already meets Bad (7 of 15 concretely-UNSAFE worlds), so those worlds are structurally immune to the plant."),
    ("changes", {"D19_D20_PROTOCOL_V1.json": "supersessions[] added recording instantiation S1 for H-D20b: drop each of EVERY single abstract transition, exhaustively. No world, seed, n grid, arm, endpoint or clean control altered."}),
    ("affected_arm_rerun", True),
    ("frozen_result_retained", True),
    ("manifest_sha256_s1", new),
    ("worlds_or_endpoints_touched", False),
    ("original_manifest_preserved_above", True)])]
json.dump(d, open(p, "w"), indent=1, sort_keys=True)
open(p, "a").write("\n")
print("S1 recorded; protocol sha now", new["D19_D20_PROTOCOL_V1.json"][:16])
