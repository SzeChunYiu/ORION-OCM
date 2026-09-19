#!/usr/bin/env python3
"""Repo-wide RATCHETING terminology gate (issue #833, row AB37).

The parent workflow runs the terminology gate over one package directory and
swallows its exit code, so a new package can land with any banned term. This
gate is repo-wide and blocking:

  * scope  = every markdown file under research/ plus repo-root markdown
             (the flagship document set), minus the declared authority docs;
  * signal = per (file, term) hit COUNT from the frozen parent gate
             research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py;
  * rule   = FAIL if any (file, term) count rises above the frozen baseline or
             a new (file, term) pair appears; PASS otherwise. Counts that fall
             are reported as ratchet progress and never fail the build.

Usage:
  python3 -I -B terminology_ratchet_v1.py                       # repo-wide check
  python3 -I -B terminology_ratchet_v1.py --owned-files LIST    # PR-scoped check
  python3 -I -B terminology_ratchet_v1.py --write               # rewrite baseline

Counted hits are PROSE hits: a hit on a verbatim issue-row quotation, inside
an inline code span or fenced block, or on an identifier token (a path, a
package name, snake_case) is exempt -- see `classify_hits`. A reviewer never
meets those as vocabulary, and five open PRs were failed on them.

On a pull request the gate is run with --owned-files, so a lane is failed only
for banned terms in files it added or grew. That is what keeps the gate from
crying wolf on another lane's PR - a gate that fires on work you did not do is
a gate that gets switched off.
"""
import importlib.util
import json
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
GATE = os.path.join(REPO, "research", "gmi-833-tranche-ab-ac-lit",
                    "GMI_TERMINOLOGY_CI_GATE_V1.py")
BASELINE = os.path.join(HERE, "TERMINOLOGY_BASELINE_V1.json")
# The main tip the committed baseline was regenerated at, when the count
# semantics changed from "every parent hit" to "prose hits only" (the three
# non-prose exemption classes below). `source_main` in the baseline stays the
# package freeze's pin; this is the measurement point of the counts.
REBASELINED_AT_MAIN = "b5193f32"

# Packages whose SUBJECT is the #833 terminology audit itself. They must quote
# the legacy terms verbatim - a crosswalk row named `machine species`, an AB row
# whose own governing phrase is `parent subtraction`, a freeze that quotes the
# issue row it may not reconcile - so scanning them measures the audit's own
# vocabulary rather than any paper-facing debt. The last three were added by
# gmi-833-ac-lanes-harness-v1 / gmi-833-ab-residual-definitions-v1 /
# gmi-833-aa-finite-universal-harness-v1 on the same criterion; their remaining
# 22 hits are quotations of row-named legacy terms (15) and text inside
# committed pre-implementation freezes that may not be edited after the fact (7).
# gmi-833-aa-fallacy-detectors-v1 is added on the same criterion: its rows name
# `morphology`, and the frozen parent it instruments exposes `remint_fixture` /
# `remint_grammar` as its public API, so the package cannot discuss its own
# subject without them.
# gmi-833-aa-ledger-gate-v1 is deliberately NOT excluded: it has zero hits.
EXCLUDED_PACKAGES = ("gmi-833-tranche-ab-ac-lit", "gmi-833-ab-terminology-harness-v1",
                     "gmi-833-terminology-migration-v1", "gmi-833-checklist-mirror-v1",
                     "gmi-833-ac-lanes-harness-v1", "gmi-833-ab-residual-definitions-v1",
                     "gmi-833-aa-finite-universal-harness-v1",
                     "gmi-833-aa-fallacy-detectors-v1")


def load_gate():
    spec = importlib.util.spec_from_file_location("gmi_term_gate_v1", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flagship_files():
    out = []
    root = os.path.join(REPO, "research")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        rel = os.path.relpath(dirpath, root)
        top = rel.split(os.sep)[0]
        if top in EXCLUDED_PACKAGES:
            continue
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    for fn in sorted(os.listdir(REPO)):
        if fn.endswith(".md"):
            out.append(os.path.join(REPO, fn))
    return sorted(out)


# A freeze document must quote its issue rows BYTE-EXACT and must never be
# edited after its receipt exists -- that is the custody property the whole
# #833 standard rests on. Those rows contain banned terms. So the ratchet and
# the closure standard were in direct conflict: a lane could satisfy one only
# by falsifying a quotation or tampering with custody.
#
# Three lanes hit this independently, and 41 already-committed freezes carry
# the identical hit and were grandfathered into the baseline -- so the rule was
# never actually being enforced on them either.
#
# Resolution: a hit inside a VERBATIM QUOTATION of an issue row does not count.
# The lane did not choose that wording; the issue did. Prose the lane writes is
# still scanned normally, including prose in the same file.
QUOTE_PREFIXES = ("- [ ] ", "- [x] ", "> - [ ] ", "> - [x] ", "> ")

# A quoted row is also recognised by SHAPE, not only by prefix: freezes number
# their quoted rows ("3. `- [ ] ...`"), wrap them in inline code
# ("`- [x] ...`") or both. Any line carrying a checkbox row inside backticks,
# or opening with a (possibly numbered, possibly block-quoted) checkbox row, is
# a quotation of the issue. The lane did not choose that wording.
_QUOTED_ROW_ANYWHERE = re.compile(r"`\s*-\s\[[ xX]\]\s")
_QUOTED_ROW_LEADING = re.compile(r"^\s*(?:>\s*)*(?:\d+[.)]\s*)?`?\s*-\s\[[ xX]\]\s")


def _is_quoted_issue_row(hit):
    """True when the hit sits on a verbatim checklist row quoted from the issue.

    The scanner already hands us the line text, so this needs no file access.
    """
    text = str(hit.get("text", ""))
    if text.lstrip().startswith(QUOTE_PREFIXES):
        return True
    return bool(_QUOTED_ROW_ANYWHERE.search(text) or _QUOTED_ROW_LEADING.match(text))


# IDENTIFIERS ARE NOT PROSE.  The parent gate matches `\bselection\b` and
# `\bmorphology\b`; `-`, `/` and `.` are word boundaries, so a package name
# (`gmi-833-morphology-selection-v1`), a path
# (`research/gmi-833-ae-morphology-sweep-v1/test_morphology_sweep_v1.py`), an
# inline code span and a fenced code block all fire as if a sentence had been
# written. Five open PRs were failed on such tokens -- a heading that is the
# package's own directory name, a `cmp` command in a reproduce block, a
# parent-pin table of package names. A reviewer reading the paper never meets
# them as vocabulary. Three exemption classes, each narrowly shaped:
#
#   1. inline code spans (`...`) and fenced code blocks (``` ... ```);
#   2. identifier tokens: a whitespace-delimited token that contains `/` or `_`,
#      opens with `gmi-<digits>-`, ends with `-v<digits>`, or carries a file
#      extension.  A hyphenated PROSE compound ("morphology-selection
#      correspondence", "the morphology-sweep lane") has none of these marks
#      and still fires;
#   3. headings whose only occurrence is the package's own directory name are
#      class 2 by construction (`# gmi-833-ae-morphology-sweep-v1`,
#      `# Parent ownership -- gmi-833-...`).
#
# The exemption is computed per LINE and per TERM by masking the non-prose
# spans and re-running the parent's own pattern on what is left: a line that
# names `gmi-833-morphology-selection-v1` AND says "the selection changes"
# keeps exactly one prose hit for `selection`.
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_TOKEN_PUNCT = "()[]{}<>,;:!?'\"*|"
_PKG_NAME = re.compile(r"(?:^|/)gmi-\d+-")
_VERSION_SUFFIX = re.compile(r"-v\d+/?$")
_FILE_EXT = re.compile(r"\.(?:py|md|json|jsonl|ya?ml|txt|csv|toml|sh|html|pdf|tex)$", re.IGNORECASE)
_PATH_PREFIXES = ("research/", "papers/", "src/", "tests/", ".github/", "docs/",
                  "/", "./", "../", "~/")


def _is_identifier_token(token):
    """A whitespace-delimited token that is a name, not a word.

    `_` never occurs inside prose; a file extension, a `gmi-<n>-` package name
    (bare or path-qualified), a `-v<n>` version suffix and a path rooted at a
    repository directory are names. A plain slash compound ("morphology/
    resource cost") and a hyphenated compound ("morphology-selection rule")
    are prose and are NOT identifiers.
    """
    core = token.strip(_TOKEN_PUNCT).rstrip(".")
    if not core:
        return False
    if "_" in core:
        return True
    if _FILE_EXT.search(core) or _PKG_NAME.search(core) or _VERSION_SUFFIX.search(core):
        return True
    if "/" in core and core.startswith(_PATH_PREFIXES):
        return True
    return False


# ISSUE SUBSECTION HEADINGS ARE QUOTATIONS.  A freeze names the subsection it
# may reconcile by the issue's own heading ("Z11 -- Intelligence Morphology
# Benchmark"), usually in its title line, and a committed freeze may never be
# edited. The lane did not choose that wording; the issue did -- the same
# criterion as the checklist-row exemption above. The headings are read from
# the committed comment snapshots (`research/*/COMMENT_*_SNAPSHOT_V1.md`, the
# `### ` lines), so the exemption is exactly as wide as the issue itself. Only
# the verbatim heading text is masked; prose on the same line is still scanned.
_SNAPSHOT_GLOB = os.path.join(REPO, "research", "*", "COMMENT_*_SNAPSHOT_V1.md")


def issue_subsection_headings():
    """Verbatim `### ` heading texts of every committed issue-comment snapshot."""
    import glob
    heads = set()
    for path in sorted(glob.glob(_SNAPSHOT_GLOB)):
        try:
            with open(path, encoding="utf-8") as fh:
                for ln in fh:
                    if ln.startswith("### "):
                        text = ln[4:].strip()
                        if len(text) >= 12:
                            heads.add(text)
        except (OSError, UnicodeDecodeError):
            continue
    return sorted(heads, key=len, reverse=True)


ISSUE_HEADINGS = issue_subsection_headings()


def mask_issue_headings(line):
    out = line
    for head in ISSUE_HEADINGS:
        if head in out:
            out = out.replace(head, " " * len(head))
    return out


def mask_non_prose(line):
    """Blank inline code spans, verbatim issue subsection headings and
    identifier tokens, preserving length so the parent's word-boundary patterns
    see the same prose they would in print."""
    out = _INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)
    out = mask_issue_headings(out)
    pieces = []
    for tok in re.split(r"(\s+)", out):
        if tok and not tok.isspace() and _is_identifier_token(tok):
            pieces.append(" " * len(tok))
        else:
            pieces.append(tok)
    return "".join(pieces)


def _fenced_lines(path):
    """1-based line numbers that sit inside a ``` fence (the fence lines too)."""
    fenced = set()
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except (OSError, UnicodeDecodeError):
        return fenced
    inside = False
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("```"):
            inside = not inside
            fenced.add(i)
            continue
        if inside:
            fenced.add(i)
    return fenced


def _compiled_patterns(gate):
    pats = {}
    for name, spec in gate.BANNED_TERMS_DEFAULT.items():
        if spec.get("active", True):
            pats[name] = re.compile(spec["pattern"], re.IGNORECASE | re.MULTILINE)
    return pats


def prose_hit_count(term_pattern, line):
    """How many matches of the parent's pattern survive on the prose of `line`."""
    return len(term_pattern.findall(mask_non_prose(line)))


def classify_hits(hits, gate=None):
    """Split the parent's hits into (prose_hits, exempt_counts).

    `exempt_counts` is a dict with the three exemption classes:
      quoted_issue_rows, code_spans (inline + fenced), identifiers.
    """
    gate = gate or load_gate()
    pats = _compiled_patterns(gate)
    fenced_cache = {}
    grouped = {}
    order = []
    for h in hits:
        key = (h["file"], h["term"], h["line_no"])
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(h)
    prose = []
    exempt = {"quoted_issue_rows": 0, "code_spans": 0, "identifiers": 0}
    for key in order:
        group = grouped[key]
        path, term, line_no = key
        line = str(group[0].get("text", ""))
        if _is_quoted_issue_row(group[0]):
            exempt["quoted_issue_rows"] += len(group)
            continue
        if path not in fenced_cache:
            fenced_cache[path] = _fenced_lines(path)
        if line_no in fenced_cache[path]:
            exempt["code_spans"] += len(group)
            continue
        pat = pats.get(term)
        if pat is None:
            prose.extend(group)
            continue
        keep = min(len(group), prose_hit_count(pat, line))
        dropped = len(group) - keep
        if dropped:
            # attribute: was it code or an identifier that carried the match?
            after_code = len(pat.findall(mask_issue_headings(_INLINE_CODE.sub(
                lambda m: " " * len(m.group(0)), line))))
            code_dropped = len(group) - min(len(group), after_code)
            exempt["code_spans"] += code_dropped
            exempt["identifiers"] += dropped - code_dropped
        prose.extend(group[:keep])
    return prose, exempt


def measure(files=None, root=None):
    gate = load_gate()
    root = root or REPO
    files = files if files is not None else flagship_files()
    hits = gate.scan_paths(files, context="paper-facing")
    prose, exempt = classify_hits(hits, gate)
    counts = {}
    for h in prose:
        rel = os.path.relpath(h["file"], root)
        counts.setdefault(rel, {})
        counts[rel][h["term"]] = counts[rel].get(h["term"], 0) + 1
    total = sum(sum(v.values()) for v in counts.values())
    return {"files_scanned": len(files), "files_with_hits": len(counts),
            "total_hits": total, "counts": counts,
            "raw_hits": len(hits),
            "quoted_issue_rows_exempt": exempt["quoted_issue_rows"],
            "code_spans_exempt": exempt["code_spans"],
            "identifiers_exempt": exempt["identifiers"]}


def prose_hits(files, root=None):
    """The surviving prose hits themselves (file, term, line_no, text), for
    reporting which lines a lane must actually reword."""
    gate = load_gate()
    root = root or REPO
    prose, _ = classify_hits(gate.scan_paths(files, context="paper-facing"), gate)
    return [dict(h, file=os.path.relpath(h["file"], root)) for h in prose]


def check(baseline, live, owned_new_files=None):
    """`owned_new_files` scopes the new-file rule. On a pull request it is the
    set of markdown paths in the PR's own diff: a lane is failed for banned
    terms in files IT added, never for files another lane added. A new file
    with hits outside that set is reported informationally
    (`unowned_new_files_with_hits`) and does not fail the build. Passing None
    keeps the strict repo-wide rule (used on push to main)."""
    return _check(baseline, live, owned_new_files)


def _check(baseline, live, owned_new_files=None):
    regressions = []
    new_files = []
    improved = 0
    removed = 0
    b = baseline["counts"]
    l = live["counts"]
    for path, terms in sorted(l.items()):
        if path not in b:
            new_files.append(path)
            continue
        for term, n in sorted(terms.items()):
            prev = b[path].get(term, 0)
            if n > prev:
                regressions.append("%s [%s] %d -> %d" % (path, term, prev, n))
            elif n < prev:
                improved += 1
                removed += prev - n
    for path, terms in sorted(b.items()):
        if path not in l:
            improved += 1
            removed += sum(terms.values())
    unowned = []
    if owned_new_files is not None:
        owned = set(owned_new_files)
        unowned = [p for p in new_files if p not in owned]
        new_files = [p for p in new_files if p in owned]
    return {"regressions": regressions, "new_files_with_hits": new_files,
            "unowned_new_files_with_hits": unowned,
            "improved_entries": improved, "sites_removed_vs_baseline": removed}


def main(argv):
    live = measure()
    if "--write" in argv:
        doc = {"schema": "GMI_TERMINOLOGY_RATCHET_BASELINE_V1",
               "issue": 833, "row": "AB37",
               "source_main": "91c6d2876ba80c517a186e28fce3bdbe4e3fc218",
               "gate": "research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CI_GATE_V1.py",
               "excluded_packages": list(EXCLUDED_PACKAGES),
               "excluded_reason": "terminology-authority and migration-log packages quote the "
                                  "banned terms definitionally; the parent gate self-skips its "
                                  "own authority docs for the same reason",
               "count_semantics": (
                   "prose hits only: hits on verbatim issue-row quotations "
                   "(checkbox rows, numbered or backticked), inside inline code "
                   "spans or fenced code blocks, and on identifier tokens "
                   "(paths, snake_case, gmi-<n>- package names, -v<n> suffixes, "
                   "file extensions) are exempt; see classify_hits"),
               "rebaselined_at_main": REBASELINED_AT_MAIN,
               "files_scanned": live["files_scanned"],
               "files_with_hits": live["files_with_hits"],
               "total_hits": live["total_hits"],
               "raw_hits": live["raw_hits"],
               "quoted_issue_rows_exempt": live["quoted_issue_rows_exempt"],
               "code_spans_exempt": live["code_spans_exempt"],
               "identifiers_exempt": live["identifiers_exempt"],
               "counts": live["counts"]}
        json.dump(doc, open(BASELINE, "w"), indent=1, sort_keys=True)
        print("baseline written: %d hits in %d of %d files"
              % (live["total_hits"], live["files_with_hits"], live["files_scanned"]))
        return 0
    baseline = json.load(open(BASELINE))
    owned = None
    if "--owned-files" in argv:
        listing = argv[argv.index("--owned-files") + 1]
        owned = [ln.strip() for ln in open(listing) if ln.strip()]
    rep = check(baseline, live, owned)
    print(json.dumps({"files_scanned": live["files_scanned"],
                      "total_hits_live": live["total_hits"],
                      "total_hits_baseline": baseline["total_hits"],
                      "regressions": len(rep["regressions"]),
                      "new_files_with_hits": len(rep["new_files_with_hits"]),
                      "sites_removed_vs_baseline": rep["sites_removed_vs_baseline"],
                      "unowned_new_files_with_hits": len(rep["unowned_new_files_with_hits"]),
                      "new_file_scope": ("PR diff" if owned is not None else "repo-wide")},
                     indent=2, sort_keys=True))
    for r in rep["regressions"][:50]:
        print("  REGRESSION " + r)
    for f in rep["new_files_with_hits"][:50]:
        print("  NEW FILE WITH BANNED TERMS " + f)
    for f in rep["unowned_new_files_with_hits"][:50]:
        print("  (informational, not this PR's file) " + f)
    if rep["regressions"] or rep["new_files_with_hits"]:
        print("[ratchet] FAIL - terminology debt increased")
        return 1
    print("[ratchet] PASS - no new banned-term site")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
