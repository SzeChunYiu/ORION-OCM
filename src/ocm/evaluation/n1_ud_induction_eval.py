"""N1 step 1 evaluation: induce the lexicon, morphology exceptions and skeleton families from the UD
EWT training split and measure protected coverage on the dev and test splits.  Writes
research/ocm-n1/N1_UD_INDUCTION_V1.json bound to the custody manifest digests.  Descriptive: no
comparator yet (N1 tasks 5–6 add the protected suite and the matched parents).

    python -m ocm.evaluation.n1_ud_induction_eval --data ~/ocm-data/ud-ewt [--out PATH]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from ocm.learning.language import ud as UD

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "ocm-n1" / "N1_UD_INDUCTION_V1.json"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    data = Path(argv[argv.index("--data") + 1]).expanduser() if "--data" in argv else Path("~/ocm-data/ud-ewt").expanduser()
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else OUT
    files = {s: data / f"en_ewt-ud-{s}.conllu" for s in ("train", "dev", "test")}
    for p in files.values():
        if not p.exists():
            print(json.dumps({"status": "CANNOT_CHECK", "reason": f"missing {p}"}))
            return 1
    t0 = time.perf_counter()
    ind = UD.induce(UD.read_conllu(files["train"]))
    from ocm.language import constructions as C
    seed = list(C.seed_constructions())
    interp = {s: UD.interpret_simple_clauses(UD.read_conllu(files[s]), ind, seed) for s in ("dev", "test")}
    rec = {"receipt": "N1_UD_INDUCTION_V1", "dataset": "UD_English-EWT r2.14 (custody manifest docs/provenance/UD_EWT_CUSTODY_MANIFEST_V1.json)", "files_sha256": {s: UD.digest_of(p) for s, p in files.items()},
           "train_induction": ind.receipt(), "coverage": {s: UD.coverage(UD.read_conllu(files[s]), ind) for s in ("dev", "test")},
           "simple_clause_interpretation_seed_constructions": interp,
           "hostile": {"frequency_promotes_threshold_100": UD.mutant_frequency_promotes(ind), "note": "planted: attestation count never changes a warrant; the count of lemmas the hostile would promote is recorded, none is promoted"},
           "wall_s": round(time.perf_counter() - t0, 2), "status": "DESCRIPTIVE (no comparator; protected suite and parents are N1 tasks 5–6)"}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"train": {k: rec["train_induction"][k] for k in ("sentences", "tokens", "lexemes", "singletons", "irregular_past_exceptions", "irregular_present_exceptions", "skeleton_families")}, "coverage": {s: {k: v for k, v in c.items() if k in ("token_coverage", "sentence_lexical_coverage", "skeleton_coverage", "cannot_check")} for s, c in rec["coverage"].items()}, "simple_clauses": {s: {k: v for k, v in c.items() if k != "misses_sample"} for s, c in interp.items()}, "misses_test": interp["test"]["misses_sample"][:6], "wall_s": rec["wall_s"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
