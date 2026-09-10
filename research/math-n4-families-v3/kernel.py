"""Tiny Hilbert/SK family worlds on the frozen MATH-1 microscope kernels.

Loads v1 (lemma reuse) and v2 (CUT_* subgoal) kernels by path. Does not copy
those files, does not mint PREFIX/SWAP names, and does not claim Metamath N4
or FLT. Family identities are invented CUT_* lemmas over successor, a
ring-distrib composition, a contraction counting identity, and even/odd
mod-2 shapes.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Mapping

_HERE = Path(__file__).resolve().parent
_V1_PATH = _HERE.parent / "math-n4-lemma-reuse-v1" / "kernel.py"
_V2_PATH = _HERE.parent / "math-n4-subgoal-v2" / "kernel.py"


def _load(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load kernel at {path}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_V1 = _load("math_n4_lemma_reuse_v1_kernel", _V1_PATH)
_V2 = _load("math_n4_subgoal_v2_kernel", _V2_PATH)

# Re-export the registered microscope. Do not fork v1/v2 salts.
Atom = _V1.Atom
Formula = _V1.Formula
HilbertProof = _V1.HilbertProof
HilbertStep = _V1.HilbertStep
KernelReject = _V1.KernelReject
Lemma = _V1.Lemma
SearchCosts = _V1.SearchCosts
SearchResult = _V1.SearchResult
Term = _V1.Term
app = _V1.app
imp = _V1.imp
is_imp = _V1.is_imp
pretty = _V1.pretty
alpha_normalize = _V1.alpha_normalize
atoms_of = _V1.atoms_of
schema_vars = _V1.schema_vars
check_proof = _V1.check_proof
formula_to_json = _V1.formula_to_json
json_to_formula = _V1.json_to_formula
json_to_term = _V1.json_to_term
lemma_from_json = _V1.lemma_from_json
lemma_to_json = _V1.lemma_to_json
term_to_json = _V1.term_to_json
instantiate_schema = _V1.instantiate_schema
unify_schema = _V1.unify_schema
infer_type = _V1.infer_type
term_pretty = _V1.term_pretty
term_size = _V1.term_size
term_unifies_goal = _V1.term_unifies_goal
reconstruct_proof = _V1.reconstruct_proof
inhabit_well_typed = _V1.inhabit_well_typed
one_step_screen = _V1.one_step_screen
retrieve_nearest_lemmas = _V1.retrieve_nearest_lemmas
goal_only_mp_search = _V1.goal_only_mp_search
B_TERM = _V1.B_TERM
C_TERM = _V1.C_TERM
I_TERM = _V1.I_TERM
K_SCHEMA = _V1.K_SCHEMA
S_SCHEMA = _V1.S_SCHEMA
PREFIX_SCHEMA = _V1.PREFIX_SCHEMA
SWAP_SCHEMA = _V1.SWAP_SCHEMA
IDENTITY_SCHEMA = _V1.IDENTITY_SCHEMA
COMPOSE_SECOND_SCHEMA = _V2.COMPOSE_SECOND_SCHEMA
FROZEN_TRAINING_LEMMA_NAMES = _V2.FROZEN_TRAINING_LEMMA_NAMES
mint_cut_id = _V2.mint_cut_id

# Successor-arithmetic: PREFIX / B adds one implication layer.
SUCC_SCHEMA: Formula = PREFIX_SCHEMA
# Ring-distrib miniature: left-distribute an outer premise over composition.
DISTRIB_SCHEMA: Formula = COMPOSE_SECOND_SCHEMA
# Combinatorics miniature: contraction, two argument slots count as one.
COUNT_SCHEMA: Formula = imp(imp("A", imp("A", "B")), imp("A", "B"))
# Number-theory miniature: even = identity, odd = argument swap (mod-2).
EVEN_SCHEMA: Formula = IDENTITY_SCHEMA
ODD_SCHEMA: Formula = SWAP_SCHEMA
# Iterator type inhabited by both I and SBI (mod-2 collapse at types).
ITER_SCHEMA: Formula = imp(imp("A", "A"), imp("A", "A"))

# Compact contraction witness found first by size-4 SK search: (S S)(S K).
COUNT_TERM: Term = app(app("S", "S"), app("S", "K"))
# Church-2-shaped combinator SBI; not a unique inhabitant of ITER_SCHEMA.
SBI_TERM: Term = app(app("S", B_TERM), I_TERM)
BB_TERM: Term = app(B_TERM, B_TERM)

# v1 declared prior catalog. Not W, not BB.
V1_CATALOG: tuple[tuple[str, Term], ...] = (("I", I_TERM), ("B", B_TERM), ("C", C_TERM))
FROZEN_NAMES = FROZEN_TRAINING_LEMMA_NAMES


def closed_goal(schema: Formula, atoms: Mapping[str, str]) -> Formula:
    return instantiate_schema(schema, atoms)


def lemma_from_schema(
    schema: Formula,
    witness: Term,
    support_ids: tuple[str, ...],
    authorized: bool = True,
) -> Lemma:
    lemma_id = mint_cut_id(alpha_normalize(schema))
    if lemma_id in FROZEN_NAMES:
        raise RuntimeError(f"refusing frozen training lemma name {lemma_id}")
    return Lemma(
        lemma_id=lemma_id,
        schema=alpha_normalize(schema),
        witness_term=witness,
        support_ids=support_ids,
        authorized=authorized,
    )


def exact_check(
    proof: HilbertProof,
    expected: Formula,
    lemmas: Mapping[str, Lemma] | None = None,
) -> Formula:
    """Exact Hilbert checker. Float/numeric answers are not licensed."""
    if isinstance(expected, float) or isinstance(proof, float):
        raise KernelReject("numeric float answers are not licensed")
    got = check_proof(proof, lemmas or {})
    if got != expected:
        raise KernelReject("reconstructed conclusion is not the closed goal")
    return got


def exact_answers_equal(left: Formula, right: Formula) -> bool:
    if isinstance(left, float) or isinstance(right, float):
        raise KernelReject("numeric float answers are not licensed")
    return left == right


def is_app(term: Term) -> bool:
    return isinstance(term, tuple) and len(term) == 3 and term[0] == "app"


def _leftmost_outermost(term: Term) -> Term | None:
    """One weak combinatory step. Orient K/S (and derived I=SKK) left to right."""
    if not is_app(term):
        return None
    fn, arg = term[1], term[2]
    if is_app(fn) and fn[1] == "K":
        return fn[2]
    if (
        is_app(fn)
        and is_app(fn[1])
        and fn[1][1] == "S"
    ):
        x = fn[1][2]
        y = fn[2]
        z = arg
        return app(app(x, z), app(y, z))
    reduced_fn = _leftmost_outermost(fn)
    if reduced_fn is not None:
        return app(reduced_fn, arg)
    reduced_arg = _leftmost_outermost(arg)
    if reduced_arg is not None:
        return app(fn, reduced_arg)
    return None


def knuth_bendix_normalize(term: Term, max_steps: int = 64) -> tuple[Term, int]:
    """Bounded weak reduction. Not a complete SK decision procedure."""
    current = term
    steps = 0
    for _ in range(max_steps):
        nxt = _leftmost_outermost(current)
        if nxt is None:
            break
        current = nxt
        steps += 1
    return current, steps


def terms_weakly_equal(left: Term, right: Term, max_steps: int = 64) -> bool:
    a, _ = knuth_bendix_normalize(left, max_steps)
    b, _ = knuth_bendix_normalize(right, max_steps)
    return a == b


@dataclass
class ParentResult:
    parent_id: str
    status: str
    term: Term | None
    proof: HilbertProof | None
    hits: tuple[str, ...]
    costs: SearchCosts
    prior_information: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "parent_id": self.parent_id,
            "status": self.status,
            "term": term_pretty(self.term) if self.term is not None else None,
            "proof_length": len(self.proof.steps) if self.proof is not None else None,
            "mp_count": self.proof.mp_count() if self.proof is not None else None,
            "hits": list(self.hits),
            "prior_information": list(self.prior_information),
            "costs": self.costs.as_dict(),
        }


def catalog_rewrite_parent(
    goal: Formula,
    catalog: tuple[tuple[str, Term], ...] = V1_CATALOG,
) -> ParentResult:
    """Knuth-Bendix-ish specialized parent: match a frozen oriented SK catalog."""
    costs = SearchCosts()
    hits: list[str] = []
    chosen: Term | None = None
    proof: HilbertProof | None = None
    for name, term in catalog:
        costs.terms_enumerated += 1
        costs.type_inferences += 1
        if term_unifies_goal(term, goal):
            hits.append(name)
            if chosen is None:
                try:
                    proof = reconstruct_proof(term, goal)
                    costs.kernel_checks += 1
                    exact_check(proof, goal)
                    chosen = term
                except KernelReject:
                    costs.kernel_rejects += 1
    status = "FOUND" if proof is not None else "NOT_FOUND"
    return ParentResult(
        parent_id="knuth_bendix_v1_catalog",
        status=status,
        term=chosen,
        proof=proof,
        hits=tuple(hits),
        costs=costs,
        prior_information=tuple(name for name, _term in catalog),
    )


def tautology_table_parent(goal: Formula, max_mp: int = 2500) -> ParentResult:
    """Hilbert tautology table: K/S instances over the goal closure, then MP."""
    row = goal_only_mp_search(goal, {}, max_mp=max_mp)
    return ParentResult(
        parent_id="hilbert_tautology_table",
        status=row.status,
        term=row.term,
        proof=row.proof,
        hits=row.one_step_hits,
        costs=row.costs,
        prior_information=("K", "S", "MP"),
    )


def primitive_sk_parent(goal: Formula, max_size: int) -> ParentResult:
    row = inhabit_well_typed(goal, ("S", "K"), {}, max_size)
    return ParentResult(
        parent_id=f"primitive_sk_size_{max_size}",
        status=row.status,
        term=row.term,
        proof=row.proof,
        hits=row.one_step_hits,
        costs=row.costs,
        prior_information=("S", "K"),
    )


def library_serve(
    goal: Formula,
    lemmas: Mapping[str, Lemma],
    max_size: int = 2,
) -> SearchResult:
    authorized = {k: v for k, v in lemmas.items() if v.authorized}
    constants = ("S", "K") + tuple(authorized.keys())
    return inhabit_well_typed(goal, constants, authorized, max_size)


def acquire_by_sk(
    schema: Formula,
    training: tuple[tuple[str, Mapping[str, str]], ...],
    max_size: int,
) -> tuple[Lemma, tuple[SearchResult, ...], Term]:
    """Anti-unify one combinator across training substitutions; mint CUT_*."""
    found: list[Term] = []
    rows: list[SearchResult] = []
    for task_id, atoms in training:
        goal = closed_goal(schema, atoms)
        row = inhabit_well_typed(goal, ("S", "K"), {}, max_size)
        if row.status != "FOUND" or row.term is None or row.proof is None:
            raise RuntimeError(f"acquisition missed {task_id}")
        exact_check(row.proof, goal)
        found.append(row.term)
        rows.append(row)
    shapes = {term_pretty(term) for term in found}
    if len(shapes) != 1:
        raise RuntimeError(f"training terms did not anti-unify: {sorted(shapes)}")
    witness = found[0]
    lemma = lemma_from_schema(
        schema,
        witness,
        support_ids=tuple(task_id for task_id, _atoms in training),
    )
    return lemma, tuple(rows), witness


def acquire_from_catalog(
    schema: Formula,
    training: tuple[tuple[str, Mapping[str, str]], ...],
    catalog: tuple[tuple[str, Term], ...],
    miss_size: int,
) -> tuple[Lemma, tuple[dict[str, Any], ...], Term, tuple[str, ...]]:
    """Size-bounded miss, then unique catalog hit. Catalog is prior information."""
    misses: list[dict[str, Any]] = []
    for task_id, atoms in training:
        goal = closed_goal(schema, atoms)
        row = inhabit_well_typed(goal, ("S", "K"), {}, miss_size)
        misses.append({
            "task_id": task_id,
            "status": row.status,
            "terms_enumerated": row.costs.terms_enumerated,
            "nodes": row.costs.nodes,
        })
        if row.status == "FOUND":
            raise RuntimeError(f"catalog would be redundant for {task_id}")
    hits: list[str] = []
    for name, term in catalog:
        if all(term_unifies_goal(term, closed_goal(schema, atoms)) for _id, atoms in training):
            hits.append(name)
    if len(hits) != 1:
        raise RuntimeError(f"expected unique catalog hit, got {hits}")
    name = hits[0]
    witness = dict(catalog)[name]
    for task_id, atoms in training:
        goal = closed_goal(schema, atoms)
        proof = reconstruct_proof(witness, goal)
        exact_check(proof, goal)
    lemma = lemma_from_schema(
        schema,
        witness,
        support_ids=tuple(task_id for task_id, _atoms in training),
    )
    return lemma, tuple(misses), witness, tuple(hits)


@dataclass
class ConjectureOutcome:
    conjecture_id: str
    claim: str
    status: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "conjecture_id": self.conjecture_id,
            "claim": self.claim,
            "status": self.status,
            "evidence": self.evidence,
        }


def test_conjecture_transfer(
    conjecture_id: str,
    claim: str,
    goal: Formula,
    lemmas: Mapping[str, Lemma],
    expect_found: bool,
    max_size: int = 2,
) -> ConjectureOutcome:
    row = library_serve(goal, lemmas, max_size)
    found = row.status == "FOUND"
    if found == expect_found:
        status = "CONFIRMED" if expect_found else "CONFIRMED"
    else:
        status = "REFUTED"
    # Honesty: a conjecture that predicted success is confirmed iff found;
    # a conjecture that predicted failure is confirmed iff not found.
    predicted_found = expect_found
    status = "CONFIRMED" if found == predicted_found else "REFUTED"
    return ConjectureOutcome(
        conjecture_id=conjecture_id,
        claim=claim,
        status=status,
        evidence={
            "found": found,
            "predicted_found": predicted_found,
            "lemmas_used": list(row.lemmas_used),
            "one_step_hits": list(row.one_step_hits),
            "mp_attempts": row.costs.mp_attempts,
            "kernel_checks": row.costs.kernel_checks,
            "term": term_pretty(row.term) if row.term is not None else None,
        },
    )


def test_conjecture_unique_inhabitant(
    conjecture_id: str,
    claim: str,
    goal: Formula,
    candidate_terms: tuple[tuple[str, Term], ...],
) -> ConjectureOutcome:
    """Exact term/type checker. Multiple inhabitants refute uniqueness."""
    inhabiting: list[str] = []
    proofs: dict[str, int] = {}
    for name, term in candidate_terms:
        if term_unifies_goal(term, goal):
            proof = reconstruct_proof(term, goal)
            exact_check(proof, goal)
            inhabiting.append(name)
            proofs[name] = len(proof.steps)
    unique = len(inhabiting) == 1
    return ConjectureOutcome(
        conjecture_id=conjecture_id,
        claim=claim,
        status="CONFIRMED" if unique else "REFUTED",
        evidence={
            "inhabiting_terms": inhabiting,
            "proof_lengths": proofs,
            "weak_I_eq_SBI": terms_weakly_equal(I_TERM, SBI_TERM),
            "float_used": False,
        },
    )


@dataclass
class Discrimination:
    goal_id: str
    one_step_hits: tuple[str, ...]
    selected: tuple[str, ...]
    served: SearchResult
    sk4: ParentResult
    one_step_cheaper: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "one_step_hits": list(self.one_step_hits),
            "selected": list(self.selected),
            "served_status": self.served.status,
            "served_lemmas": list(self.served.lemmas_used),
            "served_mp_attempts": self.served.costs.mp_attempts,
            "served_kernel_checks": self.served.costs.kernel_checks,
            "served_terms_enumerated": self.served.costs.terms_enumerated,
            "sk4_status": self.sk4.status,
            "sk4_terms_enumerated": self.sk4.costs.terms_enumerated,
            "sk4_mp_attempts": self.sk4.costs.mp_attempts,
            "one_step_or_library_cheaper_than_sk4": self.one_step_cheaper,
        }


def discriminate(
    goal_id: str,
    goal: Formula,
    lemmas: Mapping[str, Lemma],
) -> Discrimination:
    """Cheap one-step screen, then library consume; compare with SK size 4."""
    hits = one_step_screen(goal, lemmas)
    served = library_serve(goal, lemmas, 2)
    sk4 = primitive_sk_parent(goal, 4)
    library_work = served.costs.terms_enumerated + served.costs.mp_attempts
    sk4_work = sk4.costs.terms_enumerated + sk4.costs.mp_attempts
    cheaper = library_work < sk4_work
    return Discrimination(
        goal_id=goal_id,
        one_step_hits=hits,
        selected=hits if hits else served.lemmas_used,
        served=served,
        sk4=sk4,
        one_step_cheaper=cheaper,
    )
