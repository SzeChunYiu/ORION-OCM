"""Synthetic aligned microworld corpus (M3 §8 E1, §9 custody, §13 generalisation splits).

Generates ``(utterance, MeaningGraph)`` pairs from a small registered vocabulary and construction
families with a **committed seed**; the protected split is fixed by content hash *before* any
tuning (freeze-before-outcome).  Splits: ``dev`` / ``protected``, plus held-out families:
unseen lexical combinations, unseen entity names, unseen argument combinations, paraphrase pairs
(active/passive), and a construction taught only after the freeze.  Every generated example
carries its own hash so a receipt can prove which examples were visible.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from typing import Any, Iterable

from ocm.kso.ids import canonical_json

from .meaning import MEdge, MNode, MeaningGraph, canonical

NOUNS = ("robot", "door", "cat", "box", "key", "girl", "ball", "cup", "dog", "book")
VERBS_PAST = {"open": "opened", "push": "pushed", "see": "saw", "lift": "lifted", "kick": "kicked", "hold": "held", "find": "found"}
ADJS = ("red", "big", "small", "blue")


@dataclass(frozen=True)
class Example:
    example_id: str
    utterance: str
    meaning: MeaningGraph
    family: str
    split: str
    held_out: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"example_id": self.example_id, "utterance": self.utterance, "meaning": self.meaning.as_dict(), "family": self.family, "split": self.split, "held_out": list(self.held_out)}


def _transitive(agent: str, verb: str, patient: str, adj: str | None = None, *, negated: bool = False, question: bool = False, passive: bool = False) -> tuple[str, MeaningGraph]:
    nodes = [MNode("x1", "entity", agent, (("definite", "yes"),)), MNode("e", "event", verb), MNode("x2", "entity", patient, (("definite", "yes"),))]
    edges = [MEdge("ROLE:agent", ("e",), ("x1",)), MEdge("ROLE:patient", ("e",), ("x2",)), MEdge("TENSE", ("e",), ("e",), "past")]
    obj = f"the {adj} {patient}" if adj else f"the {patient}"
    if adj:
        nodes.append(MNode("p2", "property", adj))
        edges.append(MEdge("MODIFIES", ("p2",), ("x2",)))
    if negated:
        edges.append(MEdge("NEGATES", ("e",), ("e",)))
        utt = f"the {agent} did not {verb} {obj}"
    elif question:
        nodes.append(MNode("q", "question_variable", None, underspecified=True))
        edges.append(MEdge("ASKS", ("q",), ("e",), "polarity"))
        utt = f"did the {agent} {verb} {obj}"
    elif passive:
        utt = f"{obj} was {VERBS_PAST[verb]} by the {agent}"
    else:
        utt = f"the {agent} {VERBS_PAST[verb]} {obj}"
    return utt, MeaningGraph(tuple(nodes), tuple(edges), root="e")


def _split_of(example_key: str, seed: str, protected_fraction: float = 0.3) -> str:
    h = int(hashlib.sha256(f"{seed}|{example_key}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "protected" if h < protected_fraction else "dev"


def generate(seed: str = "OCM-M3-MICROWORLD-20260905", n: int = 240, *, held_out_nouns: tuple[str, ...] = ("dog", "book"), held_out_verb: str = "find") -> list[Example]:
    """Deterministic corpus.  Held-out lexemes never appear in the dev split (generalisation to
    unseen names / unseen argument combinations is measured on them)."""
    rng = random.Random(seed)
    out: list[Example] = []
    seen: set[str] = set()
    families = ("transitive", "transitive_adj", "negation", "yes_no", "passive")
    while len(out) < n:
        fam = rng.choice(families)
        agent, patient = rng.sample(NOUNS, 2)
        verb = rng.choice(list(VERBS_PAST))
        adj = rng.choice(ADJS) if fam == "transitive_adj" else None
        utt, m = _transitive(agent, verb, patient, adj, negated=(fam == "negation"), question=(fam == "yes_no"), passive=(fam == "passive"))
        if utt in seen:
            continue
        seen.add(utt)
        key = canonical_json({"u": utt, "m": canonical(m)[1]})
        held = tuple(x for x in (agent, patient, verb) if x in held_out_nouns or x == held_out_verb)
        split = "protected" if held else _split_of(key, seed)
        out.append(Example(hashlib.sha256(key.encode()).hexdigest()[:16], utt, m, fam, split, held))
    return out


def paraphrase_pairs(examples: Iterable[Example]) -> list[tuple[Example, Example]]:
    """Active/passive pairs with identical meaning graphs (meaning equivalence under paraphrase)."""
    by_digest: dict[str, list[Example]] = {}
    for e in examples:
        by_digest.setdefault(canonical(e.meaning)[1], []).append(e)
    pairs = []
    for group in by_digest.values():
        act = [e for e in group if e.family == "transitive"]
        pas = [e for e in group if e.family == "passive"]
        for a in act:
            for p in pas:
                pairs.append((a, p))
    return pairs


def custody_receipt(examples: list[Example], seed: str) -> dict[str, Any]:
    dev = [e for e in examples if e.split == "dev"]
    prot = [e for e in examples if e.split == "protected"]
    return {
        "corpus": "OCM_M3_MICROWORLD_V1",
        "seed": seed,
        "n": len(examples),
        "dev": len(dev),
        "protected": len(prot),
        "dev_sha256": hashlib.sha256("\n".join(sorted(e.example_id for e in dev)).encode()).hexdigest(),
        "protected_sha256": hashlib.sha256("\n".join(sorted(e.example_id for e in prot)).encode()).hexdigest(),
        "families": sorted({e.family for e in examples}),
        "held_out_lexemes_absent_from_dev": all(not e.held_out for e in dev),
        "note": "protected split fixed by content hash before any tuning; annotations (meaning graphs) are visible only for dev during training",
    }
