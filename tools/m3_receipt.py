#!/usr/bin/env python3
"""Verify the active runtime successor; preserve historical M3_RECEIPT_V1.json.
    python tools/m3_receipt.py --write-current  # create declared successor; never overwrite history
    python tools/m3_receipt.py --verify         # verify active successor; no historical fallback
Binds: the M3 language modules, the language obligation registry, the microworld evaluation
receipt and the dataset custody manifests (UD EWT, BLiMP); records the deterministic checker
outputs (canonical-form exhaustive check, WL collision witness, the nine required meanings'
digests, the microworld protected-split numbers) and the inherited authority.  No claim.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs" / "provenance" / "M3_RECEIPT_V1.json"
BOUND = (
    "src/ocm/language/meaning.py", "src/ocm/language/lexicon.py", "src/ocm/language/constructions.py",
    "src/ocm/language/interpret.py", "src/ocm/language/acquisition.py", "src/ocm/language/microworld.py",
    "src/ocm/language/session.py", "src/ocm/evaluation/m3_microworld_eval.py",
    "docs/theorems/OCM_LANGUAGE_OBLIGATION_REGISTRY_V1.json",
    "docs/provenance/UD_EWT_CUSTODY_MANIFEST_V1.json", "docs/provenance/BLIMP_CUSTODY_MANIFEST_V1.json",
    "research/ocm-m3/M3_MICROWORLD_EVAL_V1.json",
    "scripts/acquire_ud_ewt.sh", "scripts/acquire_blimp.sh",
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fresh() -> dict:
    from ocm.language import meaning as M
    from ocm.language import microworld as W

    ex = M.example_meanings()
    digests = {k: M.canonical(v)[1] for k, v in ex.items()}
    g1, g2 = M.wl_collision_witness()
    wl = {"wl1_hash_equal": M.wl1_hash(g1) == M.wl1_hash(g2), "canonical_equal": M.canonical(g1)[1] == M.canonical(g2)[1], "isomorphic": M.isomorphic(g1, g2)}
    corpus = W.generate()
    custody = W.custody_receipt(corpus, "OCM-M3-MICROWORLD-20260905")
    eval_receipt = json.loads((ROOT / "research/ocm-m3/M3_MICROWORLD_EVAL_V1.json").read_text(encoding="utf-8"))
    result = {
        "required_meanings": digests,
        "passive_equals_active_minus_modifier": M.canonical(M.MeaningGraph(tuple(n for n in ex["the robot opened the red door"].nodes if n.node_type != "property"), tuple(e for e in ex["the robot opened the red door"].edges if e.relation != "MODIFIES"), ex["the robot opened the red door"].root))[1] == digests["the door was opened by the robot"],
        "wl_collision_witness": wl,
        "microworld_custody": {k: custody[k] for k in ("n", "dev", "protected", "dev_sha256", "protected_sha256", "held_out_lexemes_absent_from_dev")},
        "microworld_eval": {"acquisition": eval_receipt["acquisition"], "protected": {k: v for k, v in eval_receipt["protected"].items()}, "ambiguity": eval_receipt["ambiguity"], "paraphrase": eval_receipt["paraphrase"], "revocation_locality": eval_receipt["revocation_locality"]},
    }
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    return {
        "receipt": "M3_RECEIPT_V1",
        "terminal": "M3_LANGUAGE_UNDERSTANDING_GREEN",
        "git_head_at_generation": head,
        "bound_files": {rel: sha(ROOT / rel) for rel in BOUND},
        "deterministic_results": result,
        "authority": "engineering receipt for the M3 language milestone on a synthetic microworld with a given vocabulary; real-language custody manifests are bound but no real-language result is claimed; no comparator, no novelty claim; the theory these modules implement is ORION-V2 batch 2 (B1, B2, B3, B4)",
    }


def main(argv: list[str]) -> int:
    from runtime_revision_receipts_v4 import revision_main

    return revision_main(ROOT, argv, 3)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
