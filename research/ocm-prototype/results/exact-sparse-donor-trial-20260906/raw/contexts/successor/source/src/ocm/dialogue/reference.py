"""Reference and entity tracking (M4 §3): four-valued resolution, never nearest-string.

    RESOLVED(entity_id)            exactly one candidate survives the registered constraints
    AMBIGUOUS([entity_ids])        several survive; retained as an ambiguity set (never forced)
    NEEDS_CLARIFICATION(plan)      ambiguity matters to the pending task (decided by the clarification
                                   policy, `clarify.py`) — the plan lists the candidates to ask about
    UNKNOWN_REFERENT               nothing in the workspace satisfies the constraints

Candidates come from the workspace's discourse entities filtered by *constraints* that the mention
licenses (kind, features such as number/gender when registered, description match, alias match,
ordinal position, discourse deixis over turns); recency and mention count only *order* an ambiguity
set for the clarification question — they never resolve it (M4 §3, planted mutant
``mutant_nearest_noun``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .workspace import DialogueWorkspace, Entity

PRONOUNS = {"it": {"kind": "entity", "animate": "no"}, "he": {"kind": "entity", "animate": "yes", "gender": "m"}, "she": {"kind": "entity", "animate": "yes", "gender": "f"}, "they": {"kind": "entity"}, "this": {}, "that": {}, "them": {"kind": "entity"}, "him": {"kind": "entity", "gender": "m"}, "her": {"kind": "entity", "gender": "f"}}
ORDINALS = {"first": 0, "second": 1, "third": 2, "fourth": 3, "last": -1}


class ReferenceStatus(str, Enum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    UNKNOWN_REFERENT = "UNKNOWN_REFERENT"


@dataclass(frozen=True)
class Mention:
    surface: str                              # "it", "the robot", "the second one", "that idea", "Mary"
    kind: str | None = None                   # required entity kind, if the construction fixes it
    features: tuple[tuple[str, str], ...] = ()
    turn_id: int | None = None


@dataclass(frozen=True)
class Resolution:
    status: ReferenceStatus
    candidates: tuple[str, ...]               # entity ids, ordered for a clarification question only
    constraints: tuple[str, ...]              # which constraints were applied (for the receipt)
    question_plan: dict[str, Any] | None = None


def _matches(e: Entity, kind: str | None, feats: Mapping[str, str]) -> bool:
    if kind and e.kind != kind:
        return False
    for k, v in feats.items():
        have = e.features.get(k)
        if have is not None and have != v:
            return False
    return True


def candidates_for(ws: DialogueWorkspace, m: Mention) -> tuple[list[Entity], list[str]]:
    """Entities satisfying the mention's constraints; the applied constraint names."""
    surf = m.surface.lower().strip()
    feats = dict(m.features)
    applied: list[str] = []
    pool = list(ws.entities.values())
    if surf in PRONOUNS:
        p = PRONOUNS[surf]
        kind = p.get("kind", m.kind)
        f = {**{k: v for k, v in p.items() if k != "kind"}, **feats}
        applied.append(f"pronoun:{surf}")
        return [e for e in pool if _matches(e, kind, f)], applied
    words = surf.split()
    if words and words[0] in ("the", "this", "that", "these", "those") and len(words) >= 2:
        if words[1] in ORDINALS and len(words) >= 3:            # "the second one/robot"
            idx = ORDINALS[words[1]]
            noun = words[2] if words[2] != "one" else None
            base = [e for e in pool if _matches(e, m.kind, feats) and (noun is None or any(noun in d for d in e.descriptions))]
            base.sort(key=lambda e: e.introduced_turn)
            applied.append(f"ordinal:{words[1]}")
            return ([base[idx]] if -len(base) <= idx < len(base) else []), applied
        desc = " ".join(words[1:])
        applied.append(f"description:{desc}")
        hits = [e for e in pool if _matches(e, m.kind, feats) and any(desc == d or desc == d.split(" ", 1)[-1] or d.endswith(" " + desc) for d in e.descriptions)]
        if not hits:                                              # head-noun match ("the door" vs "the red door")
            head = words[-1]
            hits = [e for e in pool if _matches(e, m.kind, feats) and any(d.split()[-1] == head for d in e.descriptions)]
            applied.append(f"head:{head}")
        return hits, applied
    applied.append(f"alias:{surf}")
    return [e for e in pool if any(a.lower() == surf for a in e.aliases)], applied


def resolve(ws: DialogueWorkspace, m: Mention, *, matters: bool = False) -> Resolution:
    cands, applied = candidates_for(ws, m)
    if not cands:
        return Resolution(ReferenceStatus.UNKNOWN_REFERENT, (), tuple(applied))
    if len(cands) == 1:
        return Resolution(ReferenceStatus.RESOLVED, (cands[0].entity_id,), tuple(applied))
    # ordering for the question only: most recently mentioned first
    ordered = tuple(e.entity_id for e in sorted(cands, key=lambda e: (-max(e.mentions), -len(e.mentions))))
    if matters:
        plan = {"ask": m.surface, "options": [{"entity_id": e.entity_id, "description": (e.descriptions or e.aliases or [e.entity_id])[0]} for e in cands]}
        return Resolution(ReferenceStatus.NEEDS_CLARIFICATION, ordered, tuple(applied), plan)
    return Resolution(ReferenceStatus.AMBIGUOUS, ordered, tuple(applied))


def mutant_nearest_noun(ws: DialogueWorkspace, m: Mention) -> str | None:
    """Planted (M4 §14): resolve any pronoun to the most recently mentioned entity, ignoring constraints."""
    if not ws.entities:
        return None
    return max(ws.entities.values(), key=lambda e: max(e.mentions)).entity_id


def mutant_most_recent_turn_only(ws: DialogueWorkspace, m: Mention, window: int = 1) -> list[str]:
    """Planted (M4 §14): only entities mentioned in the last `window` turns are candidates."""
    cutoff = len(ws.turns) - window
    return [e.entity_id for e in ws.entities.values() if max(e.mentions) > cutoff]
