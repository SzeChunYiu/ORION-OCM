#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Route B of `gmi-833-aa-logical-form-register-v1` (issue #833, section AA).

Imports NOTHING from route A. Reads the statement snapshot and the hand
register as data, re-derives every form with a hand-written character/token
scanner (the `re` module is not imported), recomputes the five review queues
from its own parse, and compares against route A's committed register and
queues by canonical-structure equality (amendment 01 item 17).

    python3 -I -B research/gmi-833-aa-logical-form-register-v1/independent_form_oracle_v1.py
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / "STATEMENT_SNAPSHOT_V1.json"
REGISTER = HERE / "LOGICAL_FORM_REGISTER_V1.json"
QUEUES = HERE / "QUEUES_V1.json"
HAND = HERE / "HAND_REGISTER_V1.json"
ROWS = ("AA16", "AA17", "AA18", "AA20", "AA22")
RUN_MODES = ("EMPIRICAL_EXPERIMENT", "STATISTICAL_EXPERIMENT")

# ---------------------------------------------------------------------------
# character scanner utilities (no regular expressions anywhere in this file)
# ---------------------------------------------------------------------------
def is_word_char(c: str) -> bool:
    return c.isalnum() or c == "_"


def find_word(text: str, phrase: str, start: int = 0, lower: Optional[str] = None,
              lead_boundary: bool = True, tail_boundary: bool = True) -> int:
    """Earliest index >= start of `phrase` (case-insensitive) with word
    boundaries on the requested sides; -1 when absent."""
    low = lower if lower is not None else text.lower()
    ph = phrase.lower()
    i = low.find(ph, start)
    while i >= 0:
        ok = True
        if lead_boundary and i > 0 and is_word_char(low[i - 1]) and is_word_char(ph[0]):
            ok = False
        j = i + len(ph)
        if ok and tail_boundary and j < len(low) and is_word_char(low[j - 1]) and is_word_char(low[j]):
            ok = False
        if ok:
            return i
        i = low.find(ph, i + 1)
    return -1


def has_word(text: str, phrase: str) -> bool:
    return find_word(text, phrase) >= 0


def startswith_word(text: str, words: Tuple[str, ...]) -> Optional[str]:
    low = text.lower()
    for w in words:
        if low.startswith(w.lower()) and (len(low) == len(w) or not is_word_char(low[len(w)])):
            return w
    return None


def collapse_ws(s: str) -> str:
    return " ".join(s.split())


def replace_spans(text: str, opener: str, closer: str, token: str) -> str:
    out = []
    i = 0
    while True:
        a = text.find(opener, i)
        if a < 0:
            out.append(text[i:])
            break
        b = text.find(closer, a + len(opener))
        if b < 0:
            out.append(text[i:])
            break
        out.append(text[i:a])
        out.append(" " + token + " ")
        i = b + len(closer)
    return "".join(out)


def replace_inline_dollar(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "$" and (i == 0 or text[i - 1] not in "\\$") and (i + 1 < n and text[i + 1] != "$"):
            j = text.find("$", i + 1)
            if j > i and j - i - 1 <= 200 and "\n" not in text[i + 1:j]:
                out.append(" <MATH> ")
                i = j + 1
                continue
        out.append(c)
        i += 1
    return "".join(out)


def normalize(text: str) -> str:
    text = replace_spans(text, "\\[", "\\]", "<MATH>")
    text = replace_spans(text, "$$", "$$", "<MATH>")
    text = replace_spans(text, "\\(", "\\)", "<MATH>")
    text = replace_inline_dollar(text)
    text = text.replace("`", "").replace("**", "").replace("__", "")
    # a lone `*` (not adjacent to a word char) is markdown emphasis
    out = []
    for i, c in enumerate(text):
        if c == "*":
            prev_w = i > 0 and is_word_char(text[i - 1])
            next_w = i + 1 < len(text) and is_word_char(text[i + 1])
            if not prev_w and not next_w:
                continue
        out.append(c)
    return collapse_ws("".join(out))


ABBREV = ("e.g.", "i.e.", "cf.", "vs.", "resp.", "etc.", "Eq.", "Thm.", "Def.",
          "Sec.", "Fig.", "no.", "approx.", "w.r.t.", "a.s.", "i.i.d.", "viz.",
          "Prop.", "Lem.", "Cor.", "Ex.", "Ch.", "pp.", "p.", "St.", "Dr.")
OPENERS_AFTER_MATH = ("If", "Then", "Thus", "Therefore", "Hence", "Consequently", "Equivalently",
                      "For", "The", "This", "In", "A", "An", "It", "So", "Moreover", "When",
                      "Whenever", "Let", "Suppose", "Assume", "Since", "By", "Because", "Under",
                      "There", "Every", "Any", "No", "With", "Without", "Conversely", "Otherwise", "Where")
MARK = "§"


def protect(t: str) -> str:
    for ab in ABBREV:
        t = t.replace(ab, ab.replace(".", MARK))
    chars = list(t)
    for i in range(1, len(chars) - 1):
        if chars[i] == "." and chars[i - 1].isdigit() and chars[i + 1].isdigit():
            chars[i] = MARK
    t = "".join(chars)
    chars = list(t)
    for i in range(1, len(chars) - 1):
        if (chars[i] == "." and chars[i - 1].isupper() and chars[i + 1].isupper()
                and (i - 2 < 0 or not is_word_char(chars[i - 2]))
                and (i + 2 >= len(chars) or not is_word_char(chars[i + 2]))):
            chars[i] = MARK
    return "".join(chars)


def split_sentences(text: str) -> List[str]:
    t = protect(text)
    # rules and bullets become breaks
    words = t.split(" ")
    rebuilt = []
    i = 0
    while i < len(words):
        w = words[i]
        if len(w) >= 3 and set(w) == {"-"} and i > 0:
            rebuilt.append(".")
        elif w in ("-", "*") and i > 0 and i + 1 < len(words) and words[i + 1] != "":
            rebuilt.append(".")
        else:
            rebuilt.append(w)
        i += 1
    words = rebuilt
    # break after <MATH>/<CODE> when a capitalised opener follows
    rebuilt = []
    for i, w in enumerate(words):
        if w in ("<MATH>", "<CODE>") and i + 1 < len(words):
            nxt = words[i + 1]
            core = nxt
            if any(core == o or (core.startswith(o) and len(core) > len(o) and not is_word_char(core[len(o)]))
                   for o in OPENERS_AFTER_MATH):
                rebuilt.append(w + ".")
                continue
        rebuilt.append(w)
    t = " ".join(rebuilt)
    # split at [.!?] + whitespace + [A-Z<([\"']
    parts = []
    cur = []
    i = 0
    n = len(t)
    while i < n:
        c = t[i]
        cur.append(c)
        if c in ".!?":
            j = i + 1
            while j < n and t[j].isspace():
                j += 1
            if j > i + 1 and j < n and (t[j].isupper() or t[j] in "<([\"'"):
                parts.append("".join(cur))
                cur = []
                i = j
                continue
        i += 1
    if cur:
        parts.append("".join(cur))
    out = []
    for p in parts:
        p = p.replace(MARK, ".").strip().strip(".").strip()
        if p and any(ch.isalpha() or ch == "<" for ch in p):
            out.append(p)
    return out


HYP_ONLY = ("Let", "Suppose", "Assume", "Fix", "Consider", "Given")
CONCL_LEAD = ("Then", "Therefore", "Hence", "Thus", "Consequently", "So", "In particular", "Moreover", "Furthermore")


def strip_lead(s: str) -> str:
    w = startswith_word(s, CONCL_LEAD)
    if w is None:
        return s
    rest = s[len(w):]
    if rest[:1] in (",", ":"):
        rest = rest[1:]
    if rest[:1].isspace():
        return rest.lstrip()
    return s


def hypothesis_chain(statement: str) -> Tuple[List[str], Optional[str], bool]:
    sents = split_sentences(statement)
    hyps = []
    concl = None
    idx = None
    for i, s in enumerate(sents):
        if startswith_word(s, HYP_ONLY) is not None:
            hyps.append(s)
            continue
        concl = s
        idx = i
        break
    trailing = idx is not None and idx < len(sents) - 1
    if concl is not None:
        concl = strip_lead(concl)
    return hyps, concl, trailing


# ---------------------------------------------------------------------------
# relational lexicon (same cue set as FREEZE 5 + amendment item 1)
# ---------------------------------------------------------------------------
def pos_eq_sign(text: str) -> int:
    for i, c in enumerate(text):
        if c == "=" and (i == 0 or text[i - 1] not in "<>!") and (i + 1 >= len(text) or text[i + 1] != "="):
            return i
    return -1


def pos_phrase_then_word(text: str, first: str, tails: Tuple[str, ...]) -> int:
    """`\\b(is|are) <MATH>` style: first word followed by one space and a tail."""
    low = text.lower()
    i = find_word(text, first, lower=low)
    while i >= 0:
        j = i + len(first)
        rest = low[j:]
        if rest.startswith(" ") and any(rest[1:].startswith(t) for t in tails):
            return i
        i = find_word(text, first, i + 1, lower=low)
    return -1


def pos_word_any_suffix(text: str, stem: str) -> int:
    """`\\bstem` with no tail boundary (intervention, intervene)."""
    return find_word(text, stem, tail_boundary=False)


def rel_positions(text: str) -> List[Tuple[int, str]]:
    low = text.lower()
    out = []

    def w(p: str) -> int:
        return find_word(text, p, lower=low)

    cues = [
        ("EQ", [w("is exactly"), w("equals"), w("equal"), w("is precisely"), pos_eq_sign(text),
                pos_phrase_then_word(text, "is", ("<math>",)), pos_phrase_then_word(text, "are", ("<math>",)),
                w("exactly")]),
        ("LE", [w("at most"), w("no more than"), low.find("<="), find_word(text, "\\le", lead_boundary=False),
                w("bounded above by"), find_word(text, "upper bound", tail_boundary=False),
                pos_phrase_then_word(text, "never", ("increase", "exceed")), find_word(text, "not exceed", tail_boundary=False)]),
        ("GE", [w("at least"), w("no fewer than"), low.find(">="), find_word(text, "\\ge", lead_boundary=False),
                w("bounded below by"), find_word(text, "lower bound", tail_boundary=False), w("requires at least")]),
        ("OPT", [w("optimal"), w("optimum"), w("minimal"), w("minimum"), w("maximal"), w("maximum"),
                 w("argmin"), w("argmax"), w("minimiser"), w("minimizer"), w("maximiser"), w("maximizer"), w("best")]),
        ("CAUSAL", [w("cause"), w("causes"), w("caused by"), w("causal"), find_word(text, "do(", tail_boundary=False),
                    pos_word_any_suffix(text, "intervention"), pos_word_any_suffix(text, "intervene")]),
        ("EXISTS", [w("exist"), w("exists"), w("there is a"), w("there is an"), w("attained")]),
    ]
    for rel, poss in cues:
        ps = [p for p in poss if p >= 0]
        if ps:
            out.append((min(ps), rel))
    return out


def rel_class(text: str) -> str:
    best = None  # type: Optional[Tuple[int, str]]
    for pos, rel in rel_positions(text):
        if best is None or pos < best[0]:
            best = (pos, rel)
    return best[1] if best else "PRED"


NEG_LEAD = ("not", "no", "never", "neither")
NEG_VERB = ("cannot", "can not", "does not", "do not", "is not", "are not", "fail to", "fails to",
            "is never", "are never", "there is no", "no longer")
DETERMINERS = ("the", "a", "an", "no", "every", "each", "its", "their", "all", "any", "some", "there", "if", "for", "it")
ROLE_VOCAB = ("necessary", "sufficient", "suffices", "requires", "needs", "only if", "iff", "if and only if",
              "necessity", "sufficiency")
INTERVENTIONAL = ("do(", "intervention", "intervene", "randomised", "randomized")


def is_negated(text: str) -> bool:
    if startswith_word(text, NEG_LEAD) is not None:
        return True
    return any(has_word(text, p) for p in NEG_VERB)


def atom(text: str) -> List[object]:
    text = text.strip().strip(",;:").strip()
    node = ["atom", text, rel_class(text)]  # type: List[object]
    return ["not", node] if is_negated(text) else node


def split_conj(text: str, word: str) -> List[str]:
    """Split at `; word ` / `, word ` followed by a determiner (word boundary)."""
    low = text.lower()
    cuts = []
    i = 0
    while i < len(low):
        if low[i] in ";,":
            j = i + 1
            while j < len(low) and low[j] == " ":
                j += 1
            if low.startswith(word + " ", j):
                k = j + len(word) + 1
                while k < len(low) and low[k] == " ":
                    k += 1
                if startswith_word(low[k:], DETERMINERS) is not None:
                    cuts.append((i, k))
                    i = k
                    continue
        i += 1
    if not cuts:
        return [text]
    parts = []
    prev = 0
    for a, b in cuts:
        parts.append(text[prev:a])
        prev = b
    parts.append(text[prev:])
    return parts


def clause(text: str) -> List[object]:
    parts = split_conj(text, "and")
    if len(parts) > 1:
        node = clause(parts[0])
        for p in parts[1:]:
            node = ["and", node, clause(p)]
        return node
    parts = split_conj(text, "or")
    if len(parts) > 1:
        node = clause(parts[0])
        for p in parts[1:]:
            node = ["or", node, clause(p)]
        return node
    return atom(text)


# ---------------------------------------------------------------------------
# sentence rules as scanner procedures (lazy-left = first separator hit)
# ---------------------------------------------------------------------------
def cut_first(s: str, seps: Tuple[str, ...], start: int = 0) -> Optional[Tuple[str, str, str]]:
    """Earliest ` sep ` (whitespace-bounded, case-insensitive) at index >= start
    with a non-empty left part; returns (left, sep, right)."""
    low = s.lower()  # a sentence-final separator never cuts (`... policy does`)
    best = None  # type: Optional[Tuple[int, str]]
    for sep in seps:
        i = low.find(" " + sep + " ", start)
        while i >= 0:
            if i >= 1 and (best is None or i < best[0]):
                best = (i, sep)
                break
            i = low.find(" " + sep + " ", i + 1)
    if best is None:
        return None
    i, sep = best
    return s[:i].rstrip(), sep, s[i + len(sep) + 2:].lstrip()


def after_prefix(s: str, prefixes: Tuple[str, ...]) -> Optional[str]:
    w = startswith_word(s, prefixes)
    if w is None:
        return None
    rest = s[len(w):]
    if not rest[:1].isspace():
        return None
    return rest.lstrip()


def first_comma_cut(s: str) -> Optional[Tuple[str, str]]:
    i = s.find(",")
    if i <= 0:
        return None
    right = s[i + 1:].lstrip()
    if not right:
        return None
    return s[:i].rstrip(), right


def var_domain(phrase: str) -> Tuple[str, str]:
    c = cut_first(phrase.strip(), ("in", "of", "with", "over", "on", "from"))
    if c:
        return c[0].strip(), c[2].strip()
    return phrase.strip(), "-"


R7_EVERY_VERBS = ("is", "are", "has", "have", "must", "can", "cannot", "requires", "satisfies", "admits", "uses",
                  "yields", "needs", "does", "equals", "lies", "belongs", "contains", "induces", "determines")
R7_NO_VERBS = ("is", "are", "has", "have", "can", "satisfies", "admits", "uses", "yields", "does", "equals",
               "determines", "contains", "recovers", "achieves", "exists")
REQUIRES_EXCLUDED = ("<MATH>", "at least", "at most", "exactly", "only", "zero", "one", "two", "no more",
                     "fewer", "more", "by")


def has_rel_cue(s: str) -> bool:
    return rel_class(s) != "PRED"


def parse_sentence(sent: str, goal: str, depth: int = 0) -> Tuple[Optional[Dict[str, object]], str]:
    s = sent.strip().rstrip(".").strip()
    if not s or depth > 6:
        return None, "NO_GRAMMAR_RULE"
    prefix = []  # type: List[List[str]]
    hyps = []  # type: List[List[object]]
    while True:
        rest = after_prefix(s, ("For",))
        if rest is not None:
            q = startswith_word(rest, ("every", "all", "each", "any"))
            if q is not None:
                body = rest[len(q):].lstrip()
                cc = first_comma_cut(body)
                if cc:
                    v, d = var_domain(cc[0])
                    prefix.append(["forall", v, d])
                    s = cc[1]
                    continue
        rest = after_prefix(s, ("There",))
        if rest is not None:
            q = startswith_word(rest, ("exists", "exist", "is an", "is a", "are"))
            if q is not None:
                body = rest[len(q):].lstrip()
                c = cut_first(body, ("such that", "with", "for which", "so that"))
                if c:
                    v, d = var_domain(c[0])
                    prefix.append(["exists", v, d])
                    s = c[2]
                    continue
        rest = after_prefix(s, ("Under", "Given", "Assuming"))
        if rest is not None:
            cc = first_comma_cut(rest)
            if cc:
                hyps.append(clause(cc[0]))
                s = cc[1]
                continue
        break
    # context + if/then
    low = s.lower()
    if startswith_word(s, ("If", "Whenever", "When")) is None:
        i = low.find(", if ")
        if i > 0:
            j = low.find(" then ", i + 5)
            if j > 0:
                ctx = s[:i]
                x = s[i + 5:j].rstrip()
                if x.endswith(","):
                    x = x[:-1].rstrip()
                y = s[j + 6:]
                hyps.append(clause(ctx))
                s = "If %s, then %s" % (x, y)
    matrix = None  # type: Optional[List[object]]
    rule = ""

    def imp(a: str, b: str) -> List[object]:
        return ["->", clause(a), clause(b)]

    c = cut_first(s, ("iff", "if and only if", "exactly when"))
    if c:
        matrix, rule = ["<->", clause(c[0]), clause(c[2])], "R1_IFF"
    if matrix is None:
        c = cut_first(s, ("is", "are"))
        while c and matrix is None:
            r = c[2]
            r2 = r[len("both "):] if r.lower().startswith("both ") else r
            if r2.lower().startswith("necessary and sufficient for "):
                matrix, rule = ["<->", clause(c[0]), clause(r2[len("necessary and sufficient for "):])], "R1_NS"
            else:
                c = cut_first(s, ("is", "are"), len(c[0]) + 1)
    if matrix is None:
        rest = after_prefix(s, ("If",))
        if rest is not None:
            low_r = rest.lower()
            j = low_r.find(" then ")
            if j > 0:
                left = rest[:j].rstrip()
                if left.endswith(","):
                    left = left[:-1].rstrip()
                matrix, rule = imp(left, rest[j + 6:]), "R2_IF_THEN"
            elif rest.lower().startswith("then "):
                pass
            else:
                cc = first_comma_cut(rest)
                if cc:
                    matrix, rule = imp(cc[0], cc[1]), "R2_IF_COMMA"
    if matrix is None:
        for lead, shape, name in (("A sufficient condition for", "rev", "R6_SUFF_COND"),
                                  ("A necessary condition for", "imp", "R5_NEC_COND")):
            if s.lower().startswith(lead.lower() + " "):
                body = s[len(lead) + 1:]
                c = cut_first(body, ("is",))
                if c:
                    r = c[2]
                    if r.lower().startswith("that "):
                        r = r[5:]
                    matrix = ["->", clause(r), clause(c[0])] if shape == "rev" else ["->", clause(c[0]), clause(r)]
                    rule = name
                    break
    if matrix is None:
        for lead in ("It suffices to", "It is sufficient to"):
            if s.lower().startswith(lead.lower() + " "):
                matrix, rule = ["->", clause(s[len(lead) + 1:]), ["atom", goal or "GOAL", rel_class(goal or "")]], "R6_IT_SUFFICES_TO"
                break
    if matrix is None:
        rest = after_prefix(s, ("Whenever", "When"))
        if rest is not None:
            cc = first_comma_cut(rest)
            if cc:
                matrix, rule = imp(cc[0], cc[1]), "R2_WHENEVER"
    if matrix is None:
        c = cut_first(s, ("implies",))
        if c:
            matrix, rule = imp(c[0], c[2]), "R2_IMPLIES"
    if matrix is None:
        c = cut_first(s, ("only if",))
        if c:
            matrix, rule = imp(c[0], c[2]), "R3_ONLY_IF"
    if matrix is None:
        c = cut_first(s, ("unless",))
        if c:
            right = clause(c[2])
            matrix = ["->", right[1] if right[0] == "not" else ["not", right], clause(c[0])]
            rule = "R4_UNLESS"
    if matrix is None:
        c = cut_first(s, ("is", "are"))
        while c and matrix is None:
            if c[2].lower().startswith("necessary for "):
                matrix, rule = ["->", clause(c[2][len("necessary for "):]), clause(c[0])], "R5_NECESSARY"
            else:
                c = cut_first(s, ("is", "are"), len(c[0]) + 1)
    if matrix is None:
        c = cut_first(s, ("requires", "needs"))
        while c and matrix is None:
            if startswith_word(c[2], REQUIRES_EXCLUDED) is None and not c[2][:1].isdigit() and not c[2].startswith("<MATH>"):
                matrix, rule = ["->", clause(c[2]), clause(c[0])], "R5_REQUIRES"
            else:
                c = cut_first(s, ("requires", "needs"), len(c[0]) + 1)
    if matrix is None:
        c = cut_first(s, ("is", "are"))
        while c and matrix is None:
            if c[2].lower().startswith("sufficient for "):
                matrix, rule = imp(c[0], c[2][len("sufficient for "):]), "R6_SUFFICIENT"
            else:
                c = cut_first(s, ("is", "are"), len(c[0]) + 1)
    if matrix is None:
        c = cut_first(s, ("suffices for",))
        if c:
            matrix, rule = imp(c[0], c[2]), "R6_SUFFICES_FOR"
    if matrix is None:
        for lead in ("It suffices that", "It is sufficient that"):
            if s.lower().startswith(lead.lower() + " "):
                matrix, rule = ["->", clause(s[len(lead) + 1:]), ["atom", goal or "GOAL", rel_class(goal or "")]], "R6_IT_SUFFICES"
                break
    if matrix is None:
        lows = s.lower()
        if not (has_word(s, "iff") or " if and only if " in lows or has_word(s, "then")):
            c = cut_first(s, ("if", "whenever", "provided that", "provided"))
            if c:
                matrix, rule = ["->", clause(c[2]), clause(c[0])], "R2_TRAIL_IF"
    if matrix is None:
        rest = after_prefix(s, ("Every", "Any", "All"))
        if rest is not None:
            c = cut_first(rest, R7_EVERY_VERBS)
            if c and c[2]:
                v, d = var_domain(c[0])
                prefix.append(["forall", v, d])
                sub, r2 = parse_sentence(c[1] + " " + c[2], goal, depth + 1)
                if sub is not None:
                    prefix.extend(sub["prefix"])
                    matrix, rule = sub["matrix"], "R7_EVERY+" + r2
        if matrix is None:
            rest = after_prefix(s, ("No",))
            if rest is not None:
                c = cut_first(rest, R7_NO_VERBS)
                if c and c[2]:
                    v, d = var_domain(c[0])
                    prefix.append(["forall", v, d])
                    sub, r2 = parse_sentence(c[1] + " " + c[2], goal, depth + 1)
                    if sub is not None:
                        prefix.extend(sub["prefix"])
                        body = sub["matrix"]
                        matrix = body[1] if body[0] == "not" else ["not", body]
                        rule = "R7_NO+" + r2
        if matrix is None:
            c = cut_first(s, ("for some",))
            if c:
                v, d = var_domain(c[2])
                prefix.append(["exists", v, d])
                sub, r2 = parse_sentence(c[0], goal, depth + 1)
                if sub is not None:
                    matrix, rule = sub["matrix"], "R8_FOR_SOME+" + r2
        if matrix is None:
            rest = after_prefix(s, ("There",))
            if rest is not None:
                q = startswith_word(rest, ("exists", "exist", "is an", "is a", "are"))
                if q is not None:
                    body = rest[len(q):].lstrip()
                    if body:
                        v, d = var_domain(body)
                        prefix.append(["exists", v, d])
                        matrix, rule = ["atom", body.strip(), "EXISTS"], "R8_THERE_EXIST_BARE"
    if matrix is None:
        if prefix or has_rel_cue(s):
            matrix = clause(s)
            rule = "R9_ATOMIC" if not prefix else "R9_ATOMIC_UNDER_PREFIX"
        else:
            return None, "NO_GRAMMAR_RULE"
    for h in reversed(hyps):
        matrix = ["->", h, matrix]
        rule = "UNDER+" + rule
    return {"prefix": prefix, "matrix": matrix}, rule


def fold_hypotheses(hyps: List[str], form: Dict[str, object]) -> Dict[str, object]:
    prefix = []  # type: List[List[str]]
    conj = []  # type: List[List[object]]
    for h in hyps:
        h = h.strip().rstrip(".").strip()
        rest = after_prefix(h, ("Let",))
        if rest is not None:
            c = cut_first(rest, ("be", "denote", "range over"))
            if c:
                prefix.append(["forall", c[0].strip(), c[2].strip()])
            else:
                v, d = var_domain(rest)
                prefix.append(["forall", v, d])
            continue
        rest = after_prefix(h, ("Fix", "Consider"))
        if rest is not None:
            v, d = var_domain(rest)
            prefix.append(["forall", v, d])
            continue
        rest = after_prefix(h, ("Suppose", "Assume", "Given"))
        if rest is not None:
            if rest.lower().startswith("that "):
                rest = rest[5:]
            conj.append(clause(rest))
            continue
        conj.append(clause(h))
    matrix = form["matrix"]
    if conj:
        ant = conj[0]
        for c in conj[1:]:
            ant = ["and", ant, c]
        matrix = ["->", ant, matrix]
    return {"prefix": prefix + list(form["prefix"]), "matrix": matrix}


def role_vocabulary(texts: List[str]) -> bool:
    joined = " ".join(texts)
    return any(has_word(joined, p) for p in ROLE_VOCAB)


def derive_form(rec: Dict[str, object]) -> Dict[str, object]:
    statement = str(rec.get("statement", ""))
    if "error" in rec or not statement:
        return {"status": "FORM_UNAVAILABLE", "form": None, "role_vocabulary": False}
    hyps, concl, trailing = hypothesis_chain(statement)
    rv = role_vocabulary(hyps + [concl or ""])
    if concl is None:
        return {"status": "FORM_UNAVAILABLE", "form": None, "role_vocabulary": rv}
    parsed, rule = parse_sentence(concl, str(rec.get("heading", "")))
    if parsed is None:
        return {"status": "FORM_UNAVAILABLE", "form": None, "role_vocabulary": rv}
    folded = fold_hypotheses(hyps, parsed)
    return {"status": "REGISTERED_MACHINE", "role_vocabulary": rv, "rule": rule,
            "form": {"prefix": folded["prefix"], "conclusion_prefix": parsed["prefix"], "matrix": folded["matrix"]}}


# ---------------------------------------------------------------------------
# canonical structure (amendment item 17)
# ---------------------------------------------------------------------------
STOP = set("""the a an and or of to in on for with by is are be as at that this these those its
their from into over under than then when where which who whom whose what any all each every
some such no not nor so if iff only also both either neither via per one two three it we our
has have had do does did can cannot may must shall will would should could let suppose assume
fix given there here they them his her he she you your yours ours mine but yet still just
""".split())


def content_tokens(text: str) -> List[str]:
    out = []
    cur = []
    low = text.lower().replace("<math>", " ")
    for c in low + " ":
        if c.isalnum() or c == "_":
            cur.append(c)
        else:
            if cur:
                t = "".join(cur)
                if len(t) >= 3 and t not in STOP:
                    out.append(t)
                cur = []
    return out


def canon(node: List[object]) -> object:
    if node[0] == "atom":
        return ["atom", content_tokens(str(node[1])), node[2]]
    if node[0] == "not":
        return ["not", canon(node[1])]
    return [node[0], canon(node[1]), canon(node[2])]


def canon_form(form: Dict[str, object]) -> object:
    return [[q for q, _, _ in form["prefix"]], canon(form["matrix"])]


# ---------------------------------------------------------------------------
# warrant + discriminators (own implementation)
# ---------------------------------------------------------------------------
FORALL_FIRST = ("fix", "for each", "for every", "for all", "for any", "given any", "arbitrary", "by induction")
EXISTS_FIRST = ("take", "choose", "construct", "exhibit", "there is", "there exist", "there exists", "there are",
                "consider the", "pick", "define", "the witness", "witnessed by", "the counterexample")
OPENING = ("Suppose", "Assume", "Let", "Given", "If", "Fix", "Consider", "Take")
SECOND_DIRECTION = ("conversely", "only if", "other direction", "for the converse", "reverse direction",
                    "the converse", "both directions", "exactly when", "if and only if", "iff")


def earliest(text: str, phrases: Tuple[str, ...], tail_boundary: bool = True) -> int:
    best = -1
    low = text.lower()
    for p in phrases:
        i = find_word(text, p, lower=low, tail_boundary=tail_boundary)
        if i >= 0 and (best < 0 or i < best):
            best = i
    return best


def let_be_arbitrary(text: str) -> int:
    low = text.lower()
    i = find_word(text, "let", lower=low)
    while i >= 0:
        j = low.find(" be arbitrary", i)
        if 0 <= j - i <= 64:
            return i
        i = find_word(text, "let", i + 1, lower=low)
    return -1


def opening_literal(first: str) -> Optional[str]:
    w = startswith_word(first, OPENING)
    if w is None:
        return None
    rest = first[len(w):]
    if not rest[:1].isspace():
        return None
    rest = rest.lstrip()
    if rest.lower().startswith("that "):
        rest = rest[5:]
    # up to [.;:] or `, then|so|and`
    end = len(rest)
    for i, c in enumerate(rest):
        if c in ".;:":
            end = i
            break
        if c == ",":
            after = rest[i + 1:].lstrip().lower()
            if startswith_word(after, ("then", "so", "and")) is not None:
                end = i
                break
    lit = rest[:end].strip()
    return lit if any(ch.isalpha() for ch in lit) else None


def second_direction(proof: str) -> bool:
    low = proof.lower()
    if any(has_word(proof, p) for p in SECOND_DIRECTION):
        return True
    a = find_word(proof, "necessity", tail_boundary=False)
    b = find_word(proof, "sufficiency", tail_boundary=False)
    return a >= 0 and b >= 0 and low.find("sufficiency", a) >= 0 or (a >= 0 and b >= 0 and low.find("necessity", b) >= 0)


def warrant_of(rec: Dict[str, object]) -> Dict[str, object]:
    proof = str(rec.get("proof", "") or "")
    w = {"first_quantifier": None, "literal": None, "polarity": None, "two": None,
         "falsifier": str(rec.get("falsifier", "") or "") or None, "evidence_mode": rec.get("evidence_mode", "UNKNOWN")}
    if not proof:
        return w
    fa = earliest(proof, FORALL_FIRST)
    lb = let_be_arbitrary(proof)
    if lb >= 0 and (fa < 0 or lb < fa):
        fa = lb
    ex = earliest(proof, EXISTS_FIRST)
    if fa >= 0 and (ex < 0 or fa <= ex):
        w["first_quantifier"] = "forall"
    elif ex >= 0:
        w["first_quantifier"] = "exists"
    sents = split_sentences(proof)
    first = sents[0] if sents else proof
    lit = opening_literal(first)
    if lit:
        w["literal"] = lit
        w["polarity"] = "neg" if is_negated(lit) else "pos"
    w["two"] = second_direction(proof)
    return w


def atoms_of(node: List[object]) -> List[List[object]]:
    if node[0] == "atom":
        return [node]
    out = []
    for ch in node[1:]:
        if isinstance(ch, list):
            out.extend(atoms_of(ch))
    return out


def side_text(node: List[object]) -> str:
    return " ".join(str(a[1]) for a in atoms_of(node))


def overlap(a: str, b: str) -> int:
    return len(set(content_tokens(a)) & set(content_tokens(b)))


def align(literal: Optional[str], matrix: List[object]) -> Optional[str]:
    if literal is None or matrix[0] not in ("->", "<->"):
        return None
    l = overlap(literal, side_text(matrix[1]))
    r = overlap(literal, side_text(matrix[2]))
    if l == r:
        return None
    return "left" if l > r else "right"


NEG_CUE = ("not", "no", "never", "cannot", "fail", "fails", "without", "violat", "differ", "exceed",
           "false", "absent", "missing", "break", "breaks", "≠")


def falsifier_negated_side(fals: Optional[str], matrix: List[object]) -> Optional[str]:
    if not fals or matrix[0] not in ("->", "<->"):
        return None
    words = fals.split()
    windows = []
    for i, wd in enumerate(words):
        lw = wd.lower()
        if any(lw.startswith(c) or lw == c for c in NEG_CUE) or "≠" in wd:
            windows.append(" ".join(words[max(0, i - 3):i + 7]))
    if not windows:
        return None
    win = " ".join(windows)
    l = overlap(win, side_text(matrix[1]))
    r = overlap(win, side_text(matrix[2]))
    if l == r:
        return None
    return "left" if l > r else "right"


def mixed(prefix: List[List[str]]) -> bool:
    qs = set(q for q, _, _ in prefix)
    return "forall" in qs and "exists" in qs


def evaluate(entries: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """entries: key -> {form, role_vocabulary, warrant, hand}"""
    queues = {r: set() for r in ROWS}  # type: Dict[str, set]
    applicable = {r: set() for r in ROWS}  # type: Dict[str, set]
    evaluable = {r: set() for r in ROWS}  # type: Dict[str, set]
    agree = {r: 0 for r in ROWS}
    for key in sorted(entries):
        e = entries[key]
        form = e["form"]
        if form is None:
            continue
        matrix = form["matrix"]
        top = matrix[0]
        hand = e.get("hand") or {}
        w = e["warrant"]
        if mixed(form["prefix"]):
            applicable["AA16"].add(key)
            wo = hand.get("outer_quantifier")
            so = form["prefix"][0][0]
            if not wo and mixed(form.get("conclusion_prefix", form["prefix"])):
                wo = w["first_quantifier"]
                so = form["conclusion_prefix"][0][0]
            if wo:
                evaluable["AA16"].add(key)
                if wo != so:
                    queues["AA16"].add((key, "PREFIX_ORDER"))
                else:
                    agree["AA16"] += 1
        if top in ("->", "<->"):
            row = "AA18" if (e["role_vocabulary"] or top == "<->") else "AA17"
            applicable[row].add(key)
            literal = None
            lit_pol = "pos"
            two = False
            if hand.get("assumes_literal"):
                literal, lit_pol, two = str(hand["assumes_literal"]), str(hand.get("literal_polarity", "pos")), bool(hand.get("two_directions", False))
            elif w["literal"]:
                literal, lit_pol, two = str(w["literal"]), str(w["polarity"]), bool(w["two"])
            side = None
            pol = None
            if literal is not None:
                side = align(literal, matrix)
                if side is not None:
                    node = matrix[1] if side == "left" else matrix[2]
                    pol = "pos" if (("neg" if node[0] == "not" else "pos") == lit_pol) else "neg"
            else:
                neg = falsifier_negated_side(w["falsifier"], matrix)
                if neg is not None:
                    side, pol, two = ("left" if neg == "right" else "right"), "pos", False
            if side is not None:
                evaluable[row].add(key)
                if row == "AA17":
                    if side == "right" and pol == "pos":
                        queues[row].add((key, "CONVERSE"))
                    elif side == "left" and pol == "neg":
                        queues[row].add((key, "INVERSE"))
                    else:
                        agree[row] += 1
                else:
                    if top == "<->":
                        if not two:
                            queues[row].add((key, "IFF_ONE_DIRECTION"))
                        else:
                            agree[row] += 1
                    elif (side == "right" and pol == "pos") or (side == "left" and pol == "neg"):
                        queues[row].add((key, "ROLE_SWAP"))
                    else:
                        agree[row] += 1
        rels = set(str(a[2]) for a in atoms_of(matrix))
        mode = str(w["evidence_mode"])
        if "OPT" in rels:
            applicable["AA20"].add(key)
            if mode not in ("UNKNOWN", "PROTOCOL_ONLY"):
                evaluable["AA20"].add(key)
                if mode in RUN_MODES:
                    queues["AA20"].add((key, "OPTIMALITY_FROM_RUN_SEARCH"))
                else:
                    agree["AA20"] += 1
        if "CAUSAL" in rels:
            applicable["AA22"].add(key)
            if mode != "UNKNOWN":
                evaluable["AA22"].add(key)
                texts = " ".join(str(a[1]) for a in atoms_of(matrix) if a[2] == "CAUSAL").lower()
                if mode in RUN_MODES and not any(m in texts for m in INTERVENTIONAL):
                    queues["AA22"].add((key, "CAUSAL_FROM_OBSERVATIONAL_RUN"))
                else:
                    agree["AA22"] += 1
    return {"queues": queues, "applicable": applicable, "evaluable": evaluable, "agree": agree}


# ---------------------------------------------------------------------------
# main: derive, compare with route A
# ---------------------------------------------------------------------------
def main() -> Dict[str, object]:
    with open(SNAPSHOT, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    with open(REGISTER, "r", encoding="utf-8") as fh:
        reg_a = json.load(fh)["entries"]
    with open(QUEUES, "r", encoding="utf-8") as fh:
        q_a = json.load(fh)
    hand = {}
    if HAND.exists():
        with open(HAND, "r", encoding="utf-8") as fh:
            hand = json.load(fh)
    records = snap["records"]
    if set(records) != set(reg_a):
        raise SystemExit("route A register keys differ from the snapshot")
    derived = {}
    form_agree = 0
    form_disagree = []
    status_disagree = []
    for key in sorted(records):
        rec = records[key]
        d = derive_form(rec)
        a = reg_a[key]
        # hand forms come from the hand file, exactly as route A takes them
        he = (hand.get("entries") or {}).get(key)
        if he and he.get("form") and a["form_status"] == "REGISTERED_HAND":
            form = {"prefix": he["form"]["prefix"], "conclusion_prefix": he["form"].get("conclusion_prefix", he["form"]["prefix"]),
                    "matrix": he["form"]["matrix"]}
            d = {"status": "REGISTERED_HAND", "form": form, "role_vocabulary": bool(he.get("role_vocabulary", False))}
        a_status = a["form_status"]
        if a_status == "REGISTERED_HAND" and d["status"] != "REGISTERED_HAND":
            status_disagree.append(key)
        elif a_status == "FORM_UNAVAILABLE" and d["status"] != "FORM_UNAVAILABLE":
            status_disagree.append(key)
        elif a_status == "REGISTERED_MACHINE" and d["status"] != "REGISTERED_MACHINE":
            status_disagree.append(key)
        elif d["form"] is not None:
            if canon_form(d["form"]) == canon_form(a["form"]) and \
                    [q for q, _, _ in d["form"]["conclusion_prefix"]] == [q for q, _, _ in a["form"].get("conclusion_prefix", a["form"]["prefix"])] \
                    and bool(d["role_vocabulary"]) == bool(a["role_vocabulary"]):
                form_agree += 1
            else:
                form_disagree.append(key)
        else:
            form_agree += 1  # both unavailable
        hw = None
        if d["form"] is not None:
            hw_src = a.get("hand_warrant")  # the hand warrant is data from the hand file; resolve its literal ourselves
            he_w = None
            if he and he.get("warrant"):
                he_w = he["warrant"]
            hwe = (hand.get("warrants") or {}).get(key)
            if hwe and hwe.get("warrant"):
                he_w = hwe["warrant"]
            if he_w:
                hw = dict(he_w)
                if hw.get("assumes_side") and d["form"]["matrix"][0] in ("->", "<->"):
                    node = d["form"]["matrix"][1] if hw["assumes_side"] == "left" else d["form"]["matrix"][2]
                    hw["assumes_literal"] = side_text(node)
                    hw["literal_polarity"] = "neg" if node[0] == "not" else "pos"
            del hw_src
        derived[key] = {"form": d["form"], "role_vocabulary": d["role_vocabulary"],
                        "warrant": warrant_of(rec) if "error" not in rec else
                        {"first_quantifier": None, "literal": None, "polarity": None, "two": None, "falsifier": None,
                         "evidence_mode": rec.get("evidence_mode", "UNKNOWN")},
                        "hand": hw}
    ev = evaluate(derived)
    queue_agree = {}
    for r in ROWS:
        a_set = set((q["key"], q["kind"]) for q in q_a["rows"][r])
        queue_agree[r] = {"route_b": len(ev["queues"][r]), "route_a": len(a_set),
                          "equal": ev["queues"][r] == a_set,
                          "only_b": sorted(x[0] for x in ev["queues"][r] - a_set),
                          "only_a": sorted(x[0] for x in a_set - ev["queues"][r]),
                          "evaluable_equal": ev["evaluable"][r] == set(q_a["evaluable"][r]),
                          "applicable_equal": ev["applicable"][r] == set(q_a["applicable"][r]),
                          "evaluable_b": len(ev["evaluable"][r]), "applicable_b": len(ev["applicable"][r]),
                          "agreeing_b": ev["agree"][r]}
    registered = sum(1 for d in derived.values() if d["form"] is not None)
    out = {
        "schema": "GMI_833_LOGICAL_FORM_ORACLE_RESULT_V1",
        "package": "gmi-833-aa-logical-form-register-v1",
        "route": "B",
        "population": len(records),
        "registered_b": registered,
        "fraction_b": str(Fraction(registered, len(records))),
        "form_agree": form_agree,
        "form_disagree": form_disagree,
        "status_disagree": status_disagree,
        "all_forms_agree": not form_disagree and not status_disagree,
        "queues": queue_agree,
        "all_queues_agree": all(v["equal"] and v["evaluable_equal"] and v["applicable_equal"] for v in queue_agree.values()),
    }
    return out


if __name__ == "__main__":
    doc = main()
    json.dump(doc, sys.stdout, indent=1, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
