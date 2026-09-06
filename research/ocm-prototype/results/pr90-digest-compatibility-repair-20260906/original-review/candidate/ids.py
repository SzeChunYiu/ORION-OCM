"""Identity scheme — one evidence/object id convention for the whole canonical package.

Resolves the three incompatible inherited schemes (small ints in ``kso_math_v1``; 60-bit SHA-256
ids in ``kso_multidomain_v1``; free strings in the M0 runtime) into one: a content-bound global id
``ev:<namespace>:<sha256[:16]>`` with a registry that detects collisions (same id, different
payload) and duplicates (same payload, different provenance) explicitly.

Legacy fixtures that use small integers keep working because the algebra is generic over hashable
ids; ``legacy_evidence_id`` gives them a canonical string form when one is needed.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Hashable


class IdentityCollision(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def evidence_id(namespace: str, payload: Any, *, width: int = 16) -> str:
    if not namespace or ":" in namespace:
        raise ValueError("namespace must be non-empty and contain no ':'")
    digest = hashlib.sha256(f"{namespace}\x1f{canonical_json(payload)}".encode("utf-8")).hexdigest()
    return f"ev:{namespace}:{digest[:width]}"


def legacy_evidence_id(value: Hashable) -> str:
    """Canonical string for a legacy small-integer or string evidence id."""
    if isinstance(value, str) and value.startswith("ev:"):
        return value
    return f"ev:legacy:{value!r}"


def object_id(kind: str, payload: Any, *, width: int = 16) -> str:
    return f"{kind}:{content_hash(payload)[:width]}"


@dataclass(slots=True)
class EvidenceRegistry:
    """Registers evidence ids against their payload digest; collisions are errors, not merges."""

    namespace: str
    _digest_by_id: dict[str, str] = field(default_factory=dict)
    _id_by_digest: dict[str, str] = field(default_factory=dict)

    def register(self, payload: Any) -> str:
        digest = content_hash(payload)
        eid = evidence_id(self.namespace, payload)
        existing = self._digest_by_id.get(eid)
        if existing is not None and existing != digest:
            raise IdentityCollision(f"evidence id {eid} already bound to a different payload")
        self._digest_by_id[eid] = digest
        self._id_by_digest.setdefault(digest, eid)
        return eid

    def is_duplicate(self, payload: Any) -> bool:
        return content_hash(payload) in self._id_by_digest

    def __len__(self) -> int:
        return len(self._digest_by_id)
