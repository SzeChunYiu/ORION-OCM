"""KSO M5 controlled chat boundary — two codecs, one internal procedure machine.

This is deliberately not open-domain language. It proves the boundary shape: two independently
implemented codecs encode the same lesson/task into the same canonical internal object; neither
codec supplies the answer; the KSO procedure store learns, composes, revokes and answers.

Exit: 0 pass; 1 failure; 2 CANNOT_CHECK.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


m3 = _load("kso_m3_learning_v1", HERE / "kso_m3_learning_v1.py")


class CodecError(ValueError):
    pass


@dataclass(frozen=True)
class TeachCommand:
    name: str
    table: tuple[int, int, int, int]


@dataclass(frozen=True)
class SolveCommand:
    name: str
    combinator: str
    x: tuple[int, int]


@dataclass(frozen=True)
class RevokeCommand:
    name: str


@dataclass(frozen=True)
class ReinstateCommand:
    name: str


@dataclass(frozen=True)
class FeedbackCommand:
    name: str
    verdict: str


Command = TeachCommand | SolveCommand | RevokeCommand | ReinstateCommand | FeedbackCommand


def command_payload(c: Command) -> dict:
    d = {"kind": type(c).__name__}
    if isinstance(c, TeachCommand):
        d |= {"name": c.name, "table": list(c.table)}
    elif isinstance(c, SolveCommand):
        d |= {"name": c.name, "combinator": c.combinator, "input": list(c.x)}
    elif isinstance(c, (RevokeCommand, ReinstateCommand)):
        d |= {"name": c.name}
    else:
        d |= {"name": c.name, "verdict": c.verdict}
    return d


def command_digest(c: Command) -> str:
    return hashlib.sha256(json.dumps(command_payload(c), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evidence_id(c: TeachCommand) -> int:
    return int(command_digest(c)[:12], 16)


class TextCodec:
    codec_id = "text-v1"

    def parse(self, text: str) -> Command:
        toks = text.strip().split()
        if not toks:
            raise CodecError("EMPTY")
        k = toks[0].lower()
        if k == "teach":
            if len(toks) != 7 or toks[2].lower() != "where":
                raise CodecError("BAD_TEACH")
            mapping = {}
            for token in toks[3:]:
                if "=" not in token:
                    raise CodecError("BAD_TEACH")
                key, val = token.split("=", 1)
                if key not in ("00", "01", "10", "11") or val not in ("0", "1"):
                    raise CodecError("BAD_TEACH")
                mapping[key] = int(val)
            if set(mapping) != {"00", "01", "10", "11"}:
                raise CodecError("INCOMPLETE_TEACH")
            return TeachCommand(toks[1].upper(), tuple(mapping[k] for k in ("00", "01", "10", "11")))
        if k == "solve":
            if len(toks) != 5 or toks[3].lower() != "on":
                raise CodecError("BAD_SOLVE")
            if toks[1].upper() not in m3.PROGRAMS:
                raise CodecError("UNKNOWN_COMBINATOR")
            bits = toks[4]
            if len(bits) != 2 or any(c not in "01" for c in bits):
                raise CodecError("BAD_INPUT")
            return SolveCommand(toks[2].upper(), toks[1].upper(), (int(bits[0]), int(bits[1])))
        if k == "revoke" and len(toks) == 2:
            return RevokeCommand(toks[1].upper())
        if k == "reinstate" and len(toks) == 2:
            return ReinstateCommand(toks[1].upper())
        if k == "feedback" and len(toks) == 3:
            return FeedbackCommand(toks[1].upper(), toks[2].lower())
        raise CodecError("UNKNOWN_COMMAND")

    def render(self, response: dict) -> str:
        if response["status"] == "PASS":
            return f"Result: {response['result']}."
        if response["status"] == "LEARNED":
            return f"Learned {response['name']} as a warranted reusable procedure."
        if response["status"] == "FEEDBACK_RECORDED_UNWARRANTED":
            return f"Feedback recorded for {response['name']}; it did not create procedure warrant."
        return response["status"]


class JsonCodec:
    codec_id = "json-v1"

    def parse(self, text: str) -> Command:
        try:
            d = json.loads(text)
        except Exception as exc:
            raise CodecError("BAD_JSON") from exc
        if not isinstance(d, dict) or "kind" not in d:
            raise CodecError("BAD_JSON")
        if "answer" in d or "result" in d:
            raise CodecError("CODEC_ATTEMPTED_TO_SUPPLY_ANSWER")
        k = d["kind"]
        if k == "teach":
            if set(d) != {"kind", "name", "table"}:
                raise CodecError("EXTRA_FIELDS")
            t = tuple(d["table"])
            if len(t) != 4 or any(x not in (0, 1) for x in t):
                raise CodecError("BAD_TABLE")
            return TeachCommand(str(d["name"]).upper(), t)
        if k == "solve":
            if set(d) != {"kind", "name", "combinator", "input"}:
                raise CodecError("EXTRA_FIELDS")
            x = tuple(d["input"])
            if len(x) != 2 or any(v not in (0, 1) for v in x):
                raise CodecError("BAD_INPUT")
            c = str(d["combinator"]).upper()
            if c not in m3.PROGRAMS:
                raise CodecError("UNKNOWN_COMBINATOR")
            return SolveCommand(str(d["name"]).upper(), c, x)
        if k == "revoke" and set(d) == {"kind", "name"}:
            return RevokeCommand(str(d["name"]).upper())
        if k == "reinstate" and set(d) == {"kind", "name"}:
            return ReinstateCommand(str(d["name"]).upper())
        if k == "feedback" and set(d) == {"kind", "name", "verdict"}:
            return FeedbackCommand(str(d["name"]).upper(), str(d["verdict"]).lower())
        raise CodecError("BAD_COMMAND")

    def render(self, response: dict) -> str:
        return json.dumps(response, sort_keys=True, separators=(",", ":"))


class ChatMachine:
    def __init__(self):
        self.store = m3.ProcedureStore()
        self.evidence_by_name: dict[str, int] = {}

    def execute(self, c: Command) -> dict:
        if isinstance(c, TeachCommand):
            eid = evidence_id(c)
            lesson = m3.Lesson(c.name, m3.Channel.INSTRUCTION, eid, declared_table=c.table)
            rec = m3.learn_instruction(lesson)
            if rec.learned is None or not self.store.admit(rec):
                return {"status": "CANNOT_CHECK_LESSON", "name": c.name}
            self.evidence_by_name[c.name] = eid
            return {
                "status": "LEARNED",
                "name": c.name,
                "evidence_id": eid,
                "procedure_digest": hashlib.sha256(bytes(c.table)).hexdigest(),
            }
        if isinstance(c, SolveCommand):
            st, val = self.store.run(c.name, c.combinator, c.x)
            return {"status": st, "name": c.name, "combinator": c.combinator, "input": list(c.x), "result": val}
        if isinstance(c, RevokeCommand):
            if c.name not in self.evidence_by_name:
                return {"status": "GAP_UNKNOWN_PROCEDURE", "name": c.name}
            self.store.revoke(self.evidence_by_name[c.name])
            return {"status": "REVOKED", "name": c.name}
        if isinstance(c, ReinstateCommand):
            if c.name not in self.evidence_by_name:
                return {"status": "GAP_UNKNOWN_PROCEDURE", "name": c.name}
            self.store.reinstate(self.evidence_by_name[c.name])
            return {"status": "REINSTATED", "name": c.name}
        if isinstance(c, FeedbackCommand):
            self.store.utility_feedback[c.name] = self.store.utility_feedback.get(c.name, 0) + 1
            lesson = m3.Lesson(
                c.name,
                m3.Channel.FEEDBACK,
                0,
                endpoint_feedback=(("chat", 1 if c.verdict == "success" else 0),),
            )
            rec = m3.learn_feedback(lesson)
            assert rec.learned is None and not rec.warranted
            return {"status": "FEEDBACK_RECORDED_UNWARRANTED", "name": c.name}
        raise AssertionError


def run_m5() -> dict[str, object]:
    text = TextCodec()
    js = JsonCodec()
    tlesson = "teach AND where 00=0 01=0 10=0 11=1"
    jlesson = '{"kind":"teach","name":"AND","table":[0,0,0,1]}'
    tq = "solve NOT AND on 11"
    jq = '{"kind":"solve","name":"AND","combinator":"NOT","input":[1,1]}'
    assert command_digest(text.parse(tlesson)) == command_digest(js.parse(jlesson))
    assert command_digest(text.parse(tq)) == command_digest(js.parse(jq))

    pre_machine = ChatMachine()
    pre = pre_machine.execute(text.parse(tq))
    assert pre["status"] == "GAP_UNKNOWN_PROCEDURE"

    mt = ChatMachine()
    mj = ChatMachine()
    rt = mt.execute(text.parse(tlesson))
    rj = mj.execute(js.parse(jlesson))
    assert rt["procedure_digest"] == rj["procedure_digest"] and rt["evidence_id"] == rj["evidence_id"]
    at = mt.execute(text.parse(tq))
    aj = mj.execute(js.parse(jq))
    assert at["status"] == aj["status"] == "PASS" and at["result"] == aj["result"] == 0

    mix = ChatMachine()
    r1 = mix.execute(text.parse(tlesson))
    r2 = mix.execute(js.parse(jq))
    assert r2["result"] == 0
    r3 = mix.execute(text.parse("revoke AND"))
    r4 = mix.execute(js.parse(jq))
    assert r4["status"] == "GAP_REVOKED_PROCEDURE"
    r5 = mix.execute(js.parse('{"kind":"reinstate","name":"AND"}'))
    r6 = mix.execute(text.parse("solve XOR_A AND on 11"))
    assert r6["status"] == "PASS" and r6["result"] == 0

    fb = ChatMachine()
    fr = fb.execute(text.parse("feedback AND success"))
    fq = fb.execute(text.parse(tq))
    assert fr["status"] == "FEEDBACK_RECORDED_UNWARRANTED" and fq["status"] == "GAP_UNKNOWN_PROCEDURE"

    injection = 0
    try:
        js.parse('{"kind":"solve","name":"AND","combinator":"NOT","input":[1,1],"answer":0}')
    except CodecError as exc:
        assert str(exc) == "CODEC_ATTEMPTED_TO_SUPPLY_ANSWER"
        injection = 1
    assert injection == 1

    transcript = [
        {"speaker": "user", "text": tq, "machine": pre},
        {"speaker": "user", "text": tlesson, "machine": r1},
        {"speaker": "user", "text": jq, "machine": r2},
        {"speaker": "user", "text": "revoke AND", "machine": r3},
        {"speaker": "user", "text": jq, "machine": r4},
        {"speaker": "user", "text": '{"kind":"reinstate","name":"AND"}', "machine": r5},
        {"speaker": "user", "text": "solve XOR_A AND on 11", "machine": r6},
    ]
    return {
        "terminal": "M5_CONTROLLED_CODEC_CHAT_GREEN",
        "translator_invariance": {
            "lesson_digest_equal": True,
            "task_digest_equal": True,
            "procedure_digest_equal": True,
            "answer_equal": True,
        },
        "chat": {
            "prelesson_gap": pre["status"],
            "learned": r1["status"],
            "answer_after_lesson": r2["result"],
            "answer_after_revocation": r4["status"],
            "answer_after_reinstatement": r6["result"],
        },
        "feedback_false_warrant": 0,
        "codec_answer_injection_rejected": injection,
        "transcript": transcript,
        "authority": {
            "open_domain_chat": False,
            "human_level_language": False,
            "novelty": False,
            "M6": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out")
    a = p.parse_args(argv)
    try:
        r = run_m5()
        if a.out:
            Path(a.out).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
        print(json.dumps(r, sort_keys=True))
        return 0
    except CodecError as exc:
        print(json.dumps({"terminal": "FAIL", "reason": str(exc)}))
        return 1
    except Exception as exc:
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
