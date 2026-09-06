"""Small, explicit native proof search for the preregistered R1 propositional gate.

This is intentionally not an FLT-specific tactic. It is a generic implicational proof-term
constructor using three inspectable operations: INTRO, ASSUMPTION and APPLY_LOCAL.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable

from flt_contract import R1_MAX_EXPANSIONS


@dataclass(frozen=True, slots=True)
class TyVar:
    name: str


@dataclass(frozen=True, slots=True)
class Arrow:
    left: "TypeExpr"
    right: "TypeExpr"


TypeExpr = TyVar | Arrow


@dataclass(frozen=True, slots=True)
class Var:
    name: str


@dataclass(frozen=True, slots=True)
class Lam:
    name: str
    body: "Term"


@dataclass(frozen=True, slots=True)
class App:
    fn: "Term"
    arg: "Term"


Term = Var | Lam | App


class BudgetExhausted(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Event:
    index: int
    operator_id: str
    input_state_id: str
    dependency: str | None
    resource_cost: int
    outcome: str
    resulting_state_ids: tuple[str, ...] = ()
    failure_class: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "operator_id": self.operator_id,
            "input_state_id": self.input_state_id,
            "dependency": self.dependency,
            "resource_cost": self.resource_cost,
            "outcome": self.outcome,
            "resulting_state_ids": list(self.resulting_state_ids),
            "failure_class": self.failure_class,
        }


@dataclass(frozen=True, slots=True)
class SearchResult:
    term: Term | None
    events: tuple[Event, ...]
    expansions: int
    unique_states: int
    duplicate_states_avoided: int
    operator_candidates_considered: int
    terminal: str


Context = tuple[tuple[str, TypeExpr], ...]


def render_type(t: TypeExpr, *, nested: bool = False) -> str:
    if isinstance(t, TyVar):
        return t.name
    left = render_type(t.left, nested=True)
    right = render_type(t.right)
    body = f"{left} → {right}"
    return f"({body})" if nested else body


def render_term(t: Term) -> str:
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Lam):
        names: list[str] = []
        body: Term = t
        while isinstance(body, Lam):
            names.append(body.name)
            body = body.body
        return f"fun {' '.join(names)} => {render_term(body)}"
    fn = render_term(t.fn)
    arg = render_term(t.arg)
    if isinstance(t.fn, Lam):
        fn = f"({fn})"
    if isinstance(t.arg, (Lam, App)):
        arg = f"({arg})"
    return f"{fn} {arg}"


def _type_key(t: TypeExpr) -> object:
    return t.name if isinstance(t, TyVar) else ["→", _type_key(t.left), _type_key(t.right)]


def _state_id(ctx: Context, goal: TypeExpr) -> str:
    payload = {"ctx": [[name, _type_key(t)] for name, t in ctx], "goal": _type_key(goal)}
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()[:20]


def _args_to_result(t: TypeExpr, result: TypeExpr) -> tuple[TypeExpr, ...] | None:
    args: list[TypeExpr] = []
    cursor = t
    while isinstance(cursor, Arrow):
        args.append(cursor.left)
        cursor = cursor.right
    return tuple(args) if cursor == result and args else None


def search(goal: TypeExpr, *, max_expansions: int = R1_MAX_EXPANSIONS) -> SearchResult:
    events: list[Event] = []
    expanded: set[str] = set()
    active: set[str] = set()
    duplicate_states = 0
    considered = 0
    expansion_count = 0
    fresh = 0

    def event(op: str, sid: str, dep: str | None, outcome: str, children: Iterable[str] = (), failure: str | None = None) -> None:
        events.append(Event(len(events), op, sid, dep, 1, outcome, tuple(children), failure))

    def prove(ctx: Context, target: TypeExpr) -> Term | None:
        nonlocal duplicate_states, considered, expansion_count, fresh
        sid = _state_id(ctx, target)
        if sid in active:
            duplicate_states += 1
            event("proof.deduplicate", sid, None, "SKIP", failure="ACTIVE_STATE_CYCLE")
            return None
        if sid in expanded:
            duplicate_states += 1
            event("proof.deduplicate", sid, None, "SKIP", failure="STATE_ALREADY_FAILED")
            return None
        if expansion_count >= max_expansions:
            raise BudgetExhausted(f"expanded {expansion_count} states (budget={max_expansions})")
        expansion_count += 1
        active.add(sid)

        for name, typ in ctx:
            considered += 1
            if typ == target:
                event("proof.assumption", sid, name, "CLOSED")
                active.remove(sid)
                return Var(name)
            event("proof.assumption", sid, name, "REJECTED", failure="TYPE_MISMATCH")

        considered += 1
        if isinstance(target, Arrow):
            name = f"h{fresh}"
            fresh += 1
            child_ctx = (*ctx, (name, target.left))
            child_sid = _state_id(child_ctx, target.right)
            event("proof.intro", sid, None, "EXPANDED", (child_sid,))
            body = prove(child_ctx, target.right)
            if body is not None:
                active.remove(sid)
                return Lam(name, body)
            event("proof.intro", sid, None, "FAILED", (child_sid,), "SUBGOAL_UNCLOSED")
        else:
            event("proof.intro", sid, None, "REJECTED", failure="GOAL_NOT_IMPLICATION")

        for name, typ in ctx:
            considered += 1
            args = _args_to_result(typ, target)
            if args is None:
                event("proof.apply_local", sid, name, "REJECTED", failure="RESULT_TYPE_MISMATCH")
                continue
            child_ids = tuple(_state_id(ctx, a) for a in args)
            event("proof.apply_local", sid, name, "EXPANDED", child_ids)
            term: Term = Var(name)
            ok = True
            for a in args:
                subterm = prove(ctx, a)
                if subterm is None:
                    ok = False
                    break
                term = App(term, subterm)
            if ok:
                active.remove(sid)
                return term
            event("proof.apply_local", sid, name, "FAILED", child_ids, "ARGUMENT_SUBGOAL_UNCLOSED")

        active.remove(sid)
        expanded.add(sid)
        return None

    try:
        term = prove((), goal)
        terminal = "CANDIDATE_CONSTRUCTED" if term is not None else "NO_PROOF_FOUND_UNDER_GRAMMAR"
    except BudgetExhausted:
        term = None
        terminal = "FAILED_UNDER_BUDGET"
    unique = len(expanded | active)
    event_state_ids = {e.input_state_id for e in events if e.operator_id != "proof.deduplicate"}
    unique = max(unique, len(event_state_ids))
    return SearchResult(term, tuple(events), expansion_count, unique, duplicate_states, considered, terminal)


def r1_goal() -> TypeExpr:
    p, q, r = TyVar("P"), TyVar("Q"), TyVar("R")
    return Arrow(Arrow(p, q), Arrow(Arrow(q, r), Arrow(p, r)))


def solve_r1(*, max_expansions: int = R1_MAX_EXPANSIONS) -> SearchResult:
    return search(r1_goal(), max_expansions=max_expansions)


def emit_r1_lean(term: Term) -> str:
    return "\n".join([
        "set_option autoImplicit false",
        "",
        "theorem r1_prop_chain_001 (P Q R : Prop) :",
        "    (P → Q) → (Q → R) → P → R :=",
        f"  {render_term(term)}",
        "",
        "#print axioms r1_prop_chain_001",
        "",
    ])


def r1_backend_output(*, max_expansions: int = R1_MAX_EXPANSIONS) -> dict[str, object]:
    result = solve_r1(max_expansions=max_expansions)
    output: dict[str, object] = {
        "search_terminal": result.terminal,
        "proof_state_expansions": result.expansions,
        "unique_proof_states": result.unique_states,
        "duplicate_states_avoided": result.duplicate_states_avoided,
        "operator_candidates_considered": result.operator_candidates_considered,
        "search_events": [event.as_dict() for event in result.events],
    }
    if result.term is not None:
        output["proof_term"] = render_term(result.term)
        output["proof_source"] = emit_r1_lean(result.term)
    return output
