"""§20 gate and publication-constitution freeze."""
from __future__ import annotations

from typing import Any


REQUIRED = ("principle", "mechanism", "prediction", "evidence", "parent", "closure")


def review_proposed_work(proposal: dict[str, Any]) -> str:
    if all(str(proposal.get(k) or "").strip() and str(proposal.get(k)).lower() not in {"none", "n/a"} for k in REQUIRED):
        return "OK"
    return "DO_NOT_BUILD"
