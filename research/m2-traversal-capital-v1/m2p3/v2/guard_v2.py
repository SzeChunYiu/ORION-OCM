# V2 static guard for emit_worlds.py. Same rule as V1 ("no filesystem access beyond the one
# required write"); only the implementation changes: V1's regex forbade any open() with a
# literal path in a write mode, which rejects the spec-mandated write when it is spelled
# literally. V2 permits exactly one open() in a write mode whose target resolves to
# "worlds.jsonl" (a string literal, or a module-level name bound once to that literal), and
# forbids every other open(). V1's forbidden modules and other forbidden calls are unchanged.
import ast, re, sys
FORBIDDEN_MODULES = {"socket", "http", "urllib", "requests", "ftplib", "smtplib", "telnetlib", "xmlrpc", "asyncio",
    "threading", "multiprocessing", "subprocess", "socketserver", "email", "ssl", "ctypes", "pickle", "shelve", "dbm", "sqlite3"}
OTHER_FORBIDDEN_CALLS = [r"\bos\.(system|popen|exec\w*|spawn\w*)\s*\(", r"\bPath\s*\([^)]*\)\.write_text\s*\(",
    r"\bwrite_bytes\s*\(", r"\beval\s*\(", r"\bexec\s*\(", r"\b__import__\s*\(", r"\bos\.environ", r"\bgetenv\s*\("]
TARGET = "worlds.jsonl"
def guard(src):
    bad_modules = sorted(m for m in FORBIDDEN_MODULES if re.search(r"(?<![A-Za-z0-9_])" + m + r"(?![A-Za-z0-9_])", src))
    bad_calls = [p for p in OTHER_FORBIDDEN_CALLS if re.search(p, src)]
    tree = ast.parse(src)
    # module-level names bound exactly once, to a string literal
    binds = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            n = node.targets[0].id
            binds[n] = node.value.value if (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and n not in binds) else None
    opens = [c for c in ast.walk(tree) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "open"]
    problems = []; writes = 0
    for c in opens:
        a0 = c.args[0] if c.args else None
        target = a0.value if isinstance(a0, ast.Constant) else (binds.get(a0.id) if isinstance(a0, ast.Name) else None)
        mode = c.args[1] if len(c.args) > 1 else next((k.value for k in c.keywords if k.arg == "mode"), None)
        mode = mode.value if isinstance(mode, ast.Constant) else ("r" if mode is None else None)
        if not isinstance(mode, str) or not any(ch in mode for ch in "wax"):
            problems.append("open() that is not a write (line %d): only the one required write is allowed" % c.lineno); continue
        if target != TARGET:
            problems.append("write to a target other than %s (line %d)" % (TARGET, c.lineno)); continue
        writes += 1
    if writes != 1: problems.append("expected exactly one write to %s, found %d" % (TARGET, writes))
    ok = not bad_modules and not bad_calls and not problems
    return {"verdict": "ACCEPT" if ok else "REJECTED_CANNOT_CHECK", "forbidden_modules": bad_modules,
            "forbidden_calls": bad_calls, "open_problems": problems, "required_writes": writes}
if __name__ == "__main__":
    import json; print(json.dumps(guard(open(sys.argv[1]).read())))
