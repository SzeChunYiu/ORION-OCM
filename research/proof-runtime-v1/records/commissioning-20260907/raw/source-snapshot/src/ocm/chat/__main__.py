"""`python -m ocm.chat` — the Conversational OCM Alpha (M6 §1).

    python -m ocm.chat [--state PATH] [--new-session] [--diagnostic] [--seed S]
                       [--knowledge-manifest PATH] [--resource-budget N] [--demo] [--script FILE]

Normal mode prints only the machine's replies.  Diagnostic mode prints, after each turn, the
structured trace assembled from the runtime's actual events (interpretation candidates, dialogue
state, active KSO objects, operators, checks, response plan, sentence plan, warrant ids, resource
summary, committed response).  `--demo` runs the deterministic scripted Alpha demonstration
(M6 §15) and exits; `--script FILE` runs one utterance per line.  External IO is zero.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .session import ChatSession, DEFAULT_MANIFEST

DEMO_SCRIPT = [
    ("1 normal multi-turn conversation", "the robot opened the door"),
    ("", "did the robot open the door"),
    ("2 follow-up / reference", "the cat pushed the box"),
    ("", "which box did it push"),
    ("3 explanation", "explain paris"),
    ("", "is paris in france"),
    ("4 consequential ambiguity → clarification", "the robot saw the bank"),
    ("", "2"),
    ("5 genuine unknown → honest unknown", "is paris in spain"),
    ("", "is paris in germany"),
    ("6 learn a new word", "teach: crate = shipping container"),
    ("7 reuse it compositionally", "the robot lifted the crate"),
    ("", "did the robot lift the crate"),
    ("8 restart process and retain it", "__restart__"),
    ("", "did the robot lift the crate"),
    ("9 revoke evidence and observe the change", "__revoke_last_lesson__"),
    ("", "the robot lifted the crate"),
    ("10 unrelated knowledge intact", "is berlin in germany"),
    ("11 diagnostic trace", "__trace__"),
]


def run_demo(state: Path, diagnostic: bool) -> int:
    if state.exists():
        shutil.rmtree(state)
    s = ChatSession(state, diagnostic=diagnostic)
    lesson_evidence: str | None = None
    for label, utt in DEMO_SCRIPT:
        if label:
            print(f"\n## {label}")
        if utt == "__restart__":
            s.runtime.persist()
            s = ChatSession(state, diagnostic=diagnostic)
            print("[process restarted; state reloaded from disk]")
            continue
        if utt == "__revoke_last_lesson__":
            utt = f"revoke {lesson_evidence}" if lesson_evidence else "revoke ev:none"
        if utt == "__trace__":
            print(json.dumps(s.last_trace(), indent=1)[:2500])
            continue
        print(f"user> {utt}")
        reply = s.say(utt)
        print(f"ocm>  {reply}")
        if utt.startswith("teach:"):
            lesson_evidence = s.traces[-1].warrant_ids[0] if s.traces[-1].warrant_ids else None
        if diagnostic:
            print(json.dumps(s.last_trace(), indent=1)[:1200])
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m ocm.chat")
    p.add_argument("--state", default="ocm_alpha_state")
    p.add_argument("--new-session", action="store_true")
    p.add_argument("--diagnostic", action="store_true")
    p.add_argument("--seed", default="OCM-ALPHA")
    p.add_argument("--knowledge-manifest", default=str(DEFAULT_MANIFEST))
    p.add_argument("--resource-budget", type=int, default=0)
    p.add_argument("--demo", action="store_true")
    p.add_argument("--script", default=None)
    a = p.parse_args(argv)
    state = Path(a.state)
    if a.demo:
        return run_demo(state, a.diagnostic)
    if a.new_session and state.exists():
        shutil.rmtree(state)
    s = ChatSession(state, diagnostic=a.diagnostic, manifest=Path(a.knowledge_manifest))
    lines = Path(a.script).read_text(encoding="utf-8").splitlines() if a.script else None
    print("Conversational OCM Alpha — bounded world; type 'quit' to exit.")
    while True:
        try:
            line = lines.pop(0) if lines is not None else input("user> ")
        except (EOFError, IndexError):
            break
        if line.strip().lower() in ("quit", "exit"):
            break
        if not line.strip():
            continue
        if lines is not None:
            print(f"user> {line}")
        print(f"ocm>  {s.say(line)}")
        if a.diagnostic:
            print(json.dumps(s.last_trace(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
