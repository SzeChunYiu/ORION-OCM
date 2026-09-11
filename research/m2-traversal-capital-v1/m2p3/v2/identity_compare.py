# Identity check for the V2 orchestrator: its receipt on M2-P2's authored package must equal
# M2-P2's committed stage-2 receipt in every scientific field. Excluded, and listed: the
# static_guard block (the one intended change), host, paths (in values and in dict keys), timing
# and receipt-schema text.
import json, sys
new = json.load(open(sys.argv[1])); old = json.load(open(sys.argv[2]))
EXCLUDE = {"static_guard", "host", "authored_dir", "timing", "timing_seconds", "status", "next"}
def scrub(x):
    if isinstance(x, dict): return {(k.rsplit("/", 1)[-1] if "/" in k else k): scrub(v) for k, v in x.items() if k not in ("file", "pristine_file", "tampered_copy_of", "path", "wall_seconds", "seconds")}
    if isinstance(x, list): return [scrub(v) for v in x]
    if isinstance(x, str) and ("/home/" in x or "/Users/" in x or "/tmp/" in x): return x.rsplit("/", 1)[-1]
    return x
keys = sorted((set(new) | set(old)) - EXCLUDE)
diffs = []
for k in keys:
    a, b = scrub(new.get(k)), scrub(old.get(k))
    if k == "authored_files":
        a = {p.rsplit("/", 1)[-1]: v for p, v in (new.get(k) or {}).items()}; b = {p.rsplit("/", 1)[-1]: v for p, v in (old.get(k) or {}).items()}
    if a != b: diffs.append(k)
print("guard: new", new.get("static_guard", {}).get("verdict"), "| old", old.get("static_guard", {}).get("verdict"))
print("stage2_verdict: new", new.get("stage2_verdict"), "| old", old.get("stage2_verdict"))
print("compared fields", len(keys), "| differing:", diffs if diffs else "NONE")
print("IDENTITY", "PASS" if not diffs else "FAIL")
