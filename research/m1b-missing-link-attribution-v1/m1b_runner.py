"""M1B ten-arm missing-link-attribution lifecycle runner (machinery only; no scored run).

Extends the proven M1 scaffold (research/m1-native-acquisition/m1_runner.py) under the
frozen protocol research/top-tier-atomic-closure-v1/M1B_MISSING_LINK_ATTRIBUTION_FREEZE_V1.json.
The M1 8-step lifecycle, per-arm checkpoint clones, sealed logs, external CHECKER_C
subprocess pattern and OS-process restart evidence are reused verbatim by importing the
M1 runner as a module; the registered learner src/ocm/learning/methods.py is bound AS-IS
(imported and driven; never copied into this lane, never modified).

The native chain is decomposed into three channels, each transplanted by exactly one
oracle arm and knocked out by exactly one KO arm:

  APPLICABILITY (which fragment helps where)
      APPL_ORACLE  serve only fragments occurring in a minimal derivation of the
                   target's solution (declared info advantage; calibration only);
                   retrieval timing and integration cost stay registered (M.solve).
      APPL_KO      the perfect set is computed, then fragments are physically
                   removed -- must collapse to primitive performance.
  RETRIEVAL TIMING (when to fire)
      RETR_ORACLE  fire exactly at solver choice points where an on-path fragment
                   applies (declared info advantage), never elsewhere; the cost of
                   a fired candidate stays registered (1 slot, no prune relief).
      RETR_KO      the perfect timing signal is computed and recorded per choice
                   point, but retrieval execution is disabled -- must collapse.
  SEARCH INTEGRATION (what an entry costs)
      INTG_ORACLE  on-path fragment entries are placed at the solver's choice
                   points charged ONLY their true enumeration cost (one slot per
                   candidate); off-path guided expansions are pruned uncharged
                   (declared info advantage: zero integration overhead).
      INTG_KO      identical interleaved placement, but every macro is charged as
                   a primitive step sequence (len(program) slots, full cost).

Native and parent arms: RESET, CONTINUED (registered learner as-is; refusal behaviour
intact), STRONG_ADAPTIVE_PARENT (decision-list applicability on frozen normal-form
partition features, own persistence outside OCM bookkeeping, serving the SAME fragments
the dev state mined; parity reported, never interpreted as failure).  KNOWN_STRUCTURE_
ORACLE is rerun unchanged from M1 as the calibration ceiling for recovery shares.

Oracle arms are NEVER headline comparators; their declared info advantages are listed
in this file, the README and every results document this machinery emits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research" / "m1-native-acquisition"))

from ocm.learning import methods as M  # noqa: E402  registered learner, bound AS-IS
import m1_runner as R1  # noqa: E402  proven M1 scaffold, reused verbatim

ARMS = ("RESET", "CONTINUED", "STRONG_ADAPTIVE_PARENT", "APPL_ORACLE", "RETR_ORACLE",
        "INTG_ORACLE", "APPL_KO", "RETR_KO", "INTG_KO", "KNOWN_STRUCTURE_ORACLE")
CALIBRATION_ONLY_ARMS = ("APPL_ORACLE", "RETR_ORACLE", "INTG_ORACLE", "KNOWN_STRUCTURE_ORACLE")

# Frozen worlds, reused BYTE-IDENTICAL (freeze: forbidden[2]).  Verified at every
# phase entry; a mismatch aborts loudly before anything runs.
FROZEN_PARTITIONS_SHA256_PREFIX = "a5b0cbc1814042a7b4ddcfbc8658e63c4b352fade22cfdcd91c1968bea13921e"
FROZEN_PROTECTED_SHA256_PREFIX = "62f199960eecfb0822bc724be9877cef9aa0fa87695917ead50ab4b1d98b236a"
# The dev phase must reproduce the M1 mined-fragment identity when run on the frozen
# worlds (deterministic learner + frozen tasks).  Checked only when explicitly bound.
FROZEN_M1_DEV_FINGERPRINT = "70d8cad4ce2189eebf878eeaa1dc597cb20dbf68d157712b6983505543ed72bc"

DECLARED_INFO_ADVANTAGES = {
    "APPL_ORACLE": "per-task minimal-derivation fragment set (which fragments occur in a "
                   "minimal solution program of THIS target); timing and cost stay registered",
    "RETR_ORACLE": "per-choice-point on-path knowledge (would the next guided candidate "
                   "carry an on-path fragment); fragment set and cost stay registered",
    "INTG_ORACLE": "per-guided-candidate on-path knowledge; on-path entries cost exactly "
                   "one slot (true enumeration cost) and off-path expansions are pruned "
                   "uncharged (zero integration overhead)",
    "KNOWN_STRUCTURE_ORACLE": "the target's true minimum primitive length (M1 arm, unchanged)",
}

HDI14_FAMILIES = ("acquisition_slots", "dev_enumeration_slots", "obligation_slots",
                  "retrieval_events", "retrieval_cost_slots", "max_penalty_tax_slots",
                  "rejected_candidates", "verification_calls", "external_checker_spawns",
                  "storage_bytes", "adapter_storage_bytes", "adaptation_events",
                  "interpreter_restarts", "wall_seconds")

# SELFTEST ONLY relaxation switch: with toy worlds the frozen-hash enforcement is
# replaced by digest RECORDING (mode stamped into every artifact).  The scored run
# never enables this (--selftest-toy-worlds is not in its driver).
WORLDS_MODE = {"toy": False}


class AssayDefect(Exception):
    """Raised when the M1B assay itself is broken (drift, fake restart, bad fixture)."""


def run_files(run_dir: Path):
    return {**R1.run_files(run_dir),
            "strong_parent": run_dir / "strong_parent_store.json",
            "m1b_dir": Path(__file__).resolve().parent}


load_json = R1.load_json
write_json = R1.write_json
events_append = R1.events_append
seal_phase = R1.seal_phase
verify_seals = R1.verify_seals
ledger_update = R1.ledger_update
budget_of = R1.budget_of
tasks_of = R1.tasks_of
checker_C = R1.checker_C


def verify_frozen_worlds(run_dir: Path) -> dict:
    """Fail loudly unless the partitions file and its protected set are byte-identical
    to the frozen M1 worlds (sha256 prefix comparison, two independent checks).
    Toy (selftest) worlds are RECORDED, never enforced, and stamped as such."""
    partitions = load_json(run_files(run_dir)["partitions"])
    raw = (run_files(run_dir)["partitions"]).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    protected = partitions.get("protected_set_sha256", "")
    if WORLDS_MODE["toy"]:
        return {"partitions_sha256": digest, "protected_set_sha256": protected,
                "mode": "toy_selftest_only_NOT_SCORED_EVIDENCE"}
    if digest != FROZEN_PARTITIONS_SHA256_PREFIX:
        raise SystemExit(f"FROZEN_WORLDS_MISMATCH: partitions sha256 {digest} != frozen "
                         f"{FROZEN_PARTITIONS_SHA256_PREFIX}; refusing to run")
    if not protected.startswith(FROZEN_PROTECTED_SHA256_PREFIX[:16]):
        raise SystemExit(f"FROZEN_WORLDS_MISMATCH: protected_set_sha256 {protected} != frozen "
                         f"{FROZEN_PROTECTED_SHA256_PREFIX}; refusing to run")
    return {"partitions_sha256": digest, "protected_set_sha256": protected, "mode": "frozen"}


# ------------------------------------------------------------- oracle knowledge
# Research-lane adapters only.  The oracle never touches the registered learner; it
# derives knowledge from the frozen partitions (min_primitive_length per target) and
# the registered grammar, and exposes it through exactly one channel per oracle arm.

def minimal_solution(row: dict) -> tuple | None:
    """First grammar-order program of minimal length whose normal form solves the row.

    Deterministic: enumerate lengths ascending up to the frozen min_primitive_length;
    the first identity found IS a minimal derivation (grammar order, no tuning)."""
    task = M.PolynomialTask(row["task_id"], row["coefficients"])
    for length in range(row["min_primitive_length"] + 1):
        from itertools import product
        for program in product(M.PRIMITIVES, repeat=length):
            if M.normal_form(program) == task.coefficients:
                return program
    return None


def on_path_fragments(p_star: tuple, library: tuple) -> tuple:
    """Library fragments occurring as PROPER contiguous subsequences of a minimal
    derivation (an occurrence spanning the whole program is not a fragment)."""
    hits = []
    for fragment in library:
        span = len(fragment)
        if span >= len(p_star):
            continue
        if any(p_star[i:i + span] == tuple(fragment) for i in range(len(p_star) - span + 1)):
            hits.append(tuple(fragment))
    return tuple(hits)


class Peekable:
    """Iterator wrapper exposing peek() without consuming (pure observation)."""

    def __init__(self, iterator):
        self._iterator = iterator
        self._buffer = []

    def peek(self):
        if not self._buffer:
            try:
                self._buffer.append(next(self._iterator))
            except StopIteration:
                return None
        return self._buffer[0]

    def __next__(self):
        if self._buffer:
            return self._buffer.pop(0)
        return next(self._iterator)


def guided_token_stream(fragments: tuple, max_length: int):
    """The registered guided stream construction (methods._guided_programs semantics):
    tokens = fragments + single primitives; token products flattened, ascending."""
    from itertools import product
    tokens = tuple(tuple(f) for f in fragments) + tuple((op,) for op in M.PRIMITIVES)
    for length in range(1, max_length + 1):
        for word in product(tokens, repeat=length):
            yield tuple(op for token in word for op in token), word


def guided_first_token_fragment(word: tuple, fragments: tuple):
    """The fragment token leading this guided expansion, if any (None for primitives)."""
    first = tuple(word[0])
    if len(first) >= 2 and first in {tuple(f) for f in fragments}:
        return first
    return None


# ------------------------------------------------- the three transplant channels

def timing_native(slots_used: int, peek_on_path: bool | None) -> bool:
    """REGISTERED retrieval timing: static parity -- fire on odd slots (M.solve)."""
    return slots_used % 2 == 1


def timing_oracle(slots_used: int, peek_on_path: bool | None) -> bool:
    """RETR_ORACLE: fire exactly where an on-path fragment applies, never elsewhere."""
    return bool(peek_on_path)


def cost_native(on_path: bool, program: tuple) -> int:
    """REGISTERED integration cost: every guided candidate costs one slot, useful or not."""
    return 1


def cost_true_enumeration(on_path: bool, program: tuple) -> int:
    """INTG_ORACLE: a placed on-path entry costs exactly its true enumeration cost
    (one slot, one candidate check); off-path expansions never enter (pruned
    uncharged by the placement policy, not by this function)."""
    return 1


def cost_primitive_sequence(on_path: bool, program: tuple) -> int:
    """INTG_KO: the macro is charged as the primitive step sequence it stands for."""
    return max(1, len(program))


def new_instrumentation() -> dict:
    return {"slots": 0, "checked": 0, "guided_checked": 0, "guided_on_path_checked": 0,
            "guided_pruned_uncharged": 0, "retrieval_events": 0, "retrieval_signal_events": 0,
            "retrieval_gt_events": 0, "retrieval_cost_slots": 0, "candidates_rejected": 0,
            "counterexample_rejects": 0, "rank_of_solution": None, "max_penalty_tax_slots": 0}


def adapter_solve(task: M.PolynomialTask, budget: M.SearchBudget, fragments: tuple,
                  timing, costing, p_star: tuple | None = None, execution: bool = True):
    """Research-lane MIRROR of the registered solve loop (methods.solve) with
    transplantable retrieval-timing and integration-cost channels.  Verification
    logic (dedup, counterexample witnesses, normal-form identity, statuses) mirrors
    the registered learner exactly; nothing in src/ocm is read other than as a
    library call.  With timing=timing_native, costing=cost_native, execution=True
    and a fragment set F it reproduces M.solve(task, budget, GeneratorMethod(F)) --
    asserted by the selftest parity hostile.

    p_star is the oracle minimal derivation (None for arms without that channel);
    it is used ONLY through the declared channel of the calling arm.
    """
    instr = new_instrumentation()
    library = tuple(tuple(f) for f in fragments)
    on_path_set = set(on_path_fragments(p_star, library)) if p_star is not None else set()
    baseline = iter(M._primitive_programs(budget.max_length))
    guided = Peekable(guided_token_stream(library, budget.max_length)) if library else None
    intg_placement = costing in (cost_true_enumeration, cost_primitive_sequence)
    seen, counterexamples = set(), [0]
    checked = slots_used = 0

    def reject_on_counterexamples(program):
        return any(M.execute(program, x) != M.evaluate_polynomial(task.coefficients, x)
                   for x in counterexamples)

    while slots_used < budget.slots:
        slots_used += 1
        peek_on_path = None
        if guided is not None:
            peeked = guided.peek()
            if peeked is None:
                if not intg_placement:  # registered behaviour: exhaust -> fall back, slot consumed
                    guided = None
                    instr["max_penalty_tax_slots"] += 1
                    continue
                guided = None  # INTG family: nothing left to place; fall through to baseline
            else:
                peek_program, peek_word = peeked
                lead = guided_first_token_fragment(peek_word, library)
                peek_on_path = bool(lead is not None and lead in on_path_set) if on_path_set else None
        gt_event = bool(peek_on_path)
        instr["retrieval_gt_events"] += int(gt_event)
        fire = False
        if guided is not None and library:
            if execution:
                fire = bool(timing(slots_used, peek_on_path))
            elif timing(slots_used, peek_on_path):
                # KO: the perfect signal FIRES and consumes the retrieval-side stream
                # (the consultation happens), but fragment serving is disabled -- the
                # candidate never enters search and is never charged a slot.
                next(guided)
                instr["retrieval_signal_events"] += 1
        program, cost, from_guided = None, 1, False
        if fire:
            program, _word = next(guided)
            from_guided = True
            instr["retrieval_events"] += 1
            lead = guided_first_token_fragment(_word, library)
            entry_on_path = bool(lead is not None and lead in on_path_set)
            if entry_on_path:
                instr["guided_on_path_checked"] += 1
            cost = costing(entry_on_path, program)
            instr["retrieval_cost_slots"] += cost
        elif guided is not None and intg_placement and slots_used % 2 == 1 and execution:
            # INTG family placement at the registered choice points: pop until an
            # on-path entry appears (off-path expansions pruned UNCHARGED -- the
            # declared zero-overhead advantage), place it, charge via the channel.
            placed = False
            while guided is not None:
                peeked = guided.peek()
                if peeked is None:
                    guided = None
                    break
                peek_program, peek_word = peeked
                lead = guided_first_token_fragment(peek_word, library)
                if lead is not None and lead in on_path_set:
                    program, _word = next(guided)
                    from_guided = True
                    instr["retrieval_events"] += 1
                    instr["guided_on_path_checked"] += 1
                    cost = costing(True, program)
                    instr["retrieval_cost_slots"] += cost
                    placed = True
                    break
                instr["guided_pruned_uncharged"] += 1
                next(guided)
            if not placed:
                try:
                    program = next(baseline)
                except StopIteration:
                    return M.SearchResult(task.fingerprint, "m1b-adapter", "EXHAUSTED_DECLARED_GRAMMAR",
                                          None, slots_used - 1, checked, tuple(counterexamples), budget.max_length), instr
        else:
            try:
                program = next(baseline)
            except StopIteration:
                return M.SearchResult(task.fingerprint, "m1b-adapter", "EXHAUSTED_DECLARED_GRAMMAR",
                                      None, slots_used - 1, checked, tuple(counterexamples), budget.max_length), instr
        if cost > 1 and slots_used - 1 + cost > budget.slots:
            break  # the macro cannot complete inside the remaining budget: censored, unchecked
        slots_used += cost - 1
        if len(program) > budget.max_length or program in seen:
            instr["max_penalty_tax_slots"] += 1
            continue
        seen.add(program)
        checked += 1
        instr["checked"] = checked
        if from_guided:
            instr["guided_checked"] += 1
        if reject_on_counterexamples(program):
            instr["counterexample_rejects"] += 1
            instr["candidates_rejected"] += 1
            continue
        coefficients = M.normal_form(program)
        if coefficients == task.coefficients:
            instr["rank_of_solution"] = checked
            instr["slots"] = slots_used
            return M.SearchResult(task.fingerprint, "m1b-adapter", "VERIFIED_POLYNOMIAL_IDENTITY",
                                  program, slots_used, checked, tuple(counterexamples), budget.max_length), instr
        instr["candidates_rejected"] += 1
        for x in range(max(len(coefficients), len(task.coefficients))):
            if M.evaluate_polynomial(coefficients, x) != M.evaluate_polynomial(task.coefficients, x):
                counterexamples.append(x)
                break
    instr["slots"] = min(slots_used, budget.slots)
    return M.SearchResult(task.fingerprint, "m1b-adapter", "BUDGET_EXHAUSTED", None,
                          instr["slots"], checked, tuple(counterexamples), budget.max_length), instr


def observe_native_retrieval(budget: M.SearchBudget, fragments: tuple, p_star: tuple) -> dict:
    """Observation-only timing trace for arms that search through the REGISTERED path
    (M.solve): replays the registered static-parity firing schedule against the guided
    stream WITHOUT running any search, so retrieval precision/recall vs the perfect
    timing oracle can be reported for every fragment-serving arm.  Pure function of
    (budget, fragments, p_star); it cannot influence any search."""
    library = tuple(tuple(f) for f in fragments)
    on_path_set = set(on_path_fragments(p_star, library)) if p_star is not None else set()
    guided = Peekable(guided_token_stream(library, budget.max_length))
    fired = gt = fired_and_gt = 0
    for slot in range(1, budget.slots + 1):
        if slot % 2 == 0 or guided.peek() is None:
            continue
        _program, word = next(guided)
        fired += 1
        lead = guided_first_token_fragment(word, library)
        hit = bool(lead is not None and lead in on_path_set)
        gt += int(hit)  # the fired event itself is the perfect-timing unit here
        fired_and_gt += int(hit)
    precision = (fired_and_gt / fired) if fired else None
    recall = precision  # every fired event is scored; no unfired on-path events exist
    return {"retrieval_events": fired, "retrieval_gt_events": gt,
            "retrieval_precision_vs_perfect_timing": precision,
            "retrieval_recall_vs_perfect_timing": recall,
            "note": "static-parity schedule observed over the guided stream; precision "
                    "= fraction of registered fires that an on-path fragment leads"}


# ------------------------------------------------ STRONG_ADAPTIVE_PARENT (fit)

def semantic_features(coefficients) -> dict:
    """Frozen normal-form partition axes (m1_partitions.predicate), computed from the
    TARGET the solver faces -- never from any solution."""
    sys.path.insert(0, str(REPO / "research" / "m1-native-acquisition"))
    import m1_partitions as P
    return P.semantic_class(coefficients)


def fit_strong_parent(dev_state: dict, coefficients_by_fingerprint: dict) -> dict:
    """Decision-list applicability policy learned from DEV data only: for every
    condition (each single frozen feature value, then each full class key) the body
    is the set of mined fragments observed on-path in >=1 matching dev solution,
    ordered by observed frequency.  Evaluation order: full class key first (most
    specific), then single-feature rules (fewest matching tasks first = most
    specific), default body = the full mined library.  No held-out task, no
    protected normal form, and no outcome tuning participate in the fit."""
    traces = [t for t in dev_state.get("traces", []) if t.get("outcome") == "SUCCESS"
              and t.get("task") in coefficients_by_fingerprint]
    library = tuple(tuple(f) for f in (dev_state.get("candidates") or {}).get("fragments", []))
    if not traces or not library:
        return {"rules": [], "default": [list(f) for f in library], "fitted": False,
                "training_tasks": 0}
    per_rule: dict[tuple, dict] = {}
    for trace in traces:
        program = tuple(trace["program"]) if trace.get("program") else ()
        if not program:
            continue
        seen_here = set()
        for fragment in library:
            span = len(fragment)
            if span >= len(program):
                continue
            if any(program[i:i + span] == fragment for i in range(len(program) - span + 1)):
                seen_here.add(fragment)
        task = M.PolynomialTask("parentfit:" + trace["task"],
                                coefficients_by_fingerprint[trace["task"]])
        features = semantic_features(task.coefficients)
        keys = [("class", features["degree_band"], features["support_band"], features["coefficient_class"]),
                ("degree_band", features["degree_band"]),
                ("support_band", features["support_band"]),
                ("coefficient_class", features["coefficient_class"])]
        for key in keys:
            slot = per_rule.setdefault(key, {"matches": 0, "counts": {}})
            slot["matches"] += 1
            for fragment in seen_here:
                slot["counts"][fragment] = slot["counts"].get(fragment, 0) + 1
    rules = []
    for key in sorted(per_rule, key=lambda k: (0 if k[0] == "class" else 1, per_rule[k]["matches"])):
        body = sorted(per_rule[key]["counts"], key=lambda f: (-per_rule[key]["counts"][f], f))
        rules.append({"condition_kind": key[0], "condition_value": list(key[1:]) if len(key) > 1 else key[1],
                      "matching_dev_tasks": per_rule[key]["matches"],
                      "body": [list(f) for f in body]})
    fingerprint_payload = {"rules": rules, "default": [list(f) for f in library],
                           "library": [list(f) for f in library],
                           "training_tasks": sorted(t["task"] for t in traces)}
    return {"rules": rules, "default": [list(f) for f in library], "fitted": True,
            "library": [list(f) for f in library],
            "training_tasks": sorted(t["task"] for t in traces),
            "fingerprint": hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode()).hexdigest()}


def strong_parent_serve(store: dict, coefficients) -> dict:
    """Apply the decision list to a TARGET's frozen normal-form features (features of
    the polynomial the solver faces; never of any solution).  First matching rule's
    body is served; with no match the default body (full mined library) is served."""
    features = semantic_features(coefficients)
    full_key = (features["degree_band"], features["support_band"], features["coefficient_class"])
    for rule in store.get("rules", []):
        kind, value = rule["condition_kind"], rule["condition_value"]
        if kind != "class" and isinstance(value, list) and len(value) == 1:
            value = value[0]
        if kind == "class" and list(full_key) == list(value):
            return {"rule": "class:" + "/".join(full_key), "fragments": [tuple(f) for f in rule["body"]],
                    "features": features}
        if kind == "degree_band" and value == full_key[0]:
            return {"rule": "degree_band:" + str(value), "fragments": [tuple(f) for f in rule["body"]],
                    "features": features}
        if kind == "support_band" and value == full_key[1]:
            return {"rule": "support_band:" + str(value), "fragments": [tuple(f) for f in rule["body"]],
                    "features": features}
        if kind == "coefficient_class" and value == full_key[2]:
            return {"rule": "coefficient_class:" + str(value), "fragments": [tuple(f) for f in rule["body"]],
                    "features": features}
    return {"rule": "default:full_library", "fragments": [tuple(f) for f in store.get("default", [])],
            "features": features}


# ------------------------------------------------------------------- phases

def phase_dev(run_dir: Path, slots: int, expected_fingerprint: str | None) -> None:
    """M1 dev phase, reused VERBATIM (solve train tasks, mine fragments, validate,
    admit or refuse, persist ordinary store).  M1B adds only: frozen-worlds
    verification before entry and a dev-identity gate after (the mined fragments
    must reproduce the frozen M1 fingerprint when the frozen worlds are bound)."""
    verify_frozen_worlds(run_dir)
    R1.phase_dev(run_dir, slots)
    ledger_path = run_files(run_dir)["ledger"]
    ledger = load_json(ledger_path)
    ledger["candidate_enumerations_dev"] = ledger.get("candidate_enumerations", 0)
    write_json(ledger_path, ledger)
    if expected_fingerprint and not WORLDS_MODE["toy"]:
        dev_state = load_json(run_files(run_dir)["dev_state"])
        mined = (dev_state.get("candidates") or {}).get("fingerprint")
        if mined != expected_fingerprint:
            raise AssayDefect(f"DEV_IDENTITY_DRIFT: mined fragment fingerprint {mined} != "
                              f"frozen M1 {expected_fingerprint}; worlds or learner drifted")


def phase_checkpoint(run_dir: Path) -> dict:
    """M1 checkpoint (persist runtime, seal dev log, record pre-restart pid) plus the
    STRONG_ADAPTIVE_PARENT fit: the decision list is learned from DEV data only and
    persisted to its OWN store outside OCM bookkeeping, sealed under this phase."""
    started = time.perf_counter()
    verify_frozen_worlds(run_dir)
    checkpoint = R1.phase_checkpoint(run_dir)
    paths = run_files(run_dir)
    partitions = load_json(paths["partitions"])
    dev_state = load_json(paths["dev_state"])
    coefficients = {row["normal_form_digest"]: row["coefficients"]
                    for stream in ("train", "validation") for row in partitions["streams"][stream]}
    store = fit_strong_parent(dev_state, coefficients)
    store["schema"] = "OCM_M1B_STRONG_PARENT_STORE"
    store["note"] = ("outside OCM bookkeeping: plain JSON, own persistence; serves the SAME "
                     "mined fragments the dev state mined, gated by a dev-learned decision "
                     "list on the frozen normal-form partition features; parity reported, "
                     "never interpreted as failure-to-learn")
    write_json(paths["strong_parent"], store)
    events_append(run_dir, "checkpoint", "STRONG_PARENT_FITTED",
                  {"fingerprint": store.get("fingerprint"), "rules": len(store.get("rules", [])),
                   "fitted": store.get("fitted")})
    seal_phase(run_dir, "checkpoint")  # re-seal: the event log grew after R1's seal
    ledger_update(run_dir, phase="checkpoint", phase_wall_seconds=time.perf_counter() - started,
                  interpreter_restarts=0)
    return checkpoint


def timing_intg(slots_used: int, peek_on_path: bool | None) -> bool:
    """INTG family placement: at the registered choice points (odd slots), fire only
    when the next guided entry is on-path (off-path expansions are handled by the
    uncharged prune loop in adapter_solve)."""
    return bool(slots_used % 2 == 1 and peek_on_path)


def classify_failure(status: str, instr: dict) -> str | None:
    """Typed per-stage failure for non-verified rows (freeze: search_behavior_metrics).
    Precedence: enum_exhausted > wrong_fragment > verification_reject > budget_censored."""
    if status == "EXHAUSTED_DECLARED_GRAMMAR":
        return "enum_exhausted"
    if status != "BUDGET_EXHAUSTED":
        return f"UNCLASSIFIED_{status}"
    if instr.get("guided_checked", 0) > 0 and instr.get("guided_on_path_checked", 0) == 0:
        return "wrong_fragment"
    if instr.get("candidates_rejected", 0) > 0:
        return "verification_reject"
    return "budget_censored"


def arm_solve(arm: str, task: M.PolynomialTask, budget: M.SearchBudget, row: dict, ctx: dict):
    """Dispatch one task@rung to its arm's channel configuration.  Returns
    (SearchResult, instrumentation dict, capability note).  Registered machinery
    (M.solve / R1.oracle_solve) is called for every arm whose transplanted channels
    are all native; the research-lane mirror runs only where timing or cost is
    transplanted (asserted natively by the selftest parity hostile)."""
    library = ctx["library"]
    p_star = ctx.get("p_star")
    instr = new_instrumentation()
    if arm == "RESET":
        return M.solve(task, budget), instr, "no learned history; registered primitive search"
    if arm == "CONTINUED":
        if ctx.get("method") is not None:
            return M.solve(task, budget, ctx["method"]), instr, "registered learner as-is"
        return M.solve(task, budget), instr, ctx.get("refusal_reason") or "no admitted generator"
    if arm == "STRONG_ADAPTIVE_PARENT":
        served = strong_parent_serve(ctx["strong_store"], task.coefficients)
        method = M.GeneratorMethod(tuple(served["fragments"]), tuple(ctx["strong_store"].get("training_tasks", ())))
        result = M.solve(task, budget, method)
        observation = observe_native_retrieval(budget, tuple(served["fragments"]), p_star) if p_star else {}
        instr.update({"retrieval_events": observation.get("retrieval_events", 0),
                      "retrieval_gt_events": observation.get("retrieval_gt_events", 0),
                      "retrieval_precision": observation.get("retrieval_precision_vs_perfect_timing"),
                      "retrieval_recall": observation.get("retrieval_recall_vs_perfect_timing"),
                      "rank_of_solution": result.candidates_checked if result.program else None,
                      "slots": result.slots, "checked": result.candidates_checked,
                      "decision_rule": served["rule"]})
        return result, instr, f"decision-list body served ({served['rule']})"
    if arm == "APPL_ORACLE":
        appl = on_path_fragments(p_star, library) if p_star else ()
        if not appl:
            return M.solve(task, budget), instr, "declared set empty: no fragments on-path"
        method = M.GeneratorMethod(appl, ())
        result = M.solve(task, budget, method)
        observation = observe_native_retrieval(budget, appl, p_star) if p_star else {}
        instr.update({"retrieval_events": observation.get("retrieval_events", 0),
                      "retrieval_gt_events": observation.get("retrieval_gt_events", 0),
                      "retrieval_precision": observation.get("retrieval_precision_vs_perfect_timing"),
                      "retrieval_recall": observation.get("retrieval_recall_vs_perfect_timing"),
                      "rank_of_solution": result.candidates_checked if result.program else None,
                      "slots": result.slots, "checked": result.candidates_checked,
                      "fragments_served": len(appl)})
        return result, instr, f"declared minimal-derivation set served ({len(appl)} fragments)"
    if arm == "RETR_ORACLE":
        result, instr = adapter_solve(task, budget, library, timing_oracle, cost_native, p_star)
        return result, instr, "oracle timing; registered cost (1 slot per fired candidate)"
    if arm == "INTG_ORACLE":
        result, instr = adapter_solve(task, budget, library, timing_intg, cost_true_enumeration, p_star)
        return result, instr, "oracle placement; true enumeration cost; off-path pruned uncharged"
    if arm == "APPL_KO":
        appl = on_path_fragments(p_star, library) if p_star else ()
        return (M.solve(task, budget), instr,
                f"perfect set computed ({len(appl)}) then fragments physically removed")
    if arm == "RETR_KO":
        result, instr = adapter_solve(task, budget, library, timing_oracle, cost_native, p_star,
                                      execution=False)
        return result, instr, "oracle timing signal fired and consumed; serving disabled"
    if arm == "INTG_KO":
        result, instr = adapter_solve(task, budget, library, timing_intg, cost_primitive_sequence, p_star)
        return result, instr, "oracle placement; every macro charged len(program) slots"
    if arm == "KNOWN_STRUCTURE_ORACLE":
        return R1.oracle_solve(task, budget, row["min_primitive_length"]), instr, "M1 arm unchanged"
    raise SystemExit(f"UNKNOWN_ARM: {arm}")


def _arm_state_bytes(arm: str, run_dir: Path, dev_state: dict) -> int:
    """storage_bytes: bytes of persisted state the arm LOADS to construct its serving
    capability at acquire time (charge-what-you-carry)."""
    paths = run_files(run_dir)
    if arm == "RESET":
        return 0
    if arm == "CONTINUED":
        clone = run_dir / "ocm_clones" / arm
        return sum(f.stat().st_size for f in clone.rglob("*") if f.is_file()) if clone.exists() else 0
    if arm == "STRONG_ADAPTIVE_PARENT":
        return paths["strong_parent"].stat().st_size if paths["strong_parent"].exists() else 0
    if arm == "KNOWN_STRUCTURE_ORACLE":
        return 0  # serves only frozen per-task class knowledge carried by the worlds
    return len(json.dumps((dev_state.get("candidates") or {}).get("fragments", [])).encode())


def _arm_adapter_bytes(arm: str) -> int:
    """adapter_storage_bytes: the serialized channel declaration the research-lane
    adapter persists for this arm (declared info advantage is stored, hence charged)."""
    if arm in ("RESET", "CONTINUED", "KNOWN_STRUCTURE_ORACLE"):
        return 0
    return len(json.dumps({"arm": arm, "declared_info_advantage":
                           DECLARED_INFO_ADVANTAGES.get(arm, "native channels only")},
                          sort_keys=True).encode())


def phase_acquire(run_dir: Path, arm: str, slots_ladder, targets_n: int) -> dict:
    """M1 lifecycle step 7-8 for one M1B arm, in a FRESH OS process (checked)."""
    started = time.perf_counter()
    verify_frozen_worlds(run_dir)
    paths = run_files(run_dir)
    checkpoint = load_json(paths["checkpoint"])
    if checkpoint["pre_restart_pid"] == os.getpid():
        raise AssayDefect("SAME_PROCESS_FAKE_RESTART: acquire must run in a fresh OS process")
    partitions = load_json(paths["partitions"])
    dev_state = load_json(paths["dev_state"])
    strong_store = load_json(paths["strong_parent"])
    protected_rows = partitions["streams"]["protected"]
    target_rows, obligation_rows = protected_rows[:targets_n], protected_rows[targets_n:]
    library = tuple(tuple(f) for f in (dev_state.get("candidates") or {}).get("fragments", []))
    ctx = {"library": library, "strong_store": strong_store, "method": None, "refusal_reason": None}
    if arm == "CONTINUED":
        if dev_state.get("generator_id"):
            from ocm.runtime.ocm_runtime import OCMRuntime
            runtime = OCMRuntime(R1.clone_ocm_root(run_dir, arm))
            ctx["method"] = M.load_generator(runtime, dev_state["generator_id"])
        else:
            ctx["refusal_reason"] = ("NO_ADMITTED_GENERATOR (learner refused deployment at "
                                     "dev time; refusal behaviour intact)")
    elif arm == "RESET":
        R1.clone_ocm_root(run_dir, arm)
    rows, obligations, verification_calls, external_spawns = [], [], 0, 0
    adaptation_events = 0
    oracle_arms = ("STRONG_ADAPTIVE_PARENT", "APPL_ORACLE", "RETR_ORACLE", "INTG_ORACLE",
                   "APPL_KO", "RETR_KO", "INTG_KO")
    p_star_cache: dict[str, tuple | None] = {}

    def p_star_for(row):
        key = row["normal_form_digest"]
        if key not in p_star_cache:
            p_star_cache[key] = minimal_solution(row)
        return p_star_cache[key]

    for row in target_rows:
        task = M.PolynomialTask(row["task_id"], row["coefficients"])
        ctx["p_star"] = p_star_for(row) if arm in oracle_arms else None
        if arm in oracle_arms:
            adaptation_events += 1  # oracle/adapter computation charged per task
        for slots in slots_ladder:
            budget = budget_of(partitions, slots)
            result, instr, note = arm_solve(arm, task, budget, row, ctx)
            verification_calls += 1
            verdict = None
            if result.program is not None:
                verdict = checker_C(row["coefficients"], result.program)
                external_spawns += 1
                verification_calls += 1
            instr = dict(instr)
            if not instr.get("retrieval_cost_slots") and instr.get("retrieval_events"):
                # registered-path arms: native integration cost is exactly one slot per fire
                instr["retrieval_cost_slots"] = instr["retrieval_events"]
            instr["typed_failure"] = (None if result.program is not None
                                      else classify_failure(result.status, instr))
            precision = instr.get("retrieval_precision")
            recall = instr.get("retrieval_recall")
            if precision is None and instr.get("retrieval_events"):
                fired, gt = instr["retrieval_events"], instr["retrieval_gt_events"]
                precision = gt / fired if fired else None
                recall = precision  # depth-matched construction; see README
                instr["retrieval_precision"], instr["retrieval_recall"] = precision, recall
            rows.append({"arm": arm, "target": row["normal_form_digest"],
                         "semantic_class": row["semantic_class"],
                         "min_primitive_length": row["min_primitive_length"],
                         "budget_slots": slots, "B_slots": result.slots,
                         "B_candidates_checked": result.candidates_checked,
                         "status": result.status,
                         "checker_verdict": verdict["verdict"] if verdict else None,
                         "checker_pid": verdict["pid"] if verdict else None,
                         "checker_methods_sha256": verdict["methods_sha256"] if verdict else None,
                         "verified_external": bool(verdict and verdict["verdict"] == "IDENTICAL"),
                         "refused": bool(ctx["refusal_reason"]), "censored": False,
                         "note": note, "search_behavior": instr})
    for row in obligation_rows:
        task = M.PolynomialTask(row["task_id"], row["coefficients"])
        ctx["p_star"] = p_star_for(row) if arm in oracle_arms else None
        budget = budget_of(partitions, slots_ladder[-1])
        result, instr, _note = arm_solve(arm, task, budget, row, ctx)
        verification_calls += 1
        verdict = checker_C(row["coefficients"], result.program) if result.program is not None else None
        external_spawns += 1 if verdict else 0
        verification_calls += 1 if verdict else 0
        obligations.append({"arm": arm, "target": row["normal_form_digest"],
                            "B_slots": result.slots, "B_candidates_checked": result.candidates_checked,
                            "status": result.status,
                            "verified_external": bool(verdict and verdict["verdict"] == "IDENTICAL"),
                            "censored": False})
    def total(field):
        return sum((r["search_behavior"] or {}).get(field, 0) for r in rows)
    run_ledger = load_json(paths["ledger"])
    uses_dev_history = arm != "RESET"
    hdi14 = {
        "acquisition_slots": sum(r["B_slots"] for r in rows),
        "dev_enumeration_slots": (run_ledger.get("candidate_enumerations_dev") or 0) if uses_dev_history else 0,
        "obligation_slots": sum(r["B_slots"] for r in obligations),
        "retrieval_events": total("retrieval_events") + total("retrieval_signal_events"),
        "retrieval_cost_slots": total("retrieval_cost_slots"),
        "max_penalty_tax_slots": total("max_penalty_tax_slots"),
        "rejected_candidates": total("candidates_rejected"),
        "verification_calls": verification_calls,
        "external_checker_spawns": external_spawns,
        "storage_bytes": _arm_state_bytes(arm, run_dir, dev_state),
        "adapter_storage_bytes": _arm_adapter_bytes(arm),
        "adaptation_events": adaptation_events + total("retrieval_signal_events"),
        "interpreter_restarts": 1,
        "wall_seconds": round(time.perf_counter() - started, 6),
    }
    missing = [family for family in HDI14_FAMILIES if family not in hdi14]
    if missing:
        raise AssayDefect(f"HDI14_INCOMPLETE: {missing}")
    report = {"schema": "OCM_M1B_ARM_REPORT", "arm": arm,
              "calibration_only": arm in CALIBRATION_ONLY_ARMS,
              "declared_info_advantage": DECLARED_INFO_ADVANTAGES.get(arm),
              "process": {"pid": os.getpid(), "pre_restart_pid": checkpoint["pre_restart_pid"],
                          "pid_changed": os.getpid() != checkpoint["pre_restart_pid"],
                          "boot_token_inherited": checkpoint["boot_token"]},
              "capability_state": {"fragments_served": (0 if arm in ("RESET", "APPL_KO") else len(library)),
                                   "library_size": len(library),
                                   "refusal_reason": ctx["refusal_reason"],
                                   "note": "see per-row notes"},
              "acquisition_rows": rows, "obligation_rows": obligations,
              "refusal_rate": (sum(1 for r in rows if r["refused"]) / len(rows)) if rows else None,
              "cost_ledger_hdi14": hdi14}
    write_json(paths["arms"] / f"{arm}.json", report)
    events_append(run_dir, f"acquire_{arm}", "ARM_REPORT",
                  {"arm": arm, "rows": len(rows), "obligations": len(obligations),
                   "refusal_rate": report["refusal_rate"]})
    seal_phase(run_dir, f"acquire_{arm}")
    ledger_update(run_dir, phase=f"acquire_{arm}", phase_wall_seconds=hdi14["wall_seconds"],
                  interpreter_restarts=1, candidate_enumerations=sum(r["B_candidates_checked"] for r in rows + obligations),
                  verification_calls=verification_calls)
    return report


def phase_restart_and_acquire(run_dir: Path, arm: str, slots_ladder, targets_n: int,
                              timeout: int = 7200) -> dict:
    """REAL OS-PROCESS RESTART (M1 pattern verbatim): spawn a fresh interpreter that
    loads persisted state and runs --phase acquire for this arm.  The child's own
    report carries its pid; the receipt cross-checks pids and fails closed."""
    child_args = [sys.executable, str(Path(__file__).resolve()), "--run-dir", str(run_dir),
                  "--phase", "acquire", "--arm", arm,
                  "--slots-ladder", ",".join(str(s) for s in slots_ladder),
                  "--targets", str(targets_n)]
    if WORLDS_MODE["toy"]:
        child_args.append("--selftest-toy-worlds")
    child = subprocess.run(child_args, capture_output=True, text=True, timeout=timeout)
    receipt = {"arm": arm, "parent_pid": os.getpid(), "child_pid": None,
               "child_returncode": child.returncode, "child_stderr_tail": child.stderr[-400:]}
    report_path = run_files(run_dir)["arms"] / f"{arm}.json"
    if child.returncode != 0 or not report_path.exists():
        write_json(report_path,
                   {"schema": "OCM_M1B_ARM_REPORT", "arm": arm, "censored_whole_arm": True,
                    "restart_receipt": receipt, "acquisition_rows": [], "obligation_rows": [],
                    "refusal_rate": None, "cost_ledger_hdi14": {},
                    "censor_reason": f"child exited {child.returncode}"})
        events_append(run_dir, f"acquire_{arm}", "ARM_CENSORED",
                      {"arm": arm, "returncode": child.returncode})
        seal_phase(run_dir, f"acquire_{arm}")
        raise SystemExit(f"ARM_CENSORED: {arm} child exit {child.returncode}: {child.stderr[-300:]}")
    report = load_json(report_path)
    report["restart_receipt"] = {**receipt, "child_pid": report["process"]["pid"]}
    write_json(report_path, report)
    if report["process"]["pid"] == os.getpid():
        raise AssayDefect("RESTART_EVIDENCE_FAILED: child pid equals parent pid")
    if report["process"]["pid"] == report["process"]["pre_restart_pid"]:
        raise AssayDefect("RESTART_EVIDENCE_FAILED: child pid equals checkpoint pre-restart pid")
    return report


M1B_CLAIM_CEILING = ("Attribution of M1's NO_NATIVE_EFFECT to applicability / retrieval timing / "
                     "search integration at THIS assay scope ONLY: frozen worlds, frozen registered "
                     "learner bound as-is, ten arms, declared info advantages.  Calibration-oracle "
                     "arms are never headline comparators.  No economics claim, no OCM-residual "
                     "claim, no open-endedness claim, and no claim about any unfrozen family is "
                     "supported by this machinery or any run it produces.")


def _typed_failure_histogram(rows: list) -> dict:
    hist: dict[str, int] = {}
    for r in rows:
        tf = (r.get("search_behavior") or {}).get("typed_failure")
        if tf:
            hist[tf] = hist.get(tf, 0) + 1
    return dict(sorted(hist.items()))


def _retrieval_aggregate(rows: list) -> dict:
    precisions = [(r["search_behavior"] or {}).get("retrieval_precision")
                  for r in rows if (r["search_behavior"] or {}).get("retrieval_precision") is not None]
    events = sum((r["search_behavior"] or {}).get("retrieval_events", 0) for r in rows)
    onpath = sum((r["search_behavior"] or {}).get("guided_on_path_checked", 0) for r in rows)
    return {"mean_retrieval_precision": (sum(precisions) / len(precisions)) if precisions else None,
            "retrieval_events": events, "guided_on_path_checked": onpath}


def phase_summarize(run_dir: Path) -> dict:
    """Deterministic M1B summary: seals verified fail-closed, leakage check, per-arm
    aggregates, matched-key paired burden tables, recovery shares vs KNOWN_STRUCTURE_
    ORACLE, KO collapse checks, typed failures, HDI-14 rollup, calibration quarantine,
    terminal per the frozen precedence (computed in m1b_stats)."""
    started = time.perf_counter()
    import m1b_stats as S1
    paths = run_files(run_dir)
    seals = verify_seals(run_dir)  # fail closed on any tampered sealed log
    worlds = verify_frozen_worlds(run_dir)
    partitions = load_json(paths["partitions"])
    dev_state = load_json(paths["dev_state"])
    protected_digests = {row["normal_form_digest"] for row in partitions["streams"]["protected"]}
    history_digests = {row["normal_form_digest"] for stream in ("train", "validation", "test")
                       for row in partitions["streams"][stream]}
    history_digests |= {t["task"] for t in dev_state.get("traces", [])}
    leakage = sorted(history_digests & protected_digests)
    arms: dict[str, dict] = {}
    for arm_file in sorted(paths["arms"].glob("*.json")):
        report = json.loads(arm_file.read_text(encoding="utf-8"))
        arms[report["arm"]] = report
    assay_defect = any(r.get("assay_defect") for r in arms.values())
    ladder_top = max((r["budget_slots"] for report in arms.values()
                      for r in report.get("acquisition_rows", [])), default=None)
    paired = {}
    for arm, report in arms.items():
        rows = [r for r in report.get("acquisition_rows", []) if not r.get("censored")]
        top_rows = [r for r in rows if ladder_top and r["budget_slots"] == ladder_top]
        paired[arm] = {"mean_B_top": (sum(r["B_slots"] for r in top_rows) / len(top_rows)) if top_rows else None,
                       "mean_B_all": (sum(r["B_slots"] for r in rows) / len(rows)) if rows else None,
                       "successes": sum(1 for r in rows if r.get("verified_external")),
                       "attempts": len(rows), "refusal_rate": report.get("refusal_rate"),
                       "censored_whole_arm": bool(report.get("censored_whole_arm")),
                       "typed_failures": _typed_failure_histogram(rows),
                       "retrieval": _retrieval_aggregate(rows),
                       "cost_ledger_hdi14": report.get("cost_ledger_hdi14", {})}
    keyed = {}
    for arm, report in arms.items():
        keyed[arm] = {r["target"] + "@" + str(r["budget_slots"]): r["B_slots"]
                      for r in report.get("acquisition_rows", []) if not r.get("censored")}
    vs_reset = {arm: S1.paired_vs_reset(keyed, arm) for arm in arms if arm != "RESET"}
    recovery = {arm: S1.recovery_share(keyed, arm) for arm in arms
                if arm not in ("RESET",) and keyed.get(arm)}
    lifetime_recovery = {arm: S1.recovery_share(keyed, arm,
                                                dev_slots=(arms[arm].get("cost_ledger_hdi14", {})
                                                           .get("dev_enumeration_slots", 0)),
                                                n_targets=max(1, paired[arm]["attempts"] // max(1, len(set(
                                                    r["target"] for r in arms[arm].get("acquisition_rows", []))))))
                         for arm in arms if arm not in ("RESET",) and keyed.get(arm)}
    ko_checks = {arm: S1.ko_collapse_check(recovery.get(arm), vs_reset.get(arm))
                 for arm in ("APPL_KO", "RETR_KO", "INTG_KO") if arm in arms}
    forced_fragment = {arm: S1.forced_fragment_check(arms[arm])
                       for arm in ("APPL_KO",) if arm in arms}
    refusal = S1.refusal_correctness_check(arms)
    direction = {arm: S1.direction_tests(keyed, arm) for arm in arms if arm != "RESET" and keyed.get(arm)}
    hdi14_rollup = {arm: report.get("cost_ledger_hdi14", {}) for arm, report in arms.items()}
    hdi14_missing = {arm: [f for f in HDI14_FAMILIES if f not in report.get("cost_ledger_hdi14", {})]
                     for arm, report in arms.items()}
    if any(hdi14_missing.values()):
        assay_defect = True
    censored_rows = sum(1 for report in arms.values()
                        for r in report.get("acquisition_rows", []) + report.get("obligation_rows", [])
                        if r.get("censored"))
    censored_arms = [arm for arm, report in arms.items() if report.get("censored_whole_arm")]
    summary = {
        "schema": "OCM_M1B_SUMMARY", "deterministic": True, "seals_verified": seals,
        "worlds": worlds, "arms_present": sorted(arms), "ladder_top": ladder_top,
        "leakage_alarm": bool(leakage), "leakage_shared": leakage,
        "insufficient_history": dev_state.get("terminal") == "INSUFFICIENT_HISTORY",
        "assay_defect": assay_defect, "hdi14_missing_families": hdi14_missing,
        "paired": paired, "paired_vs_reset": vs_reset,
        "recovery_share_vs_known_structure_oracle": recovery,
        "recovery_share_lifetime_charged": lifetime_recovery,
        "ko_collapse": ko_checks, "forced_fragment_negative": forced_fragment,
        "refusal_correctness": refusal, "direction_tests": direction,
        "censored_rows": censored_rows, "censored_arms": censored_arms,
        "cost_ledger_hdi14": hdi14_rollup,
        "registered_margin": S1.MARGIN,
        "calibration_reference_ONLY": {a: paired[a] for a in CALIBRATION_ONLY_ARMS if a in paired},
        "claim_ceiling": M1B_CLAIM_CEILING,
    }
    summary["terminal"] = S1.map_terminal(summary)
    write_json(paths["summary"], summary)
    ledger_update(run_dir, phase="summarize", phase_wall_seconds=time.perf_counter() - started)
    print(json.dumps({"terminal": summary["terminal"], "arms": sorted(arms),
                      "censored_arms": censored_arms}, sort_keys=True))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--phase", required=True,
                        choices=["dev", "checkpoint", "acquire", "restart-and-acquire", "summarize"])
    parser.add_argument("--arm", choices=ARMS)
    parser.add_argument("--slots", type=int, default=2000)
    parser.add_argument("--slots-ladder", default="2000")
    parser.add_argument("--targets", type=int, default=2,
                        help="protected rows used as acquisition targets; the rest are obligations")
    parser.add_argument("--expected-dev-fingerprint", default=None,
                        help="bind the dev phase to a frozen mined-fragment fingerprint")
    parser.add_argument("--selftest-toy-worlds", action="store_true",
                        help="SELFTEST ONLY: toy (unfrozen) worlds; recorded in every artifact; "
                             "the scored run never passes this flag")
    args = parser.parse_args()
    if args.selftest_toy_worlds:
        WORLDS_MODE["toy"] = True
    ladder = [int(s) for s in args.slots_ladder.split(",") if s]
    run_dir: Path = args.run_dir
    if args.phase == "dev":
        phase_dev(run_dir, args.slots, args.expected_dev_fingerprint)
    elif args.phase == "checkpoint":
        phase_checkpoint(run_dir)
    elif args.phase == "acquire":
        if not args.arm:
            raise SystemExit("--arm is required for --phase acquire")
        phase_acquire(run_dir, args.arm, ladder, args.targets)
    elif args.phase == "restart-and-acquire":
        if not args.arm:
            raise SystemExit("--arm is required for --phase restart-and-acquire")
        phase_restart_and_acquire(run_dir, args.arm, ladder, args.targets)
    elif args.phase == "summarize":
        phase_summarize(run_dir)


if __name__ == "__main__":
    main()
