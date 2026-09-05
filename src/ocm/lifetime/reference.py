"""Reference arms (issue #14 §10; theory batch 6 F8).

A reference arm is a pretrained language model given the *same task text* the OCM receives: the
bounded-world manifest, the lessons, the corrections and the questions.  Its pretraining exposure
is an information channel nobody can bind, so by F8 it is labelled `REFERENCE` and reported beside
the D1 decision — never inside the claim tiers, never as a matched comparator.

`OllamaReferenceArm` talks to a local open-weight model through the Ollama HTTP API (temperature
0, fixed seed, pinned model tag and digest recorded in the receipt).  Replies are graded
semantically (yes / no / unknown / clarify / other) by `classify`, not by the OCM realiser's surface
patterns, so the reference arm is measured on the families whose expected answer is a proposition:
factual in-scope (Yes), honest unknown (I do not know), post-deployment lessons (unknown → yes →
unknown after revocation → yes after relearning), negative-transfer probes (unknown or clarify).
The M7 conversation suite is graded by OCM surface patterns and is not a fair reference measure;
it is recorded as NOT_MEASURED for reference arms.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path
from typing import Any

from ocm.evaluation import m7_comparison as M7
from ocm.chat.session import DEFAULT_MANIFEST

INFORMATION_BINDING = "UNBOUND_PRETRAINING (F8): reference only; not a matched comparator; excluded from claim tiers and from the D1 decision"

SYSTEM = (
    "You are answering questions about a small closed world. Use ONLY the facts and lessons given to you in this conversation; "
    "facts marked (verified) are true; facts marked (unverified source) were asserted by a source but not verified; facts marked (rumour) come from an unreliable source. "
    "If a question is not settled by the given facts and lessons, answer exactly: I do not know. "
    "If a statement uses a word you were not taught and that is not in the facts, answer exactly: I cannot interpret this. "
    "If a statement is ambiguous between two meanings, ask exactly: Did you mean ... ? "
    "Answer yes/no questions with exactly Yes. or No. (add nothing else). A lesson has the form 'teach: word = meaning'; after a lesson, use the word. "
    "If a lesson is revoked, forget it and answer as if it had never been given."
)


def manifest_facts() -> list[str]:
    man = json.loads(Path(DEFAULT_MANIFEST).read_text(encoding="utf-8"))
    out = []
    for f in man["facts"]:
        tag = "(verified)" if f.get("verified_by") else ("(rumour)" if any("rumour" in s for s in f.get("sources", [])) else "(unverified source)")
        rel = {"LOCATED_IN": "is in", "IS_A": "is a", "ORBITS": "orbits"}.get(f["relation"], f["relation"].lower().replace("_", " "))
        out.append(f"{f['subject']} {rel} {f['object']} {tag}")
    return out


class OllamaReferenceArm:
    name = "reference_ollama"

    def __init__(self, model: str, host: str = "http://127.0.0.1:11434", seed: int = 1):
        self.model, self.host, self.seed = model, host, seed
        self.history: list[dict[str, str]] = []
        self.calls = 0
        self.tokens = 0
        self.wall = 0.0
        self.facts = manifest_facts()
        self.lessons: list[str] = []
        self.digest = self._digest()

    def _digest(self) -> str | None:
        try:
            req = urllib.request.Request(f"{self.host}/api/show", data=json.dumps({"model": self.model}).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            return (d.get("details", {}) or {}).get("digest") or d.get("digest") or d.get("modified_at")
        except Exception:  # noqa: BLE001
            return None

    def _context(self) -> str:
        return "FACTS:\n" + "\n".join(self.facts) + ("\nLESSONS:\n" + "\n".join(self.lessons) if self.lessons else "")

    def say(self, utt: str) -> str:
        if utt == "__restart__":
            self.history = []                                # the context (facts + lessons) is re-sent; the chat history is not
            return "restarted"
        if utt.startswith("teach:"):
            self.lessons.append(utt)
        if utt.startswith("revoke "):
            name = utt[len("revoke "):].strip()
            self.lessons = [l for l in self.lessons if not l.startswith(f"teach: {name} ")]
            self.lessons.append(f"(revoked: the lesson about '{name}' no longer holds)")
        msgs = [{"role": "system", "content": SYSTEM + "\n\n" + self._context()}] + self.history[-12:] + [{"role": "user", "content": utt}]
        body = {"model": self.model, "stream": False, "options": {"temperature": 0, "seed": self.seed, "num_predict": 60}, "messages": msgs}
        req = urllib.request.Request(f"{self.host}/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read())
        self.wall += time.perf_counter() - t0
        self.calls += 1
        self.tokens += int(d.get("eval_count", 0)) + int(d.get("prompt_eval_count", 0))
        reply = (d.get("message", {}) or {}).get("content", "").strip()
        self.history += [{"role": "user", "content": utt}, {"role": "assistant", "content": reply}]
        return reply

    def info(self) -> dict:
        return {"model": self.model, "digest": self.digest, "facts_in_prompt": len(self.facts), "lessons": len(self.lessons), "information_binding": INFORMATION_BINDING}

    def resources(self) -> dict:
        return {"calls": self.calls, "tokens": self.tokens, "wall_s": round(self.wall, 2), "external_io": 0}


def classify(reply: str) -> str:
    r = reply.strip().lower()
    if r.startswith("yes"):
        return "yes"
    if r.startswith("no") and not r.startswith("not"):
        return "no"
    if "do not know" in r or "don't know" in r or "unknown" in r or "not settled" in r or "cannot tell" in r:
        return "unknown"
    if "cannot interpret" in r or "not taught" in r or "unfamiliar" in r:
        return "uninterpretable"
    if "did you mean" in r or r.endswith("?"):
        return "clarify"
    return "other"


def _expect(pat: str) -> set[str]:
    """Map an M7 surface pattern to the semantic classes that satisfy it."""
    if pat == "Yes.":
        return {"yes"}
    if pat.startswith("I do not know"):
        return {"unknown"}
    if "source" in pat or "says so" in pat:
        return {"yes", "unknown"}                             # an unverified assertion may be reported or declined
    if "cannot interpret" in pat:
        return {"uninterpretable", "unknown", "clarify"}
    if "Did you mean" in pat:
        return {"clarify", "yes", "unknown"}
    return {"other"}


def phase_A_reference(arm: OllamaReferenceArm) -> dict[str, Any]:
    M7.CONVS = M7.SUITES["V2"]
    M7.LESSONS = M7.LESSON_SETS["V2"]
    M7.NEGATIVE_TRANSFER = M7.NEGATIVE_TRANSFER_V2
    fin, unk, log = [], [], []
    for q, pat in M7.factual_suite():
        r = arm.say(q)
        ok = classify(r) in _expect(pat)
        (unk if pat == "I do not know" else fin).append(ok)
        log.append((q, r[:80], pat, ok))
    steps = {"baseline_unknown": [], "acquired": [], "compositional_reuse": [], "retained_after_restart": [], "revoked_stops": [], "unrelated_intact": [], "relearned": []}
    for lesson, use, ask, passive in M7.LESSONS:
        name = lesson[len("teach:"):].split("=")[0].strip()
        steps["baseline_unknown"].append(classify(arm.say(use)) in {"uninterpretable", "unknown", "clarify"})
        arm.say(lesson)
        arm.say(use)
        steps["acquired"].append(classify(arm.say(ask)) == "yes")
        steps["compositional_reuse"].append(classify(arm.say(passive)) in {"yes", "other"})
        arm.say("__restart__")
        steps["retained_after_restart"].append(classify(arm.say(ask)) == "yes")
        arm.say(f"revoke {name}")
        steps["revoked_stops"].append(classify(arm.say(use)) in {"uninterpretable", "unknown"})
        steps["unrelated_intact"].append(classify(arm.say("is paris in france")) == "yes")
        arm.say(lesson)
        steps["relearned"].append(classify(arm.say(ask)) == "yes")
    arm.say("the robot opened the door")
    neg = [classify(arm.say(u)) in _expect(pat) for u, pat in M7.NEGATIVE_TRANSFER]
    always = sum(1 for ok in unk if not ok)
    return {"factual_in_scope": fin, "honest_unknown": unk, "post_deployment": steps, "negative_transfer": neg, "conversations": "NOT_MEASURED (graded by OCM surface patterns)", "always_attempts": always, "log": log[:12]}
