"""Row-3 verification instrument: classify every residual `prior-free` site.

Section Z row 3 of issue comment 5684819296 asks that informal `prior-free`
language in flagship claims be replaced with a defensible term, based on a
literature audit.  The corpus edit belongs to
`research/gmi-833-terminology-migration-v1`; the literature audit belongs to
`research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md` rows 9 and
26.  This file is neither: it is the instrument that decides whether the corpus
is actually clean, by classifying every surviving occurrence into the five
categories frozen in `FREEZE_V1.md` section 6 and asserting that the
`LIVE_FLAGSHIP` category is empty.

The classifier is validated before its verdict is used: planted live-flagship
sentences must fire, and known-clean text must not.

Run:  python3 -I -B prior_free_site_audit_v1.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)

TOKEN = re.compile(r"prior-free", re.IGNORECASE)

AUTHORITY_MARKERS = (
    "gmi-833-tranche-ab-ac-lit/",
    "gmi-833-ab-terminology-harness-v1/",
    "gmi-833-terminology-migration-v1/",
    "GMI_TERMINOLOGY_CROSSWALK",
    "BANNED_PAPER_TERMS",
    "GMI_TERMINOLOGY_CI_GATE",
    "gmi-833-z-z2-minimal-prior-v1/",
)
MIRROR_MARKERS = ("MIRROR", "SNAPSHOT", "comments/comment_", "_MIRROR_")
NEGATION_MARKERS = (
    "does not mean", "is not", "not prior-free", "never", "ill-posed",
    "impossible", "explicitly **not**", "explicitly not", "no such claim",
    "cannot", "literally prior-free", "literally assumption-free",
)
QUALIFIED_PREFIX = re.compile(r"architecture-prior-free", re.IGNORECASE)
QUALIFIED_PHRASE = re.compile(r"p3/p4 prior-free condition", re.IGNORECASE)
ROW_MARKERS = ("- [ ] ", "- [x] ", "# H.", "# D.")
EMPHASIS = re.compile(r"[*_`]+")
MENTION = re.compile(r"[`\u2018\u201c\"']\s*prior-free\s*[`\u2019\u201d\"']",
                     re.IGNORECASE)
ARROW = re.compile(r"prior-free`?\s*(->|\u2192)", re.IGNORECASE)
# Issue #1049 repair (see INSTRUMENT_REPAIR_1049_V1.md): an issue section header
# or checklist row quoted INSIDE a backtick span is issue text, exactly like a
# row that opens the line. Only a span that itself begins with the row marker
# AND carries the token qualifies; the span may run past the end of the line
# (a header quoted across a line break).
CODE_SPAN = re.compile(r"`([^`]*)(?:`|$)")
QUOTED_ROW = re.compile(r"^\s*(?:#{1,2} [A-Z]{1,2}\.\s|- \[[ xX]\] )")


def normalise(text):
    """Amendment 4: markdown emphasis must not defeat a negation marker."""
    return EMPHASIS.sub("", text)


def classify(path, line, prev=""):
    """Return one of the six frozen categories for one occurrence.

    `prev` is the preceding physical line; amendment 4 widened the scope from
    one line to two so a negation carried across a line break is seen.
    """
    if any(mk in path for mk in AUTHORITY_MARKERS):
        return "AUTHORITY"
    if any(mk in path for mk in MIRROR_MARKERS):
        return "MIRROR"
    stripped = line.lstrip()
    if any(stripped.startswith(mk) for mk in ROW_MARKERS):
        return "MIRROR"
    if any(QUOTED_ROW.match(span) and TOKEN.search(span)
           for span in CODE_SPAN.findall(line)):
        return "MIRROR"
    if QUALIFIED_PREFIX.search(line) or QUALIFIED_PHRASE.search(line):
        return "QUALIFIED_TERM"
    if MENTION.search(line) or ARROW.search(line):
        return "MENTION_NOT_USE"
    scope = normalise(prev + " " + line).lower()
    if any(mk in normalise(mk).lower() and normalise(mk).lower() in scope
           for mk in NEGATION_MARKERS):
        return "NEGATION"
    return "LIVE_FLAGSHIP"


def scan_text(path, text):
    out = []
    lines = text.split("\n")
    for n, line in enumerate(lines, 1):
        if TOKEN.search(line):
            prev = lines[n - 2] if n >= 2 else ""
            out.append({"file": path, "line": n,
                        "category": classify(path, line, prev),
                        "text": line.strip()[:200]})
    return out


def scan_corpus(root):
    hits = []
    files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        base = os.path.basename(dirpath)
        rel = os.path.relpath(dirpath, root)
        if not (rel.startswith("gmi-833-") or "gmi-833-" in rel):
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            files += 1
            full = os.path.join(dirpath, fn)
            relf = os.path.relpath(full, os.path.dirname(root))
            with open(full, "r") as fh:
                hits.extend(scan_text(relf, fh.read()))
    return files, hits


PLANTED_POSITIVE = [
    ("research/gmi-833-fake-pkg-v1/CLAIM.md",
     "Our search is prior-free and recovers the family from nothing."),
    ("research/gmi-833-fake-pkg-v1/ABSTRACT.md",
     "We present a prior-free derivation of known machine-intelligence families."),
    # amendment 4: the repairs must not silence a genuine live claim
    ("research/gmi-833-fake-pkg-v1/BOLD.md",
     "The enumeration is **prior-free** and needs no assumptions."),
    ("research/gmi-833-fake-pkg-v1/WRAP.md",
     "The result was obtained by a search that is\nprior-free at every stage."),
    # issue #1049 repair: a quoted header nearby must not shelter a live claim
    ("research/gmi-833-fake-pkg-v1/NEARQUOTE.md",
     "Under the `# H.` header our recovery is prior-free throughout."),
]
PLANTED_NEGATIVE = [
    ("research/gmi-833-fake-pkg-v1/CORE.md",
     "The search is architecture-uncommitted; it does not mean prior-free."),
    ("research/gmi-833-fake-pkg-v1/THEORY.md",
     "We use architecture-prior-free with the residual-prior ledger named."),
    ("research/gmi-833-checklist-mirror-v1/comments/comment_1.md",
     "- [ ] Prove why literally prior-free search is ill-posed."),
    # amendment 4: the three real shapes that defeated the first classifier
    ("research/gmi-833-fake-pkg-v1/MENTION.md",
     "the `prior-free` \u2192 `architecture-uncommitted` migration has a lane"),
    ("research/gmi-833-fake-pkg-v1/CROSSLINE.md",
     "recorded as a screened status, never as\na proof of prior-freeness."),
    ("research/gmi-833-fake-pkg-v1/BOLDNEG.md",
     "opaque summaries \u2014 it does **not** mean prior-free."),
    # issue #1049 repair: the #833 section header quoted inline, closed and
    # continued across a line break (the seven real-scale freezes' shape)
    ("research/gmi-833-fake-pkg-v1/QUOTEDHEADER.md",
     "Section of the issue: the `# H. Prior-free derivation of known"),
    ("research/gmi-833-fake-pkg-v1/QUOTEDHEADER2.md",
     "the `# H. Prior-free derivation of known machine-intelligence families` header line"),
]


def validate():
    """Recall on planted positives AND the no-alarm case on clean text."""
    fired = []
    for path, line in PLANTED_POSITIVE:
        cats = [h["category"] for h in scan_text(path, line)]
        fired.append(cats.count("LIVE_FLAGSHIP") == len(cats) and len(cats) > 0)
    quiet = []
    for path, line in PLANTED_NEGATIVE:
        cats = [h["category"] for h in scan_text(path, line)]
        quiet.append(bool(cats) and "LIVE_FLAGSHIP" not in cats)
    clean = scan_text("research/gmi-833-clean-v1/CORE.md",
                      "The search is architecture-uncommitted at P3.")
    return {
        "planted_positives": len(PLANTED_POSITIVE),
        "planted_positives_detected": sum(1 for x in fired if x),
        "planted_negatives": len(PLANTED_NEGATIVE),
        "planted_negatives_not_flagged": sum(1 for x in quiet if x),
        "no_alarm_on_clean_line": clean == [],
        "planted_negative_categories":
            [ [h["category"] for h in scan_text(p, l)] for p, l in PLANTED_NEGATIVE],
        "recall_ok": all(fired),
        "no_false_alarm_ok": all(quiet) and clean == [],
    }


def main():
    val = validate()
    files, hits = scan_corpus(RESEARCH)
    counts = {}
    for h in hits:
        counts[h["category"]] = counts.get(h["category"], 0) + 1
    live = [h for h in hits if h["category"] == "LIVE_FLAGSHIP"]
    out = {
        "schema": "GMI_833_Z2_PRIOR_FREE_SITE_AUDIT_V1",
        "validation": val,
        "markdown_files_scanned": files,
        "occurrences": len(hits),
        "by_category": counts,
        "live_flagship_sites": live,
        "H9_no_live_flagship_site": len(live) == 0,
        "literature_audit_authority": [
            "research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md row 9"
            " (architecture-prior-free; Wolpert & Macready 1997)",
            "research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md row 26"
            " (prior-free -> architecture-agnostic / architecture-uncommitted /"
            " family-agnostic search; Wolpert & Macready 1997, Mitchell 1980)",
        ],
        "corpus_edit_authority": [
            "research/gmi-833-terminology-migration-v1/MIGRATION_LOG_V1.md",
            "research/gmi-833-terminology-migration-v1/MIGRATION_LOG_V2.md",
        ],
        "hits": hits,
    }
    with open(os.path.join(HERE, "PRIOR_FREE_SITE_AUDIT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"files": files, "occurrences": len(hits),
                      "by_category": counts, "live": len(live),
                      "validation": val}, sort_keys=True))
    return 0 if (val["recall_ok"] and val["no_false_alarm_ok"]) else 1


if __name__ == "__main__":
    sys.exit(main())
