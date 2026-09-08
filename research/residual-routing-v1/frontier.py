"""R0-D1: what this study is bound to, recorded before anything is measured.

Issue #152 requires the frontier to be re-read rather than inherited from older
comments, and every receipt to be source-bound.  This module records the commit,
the branch, and the sha256 of every file whose behaviour the study depends on.
If any of them changes, the receipt is stale and the tests say so rather than the
numbers quietly becoming wrong.
"""
from __future__ import annotations

import hashlib
import pathlib
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[2]

#: Files the incumbent selection policy actually lives in. Chosen by reading the
#: call path, not by directory: solve.py contains compose/check/decide,
#: operator_index.py builds the candidate order, indexed_registry.py is the
#: additive #115 index, selection.py is the science-side selection surface.
BOUND_SOURCES = (
    "src/ocm/runtime/solve.py",
    "src/ocm/runtime/operator_index.py",
    "src/ocm/operators/indexed_registry.py",
    "src/ocm/operators/registry.py",
    "src/ocm/science/selection.py",
)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(("git", *args), cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()


def inventory() -> dict:
    return {
        "repository": "SzeChunYiu/ORION-OCM",
        "commit": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "tree_is_clean_for_bound_sources": all(
            not git("status", "--porcelain", "--", rel) for rel in BOUND_SOURCES),
        "bound_sources": {rel: sha256(REPO / rel) for rel in BOUND_SOURCES},
        "note": (
            "Every claim in this study is a claim about these exact files. The study "
            "adds no operator, no policy and no learner to any of them; it only reads "
            "and counts."),
    }
