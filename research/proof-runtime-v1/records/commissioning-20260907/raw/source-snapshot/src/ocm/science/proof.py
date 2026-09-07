"""Proof-kernel boundary (M10 §10): candidate theorem/proof → formalisation identity → kernel →
PASS(certificate) | FAIL | CANNOT_CHECK → a warranted proof object only on PASS.

Two warrants are kept apart: the *kernel* warrant (the formal statement is proved) and the
*formalisation correspondence* warrant (the formal statement faithfully captures the informal
claim) — a proof never certifies the correspondence.  Kernels are registered: `propositional`
(an exact stdlib truth-table kernel for finite propositional statements, complete for that
fragment) and `lean4` (CANNOT_CHECK here: no Lean toolchain in this study; the interface is the
contract the real kernel plugs into).  Hostiles: a mistranslated formal statement accepted as the
informal claim (correspondence dropped); a FAIL read as "the theorem is false".
"""
from __future__ import annotations

import hashlib
import itertools
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping

from ocm.kso.warrant import WarrantProfile


class KernelVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class FormalStatement:
    statement_id: str
    kernel: str                                  # registered kernel id
    text: str                                    # formal text
    informal: str                                # the informal claim it is meant to capture
    correspondence_evidence: tuple[str, ...]     # evidence that the formalisation is faithful (review, tests)

    @property
    def identity(self) -> str:
        return hashlib.sha256(f"{self.kernel}|{self.text}".encode()).hexdigest()[:16]


@dataclass(frozen=True)
class ProofCertificate:
    statement_identity: str
    kernel: str
    verdict: KernelVerdict
    detail: str
    kernel_warrant: WarrantProfile               # evidence: the kernel run id
    correspondence_warrant: WarrantProfile       # evidence: the correspondence review (separate)

    def proof_object_warrant(self) -> WarrantProfile | None:
        """A warranted proof object exists only on PASS: kernel ⊗ (correspondence is *separate* and
        reported beside it, never merged into the kernel verdict)."""
        return self.kernel_warrant if self.verdict is KernelVerdict.PASS else None


# ------------------------------------------------------------------ propositional kernel (exact)
_TOKEN = re.compile(r"\s*(<->|->|[A-Za-z_][A-Za-z0-9_]*|[()~&|]|\S)")


def _parse(text: str):
    toks = [t for t in _TOKEN.findall(text) if t.strip()]
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def take():
        nonlocal pos
        t = toks[pos]
        pos += 1
        return t

    def atom():
        t = take()
        if t == "(":
            e = iff()
            if take() != ")":
                raise ValueError("expected )")
            return e
        if t == "~":
            e = atom()
            return ("not", e)
        if re.match(r"[A-Za-z_]", t):
            return ("var", t)
        raise ValueError(f"unexpected {t}")

    def conj():
        e = atom()
        while peek() == "&":
            take()
            e = ("and", e, atom())
        return e

    def disj():
        e = conj()
        while peek() == "|":
            take()
            e = ("or", e, conj())
        return e

    def impl():
        e = disj()
        if peek() == "->":
            take()
            return ("imp", e, impl())
        return e

    def iff():
        e = impl()
        while peek() == "<->":
            take()
            e = ("iff", e, impl())
        return e

    e = iff()
    if pos != len(toks):
        raise ValueError("trailing tokens")
    return e


def _eval(e, env):
    k = e[0]
    if k == "var":
        return env[e[1]]
    if k == "not":
        return not _eval(e[1], env)
    a, b = _eval(e[1], env), _eval(e[2], env)
    return {"and": a and b, "or": a or b, "imp": (not a) or b, "iff": a == b}[k]


def _vars(e, acc):
    if e[0] == "var":
        acc.add(e[1])
    else:
        for sub in e[1:]:
            _vars(sub, acc)
    return acc


def propositional_kernel(text: str) -> tuple[KernelVerdict, str]:
    """Exact: tautology check by full truth table (complete for the propositional fragment)."""
    try:
        e = _parse(text)
    except Exception as exc:  # noqa: BLE001
        return KernelVerdict.CANNOT_CHECK, f"parse error: {exc}"
    vs = sorted(_vars(e, set()))
    if len(vs) > 16:
        return KernelVerdict.CANNOT_CHECK, "too many variables for the exact kernel"
    for bits in itertools.product([False, True], repeat=len(vs)):
        if not _eval(e, dict(zip(vs, bits))):
            return KernelVerdict.FAIL, f"countermodel {dict(zip(vs, bits))}"
    return KernelVerdict.PASS, f"tautology over {len(vs)} variables ({2 ** len(vs)} rows)"


KERNELS: dict[str, Callable[[str], tuple[KernelVerdict, str]]] = {"propositional": propositional_kernel}


def check(statement: FormalStatement, *, run_id: str) -> ProofCertificate:
    kern = KERNELS.get(statement.kernel)
    if kern is None:
        return ProofCertificate(statement.identity, statement.kernel, KernelVerdict.CANNOT_CHECK, f"kernel {statement.kernel} not available in this study", WarrantProfile.zero(), WarrantProfile.of(set(statement.correspondence_evidence)) if statement.correspondence_evidence else WarrantProfile.zero())
    v, detail = kern(statement.text)
    kw = WarrantProfile.of({run_id}) if v is KernelVerdict.PASS else WarrantProfile.zero()
    cw = WarrantProfile.of(set(statement.correspondence_evidence)) if statement.correspondence_evidence else WarrantProfile.zero()
    return ProofCertificate(statement.identity, statement.kernel, v, detail, kw, cw)


def theorem_false_from_fail(cert: ProofCertificate) -> bool:
    """A FAIL of a proof attempt is never evidence that the statement is false (only a countermodel
    from a complete kernel is) — the propositional kernel's FAIL carries a countermodel, a
    non-complete kernel's FAIL does not."""
    return cert.verdict is KernelVerdict.FAIL and cert.kernel == "propositional" and cert.detail.startswith("countermodel")


def mutant_fail_means_false(cert: ProofCertificate) -> bool:
    """Planted (M10 §17): failed proof treated as evidence the theorem is false."""
    return cert.verdict is KernelVerdict.FAIL


def mutant_accept_mistranslation(cert: ProofCertificate) -> WarrantProfile | None:
    """Planted (M10 §17): the proof object's warrant used as if it covered the informal claim
    (correspondence merged into the kernel verdict)."""
    return cert.kernel_warrant if cert.verdict is KernelVerdict.PASS else None
