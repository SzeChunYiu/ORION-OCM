"""Tests for ``ocm.store.canonical`` (new module, modelled on ORION kernel/transition.py).

Pins: ``canonical_bytes`` is byte-identical to ORION store.canonical_bytes;
``canonical_digest`` is NFC-invariant, domain-separated, type-distinguishing and
version-pinned to the running Unicode database.
"""

from __future__ import annotations

import json
import unicodedata

import pytest

from ocm.store import canonical as C


def test_canonical_bytes_matches_orion_store_semantics():
    payload = {"b": [1, 2.5, None, True], "a": {"ü": "é"}}
    assert C.canonical_bytes(payload) == json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    assert C.canonical_bytes(payload) == C.canonical_bytes({"a": {"ü": "é"}, "b": [1, 2.5, None, True]})


def test_digest_is_nfc_invariant_for_values_and_keys():
    composed = "\u00e9"          # U+00E9
    decomposed = "e\u0301"      # U+0065 U+0301
    assert unicodedata.normalize("NFC", decomposed) == composed
    assert composed != decomposed
    assert C.canonical_digest({"k": composed}, domain="d") == C.canonical_digest(
        {"k": decomposed}, domain="d"
    )
    assert C.canonical_digest({composed: 1}, domain="d") == C.canonical_digest(
        {decomposed: 1}, domain="d"
    )
    # The plain ledger encoding deliberately does NOT normalise: it is the M0 byte contract.
    assert C.canonical_bytes(composed) != C.canonical_bytes(decomposed)


def test_keys_that_collide_after_normalization_are_refused():
    with pytest.raises(C.CanonicalizationError):
        C.canonical_digest({"\u00e9": 1, "e\u0301": 2}, domain="d")


def test_digest_is_domain_separated_and_domain_is_validated():
    value = {"x": 1}
    assert C.canonical_digest(value, domain="a") != C.canonical_digest(value, domain="b")
    for bad in ("", " a", "a "):
        with pytest.raises(C.CanonicalizationError):
            C.canonical_digest(value, domain=bad)


def test_digest_distinguishes_types_that_plain_json_conflates():
    assert C.canonical_digest(1, domain="d") != C.canonical_digest(1.0, domain="d")
    assert C.canonical_digest(True, domain="d") != C.canonical_digest(1, domain="d")
    assert C.canonical_digest([1], domain="d") != C.canonical_digest((1,), domain="d")
    assert C.canonical_digest(0, domain="d") != C.canonical_digest(-0.0, domain="d")
    assert C.canonical_digest(-1, domain="d") != C.canonical_digest(1, domain="d")


def test_envelope_pins_versions_and_unicode_database():
    encoded = json.loads(C.canonical_json_bytes({"k": "v"}))
    assert encoded[:4] == [
        "ocm-typed-canonical",
        C.CANONICALIZATION_VERSION,
        C.UNICODE_POLICY,
        unicodedata.unidata_version,
    ]
    assert C.UNICODE_DATABASE_VERSION == unicodedata.unidata_version


def test_hostile_values_fail_closed():
    with pytest.raises(C.CanonicalizationError):
        C.canonical_digest(float("nan"), domain="d")
    with pytest.raises(C.CanonicalizationError):
        C.canonical_digest({1: "non-string key"}, domain="d")
    with pytest.raises(C.CanonicalizationError):
        C.canonical_digest(object(), domain="d")
    cyclic: list = []
    cyclic.append(cyclic)
    with pytest.raises(C.CanonicalizationError):
        C.canonical_digest(cyclic, domain="d")
    deep: list = []
    node = deep
    for _ in range(C.MAX_CANONICAL_DEPTH + 2):
        node.append([])
        node = node[0]
    with pytest.raises(C.CanonicalizationError):
        C.canonical_digest(deep, domain="d")
    with pytest.raises(C.CanonicalizationError):
        C.canonical_digest("\ud800", domain="d")


def test_digest_is_deterministic_across_key_order_and_is_sha256_hex():
    left = C.canonical_digest({"a": 1, "b": [2, {"c": 3}]}, domain="d")
    right = C.canonical_digest({"b": [2, {"c": 3}], "a": 1}, domain="d")
    assert left == right
    assert len(left) == 64 and set(left) <= set("0123456789abcdef")
