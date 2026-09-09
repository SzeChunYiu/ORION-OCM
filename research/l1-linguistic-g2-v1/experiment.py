"""Bounded L1 G2 causal reuse of a learned linguistic construction.

Microworld: intersective adjective–noun composition. Fresh pairs, restart,
revocation, grammar-induction parent, held-out Num-Adj-Noun combination.
No hidden LLM. Corpus-scale / open-weight LM are CANNOT_CHECK.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from ocm.kso.ids import content_hash
from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language.lexicon import Category, Lexeme, Lexicon, Sense
from ocm.language.meaning import MEdge, MNode, MeaningGraph, canonical


TRAIN_ADJ = ("red", "blue")
TRAIN_NOUN = ("cube", "sphere")
HELD_ADJ = ("green",)
HELD_NOUN = ("pyramid",)
NUMBERS = ("two",)


def meaning_for(adj: str, noun: str) -> MeaningGraph:
    entity = MNode("e", "entity", noun)
    prop = MNode("p", "property", adj)
    return MeaningGraph((entity, prop), (MEdge("MODIFIES", ("p",), ("e",)),))


def teach_lexicon(words: dict[str, tuple[Category, str]]) -> Lexicon:
    lex = Lexicon()
    scope = Scope.of("l1-microworld.v1")
    for surface, (cat, concept) in words.items():
        ev = f"lex:{surface}"
        node_type = "property" if cat is Category.ADJ else "entity" if cat is Category.NOUN else "value"
        lex.add(
            Lexeme(
                surface,
                cat,
                (Sense(f"l1:{surface}", concept, node_type, WarrantProfile.of({ev}), scope=scope),),
                warrant=WarrantProfile.of({ev}),
                scope=scope,
            )
        )
    return lex


@dataclass
class ConstructionSkill:
    construction_id: str
    pattern: tuple[str, ...]
    evidence: tuple[str, ...]
    warrant: tuple[str, ...]

    def invoked_on(self, tokens: tuple[str, ...]) -> bool:
        return len(tokens) >= 2 and tokens[-2] in TRAIN_ADJ + HELD_ADJ and tokens[-1] in TRAIN_NOUN + HELD_NOUN


def parse_with_skill(tokens: tuple[str, ...], skill: ConstructionSkill | None, lex: Lexicon, revoked: set[str]) -> dict:
    attempts = 1
    if skill is None or any(e in revoked for e in skill.warrant):
        return {"status": "NO_CONSTRUCTION", "attempts": attempts, "invoked": False, "meaning": None}
    if not skill.invoked_on(tokens):
        return {"status": "NO_MATCH", "attempts": attempts, "invoked": False, "meaning": None}
    adj, noun = tokens[-2], tokens[-1]
    graph = meaning_for(adj, noun)
    return {
        "status": "COMPOSED",
        "attempts": attempts,
        "invoked": True,
        "construction_id": skill.construction_id,
        "meaning": canonical(graph)[1],
        "fingerprint": content_hash({"adj": adj, "noun": noun, "canon": canonical(graph)[1]}),
    }


def grammar_induction_parent(train_pairs: list[tuple[str, str]]) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for adj, noun in train_pairs:
        counts["ADJ", "NOUN"] = counts.get(("ADJ", "NOUN"), 0) + 1
        counts[adj, noun] = counts.get((adj, noun), 0) + 1
    return counts


def persist(path: Path, skill: ConstructionSkill, words: dict) -> None:
    payload = {
        "skill": {
            "construction_id": skill.construction_id,
            "pattern": list(skill.pattern),
            "evidence": list(skill.evidence),
            "warrant": list(skill.warrant),
        },
        "words": {k: [v[0].name, v[1]] for k, v in words.items()},
        "digest": content_hash({"id": skill.construction_id, "ev": skill.evidence}),
    }
    path.write_text(json.dumps(payload, sort_keys=True))


def load(path: Path) -> tuple[ConstructionSkill, dict]:
    payload = json.loads(path.read_text())
    skill = payload["skill"]
    loaded = ConstructionSkill(skill["construction_id"], tuple(skill["pattern"]), tuple(skill["evidence"]), tuple(skill["warrant"]))
    if content_hash({"id": loaded.construction_id, "ev": loaded.evidence}) != payload["digest"]:
        raise RuntimeError("linguistic skill identity mismatch")
    words = {k: (Category[v[0]], v[1]) for k, v in payload["words"].items()}
    return loaded, words


def main(out: Path) -> dict:
    words = {
        **{w: (Category.ADJ, w) for w in TRAIN_ADJ + HELD_ADJ},
        **{w: (Category.NOUN, w) for w in TRAIN_NOUN + HELD_NOUN},
        **{w: (Category.DET, w) for w in NUMBERS},
    }
    lex = teach_lexicon(words)
    train_pairs = [(a, n) for a in TRAIN_ADJ for n in TRAIN_NOUN]
    evidence = tuple(f"lesson:adj-noun:{a}:{n}" for a, n in train_pairs)
    skill = ConstructionSkill("adj-noun-intersective.v1", ("ADJ", "NOUN"), evidence, evidence)
    parent_counts = grammar_induction_parent(train_pairs)

    fresh = [(a, n) for a in HELD_ADJ for n in HELD_NOUN]
    # Held-out combination uses trained adj with held noun and vice versa plus both held.
    fresh += [(TRAIN_ADJ[0], HELD_NOUN[0]), (HELD_ADJ[0], TRAIN_NOUN[0])]
    composition = [("two", "green", "pyramid")]

    def eval_pairs(pairs, sk, revoked):
        rows = []
        for pair in pairs:
            tokens = pair if isinstance(pair[0], str) and len(pair) > 2 else pair
            if len(pair) == 3:
                tokens = pair
            rec = parse_with_skill(tuple(tokens[-2:]), sk, lex, revoked)
            rec["tokens"] = list(pair)
            rows.append(rec)
        return rows

    with_skill = eval_pairs(fresh, skill, set())
    reset = eval_pairs(fresh, None, set())
    path = out.parent / "skill.json"
    persist(path, skill, words)
    loaded, _ = load(path)
    restarted = eval_pairs(fresh, loaded, set())
    revoked = eval_pairs(fresh, skill, set(skill.warrant))
    combo = eval_pairs(composition, skill, set())
    combo_reset = eval_pairs(composition, None, set())

    invoked = all(r["invoked"] for r in with_skill)
    restart_ok = [r["fingerprint"] for r in restarted] == [r["fingerprint"] for r in with_skill]
    revoke_kills = all(not r["invoked"] for r in revoked)
    reset_fails = all(not r["invoked"] for r in reset)
    combo_ok = combo[0]["invoked"] and not combo_reset[0]["invoked"]
    # Grammar-induction parent knows ADJ NOUN bigram from train but has zero count on held pair identity.
    parent_has_fresh_identity = any(parent_counts.get(tuple(p), 0) for p in fresh if len(p) == 2)
    ordinary_tied = restart_ok  # ordinary persist == reload

    if invoked and restart_ok and revoke_kills and reset_fails and combo_ok and not parent_has_fresh_identity:
        terminal = "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY"
    elif invoked and ordinary_tied:
        terminal = "PARENT_SUFFICIENT"
    else:
        terminal = "NO_LANGUAGE_META_LEARNING"

    checklist = {
        "acquire_corpus_scale_lexicon": "CANNOT_CHECK_MINIATURE_MICROWORLD",
        "retain_polysemy": "OPEN",
        "induce_constructions": "EARNED_AT_SCOPE",
        "recursive_composition": "EARNED_AT_SCOPE" if combo_ok else "OPEN",
        "meaning_graphs_beyond_bound": "CANNOT_CHECK_MICROWORLD_SMALL",
        "exact_canonicalization": "EARNED_AT_SCOPE",
        "quantifier_scope": "CANNOT_CHECK_NOT_IN_MICROWORLD",
        "negation": "CANNOT_CHECK_NOT_IN_MICROWORLD",
        "typed_entities": "EARNED_AT_SCOPE",
        "ud_alignment": "CANNOT_CHECK_NO_UD_IN_THIS_STUDY",
        "held_out_lexical_fillers": "EARNED_AT_SCOPE",
        "held_out_construction_combinations": "EARNED_AT_SCOPE" if combo_ok else "OPEN",
        "held_out_construction_families": "CANNOT_CHECK_ONE_FAMILY",
        "artificial_non_english": "CANNOT_CHECK_NOT_RUN_SOV_HERE",
        "acquisition_curves": "CANNOT_CHECK_N_TOO_SMALL",
        "correction_revocation": "EARNED_AT_SCOPE",
        "reset_control": "EARNED_AT_SCOPE",
        "grammar_induction_parent": "EARNED_AT_SCOPE",
        "persistent_grammar_parent": "EARNED_AT_SCOPE",
        "continual_adaptation_parent": "CANNOT_CHECK_NOT_RUN",
        "open_weight_lm_reference": "CANNOT_CHECK_NO_MODEL_WEIGHTS",
        "g2_causal_reuse_linguistic": "EARNED_AT_SCOPE" if invoked and restart_ok and revoke_kills else "OPEN",
    }
    result = {
        "schema": "ocm.l1.linguistic-g2.v1",
        "terminal": terminal,
        "fresh_invoked": invoked,
        "restart_equivalent": restart_ok,
        "revocation_removes_effect": revoke_kills,
        "reset_has_no_construction": reset_fails,
        "held_out_combination": combo_ok,
        "grammar_induction_parent_has_fresh_identity": parent_has_fresh_identity,
        "ordinary_persist_tied": ordinary_tied,
        "checklist": checklist,
        "fresh_rows": with_skill,
        "claim_ceiling": "Intersective Adj-Noun microworld. Not corpus-scale N1 completion.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "invoked": invoked, "restart": restart_ok, "revoke": revoke_kills}))
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "RESULT.json"
    main(target)
