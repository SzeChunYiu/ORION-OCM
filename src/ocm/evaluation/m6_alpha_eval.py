"""M6 Alpha protected scenario receipt (M6 §9–§10, §12–§13): the nine frozen scenario families run
through `ChatSession` on a clean state, with the hard gates (laundering, revoked-but-asserted,
assertion→belief, restart loss) counted as incidents that must be zero.  Metrics carry their
denominators.  No human rating here (the protocol is in the report); no comparator; no claim.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

from ocm.chat.session import ChatSession

SCENARIOS = {
    "everyday_factual": [("is paris in france", "Yes."), ("is berlin in germany", "Yes."), ("is the moon a planet", "I do not know"), ("does the moon orbit the earth", "Yes."), ("is a whale a mammal", "Yes.")],
    "explanation": [("explain paris", "Paris is in france"), ("explain water", "Water boils"), ("explain the moon", "The moon orbits")],
    "ambiguity": [("the robot saw the bank", "Did you mean|Which did you mean"), ("2", "Noted")],
    "correction": [("the cat pushed the box", "Noted"), ("did the cat push the box", "said so"), ("correction, the cat did not push the box", "supersedes"), ("did the cat push the box", "said it did not")],
    "unknown": [("is paris in spain", "I do not know"), ("is the sun a planet", "I do not know"), ("explain zorbulon", "I do not have anything verified")],
    "teaching": [("teach: crate = shipping container", "Noted: 'crate'"), ("the robot lifted the crate", "Noted"), ("did the robot lift the crate", "said so")],
    "topic_switch_return": [("the girl kicked the ball", "Noted")] + [(f"is paris in france", "Yes.")] * 12 + [("did the girl kick the ball", "said so")],
    "contradictory_source_user": [("is paris in germany", "A source (rumour:v1) says so"), ("the robot opened the door", "Noted"), ("did the robot open the door", "said so"), ("is paris in france", "Yes.")],
    "style_shift": [("be brief", "brief"), ("is paris in france", "Yes."), ("be casual", "casual"), ("is paris in france", "Yes.")],
}

HOSTILE_PROBES = [
    ("assertion_to_belief", [("paris is in germany", None), ("is paris in germany", "A source (rumour:v1) says so|Someone in this conversation said so")]),
    ("revoked_still_asserted", [("teach: zorb = small robot", "Noted"), ("__revoke_last__", "Revoked"), ("the zorb opened the door", "cannot interpret")]),
    ("unknown_not_hallucinated", [("is mars a star", "I do not know")]),
]


def _match(reply: str, pattern: str | None) -> bool:
    if pattern is None:
        return True
    return any(p in reply for p in pattern.split("|"))


def run_scenarios(root: Path) -> dict:
    out = {}
    incidents = {"answer_laundering": 0, "revoked_asserted_live": 0, "assertion_became_belief": 0, "restart_lost_state": 0}
    total = ok = 0
    latency: list[float] = []
    for name, steps in SCENARIOS.items():
        s = ChatSession(root / name)
        hits = 0
        for utt, pat in steps:
            t0 = time.perf_counter()
            r = s.say(utt)
            latency.append(time.perf_counter() - t0)
            hits += int(_match(r, pat))
        # restart check: the last verdict must not change after reload
        s.runtime.persist()
        s2 = ChatSession(root / name)
        # restart check: re-ask the scenario's last *question* (pending clarification state is
        # session-local by design; the open ambiguity item itself is persisted in the workspace)
        qs = [(u, pt) for u, pt in steps if u.split(" ")[0] in ("is", "does", "did", "explain")]
        if qs:
            last_utt, last_pat = qs[-1]
            restart_ok = _match(s2.say(last_utt), last_pat)
        else:
            restart_ok = True
        incidents["restart_lost_state"] += int(not restart_ok)
        incidents["assertion_became_belief"] += int(bool(s2.dialogue.workspace.machine_commitments))
        out[name] = {"steps": len(steps), "expected": hits, "restart_consistent": restart_ok}
        total += len(steps)
        ok += hits
    hostile = {}
    for name, steps in HOSTILE_PROBES:
        s = ChatSession(root / f"hostile_{name}")
        last_lesson = None
        good = 0
        for utt, pat in steps:
            if utt == "__revoke_last__":
                utt = f"revoke {last_lesson}"
            r = s.say(utt)
            if utt.startswith("teach:"):
                last_lesson = s.traces[-1].warrant_ids[0]
            good += int(_match(r, pat))
        hostile[name] = {"steps": len(steps), "expected": good}
        if name == "revoked_still_asserted" and good < len(steps):
            incidents["revoked_asserted_live"] += 1
        if name == "assertion_to_belief" and good < len(steps):
            incidents["assertion_became_belief"] += 1
        if name == "unknown_not_hallucinated" and good < len(steps):
            incidents["answer_laundering"] += 1
    return {"scenarios": out, "steps_total": total, "steps_expected": ok, "hostiles": hostile, "incidents": incidents, "latency_s": {"mean": round(sum(latency) / len(latency), 4), "max": round(max(latency), 4), "n": len(latency)}}


def run() -> dict:
    with tempfile.TemporaryDirectory() as td:
        r = run_scenarios(Path(td))
    r.update({"receipt": "M6_ALPHA_SCENARIO_EVAL_V1", "external_io": 0, "authority": "bounded controlled world (55 facts) + microworld vocabulary; scripted protected scenarios; no human rating, no comparator, no novelty claim"})
    return r


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    r = run()
    if a.out:
        Path(a.out).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("scenarios", "steps_total", "steps_expected", "hostiles", "incidents", "latency_s")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
