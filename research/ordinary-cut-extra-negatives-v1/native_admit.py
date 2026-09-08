"""Native-check extra SCREENED_NEGATIVE cuts against the pinned custodian prefix."""
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
    inventory, lemmas = E.extra_lemmas()
    p1 = E.load_p1()
    bodies = E.bodies_by_id()
    RECORDS.mkdir(parents=True, exist_ok=True)
    rows = []
    native_calls = 0
    for i, lemma in enumerate(lemmas):
        label = "extra-cut-" + str(i).zfill(2)
        suffix = E.emit_suffix(lemma, label)
        raw = prefix + b"\n" + suffix.encode("ascii")
        result = verify_database(raw, label)
        native_calls += 1
        emit_check = {"proof_equals_typed_emit": None, "target_equals_typed_emit": None,
                      "semantic_applications_expanded": None, "typed_emit_error": None}
        try:
            emit_check = {**E.reemit_check(lemma, bodies, p1), "typed_emit_error": None}
        except Exception as exc:
            emit_check["typed_emit_error"] = {"type": type(exc).__name__, "message": str(exc)}
        named = E.named_p1_match(lemma, p1)
        rows.append({
            "label": label,
            "source_label": lemma["source_label"],
            "ordinal": lemma["ordinal"],
            "canonical_id": lemma["canonical_id"],
            "n_hypotheses": len(lemma["hypotheses"]),
            "n_proof": len(lemma["proof"]),
            "zero_premise": not lemma["hypotheses"],
            "target": lemma["target"],
            "semantic_labels": lemma["semantic_labels"],
            "semantic_applications": lemma["semantic_applications"],
            "abstraction": lemma["abstraction"],
            "two_step_p1_composition": lemma["semantic_applications"] == 2,
            "named_p1_statement_matches": named,
            "deeper_named_alias": bool(named),
            **emit_check,
            **result,
        })
        print(i, lemma["source_label"], "hyps", len(lemma["hypotheses"]),
              lemma["abstraction"], "sem", lemma["semantic_applications"],
              result["terminal"], (result["error"] or {}).get("message", "")[:160],
              flush=True)
    out = {
        "schema": "ordinary.cut-extra-negatives.admit.v1",
        "prefix_sha256": sha256(PREFIX),
        "prefix_bytes": PREFIX.stat().st_size,
        "replay01_occurrences": inventory["replay01_occurrences"],
        "replay01_unique": inventory["replay01_unique"],
        "replay02_occurrences": inventory["replay02_occurrences"],
        "replay02_unique": inventory["replay02_unique"],
        "n_extra_unique": len(lemmas),
        "n_zero_premise": sum(1 for r in rows if r["zero_premise"]),
        "n_verified": sum(1 for r in rows if r["terminal"] == "NATIVE_VERIFIED"),
        "n_rejected": sum(1 for r in rows if r["terminal"] == "NATIVE_REJECTED"),
        "n_two_step": sum(1 for r in rows if r["two_step_p1_composition"]),
        "n_deeper_named_alias": sum(1 for r in rows if r["deeper_named_alias"]),
        "abstraction_counts": {},
        "native_calls": native_calls,
        "all_proofs_equal_typed_emit": all(r.get("proof_equals_typed_emit") for r in rows),
        "rows": rows,
    }
    for row in rows:
        kind = row["abstraction"]
        out["abstraction_counts"][kind] = out["abstraction_counts"].get(kind, 0) + 1
    (RECORDS / "ADMIT.json").write_text(json.dumps(out, indent=2) + "\n")
    (RECORDS / "DIFF.json").write_text(json.dumps({
        "schema": "ordinary.cut-extra-negatives.diff.v1",
        "replay01_occurrences": inventory["replay01_occurrences"],
        "replay01_unique": inventory["replay01_unique"],
        "replay02_occurrences": inventory["replay02_occurrences"],
        "replay02_unique": inventory["replay02_unique"],
        "extra_canonical_ids": [row["canonical_id"] for row in lemmas],
        "extra_source_labels": [row["source_label"] for row in lemmas],
        "admitted_replay01_ids": inventory["admitted_ids"],
    }, indent=2) + "\n")
    return out


if __name__ == "__main__":
    admit_all()
