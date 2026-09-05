"""The strongest faithful matched parent (M7 §4): the same knowledge, lessons, dialogue record and
budget, built from known components — retrieval memory, dialogue-state memory, in-context lesson
memory, template renderer.  Deliberately *without* warrant intervals, reopening, version spaces or a
commitment gate, so that what is subtracted is exactly the machine-epistemics machinery.

Its answers are honest to its own design: a fact retrieved from the knowledge set is answered
"Yes."; a user statement in memory is answered "said so"; otherwise "I do not know".  Corrections
replace the matching statement (string-level supersession); retraction deletes; revocation of a
lesson deletes the word (no locality accounting — that is what the OCM claim is about).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ocm.language.interpret import tokenize

CORRECTION_PREFIXES = ("correction,", "correction:", "no,", "actually,")


@dataclass
class MatchedParent:
    manifest: Path
    facts: set[tuple[str, str, str]] = field(default_factory=set)
    fact_sources: dict[tuple[str, str, str], list[str]] = field(default_factory=list)
    verified: set[tuple[str, str, str]] = field(default_factory=set)
    statements: list[dict[str, Any]] = field(default_factory=list)   # dialogue-state memory
    words: dict[str, str] = field(default_factory=dict)              # in-context lesson memory
    known_words: set[str] = field(default_factory=set)
    lessons: list[str] = field(default_factory=list)
    info: dict[str, int] = field(default_factory=lambda: {"knowledge_facts": 0, "lessons": 0, "statements": 0, "interaction_turns": 0})

    def __post_init__(self) -> None:
        self.fact_sources = {}
        man = json.loads(Path(self.manifest).read_text(encoding="utf-8"))
        for f in man["facts"]:
            t = (f["subject"], f["relation"], f["object"])
            self.facts.add(t)
            self.fact_sources.setdefault(t, []).extend(f["sources"])
            if f.get("verified_by"):
                self.verified.add(t)
        self.info["knowledge_facts"] = len(self.facts)
        from tests.m3.test_microworld import _lexicon_for

        lx = _lexicon_for(())
        self.known_words = {k.split("|")[0] for k in lx.lexemes} | {"the", "a", "an", "is", "in", "did", "do", "does", "not", "was", "by", "which", "it", "bank", "what", "of"}
        self.known_words |= {f["subject"] for f in man["facts"]} | {f["object"] for f in man["facts"]}

    # ------------------------------------------------------------------ state persistence (matched)
    def save(self, path: Path) -> None:
        path.write_text(json.dumps({"statements": self.statements, "words": self.words, "lessons": self.lessons}, sort_keys=True), encoding="utf-8")

    def load(self, path: Path) -> None:
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            self.statements, self.words, self.lessons = d["statements"], d["words"], d["lessons"]

    # ------------------------------------------------------------------ helpers
    def _unknown_tokens(self, text: str) -> list[str]:
        return [t for t in tokenize(text) if t not in self.known_words and t not in self.words and not (t.endswith("ed") and t[:-2] in self.known_words)]

    def _statement_key(self, text: str) -> tuple[str, ...]:
        toks = [t for t in tokenize(text) if t not in ("the", "a", "an", "did", "not", "do")]
        return tuple(t[:-2] if t.endswith("ed") and t[:-2] in self.known_words else t for t in toks)

    # ------------------------------------------------------------------ the loop
    def say(self, text: str) -> str:
        self.info["interaction_turns"] += 1
        low = text.strip().lower()
        if low.startswith("teach:"):
            body = low[len("teach:"):].strip()
            word, _, concept = body.partition("=")
            self.words[word.strip()] = concept.strip()
            self.lessons.append(body)
            self.info["lessons"] += 1
            return f"Noted: '{word.strip()}' means {concept.strip()}. I will use it."
        if low.startswith("revoke "):
            target = low.split(" ", 1)[1].strip()
            if target in self.words:
                del self.words[target]
                return "Revoked."
            return f"{target} is not on record."
        if low.startswith("forget "):
            key = self._statement_key(low[len("forget "):])
            self.statements = [s for s in self.statements if tuple(s["key"]) != key]
            return "Forgotten."
        corr = any(low.startswith(p) for p in CORRECTION_PREFIXES)
        if corr:
            for p in CORRECTION_PREFIXES:
                if low.startswith(p):
                    low = low[len(p):].strip()
                    break
        if self._unknown_tokens(low):
            return f"I cannot interpret this yet (UNKNOWN_LEXEME). Show me what it means."
        toks = tokenize(low)
        if toks and toks[0] in ("is", "does", "did"):
            return self._answer(toks)
        if toks and toks[0] in ("which", "what"):
            return "I do not know what 'it' refers to." if "it" in toks else "I do not know."
        if low.startswith("explain "):
            label = low[len("explain "):].replace("the ", "").strip("?. ")
            hits = [t for t in self.facts if t[0] == label]
            return " ".join(f"{a} {r.lower().replace('_', ' ')} {b}." for a, r, b in sorted(hits)[:3]) if hits else f"I do not have anything verified about '{label}'."
        # statement → memory (string-level supersession on correction)
        key = self._statement_key(low)
        negated = "not" in toks
        if corr:
            self.statements = [s for s in self.statements if tuple(s["key"]) != key]
        self.statements.append({"key": list(key), "negated": negated, "text": low})
        self.info["statements"] += 1
        return f"Noted: you said {'not ' if negated else ''}{' '.join(key)}."

    def _answer(self, toks: list[str]) -> str:
        body = [t for t in toks[1:] if t not in ("the", "a", "an")]
        if toks[0] == "is" and "in" in toks:
            i = toks.index("in")
            subj = " ".join(t for t in toks[1:i] if t != "the"); obj = " ".join(t for t in toks[i + 1:] if t != "the")
            return self._fact(subj, "LOCATED_IN", obj)
        if toks[0] == "is" and any(t in ("a", "an") for t in toks[2:]):
            start = 2 if toks[1] in ("a", "an", "the") else 1
            i = next(k for k, t in enumerate(toks) if k >= start + 1 and t in ("a", "an"))
            return self._fact(" ".join(t for t in toks[start:i] if t != "the"), "IS_A", " ".join(toks[i + 1:]))
        if toks[0] == "does" and len(body) >= 3:
            rel = {"orbit": "ORBITS", "orbits": "ORBITS", "contain": "CONTAINS"}.get(body[1])
            if rel:
                return self._fact(body[0], rel, " ".join(body[2:]))
        # did X V Y → dialogue memory
        key = tuple(t for t in body)
        pos = [s for s in self.statements if tuple(s["key"]) == key and not s["negated"]]
        neg = [s for s in self.statements if tuple(s["key"]) == key and s["negated"]]
        if pos and not neg:
            return "You said so."
        if neg and not pos:
            return "You said it did not."
        if pos and neg:
            return "You said both."
        return "I do not know."

    def _fact(self, s: str, r: str, o: str) -> str:
        t = (s, r, o)
        if t in self.facts:
            return "Yes." if t in self.verified else f"A source ({self.fact_sources[t][0]}) says so."
        return f"I do not know whether {s} {r.lower().replace('_', ' ')} {o}."
