"""Subgoal discovery + named-lemma introduction on the miniature Hilbert kernel.

Loads the frozen v1 kernel by path (does not edit it). New mechanism: invent a
CUT_* identity that is not the goal and not a frozen training lemma name, then
finish the goal and reuse the named lemma on a fresh theorem.
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Mapping

_V1_PATH = Path(__file__).resolve().parent.parent / "math-n4-lemma-reuse-v1" / "kernel.py"
_SPEC = spec_from_file_location("math_n4_lemma_reuse_v1_kernel", _V1_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load frozen v1 kernel at {_V1_PATH}")
_V1 = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _V1
_SPEC.loader.exec_module(_V1)

# Re-export the registered Hilbert microscope. Do not fork v1 salts or files.
Atom = _V1.Atom
Formula = _V1.Formula
HilbertProof = _V1.HilbertProof
HilbertStep = _V1.HilbertStep
KernelReject = _V1.KernelReject
Lemma = _V1.Lemma
SearchCosts = _V1.SearchCosts
SearchResult = _V1.SearchResult
Term = _V1.Term
FailureMemory = _V1.FailureMemory
app = _V1.app
imp = _V1.imp
is_imp = _V1.is_imp
pretty = _V1.pretty
alpha_normalize = _V1.alpha_normalize
atoms_of = _V1.atoms_of
bag_jaccard = _V1.bag_jaccard
bag_of_symbols = _V1.bag_of_symbols
check_proof = _V1.check_proof
formula_to_json = _V1.formula_to_json
json_to_formula = _V1.json_to_formula
json_to_term = _V1.json_to_term
lemma_from_json = _V1.lemma_from_json
lemma_to_json = _V1.lemma_to_json
term_to_json = _V1.term_to_json
instantiate_schema = _V1.instantiate_schema
unify_schema = _V1.unify_schema
is_k_instance = _V1.is_k_instance
is_s_instance = _V1.is_s_instance
infer_type = _V1.infer_type
term_pretty = _V1.term_pretty
term_size = _V1.term_size
term_unifies_goal = _V1.term_unifies_goal
reconstruct_proof = _V1.reconstruct_proof
inhabit_well_typed = _V1.inhabit_well_typed
inhabit_by_enumeration = _V1.inhabit_by_enumeration
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
SUFFIX_SCHEMA = _V1.SUFFIX_SCHEMA
IDENTITY_SCHEMA = _V1.IDENTITY_SCHEMA

# Frozen v1 training lemma *names*. v2 must not mint or consume these identities
# as the invented intermediate.
FROZEN_TRAINING_LEMMA_NAMES = frozenset({"PREFIX", "SWAP"})

# Principal type of B B: compose PREFIX with itself on the second argument.
# (A → (B → C)) → (A → ((D → B) → (D → C)))
COMPOSE_SECOND_SCHEMA: Formula = imp(
    imp("A", imp("B", "C")),
    imp("A", imp(imp("D", "B"), imp("D", "C"))),
)


def mint_cut_id(schema: Formula) -> str:
    """Stable lemma id from an alpha-normalized schema. Never PREFIX or SWAP."""
    blob = pretty(alpha_normalize(schema)).encode("utf-8")
    lemma_id = "CUT_" + hashlib.sha256(blob).hexdigest()[:12]
    if lemma_id in FROZEN_TRAINING_LEMMA_NAMES:
        raise RuntimeError(f"mint collided with frozen training lemma name: {lemma_id}")
    return lemma_id


def is_primitive_axiom_schema(formula: Formula) -> bool:
    return is_k_instance(formula) or is_s_instance(formula)


@dataclass(frozen=True)
class PrimitiveIdentity:
    schema: Formula
    witness_term: Term
    witness_size: int
    lemma_id: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "lemma_id": self.lemma_id,
            "schema": pretty(self.schema),
            "witness_term": term_pretty(self.witness_term),
            "witness_size": self.witness_size,
        }


def collect_primitive_identities(
    max_size: int,
    costs: SearchCosts | None = None,
) -> tuple[PrimitiveIdentity, ...]:
    """Well-typed SK inhabitants whose principal types are not K/S axioms.

    Each distinct alpha-normalized type is kept once, first witness wins.
    These are candidate subgoal identities, not frozen PREFIX/SWAP names.
    """
    costs = costs or SearchCosts()
    layers: dict[int, list[Term]] = {1: ["S", "K"]}
    seen: set[str] = set()
    found: list[PrimitiveIdentity] = []
    for const in ("S", "K"):
        costs.terms_enumerated += 1
        costs.nodes += 1
        costs.type_inferences += 1
        typ = infer_type(const)
        if typ is None:
            continue
        _consider_identity(const, typ, seen, found)
    for size in range(2, max_size + 1):
        layer: list[Term] = []
        for left in range(1, size):
            right = size - left
            for fn in layers.get(left, ()):
                fn_type = infer_type(fn)
                costs.type_inferences += 1
                for arg in layers.get(right, ()):
                    costs.terms_enumerated += 1
                    costs.nodes += 1
                    costs.mp_attempts += 1
                    arg_type = infer_type(arg)
                    costs.type_inferences += 1
                    if fn_type is None or arg_type is None:
                        costs.failed_unifications += 1
                        continue
                    term = app(fn, arg)
                    typ = infer_type(term)
                    costs.type_inferences += 1
                    if typ is None:
                        costs.failed_unifications += 1
                        continue
                    layer.append(term)
                    _consider_identity(term, typ, seen, found)
        layers[size] = layer
    found.sort(key=lambda row: (row.witness_size, row.lemma_id))
    return tuple(found)


def _consider_identity(
    term: Term,
    typ: Formula,
    seen: set[str],
    found: list[PrimitiveIdentity],
) -> None:
    schema = alpha_normalize(typ)
    if is_primitive_axiom_schema(schema):
        return
    key = pretty(schema)
    if key in seen:
        return
    seen.add(key)
    found.append(
        PrimitiveIdentity(
            schema=schema,
            witness_term=term,
            witness_size=term_size(term),
            lemma_id=mint_cut_id(schema),
        )
    )


@dataclass
class CandidateAttempt:
    identity: PrimitiveIdentity
    finish: SearchResult
    admitted: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "lemma_id": self.identity.lemma_id,
            "schema": pretty(self.identity.schema),
            "witness_term": term_pretty(self.identity.witness_term),
            "witness_size": self.identity.witness_size,
            "finish_status": self.finish.status,
            "admitted": self.admitted,
            "lemmas_used": list(self.finish.lemmas_used),
            "term": term_pretty(self.finish.term) if self.finish.term is not None else None,
        }


@dataclass
class DiscoveryResult:
    status: str
    invented_lemma: Lemma | None
    invented_identity: PrimitiveIdentity | None
    finish: SearchResult
    candidates: tuple[CandidateAttempt, ...]
    identities_enumerated: int
    one_step_hits: tuple[str, ...]
    costs: SearchCosts = field(default_factory=SearchCosts)

    def as_dict(self) -> dict[str, Any]:
        lemma = self.invented_lemma
        ident = self.invented_identity
        return {
            "status": self.status,
            "invented_lemma_id": lemma.lemma_id if lemma is not None else None,
            "invented_schema": pretty(ident.schema) if ident is not None else None,
            "invented_witness": term_pretty(ident.witness_term) if ident is not None else None,
            "frozen_name_collision": (
                lemma.lemma_id in FROZEN_TRAINING_LEMMA_NAMES if lemma is not None else False
            ),
            "identities_enumerated": self.identities_enumerated,
            "candidates_tried": [row.as_dict() for row in self.candidates],
            "one_step_hits": list(self.one_step_hits),
            "finish": self.finish.as_dict(),
            "costs": self.costs.as_dict(),
        }


def lemma_from_identity(
    identity: PrimitiveIdentity,
    support_ids: tuple[str, ...],
    authorized: bool = True,
) -> Lemma:
    if identity.lemma_id in FROZEN_TRAINING_LEMMA_NAMES:
        raise RuntimeError(f"refusing frozen training lemma name {identity.lemma_id}")
    return Lemma(
        lemma_id=identity.lemma_id,
        schema=identity.schema,
        witness_term=identity.witness_term,
        support_ids=support_ids,
        authorized=authorized,
    )


def subgoal_discover_and_finish(
    goal: Formula,
    support_ids: tuple[str, ...],
    max_primitive: int = 4,
    max_library: int = 2,
    frozen_lemmas: Mapping[str, Lemma] | None = None,
) -> DiscoveryResult:
    """Invent a CUT_* subgoal identity, then finish `goal` with that named lemma.

    Frozen training lemma names PREFIX/SWAP are never minted. K/S axiom schemas
    are not treated as invented lemmas. The selected identity's alpha-normalized
    type must differ from the goal.
    """
    frozen_lemmas = dict(frozen_lemmas or {})
    for name in frozen_lemmas:
        if name in FROZEN_TRAINING_LEMMA_NAMES:
            raise RuntimeError(f"v2 discovery refuses frozen v1 lemma {name}")
    costs = SearchCosts()
    one_step = one_step_screen(goal, frozen_lemmas)
    costs.one_step_hits = len(one_step)
    identities = collect_primitive_identities(max_primitive, costs)
    attempts: list[CandidateAttempt] = []
    goal_shape = pretty(alpha_normalize(goal))
    for identity in identities:
        if identity.lemma_id in FROZEN_TRAINING_LEMMA_NAMES:
            continue
        if pretty(identity.schema) == goal_shape:
            continue
        lemma = lemma_from_identity(identity, support_ids)
        library = dict(frozen_lemmas)
        library[lemma.lemma_id] = lemma
        constants = ("S", "K") + tuple(library.keys())
        finish = inhabit_well_typed(goal, constants, library, max_library, costs=SearchCosts())
        admitted = (
            finish.status == "FOUND"
            and finish.term is not None
            and lemma.lemma_id in finish.lemmas_used
            and lemma.lemma_id not in FROZEN_TRAINING_LEMMA_NAMES
        )
        attempts.append(CandidateAttempt(identity=identity, finish=finish, admitted=admitted))
        if admitted:
            if finish.proof is not None:
                check_proof(finish.proof, library)
            closed = infer_type(identity.witness_term)
            if closed is None:
                raise KernelReject("invented witness is ill-typed")
            holdout_ok = term_unifies_goal(identity.witness_term, closed)
            if not holdout_ok:
                raise KernelReject("invented witness does not inhabit its principal type")
            reconstruct_proof(identity.witness_term, closed)
            return DiscoveryResult(
                status="FOUND",
                invented_lemma=lemma,
                invented_identity=identity,
                finish=finish,
                candidates=tuple(attempts),
                identities_enumerated=len(identities),
                one_step_hits=one_step,
                costs=costs,
            )
    empty = inhabit_well_typed(goal, ("S", "K"), frozen_lemmas, max_library, costs=SearchCosts())
    return DiscoveryResult(
        status="NOT_FOUND",
        invented_lemma=None,
        invented_identity=None,
        finish=empty,
        candidates=tuple(attempts),
        identities_enumerated=len(identities),
        one_step_hits=one_step,
        costs=costs,
    )


def intermediate_formulas(proof: HilbertProof, goal: Formula) -> tuple[Formula, ...]:
    """Proof formulas that are not the closed goal."""
    return tuple(step.formula for step in proof.steps if step.formula != goal)
