"""Controlled dialogue microworld (M4 §11): fully known worlds and scripted conversations with gold
for reference, correction, clarification, contradiction, topic return and delayed reference.

Each generated `Dialogue` is a list of `Step`s: a speaker utterance plus the *gold* expectations
the evaluator checks after the machine's turn (expected act, expected referent set, whether a
clarification is warranted, expected answer polarity, expected reopen).  The generator is seeded
and the protected split is fixed by content hash before any tuning (freeze-before-outcome).
Vocabulary is the M3 microworld's (given lexicon), so what is measured is dialogue cognition, not
lexical coverage.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from typing import Any

from ocm.kso.ids import canonical_json

NOUNS = ("robot", "door", "cat", "box", "key", "girl", "ball", "cup", "dog", "book")
VERBS = {"open": "opened", "push": "pushed", "see": "saw", "lift": "lifted", "kick": "kicked", "hold": "held", "find": "found"}


@dataclass(frozen=True)
class Step:
    speaker: str
    utterance: str
    gold: dict[str, Any]                    # expectations checked after this step


@dataclass(frozen=True)
class Dialogue:
    dialogue_id: str
    family: str
    steps: tuple[Step, ...]
    split: str

    def as_dict(self) -> dict[str, Any]:
        return {"dialogue_id": self.dialogue_id, "family": self.family, "split": self.split, "steps": [{"speaker": s.speaker, "utterance": s.utterance, "gold": s.gold} for s in self.steps]}


def _split_of(key: str, seed: str, protected_fraction: float = 0.4) -> str:
    h = int(hashlib.sha256(f"{seed}|{key}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "protected" if h < protected_fraction else "dev"


def _statement(a, v, p):
    return f"the {a} {VERBS[v]} the {p}"


def _question(a, v, p):
    return f"did the {a} {v} the {p}"


def generate(seed: str = "OCM-M4-DIALOGUE-20260905", n: int = 120) -> list[Dialogue]:
    rng = random.Random(seed)
    out: list[Dialogue] = []
    families = ("statement_question", "correction_reopens", "contradiction_two_speakers", "pronoun_ambiguous", "pronoun_resolved", "topic_return_delayed", "retraction_unrelated_intact", "ten_speakers_no_promotion")
    seen = set()
    while len(out) < n:
        fam = rng.choice(families)
        a, p, q, r_ = rng.sample(NOUNS, 4)
        v, v2 = rng.sample(list(VERBS), 2)
        steps: list[Step] = []
        if fam == "statement_question":
            steps = [Step("alice", _statement(a, v, p), {"act": "ACKNOWLEDGE"}), Step("bob", _question(a, v, p), {"act": "ANSWER", "polarity": "reported_yes", "cites": 1}), Step("bob", _question(a, v2, p), {"act": "REPORT_UNKNOWN"})]
        elif fam == "correction_reopens":
            steps = [Step("alice", _statement(a, v, p), {"act": "ACKNOWLEDGE"}), Step("alice", _statement(q, v2, r_), {"act": "ACKNOWLEDGE"}), Step("bob", _question(a, v, p), {"act": "ANSWER", "polarity": "reported_yes"}),
                     Step("alice", f"correction, the {a} did not {v} the {p}", {"act": "ACKNOWLEDGE", "supersedes": True}), Step("bob", _question(a, v, p), {"act": "ANSWER", "polarity": "reported_no"}), Step("bob", _question(q, v2, r_), {"act": "ANSWER", "polarity": "reported_yes", "unrelated_intact": True})]
        elif fam == "contradiction_two_speakers":
            steps = [Step("alice", _statement(a, v, p), {"act": "ACKNOWLEDGE"}), Step("bob", f"the {a} did not {v} the {p}", {"act": "ACKNOWLEDGE", "contradiction": True}), Step("carol", _question(a, v, p), {"act": "REPORT_UNCERTAIN", "cites": 2})]
        elif fam == "pronoun_ambiguous":
            steps = [Step("alice", _statement(a, v, p), {"act": "ACKNOWLEDGE", "entities": 2}), Step("bob", f"which {p} did it {v2}", {"act": "CLARIFY", "candidates": 2})]
        elif fam == "pronoun_resolved":
            steps = [Step("alice", f"the {a} {VERBS[v]}", {"act": "ACKNOWLEDGE", "entities": 1}), Step("bob", f"which {p} did it {v2}", {"act": "ANSWER_OR_UNKNOWN", "resolved_to": a})]
        elif fam == "topic_return_delayed":
            fillers = [Step("alice", _statement(x, y, z), {"act": "ACKNOWLEDGE"}) for x, y, z in [(rng.choice(NOUNS), rng.choice(list(VERBS)), rng.choice(NOUNS)) for _ in range(12)] if x != z]
            steps = [Step("alice", _statement(a, v, p), {"act": "ACKNOWLEDGE"})] + fillers + [Step("bob", _question(a, v, p), {"act": "ANSWER", "polarity": "reported_yes", "gap": len(fillers)})]
        elif fam == "retraction_unrelated_intact":
            steps = [Step("alice", _statement(a, v, p), {"act": "ACKNOWLEDGE", "remember": "c1"}), Step("alice", _statement(q, v2, r_), {"act": "ACKNOWLEDGE"}), Step("alice", "__retract:c1", {"act": "ACKNOWLEDGE", "retract": True}), Step("bob", _question(a, v, p), {"act": "REPORT_UNKNOWN"}), Step("bob", _question(q, v2, r_), {"act": "ANSWER", "polarity": "reported_yes", "unrelated_intact": True})]
        else:  # ten_speakers_no_promotion
            steps = [Step(f"u{i}", _statement(a, v, p), {"act": "ACKNOWLEDGE"}) for i in range(10)] + [Step("judge", _question(a, v, p), {"act": "ANSWER", "polarity": "reported_yes", "machine_layer_empty": True})]
        key = canonical_json({"f": fam, "s": [(s.speaker, s.utterance) for s in steps]})
        if key in seen:
            continue
        seen.add(key)
        out.append(Dialogue(hashlib.sha256(key.encode()).hexdigest()[:16], fam, tuple(steps), _split_of(key, seed)))
    return out


def custody_receipt(dialogues: list[Dialogue], seed: str) -> dict[str, Any]:
    dev = [d for d in dialogues if d.split == "dev"]
    prot = [d for d in dialogues if d.split == "protected"]
    return {
        "corpus": "OCM_M4_DIALOGUE_MICROWORLD_V1", "seed": seed, "n": len(dialogues), "dev": len(dev), "protected": len(prot),
        "dev_sha256": hashlib.sha256("\n".join(sorted(d.dialogue_id for d in dev)).encode()).hexdigest(),
        "protected_sha256": hashlib.sha256("\n".join(sorted(d.dialogue_id for d in prot)).encode()).hexdigest(),
        "families": sorted({d.family for d in dialogues}), "turns_total": sum(len(d.steps) for d in dialogues),
        "note": "protected split fixed by content hash before any tuning; gold is generated with the world, never from the machine",
    }
