#!/usr/bin/env python3
"""GMI terminology CI gate v1 (#833, sections AB/AC).

Scans a given markdown file (or a package directory of markdown files) for
paper-facing banned terms from BANNED_PAPER_TERMS_V1.md, reports line hits,
and exits 0 only if the target is clean or the finding list is explicitly
acknowledged (an --acknowledge IDs file lists accepted findings).

Discharges the AB box "terminology review as CI/checklist gate for flagship
documents" by being wired into a path-scoped workflow.

Design:
  * stdlib-only (no numpy); safe to run on the Mac for files this size.
  * The "obligation" term is banned ONLY in paper-facing prose contexts and is
    skipped inside the BANNED list's own definitional rows.
  * A bare "prior-free" match requires the pattern not to be preceded by a
    leading architecture-agnostic token in the same line; simply: the regex
    flags "prior-free" unless "architecture-" precedes it on the same line
    within the prior-free window.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BANNED_TERMS_DEFAULT = {
    "obligation": {
        "pattern": r"\bobligation(?:s)?\b",
        "reason": "claim-governance tuple in v1; deontic overload in paper-facing prose",
        "replacement": "task / behavioral specification / formal specification / requirement",
        "contexts": ["paper-facing"],
        "active": True,
    },
    "prior-free (bare)": {
        "pattern": r"(?<!architecture-)\bprior-free\b(?!\w)",
        "reason": "implicitly assumption-free; still ill-posed as a literal claim",
        "replacement": "architecture-agnostic / architecture-uncommitted / architecture-prior-free + ledger",
        "contexts": ["paper-facing", "ledger"],
        "active": True,
    },
    "remint": {
        "pattern": r"\bremint(?:s|ing|ed)?\b",
        "reason": "internal-process metaphor; reviewer cannot tell what was redone",
        "replacement": "independent regeneration / relabeling control / independent replication",
        "contexts": ["paper-facing"],
        "active": True,
    },
    "negative twin": {
        "pattern": r"\bnegative twin(?:s)?\b",
        "reason": "undefined for the reader",
        "replacement": "matched negative control / ablation / placebo / negative control",
        "contexts": ["paper-facing"],
        "active": True,
    },
    "parent subtraction": {
        "pattern": r"\bparent subtraction(?:s)?\b",
        "reason": "obscure metaphor",
        "replacement": "subsumption analysis / ablation / novelty analysis / strongest-baseline comparison",
        "contexts": ["paper-facing"],
        "active": True,
    },
    "neutral search": {
        "pattern": r"\bneutral search(?:es)?\b",
        "reason": "no search is neutral; the procedure must be named",
        "replacement": "family-blind enumerative search / grammar-based synthesis / evolutionary search",
        "contexts": ["paper-facing"],
        "active": True,
    },
    "machine species": {
        "pattern": r"\bmachine specie[cs]\b",
        "reason": "biological species analogy without defined equivalence",
        "replacement": "model family / architecture family / equivalence class",
        "contexts": ["paper-facing"],
        "active": True,
    },
    "bare morphology": {
        "pattern": r"\bmorphology\b",
        "reason": "where architecture/model-class works the loaded biological term is banned",
        "replacement": "architecture / model class / representation / mechanism",
        "contexts": ["paper-facing"],
        "active": True,
        "exception_lines": [
            "structure across heterogeneous computational organizations",
            "cross-organization",
            "organizations when one organizing principle",
        ],
    },
    "bare carrier": {
        "pattern": r"\bcarrier(?:s)?\b",
        "reason": "unrepresentational, substrate-vague in paper-facing text",
        "replacement": "state representation / state space / substrate / representation space",
        "contexts": ["paper-facing"],
        "active": True,
    },
    "bare selection (undisambiguated)": {
        "pattern": r"\bselection\b",
        "reason": "five distinct academic senses",
        "replacement": "algorithm / model / architecture / configuration / evolutionary selection",
        "contexts": ["paper-facing"],
        "active": True,
        "exception_terms": [
            "algorithm selection", "model selection", "architecture search",
            "configuration selection", "evolutionary selection", "selection law",
            "selection mapping", "selection process", "natural selection", "selection problem",
        ],
    },
    "open-ended as bigness (bare)": {
        "pattern": r"\bopen-?ended\b",
        "reason": "must tie to the OEE (artificial life) literature, not mere bigness",
        "replacement": "open-ended evolution / open-endedness (OEE sense)",
        "contexts": ["paper-facing"],
        "active": False,  # flag only in OEE-sensitive documents; see usage
    },
    "proof by finite enumeration": {
        "pattern": r"\bproof\b by finite (?:enumeration|manipulation)|finite enumeration.{0,60}\bproof\b",
        "reason": "exhaustive finite run is a reconstruction, not a universal proof",
        "replacement": "reconstruction / certified finite check",
        "contexts": ["paper-facing"],
        "active": True,
    },
}


def _load_banned(term_list_path: Path | None) -> dict:
    if term_list_path is None:
        return BANNED_TERMS_DEFAULT
    data = json.loads(term_list_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"term%d" % i: {"pattern": t} for i, t in enumerate(data)}
    return data


def _compile(patterns: dict):
    compiled = {}
    for name, spec in patterns.items():
        if not spec.get("active", True):
            continue
        try:
            compiled[name] = re.compile(spec["pattern"], re.IGNORECASE | re.MULTILINE)
        except re.error as exc:  # pragma: no cover
            raise SystemExit("gate: bad regex for %r: %s" % (name, exc))
    return compiled


def _apply_exceptions(term_name, spec, line: str) -> bool:
    exceptions = spec.get("exception_lines", []) + spec.get("exception_terms", [])
    lowered = line.lower()
    return any(ex.lower() in lowered for ex in exceptions)


SELF_AUTHORITY_CONTEXT_LINES = (
    "banned", "migration rule", "legacy gmi term", "proposed paper term",
    "sanctioned", "replacement", "exit code", "ci gate", "authority",
    "route", "crosswalk", "would not", "misleads",
)


def _authority_doc(path: Path) -> bool:
    """True for files that are themselves the terminology-authority artifacts
    (crosswalk, banned list, lanes, template, this gate's own docstring), where
    banned terms appear as quoted/named-and-replaced objects and must be
    REJECTED as targets but never as violations."""
    name = path.name.lower()
    return any(
        k in name
        for k in (
            "gmi_terminology_crosswalk_v2",
            "banned_paper_terms_v1",
            "expert_literature_lanes_v1",
            "what_is_actually_new_template_v1",
            "gmi_terminology_ci_gate_v1",
        )
    )


def scan_paths(targets, banned=None, context="paper-facing", acknowledge=()):
    """Return list of hit dicts: {file, term, line_no, text}."""
    banned = banned if banned is not None else BANNED_TERMS_DEFAULT
    banned = {k: v for k, v in banned.items() if v.get("active", True) and context in v.get("contexts", [context])}
    compiled = _compile(banned)

    files = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            files.extend(sorted(p.glob("**/*.md")))
        else:
            files.append(p)

    hits = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            hits.append({"file": str(f), "term": "__unreadable__", "line_no": 0, "text": ""})
            continue
        for term, rx in compiled.items():
            for m in rx.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                line = text.splitlines()[line_no - 1] if text.splitlines() else ""
                if _apply_exceptions(term, banned[term], line):
                    continue
                if _authority_doc(f):
                    continue
                hits.append({"file": str(f), "term": term, "line_no": line_no, "text": line.strip()})
    if acknowledge:
        ack = set(acknowledge)
        hits = [h for h in hits if not (str(h["file"]), h["line_no"]) in ack]
    return hits


def main(argv=None):  # noqa: C901
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="+", help="md file(s) or package dir(s)")
    ap.add_argument("--term-list", default=None, help="JSON term list (optional override)")
    ap.add_argument("--context", default="paper-facing", choices=["paper-facing", "ledger", "all"])
    ap.add_argument("--acknowledge", nargs="*", default=(), help="file:line pairs to exempt")
    ap.add_argument("--json", action="store_true", help="emit JSON findings")
    args = ap.parse_args(argv)

    hits = scan_paths(args.targets, banned=_load_banned(args.term_list), context=args.context, acknowledge=args.acknowledge)
    if args.json:
        print(json.dumps({"hits": hits}, indent=2))
    else:
        for h in hits:
            print("%s:%d  [%s]  %s" % (h["file"], h["line_no"], h["term"], h["text"]))
        print("[gate] %d banned-term hit(s) in %d target(s)" % (len(hits), len(args.targets)))
    return 0 if not hits else 1


if __name__ == "__main__":
    sys.exit(main())
