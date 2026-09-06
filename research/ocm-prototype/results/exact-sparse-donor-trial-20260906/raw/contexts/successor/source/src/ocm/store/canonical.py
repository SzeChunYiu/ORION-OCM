"""Canonical bytes and versioned, Unicode-pinned digests for the OCM store.

Two functions, two jobs:

``canonical_bytes(payload)``
    Behaviourally identical to ORION ``orion.kernel.store.canonical_bytes``:
    ``json.dumps(payload, sort_keys=True, separators=(",", ":"))`` encoded as
    UTF-8 (``ensure_ascii`` left at its default). It is the encoding the ledger
    hash chain and the vendored hard-gate fingerprint are computed over, so it
    must never change.

``canonical_digest(value, *, domain)``
    A domain-separated SHA-256 commitment over a *typed* canonical tree,
    modelled on ORION ``orion/kernel/transition.py`` (``_typed_value`` /
    ``canonical_json_bytes`` / ``canonical_digest``) without copying any ORION
    mechanics type. Two disciplines are pinned into every digest:

    * a versioned canonicalization (``CANONICALIZATION_VERSION``) so a change
      to the encoding is a change of identity, never a silent re-hash; and
    * a Unicode policy: every string (values and mapping keys) is NFC-normalised
      before encoding, and the Unicode Character Database version the running
      interpreter used to do that (``unicodedata.unidata_version``) is folded
      into the digest envelope. Two logically identical states differing only
      in Unicode composition therefore hash identically (M2 §4), and a Python
      upgrade that changes normalisation cannot silently change a state hash:
      it changes the recorded ``UNICODE_DATABASE_VERSION`` instead.

Integers are encoded as sign + magnitude octets (no float coercion), floats as
their IEEE-754 big-endian bit pattern (non-finite refused), ``bool`` is kept
distinct from ``int``, ``tuple`` from ``list``, mapping keys must be ``str`` and
are ordered by the UTF-8 bytes of their NFC form. Depth, node and byte budgets
bound the work a hostile value can demand.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import unicodedata
from typing import Any

CANONICALIZATION_VERSION = "ocm.typed-canonical.v1"
UNICODE_POLICY = "ocm.unicode.nfc-normalize.v1"
UNICODE_DATABASE_VERSION = unicodedata.unidata_version
MAX_CANONICAL_BYTES = 8_388_608
MAX_CANONICAL_DEPTH = 128
MAX_CANONICAL_NODES = 100_000

_CANONICAL_PREFIX = b"OCM-CANONICAL-DIGEST\x00"


class CanonicalizationError(ValueError):
    """Raised when a value has no unambiguous OCM canonical representation."""


def canonical_bytes(payload: Any) -> bytes:
    """Encode a payload as canonical JSON so digests are reproducible.

    Byte-identical semantics to ORION ``kernel/store.py::canonical_bytes``.
    """

    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def normalize_text(value: str) -> str:
    """Apply the pinned Unicode policy to one string: NFC, no lone surrogates."""

    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise CanonicalizationError("canonical text cannot contain lone surrogates") from error
    return unicodedata.normalize("NFC", value)


def _typed_value(value: Any, *, active: set[int], depth: int, nodes: list[int]) -> Any:
    """Map exact built-in values to a typed, deterministic JSON tree."""

    if depth > MAX_CANONICAL_DEPTH:
        raise CanonicalizationError("canonical value exceeds the maximum depth")
    nodes[0] += 1
    if nodes[0] > MAX_CANONICAL_NODES:
        raise CanonicalizationError("canonical value exceeds the maximum node count")
    if value is None:
        return ["null"]
    if type(value) is bool:
        return ["bool", value]
    if type(value) is int:
        magnitude = abs(value)
        octets = magnitude.to_bytes(max(1, (magnitude.bit_length() + 7) // 8), "big")
        return ["int-sign-magnitude", [int(value < 0), octets.hex()]]
    if type(value) is str:
        return ["str", normalize_text(value)]
    if type(value) is float:
        if not math.isfinite(value):
            raise CanonicalizationError("non-finite floats have no canonical form")
        return ["float64-bits", struct.pack(">d", value).hex()]

    if type(value) not in {dict, list, tuple}:
        raise CanonicalizationError(
            f"unsupported canonical type: {value.__class__.__module__}."
            f"{value.__class__.__qualname__}"
        )

    object_id = id(value)
    if object_id in active:
        raise CanonicalizationError("cyclic values have no canonical form")
    active.add(object_id)
    try:
        if type(value) is dict:
            entries: list[list[Any]] = []
            seen: set[str] = set()
            for key, item in value.items():
                if type(key) is not str:
                    raise CanonicalizationError("canonical mappings require string keys")
                normalized_key = normalize_text(key)
                if normalized_key in seen:
                    raise CanonicalizationError(
                        "canonical mapping keys collide after Unicode normalization"
                    )
                seen.add(normalized_key)
                entries.append(
                    [
                        ["str", normalized_key],
                        _typed_value(item, active=active, depth=depth + 1, nodes=nodes),
                    ]
                )
            entries.sort(key=lambda entry: entry[0][1].encode("utf-8"))
            return ["map", entries]
        tag = "list" if type(value) is list else "tuple"
        return [
            tag,
            [_typed_value(item, active=active, depth=depth + 1, nodes=nodes) for item in value],
        ]
    finally:
        active.remove(object_id)


def canonical_json_bytes(value: Any) -> bytes:
    """Encode OCM's versioned typed tree; this is not ordinary JSON identity."""

    envelope = [
        "ocm-typed-canonical",
        CANONICALIZATION_VERSION,
        UNICODE_POLICY,
        UNICODE_DATABASE_VERSION,
        _typed_value(value, active=set(), depth=0, nodes=[0]),
    ]
    try:
        encoded = json.dumps(
            envelope,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError, RecursionError) as error:
        raise CanonicalizationError("value cannot be encoded canonically") from error
    if len(encoded) > MAX_CANONICAL_BYTES:
        raise CanonicalizationError("canonical value exceeds the maximum byte count")
    return encoded


def canonical_digest(value: Any, *, domain: str) -> str:
    """Return a versioned, domain-separated SHA-256 commitment.

    ``domain`` names what the digest is a commitment *to* (for example
    ``"ocm.registry-state.v1"``); its length-prefixed bytes precede the
    canonical envelope so equal payloads under different domains never collide.
    """

    if type(domain) is not str or not domain or domain != domain.strip():
        raise CanonicalizationError("domain must be nonblank exact text")
    domain_bytes = normalize_text(domain).encode("utf-8")
    encoded = (
        _CANONICAL_PREFIX
        + len(domain_bytes).to_bytes(4, "big")
        + domain_bytes
        + canonical_json_bytes(value)
    )
    return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "CANONICALIZATION_VERSION",
    "CanonicalizationError",
    "MAX_CANONICAL_BYTES",
    "MAX_CANONICAL_DEPTH",
    "MAX_CANONICAL_NODES",
    "UNICODE_DATABASE_VERSION",
    "UNICODE_POLICY",
    "canonical_bytes",
    "canonical_digest",
    "canonical_json_bytes",
    "normalize_text",
]
