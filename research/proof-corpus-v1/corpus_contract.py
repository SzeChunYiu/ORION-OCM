"""Inventory data contract. No theorem truth, study selection or solver authority."""
import hashlib
import json
import re

SOURCE_COMMIT = "aa2d8b34692b16c70f699536de0d8e75b9a3e9ef"
MATHLIB_COMMIT = "db584cd6d46c92f209a44c0f1c829460d327499d"
TOOLCHAIN = "leanprover/lean4:v4.33.1"
EXPECTED_PAIRS = 29511
ROOTS = ("Theorems", "P2M", "Definitions", "FinalCheck.lean",
         "lean-toolchain", "lake-manifest.json", "lakefile.lean", "lakefile.toml")


class CorpusError(ValueError):
    def __init__(self, code, detail=""):
        self.code = code
        super().__init__(code + (": " + detail if detail else ""))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value):
    return sha256(encoded(value))


def key_identity(key):
    if type(key) is not str or not re.fullmatch(r"[A-Za-z0-9_']+", key):
        raise CorpusError("MODULE_IDENTITY")
    return key


def commit_identity(commit):
    if type(commit) is not str or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise CorpusError("COMMIT_IDENTITY")
    return commit
