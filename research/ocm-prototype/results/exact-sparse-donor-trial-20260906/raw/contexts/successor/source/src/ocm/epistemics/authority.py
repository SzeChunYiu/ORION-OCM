from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class AuthorityViolation(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AuthorityAnchor:
    path: str
    required_literals: tuple[str, ...]
    forbidden_promotions: tuple[str, ...] = ()


ANCHORS = (
    AuthorityAnchor("research/orion-machine/results/KSO_M2_SOLVE_OUTCOME_V1.md", ("PARENT_SUFFICIENT",), ("KSO_SUPERIOR", "GENERAL_SUPERIORITY_ESTABLISHED")),
    AuthorityAnchor("research/orion-machine/reference/kso_m6_formal_math_v1.py", ("M6A_FORMAL_MATH_VERIFIER_CHANNEL_INTEGRATED_PARENT_SUFFICIENT", "PARENT_SUFFICIENT"), ("FRONTIER_MATH_SOLVED", "GENERAL_SUPERIORITY_ESTABLISHED")),
    AuthorityAnchor("research/orion-machine/reference/kso_m5_chat_v1.py", ("M5_CONTROLLED_CODEC_CHAT_GREEN", '"open_domain_chat": False'), ("OPEN_DOMAIN_CHAT_GREEN",)),
    AuthorityAnchor("research/orion-machine/reference/kso_language_v0.py", ("LANGUAGE_KSO_L0_CONTROLLED_GREEN", '"open_domain_language": False'), ("LANGUAGE_KSO_ALPHA",)),
)


def guard_text(anchor: AuthorityAnchor, text: str) -> None:
    missing = [literal for literal in anchor.required_literals if literal not in text]
    promotions = [literal for literal in anchor.forbidden_promotions if literal in text]
    if missing or promotions:
        raise AuthorityViolation(json.dumps({"path": anchor.path, "missing": missing, "forbidden_promotions": promotions}, sort_keys=True))


def verify_authority(root: Path) -> dict[str, object]:
    checked = []
    for anchor in ANCHORS:
        path = root / anchor.path
        if not path.exists(): raise AuthorityViolation(f"authority anchor missing: {anchor.path}")
        guard_text(anchor, path.read_text(encoding="utf-8")); checked.append(anchor.path)
    return {"terminal": "AUTHORITY_PRESERVATION_GREEN", "anchors_checked": checked, "general_novelty": "NOT_ESTABLISHED", "m2_parent_tie": "PARENT_SUFFICIENT", "m6a_parent_tie": "PARENT_SUFFICIENT"}
