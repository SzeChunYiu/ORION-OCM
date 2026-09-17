import json
import re

import a2_extension_v1 as x

pkgs = x.census_packages()
OPS = re.compile(r"\b(OPCODES|OPS|PRIMITIVES|OPERATORS|INSTRUCTIONS|OP_TABLE)\s*[=:{]", re.I)
BASIS = re.compile(r"primitive (basis|set)|opcode list|instruction set is|set of (primitives|operators)|grammar is", re.I)
DEFOP = re.compile(r"\bdef\s+(op|prim|opcode|instr)_\w+|\bclass\s+(Op|Prim|Opcode)\w*", re.I)
MDROW = re.compile(r"\|\s*`[^`]{1,40}`\s*\|", re.M)
MANYDEF = re.compile(r"\bdef\s+\w+")

combo = {}
for pkg in sorted(pkgs):
    pdir = x.RESEARCH / pkg
    sig = set()
    for p, t in x.primitive_defining_files(pdir):
        if OPS.search(t):
            sig.add("OPS")
        if BASIS.search(t):
            sig.add("BASIS")
        if DEFOP.search(t):
            sig.add("DEFOP")
        if MDROW.search(t):
            sig.add("MDROW")
        if len(MANYDEF.findall(t)) >= 2:
            sig.add("MANYDEF")
    if sig:
        combo[pkg] = sorted(sig)

print("packages with any signal:", len(combo))
base = {"OPS", "BASIS", "DEFOP"}
for extra in ([], ["MANYDEF"], ["MDROW"], ["MANYDEF", "MDROW"]):
    n = sum(1 for s in combo.values() if (set(s) & base) or (extra and set(s) & set(extra)))
    label = "+ " + (",".join(extra) if extra else "none")
    print(f"OPS/BASIS/DEFOP {label}: {n}")
missing = [p for p, s in combo.items() if not (set(s) & base) and "MANYDEF" in s]
print("missing-base with MANYDEF:", missing[:10])
print("robustness-controls signals:", combo.get("gmi-833-robustness-controls-v1"))
print("aj9b signals:", combo.get("gmi-833-aj9b-k01-blind-recovery-v1"))
print("af-barrier pkgs present?:", [p for p in combo if p.startswith("gmi-833-af-barrier")][:3])
with open("diag_census_out.json", "w") as fh:
    json.dump(combo, fh, indent=1, sort_keys=True)
