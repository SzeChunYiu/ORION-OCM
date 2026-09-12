#!/usr/bin/env python3
"""Stage-3 resume precondition: is every world's scored run complete and verified?

Runs WHERE THE RUN TREE IS (the cluster). It answers exactly one question and never
guesses: for each registered world, are BOTH primary arms present and does each report
all_targets_verified? The scorer's own os.path.exists guard silently skips a world that
is missing an arm, and a silently dropped world changes m, hence Holm, hence the
terminal -- so this must be established before the scorer is ever pointed at the tree.

Exit codes are deliberately distinct so that no caller can read one as another:
  0  COMPLETE      every registered world has both arms, both verified
  3  INCOMPLETE    the tree was read fine, but some world is missing an arm or unverified
  4  CANNOT_CHECK  the run tree itself could not be read (missing root, unreadable JSON)
A crash exits non-zero on its own. "Could not check" is never "checked and fine".
"""
import json, os, sys

WORLDS = ["brass_lantern", "deep_well", "leaky_seam", "long_and_short",
          "narrow_gauge", "shallow_shelf", "tin_orchard", "twin_roots"]
# from M2P4_STAGE3_FREEZE_V1.the_run.protected_targets_per_world
REGISTERED_NT = {"brass_lantern": 38, "deep_well": 37, "leaky_seam": 36, "long_and_short": 49,
                 "narrow_gauge": 84, "shallow_shelf": 33, "tin_orchard": 38, "twin_roots": 50}
PRIMARY_ARMS = ["arm_PARENT_GF_D4.json", "arm_RESET.json"]
ALL_ARMS = ["arm_RESET.json", "arm_PARENT_GF_D4.json", "arm_SHUFFLED_HISTORY.json",
            "arm_CONTINUED_OCM.json", "arm_PARENT_WITH_MDL.json",
            "arm_PARENT_GFQ_D3.json", "arm_PARENT_GFQ_D4.json"]

def main():
    if len(sys.argv) != 2:
        print("usage: m2p4_resume_check.py <runs_root>", file=sys.stderr); return 4
    root = sys.argv[1]
    if not os.path.isdir(root):
        print(json.dumps({"verdict": "CANNOT_CHECK", "reason": f"runs root not a directory: {root}"}))
        return 4
    per, complete = [], True
    for w in WORLDS:
        d = os.path.join(root, f"m2p4_{w}_scored")
        rec = {"world": w, "run_dir_exists": os.path.isdir(d)}
        if not rec["run_dir_exists"]:
            rec["status"] = "MISSING_RUN_DIR"; complete = False; per.append(rec); continue
        rec["arms_present"] = sorted(a for a in ALL_ARMS if os.path.exists(os.path.join(d, a)))
        rec["n_arms"] = len(rec["arms_present"])
        missing_primary = [a for a in PRIMARY_ARMS if not os.path.exists(os.path.join(d, a))]
        rec["missing_primary_arms"] = missing_primary
        verified, nt = {}, {}
        for a in PRIMARY_ARMS:
            p = os.path.join(d, a)
            if not os.path.exists(p):
                continue
            try:
                obj = json.load(open(p))
            except Exception as e:                      # unreadable is CANNOT_CHECK, not "incomplete"
                print(json.dumps({"verdict": "CANNOT_CHECK",
                                  "reason": f"unreadable {p}: {e.__class__.__name__}"}))
                return 4
            verified[a] = obj.get("all_targets_verified") is True
            rows = obj.get("rows")
            nt[a] = len(rows) if isinstance(rows, list) else None
        rec["all_targets_verified"] = verified
        rec["n_rows"] = nt
        # a world whose row count disagrees with the registration is not the registered measurement
        rec["nt_matches_registration"] = all(v == REGISTERED_NT[w] for v in nt.values() if v is not None) \
                                         and len(nt) == len(PRIMARY_ARMS)
        ok = (not missing_primary and all(verified.get(a) for a in PRIMARY_ARMS)
              and rec["nt_matches_registration"])
        rec["status"] = "OK" if ok else "INCOMPLETE"
        if not ok:
            complete = False
        per.append(rec)
    out = {"verdict": "COMPLETE" if complete else "INCOMPLETE",
           "worlds_expected": len(WORLDS),
           "worlds_ok": sum(1 for r in per if r.get("status") == "OK"),
           "scorer_may_run": complete, "per_world": per}
    print(json.dumps(out, indent=1))
    return 0 if complete else 3

if __name__ == "__main__":
    sys.exit(main())
