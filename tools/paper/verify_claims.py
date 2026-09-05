#!/usr/bin/env python3
"""Verify every numeric claim in docs/paper/manuscript/main.md against its receipt.

Stdlib only. Reads docs/paper/manuscript/claims_map.md, whose tables have the columns

    | # | Section | Phrase | Source | Check |

and, for every row, does three things:

1. checks that ``Phrase`` occurs verbatim in main.md (the sentence the row binds);
2. resolves ``Source`` (one or more repository paths separated by ``;``, optionally
   prefixed ``V2:`` for the ORION-V2 theory directory) and confirms the file exists
   (a missing ORION-V2 working-tree file is read with ``git show origin/main:``);
3. evaluates every clause in ``Check`` (clauses separated by ``;``).

Clause grammar (whitespace-insensitive around ``=``):

    <expr> = <value>
    @<k> <expr> = <value>         evaluate against the k-th source file (1-based)
    contains "literal"            the source file contains the literal text
    note: free text               no check; the row is UNCHECKABLE with that note

``<expr>`` for JSON sources is a dotted path such as ``deterministic_results.v4.tests.A_conversations.positive``;
segments may carry ``[i]`` (index) or ``[*]`` (every element); a segment may be quoted with
double quotes when it contains ``.`` or spaces. Aggregates: ``sum(<path>)`` (numbers, booleans,
or ``"a/b"`` fraction strings, which sum to a fraction), ``count(<path>)``, ``min(<path>)``,
``max(<path>)``, ``keys(<path>)`` (sorted key list) and ``statuscount(<path>, <prefix>)`` (number of
list elements whose ``status`` field starts with ``<prefix>``; ``<prefix>`` may be ``PREFIX|PREFIX2``).
For a glob source (``docs/theorems/*.json``) the expression is evaluated on every matching file
and numeric results are summed.

``<value>`` is a number (compared after rounding the found value to the printed decimals), a
fraction ``a/b`` (compared exactly), a bracketed list ``[..]`` (element-wise, same rules), a quoted
string (exact), or a bare token (exact string match after ``str()``).

Statuses: OK, MISMATCH, UNCHECKABLE (no machine-checkable clause), MISSING_FILE, PHRASE_MISSING.
Exit code 0 when no MISMATCH, MISSING_FILE or PHRASE_MISSING row remains, else 1.

Usage:
    python tools/paper/verify_claims.py [--repo ROOT] [--v2-root PATH] [--claims FILE] [--manuscript FILE]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from fractions import Fraction

V2_PREFIX = "V2:"
V2_SUBDIR = "research/machine-epistemics-theory"


# ----------------------------------------------------------------------------- parsing helpers
def split_top(s: str, sep: str) -> list[str]:
    """Split on ``sep`` outside quotes, brackets and parentheses."""
    out, buf, depth, q = [], [], 0, None
    for ch in s:
        if q:
            buf.append(ch)
            if ch == q:
                q = None
            continue
        if ch in "\"'":
            q = ch
            buf.append(ch)
            continue
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return [x.strip() for x in out if x.strip()]


def parse_table_rows(md: str) -> list[dict]:
    rows = []
    for line in md.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("#", "") or set(cells[0]) <= set("-: "):
            continue
        if not re.match(r"^\d+$", cells[0]):
            continue
        rows.append({"id": int(cells[0]), "section": cells[1], "phrase": cells[2],
                     "source": cells[3], "check": "|".join(cells[4:])})
    return rows


def unescape_cell(s: str) -> str:
    return s.replace("\\|", "|").replace("&#124;", "|")


def parse_value(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [parse_value(x) for x in split_top(v[1:-1], ",")]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return ("str", v[1:-1])
    if re.match(r"^-?\d+/\d+$", v):
        a, b = v.split("/")
        return ("frac", int(a), int(b))
    if re.match(r"^-?\d+(\.\d+)?([eE]-?\d+)?$", v):
        return ("num", v)
    if v in ("true", "True"):
        return ("bool", True)
    if v in ("false", "False"):
        return ("bool", False)
    if v in ("null", "None"):
        return ("none", None)
    return ("str", v)


# ----------------------------------------------------------------------------- path evaluation
def split_path(path: str) -> list:
    segs, i, n = [], 0, len(path)
    while i < n:
        if path[i] == ".":
            i += 1
            continue
        if path[i] == '"':
            j = path.index('"', i + 1)
            segs.append(("key", path[i + 1:j]))
            i = j + 1
            continue
        if path[i] == "[":
            j = path.index("]", i)
            tok = path[i + 1:j]
            segs.append(("all", None) if tok == "*" else ("idx", int(tok)))
            i = j + 1
            continue
        j = i
        while j < n and path[j] not in ".[":
            j += 1
        segs.append(("key", path[i:j]))
        i = j
    return segs


def walk(obj, segs: list, star: bool = False):
    """Return (value, star_flag). With ``[*]`` the value is a flat list."""
    for k, (kind, val) in enumerate(segs):
        if kind == "all":
            items = obj if isinstance(obj, list) else list(obj.values())
            rest = segs[k + 1:]
            out = []
            for it in items:
                v, _ = walk(it, rest, True)
                if isinstance(v, list) and rest and any(s[0] == "all" for s in rest):
                    out.extend(v)
                else:
                    out.append(v)
            return out, True
        if kind == "idx":
            obj = obj[val]
        else:
            if isinstance(obj, dict):
                if val not in obj:
                    raise KeyError(val)
                obj = obj[val]
            elif isinstance(obj, list):
                obj = obj[int(val)]
            else:
                raise KeyError(val)
    return obj, star


def as_fraction(v):
    if isinstance(v, str) and re.match(r"^\d+/\d+$", v):
        a, b = v.split("/")
        return int(a), int(b)
    return None


def aggregate(fn: str, values, arg: str | None):
    if fn == "count":
        return len(values) if isinstance(values, (list, dict)) else 1
    if fn == "keys":
        return sorted(values.keys())
    if fn == "statuscount":
        prefixes = [p.strip() for p in (arg or "").split("|")]
        return sum(1 for r in values if isinstance(r, dict)
                   and any(str(r.get("status", "")).startswith(p) for p in prefixes))
    vals = values if isinstance(values, list) else [values]
    if vals and all(as_fraction(v) for v in vals):
        num = sum(as_fraction(v)[0] for v in vals)
        den = sum(as_fraction(v)[1] for v in vals)
        return f"{num}/{den}"
    nums = [float(v) if not isinstance(v, bool) else float(v) for v in vals]
    if fn == "sum":
        s = sum(nums)
        return int(s) if s == int(s) else s
    if fn == "min":
        return min(nums)
    if fn == "max":
        return max(nums)
    raise ValueError(fn)


def evaluate(expr: str, data):
    m = re.match(r"^(sum|count|min|max|keys|statuscount|valuecount)\((.*)\)$", expr.strip())
    if m:
        fn, inner = m.group(1), m.group(2)
        arg = None
        if fn in ("statuscount", "valuecount"):
            inner, arg = [x.strip() for x in split_top(inner, ",")][:2]
        v, _ = walk(data, split_path(inner.strip()))
        if fn == "valuecount":
            vals = v if isinstance(v, list) else list(v.values()) if isinstance(v, dict) else [v]
            return sum(1 for x in vals if str(x) == arg.strip().strip('"'))
        return aggregate(fn, v, arg)
    v, _ = walk(data, split_path(expr.strip()))
    return v


# ----------------------------------------------------------------------------- comparison
def decimals(s: str) -> int:
    return len(s.split(".")[1]) if "." in s and "e" not in s.lower() else 0


def compare(found, expected) -> tuple[bool, str]:
    if isinstance(expected, list):
        if not isinstance(found, list) or len(found) != len(expected):
            return False, f"found {found!r}"
        for f, e in zip(found, expected):
            ok, _ = compare(f, e)
            if not ok:
                return False, f"found {found!r}"
        return True, f"found {found!r}"
    kind = expected[0]
    if kind == "num":
        target = expected[1]
        fr = as_fraction(found)
        if fr:
            found = fr[0] / fr[1]
        try:
            fv = float(found)
        except (TypeError, ValueError):
            return False, f"found {found!r}"
        d = decimals(target)
        return round(fv, d) == round(float(target), d), f"found {found!r}"
    if kind == "frac":
        fr = as_fraction(found)
        if fr:
            return (fr[0], fr[1]) == (expected[1], expected[2]), f"found {found!r}"
        return False, f"found {found!r}"
    if kind == "bool":
        return found is expected[1], f"found {found!r}"
    if kind == "none":
        return found is None, f"found {found!r}"
    return str(found) == expected[1], f"found {found!r}"


# ----------------------------------------------------------------------------- sources
class Sources:
    def __init__(self, repo: str, v2_root: str):
        self.repo, self.v2_root, self.cache = repo, v2_root, {}

    def resolve(self, spec: str) -> list[str]:
        spec = spec.strip()
        if spec.startswith(V2_PREFIX):
            name = spec[len(V2_PREFIX):].strip()
            return [os.path.join(self.v2_root, V2_SUBDIR, name)]
        if any(ch in spec for ch in "*?"):
            return sorted(glob.glob(os.path.join(self.repo, spec)))
        return [os.path.join(self.repo, spec)]

    def text(self, path: str) -> str | None:
        if path in self.cache:
            return self.cache[path]
        txt = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                txt = fh.read()
        elif path.startswith(self.v2_root):
            rel = os.path.relpath(path, self.v2_root)
            try:
                txt = subprocess.run(["/usr/bin/git", "-C", self.v2_root, "show", f"origin/main:{rel}"],
                                     capture_output=True, text=True, check=True).stdout
            except (subprocess.CalledProcessError, FileNotFoundError):
                txt = None
        self.cache[path] = txt
        return txt

    def json(self, path: str):
        key = ("json", path)
        if key not in self.cache:
            txt = self.text(path)
            self.cache[key] = json.loads(txt) if txt is not None else None
        return self.cache[key]


# ----------------------------------------------------------------------------- row check
def check_row(row: dict, src: Sources, manuscript: str) -> tuple[str, str]:
    phrase = unescape_cell(row["phrase"]).strip().strip('"')
    if phrase and phrase not in manuscript:
        return "PHRASE_MISSING", f"phrase not in main.md: {phrase[:60]!r}"
    specs = [s for s in split_top(unescape_cell(row["source"]), ";") if s and s != "—"]
    files_per_spec = [src.resolve(s) for s in specs]
    for spec, files in zip(specs, files_per_spec):
        if not files:
            return "MISSING_FILE", f"no file matches {spec}"
        for f in files:
            if src.text(f) is None:
                return "MISSING_FILE", f"missing {spec}"
    clauses = split_top(unescape_cell(row["check"]), ";")
    if not clauses or all(c.lower().startswith("note:") for c in clauses):
        return "UNCHECKABLE", "; ".join(clauses) if clauses else "no check"
    details = []
    for clause in clauses:
        if clause.lower().startswith("note:"):
            details.append(clause)
            continue
        k = 1
        m = re.match(r"^@(\d+)\s+(.*)$", clause)
        if m:
            k, clause = int(m.group(1)), m.group(2)
        if k > len(files_per_spec):
            return "MISMATCH", f"clause refers to source {k}, only {len(files_per_spec)} given"
        files = files_per_spec[k - 1]
        m = re.match(r'^contains\s+"(.*)"$', clause.strip(), re.S)
        if m:
            lit = m.group(1)
            if not any(lit in (src.text(f) or "") for f in files):
                return "MISMATCH", f"literal not found: {lit[:70]!r}"
            details.append(f"contains ok: {lit[:40]!r}")
            continue
        if "=" not in clause:
            return "MISMATCH", f"cannot parse clause {clause!r}"
        expr, val = clause.rsplit("=", 1)
        expected = parse_value(val)
        if expr.strip() == "filecount":
            ok, det = compare(len(files), expected)
            if not ok:
                return "MISMATCH", f"filecount expected {val.strip()} but {det}"
            details.append(f"filecount = {val.strip()}")
            continue
        try:
            if len(files) > 1:
                found = None
                for f in files:
                    v = evaluate(expr, src.json(f))
                    found = v if found is None else found + v
            else:
                found = evaluate(expr, src.json(files[0]))
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return "MISMATCH", f"{expr.strip()}: cannot resolve ({exc!r})"
        ok, det = compare(found, expected)
        if not ok:
            return "MISMATCH", f"{expr.strip()} expected {val.strip()} but {det}"
        details.append(f"{expr.strip()} = {val.strip()}")
    return "OK", "; ".join(details)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(here, "..", "..")))
    ap.add_argument("--v2-root", default=os.path.abspath(os.path.join(here, "..", "..", "..", "..", "ORION-V2")))
    ap.add_argument("--claims", default=None)
    ap.add_argument("--manuscript", default=None)
    args = ap.parse_args()
    claims = args.claims or os.path.join(args.repo, "docs/paper/manuscript/claims_map.md")
    manuscript = args.manuscript or os.path.join(args.repo, "docs/paper/manuscript/main.md")
    with open(claims, encoding="utf-8") as fh:
        rows = parse_table_rows(fh.read())
    with open(manuscript, encoding="utf-8") as fh:
        text = fh.read()
    src = Sources(args.repo, args.v2_root)
    counts: dict[str, int] = {}
    print(f"{'row':>4} | {'section':<10} | {'status':<15} | detail")
    print("-" * 100)
    for row in rows:
        status, detail = check_row(row, src, text)
        counts[status] = counts.get(status, 0) + 1
        print(f"{row['id']:>4} | {row['section'][:10]:<10} | {status:<15} | {detail}")
    print("-" * 100)
    print("rows:", len(rows), " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    bad = sum(counts.get(k, 0) for k in ("MISMATCH", "MISSING_FILE", "PHRASE_MISSING"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
