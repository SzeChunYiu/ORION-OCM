"""Aggregate N1 UD train/dev calibration runner for an authorized compute host.

This runner never downloads data and never emits sentence/token annotations.  It
binds local files to the r2.14 custody manifest and reports only aggregate
learning/coverage/resource statistics.  The protected EWT test split remains
unavailable here: a future frozen protected evaluator is a distinct artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
import tracemalloc

from ud_induction import induce_lexicon, load_split, past_morphology, split_summary
from ud_grammar import coverage, induce_grammar


def evaluate(train_sentences, eval_sentences, *, min_attestations: int = 1, max_chart_nodes: int = 2_000_000) -> dict:
    tracemalloc.start()
    start = time.perf_counter()
    lexicon = induce_lexicon(train_sentences)
    morphology = past_morphology(train_sentences)
    grammar = induce_grammar(train_sentences, min_attestations=min_attestations)
    cov = coverage(
        train_sentences,
        eval_sentences,
        min_attestations=min_attestations,
        max_chart_nodes=max_chart_nodes,
    )
    wall = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "receipt": "N1_UD_DEV_CALIBRATION_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "train": split_summary(train_sentences),
        "grammar": {
            "rules": len(grammar.rules),
            "families": grammar.families,
            "order_hypotheses": grammar.order_hypotheses,
            "projective_sentences": grammar.projective_sentences,
            "nonprojective_sentences": grammar.nonprojective_sentences,
            "min_attestations": min_attestations,
        },
        "morphology": {
            "past_pairs": len(morphology.past_pairs),
            "exact_plus_ed": len(morphology.regular_ed),
            "irregular_or_non_ed": len(morphology.irregular_or_non_ed),
        },
        "lexicon": {
            "lemma_upos_types": lexicon.lexeme_types,
            "surface_form_types": lexicon.form_types,
            "attestations": len(lexicon.attestations),
        },
        "eval": cov.as_dict(),
        "resources": {
            "wall_seconds": wall,
            "python_tracemalloc_peak_bytes": peak,
            "max_chart_nodes_per_sentence": max_chart_nodes,
        },
        "terminal": "DEV_CALIBRATION_ONLY",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-attestations", type=int, default=1)
    parser.add_argument("--max-chart-nodes", type=int, default=2_000_000)
    parser.add_argument("--max-dev-sentences", type=int)
    args = parser.parse_args()

    train = load_split(args.data_dir / "en_ewt-ud-train.conllu", "train")
    dev = load_split(args.data_dir / "en_ewt-ud-dev.conllu", "dev")
    if args.max_dev_sentences is not None:
        if args.max_dev_sentences < 1:
            raise SystemExit("--max-dev-sentences must be positive")
        dev = dev[: args.max_dev_sentences]
    result = evaluate(
        train,
        dev,
        min_attestations=args.min_attestations,
        max_chart_nodes=args.max_chart_nodes,
    )
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": result["receipt"],
        "terminal": result["terminal"],
        "train_lexeme_types": result["lexicon"]["lemma_upos_types"],
        "grammar_rules": result["grammar"]["rules"],
        "dev_exact_structure": result["eval"]["exact_gold_structure_projective"],
        "wall_seconds": result["resources"]["wall_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
