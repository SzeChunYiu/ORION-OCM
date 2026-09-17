import json
import re
from pathlib import Path

import a2_extension_v1 as x

pkgs = x.census_packages()

VOCAB = re.compile(r"primitive|operator|instruction set|opcode|grammar|DSL", re.I)


def vocab_files(pdir):
    out = []
    for p in sorted(pdir.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix not in (".py", ".md", ".txt", ".json"):
            continue
        try:
            t = p.read_text(errors="replace")
        except OSError:
            continue
        if len(t) > 2_000_000:
            continue
        if VOCAB.search(t) or VOCAB.search(p.stem):
            out.append(t)
    return out


VARIANTS = {
    "ops_assign": re.compile(r"\b(OPCODES|OPS|PRIMITIVES|OPERATORS|INSTRUCTIONS|OP_TABLE)\s*[=:{]", re.I),
    "json_key": re.compile(r"[\"'](?:opcodes?|operators?|primitives?|instructions?)[\"']\s*:", re.I),
    "backtick_ops": re.compile(r"`[a-z_][a-z0-9_]{0,20}`\s*[-:\u2014]|\bdefine[sd]?\s+\d+\s+(primitive|operator|opcode)", re.I),
    "basis_phrase": re.compile(r"primitive (basis|set)|opcode list|instruction set|set of (primitives|operators)|operator set", re.I),
    "def_op": re.compile(r"\bdef\s+(op|prim|opcode|instr)_\w+|\bclass\s+(Op|Prim|Opcode)\w*", re.I),
    "def_any2": re.compile(r"\bdef\s+\w+"),
    "md_row": re.compile(r"\|\s*`[^`]{1,40}`\s*\|", re.M),
    "quotelist": re.compile(r"(?:^|\n)\s*[-*]\s*`[a-z_][a-z0-9_]{0,20}`", re.M),
    "kind_dispatch": re.compile(r"kind\s*==|opcode\s*==|\bop\s*==|operation\s*==", re.I),
    "grammar_assign": re.compile(r"\bGRAMMAR\w*\s*[=:]|\bDSL\w*\s*[=:]", re.I),
}
A2_RE = re.compile(r"state_access|content_dependent_routing|verifier_access|strategy_signature|Sigma\(", re.I)

stats = {}
for pkg in sorted(pkgs):
    pdir = x.RESEARCH / pkg
    if not pdir.exists():
        stats[pkg] = {"missing": True}
        continue
    vfs = vocab_files(pdir)
    row = {k: any(VARIANTS[k].search(t) for t in vfs) for k in VARIANTS}
    row["n_vocab_files"] = len(vfs)
    files_by = {k: [t for t in vfs if VARIANTS[k].search(t)] for k in VARIANTS}
    row["a2_by"] = {k: any(A2_RE.search(t) for t in ts) for k, ts in files_by.items()}
    stats[pkg] = row

with open("diag_census_out.json", "w") as fh:
    json.dump(stats, fh, indent=1, sort_keys=True)

n_vocab = sum(1 for r in stats.values() if r.get("n_vocab_files", 0) > 0)
print("packages with >=1 vocab file:", n_vocab)
combos = [
    ["json_key"],
    ["ops_assign", "json_key"],
    ["ops_assign", "basis_phrase", "json_key"],
    ["ops_assign"],
    ["ops_assign", "basis_phrase"],
    ["ops_assign", "basis_phrase", "def_op"],
    ["ops_assign", "basis_phrase", "def_op", "grammar_assign"],
    ["ops_assign", "basis_phrase", "def_op", "grammar_assign", "kind_dispatch"],
    ["ops_assign", "basis_phrase", "def_op", "grammar_assign", "kind_dispatch", "def_any2"],
    ["ops_assign", "basis_phrase", "def_op", "grammar_assign", "kind_dispatch", "def_any2", "md_row"],
    ["ops_assign", "basis_phrase", "def_op", "grammar_assign", "kind_dispatch", "def_any2", "md_row", "quotelist"],
    ["ops_assign", "basis_phrase", "def_op", "grammar_assign", "kind_dispatch", "def_any2", "md_row", "quotelist", "json_key"],
    ["ops_assign", "basis_phrase", "def_op", "grammar_assign", "kind_dispatch", "def_any2", "md_row", "quotelist", "json_key", "backtick_ops"],
]
for c in combos:
    prim = [p for p, r in stats.items() if r.get("n_vocab_files", 0) > 0 and any(r.get(k) for k in c)]
    cov = [p for p in prim if any(stats[p]["a2_by"].get(k) for k in c if stats[p].get(k))]
    unaud = [p for p in prim if p not in cov]
    mark = " <== MATCHES 109/108/1" if (len(prim), len(unaud), len(cov)) == (109, 108, 1) else ""
    print(f"{'+'.join(c)}: prim={len(prim)} unaud={len(unaud)} cov={len(cov)}{mark}")
print("robustness row:", stats.get("gmi-833-robustness-controls-v1"))
print("aj9b row:", {k: v for k, v in stats.get("gmi-833-aj9b-k01-blind-recovery-v1", {}).items() if k != "n_vocab_files"})
