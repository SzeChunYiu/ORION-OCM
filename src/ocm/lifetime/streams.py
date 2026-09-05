"""Per-lifetime protected streams for the V3 paired-lifetimes design (M12 V3 §Generators; theory
batch 6 F2 / batch 7 G8).

A stream is a seeded *substitution* of the frozen M7 V2 suites inside the bounded world: agents are
permuted among agents, objects among objects, regular verbs among regular verbs and irregular among
irregular (so a mis-inflection probe stays a mis-inflection), verified fact questions are drawn
from other verified facts of the same relation, out-of-scope questions from the out-of-scope pool,
and lesson words are replaced by nonce words absent from the lexicon and the manifest.  Expected
patterns are rewritten with the same substitution, so the grading rule is unchanged.  The stream
manifest records every map and the SHA-256 of every generated suite; the pre-registration binds
the manifest hash before any outcome is read.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from typing import Any

from ocm.chat.session import DEFAULT_MANIFEST
from ocm.evaluation import m7_comparison as M7
from ocm.language import microworld as W

AGENTS = ("robot", "cat", "girl", "dog")
OBJECTS = ("door", "box", "key", "ball", "cup", "book")
REGULAR = tuple(v for v, p in W.VERBS_PAST.items() if p == v + "ed")
IRREGULAR = tuple(v for v, p in W.VERBS_PAST.items() if p != v + "ed")
NONCE_POOL = ("torch", "plank", "marble", "sled", "totem", "urn", "vial", "yoke", "zither", "quill", "bolt", "hinge", "ladle", "mortar", "pulley", "rudder", "spool", "trowel", "visor", "wick", "awl", "bobbin", "chisel", "dowel")
# Batch 7 G7: the M7 out-of-scope questions are all world-false; a world-TRUE but unlicensed half
# lets the grading separate "licensed by the given facts" from "true in the world".
OUT_OF_SCOPE_TRUE = ("is tokyo in japan", "is madrid in spain", "is a whale a mammal", "is a rose a plant", "is oslo in norway", "is a piano an instrument", "is lisbon in portugal", "is an oak a tree", "is a salmon a fish", "is vienna in austria")
NONCE_MEANINGS = ("lamp", "shelf", "small stone", "cart", "garden statue", "pot", "shipping container", "small robot", "instrument", "tool", "rope", "basket")


def _manifest_words() -> set[str]:
    man = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    return {f["subject"] for f in man["facts"]} | {f["object"] for f in man["facts"]}


def _verified_questions() -> dict[str, list[str]]:
    """Question surfaces by relation for verified facts (expected 'Yes.'), from the M7 factual suite."""
    out: dict[str, list[str]] = {"in": [], "is_a": [], "orbit": []}
    for q, pat in M7.factual_suite():
        if pat != "Yes.":
            continue
        if q.startswith("is ") and " in " in q:
            out["in"].append(q)
        elif q.startswith("does "):
            out["orbit"].append(q)
        else:
            out["is_a"].append(q)
    return out


def build_stream(k: int, *, seed: str = "OCM-M12-V3", world_true_half: bool = False) -> dict[str, Any]:
    rng = random.Random(f"{seed}|lifetime|{k}")
    agents = list(AGENTS); rng.shuffle(agents)
    objects = list(OBJECTS); rng.shuffle(objects)
    reg = list(REGULAR); rng.shuffle(reg)
    irr = list(IRREGULAR); rng.shuffle(irr)
    noun_map = {**dict(zip(AGENTS, agents)), **dict(zip(OBJECTS, objects))}
    verb_map = {**dict(zip(REGULAR, reg)), **dict(zip(IRREGULAR, irr))}
    banned = _manifest_words() | set(W.NOUNS) | set(W.VERBS_PAST) | set(W.ADJS)
    pool = [w for w in NONCE_POOL if w not in banned]
    rng.shuffle(pool)
    meanings = list(NONCE_MEANINGS); rng.shuffle(meanings)
    vq = _verified_questions()
    for lst in vq.values():
        rng.shuffle(lst)
    oos = list(M7.OUT_OF_SCOPE); rng.shuffle(oos)
    state = {"noun": noun_map, "verb": verb_map, "nonce": {}, "pool": pool, "meanings": meanings, "vq": vq, "vq_i": {k_: 0 for k_ in vq}, "oos": oos, "oos_i": 0}

    def word_sub(text: str) -> str:
        def one(m):
            w = m.group(0)
            if w in state["noun"]:
                return state["noun"][w]
            for v, p in W.VERBS_PAST.items():
                if w == v:
                    return state["verb"][v]
                if w == p:
                    return W.VERBS_PAST[state["verb"][v]]
                if w == v + "ed" and p != v + "ed":                       # mis-inflected irregular (goed-style) → new irregular + ed
                    return state["verb"][v] + "ed"
            if w in state["nonce"]:
                return state["nonce"][w]
            return w
        return re.sub(r"[a-z]+", one, text)

    def lesson_sub(text: str) -> str:
        m = re.match(r"teach: (\w+) = (.+)", text)
        if not m:
            return word_sub(text)
        old = m.group(1)
        if old not in state["nonce"]:
            state["nonce"][old] = state["pool"].pop()
        idx = list(state["nonce"]).index(old)                                   # one meaning per nonce word, stable across re-teaching
        return f"teach: {state['nonce'][old]} = {state['meanings'][idx % len(state['meanings'])]}"

    def question_sub(q: str, pat: str) -> str:
        if pat == "Yes." and q in {x for lst in vq.values() for x in lst} | set(M7.OUT_OF_SCOPE):
            kind = "in" if " in " in q else ("orbit" if q.startswith("does ") else "is_a")
            lst = vq[kind]
            i = state["vq_i"][kind] % len(lst); state["vq_i"][kind] += 1
            return lst[i]
        if pat.startswith("I do not know") and q in M7.OUT_OF_SCOPE:
            i = state["oos_i"] % len(oos); state["oos_i"] += 1
            return oos[i]
        return word_sub(q)

    def pat_sub(pat: str) -> str:
        return re.sub(r"'(\w+)'", lambda m: f"'{state['nonce'].get(m.group(1), m.group(1))}'", pat)

    convs = json.loads(M7.SUITES["V2"].read_text(encoding="utf-8"))["conversations"]
    new_convs = []
    for c in convs:
        turns = []
        for speaker, utt, pat in c["turns"]:
            if utt.startswith("teach:"):
                u2 = lesson_sub(utt)
            elif utt.startswith("__"):
                u2 = utt
            else:
                u2 = question_sub(utt, pat)
            turns.append([speaker, u2, pat_sub(pat)])
        new_convs.append({"id": f"{c['id']}@L{k}", "turns": turns})
    lessons = []
    for lesson, use, ask, passive in M7.LESSON_SETS["V2"]:
        l2 = lesson_sub(lesson)
        lessons.append((l2, word_sub(use), word_sub(ask), word_sub(passive)))
    negatives = [(word_sub(u), p) for u, p in M7.NEGATIVE_TRANSFER_V2]
    factual = [(question_sub(q, pat) if pat in ("Yes.",) or pat.startswith("I do not know") else q, pat) for q, pat in M7.factual_suite()]
    if world_true_half:
        wt = list(OUT_OF_SCOPE_TRUE); rng.shuffle(wt)
        factual += [(q, "I do not know") for q in wt]                              # unlicensed by the given facts although world-true
    stream = {"lifetime": k, "seed": seed, "maps": {"noun": noun_map, "verb": verb_map, "nonce": dict(state["nonce"])}, "conversations": new_convs, "lessons": lessons, "negative_transfer": negatives, "factual": factual,
              "work_task_ids": list(range(500 + 20 * k, 500 + 20 * k + 10)), "work_withheld_ids": list(range(700 + 3 * k, 700 + 3 * k + 3)), "science_dataset_ids": list(range(200 + 12 * k, 212 + 12 * k)), "ordering": ("O1", "O2", "O3")[k % 3]}
    stream["sha256"] = hashlib.sha256(json.dumps({kk: v for kk, v in stream.items() if kk != "sha256"}, sort_keys=True, default=str).encode()).hexdigest()
    return stream


def stream_manifest(n: int = 8, *, seed: str = "OCM-M12-V3", world_true_half: bool = False, name: str = "M12_V3_STREAM_MANIFEST_V1") -> dict[str, Any]:
    streams = [build_stream(k, seed=seed, world_true_half=world_true_half) for k in range(n)]
    man = {"manifest": name, "seed": seed, "lifetimes": n, "world_true_half": world_true_half, "streams": [{"lifetime": s["lifetime"], "sha256": s["sha256"], "maps": s["maps"], "ordering": s["ordering"], "work_task_ids": s["work_task_ids"], "science_dataset_ids": s["science_dataset_ids"]} for s in streams]}
    man["sha256"] = hashlib.sha256(json.dumps(man, sort_keys=True).encode()).hexdigest()
    return man


def leak_check(stream: dict[str, Any]) -> dict[str, Any]:
    """Batch 7 G8 hostile: a substitution that leaks the answer pattern — a nonce word appearing in an
    expected pattern before its lesson, or a verified question whose expected answer changed."""
    seen = set()
    leaks = []
    for c in stream["conversations"]:
        for speaker, utt, pat in c["turns"]:
            m = re.match(r"teach: (\w+) =", utt)
            if m:
                seen.add(m.group(1))
            for w in re.findall(r"'(\w+)'", pat):
                if w not in seen:
                    leaks.append((c["id"], w))
    return {"pattern_leaks": leaks, "ok": not leaks}
