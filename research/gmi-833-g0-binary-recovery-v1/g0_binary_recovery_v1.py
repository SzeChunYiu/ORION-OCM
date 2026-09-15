from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import json
from typing import Callable, Iterable, Mapping, Sequence

CLAIM_CEILING = "GMI_P3_RELATIVE_BINARY_STATE_PROPERTY_RECOVERY_UNDER_NAND_NOR_GRAMMAR_TWINS_AT_REGISTERED_FINITE_SCOPE"
GRAMMARS = ("NAND", "NOR")


class RecoveryError(ValueError):
    pass


@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple[object, ...]
    gates: int
    text: str


@dataclass(frozen=True)
class Candidate:
    state_bits: int
    next_truth: tuple[int, ...] | None
    output_truth: tuple[int, ...]
    gate_count: int

    @property
    def resources(self) -> tuple[int, int]:
        return (self.state_bits, self.gate_count)

    @property
    def semantic_id(self) -> tuple[object, ...]:
        return (self.state_bits, self.next_truth, self.output_truth)


def var(name: str) -> Expr:
    if not name:
        raise RecoveryError("EMPTY_VARIABLE")
    return Expr("VAR", (name,), 0, name)


def gate_value(kind: str, a: int, b: int) -> int:
    if a not in (0, 1) or b not in (0, 1):
        raise RecoveryError("NON_BINARY_VALUE")
    if kind == "NAND":
        return 1 - (a & b)
    if kind == "NOR":
        return 1 - (a | b)
    raise RecoveryError("UNKNOWN_GATE")


def eval_expr(expr: Expr, env: Mapping[str, int]) -> int:
    if expr.op == "VAR":
        name = str(expr.args[0])
        if name not in env:
            raise RecoveryError("MISSING_VARIABLE")
        value = env[name]
        if value not in (0, 1):
            raise RecoveryError("NON_BINARY_VALUE")
        return value
    if len(expr.args) != 2 or not isinstance(expr.args[0], Expr) or not isinstance(expr.args[1], Expr):
        raise RecoveryError("MALFORMED_EXPR")
    return gate_value(expr.op, eval_expr(expr.args[0], env), eval_expr(expr.args[1], env))


def assignments(variables: Sequence[str]) -> tuple[dict[str, int], ...]:
    if not variables or len(set(variables)) != len(variables):
        raise RecoveryError("MALFORMED_VARIABLES")
    return tuple(dict(zip(variables, bits, strict=True)) for bits in product((0, 1), repeat=len(variables)))


def truth_of(expr: Expr, variables: Sequence[str]) -> tuple[int, ...]:
    return tuple(eval_expr(expr, env) for env in assignments(variables))


def synthesize(kind: str, variables: Sequence[str]) -> dict[tuple[int, ...], Expr]:
    if kind not in GRAMMARS:
        raise RecoveryError("UNKNOWN_GRAMMAR")
    envs = assignments(variables)
    best: dict[tuple[int, ...], Expr] = {}
    for name in variables:
        expr = var(name)
        truth = tuple(env[name] for env in envs)
        best[truth] = expr

    changed = True
    while changed:
        changed = False
        current = tuple(best.items())
        for truth_a, expr_a in current:
            for truth_b, expr_b in current:
                truth = tuple(gate_value(kind, a, b) for a, b in zip(truth_a, truth_b, strict=True))
                candidate = Expr(
                    kind,
                    (expr_a, expr_b),
                    expr_a.gates + expr_b.gates + 1,
                    f"{kind}({expr_a.text},{expr_b.text})",
                )
                old = best.get(truth)
                if old is None or (candidate.gates, candidate.text) < (old.gates, old.text):
                    best[truth] = candidate
                    changed = True
    return best


def reexecute_synthesis(best: Mapping[tuple[int, ...], Expr], variables: Sequence[str]) -> bool:
    return all(truth_of(expr, variables) == truth for truth, expr in best.items())


def nand_via_nor(a: int, b: int) -> tuple[int, int]:
    # Shared-intermediate 4-NOR circuit: na=!a, nb=!b, ab=a&b, out=!(a&b).
    na = gate_value("NOR", a, a)
    nb = gate_value("NOR", b, b)
    ab = gate_value("NOR", na, nb)
    out = gate_value("NOR", ab, ab)
    return out, 4


def nor_via_nand(a: int, b: int) -> tuple[int, int]:
    # Shared-intermediate 4-NAND circuit: na=!a, nb=!b, ab=a|b, out=!(a|b).
    na = gate_value("NAND", a, a)
    nb = gate_value("NAND", b, b)
    ab = gate_value("NAND", na, nb)
    out = gate_value("NAND", ab, ab)
    return out, 4


def cross_compiler_check() -> bool:
    for a, b in product((0, 1), repeat=2):
        x, cx = nand_via_nor(a, b)
        y, cy = nor_via_nand(a, b)
        if cx != 4 or cy != 4:
            return False
        if x != gate_value("NAND", a, b) or y != gate_value("NOR", a, b):
            return False
    return True


def candidate_space(kind: str, *, reverse: bool = False) -> tuple[Candidate, ...]:
    unary = synthesize(kind, ("X",))
    binary = synthesize(kind, ("S", "X"))
    candidates: list[Candidate] = []
    for output_truth, output_expr in unary.items():
        candidates.append(Candidate(0, None, output_truth, output_expr.gates))
    for next_truth, next_expr in binary.items():
        for output_truth, output_expr in binary.items():
            candidates.append(
                Candidate(1, next_truth, output_truth, next_expr.gates + output_expr.gates)
            )
    if reverse:
        candidates.reverse()
    return tuple(candidates)


def unary_apply(truth: tuple[int, ...], x: int) -> int:
    if len(truth) != 2 or x not in (0, 1):
        raise RecoveryError("BAD_UNARY_TRUTH")
    return truth[x]


def binary_apply(truth: tuple[int, ...], state: int, x: int) -> int:
    if len(truth) != 4 or state not in (0, 1) or x not in (0, 1):
        raise RecoveryError("BAD_BINARY_TRUTH")
    return truth[2 * state + x]


def execute(candidate: Candidate, sequence: Sequence[int]) -> tuple[int, ...]:
    if any(x not in (0, 1) for x in sequence):
        raise RecoveryError("NON_BINARY_SEQUENCE")
    state = 0
    outputs: list[int] = []
    for x in sequence:
        if candidate.state_bits == 0:
            outputs.append(unary_apply(candidate.output_truth, x))
        elif candidate.state_bits == 1 and candidate.next_truth is not None:
            outputs.append(binary_apply(candidate.output_truth, state, x))
            state = binary_apply(candidate.next_truth, state, x)
        else:
            raise RecoveryError("MALFORMED_CANDIDATE")
    return tuple(outputs)


def delay1_target(sequence: Sequence[int]) -> tuple[int, ...]:
    if any(x not in (0, 1) for x in sequence):
        raise RecoveryError("NON_BINARY_SEQUENCE")
    if not sequence:
        return ()
    return tuple((0, *sequence[:-1]))


def identity_target(sequence: Sequence[int]) -> tuple[int, ...]:
    if any(x not in (0, 1) for x in sequence):
        raise RecoveryError("NON_BINARY_SEQUENCE")
    return tuple(sequence)


def task_sequences(length: int = 4) -> tuple[tuple[int, ...], ...]:
    if length <= 0:
        raise RecoveryError("NONPOSITIVE_SEQUENCE_LENGTH")
    return tuple(product((0, 1), repeat=length))


def satisfies(candidate: Candidate, target: Callable[[Sequence[int]], tuple[int, ...]], *, length: int = 4) -> bool:
    return all(execute(candidate, seq) == target(seq) for seq in task_sequences(length))


def dominates(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] <= b[0] and a[1] <= b[1] and a != b


def exact_solutions(kind: str, target: Callable[[Sequence[int]], tuple[int, ...]], *, reverse: bool = False) -> tuple[Candidate, ...]:
    return tuple(c for c in candidate_space(kind, reverse=reverse) if satisfies(c, target))


def pareto_solutions(candidates: Iterable[Candidate]) -> tuple[Candidate, ...]:
    vals = tuple(candidates)
    return tuple(
        sorted(
            (c for c in vals if not any(dominates(d.resources, c.resources) for d in vals)),
            key=lambda c: (c.resources, c.semantic_id),
        )
    )


def universal_delay1_check(candidate: Candidate, max_length: int = 8) -> int:
    # Exhaustive finite certificate of the induction theorem stated in the note.
    checks = 0
    for length in range(1, max_length + 1):
        for seq in product((0, 1), repeat=length):
            if execute(candidate, seq) != delay1_target(seq):
                raise RecoveryError("RECOVERED_DELAY_CANDIDATE_FAILED")
            checks += 1
    return checks


def serialize_candidate(candidate: Candidate) -> dict[str, object]:
    return {
        "state_bits": candidate.state_bits,
        "next_truth": None if candidate.next_truth is None else "".join(map(str, candidate.next_truth)),
        "output_truth": "".join(map(str, candidate.output_truth)),
        "gate_count": candidate.gate_count,
        "resources": list(candidate.resources),
    }


def finite_certificate() -> dict[str, object]:
    grammar_results: dict[str, object] = {}
    recovered_delay: dict[str, Candidate] = {}
    recovered_identity: dict[str, Candidate] = {}
    all_checks = True

    for kind in GRAMMARS:
        unary = synthesize(kind, ("X",))
        binary = synthesize(kind, ("S", "X"))
        closure_ok = len(unary) == 4 and len(binary) == 16
        reexec_ok = reexecute_synthesis(unary, ("X",)) and reexecute_synthesis(binary, ("S", "X"))

        delay = exact_solutions(kind, delay1_target)
        delay_rev = exact_solutions(kind, delay1_target, reverse=True)
        delay_pf = pareto_solutions(delay)
        delay_pf_rev = pareto_solutions(delay_rev)
        if len(delay) != 1 or len(delay_pf) != 1 or delay_pf != delay_pf_rev:
            raise RecoveryError("DELAY_RECOVERY_NOT_UNIQUE")
        d = delay_pf[0]
        recovered_delay[kind] = d

        no_state_delay = tuple(c for c in candidate_space(kind) if c.state_bits == 0 and satisfies(c, delay1_target))
        if no_state_delay:
            raise RecoveryError("STATELESS_DELAY_FALSE_POSITIVE")

        identity = exact_solutions(kind, identity_target)
        identity_rev = exact_solutions(kind, identity_target, reverse=True)
        identity_pf = pareto_solutions(identity)
        identity_pf_rev = pareto_solutions(identity_rev)
        if len(identity_pf) != 1 or identity_pf != identity_pf_rev:
            raise RecoveryError("IDENTITY_PARETO_NOT_UNIQUE")
        i = identity_pf[0]
        recovered_identity[kind] = i

        grammar_results[kind] = {
            "unary_semantics": len(unary),
            "binary_semantics": len(binary),
            "unary_max_min_tree_gates": max(e.gates for e in unary.values()),
            "binary_max_min_tree_gates": max(e.gates for e in binary.values()),
            "candidate_semantics": len(candidate_space(kind)),
            "expressions_reexecute": reexec_ok,
            "delay_exact_solutions": len(delay),
            "delay_stateless_exact_solutions": len(no_state_delay),
            "identity_exact_solutions": len(identity),
            "identity_pareto_solutions": len(identity_pf),
        }
        all_checks = all_checks and closure_ok and reexec_ok

    nand_delay = recovered_delay["NAND"]
    nor_delay = recovered_delay["NOR"]
    expected_next = (0, 1, 0, 1)  # projection X, discovered after search for reporting only
    expected_output = (0, 0, 1, 1)  # projection S, discovered after search for reporting only
    same_delay_semantics = nand_delay.semantic_id == nor_delay.semantic_id
    delay_property = (
        nand_delay.state_bits == 1
        and nand_delay.next_truth == expected_next
        and nand_delay.output_truth == expected_output
        and nand_delay.gate_count == 0
    )

    nand_identity = recovered_identity["NAND"]
    nor_identity = recovered_identity["NOR"]
    same_identity_semantics = nand_identity.semantic_id == nor_identity.semantic_id
    identity_property = (
        nand_identity.state_bits == 0
        and nand_identity.next_truth is None
        and nand_identity.output_truth == (0, 1)
        and nand_identity.gate_count == 0
    )

    trajectory_checks = universal_delay1_check(nand_delay, 8)
    cross_ok = cross_compiler_check()

    # Analytic stateless collision witness: same current input 0, different previous input.
    seq_a, seq_b = (0, 0), (1, 0)
    collision = {
        "same_current_input": seq_a[-1] == seq_b[-1] == 0,
        "required_output_a_at_t1": delay1_target(seq_a)[1],
        "required_output_b_at_t1": delay1_target(seq_b)[1],
    }
    collision_ok = collision["required_output_a_at_t1"] != collision["required_output_b_at_t1"]

    checks = {
        "both_grammars_complete_on_registered_boolean_semantics": all_checks,
        "stored_expressions_reexecute": all(bool(grammar_results[g]["expressions_reexecute"]) for g in GRAMMARS),
        "bounded_four_gate_cross_compilers": cross_ok,
        "delay_unique_semantic_recovery_both_grammars": same_delay_semantics and delay_property,
        "delay_stateless_matched_negative_impossible": all(grammar_results[g]["delay_stateless_exact_solutions"] == 0 for g in GRAMMARS),
        "delay_recovered_candidate_solves_all_sequences_through_length_8": trajectory_checks == sum(2**n for n in range(1, 9)),
        "stateless_collision_witness": collision_ok,
        "identity_unique_pareto_stateless_recovery_both_grammars": same_identity_semantics and identity_property,
        "state_exposure_not_sufficient_for_selection": all(grammar_results[g]["identity_exact_solutions"] > 1 for g in GRAMMARS) and identity_property,
        "forward_reverse_exhaustive_search_same_semantic_pareto": True,
    }
    if not all(checks.values()):
        raise RecoveryError("CERTIFICATE_CHECK_FAILED")

    return {
        "schema": "GMI_833_G0_BINARY_RECOVERY_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "verdict": "GREEN",
        "prior_disclosure": {
            "level": "P3_RELATIVE_AT_REGISTERED_FINITE_SCOPE",
            "architectural_prior": False,
            "representation_prior": "binary wires plus optional generic one-bit persistent state",
            "operator_prior": "one functionally-complete generic Boolean primitive per grammar twin",
            "search_prior": "exhaustive finite semantic search; deterministic lexical tie only inside expression synthesis",
            "ecological_prior": "DELAY1 and IDENTITY behavioral sequence tasks",
            "evaluation_prior": "exact protected output equality; Pareto resources=(state_bits,primitive_tree_gate_count)",
            "target_family_name_visible_to_search": False,
            "target_property_vector_visible_to_search": False,
        },
        "checks": checks,
        "counts": {
            "grammar_twins": 2,
            "candidates_per_grammar": 260,
            "delay_sequences_length_4": 16,
            "delay_universal_certificate_sequences_lengths_1_to_8": trajectory_checks,
            "cross_compiler_input_pairs": 4,
        },
        "grammar_results": grammar_results,
        "recovered": {
            "DELAY1_NAND": serialize_candidate(nand_delay),
            "DELAY1_NOR": serialize_candidate(nor_delay),
            "IDENTITY_NAND": serialize_candidate(nand_identity),
            "IDENTITY_NOR": serialize_candidate(nor_identity),
            "post_hoc_delay_property": "ONE_BIT_PERSISTENT_STATE_WITH_NEXT_STATE_INPUT_PROJECTION_AND_OUTPUT_STATE_PROJECTION",
        },
        "hostiles": {
            "stateless_collision": collision,
            "state_removed_delay_exact_solution_count": 0,
            "identity_stateful_exact_solutions_exist_but_are_pareto_dominated": int(grammar_results["NAND"]["identity_exact_solutions"]) - 1,
        },
        "forbidden_promotions": [
            "FINAL_UNIVERSAL_G0_VALIDATED",
            "ALL_KNOWN_FORMS_P3_RECOVERED",
            "NEURAL_SYMBOLIC_PROBABILISTIC_CLOSURE",
            "REAL_LEARNING_DYNAMICS_VALIDATED",
            "BROAD_GRAMMAR_NEUTRALITY_PROVED",
            "UNKNOWN_FORM_DISCOVERY_VALIDATED",
            "COMPLETE_GMI",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(finite_certificate(), sort_keys=True, separators=(",", ":")))
