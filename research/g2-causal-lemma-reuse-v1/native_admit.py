"""Native-check extracted cuts against the pinned custodian prefix."""
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "native-method-serving-v1" / "vendor")]
import extract as E  # noqa: E402
import mmverify as N  # noqa: E402

PREFIX = Path("/tmp/orion-native/CUSTODIAN-PREFIX.mm")
SETMM = Path("/tmp/orion-native/set.mm")
RECORDS = HERE / "records" / "admit-01"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_database(raw, begin_label):
    start = time.monotonic()
    log = []
    N.verbosity = 0
    N.logfile = type("L", (), {"write": lambda self, s: log.append(s)})()
    mm = N.MM(begin_label, None)
    error = None
    path = None
    try:
        with tempfile.NamedTemporaryFile("w+", encoding="ascii", delete=False) as handle:
            handle.write(raw.decode("ascii") if isinstance(raw, bytes) else raw)
            handle.flush()
            path = handle.name
        with open(path, encoding="ascii") as stream:
            mm.read(N.Toks(stream))
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    return {
        "terminal": "NATIVE_VERIFIED" if error is None else "NATIVE_REJECTED",
        "error": error,
        "wall_s": time.monotonic() - start,
        "log_tail": "".join(log)[-2000:],
        "database_path": path,
    }


def admit_all():
    prefix = PREFIX.read_bytes()
    lemmas = E.unique_negatives()
    RECORDS.mkdir(parents=True, exist_ok=True)
    rows = []
    native_calls = 0
    for i, lemma in enumerate(lemmas):
        label = "cut-lemma-" + str(i).zfill(2)
        suffix = E.emit_suffix(lemma, label)
        raw = prefix + b"\n" + suffix.encode("ascii")
        result = verify_database(raw, label)
        native_calls += 1
        rows.append({
            "label": label,
            "source_label": lemma["source_label"],
            "canonical_id": lemma["canonical_id"],
            "n_hypotheses": len(lemma["hypotheses"]),
            "n_proof": len(lemma["proof"]),
            "zero_premise": not lemma["hypotheses"],
            "target": lemma["target"],
            **result,
        })
        print(i, lemma["source_label"], "hyps", len(lemma["hypotheses"]), result["terminal"],
              (result["error"] or {}).get("message", "")[:160], flush=True)
    out = {
        "schema": "g2.causal-lemma-reuse.admit.v1",
        "prefix_sha256": sha256(PREFIX),
        "prefix_bytes": PREFIX.stat().st_size,
        "n_unique_negatives": len(lemmas),
        "n_zero_premise": sum(1 for r in rows if r["zero_premise"]),
        "n_verified": sum(1 for r in rows if r["terminal"] == "NATIVE_VERIFIED"),
        "n_rejected": sum(1 for r in rows if r["terminal"] == "NATIVE_REJECTED"),
        "native_calls": native_calls,
        "rows": rows,
    }
    (RECORDS / "ADMIT.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    admit_all()
