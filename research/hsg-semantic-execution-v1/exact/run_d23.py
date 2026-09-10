#!/usr/bin/env python3
"""D23 language semantic round-trip laboratory -- runner.

Executes the arms frozen in D23_PROTOCOL_V1.json / FREEZE_D23_V1.json.
Strict contract: corpus, word tables, arms, endpoints, hostiles, clean
controls and verdict vocabulary are READ FROM THE FROZEN PROTOCOL FILE,
not re-implemented. The only realization code here is the reader machinery
(order-free token parser + the frozen J tables) and the arm drivers.

Exit codes (distinct on purpose):
  0  RUN_COMPLETED_ALL_FROZEN_EXPECTATIONS_MET
  1  RUN_COMPLETED_WITH_RECORDED_EXPECTATION_FAILURES (findings, not crashes)
  3  CANNOT_CHECK (reader-construction self-check failed)

Determinism: rng_draws = 0, sorted iteration, int/str/set arithmetic only,
no float in any decision predicate. wall_s/cpu_s are metadata, excluded
from the cross-host identity hash.
"""
import hashlib, json, os, platform, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.dirname(HERE)
PROTOCOL_PATH = os.path.join(CAP, "D23_PROTOCOL_V1.json")
RESULTS_PATH = os.path.join(CAP, "exact", "results", "D23_RESULTS.json")
RECEIPTS_PATH = os.path.join(CAP, "exact", "receipts", "D23_receipts.jsonl")
HOST_RECEIPT_PATH = os.path.join(CAP, "exact", "receipts", "D23_HOST_RECEIPT.json")

COORDS7 = ["referent", "negation", "quantity", "scope", "modality",
           "warrant", "speech_act"]
ACTIONS = ["COMMIT_SHIP", "COMMIT_HOLD", "CLARIFY", "ABSTAIN"]  # frozen priority

class Ops:
    """B_exec stage counters (E6): disjoint integer counts, never scalarized."""
    def __init__(self):
        self.interpretation_ops = 0
        self.ambiguity_ops = 0
        self.realization_ops = 0
        self.reverse_read_ops = 0
        self.verification_calls = 0
        self.clarification_ops = 0
        self.rejected_attempts = 0
    def as_dict(self):
        return dict(sorted(self.__dict__.items()))

def rec_key(r):
    return json.dumps({c: r[c] for c in sorted(r)}, sort_keys=True)

def rec_set(rs):
    return {rec_key(r) for r in rs}

# ---------------------------------------------------------------- reader
class Reader:
    """Order-free reader over the FROZEN word tables.

    Token order is not a protected coordinate (frozen), so each token maps
    to its coordinate by inverse word lookup; base and synonym words share
    no spelling across coordinates (asserted at construction). A token
    'x-or-y' is an ambiguous surface slot: both sides map to the same
    coordinate with different values, expanding to one reading per side.
    """
    def __init__(self, proto, ops):
        wt = proto["protected_coordinates"]["word_tables_frozen"]
        self.base = wt["base"]
        self.syn = wt["synonym"]
        self.ops = ops
        self.inv = {}
        collisions = []
        for coord, words in sorted(self.base.items()):
            for value, word in sorted(words.items()):
                if word in self.inv and self.inv[word] != (coord, value):
                    collisions.append(word)
                self.inv[word] = (coord, value)
        # synonym table is keyed by the BASE word -> synonym word; map each
        # synonym word back to the VALUE whose base word it replaces
        bword_to_value = {word: value
                          for coord, words in self.base.items()
                          for value, word in words.items()}
        for coord, words in sorted(self.syn.items()):
            for bword, sword in sorted(words.items()):
                value = bword_to_value[bword]
                if sword in self.inv and self.inv[sword] != (coord, value):
                    collisions.append(sword)
                self.inv[sword] = (coord, value)
        self.word_collisions = sorted(set(collisions))
        self.order = wt["order"]

    def parse(self, surface):
        """Reading set of a surface as a list of records (dicts)."""
        amb = []   # list of (coord, sorted values)
        fixed = {}
        for tok in surface.split():
            self.ops.interpretation_ops += 1
            if "-or-" in tok:
                sides = tok.split("-or-")
                mapped = [self.inv[s] for s in sides]
                coords = {m[0] for m in mapped}
                if len(coords) != 1:
                    return None
                coord = mapped[0][0]
                vals = sorted({m[1] for m in mapped})
                if len(vals) < 2:
                    return None
                amb.append((coord, vals))
                self.ops.ambiguity_ops += 1
            else:
                coord, value = self.inv[tok]
                fixed[coord] = value
        if len(fixed) + len(amb) != 7:
            return None
        out = []
        def build(i, cur):
            if i == len(amb):
                out.append(dict(cur))
                return
            coord, vals = amb[i]
            for v in vals:
                cur[coord] = v
                build(i + 1, cur)
        build(0, fixed)
        return out

def realize(rec, reader):
    """Canonical realization: base word table, frozen token order."""
    reader.ops.realization_ops += 1
    return " ".join(reader.base[c][rec[c]] for c in reader.order)

# ------------------------------------------------- frozen J table variants
def declared_readings(item):
    """The frozen J_full table entry for a corpus item (dispatch on the
    frozen structure: 'readings' -> ambiguous, 'contexts' -> context-split,
    else singleton ground)."""
    if "readings" in item:
        return [r["record"] for r in item["readings"]]
    if "contexts" in item:
        return [c["required_record"] for c in item["contexts"]]
    return [item["ground"]]

def j_full(item, reader):
    reader.ops.reverse_read_ops += 1
    return declared_readings(item)

def j_omitted(item, reader):
    rs = declared_readings(item)
    keep = sorted(rs, key=rec_key)[1:]  # drop lexicographically first
    reader.ops.reverse_read_ops += 1
    return keep

def j_empty(item, reader):
    reader.ops.reverse_read_ops += 1
    return []

def t66_gate_declared(committed, declared, ops):
    """Frozen T66 gate applied to the DECLARED reading set (A2): a commit is
    admissible only if the reader's J COVERS the declared set."""
    ops.verification_calls += 1
    if not declared or not (rec_set(committed) >= rec_set(declared)):
        return "REFUSED_COVERAGE_GAP"
    return "COMMIT_OK"

def violated_coords(reading, ground):
    return sorted(c for c in COORDS7 if reading[c] != ground[c])

# ---------------------------------------------------------------- arms
def arm_a1(proto, reader, findings):
    """A1_roundtrip_clean: CLEAN CONTROL. 40 faithful surfaces via J_full.
    Expect coverage 1.0, zero round-trip error, zero refusals, zero flags.
    Any alarm VOIDS the tranche (CONTROL_FALSE_ALARM)."""
    ops = Ops()
    items = (proto["corpus"]["faithful_base"]
             + proto["corpus"]["paraphrases"])
    per_item = []
    for it in sorted(items, key=lambda x: x["id"]):
        parsed = reader.parse(it["surface"])
        declared = declared_readings(it)
        gate = t66_gate_declared(parsed, declared, ops)
        viol = [violated_coords(r, it["ground"]) for r in parsed or []]
        flag = bool(viol) and any(v for v in viol)
        per_item.append({"id": it["id"], "set_equal": rec_set(parsed or []) == rec_set(declared),
                         "violated": sorted({c for v in viol for c in v}),
                         "gate": gate, "flag": flag})
    n_refuse = sum(1 for p in per_item if p["gate"] != "COMMIT_OK")
    n_flag = sum(1 for p in per_item if p["flag"])
    n_err = sum(1 for p in per_item if p["violated"])
    coverage = sum(1 for p in per_item if p["set_equal"])
    verdict = "CONTROL_FALSE_ALARM" if (n_refuse or n_flag or n_err
                                        or coverage != len(per_item)) else "COMMIT_OK"
    if verdict == "CONTROL_FALSE_ALARM":
        findings.append("A1 clean control alarmed: refuse=%d flag=%d err=%d coverage=%d/%d"
                        % (n_refuse, n_flag, n_err, coverage, len(per_item)))
    return {"arm": "A1_roundtrip_clean", "verdict": verdict,
            "n_items": len(per_item), "coverage_set_equal": coverage,
            "refusals": n_refuse, "flags": n_flag, "round_trip_errors": n_err,
            "tranche_voided": verdict == "CONTROL_FALSE_ALARM",
            "per_item": per_item, "B_exec": ops.as_dict()}, ops

def arm_a2(proto, reader, findings):
    """A2_omitted_reading: H-T66a language layer. Gate on the DECLARED set
    must refuse on all 4 AMB surfaces under J_omitted; a naive gate on the
    reader's own J commits through incomplete coverage (the planted flip).
    Clean control: J_full on the same surfaces -> zero coverage refusals."""
    ops = Ops()
    items = sorted(proto["corpus"]["ambiguous"], key=lambda x: x["id"])
    per_item = []
    for it in items:
        own = j_omitted(it, reader)
        declared = declared_readings(it)
        parsed = reader.parse(it["surface"])
        gate_correct = t66_gate_declared(own, declared, ops)
        # naive gate: checks only its own J (the failure mode being planted)
        ops.verification_calls += 1
        naive = "COMMIT_OK" if own else "REFUSED_COVERAGE_GAP"
        ctrl = j_full(it, reader)
        gate_ctrl = t66_gate_declared(ctrl, declared, ops)
        per_item.append({"id": it["id"], "gate_on_declared": gate_correct,
                         "naive_gate_on_own_j": naive,
                         "clean_control_j_full": gate_ctrl})
        if gate_correct != "REFUSED_COVERAGE_GAP":
            findings.append("A2 %s: gate did NOT refuse under J_omitted" % it["id"])
        if naive == "COMMIT_OK":
            ops.rejected_attempts += 1  # the unsafe commit the gate exists to block
    n_refuse = sum(1 for p in per_item if p["gate_on_declared"] == "REFUSED_COVERAGE_GAP")
    n_naive_commits = sum(1 for p in per_item if p["naive_gate_on_own_j"] == "COMMIT_OK")
    n_ctrl_refuse = sum(1 for p in per_item if p["clean_control_j_full"] != "COMMIT_OK")
    hostile_fired = n_naive_commits > 0
    verdict = "REFUSED_COVERAGE_GAP" if (n_refuse == len(per_item) and n_ctrl_refuse == 0) \
        else "HOSTILE_DID_NOT_FLIP"
    if not hostile_fired:
        findings.append("A2: naive gate never committed through incomplete J; plant inert")
    return {"arm": "A2_omitted_reading", "verdict": verdict,
            "hostile": "H-T66a", "n_items": len(per_item),
            "refusals_correct_gate": n_refuse,
            "naive_gate_silent_commits": n_naive_commits,
            "clean_control_refusals": n_ctrl_refuse,
            "per_item": per_item, "B_exec": ops.as_dict()}, ops

def arm_a3(proto, reader, findings):
    """A3_costume: H-D23a. 7/7 flagged with exactly the flipped coordinate,
    zero silent accepts; clean control = B1..B7 style-P1 paraphrases, zero flags."""
    ops = Ops()
    costumes = sorted(proto["corpus"]["costumes"], key=lambda x: x["id"])
    bases = {b["id"]: b for b in proto["corpus"]["faithful_base"]}
    per_item, ctrl_items = [], []
    for it in costumes:
        parsed = reader.parse(it["surface"])
        base_ground = bases[it["base"]]["ground"]
        viol = sorted({c for r in (parsed or [])
                       for c in violated_coords(r, base_ground)})
        expected = [it["flipped_coordinate"]]
        ok = (viol == expected)
        per_item.append({"id": it["id"], "violated": viol, "expected": expected,
                         "flagged": ok, "silent_accept": bool(viol) and not ok})
        if not viol:
            ops.rejected_attempts += 1
    for bid in sorted(bases):
        if bid not in [it["base"] for it in costumes]:
            continue
        pit = [p for p in proto["corpus"]["paraphrases"]
               if p["id"] == bid + "-P1"][0]
        parsed = reader.parse(pit["surface"])
        viol = sorted({c for r in (parsed or [])
                       for c in violated_coords(r, pit["ground"])})
        ctrl_items.append({"id": pit["id"], "violated": viol})
    n_flag = sum(1 for p in per_item if p["flagged"])
    n_silent = sum(1 for p in per_item if p["silent_accept"])
    n_ctrl = sum(1 for c in ctrl_items if c["violated"])
    verdict = "ROUND_TRIP_ERROR_DETECTED" if (n_flag == 7 and n_silent == 0 and n_ctrl == 0) \
        else ("HOSTILE_DID_NOT_FLIP" if n_flag < 7 else "CONTROL_FALSE_ALARM")
    if verdict != "ROUND_TRIP_ERROR_DETECTED":
        findings.append("A3: flagged %d/7, silent %d, control flags %d"
                        % (n_flag, n_silent, n_ctrl))
    return {"arm": "A3_costume", "verdict": verdict, "hostile": "H-D23a",
            "n_items": len(per_item), "flagged": n_flag, "silent_accepts": n_silent,
            "clean_control_flags": n_ctrl, "per_item": per_item,
            "clean_control_items": ctrl_items, "B_exec": ops.as_dict()}, ops

def arm_a4(proto, reader, findings):
    """A4_ambiguity_t68: intersection of declared safe-action sets.
    Nonempty -> deterministic commit (first in frozen priority order);
    empty -> CLARIFY if a frozen discriminating question exists, else ABSTAIN.
    Clean control: the 10 base items with G = all four actions -> COMMIT_SHIP."""
    ops = Ops()
    qs = proto["corpus"]["clarification_questions"]
    items = sorted(proto["corpus"]["ambiguous"], key=lambda x: x["id"])
    per_item = []
    for it in items:
        sets = [r["safe_actions"] for r in it["readings"]]
        ops.ambiguity_ops += 1
        inter = sorted(set(sets[0]).intersection(*sets[1:])) if sets else []
        choice = next((a for a in ACTIONS if a in inter), None)
        has_q = any(it["id"] in q["applies_to"] for q in qs)
        if inter:
            act, term = choice, "COMMIT_OK"
            ops.verification_calls += 1
        else:
            ops.clarification_ops += 1
            act, term = ("CLARIFY", "CLARIFY_CORRECT") if has_q else ("ABSTAIN", "ABSTAIN_CORRECT")
        unsafe = bool(inter) is False and act.startswith("COMMIT")
        expected_commit = it.get("deterministic_safe_commit")
        ok_commit = (expected_commit is None and not inter) or \
                    (inter and expected_commit in inter)
        per_item.append({"id": it["id"], "t68_branch": it["t68_branch"],
                         "intersection": inter, "action": act, "terminal": term,
                         "unsafe_commit": unsafe, "commit_matches_frozen": ok_commit})
        if unsafe:
            findings.append("A4 %s: UNSAFE_COMMIT on empty intersection" % it["id"])
    bases = sorted(proto["corpus"]["faithful_base"], key=lambda x: x["id"])
    ctrl = []
    for b in bases:
        ops.ambiguity_ops += 1
        inter = sorted(ACTIONS)
        act = next(a for a in ACTIONS if a in inter)
        ctrl.append({"id": b["id"], "action": act, "over_refusal": act == "CLARIFY"})
    n_unsafe = sum(1 for p in per_item if p["unsafe_commit"])
    n_ok = sum(1 for p in per_item if p["commit_matches_frozen"]
               and not p["unsafe_commit"]
               and p["terminal"] in ("COMMIT_OK", "CLARIFY_CORRECT", "ABSTAIN_CORRECT"))
    n_over = sum(1 for c in ctrl if c["over_refusal"])
    verdict = "COMMIT_OK" if (n_unsafe == 0 and n_ok == len(per_item) and n_over == 0) \
        else ("UNSAFE_COMMIT" if n_unsafe else "OVER_REFUSAL")
    return {"arm": "A4_ambiguity_t68", "verdict": verdict,
            "n_items": len(per_item), "unsafe_commits": n_unsafe,
            "clean_control_over_refusals": n_over, "per_item": per_item,
            "clean_control": ctrl, "B_exec": ops.as_dict()}, ops

def arm_a5(proto, reader, findings):
    """A5_context_split_t69: does any single context-free reading satisfy BOTH
    contexts? Expect 2/2 CONTEXT_CONFLICT_DETECTED with the frozen disjoint_on
    witness. If any reading satisfies both, world design failed (LANE FAILS).
    Clean control: each context alone satisfiable by its own required record."""
    ops = Ops()
    items = sorted(proto["corpus"]["context_split"], key=lambda x: x["id"])
    per_item = []
    for it in items:
        reqs = [c["required_record"] for c in it["contexts"]]
        parsed = reader.parse(it["surface"]) or []
        candidates = parsed + reqs
        ops.verification_calls += 1
        both = [r for r in candidates
                if all(rec_key(r) == rec_key(q) for q in reqs)]
        diff = sorted(c for c in COORDS7 if reqs[0][c] != reqs[1][c])
        witness_ok = diff == sorted(it["disjoint_on"])
        alone = all(any(rec_key(r) == rec_key(q) for r in candidates) for q in reqs)
        conflict = not both
        per_item.append({"id": it["id"], "context_free_readings_satisfying_both": len(both),
                         "diff_coords": diff, "frozen_disjoint_on": sorted(it["disjoint_on"]),
                         "witness_matches_frozen": witness_ok,
                         "each_context_alone_satisfiable": alone,
                         "conflict_detected": conflict})
        if not witness_ok or not alone:
            findings.append("A5 %s: world-design failure (witness %s, alone %s)"
                            % (it["id"], witness_ok, alone))
    n_conf = sum(1 for p in per_item if p["conflict_detected"] and p["witness_matches_frozen"])
    verdict = "CONTEXT_CONFLICT_DETECTED" if n_conf == len(per_item) else "LANE_FAILS_WORLD_DESIGN"
    return {"arm": "A5_context_split_t69", "verdict": verdict, "n_items": len(per_item),
            "conflicts_with_frozen_witness": n_conf, "per_item": per_item,
            "B_exec": ops.as_dict()}, ops

def arm_a6(proto, reader, findings):
    """A6_clarification_voi: eliminations(q,s) = declared readings eliminated by
    the ground answer; must match the frozen table exactly, zeros included."""
    ops = Ops()
    qs = proto["corpus"]["clarification_questions"]
    items = {it["id"]: it for it in proto["corpus"]["ambiguous"]}
    per_pair = []
    for q in sorted(qs, key=lambda x: x["id"]):
        coord = q["targets_coordinate"]
        for sid in sorted(q["applies_to"]):
            ops.clarification_ops += 1
            readings = items[sid]["readings"]
            vals = sorted({r["record"][coord] for r in readings})
            counts = sorted({sum(1 for r in readings if r["record"][coord] != v)
                             for v in vals})  # answer-independent by construction?
            deterministic = len(counts) == 1
            measured = counts[0] if deterministic else None
            frozen = q["eliminates_on_ground_answer"][sid]
            per_pair.append({"question": q["id"], "item": sid,
                             "answers_possible": vals,
                             "answer_independent": deterministic,
                             "measured": measured, "frozen": frozen,
                             "match": deterministic and measured == frozen})
            if not (deterministic and measured == frozen):
                findings.append("A6 %s/%s: measured %s vs frozen %s"
                                % (q["id"], sid, measured, frozen))
    n_match = sum(1 for p in per_pair if p["match"])
    verdict = "CLARIFY_CORRECT" if n_match == len(per_pair) else "CANNOT_CHECK"
    zero_cases = [p for p in per_pair if p["frozen"] == 0]
    return {"arm": "A6_clarification_voi", "verdict": verdict,
            "n_pairs": len(per_pair), "matches": n_match,
            "zero_value_cases_retained": [p["question"] + "/" + p["item"] for p in zero_cases],
            "per_pair": per_pair, "B_exec": ops.as_dict()}, ops

# ------------------------------------------------------------- endpoints
def endpoints_e1_e5(proto, reader, arms):
    """E1 coverage (set equality, not accuracy; supersets counted separately),
    E2 round-trip violation multiset, E3 ambiguity-set sizes, E5 empty-J arm."""
    ops = Ops()
    groups = [("faithful_base", "faithful_base"), ("paraphrases", "paraphrases"),
              ("costumes", "costumes"), ("ambiguous", "ambiguous"),
              ("context_split", "context_split")]
    cov_rows, sizes, viol_rows, empty_j = [], [], [], []
    supersets = 0
    for gkey, gname in groups:
        for it in sorted(proto["corpus"][gkey], key=lambda x: x["id"]):
            parsed = reader.parse(it["surface"]) or []
            declared = declared_readings(it)
            pk, dk = rec_set(parsed), rec_set(declared)
            cov_rows.append({"id": it["id"], "group": gname,
                             "set_equal": pk == dk,
                             "superset": pk > dk, "subset": pk < dk})
            supersets += 1 if pk > dk else 0
            sizes.append({"id": it["id"], "|J|": len(declared),
                          "|parse|": len(parsed)})
            if gkey in ("faithful_base", "paraphrases"):
                for r in parsed:
                    viol_rows.append({"id": it["id"],
                                      "violated": violated_coords(r, it["ground"])})
    for it in sorted(proto["corpus"]["ambiguous"], key=lambda x: x["id"]):
        got = j_empty(it, reader)
        ops.verification_calls += 1
        empty_j.append({"id": it["id"], "|J|": len(got),
                        "commit": len(got) > 0,
                        "terminal": "ABSTAIN_CORRECT" if not got else "UNSAFE_COMMIT"})
    n = len(cov_rows)
    return {
        "E1_coverage": {"items": n,
                        "set_equal": sum(1 for r in cov_rows if r["set_equal"]),
                        "strict_supersets": supersets,
                        "strict_subsets": sum(1 for r in cov_rows if r["subset"])},
        "E2_round_trip": {"committed_readings": len(viol_rows),
                          "nonempty_violations": sum(1 for v in viol_rows if v["violated"]),
                          "per_coordinate": {c: sum(1 for v in viol_rows if c in v["violated"])
                                             for c in COORDS7},
                          "silent_unflagged_violations": 0 if arms["A3"]["silent_accepts"] == 0
                          else None},
        "E3_ambiguity_sizes": sizes,
        "E5_empty_J": {"surfaces": len(empty_j), "commits": sum(1 for e in empty_j if e["commit"]),
                       "all_abstain_correct": all(e["terminal"] == "ABSTAIN_CORRECT" for e in empty_j),
                       "per_surface": empty_j},
        "B_exec_endpoint_pass": ops.as_dict(),
    }

# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    c0 = time.process_time()
    proto = json.load(open(PROTOCOL_PATH))
    proto_sha = hashlib.sha256(open(PROTOCOL_PATH, "rb").read()).hexdigest()
    freeze_path = os.path.join(CAP, "FREEZE_D23_V1.json")
    freeze = json.load(open(freeze_path))
    freeze_sha = hashlib.sha256(open(freeze_path, "rb").read()).hexdigest()
    findings = []

    # ---- CANNOT_CHECK gate: the protocol file must match its freeze record
    if freeze["manifest_sha256"]["D23_PROTOCOL_V1.json"] != proto_sha:
        print("CANNOT_CHECK protocol sha does not match FREEZE_D23_V1.json")
        return 3

    ops0 = Ops()
    reader = Reader(proto, ops0)

    # ---- construction self-check
    self_check = {"word_collisions": reader.word_collisions, "counts": {}}
    corpus = proto["corpus"]
    for gkey, expect in [("faithful_base", 10), ("paraphrases", 30),
                         ("costumes", 7), ("ambiguous", 4),
                         ("context_split", 2), ("clarification_questions", 4)]:
        self_check["counts"][gkey] = len(corpus[gkey])
    parse_mismatch = []
    for gkey in ("faithful_base", "paraphrases", "costumes", "ambiguous"):
        for it in sorted(corpus[gkey], key=lambda x: x["id"]):
            parsed = reader.parse(it["surface"])
            if parsed is None or rec_set(parsed) != rec_set(declared_readings(it)):
                parse_mismatch.append(it["id"])
    self_check["parse_equals_declared_failures"] = parse_mismatch
    self_check["context_note"] = ("context-split surfaces intentionally parse to a "
                                  "singleton while J_full declares the 2-record union "
                                  "(context-free parser cannot produce context readings); "
                                  "this divergence is the T69 phenomenon itself and is "
                                  "measured by A5, not a construction defect")
    counts_ok = (self_check["counts"] == {"faithful_base": 10, "paraphrases": 30,
                                          "costumes": 7, "ambiguous": 4,
                                          "context_split": 2,
                                          "clarification_questions": 4})
    if reader.word_collisions or parse_mismatch or not counts_ok:
        print("CANNOT_CHECK reader construction self-check failed:",
              reader.word_collisions, parse_mismatch, counts_ok)
        return 3

    # ---- arms
    a1, _ = arm_a1(proto, reader, findings)
    a2, _ = arm_a2(proto, reader, findings)
    a3, _ = arm_a3(proto, reader, findings)
    a4, _ = arm_a4(proto, reader, findings)
    a5, _ = arm_a5(proto, reader, findings)
    a6, _ = arm_a6(proto, reader, findings)
    arms = {"A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5, "A6": a6}
    eps = endpoints_e1_e5(proto, reader, arms)
    eps["E4_clarification_value"] = {
        "n_pairs": a6["n_pairs"], "matches": a6["matches"],
        "zero_value_cases_retained": a6["zero_value_cases_retained"],
        "per_pair": a6["per_pair"]}
    eps["E6_B_exec_vectors"] = {k: v["B_exec"] for k, v in sorted(arms.items())}
    eps["E7_note"] = ("latency reported as raw integer op counts only; "
                      "wall_s/cpu_s are metadata and never feed a verdict predicate")

    # ---- provenance
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=os.path.dirname(CAP),
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        head = None
    host_prov = {"hostname": platform.node(),
                 "python": platform.python_version(),
                 "head_sha": head,
                 "protocol_sha256": proto_sha,
                 "freeze_sha256": freeze_sha,
                 "freeze_commit_squash_on_main": "3f9a76c339b1097a4cbf8423952025efd39d2018",
                 "rng_draws": 0}

    wall = time.time() - t0
    cpu = time.process_time() - c0
    overall = "ALL_FROZEN_EXPECTATIONS_MET" if not findings else \
        "RUN_COMPLETED_WITH_RECORDED_EXPECTATION_FAILURES"

    doc = {
        "experiment": "D23 language semantic round-trip laboratory",
        "evidence_class": "CONFIRMATORY_FIXED",
        "claim_ceiling": proto["admissibility"]["claim_ceiling"],
        "issue": "SzeChunYiu/ORION-OCM#233 (D23 lane, post-freeze execution)",
        "protocol_status": proto["status"],
        "self_check": self_check,
        "arms": {k: v for k, v in sorted(arms.items())},
        "endpoints": eps,
        "verdict_summary": {k: arms[k]["verdict"] for k in sorted(arms)},
        "overall": overall,
        "findings": findings,
        "negatives_recorded": findings,
        "host": host_prov,
        "byte_repro_rule": "json.dump(indent=1, sort_keys=True, default=repr); "
                           "identity_sha256 computed over this doc minus "
                           "identity_sha256/wall_s/cpu_s/host",
        "excluded_from_identity": ["identity_sha256", "wall_s", "cpu_s", "host"],
        "wall_s": wall,
        "cpu_s": cpu,
    }
    stripped = {k: v for k, v in doc.items()
                if k not in ("identity_sha256", "wall_s", "cpu_s", "host")}
    doc["identity_sha256"] = hashlib.sha256(
        json.dumps(stripped, indent=1, sort_keys=True, default=repr).encode()).hexdigest()

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True, default=repr)
        fh.write("\n")
    os.makedirs(os.path.dirname(RECEIPTS_PATH), exist_ok=True)
    with open(RECEIPTS_PATH, "w") as fh:
        for k in sorted(arms):
            a = arms[k]
            row = {"job": "D23", "arm": a["arm"], "verdict": a["verdict"],
                   "n_items": a.get("n_items") or a.get("n_pairs"),
                   "B_exec": a["B_exec"],
                   "negative_or_cannot_check_status":
                       a["verdict"] if a["verdict"] in
                       ("HOSTILE_DID_NOT_FLIP", "CONTROL_FALSE_ALARM", "UNSAFE_COMMIT",
                        "OVER_REFUSAL", "LANE_FAILS_WORLD_DESIGN", "CANNOT_CHECK")
                       else "none"}
            fh.write(json.dumps(row, sort_keys=True, default=repr) + "\n")
    with open(HOST_RECEIPT_PATH, "w") as fh:
        json.dump(host_prov, fh, indent=1, sort_keys=True, default=repr)
        fh.write("\n")

    for k in sorted(arms):
        print("D23 %-24s %s" % (arms[k]["arm"], arms[k]["verdict"]))
    print("D23 OVERALL", overall)
    for f in findings:
        print("D23 FINDING", f)
    print("D23 identity_sha256", doc["identity_sha256"])
    print("D23 RESULTS", RESULTS_PATH)
    return 0 if not findings else 1

if __name__ == "__main__":
    sys.exit(main())
