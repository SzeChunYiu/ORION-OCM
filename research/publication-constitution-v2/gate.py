"""§20 gate and publication-constitution v2 freeze."""
from __future__ import annotations

from typing import Any


REQUIRED = ("principle", "mechanism", "prediction", "evidence", "parent", "closure")
PUBLICATION_GAPS = ("independent_authorship", "fresh_host")
BLANK = frozenset({"", "none", "n/a"})


def _blank(value: Any) -> bool:
    return str(value or "").strip().lower() in BLANK


def review_proposed_work(proposal: dict[str, Any]) -> str:
    if all(not _blank(proposal.get(key)) for key in REQUIRED):
        return "OK"
    return "DO_NOT_BUILD"


def review_publication_close(answers: dict[str, Any]) -> str:
    """Confirmatory / #144 close. Missing independent authorship or fresh host is DO_NOT_BUILD."""
    if review_proposed_work(answers) != "OK":
        return "DO_NOT_BUILD"
    if any(_blank(answers.get(key)) for key in PUBLICATION_GAPS):
        return "DO_NOT_BUILD"
    if any(
        str(answers.get(key) or "").startswith("CANNOT_CHECK")
        or str(answers.get(key) or "").startswith("MISSING")
        for key in PUBLICATION_GAPS
    ):
        return "DO_NOT_BUILD"
    return "OK"
