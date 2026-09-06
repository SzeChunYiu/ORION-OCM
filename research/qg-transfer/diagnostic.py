"""Reproducible developer diagnostic, not a protected performance result."""
from __future__ import annotations
import json
import platform
import time
from finite_views import compile_view, verify_view

NAMES = ("operator_family", "scope", "current_status")
PATTERNS = tuple((f"reusable-method-{i}", f"context-{i % 4}", "LIVE") for i in range(16))


def stream(n):
    return (PATTERNS[i % len(PATTERNS)] for i in range(n))


def run(n):
    start = time.perf_counter()
    view = compile_view(stream(n), NAMES, NAMES)
    built = time.perf_counter() - start
    start = time.perf_counter()
    verified = verify_view(stream(n), NAMES, view)
    checked = time.perf_counter() - start
    assert verified
    encoded = view.to_bytes()
    assert len(encoded) == view.encoded_payload_bytes
    # Comparable concrete UTF-8 JSON-lines source, including names header.
    row_sizes = [len(json.dumps(r, separators=(",", ":")).encode()) + 1 for r in PATTERNS]
    raw_bytes = len(json.dumps(NAMES, separators=(",", ":")).encode()) + 1
    raw_bytes += (n // 16) * sum(row_sizes) + sum(row_sizes[:n % 16])
    start = time.perf_counter()
    checksum = sum(len(view.answer(i % n, "operator_family", current_source_digest=view.source_digest)) for i in range(10000))
    queried = time.perf_counter() - start
    return {
        "rows": n, "dictionary_entries": len(view.signatures),
        "membership_bytes": len(view.codes), "view_payload_bytes": len(encoded),
        "source_jsonl_bytes": raw_bytes, "source_plus_view_bytes": raw_bytes + len(encoded),
        "payload_only_ratio": raw_bytes / len(encoded),
        "compile_seconds": built, "verification_seconds": checked,
        "queries": 10000, "query_seconds": queried, "query_checksum": checksum,
        "compile_source_rows": n, "verification_source_rows": n,
        "temporary_code_array_bytes": 8 * n,
        "scope": "developer synthetic repetition; source retained; not end-to-end storage reduction",
    }


if __name__ == "__main__":
    print(json.dumps({
        "terminal": "PARENT_SUFFICIENT_DICTIONARY_ENCODING_DEVELOPMENT_ONLY",
        "python": platform.python_version(), "platform": platform.platform(),
        "trained_parameters": 0, "quantum_operations": 0,
        "comparison": "same retained observations; packed dictionary vs repeated JSONL, not OCM vs LLM",
        "results": [run(n) for n in (1000, 10000, 100000, 1000000)],
    }, indent=2))
