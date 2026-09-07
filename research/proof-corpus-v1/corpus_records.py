"""Account for every listed lexical row without retaining raw solution bodies."""
import json
import re
from corpus_contract import CorpusError, MATHLIB_COMMIT, TOOLCHAIN
from corpus_syntax import extract_wrapper, extract_solution


def row_kind(path):
    if path.startswith("Theorems/") and path.endswith(".lean"):
        return "wrappers"
    if path.startswith("P2M/Sol/") and path.endswith(".lean"):
        return "solutions"
    return "context"


class Records:
    def __init__(self, entries):
        self.files = {row["path"]: dict(row, state="UNREAD") for row in entries}
        self.wrappers, self.solutions, self.environment = {}, {}, {}
        self.counts = {kind: {"listed": 0, "examined": 0, "accepted": 0,
                              "refused": 0, "unread": 0}
                       for kind in ("wrappers", "solutions", "context")}
        for row in entries:
            counts = self.counts[row_kind(row["path"])]
            counts["listed"] += 1
            counts["unread"] += 1

    def consume(self, row):
        path, body = row["path"], row["body"]
        kind, record = row_kind(path), {k: v for k, v in row.items() if k != "body"}
        counts = self.counts[kind]
        counts["examined"] += 1
        counts["unread"] -= 1
        key = path
        try:
            if kind == "context":
                if path in ("lean-toolchain", "lake-manifest.json"):
                    self.environment[path] = body.decode("utf-8")
            else:
                pattern = r"Theorems/Thm_([A-Za-z0-9_']+)\.lean" if kind == "wrappers" else r"P2M/Sol/S_([A-Za-z0-9_']+)\.lean"
                match = re.fullmatch(pattern, path)
                if not match:
                    raise CorpusError("PAIR_PATH", path)
                key = match[1]
                extractor = extract_wrapper if kind == "wrappers" else extract_solution
                record.update(extractor(body.decode("utf-8"), key))
            record["state"] = "ACCEPTED"
            counts["accepted"] += 1
        except (CorpusError, UnicodeError) as exc:
            record.update(state="REFUSED", failure_code=exc.code if isinstance(exc, CorpusError) else "SOURCE_UTF8")
            counts["refused"] += 1
        self.files[path] = {k: v for k, v in record.items()
                            if k in ("path", "mode", "oid", "sha256", "bytes", "state", "failure_code")}
        if kind != "context":
            table = self.wrappers if kind == "wrappers" else self.solutions
            table[key] = record

    def check_complete(self):
        if any(c["unread"] or c["refused"] for c in self.counts.values()):
            raise CorpusError("LEXICAL_COVERAGE")
        if self.environment.get("lean-toolchain", "").strip() != TOOLCHAIN:
            raise CorpusError("ENVIRONMENT_IDENTITY", "Lean toolchain")
        try:
            manifest = json.loads(self.environment["lake-manifest.json"])
            mathlib = [p for p in manifest["packages"] if p.get("name") == "mathlib"]
            if len(mathlib) != 1 or mathlib[0].get("rev") != MATHLIB_COMMIT:
                raise ValueError("Mathlib")
        except (KeyError, ValueError, TypeError, AttributeError) as exc:
            raise CorpusError("ENVIRONMENT_IDENTITY", "Mathlib revision") from exc
