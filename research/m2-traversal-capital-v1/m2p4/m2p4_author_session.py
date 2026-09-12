#!/usr/bin/env python3
"""Build the M2-P4 author-session prompt. BUILDS ONLY — it never spawns anything.

The author unit is a FRESH session given ONLY the frozen neutral spec, verbatim. This
script exists so the prompt is a versioned artifact rather than an ad-hoc in-session
step (M2-P2 and M2-P3 left no committed wrapper, so their prompts survive only in
scratch files). The framing lines are M2-P3's, unchanged; only the spec text and the
studio path differ.

It asserts the spec's frozen sha256 before embedding it, and it asserts that the
assembled prompt contains NONE of the things the freeze forbids disclosing to the
author: the viability economics, the f + k^2 bound, the calibration worlds, or any
repository/lane vocabulary.
"""
import argparse, hashlib, io, json, re, sys
from pathlib import Path

SPEC_SHA = "382e6152fcdf9569039a14e46eae45fcc8609ab8b70d628e605c688ed71f64ea"

FRAMING = """You are working alone on a self-contained design task. Everything you need is in the task text below.

Rules for this session:
- Work ONLY inside this directory: {studio}
- Create your files there, and run Python there if you need to check your work. Do not read, list or open anything outside that directory, and do not use any web or search tool.
- When you are done, the directory must contain exactly the three files the task asks for: emit_worlds.py, worlds.jsonl (produced by running emit_worlds.py from inside that directory), and AUTHOR_NOTES.md.
- Reply with a short summary of what you made.

The task text follows, verbatim, between the two lines of equals signs.

==========
{spec}
==========
"""

# things the freeze forbids the author from seeing (freeze.forbidden)
LEAK_PATTERNS = [
    r"f \+ k\^?2", r"k\s*>=\s*10", r"viab", r"floor", r"members_min",
    r"calibrat", r"ORION", r"OCM", r"m2p\d", r"REVIVAL", r"ledger",
    r"guided-first", r"PARENT_", r"CONTINUED", r"RESET\b", r"repository",
]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--studio", required=True, help="scratch dir OUTSIDE the repo")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    spec_path = Path(a.spec)
    spec = io.open(spec_path, encoding="utf-8").read()
    got = hashlib.sha256(spec.encode()).hexdigest()
    if got != SPEC_SHA:
        print("REFUSE: spec sha256 %s != frozen %s" % (got[:16], SPEC_SHA[:16]))
        return 2
    if Path(a.studio).resolve().is_relative_to(Path.cwd().resolve()):
        print("REFUSE: studio directory is inside the repository")
        return 3

    prompt = FRAMING.format(studio=a.studio, spec=spec.rstrip("\n"))

    # the spec itself is the ONLY place these words may appear; check the framing only
    framing_only = prompt.replace(spec, "")
    leaks = [p for p in LEAK_PATTERNS if re.search(p, framing_only, re.I)]
    if leaks:
        print("REFUSE: framing leaks forbidden context: %s" % leaks)
        return 4
    # and the spec must itself be clean of lane vocabulary (taxonomy scan is the real gate)
    spec_leaks = [p for p in (r"ORION", r"OCM", r"m2p\d", r"REVIVAL", r"guided-first",
                              r"PARENT_", r"f \+ k\^?2", r"calibrat")
                  if re.search(p, spec, re.I)]
    if spec_leaks:
        print("REFUSE: spec itself carries forbidden vocabulary: %s" % spec_leaks)
        return 5

    io.open(a.out, "w", encoding="utf-8").write(prompt)
    print(json.dumps({
        "spec": str(spec_path), "spec_sha256": got, "studio": a.studio,
        "out": a.out, "prompt_chars": len(prompt),
        "spec_embedded_verbatim": spec.rstrip("\n") in prompt,
        "framing_leak_check": "CLEAN", "spec_leak_check": "CLEAN",
        "note": "prompt built; this script never spawns an author session",
    }, indent=1))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
