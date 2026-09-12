# Calibration of the V2 guard against real emitters and tamper controls; every expectation is
# fixed here before the run. The V1 guard is run on the same inputs for comparison.
import json, re, sys
sys.path.insert(0, sys.argv[2]); import guard_v2 as G2
R = sys.argv[1]
V1_OPEN = r"\bopen\s*\(\s*['\"][^'\"]*['\"]\s*,\s*['\"][wax]"
p2 = open(R + "/research/m2-traversal-capital-v1/m2p2/authored/emit_worlds.py").read()
p3 = open(R + "/research/m2-traversal-capital-v1/m2p3/authored/emit_worlds.py").read()
cases = [
 ("M2-P2 emitter (real)", p2, "ACCEPT"),
 ("M2-P3 package A emitter (real)", p3, "ACCEPT"),
 ("tamper: package A plus a second write", p3 + '\nopen("worlds.jsonl", "a").write("x")\n', "REJECTED_CANNOT_CHECK"),
 ("tamper: package A writing another path", p3.replace('open("worlds.jsonl", "w")', 'open("other.txt", "w")'), "REJECTED_CANNOT_CHECK"),
 ("tamper: M2-P2 with its name rebound to another path", p2.replace('OUT_NAME = "worlds.jsonl"', 'OUT_NAME = "../worlds.jsonl"'), "REJECTED_CANNOT_CHECK"),
 ("tamper: package A plus a read of another file", p3 + '\nopen("/etc/passwd").read()\n', "REJECTED_CANNOT_CHECK"),
 ("tamper: package A plus an os.environ read", p3 + '\nimport os\nx = os.environ\n', "REJECTED_CANNOT_CHECK"),
 ("tamper: package A plus subprocess", p3 + '\nimport subprocess\n', "REJECTED_CANNOT_CHECK")]
allok = True
for name, src, want in cases:
    g = G2.guard(src); v1 = "REJECTED_CANNOT_CHECK" if re.search(V1_OPEN, src) else "ACCEPT(open-pattern only)"
    ok = g["verdict"] == want; allok &= ok
    print("%-50s V2 %-22s expected %-22s %s | V1 open-pattern: %s | %s" % (name, g["verdict"], want, "OK" if ok else "MISMATCH", v1, "; ".join(g["open_problems"] + g["forbidden_modules"] + g["forbidden_calls"])[:120]))
print("CALIBRATION", "PASS" if allok else "FAIL", "%d cases" % len(cases))
