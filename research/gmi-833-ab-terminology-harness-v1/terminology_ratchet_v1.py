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

A file whose current bytes are pinned by a receipt in its own package (a
freeze at its `freeze_commit`, a snapshot hashed in a record) is IMMUTABLE:
it is measured and reported but the new-file rule does not fail a lane for
it, because the only way to reword it would be to break custody -- see
`custody_state`. Nothing is exempt by file NAME.

On a pull request the gate is run with --owned-files, so a lane is failed only
for banned terms in files it added or grew. That is what keeps the gate from
crying wolf on another lane's PR - a gate that fires on work you did not do is
a gate that gets switched off.
"""
import hashlib
import importlib.util
import json
import io
import os
import re
import shutil
import subprocess
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


def mask_non_prose(line):
    """Blank inline code spans and identifier tokens, preserving length so the
    parent's word-boundary patterns see the same prose they would in print."""
    out = _INLINE_CODE.sub(lambda m: " " * len(m.group(0)), line)
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
            after_code = len(pat.findall(_INLINE_CODE.sub(
                lambda m: " " * len(m.group(0)), line)))
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


# ---------------------------------------------------------------------------
# IMMUTABLE CUSTODY FILES.  A freeze (and its amendments) must never be edited
# after its receipt exists -- that is the custody property the #833 standard
# rests on, and the reason a lane cannot reword a banned term there. But the
# rule is not "files named FREEZE": a freeze nobody has pinned is an ordinary
# markdown file, editable and enforced. A file is IMMUTABLE iff its CURRENT
# BYTES are pinned by a receipt in its own package, verified two ways:
#
#   PINNED_HASH    the file's git blob sha (or sha256 / md5 of its bytes)
#                  appears in a JSON record of the package (MANIFEST_V1.json,
#                  RESULT_V1.json, *_RECEIPT*.json, registers, reconciliation
#                  snapshots pinned by `*_md5_at_extraction`, ...);
#   PINNED_COMMIT  a commit the package names under a freeze/amendment/custody
#                  key (`freeze_commit`, `freeze_commits`, `freeze_amendments`,
#                  ...) carries the SAME blob at the same path -- the
#                  freeze-first ordering the standard requires, checked on bytes
#                  rather than branch topology so a squash merge cannot fake or
#                  break it;
#   UNREACHABLE    the package names a custody commit that is not in the object
#                  store, so the pin cannot be verified: reported distinctly and
#                  ENFORCED (never silently passed);
#   UNPINNED       nothing pins these bytes: editable, enforced.
#
# Editing a pinned file changes its bytes, breaks the pin, and the file becomes
# UNPINNED -- the exemption cannot outlive the custody it rests on. Immutable
# files are still measured and REPORTED (`immutable_files_with_hits`); they are
# only excluded from the new-file rule. Count regressions stay enforced
# everywhere: a pinned file's count cannot rise without its bytes changing.
_HEX_TOKEN = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{7,40}(?![0-9a-fA-F])")


def _looks_like_commit(token):
    """A full 40-hex id, or an abbreviated one that carries at least one
    letter: a date (`20260913`) or a counter under a freeze key is not a
    commit, and treating it as one made a real package UNREACHABLE."""
    return len(token) == 40 or any(c in "abcdefABCDEF" for c in token)
_CUSTODY_KEY = re.compile(r"freeze|amend|custody", re.IGNORECASE)
_CUSTODY_STATES = ("PINNED_HASH", "PINNED_COMMIT", "UNREACHABLE", "UNPINNED")


def _git():
    return shutil.which("git") or "/usr/bin/git"


def blob_sha1(data):
    """git's blob object id for `data` (no git needed)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _package_dir(path, root):
    """research/<pkg> for a file under research/, else the file's own dir."""
    rel = os.path.relpath(os.path.abspath(path), root)
    parts = rel.split(os.sep)
    if len(parts) >= 3 and parts[0] == "research":
        return os.path.join(root, parts[0], parts[1])
    return os.path.dirname(os.path.abspath(path))


def _receipt_jsons(path, root):
    dirs = {_package_dir(path, root), os.path.dirname(os.path.abspath(path))}
    out = {}
    for d in sorted(dirs):
        try:
            names = sorted(os.listdir(d))
        except OSError:
            continue
        for fn in names:
            if fn.endswith(".json") and fn != os.path.basename(path):
                try:
                    out[os.path.join(d, fn)] = open(os.path.join(d, fn), encoding="utf-8").read()
                except (OSError, UnicodeDecodeError):
                    pass
    return out


def _custody_commit_tokens(doc):
    """Hex tokens found under freeze/amendment/custody keys, recursively."""
    found = []

    def walk(node, under):
        if isinstance(node, dict):
            for k, v in node.items():
                hit = under or bool(_CUSTODY_KEY.search(str(k)))
                if hit:
                    found.extend(_HEX_TOKEN.findall(str(k)))
                walk(v, hit)
        elif isinstance(node, list):
            for v in node:
                walk(v, under)
        elif under and isinstance(node, str):
            found.extend(_HEX_TOKEN.findall(node))
    walk(doc, False)
    seen = []
    for t in found:
        t = t.lower()
        if t not in seen and _looks_like_commit(t):
            seen.append(t)
    return seen


def _blob_at(commit, rel, root):
    """('BLOB', sha) | ('ABSENT', None) | ('UNREACHABLE', None)."""
    try:
        r = subprocess.run([_git(), "-C", root, "rev-parse", "--verify", "-q",
                            "%s:%s" % (commit, rel)], capture_output=True, text=True)
    except (OSError, ValueError):
        return ("UNREACHABLE", None)
    if r.returncode == 0 and r.stdout.strip():
        return ("BLOB", r.stdout.strip())
    try:
        e = subprocess.run([_git(), "-C", root, "cat-file", "-e", commit + "^{commit}"],
                           capture_output=True, text=True)
    except (OSError, ValueError):
        return ("UNREACHABLE", None)
    return ("ABSENT", None) if e.returncode == 0 else ("UNREACHABLE", None)


def custody_state(path, root=None):
    """Classify `path` into one of `_CUSTODY_STATES`; see the block comment."""
    root = os.path.abspath(root or REPO)
    path = os.path.abspath(path)
    try:
        data = open(path, "rb").read()
    except OSError:
        return {"state": "UNPINNED", "pinned_by": None, "reason": "unreadable"}
    hashes = (blob_sha1(data), hashlib.sha256(data).hexdigest(), hashlib.md5(data).hexdigest())
    receipts = _receipt_jsons(path, root)
    for jpath in sorted(receipts):
        if any(h in receipts[jpath] for h in hashes):
            return {"state": "PINNED_HASH", "pinned_by": os.path.relpath(jpath, root),
                    "reason": "current bytes hashed in a package record"}
    tokens = []
    for jpath in sorted(receipts):
        try:
            doc = json.loads(receipts[jpath])
        except ValueError:
            continue
        for t in _custody_commit_tokens(doc):
            if t not in tokens:
                tokens.append(t)
    rel = os.path.relpath(path, root)
    unreachable = []
    for t in tokens:
        kind, sha = _blob_at(t, rel, root)
        if kind == "BLOB" and sha == hashes[0]:
            return {"state": "PINNED_COMMIT", "pinned_by": t,
                    "reason": "same blob at the named custody commit"}
        if kind == "UNREACHABLE":
            unreachable.append(t)
    if unreachable:
        return {"state": "UNREACHABLE", "pinned_by": None,
                "reason": "custody commit(s) not in object store: %s" % ",".join(unreachable[:5])}
    return {"state": "UNPINNED", "pinned_by": None,
            "reason": "no package record pins these bytes"}


def is_immutable(state):
    return state.get("state") in ("PINNED_HASH", "PINNED_COMMIT")


def check(baseline, live, owned_new_files=None, custody=None, root=None):
    """`owned_new_files` scopes the new-file rule. On a pull request it is the
    set of markdown paths in the PR's own diff: a lane is failed for banned
    terms in files IT added, never for files another lane added. A new file
    with hits outside that set is reported informationally
    (`unowned_new_files_with_hits`) and does not fail the build. Passing None
    keeps the strict repo-wide rule (used on push to main).

    `custody` maps a repo-relative path to a `custody_state` dict; the default
    consults the package receipts under `root` (the repository). A new file
    whose bytes are pinned is moved from the enforced list to
    `immutable_files_with_hits` (informational, with its state and pin)."""
    root = os.path.abspath(root or REPO)
    if custody is None:
        custody = lambda rel: custody_state(os.path.join(root, rel), root)  # noqa: E731
    return _check(baseline, live, owned_new_files, custody)


def _check(baseline, live, owned_new_files=None, custody=None):
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
    immutable = []
    custody_states = {}
    if custody is not None:
        for p in new_files + unowned:
            st = custody(p)
            custody_states[p] = st["state"]
            if is_immutable(st):
                immutable.append({"path": p, "state": st["state"], "pinned_by": st["pinned_by"],
                                  "owned": p in new_files, "hits": sum(l[p].values())})
        pinned = {e["path"] for e in immutable}
        new_files = [p for p in new_files if p not in pinned]
        unowned = [p for p in unowned if p not in pinned]
    return {"regressions": regressions, "new_files_with_hits": new_files,
            "unowned_new_files_with_hits": unowned,
            "immutable_files_with_hits": immutable,
            "custody_states": custody_states,
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
                      "immutable_files_with_hits": len(rep["immutable_files_with_hits"]),
                      "unreachable_custody_files": sorted(
                          p for p, s in rep["custody_states"].items() if s == "UNREACHABLE"),
                      "new_file_scope": ("PR diff" if owned is not None else "repo-wide")},
                     indent=2, sort_keys=True))
    for r in rep["regressions"][:50]:
        print("  REGRESSION " + r)
    for f in rep["new_files_with_hits"][:50]:
        print("  NEW FILE WITH BANNED TERMS %s [custody: %s]"
              % (f, rep["custody_states"].get(f, "n/a")))
    for f in rep["unowned_new_files_with_hits"][:50]:
        print("  (informational, not this PR's file) " + f)
    for e in rep["immutable_files_with_hits"][:50]:
        print("  (informational, immutable custody file, %s by %s, %d hit(s)%s) %s"
              % (e["state"], e["pinned_by"], e["hits"], "" if e["owned"] else ", not this PR's file",
                 e["path"]))
    if rep["regressions"] or rep["new_files_with_hits"]:
        print("[ratchet] FAIL - terminology debt increased")
        return 1
    print("[ratchet] PASS - no new banned-term site")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
