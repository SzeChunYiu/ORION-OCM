"""Declared bounded task-language seed; no learned-English or parser claim."""
from __future__ import annotations

import re
import hashlib
from pathlib import Path

from clia_grammar import GRAMMAR, dump, forms
from clia_tasks import digest, load_task, signatures
import clia_process

MAXIMUM = "jmbl_fg_max3"
GUARDED = "jmbl_fg_mpg_guard2"
TASK_IDS = (MAXIMUM, GUARDED)
TOKENIZER = "ascii-words/signed-decimal-integers/punctuation.v1"
TOKEN = re.compile(r"-?[0-9]+|[a-z]+|[?,.=]")
MAX_PREFIXES = (
    ("what", "is", "the", "largest", "of"),
    ("what", "is", "the", "maximum", "of"),
    ("find", "the", "largest", "of"),
)
GUARD_PREFIX = ("apply", "the", "guarded", "function", "with")


def signature(task):
    return {name: {"parameters": [[str(n), str(t)] for n, t in spec["parameters"]],
                   "sort": spec["sort"]} for name, spec in signatures(task).items()}


def contract(task_id):
    task = load_task(task_id)
    return {"schema": "ocm.text-contract.v1", "task_id": task_id,
            "task_sha256": task["task_sha256"], "signature": signature(task),
            "scope": "g1-pilot", "tokenizer": TOKENIZER,
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "seed_prefixes": [list(x) for x in (MAX_PREFIXES if task_id == MAXIMUM else (GUARD_PREFIX,))],
            "semantics": ("maximum of exactly three supplied integers" if task_id == MAXIMUM
                          else "x+y when x+y+z >= 1; otherwise x-y"),
            "parameter_order": ["x", "y", "z"], "result_type": "Int",
            "quantity_scope": "ground request; acquired program checked universally",
            "mapping_authority": "declared host seed; not acquired language"}


def tokenize(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("a nonempty text request is required")
    lowered = text.lower()
    tokens, end = [], 0
    for match in TOKEN.finditer(lowered):
        if lowered[end:match.start()].strip():
            raise ValueError("unsupported token; use exact signed decimal integers")
        tokens.append(match.group())
        end = match.end()
    if lowered[end:].strip():
        raise ValueError("unsupported trailing text")
    return tokens


def interpret(text):
    try:
        tokens = tokenize(text)
    except ValueError as exc:
        return {"status": "INPUT_REFUSED", "reason": str(exc)}
    body = tokens[:-1] if tokens[-1] in ("?", ".") else tokens
    args, task_id = None, None
    for prefix in MAX_PREFIXES:
        if tuple(body[:len(prefix)]) == prefix:
            numbers = body[len(prefix):]
            # Exact constructions only: a, b and c; no subsequence/number fishing.
            if len(numbers) == 5 and numbers[1] == "," and numbers[3] == "and":
                args, task_id = [numbers[i] for i in (0, 2, 4)], MAXIMUM
            else:
                return {"status": "CLARIFICATION_REQUIRED", "reason": "name exactly three integers as a, b and c"}
            break
    if tuple(body[:len(GUARD_PREFIX)]) == GUARD_PREFIX:
        roles = body[len(GUARD_PREFIX):]
        if len(roles) != 11 or roles[3] != "," or roles[7] != ",":
            return {"status": "CLARIFICATION_REQUIRED", "reason": "supply each of x, y and z once"}
        bindings = {}
        for offset in (0, 4, 8):
            name, equals, number = roles[offset:offset + 3]
            if name not in ("x", "y", "z") or name in bindings or equals != "=":
                return {"status": "CLARIFICATION_REQUIRED", "reason": "distinct named x, y, z bindings required"}
            bindings[name] = number
        args, task_id = [bindings[n] for n in ("x", "y", "z")], GUARDED
    if args is None:
        return {"status": "INPUT_REFUSED", "reason": "outside the declared two-family task language"}
    if any(re.fullmatch(r"-?[0-9]+", x) is None for x in args):
        return {"status": "INPUT_REFUSED", "reason": "exact signed decimal integers required"}
    try:
        values = [int(x) for x in args]
    except ValueError:
        return {"status": "INPUT_REFUSED", "reason": "integer operational bound exceeded"}
    if any(x.bit_length() > GRAMMAR["bounds"]["integer_bits"] for x in values):
        return {"status": "INPUT_REFUSED", "reason": "integer operational bound exceeded"}
    accepted = contract(task_id)
    return {"status": "INTERPRETED", "tokens": tokens,
            "semantic": {**accepted, "contract_sha256": digest(accepted), "arguments": values,
                         "bindings": dict(zip(("x", "y", "z"), values)), "unresolved_ambiguity": []}}



def validate_semantic(semantic):
    if not isinstance(semantic, dict) or semantic.get("task_id") not in TASK_IDS:
        raise ValueError("unknown semantic task")
    expected = contract(semantic["task_id"])
    if (any(semantic.get(k) != v for k, v in expected.items())
            or semantic.get("contract_sha256") != digest(expected)):
        raise ValueError("accepted semantic contract binding changed")
    args = semantic.get("arguments")
    if (not isinstance(args, list) or len(args) != 3
            or any(type(x) is not int or x.bit_length() > GRAMMAR["bounds"]["integer_bits"] for x in args)
            or semantic.get("bindings") != dict(zip(("x", "y", "z"), args))
            or semantic.get("unresolved_ambiguity") != []):
        raise ValueError("exact role bindings and resolved bounded semantics required")
    return semantic


def check_ground(task, arguments, value):
    """Check the source specification at this tuple, independently of program evaluation."""
    if type(value) is not int or len(arguments) != 3 or any(type(x) is not int for x in arguments):
        return {"status": "FAIL", "reason": "exact integer result and tuple required"}
    commands, constraints = [], []
    for node in forms(task["original_sygus"]):
        tag = str(node[0])
        if tag == "synth-fun":
            commands.append("(define-fun " + str(node[1]) + " " + dump(node[2]) + " Int " + dump(value) + ")")
        elif tag == "declare-var":
            commands.append("(declare-const " + str(node[1]) + " " + str(node[2]) + ")")
        elif tag == "define-fun":
            commands.append(dump(node))
        elif tag == "constraint":
            constraints.append(dump(node[1]))
    commands += ["(assert (= " + n + " " + dump(v) + "))" for n, v in zip(("x", "y", "z"), arguments)]
    commands.append("(assert (not (and " + " ".join(constraints) + ")))")
    checked = clia_process.invoke("verify", {"smt2": "\n".join(commands)})
    return {**checked, "scope": "source-specification at exact supplied tuple",
            "task_sha256": task["task_sha256"], "arguments": arguments, "value": value}


def response_plan(semantic, value, support_atoms):
    return {"schema": "ocm.checked-numeric-response.v1", "task_id": semantic["task_id"],
            "task_sha256": semantic["task_sha256"], "arguments": semantic["arguments"],
            "value": value, "polarity": "positive", "support_atoms": list(support_atoms)}


def realize(plan):
    prefix = "The largest value is" if plan["task_id"] == MAXIMUM else "The guarded function returns"
    return prefix + " " + str(plan["value"]) + "."


def check_response(plan, english):
    """Independent output contract checks quantity, task meaning, polarity and no extra clause."""
    if (not isinstance(plan, dict) or not {"value", "polarity", "support_atoms"} <= plan.keys()
            or plan.get("task_id") not in TASK_IDS
            or plan.get("task_sha256") != load_task(plan["task_id"])["task_sha256"]):
        return {"status": "FAIL", "reason": "unknown response semantic contract"}
    pattern = (r"The largest value is (-?[0-9]+)\." if plan["task_id"] == MAXIMUM
               else r"The guarded function returns (-?[0-9]+)\.")
    match = re.fullmatch(pattern, english) if isinstance(english, str) else None
    ok = bool(match and type(plan["value"]) is int and int(match[1]) == plan["value"]
              and plan["polarity"] == "positive" and plan["support_atoms"])
    return {"status": "PASS" if ok else "FAIL", "scope": "declared bounded response meaning"}
