from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

AXES = ("w", "x", "y", "r")
VALUES = (-1, 0, 1)
CAP = 6
FREEZE_COMMIT = "0d7810039a8705dab44928d09f1bdebd4cd3b91e"
TARGETS_COMMIT = "2f2324109373d97e055736d1291077fe12efd296"
CLAIM = "NEUTRAL_THREE_LAW_REDISCOVERY_AT_REGISTERED_FINITE_GRAMMAR_SCOPE"
UNIVERSE_SHA = "e8aec22f36a3558cb3f9356e57b4e13575d7905862cfac9fe1240618850ce523"
TARGET_OBJECT_SHA = {
    "opaque_1": "7d575d7033a2eef62b6fe818be4dd15092f86617a9eb902366e871beaa6577d9",
    "opaque_2": "93d925ea0d70134e43ad0add4b1b5a49730eb3f74dacba2345f4caf3ac956db3",
    "opaque_3": "65b57eef0aa754f875d9f7bd656504a2a1f2cf543562948faf1af9de3143b315",
}
EXPECTED_COST = {"opaque_1": 4, "opaque_2": 6, "opaque_3": 6}
EXPECTED_SIG = {
    "opaque_1": ("w", "y"),
    "opaque_2": ("w", "x", "y"),
    "opaque_3": ("w", "x", "r"),
}
HERE = Path(__file__).resolve().parent
TARGETS_PATH = HERE / "TARGETS_V1.json"


def frac_text(v: F) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def parse_frac(s: str) -> F:
    if not isinstance(s, str) or not s:
        raise ValueError("fraction must be nonempty string")
    return F(s)


def compact_sha(obj) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def universe():
    return tuple(product(VALUES, repeat=4))


def universe_json_rows():
    return [{axis: int(row[i]) for i, axis in enumerate(AXES)} for row in universe()]


def verify_universe():
    got = compact_sha(universe_json_rows())
    if got != UNIVERSE_SHA:
        raise RuntimeError(f"universe digest mismatch: {got}")
    return got


def load_targets(path=TARGETS_PATH):
    raw = json.loads(Path(path).read_text())
    if raw.get("schema") != "NeutralThreeLawTargetsV1" or raw.get("universe_sha256") != UNIVERSE_SHA:
        raise ValueError("target artifact metadata mismatch")
    seen = set()
    out = []
    for obj in raw.get("targets", []):
        oid = obj.get("opaque_id")
        if oid not in TARGET_OBJECT_SHA or oid in seen:
            raise ValueError("unknown/duplicate opaque target")
        if compact_sha(obj) != TARGET_OBJECT_SHA[oid]:
            raise ValueError(f"{oid} frozen object digest mismatch")
        vals = tuple(parse_frac(x) for x in obj.get("outputs", []))
        if len(vals) != 81:
            raise ValueError("target table length mismatch")
        out.append((oid, vals))
        seen.add(oid)
    if seen != set(TARGET_OBJECT_SHA):
        raise ValueError("target set mismatch")
    return tuple(out)


def _terminal_tables(allowed_vars):
    rows = universe()
    tables = {}
    for constant in (-1, 0, 1):
        tables[tuple(F(constant) for _ in rows)] = str(constant)
    for j, name in enumerate(AXES):
        if name in allowed_vars:
            tables[tuple(F(row[j]) for row in rows)] = name
    return tables


def _lex_insert(mapping, table, expr):
    old = mapping.get(table)
    if old is None or expr < old:
        mapping[table] = expr


@dataclass(frozen=True)
class SearchResult:
    by_cost: tuple
    best_cost: dict
    best_expr: dict


def search_semantics(cap=CAP, allowed_vars=AXES, allow_half=True):
    if type(cap) is not int or cap < 1:
        raise ValueError("cap must be positive int")
    allowed_vars = tuple(allowed_vars)
    if len(set(allowed_vars)) != len(allowed_vars) or any(v not in AXES for v in allowed_vars):
        raise ValueError("invalid variable set")
    if type(allow_half) is not bool:
        raise ValueError("allow_half must be bool")
    by = [None] + [{} for _ in range(cap)]
    by[1] = _terminal_tables(allowed_vars)
    best_cost = {table: 1 for table in by[1]}
    best_expr = dict(by[1])
    for cost in range(2, cap + 1):
        candidates = {}
        if allow_half:
            for table, expr in by[cost - 1].items():
                out = tuple(value / F(2) for value in table)
                if out not in best_cost:
                    _lex_insert(candidates, out, f"half({expr})")
        for left_cost in range(1, cost - 1):
            right_cost = cost - 1 - left_cost
            if right_cost < 1:
                continue
            for left_table, left_expr in by[left_cost].items():
                for right_table, right_expr in by[right_cost].items():
                    outputs = (
                        (tuple(a + b for a, b in zip(left_table, right_table)), f"({left_expr}+{right_expr})"),
                        (tuple(a - b for a, b in zip(left_table, right_table)), f"({left_expr}-{right_expr})"),
                        (tuple(a * b for a, b in zip(left_table, right_table)), f"({left_expr}*{right_expr})"),
                    )
                    for out, expr in outputs:
                        if out not in best_cost:
                            _lex_insert(candidates, out, expr)
        candidates = {table: expr for table, expr in candidates.items() if table not in best_cost}
        by[cost] = candidates
        for table, expr in candidates.items():
            best_cost[table] = cost
            best_expr[table] = expr
    return SearchResult(tuple(by), best_cost, best_expr)


def table_digest(table):
    return compact_sha([frac_text(value) for value in table])


def dependency_signature(table):
    rows = universe()
    index = {row: i for i, row in enumerate(rows)}
    signature = []
    witnesses = {}
    for j, name in enumerate(AXES):
        witness = None
        for row in rows:
            i = index[row]
            for value in VALUES:
                if value == row[j]:
                    continue
                other = list(row)
                other[j] = value
                other = tuple(other)
                k = index[other]
                if table[i] != table[k]:
                    witness = (row, other, table[i], table[k])
                    break
            if witness is not None:
                break
        if witness is not None:
            signature.append(name)
            witnesses[name] = witness
    return tuple(signature), witnesses


def invariant_in_variable(table, name):
    if name not in AXES:
        raise ValueError("unknown variable")
    j = AXES.index(name)
    groups = {}
    for row, value in zip(universe(), table):
        key = row[:j] + row[j + 1 :]
        groups.setdefault(key, set()).add(value)
    return all(len(values) == 1 for values in groups.values())


def witness_json(witness):
    row_a, row_b, out_a, out_b = witness
    return {
        "row_a": list(row_a),
        "row_b": list(row_b),
        "out_a": frac_text(out_a),
        "out_b": frac_text(out_b),
    }


def recover(target_rows, search):
    rows = []
    for opaque_id, table in target_rows:
        if table not in search.best_cost:
            rows.append({"opaque_id": opaque_id, "matched": False})
            continue
        signature, witnesses = dependency_signature(table)
        rows.append(
            {
                "opaque_id": opaque_id,
                "matched": True,
                "min_cost": search.best_cost[table],
                "canonical_expression": search.best_expr[table],
                "table_sha256": table_digest(table),
                "dependency_signature": list(signature),
                "dependency_witnesses": {name: witness_json(witnesses[name]) for name in signature},
                "nonrequired_invariance": {
                    name: invariant_in_variable(table, name) for name in AXES if name not in signature
                },
            }
        )
    return rows


class ActivatedProtocol:
    def __init__(self):
        self._active = False
        self.cap = CAP
        self.allowed_vars = AXES
        self.allow_half = True

    def activate(self):
        self._active = True

    def mutate(self, **kwargs):
        if self._active:
            raise RuntimeError("protocol is frozen after target activation")
        for key, value in kwargs.items():
            if key not in ("cap", "allowed_vars", "allow_half"):
                raise ValueError("unknown protocol field")
            setattr(self, key, value)


def build_receipt(target_path=TARGETS_PATH):
    verify_universe()
    targets = load_targets(target_path)
    protocol = ActivatedProtocol()
    protocol.activate()
    search = search_semantics()
    recovered = recover(targets, search)
    by_id = {row["opaque_id"]: row for row in recovered}
    for opaque_id, expected_cost in EXPECTED_COST.items():
        if not by_id[opaque_id]["matched"] or by_id[opaque_id]["min_cost"] != expected_cost:
            raise RuntimeError(f"{opaque_id} frozen minimum mismatch")
        if tuple(by_id[opaque_id]["dependency_signature"]) != EXPECTED_SIG[opaque_id]:
            raise RuntimeError(f"{opaque_id} dependency signature mismatch")
        if not all(by_id[opaque_id]["nonrequired_invariance"].values()):
            raise RuntimeError(f"{opaque_id} unexpected nonrequired dependency")

    target_map = dict(targets)
    ablations = {}
    for variable in AXES:
        ablated = search_semantics(allowed_vars=tuple(v for v in AXES if v != variable))
        affected = []
        for opaque_id, signature in EXPECTED_SIG.items():
            if variable in signature:
                matched = target_map[opaque_id] in ablated.best_cost
                affected.append({"opaque_id": opaque_id, "matched_through_cap": matched})
                if matched:
                    raise RuntimeError(f"required variable ablation unexpectedly matched: {opaque_id}/{variable}")
        ablations[variable] = affected

    no_half = search_semantics(allow_half=False)
    no_half_result = {}
    for opaque_id, table in targets:
        has_noninteger = any(value.denominator != 1 for value in table)
        matched = table in no_half.best_cost
        no_half_result[opaque_id] = {
            "has_noninteger_output": has_noninteger,
            "matched_through_cap": matched,
        }
        if not has_noninteger or matched:
            raise RuntimeError("half hostile failed")

    perturbed = list(target_map["opaque_1"])
    perturbed[0] += F(1, 4)
    perturbed = tuple(perturbed)
    perturb = {
        "table_sha256": table_digest(perturbed),
        "matched_through_cap": perturbed in search.best_cost,
    }
    if perturb["matched_through_cap"]:
        raise RuntimeError("perturbed target unexpectedly matched")

    rows = universe()
    w = tuple(F(row[0]) for row in rows)
    y = tuple(F(row[2]) for row in rows)
    alternate = tuple(a / F(2) + b / F(2) for a, b in zip(w, y))
    equivalent = {
        "lower_cost_expression": "half((w+y))",
        "lower_cost": 4,
        "higher_cost_expression": "(half(w)+half(y))",
        "higher_cost": 5,
        "same_table": alternate == target_map["opaque_1"],
        "quotient_min_cost": search.best_cost[target_map["opaque_1"]],
        "quotient_expression": search.best_expr[target_map["opaque_1"]],
    }
    if not equivalent["same_table"] or equivalent["quotient_min_cost"] != 4:
        raise RuntimeError("equivalent syntax quotient hostile failed")

    reversed_recovery = recover(tuple(reversed(targets)), search)
    first = {
        row["opaque_id"]: (row.get("matched"), row.get("min_cost"), row.get("table_sha256"))
        for row in recovered
    }
    second = {
        row["opaque_id"]: (row.get("matched"), row.get("min_cost"), row.get("table_sha256"))
        for row in reversed_recovery
    }
    if first != second:
        raise RuntimeError("opaque id order changed recovery")

    mutation_rejected = False
    try:
        protocol.mutate(cap=5)
    except RuntimeError:
        mutation_rejected = True
    if not mutation_rejected:
        raise RuntimeError("post-activation mutation was accepted")

    return {
        "schema": "NeutralThreeLawReceiptV1",
        "issue": 768,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "target_materialization_commit": TARGETS_COMMIT,
        "claim_ceiling": CLAIM,
        "universe": {"size": 81, "sha256": UNIVERSE_SHA, "axes": list(AXES), "values": list(VALUES)},
        "grammar": {
            "cap": CAP,
            "terminals": ["-1", "0", "1", "w", "x", "y", "r"],
            "unary": ["half"],
            "binary": ["+", "-", "*"],
            "tree_cost": "one per terminal/operator",
        },
        "quotient": {
            "new_semantic_tables_by_cost": {str(cost): len(search.by_cost[cost]) for cost in range(1, CAP + 1)},
            "total_semantic_tables": len(search.best_cost),
        },
        "recoveries": recovered,
        "required_variable_ablations": ablations,
        "remove_half": no_half_result,
        "perturbed_target": perturb,
        "equivalent_syntax": equivalent,
        "opaque_id_permutation_invariant": first == second,
        "post_activation_mutation_rejected": mutation_rejected,
        "evidence_classes": {
            "C1-1": "P1",
            "C1-2": "P1",
            "C1-3": "P1/P2",
            "C1-4": "P1/P2",
            "C1-5": "P1/P2",
        },
        "forbidden_claims": [
            "UNIVERSAL_LAW_DISCOVERY",
            "CROSS_GRAMMAR_REPLICATION",
            "REAL_AGENT_EVIDENCE",
            "COMPLETE_GMI",
        ],
    }


def main():
    print(json.dumps(build_receipt(), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
