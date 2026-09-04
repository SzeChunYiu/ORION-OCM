"""Runnable KSO learning/chat demonstration.

Default mode prints a deterministic transcript. `--interactive` accepts either text-v1 commands or
json-v1 commands on stdin; lines beginning with "{" use the JSON codec, others use the text codec.

This is the controlled M5 Boolean-procedure domain, not open-domain chat.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load():
    name = "kso_m5_chat_v1"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / "kso_m5_chat_v1.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("kso_m5_chat_v1.py missing")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


m5 = _load()
SCRIPT = (
    "solve NOT AND on 11",
    "teach AND where 00=0 01=0 10=0 11=1",
    '{"kind":"solve","name":"AND","combinator":"NOT","input":[1,1]}',
    "revoke AND",
    "solve NOT AND on 11",
    '{"kind":"reinstate","name":"AND"}',
    "solve XOR_A AND on 11",
)


def choose_codec(line):
    return m5.JsonCodec() if line.lstrip().startswith("{") else m5.TextCodec()


def respond(machine, line):
    codec = choose_codec(line)
    cmd = codec.parse(line)
    r = machine.execute(cmd)
    return m5.TextCodec().render(r), r


def run_script(lines=SCRIPT):
    machine = m5.ChatMachine()
    out = []
    for line in lines:
        rendered, raw = respond(machine, line)
        out.append({"user": line, "kso": rendered, "receipt": raw})
    return out


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--interactive", action="store_true")
    a = p.parse_args(argv)
    machine = m5.ChatMachine()
    if a.interactive:
        for raw in sys.stdin:
            line = raw.strip()
            if not line:
                continue
            if line.lower() in {"quit", "exit"}:
                break
            try:
                rendered, receipt = respond(machine, line)
                print(rendered)
                print("receipt:", json.dumps(receipt, sort_keys=True))
            except Exception as exc:
                print(f"ERROR {type(exc).__name__}: {exc}")
        return 0
    for row in run_script():
        print(f"> {row['user']}")
        print(row["kso"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
