#!/usr/bin/env python3
"""P1 pipeline selftest: the freeze's four hostiles + no-alarm (P1_PIPELINE_FREEZE_V1.json).

Legal to run on any host (toy data, sub-second).  Distinct exit code per
failure class -- "could not check" is never "checked and fine":

  0  ALL_PASS
  3  CANNOT_CHECK        harness could not run a check (missing file, etc.)
  10 HOSTILE_A           a planted-INVALID plan was ACCEPTED
  11 HOSTILE_B           a planted-VALID plan was REJECTED
  12 HOSTILE_C           the tampered domain did not flip a previously-valid plan
  13 NO_ALARM            clean family set produced a CANNOT_CHECK or a rejected-valid
  14 INDEPENDENCE        p1_validator.py / p1_families.py import outside stdlib
                         or reference src/ocm
  15 REPRODUCTION        P1_FAMILY_TABLE_V1.json does not reproduce byte-identically

Hostile cases (freeze independent_truth.hostile_validation_required_before_use):
  A planted-invalid: precondition violation, wrong delete effect (fact used
    after its deletion), goal-not-reached -- all MUST be rejected;
  B planted-valid across all three transcribed domains -- all MUST be accepted;
  C tampered domain: ONE changed precondition in blocksworld (stack gains
    (clear ?x)) MUST flip at least one previously-valid plan's verdict;
  D no-alarm: every committed family member validates (empty plan) with
    exit 0 or 1 and NEVER 3; zero CANNOT_CHECK; the planted-valid set
    (the known-valid members) is fully accepted.
"""
import ast
import filecmp
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1_validator as V  # noqa: E402  (module use; CLI contract also spot-checked)

DOMAINS = {
    "blocks": os.path.join(HERE, "ipc_domains", "blocksworld-ipc2.pddl"),
    "gripper": os.path.join(HERE, "ipc_domains", "gripper-ipc1.pddl"),
    "logistics": os.path.join(HERE, "ipc_domains", "logistics-ipc1.pddl"),
}

BW_PROBLEM = """
(define (problem selftest-bw)
  (:domain blocks-strips)
  (:objects a b c - block)
  (:init (ontable a) (ontable b) (ontable c) (clear a) (clear b) (clear c) (handempty))
  (:goal (and (on b a) (on c b))))
"""

BW_VALID = "(pick-up b)\n(stack b a)\n(pick-up c)\n(stack c b)\n"
BW_PRE_VIOLATION = "(unstack b a)\n"                      # (on b a) never true
BW_DELETED_FACT = "(pick-up b)\n(stack b a)\n(pick-up a)\n"  # clear(a) was deleted
BW_GOAL_MISSED = "(pick-up b)\n(put-down b)\n"            # executes, goal unreached

GR_PROBLEM = """
(define (problem selftest-gr)
  (:domain gripper-strips)
  (:objects rooma roomb - location ball1 ball2 - object)
  (:init (at-robby rooma) (at ball1 rooma) (at ball2 rooma) (free left) (free right))
  (:goal (and (at ball1 roomb) (at ball2 roomb))))
"""

GR_VALID = ("(pick ball1 rooma left)\n(pick ball2 rooma right)\n(move rooma roomb)\n"
            "(drop ball1 roomb left)\n(drop ball2 roomb right)\n")

LG_PROBLEM = """
(define (problem selftest-lg)
  (:domain logistics-strips)
  (:objects c1 - city apt1 - airport l1x - location t1 - truck ap1 - airplane p1 - package)
  (:init (in-city apt1 c1) (in-city l1x c1) (truck-at t1 apt1)
         (airplane-at ap1 apt1) (obj-at p1 l1x))
  (:goal (obj-at p1 apt1)))
"""

LG_VALID = ("(drive-truck t1 apt1 l1x c1)\n(load-truck p1 t1 l1x)\n"
            "(drive-truck t1 l1x apt1 c1)\n(unload-truck p1 t1 apt1)\n")


def read(path):
    with open(path) as fh:
        return fh.read()


def cli(domain_path, problem_path, plan_path):
    return subprocess.run(
        [sys.executable, os.path.join(HERE, "p1_validator.py"),
         domain_path, problem_path, plan_path],
        capture_output=True, text=True)


def hostile_a(tmp):
    cases = [("precondition violation", BW_PRE_VIOLATION),
             ("wrong delete effect", BW_DELETED_FACT),
             ("goal not reached", BW_GOAL_MISSED)]
    dom = read(DOMAINS["blocks"])
    for label, plan in cases:
        code, reason = V.validate(dom, BW_PROBLEM, plan)
        print(f"  A {label}: exit {code} ({reason})")
        if code != V.INVALID:
            print(f"HOSTILE_A FAIL: {label} must be REJECTED (exit 1), got {code}")
            return False
    return True


def hostile_b(tmp):
    doms = {"blocks": (DOMAINS["blocks"], BW_PROBLEM, BW_VALID),
            "gripper": (DOMAINS["gripper"], GR_PROBLEM, GR_VALID),
            "logistics": (DOMAINS["logistics"], LG_PROBLEM, LG_VALID)}
    for name, (dpath, prob, plan) in doms.items():
        code, reason = V.validate(read(dpath), prob, plan)
        print(f"  B planted-valid [{name}]: exit {code} ({reason})")
        if code != V.VALID:
            print(f"HOSTILE_B FAIL: {name} valid plan REJECTED (got {code})")
            return False
    return True


def hostile_c(tmp):
    dom = read(DOMAINS["blocks"])
    needle = ":precondition (and (holding ?x) (clear ?y))"
    changed = ":precondition (and (holding ?x) (clear ?y) (clear ?x))"
    if dom.count(needle) != 1:
        print(f"HOSTILE_C CANNOT_CHECK: tamper needle occurs {dom.count(needle)}x")
        return None
    tampered = dom.replace(needle, changed)
    before, _ = V.validate(dom, BW_PROBLEM, BW_VALID)
    after, reason = V.validate(tampered, BW_PROBLEM, BW_VALID)
    print(f"  C tamper (stack gains (clear ?x)): {before} -> {after} ({reason})")
    return before == V.VALID and after == V.INVALID


def no_alarm():
    table_path = os.path.join(HERE, "P1_FAMILY_TABLE_V1.json")
    try:
        table = json.loads(read(table_path))
    except (OSError, ValueError) as exc:
        print(f"NO_ALARM CANNOT_CHECK: family table unreadable: {exc}")
        return None
    cannot, members = 0, 0
    for fam in table.get("families", []):
        dom = read(os.path.join(HERE, fam["domain_file"]))
        for m in fam["members"]:
            members += 1
            code, _ = V.validate(dom, m["instance_text"], "")
            if code == V.CANNOT_CHECK:
                cannot += 1
                print(f"  D CANNOT_CHECK on clean member {m['member_id']}")
    print(f"  D clean family set: {members} members, {cannot} CANNOT_CHECK, "
          f"0 rejected-valid (planted-valid set from B)")
    if cannot:
        print("NO_ALARM FAIL: clean family set produced CANNOT_CHECK")
        return False
    return members == table.get("total_members")


ALLOWED_IMPORTS = {
    "p1_validator.py": {"sys", "re"},
    "p1_families.py": {"hashlib", "json", "os", "random", "sys"},
}


def independence():
    ok = True
    for fname, allowed in ALLOWED_IMPORTS.items():
        path = os.path.join(HERE, fname)
        try:
            tree = ast.parse(read(path))
        except (OSError, SyntaxError) as exc:
            print(f"INDEPENDENCE CANNOT_CHECK: {fname}: {exc}")
            return None
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:  # relative import = local module dependency
                    imported.add("<relative>")
                else:
                    imported.add((node.module or "").split(".")[0])
        bad = imported - allowed
        print(f"  E {fname}: imports {sorted(imported)} -> "
              f"{'stdlib-only OK' if not bad else 'VIOLATION ' + str(sorted(bad))}")
        if bad or imported & {"ocm", "src"}:
            ok = False
    return ok


def reproduction(tmp):
    table_path = os.path.join(HERE, "P1_FAMILY_TABLE_V1.json")
    out = os.path.join(tmp, "repro", "P1_FAMILY_TABLE_V1.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, "p1_families.py"), "--out", out],
        capture_output=True, text=True)
    same = r.returncode == 0 and filecmp.cmp(table_path, out, shallow=False)
    print(f"  F re-emission exit {r.returncode}, byte-identical: {same}")
    return same


def cli_contract(tmp):
    """Spot-check the CLI exit-code contract via subprocess (0 / 1 / 3)."""
    d, p = os.path.join(tmp, "d.pddl"), os.path.join(tmp, "p.pddl")
    open(d, "w").write(read(DOMAINS["blocks"]))
    open(p, "w").write(BW_PROBLEM)
    for label, plan, want in (("valid", BW_VALID, 0),
                              ("invalid", BW_PRE_VIOLATION, 1),
                              ("cannot-check", "(pick-up\n", 3)):
        pl = os.path.join(tmp, label + ".plan")
        open(pl, "w").write(plan)
        r = cli(d, p, pl)
        verdict = {0: "VALID", 1: "INVALID", 3: "CANNOT_CHECK"}[r.returncode]
        print(f"  CLI {label}: exit {r.returncode} ({verdict}: {r.stdout.strip()[:70]})")
        if r.returncode != want:
            print(f"CLI CONTRACT FAIL: {label} expected {want}, got {r.returncode}")
            return False
    return True


def main():
    import time
    t0 = time.perf_counter()
    checks = [("A planted-invalid rejected", hostile_a, 10),
              ("B planted-valid accepted", hostile_b, 11),
              ("C tampered domain flips verdict", hostile_c, 12),
              ("D no-alarm on clean family set", no_alarm, 13),
              ("E independence (no src/ocm imports)", independence, 14),
              ("F family table reproduces byte-identically", reproduction, 15),
              ("G CLI exit-code contract", cli_contract, 3)]
    with tempfile.TemporaryDirectory() as tmp:
        for label, fn, fail_code in checks:
            try:
                result = fn(tmp) if fn.__code__.co_argcount else fn()
            except Exception as exc:  # harness failure is never a quiet pass
                print(f"{label}: CANNOT_CHECK harness exception: {exc!r}")
                return 3
            if result is None:
                print(f"{label}: CANNOT_CHECK")
                return 3
            if result is False:
                return fail_code
    dt = time.perf_counter() - t0
    print(f"P1_SELFTEST PASS: all 7 checks green in {dt:.2f}s "
          "(4 hostiles + no-alarm + independence + reproduction)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
