"""Bounded input hypotheses. Similar spelling never supplies a semantic warrant.

Only unknown tokens are considered; known words, negation, numbers and commands
are preserved. Equal-distance candidates remain alternatives, irrespective of
which answer the knowledge base would prefer.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import re

from ocm.kso.warrant import Liveness

WORDS = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
PROTECTED = frozenset({"not", "no", "never", "nor", "none", "all", "any", "some"})
FUNCTIONS = frozenset("what which who is are does do did the a an in of orbit orbits explain compare and with summarize summarise please can you tell me about hello hi hey thanks thank yes help list skills methods have learned know learn good morning".split())
COMMANDS = ("teach:", "remember:", "learn method ", "find method:", "run ", "revoke ", "reinstate ")


def one_edit(a: str, b: str) -> bool:
    """Insertion, deletion, substitution, or one adjacent transposition."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        differences = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        return len(differences) == 1 or (len(differences) == 2
            and differences[1] == differences[0] + 1
            and a[differences[0]] == b[differences[1]]
            and a[differences[1]] == b[differences[0]])
    short, long = sorted((a, b), key=len)
    i = next((i for i, (x, y) in enumerate(zip(short, long)) if x != y), len(short))
    return short[i:] == long[i + 1:]


@dataclass(frozen=True)
class InputHypotheses:
    original: str
    candidates: tuple[str, ...] = ()
    edits: tuple[tuple[str, tuple[str, ...]], ...] = ()
    status: str = "UNCHANGED"


def propose(text, lexicon, revoked=()):
    if len(text) > 2048 or text.lower().strip().startswith(COMMANDS):
        return InputHypotheses(text)
    revoked = frozenset(revoked)
    matches = list(WORDS.finditer(text))
    if len(matches) > 64:
        return InputHypotheses(text, status="INPUT_BUDGET")
    if all(m.group().lower() in FUNCTIONS | PROTECTED or
           lexicon.analyse(m.group().lower(), revoked).readings for m in matches):
        return InputHypotheses(text)
    known = {lex.lemma for lex in lexicon.lexemes.values()} | FUNCTIONS | PROTECTED
    vocabulary = set(FUNCTIONS)
    for lex in lexicon.lexemes.values():
        forms = {lex.lemma}
        for rule in lexicon.rules:
            if rule.category == lex.category and (not rule.lemmas or lex.lemma in rule.lemmas):
                forms.add(rule.apply(lex.lemma))
        known.update(forms)  # revoked forms must not be rescued by a spelling guess
        for form in forms:
            if form.isalpha() and any(r.liveness(revoked) is Liveness.LIVE
                                     for r in lexicon.analyse(form, revoked).readings):
                vocabulary.add(form)
    edits, positions = [], []
    for i, match in enumerate(matches):
        word = match.group().lower()
        if word in known or len(word) < 3 or len(word) > 32:
            continue
        candidates = tuple(sorted(v for v in vocabulary if v not in PROTECTED and one_edit(word, v)))
        if candidates:
            edits.append((word, candidates))
            positions.append(i)
    if not edits:
        return InputHypotheses(text)
    count = 1
    for _, choices in edits:
        count *= len(choices)
    if len(edits) > 3 or count > 16:
        return InputHypotheses(text, edits=tuple(edits), status="CLARIFY_BUDGET")
    candidates = []
    for choices in product(*(e[1] for e in edits)):
        result, cursor = [], 0
        replacements = dict(zip(positions, choices))
        for i, match in enumerate(matches):
            result.extend((text[cursor:match.start()], replacements.get(i, match.group())))
            cursor = match.end()
        result.append(text[cursor:])
        candidates.append("".join(result))
    return InputHypotheses(text, tuple(candidates), tuple(edits), "GUESS" if count == 1 else "AMBIGUOUS")
