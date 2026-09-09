"""FNA-4: library/synthesis learner parent suite for #62 (experience consolidation).

#214 work package FNA-4. The #62 question: does solved+failed experience consolidate into
persistent governed structure that makes FUTURE composition cheaper,

    C_future(T_j | E_t) < C_future(T_j | E_0)

on main's own composition discipline. Operator selection goes through the PRODUCTION
``runtime/operator_index.SolveOperatorIndex`` (rarest-input inverted index); macros carry
``kso/warrant.WarrantProfile`` evidence bridged by meet (the KS-T20 rule compose_stage
applies); macro admission content-hashes its skeleton.

Cost model (FNA4_PROTOCOL.md): ONE commensurable integer unit per backend simulation,
checker call, posting read, or learner work step. A macro never makes execution free --
applying it charges one simulation per primitive step inside it. What a library saves is
SEARCH: deadend expansions, posting reads and checker calls on candidates the solved family
structure would never have tried.

No neural arm exists here (FNA4_SOURCE_LEDGER.json: the parents are Soar chunking,
Reynolds anti-unification, Stitch top-down usefulness search, e-graph saturation, misfire
nogoods, CEGIS specialization). Research-only; no production source modified.
Python 3.8-compatible syntax.
"""
from __future__ import annotations

import hashlib
import itertools
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for p in (str(HERE), str(REPO / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ocm.runtime.operator_index import SolveOperatorIndex  # noqa: E402
from ocm.runtime.solve import OperatorSpec  # noqa: E402
from ocm.kso.warrant import WarrantProfile, meet_all_profiles  # noqa: E402

SCHEMA = "ocm.fna.fna4-library-synthesis.v1"
FORBIDDEN_CLAIMS = ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT", "NEURAL_SUPERIOR",
                    "NEURAL_NECESSARY", "GENERAL_SUPERIORITY", "AGI")
DOMAIN_CAP = 24          # hole-domain enumeration cap; every enumeration step is charged


class Misfire(Exception):
    """A structurally applicable operator whose execution fails on this input."""


def _h(data) -> str:
    return hashlib.sha256(repr(data).encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# frozen data algebra (FNA4_PROTOCOL.md "Frozen world")
# tokens = tuple of records; record = (f0, f1, f2) small ints; scalars are Fractions.
# ---------------------------------------------------------------------------


def _records(rng, n, dup):
    recs = [tuple(rng.randint(0, 5) for _ in range(3)) for _ in range(n)]
    if dup:
        recs += recs[:dup]
    return tuple(recs)


def _csv(recs):
    return ("csv", tuple(recs))


def _jsonl(recs):
    return ("jsonl", tuple(recs))


def _prim_parse(params, data):
    # params = ("parse", surface); data = (surface_tag, records)
    if data[0] != params[1]:
        raise Misfire("parse:%s on raw:%s" % (params[1], data[0]))
    return data[1]


def _prim_filter(params, recs):
    # params = ("filter", "eq", "fK"); value = first record's field (deterministic)
    k = int(params[2][1:])
    v = recs[0][k]
    return tuple(r for r in recs if r[k] == v)


def _prim_sort(params, recs):
    # params = ("sort", "asc"|"desc", "fK")
    k = int(params[2][1:])
    if params[1] == "desc":
        return tuple(sorted(recs, key=lambda r: r[k], reverse=True))
    return tuple(sorted(recs, key=lambda r: (r[k], r)))


def _prim_dedupe(_params, recs):
    return tuple(dict.fromkeys(recs))


def _prim_merge(_params, two):
    return tuple(two[0]) + tuple(two[1])


def _prim_agg(params, recs):
    # params = ("agg", "sum"|"mean"|"count", "fK"?) ; agg:count has no field slot
    if params[1] == "count":
        return Fraction(len(recs))
    k = int(params[2][1:])
    s = sum(r[k] for r in recs)
    return Fraction(s) if params[1] == "sum" else Fraction(s, len(recs))


def _prim_scale(params, val):
    # params = ("scale", "2"|"3")
    return val * int(params[1])


def _prim_zip(_params, recs):
    return Fraction(sum(1 for r in recs if r[0] <= r[1]))


#: name -> (ins types, out type, behaviour). family = name before the first ':'.
PRIMITIVES = {
    "parse:csv": (("raw",), "tokens", _prim_parse),
    "parse:jsonl": (("raw",), "tokens", _prim_parse),
    "filter:eq:f0": (("tokens",), "tokens", _prim_filter),
    "filter:eq:f1": (("tokens",), "tokens", _prim_filter),
    "filter:eq:f2": (("tokens",), "tokens", _prim_filter),
    "sort:asc:f0": (("tokens",), "tokens", _prim_sort),
    "sort:asc:f1": (("tokens",), "tokens", _prim_sort),
    "sort:asc:f2": (("tokens",), "tokens", _prim_sort),
    "sort:desc:f0": (("tokens",), "tokens", _prim_sort),
    "sort:desc:f1": (("tokens",), "tokens", _prim_sort),
    "sort:desc:f2": (("tokens",), "tokens", _prim_sort),
    "dedupe:stable": (("tokens",), "tokens", _prim_dedupe),
    "merge:2": (("tokens", "tokens"), "tokens", _prim_merge),
    "agg:sum:f0": (("tokens",), "scalar", _prim_agg),
    "agg:sum:f1": (("tokens",), "scalar", _prim_agg),
    "agg:sum:f2": (("tokens",), "scalar", _prim_agg),
    "agg:mean:f0": (("tokens",), "scalar", _prim_agg),
    "agg:mean:f1": (("tokens",), "scalar", _prim_agg),
    "agg:mean:f2": (("tokens",), "scalar", _prim_agg),
    "agg:count": (("tokens",), "scalar", _prim_agg),
    "scale:2": (("scalar",), "scalar", _prim_scale),
    "scale:3": (("scalar",), "scalar", _prim_scale),
    "zip:count": (("tokens",), "scalar", _prim_zip),
}

CATALOGUE = tuple(sorted(PRIMITIVES))


def family_of(name):
    return name.split(":")[0]


def name_params(name):
    return tuple(name.split(":"))


def simulate(name, args):
    """One backend simulation. The caller charges exactly one unit."""
    _ins, _out, fn = PRIMITIVES[name]
    return fn(name_params(name), args[0] if len(args) == 1 else args)


# ---------------------------------------------------------------------------
# tasks (frozen families; fresh tasks = new payloads + new parameter draws)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Task:
    task_id: str
    family: str            # F1 | F2 | F3
    initial: tuple         # tuple of (type, surface, data)
    goal: Fraction
    true_chain: tuple      # ground truth, receipts only; never shown to any arm


def run_chain(chain, initial):
    """Deterministic chain interpreter: each step consumes the most recent atoms of its
    input types from the tape and appends its output (composition semantics)."""
    tape = [(t, d) for (t, _s, d) in initial]
    for name in chain:
        ins, out, _fn = PRIMITIVES[name]
        args = []
        for t in ins:
            pick = max(i for i, (tt, _d) in enumerate(tape) if tt == t)
            args.append(tape.pop(pick)[1])
        tape.append((out, simulate(name, args)))
    return tape[-1][1]


def gen_task(rng, family, uid, force=None):
    """Deterministic given (rng, family, uid). Acquisition and test draws are disjoint.
    ``force`` overrides drawn parameters (stream construction for the repeat-rate sweep;
    it never touches payloads, which stay salt-drawn and fresh)."""
    force = force or {}
    fmts = ("csv", "jsonl")
    if family == "F1":
        fmt = force.get("fmt", rng.choice(fmts))
        fk = force.get("fk", rng.choice(("f0", "f1", "f2")))
        sd = force.get("sd", rng.choice(("asc", "desc")))
        sk = force.get("sk", rng.choice(("f0", "f1", "f2")))
        af = force.get("af", rng.choice(("sum", "mean", "count")))
        ak = force.get("ak", rng.choice(("f0", "f1", "f2")))
        k = force.get("k", rng.choice(("2", "3")))
        recs = _records(rng, 8, 0)
        chain = ("parse:" + fmt, "filter:eq:" + fk, "sort:" + sd + ":" + sk,
                 "agg:count" if af == "count" else "agg:%s:%s" % (af, ak), "scale:" + k)
        raw = _csv(recs) if fmt == "csv" else _jsonl(recs)
        initial = (("raw", fmt, raw),)
    elif family == "F2":
        pair = force.get("fmt_pair", rng.sample(fmts, 2))
        fmt_a, fmt_b = pair[0], pair[1]
        af = force.get("af", rng.choice(("sum", "mean")))
        ak = force.get("ak", rng.choice(("f0", "f1", "f2")))
        ra, rb = _records(rng, 6, 2), _records(rng, 6, 2)
        # Tape semantics consume the most recent atom of each type, so the first
        # parse step reads the SECOND raw atom: chain order mirrors initial order.
        chain = ("parse:" + fmt_b, "parse:" + fmt_a, "merge:2", "dedupe:stable",
                 "agg:%s:%s" % (af, ak))
        wrap = _csv if fmt_a == "csv" else _jsonl
        wrapb = _csv if fmt_b == "csv" else _jsonl
        initial = (("raw", fmt_a, wrap(ra)), ("raw", fmt_b, wrapb(rb)))
    elif family == "F3":
        fmt = force.get("fmt", rng.choice(fmts))
        k = force.get("k", rng.choice(("2", "3")))
        recs = _records(rng, 10, 0)
        chain = ("parse:" + fmt, "zip:count", "scale:" + k)
        raw = _csv(recs) if fmt == "csv" else _jsonl(recs)
        initial = (("raw", fmt, raw),)
    else:
        raise ValueError(family)
    return Task(uid, family, initial, run_chain(chain, initial), chain)


# ---------------------------------------------------------------------------
# production operator index over the catalogue (type level) + work counters
# ---------------------------------------------------------------------------


def _opspec(name):
    ins, out, _fn = PRIMITIVES[name]
    return OperatorSpec(operator_id=name, version="fna4-v1",
                        backend=lambda ks, oid, ctx: {}, input_atoms=ins, output_type=out)


INDEX = SolveOperatorIndex([_opspec(n) for n in CATALOGUE])

#: family-level registration evidence: revoking ev:fam:<family> kills that family's
#: primitives and exactly the macros whose skeleton contains it.
FAMILY_WARRANT = {f: WarrantProfile.certified([frozenset(["ev:fam:" + f])])
                  for f in sorted({family_of(n) for n in CATALOGUE})}

PRIM_WARRANT = {n: FAMILY_WARRANT[family_of(n)] for n in CATALOGUE}


def atom_id(typ, data):
    return typ + ":" + _h(data)


class Work(object):
    """One commensurable unit per simulation / checker call / posting read / learner step."""

    def __init__(self):
        self.simulations = 0
        self.checker_calls = 0
        self.posting_reads = 0
        self.learner_steps = 0

    def sim(self, n=1):
        self.simulations += n

    def check(self, n=1):
        self.checker_calls += n

    def post(self, n):
        self.posting_reads += n

    def learn(self, n=1):
        self.learner_steps += n

    def total(self):
        return self.simulations + self.checker_calls + self.posting_reads + self.learner_steps

    def as_dict(self):
        return {"simulations": self.simulations, "checker_calls": self.checker_calls,
                "posting_reads": self.posting_reads, "learner_steps": self.learner_steps,
                "total_units": self.total()}


# ---------------------------------------------------------------------------
# macros: learned composition templates over the frozen algebra
# ---------------------------------------------------------------------------


def make_macro(skeleton, instances, label="LEARNED"):
    """skeleton: tuple of (family, slots); slots[i] is None (hole) or a constant.
    Hole domains are the observed values across `instances` (traces the pattern matched).
    Warrant = meet of the families' registration evidence (KS-T20 bridge rule)."""
    domains = []
    for pos, (_fam, slots) in enumerate(skeleton):
        for i, s in enumerate(slots):
            if s is None:
                dom = sorted({inst[pos][1][i] for inst in instances})
                domains.append(tuple(dom))
    warr = meet_all_profiles([FAMILY_WARRANT[f] for f, _s in skeleton]) if skeleton \
        else WarrantProfile.one()
    mid = hashlib.sha256(repr((skeleton, label)).encode("utf-8")).hexdigest()[:16]
    return Macro(mid, skeleton, tuple(domains), warr, label)


@dataclass
class Macro:
    macro_id: str
    skeleton: tuple
    domains: tuple
    warrant: WarrantProfile
    label: str = "LEARNED"

    def body_names(self, assignment):
        """Instantiate the skeleton with a flat assignment (hole order: step-major)."""
        out, h = [], 0
        for fam, slots in self.skeleton:
            params = []
            for s in slots:
                if s is None:
                    params.append(str(assignment[h]))
                    h += 1
                else:
                    params.append(str(s))
            out.append(":".join([fam] + params))
        return tuple(out)

    def families(self):
        return tuple(f for f, _s in self.skeleton)

    def in_types(self):
        """Input types of a family are constant across its parameterizations here."""
        first = self.skeleton[0][0]
        sample = next(n for n in CATALOGUE if family_of(n) == first)
        return PRIMITIVES[sample][0]

    def out_type(self):
        last = self.skeleton[-1][0]
        sample = next(n for n in CATALOGUE if family_of(n) == last)
        return PRIMITIVES[sample][1]

    def assignments(self):
        return list(itertools.islice(itertools.product(*self.domains), DOMAIN_CAP)) \
            if self.domains else [()]

    def size(self):
        return len(self.skeleton)

    def as_dict(self):
        return {"macro_id": self.macro_id, "label": self.label,
                "skeleton": [[f, list(s)] for f, s in self.skeleton],
                "domains": [list(d) for d in self.domains],
                "warrant": self.warrant.as_dict()}
