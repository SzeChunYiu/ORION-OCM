"""Frozen identities, terminals, and receipt helpers for the FLT-KSO v1 research tranche."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

ANTHROPIC_REPOSITORY = "anthropics/fermats-last-theorem"
ANTHROPIC_COMMIT = "aa2d8b34692b16c70f699536de0d8e75b9a3e9ef"
ANTHROPIC_TREE = "8bb1c43c8f26f1c127591dddeffdead2b5094eb7"
LEAN_TOOLCHAIN = "leanprover/lean4:v4.33.1"
LEAN_VERSION = "4.33.1"
MATHLIB_TAG = "v4.33.0"
MATHLIB_COMMIT = "db584cd6d46c92f209a44c0f1c829460d327499d"
SOURCE_BASE = "787a5d2c1611cdf9acbb87cb44fa1b878c8a4d1f"
R1_CHALLENGE_ID = "R1_PROP_CHAIN_001"
R1_STATEMENT = "(P → Q) → (Q → R) → P → R"
R1_MAX_EXPANSIONS = 64
R1_MAX_CHECKER_CALLS = 16


class AttemptStatus(str, Enum):
    OPEN = "OPEN"
    PROPOSED = "PROPOSED"
    CHECKING = "CHECKING"
    PROVED = "PROVED"
    REFUTED = "REFUTED"
    FAILED_UNDER_BUDGET = "FAILED_UNDER_BUDGET"
    UNKNOWN = "UNKNOWN"
    CANNOT_CHECK = "CANNOT_CHECK"


class Terminal(str, Enum):
    KNOWN_PROOF_REPLAY_ONLY = "KNOWN_PROOF_REPLAY_ONLY"
    F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED = "F0_MASKED_COMPOSITION_APPARATUS_SUPPORTED"
    UNSEEN_COMPOSITION_SUPPORTED = "UNSEEN_COMPOSITION_SUPPORTED"
    MECHANICAL_HIDDEN_PROOF_RECONSTRUCTION_SUPPORTED = "MECHANICAL_HIDDEN_PROOF_RECONSTRUCTION_SUPPORTED"
    MECHANICAL_DEPENDENCY_DISCOVERY_SUPPORTED = "MECHANICAL_DEPENDENCY_DISCOVERY_SUPPORTED"
    CAUSAL_PROOF_METHOD_REUSE_SUPPORTED = "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED"
    PARENT_SUFFICIENT = "PARENT_SUFFICIENT"
    FAILED_UNDER_BUDGET = "FAILED_UNDER_BUDGET"
    SOLUTION_LEAKAGE_DETECTED = "SOLUTION_LEAKAGE_DETECTED"
    CHECKER_OR_ENVIRONMENT_MISMATCH = "CHECKER_OR_ENVIRONMENT_MISMATCH"
    CANNOT_CHECK_PINNED_FLT_ENVIRONMENT = "CANNOT_CHECK_PINNED_FLT_ENVIRONMENT"
    CANNOT_CHECK_PRIVATE_OPEN_GUARD = "CANNOT_CHECK_PRIVATE_OPEN_GUARD"
    CANNOT_CHECK_F0_CUSTODY_TRACE = "CANNOT_CHECK_F0_CUSTODY_TRACE"
    CANNOT_CHECK_SIGNATURE_EXTRACTION_COVERAGE = "CANNOT_CHECK_SIGNATURE_EXTRACTION_COVERAGE"
    CANNOT_CHECK_KERNEL = "CANNOT_CHECK_KERNEL"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True, slots=True)
class EnvironmentIdentity:
    anthropic_repository: str = ANTHROPIC_REPOSITORY
    anthropic_commit: str = ANTHROPIC_COMMIT
    anthropic_tree: str = ANTHROPIC_TREE
    lean_toolchain: str = LEAN_TOOLCHAIN
    lean_version: str = LEAN_VERSION
    mathlib_tag: str = MATHLIB_TAG
    mathlib_commit: str = MATHLIB_COMMIT

    @property
    def digest(self) -> str:
        return sha256_text(canonical_json(asdict(self)))


def statement_identity(statement: str, environment: EnvironmentIdentity) -> str:
    # Deliberately includes environment identity: name/surface similarity is never semantic identity.
    return sha256_text(canonical_json({"statement": statement.strip(), "environment": environment.digest}))


def tree_manifest(root: Path, *, exclude: Iterable[str] = ()) -> dict[str, str]:
    excluded = set(exclude)
    out: dict[str, str] = {}
    for p in sorted(x for x in root.rglob("*") if x.is_file() and not x.is_symlink()):
        rel = p.relative_to(root).as_posix()
        if rel in excluded:
            continue
        out[rel] = sha256_file(p)
    return out


def manifest_digest(root: Path, *, exclude: Iterable[str] = ()) -> str:
    return sha256_text(canonical_json(tree_manifest(root, exclude=exclude)))


def base_receipt(*, source_sha: str, arm: str, challenge_id: str) -> dict[str, Any]:
    return {
        "schema": "flt-kso-v1.receipt.v1",
        "source_sha": source_sha,
        "source_base": SOURCE_BASE,
        "arm": arm,
        "challenge_id": challenge_id,
        "environment": asdict(EnvironmentIdentity()),
        "environment_digest": EnvironmentIdentity().digest,
        "llm_calls": 0,
        "llm_tokens": 0,
        "foundation_model_calls": 0,
        "parametric_model_in_mechanism": False,
    }
