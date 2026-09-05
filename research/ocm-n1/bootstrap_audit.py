"""Prospective N1 language-bootstrap audit.

This is an accounting gate, not a language-capability evaluator.  It binds the
current historical language/communication sources and makes their authored prior
content explicit before N1 protected acquisition.  It intentionally lives under
``research/`` so it does not rewrite sealed M1-M12 runtime source inventories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

MANIFEST = HERE / "LANGUAGE_BOOTSTRAP_MANIFEST_V1.json"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def runtime_inventory() -> dict[str, Any]:
    from ocm.dialogue.clarify import binary_questions
    from ocm.dialogue.gate import Act
    from ocm.dialogue.planner import FUNCTIONAL_RELATIONS, Rhetorical
    from ocm.dialogue.reference import ORDINALS, PRONOUNS
    from ocm.dialogue.surface_text import PHRASES
    from ocm.language.bootstrap import acquisition_lexicon, microworld_lexicon
    from ocm.language.constructions import seed_constructions
    from ocm.language.lexicon import Category

    micro = microworld_lexicon()
    acquisition = acquisition_lexicon()
    cons = seed_constructions()
    # Exercise the clarification producer to ensure this audit is not merely
    # counting an unused symbol.  Wording is intentionally treated as prior.
    qs = binary_questions(("a", "b"), str)
    if not qs or not all(isinstance(q.text, str) and q.text for q in qs):
        raise AssertionError("registered clarification wording is not executable")
    return {
        "microworld_seed_lexemes": len(micro.lexemes),
        "microworld_seed_morph_rules": len(micro.rules),
        "acquisition_fixture_seed_lexemes": len(acquisition.lexemes),
        "acquisition_fixture_seed_morph_rules": len(acquisition.rules),
        "lexical_categories": len(Category),
        "seed_constructions": [c.construction_id for c in cons],
        "seed_construction_families": [c.family for c in cons],
        "fixed_dialogue_acts": len(Act),
        "fixed_rhetorical_relations": len(Rhetorical),
        "fixed_reference_pronouns": len(PRONOUNS),
        "fixed_reference_ordinals": len(ORDINALS),
        "fixed_world_surface_phrase_templates": len(PHRASES),
        "functional_relation_registry_entries": len(FUNCTIONAL_RELATIONS),
        "clarification_question_forms_executable": True,
    }


def verify() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "ocm.language-bootstrap.v1":
        raise AssertionError("unexpected bootstrap manifest schema")
    if manifest.get("protected_outcomes_read") is not False:
        raise AssertionError("bootstrap audit lost prospective-only scope")

    binding_errors = {}
    for rel, expected in manifest["source_bindings"].items():
        path = ROOT / rel
        actual = git_blob_sha(path) if path.is_file() else "MISSING"
        if actual != expected:
            binding_errors[rel] = {"expected": expected, "actual": actual}
    if binding_errors:
        raise AssertionError(f"language bootstrap source binding drift: {binding_errors}")

    actual = runtime_inventory()
    expected = manifest["observed_current_runtime"]
    mismatches = {k: {"expected": v, "actual": actual.get(k)} for k, v in expected.items() if actual.get(k) != v}
    if mismatches:
        raise AssertionError(f"language bootstrap inventory drift: {mismatches}")

    target = manifest["n1_minimal_target"]
    if not target["retain_constitutional_or_language_general"] or not target["exclude_from_time_zero_language_competence"]:
        raise AssertionError("minimal target must declare both retained and excluded prior classes")

    strong_prior_present = any(
        actual[k] > 0
        for k in (
            "microworld_seed_lexemes",
            "microworld_seed_morph_rules",
            "fixed_reference_pronouns",
            "fixed_world_surface_phrase_templates",
        )
    ) and bool(actual["seed_constructions"])
    if not strong_prior_present:
        raise AssertionError("audit expected the historical runtime to contain authored language prior")

    return {
        "receipt": "LANGUAGE_BOOTSTRAP_AUDIT_V1",
        "base_main_commit": manifest["base_main_commit"],
        "source_bindings": "PASS",
        "inventory": actual,
        "prior_classes": len(manifest["prior_classes"]),
        "minimal_target_retained_classes": len(target["retain_constitutional_or_language_general"]),
        "minimal_target_excluded_classes": len(target["exclude_from_time_zero_language_competence"]),
        "strong_authored_language_prior_present": strong_prior_present,
        "terminal": manifest["current_terminal"],
        "claim_authority": manifest["claim_authority"],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = verify()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
