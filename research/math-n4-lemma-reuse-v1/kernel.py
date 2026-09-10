"""Exact implicational Hilbert kernel (bounded MATH-1 microscope).

Positive implicational calculus: axiom schemas K and S, rule MP. Combinatory
SK terms are Hilbert proofs. Schematic lemmas are derived axioms whose witnessing
SK terms are kernel-checked. This is not a Metamath kernel and not N4 close.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Iterable, Mapping

Atom = str
Formula = Atom | tuple  # ("imp", Formula, Formula)


def imp(a: Formula, b: Formula) -> Formula:
    return ("imp", a, b)


def is_imp(formula: Formula) -> bool:
    return isinstance(formula, tuple) and len(formula) == 3 and formula[0] == "imp"


def pretty(formula: Formula) -> str:
    if not is_imp(formula):
        return str(formula)
    return f"({pretty(formula[1])} → {pretty(formula[2])})"


def subformulas(formula: Formula) -> tuple[Formula, ...]:
    seen: list[Formula] = []
    stack = [formula]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.append(cur)
        if is_imp(cur):
            stack.append(cur[1])
            stack.append(cur[2])
    return tuple(seen)


def atoms_of(formula: Formula) -> tuple[str, ...]:
    out: list[str] = []
    for part in subformulas(formula):
        if not is_imp(part) and part not in out:
            out.append(str(part))
    return tuple(out)


def size_of(formula: Formula) -> int:
    if not is_imp(formula):
        return 1
    return 1 + size_of(formula[1]) + size_of(formula[2])


def substitute(formula: Formula, mapping: Mapping[str, Formula]) -> Formula:
    if not is_imp(formula):
        return mapping.get(str(formula), formula)
    return imp(substitute(formula[1], mapping), substitute(formula[2], mapping))


def schema_vars(formula: Formula) -> tuple[str, ...]:
    return atoms_of(formula)


def alpha_normalize(formula: Formula) -> Formula:
    """Rename atoms in first-seen order to v0, v1, ... (shape identity)."""
    mapping: dict[str, str] = {}

    def walk(cur: Formula) -> Formula:
        if not is_imp(cur):
            name = str(cur)
            if name not in mapping:
                mapping[name] = f"v{len(mapping)}"
            return mapping[name]
        return imp(walk(cur[1]), walk(cur[2]))

    return walk(formula)


def bag_of_symbols(formula: Formula) -> Counter:
    bag: Counter = Counter()

    def walk(cur: Formula) -> None:
        if not is_imp(cur):
            bag[str(cur)] += 1
            return
        bag["imp"] += 1
        walk(cur[1])
        walk(cur[2])

    walk(formula)
    return bag


def bag_jaccard(a: Formula, b: Formula) -> float:
    """Shape-level Jaccard: atoms are alpha-normalized before the bag."""
    left = bag_of_symbols(alpha_normalize(a))
    right = bag_of_symbols(alpha_normalize(b))
    keys = set(left) | set(right)
    inter = sum(min(left[k], right[k]) for k in keys)
    union = sum(max(left[k], right[k]) for k in keys)
    if union == 0:
        return 1.0
    return inter / union


# --- axiom schemas ---------------------------------------------------------

K_SCHEMA: Formula = imp("A", imp("B", "A"))
S_SCHEMA: Formula = imp(
    imp("A", imp("B", "C")),
    imp(imp("A", "B"), imp("A", "C")),
)
# PREFIX / B: (B → C) → ((A → B) → (A → C))
PREFIX_SCHEMA: Formula = imp(
    imp("B", "C"),
    imp(imp("A", "B"), imp("A", "C")),
)
# SWAP / C: (A → (B → C)) → (B → (A → C))
SWAP_SCHEMA: Formula = imp(
    imp("A", imp("B", "C")),
    imp("B", imp("A", "C")),
)
# SUFFIX / B': (A → B) → ((B → C) → (A → C))
SUFFIX_SCHEMA: Formula = imp(
    imp("A", "B"),
    imp(imp("B", "C"), imp("A", "C")),
)
IDENTITY_SCHEMA: Formula = imp("A", "A")


def instantiate_schema(schema: Formula, mapping: Mapping[str, Formula]) -> Formula:
    return substitute(schema, mapping)


def unify_schema(schema: Formula, goal: Formula) -> dict[str, Formula] | None:
    """Match a schematic axiom against a closed goal. Vars are schema atoms."""
    mapping: dict[str, Formula] = {}

    def walk(pattern: Formula, value: Formula) -> bool:
        if not is_imp(pattern):
            name = str(pattern)
            if name in mapping:
                return mapping[name] == value
            mapping[name] = value
            return True
        if not is_imp(value):
            return False
        return walk(pattern[1], value[1]) and walk(pattern[2], value[2])

    if walk(schema, goal):
        return mapping
    return None


def is_k_instance(formula: Formula) -> bool:
    return unify_schema(K_SCHEMA, formula) is not None


def is_s_instance(formula: Formula) -> bool:
    return unify_schema(S_SCHEMA, formula) is not None


# --- Hilbert proof objects -------------------------------------------------

@dataclass(frozen=True)
class HilbertStep:
    formula: Formula
    rule: str  # K | S | MP | LEMMA
    premises: tuple[int, ...] = ()
    lemma_id: str | None = None


@dataclass(frozen=True)
class HilbertProof:
    steps: tuple[HilbertStep, ...]

    @property
    def conclusion(self) -> Formula:
        return self.steps[-1].formula

    def lemmas_invoked(self) -> tuple[str, ...]:
        seen: list[str] = []
        for step in self.steps:
            if step.rule == "LEMMA" and step.lemma_id and step.lemma_id not in seen:
                seen.append(step.lemma_id)
        return tuple(seen)

    def mp_count(self) -> int:
        return sum(1 for step in self.steps if step.rule == "MP")


@dataclass(frozen=True)
class Lemma:
    lemma_id: str
    schema: Formula
    witness_term: Any
    support_ids: tuple[str, ...]
    authorized: bool = True


class KernelReject(Exception):
    pass


def check_proof(
    proof: HilbertProof,
    lemmas: Mapping[str, Lemma] | None = None,
) -> Formula:
    """Exact Hilbert checker. Every MP step must cite A and A→B already derived."""
    lemmas = lemmas or {}
    derived: list[Formula] = []
    for index, step in enumerate(proof.steps):
        if step.rule == "K":
            if not is_k_instance(step.formula):
                raise KernelReject(f"step {index} is not a K instance")
        elif step.rule == "S":
            if not is_s_instance(step.formula):
                raise KernelReject(f"step {index} is not an S instance")
        elif step.rule == "LEMMA":
            if not step.lemma_id or step.lemma_id not in lemmas:
                raise KernelReject(f"step {index} cites unknown lemma {step.lemma_id}")
            lemma = lemmas[step.lemma_id]
            if not lemma.authorized:
                raise KernelReject(f"step {index} cites revoked lemma {step.lemma_id}")
            if unify_schema(lemma.schema, step.formula) is None:
                raise KernelReject(f"step {index} is not an instance of {step.lemma_id}")
        elif step.rule == "MP":
            if len(step.premises) != 2:
                raise KernelReject(f"step {index} MP needs two premises")
            i, j = step.premises
            if i >= index or j >= index:
                raise KernelReject(f"step {index} MP looks forward")
            left = derived[i]
            implication = derived[j]
            if not is_imp(implication) or implication[1] != left or implication[2] != step.formula:
                raise KernelReject(f"step {index} MP does not match A and A→B")
        else:
            raise KernelReject(f"step {index} unknown rule {step.rule}")
        derived.append(step.formula)
    if not derived:
        raise KernelReject("empty proof")
    return derived[-1]


# --- combinatory terms and principal types ---------------------------------

Term = str | tuple  # "S" | "K" | lemma_id | ("app", Term, Term)


def app(left: Term, right: Term) -> Term:
    return ("app", left, right)


def term_size(term: Term) -> int:
    if not isinstance(term, tuple):
        return 1
    return term_size(term[1]) + term_size(term[2])


def term_pretty(term: Term) -> str:
    if not isinstance(term, tuple):
        return str(term)
    return f"({term_pretty(term[1])} {term_pretty(term[2])})"


@dataclass
class _Var:
    n: int

    def __repr__(self) -> str:
        return f"?{self.n}"


def _deref(node: Any, subst: dict) -> Any:
    while isinstance(node, _Var) and node.n in subst:
        node = subst[node.n]
    return node


def _occurs(var: _Var, node: Any, subst: dict) -> bool:
    node = _deref(node, subst)
    if isinstance(node, _Var):
        return node.n == var.n
    if is_imp(node):
        return _occurs(var, node[1], subst) or _occurs(var, node[2], subst)
    return False


def _unify(left: Any, right: Any, subst: dict) -> bool:
    left = _deref(left, subst)
    right = _deref(right, subst)
    if left == right:
        return True
    if isinstance(left, _Var):
        if _occurs(left, right, subst):
            return False
        subst[left.n] = right
        return True
    if isinstance(right, _Var):
        if _occurs(right, left, subst):
            return False
        subst[right.n] = left
        return True
    if is_imp(left) and is_imp(right):
        return _unify(left[1], right[1], subst) and _unify(left[2], right[2], subst)
    return False


def _apply_subst(node: Any, subst: dict) -> Any:
    node = _deref(node, subst)
    if is_imp(node):
        return imp(_apply_subst(node[1], subst), _apply_subst(node[2], subst))
    return node


def _schema_type(schema: Formula, fresh) -> Formula:
    mapping = {name: fresh() for name in schema_vars(schema)}
    return substitute(schema, mapping)


def infer_type(term: Term, lemmas: Mapping[str, Lemma] | None = None) -> Formula | None:
    """Principal type of a closed combinatory term, or None if ill-typed."""
    lemmas = lemmas or {}
    subst: dict[int, Any] = {}
    counter = [0]

    def fresh() -> _Var:
        counter[0] += 1
        return _Var(counter[0])

    def infer(node: Term) -> Any | None:
        if node == "S":
            a, b, c = fresh(), fresh(), fresh()
            return imp(imp(a, imp(b, c)), imp(imp(a, b), imp(a, c)))
        if node == "K":
            a, b = fresh(), fresh()
            return imp(a, imp(b, a))
        if not isinstance(node, tuple):
            lemma = lemmas.get(str(node))
            if lemma is None or not lemma.authorized:
                return None
            return _schema_type(lemma.schema, fresh)
        if node[0] != "app":
            return None
        fn = infer(node[1])
        arg = infer(node[2])
        if fn is None or arg is None:
            return None
        result = fresh()
        if not _unify(fn, imp(arg, result), subst):
            return None
        return _apply_subst(result, subst)

    raw = infer(term)
    if raw is None:
        return None
    typed = _apply_subst(raw, subst)
    # Ground remaining variables with stable dummy atoms for comparison.
    mapping: dict[int, str] = {}

    def ground(node: Any) -> Formula:
        node = _deref(node, subst)
        if isinstance(node, _Var):
            if node.n not in mapping:
                mapping[node.n] = f"t{len(mapping)}"
            return mapping[node.n]
        if is_imp(node):
            return imp(ground(node[1]), ground(node[2]))
        return node

    return ground(typed)


def term_inhabits(term: Term, goal: Formula, lemmas: Mapping[str, Lemma] | None = None) -> bool:
    inferred = infer_type(term, lemmas)
    if inferred is None:
        return False
    return alpha_normalize(inferred) == alpha_normalize(goal)


def term_unifies_goal(term: Term, goal: Formula, lemmas: Mapping[str, Lemma] | None = None) -> bool:
    """Whether the term's principal type instantiates to the closed goal."""
    lemmas = lemmas or {}
    subst: dict[int, Any] = {}
    counter = [0]

    def fresh() -> _Var:
        counter[0] += 1
        return _Var(counter[0])

    def infer(node: Term) -> Any | None:
        if node == "S":
            a, b, c = fresh(), fresh(), fresh()
            return imp(imp(a, imp(b, c)), imp(imp(a, b), imp(a, c)))
        if node == "K":
            a, b = fresh(), fresh()
            return imp(a, imp(b, a))
        if not isinstance(node, tuple):
            lemma = lemmas.get(str(node))
            if lemma is None or not lemma.authorized:
                return None
            return _schema_type(lemma.schema, fresh)
        fn = infer(node[1])
        arg = infer(node[2])
        if fn is None or arg is None:
            return None
        result = fresh()
        if not _unify(fn, imp(arg, result), subst):
            return None
        return _apply_subst(result, subst)

    raw = infer(term)
    if raw is None:
        return False
    typed = _apply_subst(raw, subst)
    return _unify(typed, goal, subst)


# --- Hilbert reconstruction from combinatory terms -------------------------

@dataclass
class _TypedNode:
    term: Term
    raw: Any
    children: tuple["_TypedNode", ...]


def reconstruct_proof(term: Term, goal: Formula, lemmas: Mapping[str, Lemma] | None = None) -> HilbertProof:
    """Rebuild a Hilbert deduction from a combinatory term against a closed goal.

    Each leaf occurrence carries its own type variables. Types are not cached by
    term structure, so two uses of K in S(KS)K remain distinct axiom instances.
    """
    lemmas = dict(lemmas or {})
    subst: dict[int, Any] = {}
    counter = [0]

    def fresh() -> _Var:
        counter[0] += 1
        return _Var(counter[0])

    def build(node: Term) -> _TypedNode:
        if node == "S":
            a, b, c = fresh(), fresh(), fresh()
            return _TypedNode(node, imp(imp(a, imp(b, c)), imp(imp(a, b), imp(a, c))), ())
        if node == "K":
            a, b = fresh(), fresh()
            return _TypedNode(node, imp(a, imp(b, a)), ())
        if not isinstance(node, tuple):
            lemma = lemmas[str(node)]
            return _TypedNode(node, _schema_type(lemma.schema, fresh), ())
        fn = build(node[1])
        arg = build(node[2])
        result = fresh()
        if not _unify(fn.raw, imp(arg.raw, result), subst):
            raise KernelReject(f"ill-typed application {term_pretty(node)}")
        return _TypedNode(node, result, (fn, arg))

    tree = build(term)
    if not _unify(tree.raw, goal, subst):
        raise KernelReject("term does not inhabit the goal")

    dummy = atoms_of(goal)[0] if atoms_of(goal) else "x"

    def ground(node: Any) -> Formula:
        node = _deref(node, subst)
        if isinstance(node, _Var):
            subst[node.n] = dummy
            return dummy
        if is_imp(node):
            return imp(ground(node[1]), ground(node[2]))
        return node

    steps: list[HilbertStep] = []

    def emit(tn: _TypedNode) -> int:
        if not tn.children:
            formula = ground(tn.raw)
            if tn.term == "S":
                steps.append(HilbertStep(formula=formula, rule="S"))
            elif tn.term == "K":
                steps.append(HilbertStep(formula=formula, rule="K"))
            else:
                steps.append(HilbertStep(formula=formula, rule="LEMMA", lemma_id=str(tn.term)))
            return len(steps) - 1
        fn_idx = emit(tn.children[0])
        arg_idx = emit(tn.children[1])
        fn_formula = steps[fn_idx].formula
        arg_formula = steps[arg_idx].formula
        if not is_imp(fn_formula) or fn_formula[1] != arg_formula:
            raise KernelReject("reconstructed MP premises do not match")
        steps.append(HilbertStep(formula=fn_formula[2], rule="MP", premises=(arg_idx, fn_idx)))
        return len(steps) - 1

    emit(tree)
    proof = HilbertProof(tuple(steps))
    checked = check_proof(proof, lemmas)
    if checked != goal:
        raise KernelReject("reconstructed conclusion is not the closed goal")
    return proof


# Known compact SK inhabitants used as acquisition search targets, not oracles.
B_TERM: Term = app(app("S", app("K", "S")), "K")  # S(KS)K
I_TERM: Term = app(app("S", "K"), "K")  # SKK
# Compact C: S(S(KS)(S(KK)S))(KK)
C_TERM: Term = app(
    app("S", app(app("S", app("K", "S")), app(app("S", app("K", "K")), "S"))),
    app("K", "K"),
)


@lru_cache(maxsize=None)
def sk_terms_of_size(n: int) -> tuple[Term, ...]:
    if n < 1:
        return ()
    if n == 1:
        return ("S", "K")
    out: list[Term] = []
    for left in range(1, n):
        right = n - left
        for fn in sk_terms_of_size(left):
            for arg in sk_terms_of_size(right):
                out.append(app(fn, arg))
    return tuple(out)


def library_terms_of_size(n: int, constants: tuple[str, ...]) -> tuple[Term, ...]:
    if n < 1:
        return ()
    if n == 1:
        return constants
    out: list[Term] = []
    for left in range(1, n):
        right = n - left
        for fn in library_terms_of_size(left, constants):
            for arg in library_terms_of_size(right, constants):
                out.append(app(fn, arg))
    return tuple(out)


@dataclass
class SearchCosts:
    terms_enumerated: int = 0
    type_inferences: int = 0
    successful_unifications: int = 0
    failed_unifications: int = 0
    kernel_checks: int = 0
    kernel_rejects: int = 0
    mp_attempts: int = 0
    lemma_instantiations: int = 0
    one_step_hits: int = 0
    nodes: int = 0
    skipped_nogoods: int = 0
    formulas_materialized: int = 0
    subgoals_introduced: int = 0
    wall_s: float = 0.0

    def as_dict(self) -> dict[str, int | float]:
        return {
            "terms_enumerated": self.terms_enumerated,
            "type_inferences": self.type_inferences,
            "successful_unifications": self.successful_unifications,
            "failed_unifications": self.failed_unifications,
            "kernel_checks": self.kernel_checks,
            "kernel_rejects": self.kernel_rejects,
            "mp_attempts": self.mp_attempts,
            "lemma_instantiations": self.lemma_instantiations,
            "one_step_hits": self.one_step_hits,
            "nodes": self.nodes,
            "skipped_nogoods": self.skipped_nogoods,
            "formulas_materialized": self.formulas_materialized,
            "subgoals_introduced": self.subgoals_introduced,
            "wall_s": self.wall_s,
        }


@dataclass
class SearchResult:
    status: str
    proof: HilbertProof | None
    term: Term | None
    costs: SearchCosts
    lemmas_used: tuple[str, ...]
    subgoals: tuple[Formula, ...]
    one_step_hits: tuple[str, ...]
    skipped_nogoods: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "lemmas_used": list(self.lemmas_used),
            "one_step_hits": list(self.one_step_hits),
            "skipped_nogoods": self.skipped_nogoods,
            "subgoals": [pretty(s) for s in self.subgoals],
            "term": term_pretty(self.term) if self.term is not None else None,
            "proof_length": len(self.proof.steps) if self.proof is not None else None,
            "mp_count": self.proof.mp_count() if self.proof is not None else None,
            "costs": self.costs.as_dict(),
        }


def one_step_screen(goal: Formula, lemmas: Mapping[str, Lemma]) -> tuple[str, ...]:
    """One-step successor matching: goal unifies with an axiom or lemma schema.

    Two-step derived lemmas are not consumed here. This is the failure mode of
    the Metamath one-step screens (#180): invocation count is zero when the
    goal is a composition rather than an instance.
    """
    hits: list[str] = []
    if is_k_instance(goal):
        hits.append("K")
    if is_s_instance(goal):
        hits.append("S")
    for lemma_id, lemma in lemmas.items():
        if lemma.authorized and unify_schema(lemma.schema, goal) is not None:
            hits.append(lemma_id)
    return tuple(hits)


@dataclass
class FailureMemory:
    """Scoped failed applications, keyed by alpha-normalized type shapes.

    Not a task-id blacklist. Compatible dead ends share a shape; a different
    theorem identity with the same local failure is skipped. Success outside
    the failure shape is preserved.
    """

    nogoods: set[tuple[str, str]] = field(default_factory=set)

    def key(self, operator: Formula, operand: Formula) -> tuple[str, str]:
        return (pretty(alpha_normalize(operator)), pretty(alpha_normalize(operand)))

    def record(self, operator: Formula, operand: Formula) -> None:
        self.nogoods.add(self.key(operator, operand))

    def should_skip(self, operator: Formula, operand: Formula) -> bool:
        return self.key(operator, operand) in self.nogoods

    def contains_task_id(self, task_id: str) -> bool:
        blob = " ".join(a + " " + b for a, b in self.nogoods)
        return task_id in blob

    def as_list(self) -> list[list[str]]:
        return sorted([list(item) for item in self.nogoods])


def _try_finish(term: Term, goal: Formula, lemmas: Mapping[str, Lemma], costs: SearchCosts) -> HilbertProof | None:
    costs.type_inferences += 1
    if not term_unifies_goal(term, goal, lemmas):
        costs.failed_unifications += 1
        return None
    costs.successful_unifications += 1
    try:
        proof = reconstruct_proof(term, goal, lemmas)
        costs.kernel_checks += 1
        return proof
    except KernelReject:
        costs.kernel_rejects += 1
        return None


def inhabit_well_typed(
    goal: Formula,
    constants: tuple[str, ...],
    lemmas: Mapping[str, Lemma],
    max_size: int,
    costs: SearchCosts | None = None,
    failure_memory: FailureMemory | None = None,
) -> SearchResult:
    """Bottom-up well-typed combinatory inhabitation (same searcher, varying constants).

    Only well-typed applications are retained. This is the primitive acquisition
    parent and the library consumer when constants include admitted lemmas.
    """
    costs = costs or SearchCosts()
    one_step = one_step_screen(goal, lemmas)
    costs.one_step_hits = len(one_step)
    subgoals: list[Formula] = []
    layers: dict[int, list[Term]] = {1: list(constants)}
    for const in constants:
        costs.terms_enumerated += 1
        costs.nodes += 1
        proof = _try_finish(const, goal, lemmas, costs)
        if proof is not None:
            return SearchResult(
                status="FOUND",
                proof=proof,
                term=const,
                costs=costs,
                lemmas_used=proof.lemmas_invoked(),
                subgoals=tuple(subgoals),
                one_step_hits=one_step,
                skipped_nogoods=costs.skipped_nogoods,
            )
    for size in range(2, max_size + 1):
        layer: list[Term] = []
        for left in range(1, size):
            right = size - left
            for fn in layers.get(left, ()):
                fn_type = infer_type(fn, lemmas)
                costs.type_inferences += 1
                for arg in layers.get(right, ()):
                    costs.terms_enumerated += 1
                    costs.nodes += 1
                    costs.mp_attempts += 1
                    arg_type = infer_type(arg, lemmas)
                    costs.type_inferences += 1
                    if fn_type is None or arg_type is None:
                        costs.failed_unifications += 1
                        continue
                    if failure_memory is not None and failure_memory.should_skip(fn_type, arg_type):
                        costs.skipped_nogoods += 1
                        continue
                    term = app(fn, arg)
                    if infer_type(term, lemmas) is None:
                        costs.failed_unifications += 1
                        if failure_memory is not None:
                            failure_memory.record(fn_type, arg_type)
                        continue
                    layer.append(term)
                    if is_imp(fn_type):
                        subgoals.append(fn_type[1])
                        costs.subgoals_introduced += 1
                    proof = _try_finish(term, goal, lemmas, costs)
                    if proof is not None:
                        return SearchResult(
                            status="FOUND",
                            proof=proof,
                            term=term,
                            costs=costs,
                            lemmas_used=proof.lemmas_invoked(),
                            subgoals=tuple(subgoals),
                            one_step_hits=one_step,
                            skipped_nogoods=costs.skipped_nogoods,
                        )
        layers[size] = layer
    return SearchResult(
        status="NOT_FOUND",
        proof=None,
        term=None,
        costs=costs,
        lemmas_used=(),
        subgoals=tuple(subgoals),
        one_step_hits=one_step,
        skipped_nogoods=costs.skipped_nogoods,
    )


def inhabit_by_enumeration(
    goal: Formula,
    constants: tuple[str, ...],
    lemmas: Mapping[str, Lemma],
    max_size: int,
    costs: SearchCosts | None = None,
    failure_memory: FailureMemory | None = None,
) -> SearchResult:
    """Size-bounded combinatory inhabitation including ill-typed terms (failure memory)."""
    costs = costs or SearchCosts()
    one_step = one_step_screen(goal, lemmas)
    costs.one_step_hits = len(one_step)
    subgoals: list[Formula] = []
    for size in range(1, max_size + 1):
        terms = library_terms_of_size(size, constants)
        for term in terms:
            costs.terms_enumerated += 1
            costs.nodes += 1
            if isinstance(term, tuple):
                fn_type = infer_type(term[1], lemmas)
                arg_type = infer_type(term[2], lemmas)
                costs.mp_attempts += 1
                costs.type_inferences += 2
                if fn_type is None or arg_type is None:
                    costs.failed_unifications += 1
                    continue
                if failure_memory is not None and failure_memory.should_skip(fn_type, arg_type):
                    costs.skipped_nogoods += 1
                    continue
                if infer_type(term, lemmas) is None:
                    costs.failed_unifications += 1
                    if failure_memory is not None:
                        failure_memory.record(fn_type, arg_type)
                    continue
                if is_imp(fn_type):
                    subgoals.append(fn_type[1])
                    costs.subgoals_introduced += 1
            proof = _try_finish(term, goal, lemmas, costs)
            if proof is not None:
                return SearchResult(
                    status="FOUND",
                    proof=proof,
                    term=term,
                    costs=costs,
                    lemmas_used=proof.lemmas_invoked(),
                    subgoals=tuple(subgoals),
                    one_step_hits=one_step,
                    skipped_nogoods=costs.skipped_nogoods,
                )
    return SearchResult(
        status="NOT_FOUND",
        proof=None,
        term=None,
        costs=costs,
        lemmas_used=(),
        subgoals=tuple(subgoals),
        one_step_hits=one_step,
        skipped_nogoods=costs.skipped_nogoods,
    )


def mappings_from_pool(names: tuple[str, ...], pool: tuple[Formula, ...]) -> Iterable[dict[str, Formula]]:
    if not names:
        yield {}
        return
    first, rest = names[0], names[1:]
    for formula in pool:
        for tail in mappings_from_pool(rest, pool):
            yield {first: formula, **tail}


def _shift_proof(proof: HilbertProof, offset: int) -> tuple[HilbertStep, ...]:
    shifted = []
    for step in proof.steps:
        premises = tuple(p + offset for p in step.premises) if step.rule == "MP" else step.premises
        shifted.append(HilbertStep(
            formula=step.formula,
            rule=step.rule,
            premises=premises,
            lemma_id=step.lemma_id,
        ))
    return tuple(shifted)


def goal_only_mp_search(
    goal: Formula,
    lemmas: Mapping[str, Lemma],
    max_mp: int,
    failure_memory: FailureMemory | None = None,
    include_axioms: bool = True,
) -> SearchResult:
    """Goal-only intermediate-consuming consumer.

    Seeds axiom/lemma instances over the goal's formula closure, then saturates
    MP using an antecedent index. Lemma conclusions that are not the goal become
    intermediates. One-step identity matching is recorded separately and is not
    this consumer.
    """
    costs = SearchCosts()
    one_step = one_step_screen(goal, lemmas)
    costs.one_step_hits = len(one_step)
    pool = subformulas(goal)
    costs.formulas_materialized = len(pool)
    bank: dict[Formula, HilbertProof] = {}
    by_antecedent: dict[Formula, list[tuple[Formula, HilbertProof]]] = {}
    subgoals: list[Formula] = []

    def index_implication(proof: HilbertProof) -> None:
        formula = proof.conclusion
        if is_imp(formula):
            by_antecedent.setdefault(formula[1], []).append((formula, proof))

    def admit(proof: HilbertProof) -> bool:
        formula = proof.conclusion
        if formula in bank:
            return False
        bank[formula] = proof
        costs.formulas_materialized += 1
        index_implication(proof)
        return True

    if include_axioms:
        for mapping in mappings_from_pool(("A", "B"), pool):
            formula = instantiate_schema(K_SCHEMA, mapping)
            admit(HilbertProof((HilbertStep(formula=formula, rule="K"),)))
        for mapping in mappings_from_pool(("A", "B", "C"), pool):
            formula = instantiate_schema(S_SCHEMA, mapping)
            admit(HilbertProof((HilbertStep(formula=formula, rule="S"),)))

    authorized = {k: v for k, v in lemmas.items() if v.authorized}
    for lemma_id, lemma in authorized.items():
        names = schema_vars(lemma.schema)
        for mapping in mappings_from_pool(names, pool):
            formula = instantiate_schema(lemma.schema, mapping)
            costs.lemma_instantiations += 1
            if formula != goal:
                subgoals.append(formula)
                costs.subgoals_introduced += 1
            admit(HilbertProof((HilbertStep(formula=formula, rule="LEMMA", lemma_id=lemma_id),)))

    if goal in bank:
        proof = bank[goal]
        costs.kernel_checks += 1
        check_proof(proof, lemmas)
        return SearchResult(
            status="FOUND",
            proof=proof,
            term=None,
            costs=costs,
            lemmas_used=proof.lemmas_invoked(),
            subgoals=tuple(subgoals),
            one_step_hits=one_step,
        )

    progress = True
    while progress and costs.mp_attempts < max_mp:
        progress = False
        for ant_formula, ant_proof in list(bank.items()):
            for impl_formula, impl_proof in list(by_antecedent.get(ant_formula, ())):
                costs.nodes += 1
                costs.mp_attempts += 1
                if failure_memory is not None and failure_memory.should_skip(impl_formula, ant_formula):
                    costs.skipped_nogoods += 1
                    continue
                conclusion = impl_formula[2]
                if conclusion in bank:
                    continue
                offset = len(ant_proof.steps)
                merged = ant_proof.steps + _shift_proof(impl_proof, offset)
                i = len(ant_proof.steps) - 1
                j = len(merged) - 1
                new_proof = HilbertProof(merged + (
                    HilbertStep(formula=conclusion, rule="MP", premises=(i, j)),
                ))
                try:
                    costs.kernel_checks += 1
                    check_proof(new_proof, lemmas)
                except KernelReject:
                    costs.kernel_rejects += 1
                    if failure_memory is not None:
                        failure_memory.record(impl_formula, ant_formula)
                    continue
                costs.successful_unifications += 1
                admit(new_proof)
                progress = True
                if conclusion == goal:
                    return SearchResult(
                        status="FOUND",
                        proof=new_proof,
                        term=None,
                        costs=costs,
                        lemmas_used=new_proof.lemmas_invoked(),
                        subgoals=tuple(subgoals),
                        one_step_hits=one_step,
                        skipped_nogoods=costs.skipped_nogoods,
                    )
    return SearchResult(
        status="NOT_FOUND",
        proof=None,
        term=None,
        costs=costs,
        lemmas_used=(),
        subgoals=tuple(subgoals),
        one_step_hits=one_step,
        skipped_nogoods=costs.skipped_nogoods,
    )


def formula_to_json(formula: Formula):
    if not is_imp(formula):
        return str(formula)
    return ["imp", formula_to_json(formula[1]), formula_to_json(formula[2])]


def json_to_formula(data) -> Formula:
    if isinstance(data, str):
        return data
    if isinstance(data, list) and data and data[0] == "imp":
        return imp(json_to_formula(data[1]), json_to_formula(data[2]))
    raise ValueError(f"bad formula json: {data!r}")


def term_to_json(term: Term):
    if not isinstance(term, tuple):
        return str(term)
    return ["app", term_to_json(term[1]), term_to_json(term[2])]


def json_to_term(data) -> Term:
    if isinstance(data, str):
        return data
    if isinstance(data, list) and data and data[0] == "app":
        return app(json_to_term(data[1]), json_to_term(data[2]))
    raise ValueError(f"bad term json: {data!r}")


def lemma_to_json(lemma: Lemma) -> dict:
    return {
        "lemma_id": lemma.lemma_id,
        "schema": formula_to_json(lemma.schema),
        "witness_term": term_to_json(lemma.witness_term),
        "support_ids": list(lemma.support_ids),
        "authorized": lemma.authorized,
    }


def lemma_from_json(data: Mapping[str, Any]) -> Lemma:
    return Lemma(
        lemma_id=str(data["lemma_id"]),
        schema=json_to_formula(data["schema"]),
        witness_term=json_to_term(data["witness_term"]),
        support_ids=tuple(data["support_ids"]),
        authorized=bool(data["authorized"]),
    )


def retrieve_nearest_lemmas(goal: Formula, lemmas: Mapping[str, Lemma], k: int) -> tuple[str, ...]:
    ranked = sorted(
        (
            (bag_jaccard(goal, lemma.schema), lemma_id)
            for lemma_id, lemma in lemmas.items()
            if lemma.authorized
        ),
        key=lambda row: (-row[0], row[1]),
    )
    return tuple(lemma_id for _score, lemma_id in ranked[:k])
