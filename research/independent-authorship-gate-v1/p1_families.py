#!/usr/bin/env python3
"""Emit the frozen S1 family table (P1_PIPELINE_FREEZE_V1.json).

Emits P1_FAMILY_TABLE_V1.json deterministically from the transcribed IPC
domains in ipc_domains/ and the frozen generator parameters, under the frozen
seed.  Stdlib only; imports NOTHING from src/ocm and does NOT import (or run)
p1_validator.py -- the emitter must stay independent of the oracle so it can
never select instances by oracle verdict (no rejection sampling, no difficulty
filtering, no oracle-informed selection; parse failures are the only
exclusions and are retained with reasons).

Truth labels are NOT emitted here: they are recovered later by the independent
validator (freeze: independent_truth.label_recovery_rule).  Generator-intent
information (e.g. the authored goal) is retained as audit-only.

Determinism: identical inputs + frozen seed => byte-identical output (verify
by running twice and diffing; p1_selftest.py asserts it).

Usage: p1_families.py [--out PATH]   (default: this file's directory table)
"""
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE_NAME = "P1_FAMILY_TABLE_V1.json"
FREEZE_NAME = "P1_PIPELINE_FREEZE_V1.json"
RECORDED_UTC = "2026-09-10"  # frozen emission stamp, never a wall clock

FAMILIES = [
    ("S1-BLOCKSWORLD-IPC2", "ipc_domains/blocksworld-ipc2.pddl", "blocksworld-ipc2"),
    ("S1-GRIPPER-IPC1", "ipc_domains/gripper-ipc1.pddl", "gripper-ipc1"),
    ("S1-LOGISTICS-IPC1", "ipc_domains/logistics-ipc1.pddl", "logistics-ipc1"),
]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read(rel):
    with open(os.path.join(HERE, rel), "rb") as fh:
        return fh.read()


def provenance_header(rel):
    """The ';; PROVENANCE' comment block of a transcribed domain, verbatim."""
    lines, in_header = [], False
    for raw in read(rel).decode("ascii").splitlines():
        stripped = raw.strip()
        if stripped.startswith(";;"):
            text = stripped[2:].strip()
            if text == "PROVENANCE":
                in_header, lines = True, []
                continue
            if in_header and text:
                lines.append(text)
        elif stripped and in_header:
            break
    return lines


def atom(name, *args):
    return "(" + " ".join([name] + list(args)) + ")"


def and_block(atoms):
    return "(and " + " ".join(sorted(atoms)) + ")" if atoms else "(and)"


def problem_text(pid, domain, objects, init, goal):
    """Canonical, deterministic problem-file text (sorted facts, one line each
    inside the blocks)."""
    lines = [
        f"(define (problem {pid})",
        f"  (:domain {domain})",
        "  (:objects " + objects + ")",
        "  (:init " + " ".join(sorted(init)) + ")",
        "  (:goal " + and_block(goal) + "))",
        "",
    ]
    return "\n".join(lines)


def tower_facts(towers):
    """Blocks-world INITIAL facts for one deal: tower j is bottom..top."""
    facts = ["(handempty)"]
    for tower in towers:
        if not tower:
            continue
        facts.append(atom("ontable", tower[0]))
        for lower, upper in zip(tower, tower[1:]):
            facts.append(atom("on", upper, lower))
        facts.append(atom("clear", tower[-1]))
    return facts


def goal_facts(towers):
    """Blocks-world GOAL facts for one deal: tower STRUCTURE only (on/ontable),
    as in the public random-tower generator -- no clear/handempty atoms."""
    facts = []
    for tower in towers:
        if not tower:
            continue
        facts.append(atom("ontable", tower[0]))
        for lower, upper in zip(tower, tower[1:]):
            facts.append(atom("on", upper, lower))
    return facts


def blocksworld_member(n, t, rng):
    blocks = [f"b{i}" for i in range(1, n + 1)]

    def deal():
        order = list(blocks)
        rng.shuffle(order)
        return [order[j::t] for j in range(t)]

    init_deal, goal_deal = deal(), deal()
    init, goal = tower_facts(init_deal), goal_facts(goal_deal)
    pid = f"p1-bw-n{n:02d}"
    return pid, problem_text(pid, "blocks-strips",
                             " ".join(blocks) + " - block", init, goal)


def gripper_member(n, rng):
    balls = [f"ball{i}" for i in range(1, n + 1)]
    init = ([atom("at-robby", "rooma"), atom("free", "left"), atom("free", "right")]
            + [atom("at", b, "rooma") for b in balls])
    goal = [atom("at", b, "roomb") for b in balls]
    pid = f"p1-gr-n{n:02d}"
    return pid, problem_text(pid, "gripper-strips",
                             "rooma roomb - location " + " ".join(balls) + " - object",
                             init, goal)


def logistics_member(cities, packages, rng):
    locs = []
    for i in range(1, cities + 1):
        locs.append((f"apt{i}", "airport", f"c{i}"))
        locs.append((f"loc{i}", "location", f"c{i}"))
    all_locs = [name for name, _, _ in locs]
    init, goal = [], []
    for name, _, city in locs:
        init.append(atom("in-city", name, city))
    for i in range(1, cities + 1):
        init.append(atom("truck-at", f"t{i}", f"apt{i}"))
    init.append(atom("airplane-at", "ap1", "apt1"))
    for j in range(1, packages + 1):
        origin, dest = rng.choice(all_locs), rng.choice(all_locs)
        init.append(atom("obj-at", f"p{j}", origin))
        goal.append(atom("obj-at", f"p{j}", dest))
    objs = []
    objs.append(" ".join(f"c{i}" for i in range(1, cities + 1)) + " - city")
    objs.append(" ".join(f"apt{i}" for i in range(1, cities + 1)) + " - airport")
    objs.append(" ".join(f"loc{i}" for i in range(1, cities + 1)) + " - location")
    objs.append(" ".join(f"t{i}" for i in range(1, cities + 1)) + " - truck")
    objs.append("ap1 - airplane")
    objs.append(" ".join(f"p{j}" for j in range(1, packages + 1)) + " - package")
    pid = f"p1-lg-c{cities:02d}p{packages:02d}"
    return pid, problem_text(pid, "logistics-strips", " ".join(objs), init, goal)


def build_family(family_id, domain_rel, param_key, params, seed):
    dp = params["domains"][param_key]
    defaults = dp["default_parameters"]
    rng = random.Random(f"{seed}|{family_id}")
    members = []
    if param_key == "blocksworld-ipc2":
        pairs = list(zip(defaults["member_sizes_n"], defaults["towers_t"]))
        built = [blocksworld_member(n, t, rng) for n, t in pairs]
    elif param_key == "gripper-ipc1":
        built = [gripper_member(n, rng) for n in defaults["member_sizes_n"]]
    else:
        built = [logistics_member(m["cities"], m["packages"], rng)
                 for m in defaults["members"]]
    for pid, text in built:
        members.append({
            "member_id": pid,
            "instance_sha256": sha256_bytes(text.encode("ascii")),
            "instance_text": text,
            "intent_audit": {
                "authored_goal": text.split("(:goal ", 1)[1].rstrip(")\n"),
                "note": ("audit-only generator intent; truth labels are recovered "
                         "by p1_validator.py, never read from this field"),
            },
        })
    return {
        "family_id": family_id,
        "domain_file": domain_rel,
        "domain_sha256": sha256_bytes(read(domain_rel)),
        "domain_provenance": provenance_header(domain_rel),
        "generator": {
            "semantics": dp["provenance"],
            "default_parameters": defaults,
            "seed_stream": f"{seed}|{family_id}",
        },
        "members": members,
        "exclusions": [],
        "member_count": len(members),
    }


def emit(out_path):
    params = json.loads(read("ipc_domains/GENERATOR_PARAMS_V1.json").decode("ascii"))
    seed = params["frozen_seed"]
    families = [build_family(fid, rel, key, params, seed)
                for fid, rel, key in FAMILIES]
    pipeline_files = [rel for _, rel, _ in FAMILIES] + [
        "ipc_domains/GENERATOR_PARAMS_V1.json", "p1_validator.py", "p1_families.py",
        FREEZE_NAME]
    table = {
        "schema": "OCM_P1_FAMILY_TABLE",
        "version": "V1",
        "freeze": FREEZE_NAME,
        "emitted_by": "p1_families.py",
        "recorded_utc": RECORDED_UTC,
        "determinism": {
            "frozen_seed": seed,
            "byte_identical_rerun_expected": True,
            "rng": ("per-family random.Random seeded with '<frozen_seed>|<family_id>'; "
                    "all facts and object lists sorted before emission"),
        },
        "discipline": params["discipline"],
        "pipeline_file_sha256": {rel: sha256_bytes(read(rel)) for rel in sorted(pipeline_files)},
        "families": families,
        "total_members": sum(f["member_count"] for f in families),
        "exclusions": [],
        "exclusions_rule": ("parse failures are the only exclusions and are retained "
                            "here with reasons; none occurred at emission"),
    }
    with open(out_path, "w") as fh:
        fh.write(json.dumps(table, indent=1, sort_keys=True) + "\n")
    return table


def main(argv):
    out = os.path.join(HERE, TABLE_NAME)
    if len(argv) == 3 and argv[1] == "--out":
        out = argv[2]
    elif argv[1:]:
        print("usage: p1_families.py [--out PATH]", file=sys.stderr)
        return 3
    table = emit(out)
    fams = ", ".join(f"{f['family_id']}={f['member_count']}" for f in table["families"])
    print(f"P1_FAMILY_TABLE emitted: {table['total_members']} members ({fams}) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
