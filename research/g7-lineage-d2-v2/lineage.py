"""G7 persistent developmental lineage — D2 successor vessel.

Continues lineage id orion-ocm-g7-lineage-v1:microscope-d0-d1 through a third
earned DevelopmentTransitionV1 (OCM_1 → OCM_2). Serialises the whole earned
bundle, restarts by loading it, and refuses a tampered digest. Reset stores
cannot read continued-arm files. Constitution C is frozen.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
import os
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "schema.json"
PRIMITIVES = ("inc", "dec", "double", "square")
MACRO_TOKEN = "MACRO"
LINEAGE_ID = "orion-ocm-g7-lineage-v1:microscope-d0-d1"
GRAMMAR_ID = "g7.polynomial-total-arithmetic.v1"
D2_GRAMMAR_ID = "g7.diagnosis-probe-planning.v1"
CONSTITUTION = ("check", "authority", "meter", "commit")
D2_MODULES = 6
D2_SYNDROME_WINDOWS = ((0, 1, 2), (2, 3, 4), (4, 5, 0), (1, 3, 5))
PROBE_COST = 1
REPLACE_COST = 4
PERSIST_SLOTS = (
    "field_state",
    "learned_methods",
    "method_schemas",
    "imported_donors",
    "applicability_scope",
    "failure_counterexample_knowledge",
    "representations",
    "support_dependency",
    "acquisition_strategies",
    "executive_metareasoning_policy",
    "self_model",
    "self_change_history",
    "resource_history",
)
STAGES = ("EMPTY", "OCM_0", "OCM_1", "OCM_2", "OCM_3", "OCM_4", "OCM_5", "OCM_6")
UNRUN_STAGES = ("OCM_3", "OCM_4", "OCM_5", "OCM_6")
LATER_AT_SEED = ("OCM_2", "OCM_3", "OCM_4", "OCM_5", "OCM_6")
D2_POLICY_ROUND_ROBIN = "ROUND_ROBIN"
D2_POLICY_GREEDY = "GREEDY_POSTERIOR_SPLIT"
D2_POLICY_PROBE_ALL = "PROBE_ALL"
ORIGIN_TAUGHT = "TAUGHT_IMPORTED"
ORIGIN_APPLICABILITY = "LEARNED_APPLICABILITY"
ORIGIN_COMPOSITION = "LEARNED_COMPOSITION"
ORIGIN_REDISCOVERY = "INDEPENDENT_REDISCOVERY"
BUNDLE_FILE = "bundle.json"
ARMS = ("CONTINUED_OCM", "RESET_OCM", "TASK_SPECIFIC_OCM", "STRONG_ADAPTIVE_PARENT")


class DigestTamperError(RuntimeError):
    """Loading a bundle whose digest does not match the payload."""


class IsolationError(RuntimeError):
    """A store attempted to read or write outside its root, or into another arm."""


class SchemaError(ValueError):
    """DevelopmentTransitionV1 failed the G7 schema."""


class ConstitutionMutationError(RuntimeError):
    """C is frozen; a store or admit attempted to rewrite it."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def stable_rank(salt: str, fingerprint: str) -> str:
    return hashlib.sha256((salt + "\0" + fingerprint).encode()).hexdigest()


def execute(program, x):
    value = Fraction(x)
    for op in program:
        if op == "inc":
            value += 1
        elif op == "dec":
            value -= 1
        elif op == "double":
            value *= 2
        elif op == "square":
            value *= value
        else:
            raise ValueError(f"unknown primitive {op}")
    return value


def normal_form(program):
    coefficients = [Fraction(0), Fraction(1)]
    for op in program:
        if op == "inc":
            coefficients[0] += 1
        elif op == "dec":
            coefficients[0] -= 1
        elif op == "double":
            coefficients = [2 * c for c in coefficients]
        elif op == "square":
            squared = [Fraction(0)] * (2 * len(coefficients) - 1)
            for i, a in enumerate(coefficients):
                for j, b in enumerate(coefficients):
                    squared[i + j] += a * b
            coefficients = squared
        else:
            raise ValueError(f"unknown primitive {op}")
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    return tuple(coefficients)


def polynomial_degree(coefficients) -> int:
    return max(0, len(tuple(coefficients)) - 1)


def task_id(coefficients) -> str:
    return content_hash({"domain": GRAMMAR_ID, "coefficients": [str(c) for c in coefficients]})


def taught_donors():
    return [
        {
            "identity": f"donor:primitive:{op}",
            "kind": "primitive",
            "origin_category": ORIGIN_TAUGHT,
            "payload": {"operator": op, "grammar": GRAMMAR_ID},
        }
        for op in PRIMITIVES
    ]


def empty_bundle(lineage_id: str = LINEAGE_ID) -> dict:
    donors = taught_donors()
    return {
        "schema": "ocm.g7.persistent-bundle.v1",
        "lineage_id": lineage_id,
        "stage": "EMPTY",
        "field_state": {"atoms": [], "notes": "seed field; no earned claims"},
        "learned_methods": [],
        "method_schemas": [],
        "imported_donors": donors,
        "applicability_scope": [],
        "failure_counterexample_knowledge": [],
        "representations": [
            {
                "identity": "rep:coefficient-normal-form.v1",
                "origin_category": ORIGIN_TAUGHT,
                "payload": {"kind": "univariate-rational-coefficients"},
            }
        ],
        "support_dependency": {"edges": []},
        "acquisition_strategies": [
            {
                "identity": "strategy:exact-macro-token-bfs.v1",
                "origin_category": ORIGIN_TAUGHT,
                "payload": {"algorithm": "exact token-word BFS with one optional MACRO"},
            }
        ],
        "executive_metareasoning_policy": {
            "identity": "pi:domain-general-exact-search.v1",
            "origin_category": ORIGIN_TAUGHT,
            "payload": {
                "rule": (
                    "serve admitted macros on the polynomial family; apply scoped "
                    "failure nogoods; serve D2 probe policy on the diagnosis family; "
                    "do not rewrite C"
                ),
                "constitution": list(CONSTITUTION),
            },
        },
        "self_model": {
            "identity": "self:g7-microscope-v1",
            "stage": "EMPTY",
            "known_competence": [],
            "unknown": list(LATER_AT_SEED),
        },
        "self_change_history": [],
        "resource_history": [],
    }


def constitution_of(bundle: dict) -> tuple:
    payload = (bundle.get("executive_metareasoning_policy") or {}).get("payload") or {}
    value = payload.get("constitution")
    if not isinstance(value, list):
        raise ConstitutionMutationError("constitution missing from executive policy")
    return tuple(value)


def assert_constitution_frozen(bundle: dict) -> None:
    if constitution_of(bundle) != CONSTITUTION:
        raise ConstitutionMutationError("constitution C mutated; load/persist fails closed")


def mutate_constitution(bundle: dict, new_c) -> dict:
    """Hostile helper: rewriting C is refused."""
    clone = json.loads(canonical_json(bundle))
    clone["executive_metareasoning_policy"]["payload"]["constitution"] = list(new_c)
    raise ConstitutionMutationError("C is not a writable slot")


def bundle_digest(bundle: dict) -> str:
    payload = {k: v for k, v in bundle.items() if k != "digest"}
    return content_hash(payload)


def machine_identity(bundle: dict) -> str:
    return bundle_digest(bundle)


def envelope(bundle: dict) -> dict:
    digest = bundle_digest(bundle)
    return {"schema": "ocm.g7.persistent-envelope.v1", "digest": digest, "bundle": bundle}


def count_objects(bundle: dict) -> int:
    n = 0
    for slot in PERSIST_SLOTS:
        value = bundle[slot]
        if isinstance(value, list):
            n += len(value)
        elif isinstance(value, dict):
            n += 1
        elif value:
            n += 1
    return n


def active_objects(bundle: dict) -> list[str]:
    ids = []
    for method in bundle["learned_methods"]:
        ids.append(method["identity"])
    for rec in bundle["failure_counterexample_knowledge"]:
        ids.append(rec["identity"])
    for donor in bundle["imported_donors"]:
        ids.append(donor["identity"])
    return ids


class LineageStore:
    """One arm's on-disk root. Paths outside the root are refused."""

    def __init__(self, root: Path, role: str):
        if role not in ARMS:
            raise ValueError(f"unknown arm {role}")
        self.root = Path(root).resolve()
        self.role = role
        self.root.mkdir(parents=True, exist_ok=True)
        role_file = self.root / "ARM"
        if role_file.exists():
            recorded = role_file.read_text(encoding="utf-8").strip()
            if recorded != role:
                raise IsolationError(f"store at {self.root} is arm {recorded}, not {role}")
        else:
            role_file.write_text(role + "\n", encoding="utf-8")

    def _inside(self, path: Path) -> Path:
        resolved = Path(path).resolve()
        if not resolved.is_relative_to(self.root):
            raise IsolationError(f"{self.role} store refused path outside root: {resolved}")
        return resolved

    def persist(self, bundle: dict) -> Path:
        if self.role == "CONTINUED_OCM" and bundle.get("lineage_id") != LINEAGE_ID:
            raise IsolationError(
                "continued arm may persist only lineage %s, got %r"
                % (LINEAGE_ID, bundle.get("lineage_id"))
            )
        assert_constitution_frozen(bundle)
        path = self._inside(self.root / BUNDLE_FILE)
        payload = envelope(bundle)
        temp = path.with_suffix(".tmp")
        if temp.exists():
            temp.unlink()
        with temp.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        fd = os.open(self.root, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        return path

    def load(self) -> dict:
        path = self._inside(self.root / BUNDLE_FILE)
        if not path.is_file():
            raise FileNotFoundError(str(path))
        payload = json.loads(path.read_text(encoding="utf-8"))
        bundle = payload["bundle"]
        expected = payload.get("digest")
        observed = bundle_digest(bundle)
        if expected != observed:
            raise DigestTamperError("persistent-state digest mismatch; load fails closed")
        assert_constitution_frozen(bundle)
        return bundle


def assert_disjoint_stores(continued: LineageStore, reset: LineageStore) -> None:
    if continued.root == reset.root:
        raise IsolationError("reset arm shares continued root")
    if reset.root.is_relative_to(continued.root) or continued.root.is_relative_to(reset.root):
        raise IsolationError("reset arm nested under continued store")
    foreign = reset.root / BUNDLE_FILE
    if foreign.exists() and foreign.resolve().is_relative_to(continued.root):
        raise IsolationError("reset arm can see continued bundle")


def proper_fragments(program, min_length=2, max_length=3):
    out = set()
    program = tuple(program)
    for start in range(len(program)):
        stop = min(len(program), start + max_length)
        for end in range(start + min_length, stop + 1):
            fragment = tuple(program[start:end])
            if len(fragment) < len(program):
                out.add(fragment)
    return out


def expand_tokens(token_word, macro):
    expanded = []
    used = False
    for token in token_word:
        if token == MACRO_TOKEN:
            if macro is None:
                raise ValueError("macro token without macro")
            expanded.extend(macro)
            used = True
        else:
            if token not in PRIMITIVES:
                raise ValueError(f"unknown token {token}")
            expanded.append(token)
    return tuple(expanded), used


def degree_dead_end(macro, target_coefficients) -> bool:
    if macro is None:
        return False
    return polynomial_degree(normal_form(macro)) > polynomial_degree(target_coefficients)


def build_search_index(macro, max_primitive_length: int, failure_records=()):
    macro = tuple(macro) if macro is not None else None
    tokens = ((MACRO_TOKEN,) + PRIMITIVES) if macro is not None else PRIMITIVES
    skip_macro_first = any(
        rec.get("pattern") == "MACRO_AT_EMPTY_PREFIX" and rec.get("active")
        for rec in failure_records
    )
    seen_programs = set()
    first_by_coefficients = {}
    enumeration_attempts = 0
    unique_candidates_checked = 0
    skipped_by_failure = 0
    for token_depth in range(max_primitive_length + 1):
        for token_word in product(tokens, repeat=token_depth):
            if skip_macro_first and token_word and token_word[0] == MACRO_TOKEN:
                skipped_by_failure += 1
                continue
            expanded, macro_used = expand_tokens(token_word, macro)
            if len(expanded) > max_primitive_length:
                continue
            enumeration_attempts += 1
            if expanded in seen_programs:
                continue
            seen_programs.add(expanded)
            unique_candidates_checked += 1
            coefficients = normal_form(expanded)
            first_by_coefficients.setdefault(coefficients, {
                "enumeration_attempts": enumeration_attempts,
                "unique_candidates_checked": unique_candidates_checked,
                "token_word": token_word,
                "program": expanded,
                "macro_used": macro_used,
            })
    return {
        "macro": macro,
        "max_primitive_length": max_primitive_length,
        "total_enumeration_attempts": enumeration_attempts,
        "total_unique_candidates_checked": unique_candidates_checked,
        "skipped_by_failure": skipped_by_failure,
        "first_by_coefficients": first_by_coefficients,
    }


def solve_from_index(coefficients, index):
    hit = index["first_by_coefficients"].get(tuple(coefficients))
    if hit is None:
        raise RuntimeError(f"grammar failed to solve {task_id(coefficients)}")
    if normal_form(tuple(hit["program"])) != tuple(coefficients):
        raise RuntimeError("exact verification failed")
    return {
        "task": task_id(coefficients),
        "enumeration_attempts": hit["enumeration_attempts"],
        "unique_candidates_checked": hit["unique_candidates_checked"],
        "token_word": list(hit["token_word"]),
        "program": list(hit["program"]),
        "macro_used": hit["macro_used"],
        "verified": True,
    }


def evaluate_index(tasks, index):
    rows = [solve_from_index(task["coefficients"], index) for task in tasks]
    return rows, sum(row["enumeration_attempts"] for row in rows), sum(
        row["unique_candidates_checked"] for row in rows
    )


def population_by_min_length(max_length: int):
    best = {}
    for length in range(max_length + 1):
        for program in product(PRIMITIVES, repeat=length):
            coefficients = normal_form(program)
            fingerprint = task_id(coefficients)
            best.setdefault(fingerprint, (length, coefficients, program))
    return best


def take_stratum(population, length: int, salt: str, n: int, exclude=(), require_square=None):
    excluded = set(exclude)
    pool = []
    for fingerprint, (minimum, coefficients, program) in population.items():
        if minimum != length or fingerprint in excluded:
            continue
        has_square = "square" in program
        if require_square is True and not has_square:
            continue
        if require_square is False and has_square:
            continue
        pool.append({
            "fingerprint": fingerprint,
            "coefficients": coefficients,
            "min_length": minimum,
            "witness_program": program,
        })
    chosen = tuple(sorted(
        pool,
        key=lambda task: (stable_rank(salt, task["fingerprint"]), task["fingerprint"]),
    )[:n])
    if len(chosen) != n:
        raise RuntimeError(
            f"stratum length={length} square={require_square} too small: {len(chosen)} < {n}"
        )
    return chosen


def solve_training(tasks, max_length: int):
    index = build_search_index(None, max_length)
    rows = []
    total = 0
    for task in tasks:
        row = solve_from_index(task["coefficients"], index)
        rows.append((task, row))
        total += row["enumeration_attempts"]
    return tuple(rows), total


def candidate_pool(training_rows, cap=8, min_support=2, require_square=False):
    support = Counter()
    for _task, result in training_rows:
        support.update(proper_fragments(result["program"]))
    eligible = [
        fragment for fragment, count in support.items()
        if count >= min_support and (not require_square or "square" in fragment)
    ]
    candidates = tuple(sorted(
        eligible,
        key=lambda fragment: (-support[fragment], -len(fragment), fragment),
    )[:cap])
    return candidates, {fragment: support[fragment] for fragment in candidates}


def tournament(training_rows, validation_tasks, max_length: int, require_square_fragment=False):
    candidates, support = candidate_pool(training_rows, require_square=require_square_fragment)
    primitive_index = build_search_index(None, max_length)
    primitive_rows, primitive_attempts, primitive_checks = evaluate_index(validation_tasks, primitive_index)
    evaluations = []
    for candidate in candidates:
        index = build_search_index(candidate, max_length)
        rows, attempts, checks = evaluate_index(validation_tasks, index)
        strict = harmful = macro_wins = 0
        baseline = {row["task"]: row for row in primitive_rows}
        for row in rows:
            base = baseline[row["task"]]
            if row["enumeration_attempts"] < base["enumeration_attempts"]:
                strict += 1
                if row["macro_used"]:
                    macro_wins += 1
            elif row["enumeration_attempts"] > base["enumeration_attempts"]:
                harmful += 1
        evaluations.append({
            "fragment": list(candidate),
            "support": support[candidate],
            "aggregate_enumeration_attempts": attempts,
            "aggregate_unique_checks": checks,
            "saving": primitive_attempts - attempts,
            "strict_improvement_tasks": strict,
            "harmful_tasks": harmful,
            "macro_strict_wins": macro_wins,
        })
    if not candidates:
        return {
            "accepted": False,
            "selected": None,
            "candidate_order": [],
            "baseline_aggregate_enumeration_attempts": primitive_attempts,
            "baseline_aggregate_unique_checks": primitive_checks,
            "evaluations": [],
            "all_candidate_validation_attempts": 0,
        }
    selected = min(
        enumerate(evaluations),
        key=lambda item: (item[1]["aggregate_enumeration_attempts"], item[0]),
    )[1]
    accepted = selected["aggregate_enumeration_attempts"] < primitive_attempts and selected["macro_strict_wins"] > 0
    return {
        "accepted": accepted,
        "selected": selected if accepted else None,
        "candidate_order": [list(c) for c in candidates],
        "baseline_aggregate_enumeration_attempts": primitive_attempts,
        "baseline_aggregate_unique_checks": primitive_checks,
        "evaluations": evaluations,
        "all_candidate_validation_attempts": sum(e["aggregate_enumeration_attempts"] for e in evaluations),
    }


def method_record(macro, origin: str) -> dict:
    identity = "method:" + content_hash({"kind": "macro.operator.g7.v1", "macro": list(macro)})
    return {
        "identity": identity,
        "kind": "macro",
        "origin_category": origin,
        "payload": {
            "macro": list(macro),
            "degree": polynomial_degree(normal_form(macro)),
            "fingerprint": content_hash({"macro": list(macro)}),
        },
    }


def method_schema_record(method: dict) -> dict:
    identity = "schema:" + content_hash({"method": method["identity"], "kind": "macro-token"})
    return {
        "identity": identity,
        "kind": "schema",
        "origin_category": method["origin_category"],
        "payload": {
            "pattern": "MACRO replaces a contiguous primitive fragment in exact token search",
            "originating_method_ids": [method["identity"]],
        },
    }


def admit_macro(bundle: dict, macro, origin: str, stage: str, change_note: str) -> dict:
    bundle = json.loads(canonical_json(bundle))
    method = method_record(macro, origin)
    schema = method_schema_record(method)
    existing = [m["identity"] for m in bundle["learned_methods"]]
    if method["identity"] not in existing:
        bundle["learned_methods"].append(method)
        bundle["method_schemas"].append(schema)
        bundle["support_dependency"]["edges"].append({
            "source": "training-proofs",
            "target": method["identity"],
            "relation": "SUPPORT",
        })
        bundle["field_state"]["atoms"].append({
            "id": method["identity"],
            "type": "procedure",
            "content": method["payload"]["fingerprint"],
        })
        bundle["self_model"]["known_competence"].append(method["identity"])
    bundle["stage"] = stage
    bundle["self_model"]["stage"] = stage
    bundle["self_change_history"].append({
        "change": change_note,
        "stage": stage,
        "method": method["identity"],
    })
    assert_constitution_frozen(bundle)
    return bundle, method


def current_macro(bundle: dict):
    methods = bundle.get("learned_methods") or []
    for method in methods:
        payload = method.get("payload") or {}
        if method.get("kind") == "macro" or payload.get("macro"):
            return tuple(payload["macro"])
    return None


def current_probe_policy(bundle: dict):
    for method in bundle.get("learned_methods") or []:
        if method.get("kind") == "probe_policy":
            return method
    return None


def failure_record(method_id: str, macro, train_tasks) -> dict:
    degree = polynomial_degree(normal_form(macro))
    identity = "failure:" + content_hash({
        "pattern": "MACRO_AT_EMPTY_PREFIX",
        "method": method_id,
        "max_target_degree_exclusive": degree,
    })
    return {
        "identity": identity,
        "kind": "failure_record",
        "origin_category": ORIGIN_APPLICABILITY,
        "active": True,
        "pattern": "MACRO_AT_EMPTY_PREFIX",
        "method_id": method_id,
        "task_ids": [],
        "scope": {
            "kind": "target_degree_lt",
            "degree": degree,
            "not_task_id_blacklist": True,
        },
        "outcome": "METHOD_FAILURE",
        "feedback": "MACRO as first token raises degree above the target class; not task impossibility",
        "evidence_task_count": len(train_tasks),
        "payload": {
            "pattern": "MACRO_AT_EMPTY_PREFIX",
            "max_target_degree_exclusive": degree,
        },
    }


def admit_failure(bundle: dict, record: dict, stage: str) -> dict:
    bundle = json.loads(canonical_json(bundle))
    ids = [r["identity"] for r in bundle["failure_counterexample_knowledge"]]
    if record["identity"] not in ids:
        bundle["failure_counterexample_knowledge"].append(record)
        bundle["applicability_scope"].append({
            "identity": "scope:" + record["identity"],
            "origin_category": ORIGIN_APPLICABILITY,
            "payload": record["scope"],
        })
        bundle["support_dependency"]["edges"].append({
            "source": record["identity"],
            "target": record["method_id"],
            "relation": "RESTRICTS",
        })
    bundle["stage"] = stage
    bundle["self_model"]["stage"] = stage
    bundle["self_change_history"].append({
        "change": "admit-scoped-failure-memory",
        "stage": stage,
        "failure": record["identity"],
    })
    assert_constitution_frozen(bundle)
    return bundle


def failure_records_for_task(bundle: dict, coefficients) -> list:
    active = []
    for rec in bundle.get("failure_counterexample_knowledge") or []:
        if not rec.get("active"):
            continue
        scope = rec.get("scope") or {}
        if scope.get("kind") == "target_degree_lt" and polynomial_degree(coefficients) < scope["degree"]:
            active.append(rec)
    return active


def search_bundle(bundle: dict, tasks, max_length: int):
    macro = current_macro(bundle)
    # Failure records are applied per-task: a high-degree task must still use MACRO.
    rows = []
    attempts = 0
    checks = 0
    skipped = 0
    for task in tasks:
        recs = failure_records_for_task(bundle, task["coefficients"])
        index = build_search_index(macro, max_length, recs)
        row = solve_from_index(task["coefficients"], index)
        rows.append(row)
        attempts += row["enumeration_attempts"]
        checks += row["unique_candidates_checked"]
        skipped += index["skipped_by_failure"]
    return rows, attempts, checks, skipped


def diagnosis_task_id(stuck) -> str:
    return content_hash({"domain": D2_GRAMMAR_ID, "stuck": [int(x) for x in stuck]})


def diagnosis_syndrome(stuck) -> tuple:
    members = set(stuck)
    return tuple(
        sum(1 for index in window if index in members) % 2
        for window in D2_SYNDROME_WINDOWS
    )


def diagnosis_population():
    out = []
    for count in (2, 3):
        for combo in combinations(range(D2_MODULES), count):
            stuck = tuple(combo)
            out.append({
                "fingerprint": diagnosis_task_id(stuck),
                "stuck": stuck,
                "syndrome": diagnosis_syndrome(stuck),
                "domain": D2_GRAMMAR_ID,
            })
    return tuple(out)


def take_diagnosis(population, salt: str, n: int, exclude=()):
    excluded = set(exclude)
    pool = [task for task in population if task["fingerprint"] not in excluded]
    chosen = tuple(sorted(
        pool,
        key=lambda task: (stable_rank(salt, task["fingerprint"]), task["fingerprint"]),
    )[:n])
    if len(chosen) != n:
        raise RuntimeError(f"diagnosis stratum too small: {len(chosen)} < {n}")
    return chosen


def d2_posterior(syndrome, observations, population=None):
    population = population if population is not None else diagnosis_population()
    remaining = []
    for task in population:
        if tuple(task["syndrome"]) != tuple(syndrome):
            continue
        members = set(task["stuck"])
        if all((index in members) is stuck for index, stuck in observations.items()):
            remaining.append(task)
    return remaining


def d2_choose_probe(name: str, observations: dict, posterior: list):
    unused = [index for index in range(D2_MODULES) if index not in observations]
    if not unused:
        return None
    if name == D2_POLICY_PROBE_ALL:
        return unused[0]
    if name == D2_POLICY_ROUND_ROBIN:
        return unused[0]
    if name != D2_POLICY_GREEDY:
        raise ValueError(f"unknown D2 policy {name}")
    best = unused[0]
    best_key = None
    for index in unused:
        yes = sum(1 for task in posterior if index in set(task["stuck"]))
        no = len(posterior) - yes
        if yes == 0 or no == 0:
            key = (1, abs(yes - no), index)
        else:
            key = (0, abs(yes - no), index)
        if best_key is None or key < best_key:
            best_key = key
            best = index
    return best


def diagnose_episode(task, policy_name: str, population=None):
    """Identify hidden stuck modules by probing; then plan ordered replacements.

    Constitution keys are not actions. Replace is allowed only on module indices.
    """
    population = population if population is not None else diagnosis_population()
    hidden = tuple(task["stuck"])
    syndrome = tuple(task["syndrome"])
    observations = {}
    probes = []
    while True:
        posterior = d2_posterior(syndrome, observations, population)
        if len(posterior) <= 1:
            break
        index = d2_choose_probe(policy_name, observations, posterior)
        if index is None:
            break
        observations[index] = index in set(hidden)
        probes.append(index)
        if len(probes) >= D2_MODULES:
            break
    posterior = d2_posterior(syndrome, observations, population)
    identified = len(posterior) == 1 and tuple(posterior[0]["stuck"]) == hidden
    plan = list(hidden) if identified else []
    # Hostile: constitution is not a replace target.
    for item in plan:
        if item not in range(D2_MODULES):
            raise ConstitutionMutationError("repair plan attempted to touch C")
    probe_cost = PROBE_COST * len(probes)
    replace_cost = REPLACE_COST * len(plan)
    token_word = [f"probe:{index}" for index in probes] + [f"replace:{index}" for index in plan]
    return {
        "task": task["fingerprint"],
        "policy": policy_name,
        "probes": probes,
        "plan": plan,
        "token_word": token_word,
        "program": token_word,
        "enumeration_attempts": probe_cost + replace_cost,
        "unique_candidates_checked": len(probes) + len(plan),
        "probe_count": len(probes),
        "identified": identified,
        "verified": identified,
        "macro_used": False,
        "policy_used": policy_name != D2_POLICY_ROUND_ROBIN and policy_name != D2_POLICY_PROBE_ALL,
    }


def evaluate_diagnosis(tasks, policy_name: str, population=None):
    rows = [diagnose_episode(task, policy_name, population) for task in tasks]
    if not all(row["identified"] for row in rows):
        raise RuntimeError(f"D2 policy {policy_name} failed to identify a held-out case")
    total = sum(row["enumeration_attempts"] for row in rows)
    checks = sum(row["unique_candidates_checked"] for row in rows)
    probes = sum(row["probe_count"] for row in rows)
    return rows, total, checks, probes


def d2_taught_donors():
    donors = [
        {
            "identity": f"donor:probe:{index}",
            "kind": "primitive",
            "origin_category": ORIGIN_TAUGHT,
            "payload": {"operator": f"probe:{index}", "grammar": D2_GRAMMAR_ID},
        }
        for index in range(D2_MODULES)
    ]
    donors.append({
        "identity": "donor:replace-identified-module",
        "kind": "primitive",
        "origin_category": ORIGIN_TAUGHT,
        "payload": {"operator": "replace", "grammar": D2_GRAMMAR_ID},
    })
    return donors


def probe_policy_record(name: str, origin: str) -> dict:
    identity = "method:" + content_hash({
        "kind": "probe-policy.g7.d2.v1",
        "name": name,
        "windows": list(D2_SYNDROME_WINDOWS),
        "modules": D2_MODULES,
    })
    return {
        "identity": identity,
        "kind": "probe_policy",
        "origin_category": origin,
        "payload": {
            "name": name,
            "family": D2_GRAMMAR_ID,
            "algorithm": name,
            "modules": D2_MODULES,
            "windows": [list(window) for window in D2_SYNDROME_WINDOWS],
            "not_task_id_table": True,
        },
    }


def admit_probe_policy(bundle: dict, name: str, origin: str, stage: str, change_note: str):
    bundle = json.loads(canonical_json(bundle))
    assert_constitution_frozen(bundle)
    method = probe_policy_record(name, origin)
    schema = {
        "identity": "schema:" + content_hash({"method": method["identity"], "kind": "probe-policy"}),
        "kind": "schema",
        "origin_category": origin,
        "payload": {
            "pattern": (
                "greedy posterior split: probe the unused module that most evenly "
                "partitions remaining diagnosis hypotheses, then replace identified modules"
            ),
            "originating_method_ids": [method["identity"]],
            "family": D2_GRAMMAR_ID,
        },
    }
    existing = [item["identity"] for item in bundle["learned_methods"]]
    if method["identity"] not in existing:
        bundle["learned_methods"].append(method)
        bundle["method_schemas"].append(schema)
        bundle["support_dependency"]["edges"].append({
            "source": "d2-training-proofs",
            "target": method["identity"],
            "relation": "SUPPORT",
        })
        bundle["field_state"]["atoms"].append({
            "id": method["identity"],
            "type": "procedure",
            "content": method["payload"]["algorithm"],
        })
        bundle["self_model"]["known_competence"].append(method["identity"])
        existing_donors = {donor["identity"] for donor in bundle["imported_donors"]}
        for donor in d2_taught_donors():
            if donor["identity"] not in existing_donors:
                bundle["imported_donors"].append(donor)
    bundle["stage"] = stage
    bundle["self_model"]["stage"] = stage
    bundle["self_model"]["unknown"] = [
        item for item in bundle["self_model"]["unknown"] if item != "OCM_2"
    ]
    bundle["self_change_history"].append({
        "change": change_note,
        "stage": stage,
        "method": method["identity"],
    })
    assert_constitution_frozen(bundle)
    return bundle, method


def d2_tournament(validation_tasks, population=None):
    candidates = (D2_POLICY_ROUND_ROBIN, D2_POLICY_GREEDY, D2_POLICY_PROBE_ALL)
    evaluations = []
    for name in candidates:
        rows, total, checks, probes = evaluate_diagnosis(validation_tasks, name, population)
        evaluations.append({
            "name": name,
            "aggregate_cost": total,
            "aggregate_probes": probes,
            "aggregate_checks": checks,
            "identified": all(row["identified"] for row in rows),
        })
    baseline = next(item for item in evaluations if item["name"] == D2_POLICY_ROUND_ROBIN)
    selected = min(
        enumerate(evaluations),
        key=lambda item: (item[1]["aggregate_cost"], item[0]),
    )[1]
    accepted = (
        selected["name"] == D2_POLICY_GREEDY
        and selected["aggregate_cost"] < baseline["aggregate_cost"]
        and selected["identified"]
    )
    return {
        "accepted": accepted,
        "selected": selected if accepted else None,
        "baseline": baseline,
        "evaluations": evaluations,
        "all_candidate_validation_cost": sum(item["aggregate_cost"] for item in evaluations),
    }


def cost(work_units: int, verifier_calls: int, notes: str) -> dict:
    return {"work_units": int(work_units), "verifier_calls": int(verifier_calls), "notes": notes}


def coordinate(value: float, status: str, notes: str) -> dict:
    return {"value": float(value), "status": status, "notes": notes}


def arm_result(arm: str, work_units: int, reused: bool, loaded_foreign: bool, notes: str) -> dict:
    return {
        "arm": arm,
        "work_units": int(work_units),
        "reused_prior_methods": bool(reused),
        "loaded_foreign_store": bool(loaded_foreign),
        "notes": notes,
    }


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_transition(instance: dict, schema: dict | None = None) -> None:
    schema = schema or load_schema()
    _validate(instance, schema, root=schema)


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise SchemaError(f"unsupported $ref {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"unresolved $ref {ref}")
        node = node[part]
    return node


def _type_ok(instance: Any, declared: Any) -> bool:
    if isinstance(declared, list):
        return any(_type_ok(instance, item) for item in declared)
    return {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": type(instance) is str,
        "integer": type(instance) is int,
        "number": type(instance) in (int, float) and type(instance) is not bool,
        "boolean": type(instance) is bool,
        "null": instance is None,
    }.get(declared, False)


def _validate(instance: Any, schema: Any, *, root: dict) -> None:
    if not isinstance(schema, dict):
        raise SchemaError("invalid schema")
    if "$ref" in schema:
        _validate(instance, _resolve(schema["$ref"], root), root=root)
        return
    if "const" in schema and instance != schema["const"]:
        raise SchemaError(f"const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"enum {schema['enum']}")
    if "type" in schema and not _type_ok(instance, schema["type"]):
        raise SchemaError(f"type {schema['type']}")
    if "minimum" in schema and isinstance(instance, (int, float)) and type(instance) is not bool:
        if instance < schema["minimum"]:
            raise SchemaError("minimum")
    if "minLength" in schema and isinstance(instance, str) and len(instance) < schema["minLength"]:
        raise SchemaError("minLength")
    if "maxLength" in schema and isinstance(instance, str) and len(instance) > schema["maxLength"]:
        raise SchemaError("maxLength")
    if "required" in schema:
        if not isinstance(instance, dict):
            raise SchemaError("object required")
        missing = [k for k in schema["required"] if k not in instance]
        if missing:
            raise SchemaError(f"required {missing}")
    if "properties" in schema or schema.get("additionalProperties") is False:
        if not isinstance(instance, dict):
            raise SchemaError("object")
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in props:
                _validate(value, props[key], root=root)
            elif additional is False:
                raise SchemaError(f"additional property {key}")
            elif isinstance(additional, dict):
                _validate(value, additional, root=root)
    if "items" in schema and isinstance(instance, list):
        for item in instance:
            _validate(item, schema["items"], root=root)


def emit_transition(
    *,
    lineage_id: str,
    source_stage: str,
    target_stage: str,
    source_machine_identity: str,
    target_bundle: dict,
    imported_donor_identities: list[str],
    prior_information_manifest: dict,
    new_information_supplied: dict,
    new_methods_schemas: list,
    reused_method_identities: list[str],
    actual_execution_witnesses: list,
    primitive_operators_added: list[str],
    composition_depth: int,
    acquisition_cost: dict,
    reasoning_cost: dict,
    verification_cost: dict,
    revision_cost: dict,
    self_change_cost: dict,
    maintenance_cost: dict,
    persistent_bytes: int,
    active_k_n: dict,
    kappa: dict,
    omega: dict,
    chi: dict,
    retention: dict,
    negative_transfer: dict,
    ablation: dict,
    strongest_parent_result: dict,
    terminal: str,
) -> dict:
    record = {
        "schema": "ocm.g7.development-transition.v1",
        "lineage_id": lineage_id,
        "source_stage": source_stage,
        "target_stage": target_stage,
        "source_machine_identity": source_machine_identity,
        "target_machine_identity": machine_identity(target_bundle),
        "persistent_state_digest": bundle_digest(target_bundle),
        "imported_donor_identities": imported_donor_identities,
        "prior_information_manifest": prior_information_manifest,
        "new_information_supplied": new_information_supplied,
        "new_methods_schemas": new_methods_schemas,
        "reused_method_identities": reused_method_identities,
        "actual_execution_witnesses": actual_execution_witnesses,
        "primitive_operators_added": primitive_operators_added,
        "composition_depth": composition_depth,
        "acquisition_cost": acquisition_cost,
        "reasoning_cost": reasoning_cost,
        "verification_cost": verification_cost,
        "revision_cost": revision_cost,
        "self_change_cost": self_change_cost,
        "maintenance_cost": maintenance_cost,
        "persistent_bytes": persistent_bytes,
        "active_k_n": active_k_n,
        "kappa": kappa,
        "omega": omega,
        "chi": chi,
        "retention": retention,
        "negative_transfer": negative_transfer,
        "ablation": ablation,
        "strongest_parent_result": strongest_parent_result,
        "terminal": terminal,
    }
    validate_transition(record)
    if record["target_machine_identity"] != record["persistent_state_digest"]:
        raise RuntimeError("machine identity must equal persistent-state digest")
    return record
