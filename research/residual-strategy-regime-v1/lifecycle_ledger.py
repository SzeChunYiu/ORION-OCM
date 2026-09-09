"""A lifecycle cost ledger for a reusable cognitive object.

Two lanes arrived independently at the same decomposition of what a carried
representation costs, and neither can finish a net-benefit claim without all four
terms charged on the same population:

```text
PREPARATION    building the object                 paid once per epoch
PER_USE        consulting it                       paid once per use
OCCUPANCY      holding it                          paid per step held
INVALIDATION   detecting and absorbing a reset,    paid once per invalidation
               drift or revocation
REPLAY         checkpointing and deterministically paid once per replay
               replaying to recover
CUSTODY        binding source and output identity  paid once per custody event
```

This module first carried FOUR terms, on the strength of two lanes reaching the
same decomposition independently.  That was wrong, and gate readiness item 6 of
`GENERAL_NET_BENEFIT_GATE_V1.md` is what refuted it: its complete cost vector
names checkpoint/replay and source/output custody, and neither is a build, a use,
a step held or an invalidation.  Two lanes agreeing is weaker evidence than one
document enumerating, and the correction is recorded here rather than smoothed
over.  ``test_the_ledger_can_hold_every_cost_the_gate_requires`` reads that list
out of the gate document at test time, so the next cost added there fails a test
until this ledger can hold it.

The failure this module exists to prevent is not arithmetic.  It is a term that
is *absent* rather than wrong, because an absent term has no error bar and does
not announce itself.  Every real correction in the cognitive-ladder lane came
from billing something previously free -- rule use in DEV-2, deliberation in X1,
the scan in DEV-6, the compiled table's storage in X7 -- and each time the SIGN
of a published comparison moved, not merely its magnitude.

So this ledger makes an uncharged term a first-class value with a reason
attached, and enforces one rule above all others:

> **A ledger with any uncharged term may report an upper BOUND on net benefit.
> It may never report a net benefit.**

Coordinates are never collapsed inside the ledger.  Comparison is Pareto on the
repository's own `ResourceVector`, exactly as contract §19 requires.  A scalar
margin exists only against explicitly declared prices, and carries the prices it
was computed under so that it cannot be quoted away from them.

Research-only.  This module measures; it changes no policy, no lifecycle gate and
no production code, and it authorizes nothing.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from ocm.kso.resources import COORDINATES, ResourceVector

__all__ = ["TERMS", "GATE_COST_MAPPING", "Charge", "uncharged", "charged",
           "LifecycleLedger", "pareto_verdict", "scalar_margin", "break_even_uses"]

#: A ledger must carry a Charge for each; there is no default.
TERMS = ("PREPARATION", "PER_USE", "OCCUPANCY", "INVALIDATION", "REPLAY", "CUSTODY")

#: Where each cost named by GENERAL_NET_BENEFIT_GATE_V1 readiness item 6 lands.
#: Kept as data rather than prose so a test can check coverage against the gate
#: document itself instead of against a transcription of it.
GATE_COST_MAPPING: Mapping[str, str] = {
    "acquisition": "PREPARATION",
    "compilation": "PREPARATION",
    "policy use": "PER_USE",
    "solving": "PER_USE",
    "checking": "PER_USE",
    "storage": "OCCUPANCY",
    "maintenance": "OCCUPANCY",
    "invalidation": "INVALIDATION",
    "checkpoint/replay": "REPLAY",
    "source/output custody": "CUSTODY",
}

ZERO = ResourceVector()


def _scale(vector: ResourceVector, factor: int) -> ResourceVector:
    if factor < 0:
        raise ValueError("multiplicity must be non-negative")
    return ResourceVector(**{name: getattr(vector, name) * factor for name in COORDINATES})


@dataclass(frozen=True, slots=True)
class Charge:
    """One term's unit cost, or an explicit statement that it was not charged.

    ``vector`` is the cost of ONE unit of the term -- one build, one use, one step
    held, one invalidation -- and the ledger multiplies it by the matching
    multiplicity. A charge is either priced or uncharged, never both and never
    neither.
    """

    term: str
    vector: ResourceVector | None = None
    uncharged_reason: str | None = None

    def __post_init__(self) -> None:
        if self.term not in TERMS:
            raise ValueError(f"unknown ledger term: {self.term}")
        if (self.vector is None) == (self.uncharged_reason is None):
            raise ValueError(
                "a charge is either a vector or an uncharged reason, never both and "
                "never neither: an omitted term is exactly what this ledger exists to "
                "catch, so it must be stated rather than left empty")
        if self.uncharged_reason is not None and not self.uncharged_reason.strip():
            raise ValueError("an uncharged term needs a reason, not an empty string")

    @property
    def is_charged(self) -> bool:
        return self.vector is not None


def charged(term: str, vector: ResourceVector) -> Charge:
    return Charge(term=term, vector=vector)


def uncharged(term: str, reason: str) -> Charge:
    return Charge(term=term, uncharged_reason=reason)


@dataclass(frozen=True, slots=True)
class LifecycleLedger:
    """What one reusable object cost over one population, against one parent."""

    subject: str
    parent: str
    population: str
    #: what the parent paid over the SAME population; the thing to beat
    parent_cost: ResourceVector
    preparation: Charge
    per_use: Charge
    occupancy: Charge
    invalidation: Charge
    replay: Charge
    custody: Charge
    #: multiplicities observed over the population
    epochs: int = 1
    uses: int = 0
    steps_held: int = 0
    invalidations: int = 0
    replays: int = 0
    custody_events: int = 0
    #: True when the observation window ended while the object was still in use,
    #: so every total below is a floor. X8's lesson: a sweep that stops while the
    #: quantity is still moving reports a bound, and calling it a boundary is the
    #: error.
    right_censored: bool = False

    def __post_init__(self) -> None:
        for name, charge in self.charges().items():
            if charge.term != name:
                raise ValueError(f"charge in slot {name} is labelled {charge.term}")
        for name in ("epochs", "uses", "steps_held", "invalidations", "replays",
                     "custody_events"):
            if getattr(self, name) < 0:
                raise ValueError(f"multiplicity must be non-negative: {name}")
        if self.epochs < 1:
            raise ValueError("an object that was never built has no ledger")
        if self.invalidations > self.epochs - 1 + self.invalidations * 0:
            # An epoch begins at a build; invalidations end epochs. The last epoch
            # may be open, so invalidations is at most epochs, and equals epochs
            # only when the final epoch also ended.
            if self.invalidations > self.epochs:
                raise ValueError("more invalidations than epochs")

    def charges(self) -> dict[str, Charge]:
        return {"PREPARATION": self.preparation, "PER_USE": self.per_use,
                "OCCUPANCY": self.occupancy, "INVALIDATION": self.invalidation,
                "REPLAY": self.replay, "CUSTODY": self.custody}

    def multiplicities(self) -> dict[str, int]:
        return {"PREPARATION": self.epochs, "PER_USE": self.uses,
                "OCCUPANCY": self.steps_held, "INVALIDATION": self.invalidations,
                "REPLAY": self.replays, "CUSTODY": self.custody_events}

    @property
    def uncharged_terms(self) -> tuple[str, ...]:
        return tuple(name for name, charge in self.charges().items()
                     if not charge.is_charged)

    @property
    def complete(self) -> bool:
        return not self.uncharged_terms

    def term_totals(self) -> dict[str, ResourceVector | None]:
        counts = self.multiplicities()
        return {name: (_scale(charge.vector, counts[name]) if charge.is_charged else None)
                for name, charge in self.charges().items()}

    def total(self) -> ResourceVector:
        """The sum of the CHARGED terms.

        An uncharged term contributes nothing, which is precisely why a total
        computed from an incomplete ledger is a LOWER bound on cost and therefore
        an UPPER bound on benefit. Nothing here hides that; ``complete`` reports
        it and every verdict function refuses to state a benefit without it.
        """
        out = ZERO
        for vector in self.term_totals().values():
            if vector is not None:
                out = out + vector
        return out

    def identity(self) -> dict[str, Any]:
        """The sum of the parts equals the whole, coordinate by coordinate.

        Cheap, and it is the check that caught a real accounting bug in the other
        lane: work that was being charged into a channel it did not belong to.
        """
        rebuilt = {name: 0 for name in COORDINATES}
        for vector in self.term_totals().values():
            if vector is None:
                continue
            for name in COORDINATES:
                rebuilt[name] += getattr(vector, name)
        total = self.total().as_dict()
        residual = {name: total[name] - rebuilt[name] for name in COORDINATES}
        return {"residual": residual, "holds": all(v == 0 for v in residual.values())}


def pareto_verdict(ledger: LifecycleLedger) -> dict[str, Any]:
    """Compare without a price. The only comparison the core permits."""
    total = ledger.total()
    parent = ledger.parent_cost
    if total.dominates(parent):
        verdict = "OBJECT_DOMINATES_PARENT"
    elif parent.dominates(total):
        verdict = "PARENT_DOMINATES_OBJECT"
    elif total == parent:
        verdict = "IDENTICAL"
    else:
        verdict = "INCOMPARABLE_WITHOUT_A_PRICE"
    claim = "BOUND_ONLY" if not ledger.complete else "MEASURED"
    return {
        "verdict": verdict,
        "claim_strength": claim,
        "uncharged_terms": list(ledger.uncharged_terms),
        "right_censored": ledger.right_censored,
        "reading": _reading(verdict, ledger),
        "object_total": total.as_dict(),
        "parent_total": parent.as_dict(),
    }


def _reading(verdict: str, ledger: LifecycleLedger) -> str:
    if not ledger.complete:
        names = ", ".join(ledger.uncharged_terms)
        return (f"{verdict} is an UPPER BOUND on the object's advantage and not a "
                f"measurement of it, because {names} is uncharged. The uncharged term "
                "can only move the comparison against the object, so a parent win here "
                "is real and an object win here is not yet a result.")
    if ledger.right_censored:
        return (f"{verdict} over an observation window that ended while the object was "
                "still in use. Preparation is already paid and further uses can only "
                "help the object, so this is a conservative reading for the object and "
                "an optimistic one for the parent.")
    return f"{verdict} with all four terms charged over the stated population."


def scalar_margin(ledger: LifecycleLedger, prices: Mapping[str, float]) -> dict[str, Any]:
    """Parent cost minus object cost under EXPLICITLY declared coordinate prices.

    The prices travel with the number. A margin quoted without them is a different
    claim from the one this function computed, and the receipt makes substituting
    one for the other visible.
    """
    missing = [name for name in COORDINATES if name not in prices]
    if missing:
        raise ValueError(f"every coordinate needs a declared price; missing: {missing}")
    if any(prices[name] < 0 for name in COORDINATES):
        raise ValueError("a negative price would make more work look like less")

    def value(vector: ResourceVector) -> float:
        return sum(prices[name] * getattr(vector, name) for name in COORDINATES)

    object_value, parent_value = value(ledger.total()), value(ledger.parent_cost)
    margin = parent_value - object_value
    return {
        "prices": {name: prices[name] for name in COORDINATES},
        "object_value": object_value,
        "parent_value": parent_value,
        "margin": margin,
        "ratio_to_parent": (object_value / parent_value) if parent_value else None,
        "claim_strength": "BOUND_ONLY" if not ledger.complete else "MEASURED",
        "net_benefit_claimable": bool(ledger.complete and margin > 0),
        "why_not_claimable": (
            None if ledger.complete else
            "a net benefit may not be claimed from a ledger with an uncharged term; "
            f"uncharged: {', '.join(ledger.uncharged_terms)}"),
    }


def break_even_uses(ledger: LifecycleLedger, prices: Mapping[str, float]) -> dict[str, Any]:
    """How many uses the object needs before it repays what holding it costs.

    The per-use saving is the parent's cost per use minus the object's, and the
    fixed side is preparation plus occupancy plus invalidation. If the per-use
    saving is not positive there is no horizon at which the object repays, and
    that is reported as such rather than as a very large number.
    """
    if not ledger.complete:
        return {"break_even_uses": None, "claim_strength": "BOUND_ONLY",
                "why": "an uncharged term makes any horizon a floor, not a horizon"}
    if ledger.uses <= 0:
        return {"break_even_uses": None, "claim_strength": "MEASURED",
                "why": "no uses were observed, so there is no per-use rate to project"}

    def value(vector: ResourceVector) -> float:
        return sum(prices[name] * getattr(vector, name) for name in COORDINATES)

    parent_per_use = value(ledger.parent_cost) / ledger.uses
    object_per_use = value(ledger.per_use.vector)
    counts = ledger.multiplicities()
    fixed = sum(value(_scale(charge.vector, counts[name]))
                for name, charge in ledger.charges().items() if name != "PER_USE")
    saving = parent_per_use - object_per_use
    if saving <= 0:
        return {"break_even_uses": None, "claim_strength": "MEASURED",
                "parent_cost_per_use": parent_per_use, "object_cost_per_use": object_per_use,
                "fixed_cost": fixed,
                "why": ("the object costs at least as much per use as the parent, so no "
                        "reuse horizon repays it; the fixed cost is not the obstacle")}
    import math
    horizon = math.ceil(fixed / saving)
    return {"break_even_uses": horizon, "claim_strength": "MEASURED",
            "parent_cost_per_use": parent_per_use, "object_cost_per_use": object_per_use,
            "fixed_cost": fixed, "saving_per_use": saving,
            "observed_uses": ledger.uses,
            "observed_population_is_past_break_even": ledger.uses >= horizon,
            "why": ("fixed cost divided by the per-use saving, with the fixed side "
                    "already multiplied by the observed epochs, steps held and "
                    "invalidations rather than assumed to be paid once")}


def report(ledger: LifecycleLedger, prices: Mapping[str, float] | None = None
           ) -> dict[str, Any]:
    identity = ledger.identity()
    doc: dict[str, Any] = {
        "schema": "ocm.lifecycle-cost-ledger.v1",
        "terms_declared": list(TERMS),
        "gate_cost_mapping": dict(GATE_COST_MAPPING),
        "subject": ledger.subject,
        "parent": ledger.parent,
        "population": ledger.population,
        "terms": {name: ({"charged": True, "unit": charge.vector.as_dict(),
                          "multiplicity": ledger.multiplicities()[name]}
                         if charge.is_charged else
                         {"charged": False, "reason": charge.uncharged_reason,
                          "multiplicity": ledger.multiplicities()[name]})
                  for name, charge in ledger.charges().items()},
        "identity": identity,
        "complete": ledger.complete,
        "right_censored": ledger.right_censored,
        "pareto": pareto_verdict(ledger),
        "what_this_does_not_establish": (
            "A ledger over one population against one parent. It measures and does "
            "not authorize: no policy, lifecycle gate or production behaviour is "
            "changed by anything here, and a positive margin is a fact about the "
            "stated population under the stated prices, not a general claim."),
    }
    if prices is not None:
        doc["scalar"] = scalar_margin(ledger, prices)
        doc["break_even"] = break_even_uses(ledger, prices)
    if not identity["holds"]:
        doc["terminal"] = "LEDGER_IDENTITY_REFUTED"
        doc["terminal_reason"] = (
            "The sum of the term totals is not the ledger total, so some cost is "
            "being counted in a channel it does not belong to. Nothing downstream "
            "of this is interpretable.")
    elif not ledger.complete:
        doc["terminal"] = "INCOMPLETE_LEDGER_BOUND_ONLY"
        doc["terminal_reason"] = (
            "At least one of the four terms is uncharged, so this ledger can bound "
            "the object's advantage from above and cannot establish one. The "
            "uncharged terms are named with their reasons.")
    else:
        doc["terminal"] = "COMPLETE_LEDGER"
        doc["terminal_reason"] = (
            "All four terms are charged over the stated population, so the Pareto "
            "verdict is a measurement. Any scalar margin remains relative to the "
            "prices it was computed under, which travel with it.")
    return doc
