from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Callable, Iterable, List, Mapping, Optional, Sequence, Tuple

F = Fraction
ALLOWED_KINDS = ("INFO", "RECODE", "SKILL", "LAW", "MORPH")


def _fraction(value, name: str) -> F:
    if type(value) is not F:
        raise ValueError(f"{name} must be an exact Fraction")
    return value


def _budget(value, name: str) -> F:
    value = _fraction(value, name)
    if not F(0) <= value <= F(1):
        raise ValueError(f"{name} must lie in [0,1]")
    return value


def _domain(values: Sequence[F], name: str) -> Tuple[F, ...]:
    if not isinstance(values, tuple) or not values:
        raise ValueError(f"{name} must be a nonempty tuple")
    for x in values:
        _fraction(x, name)
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must not contain duplicates")
    if tuple(sorted(values)) != values:
        raise ValueError(f"{name} must be sorted")
    return values


def frac(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def set_strings(values: Iterable[F]) -> List[str]:
    return [frac(x) for x in sorted(values)]


@dataclass(frozen=True)
class TransportContract:
    name: str
    from_version: int
    to_version: int
    change_kind: str
    source_domain: Tuple[F, ...]
    target_domain: Tuple[F, ...]
    relation: Tuple[Tuple[F, F], ...]
    relation_failure_budget: F = F(0)

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be nonempty")
        if type(self.from_version) is not int or type(self.to_version) is not int:
            raise ValueError("versions must be integers")
        if self.to_version != self.from_version + 1:
            raise ValueError("V1 transport requires adjacent forward versions")
        if self.change_kind not in ALLOWED_KINDS:
            raise ValueError("unknown developmental change kind")
        _domain(self.source_domain, "source_domain")
        _domain(self.target_domain, "target_domain")
        _budget(self.relation_failure_budget, "relation_failure_budget")
        if not isinstance(self.relation, tuple) or not self.relation:
            raise ValueError("relation must be a nonempty tuple")
        if len(set(self.relation)) != len(self.relation):
            raise ValueError("relation must not contain duplicate pairs")
        src_seen = set()
        for pair in self.relation:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("relation entries must be exact pairs")
            x, y = pair
            _fraction(x, "relation source")
            _fraction(y, "relation target")
            if x not in self.source_domain:
                raise ValueError("relation source outside source domain")
            if y not in self.target_domain:
                raise ValueError("relation target outside target domain")
            src_seen.add(x)
        if src_seen != set(self.source_domain):
            raise ValueError("relation must give every source-domain point a successor")


@dataclass(frozen=True)
class ConfidenceObject:
    version: int
    domain: Tuple[F, ...]
    values: Tuple[F, ...]
    failure_budget: F
    terminal: str
    raw_evidence_count: int = 0

    def __post_init__(self):
        if type(self.version) is not int:
            raise ValueError("version must be an integer")
        _domain(self.domain, "domain")
        if not isinstance(self.values, tuple) or not self.values:
            raise ValueError("values must be a nonempty tuple")
        for x in self.values:
            _fraction(x, "confidence value")
        if tuple(sorted(set(self.values))) != self.values:
            raise ValueError("values must be sorted and unique")
        if not set(self.values).issubset(self.domain):
            raise ValueError("confidence set outside domain")
        _budget(self.failure_budget, "failure_budget")
        if type(self.raw_evidence_count) is not int or self.raw_evidence_count < 0:
            raise ValueError("raw_evidence_count must be a nonnegative integer")


def relational_image(values: Iterable[F], relation: Iterable[Tuple[F, F]]) -> Tuple[F, ...]:
    values_set = set(values)
    out = {y for x, y in relation if x in values_set}
    if not out:
        raise ValueError("relation has empty image on supplied values")
    return tuple(sorted(out))


def cumulative_failure(source_alpha: F, betas: Iterable[F]) -> F:
    total = _budget(source_alpha, "source_alpha")
    for beta in betas:
        total += _budget(beta, "beta")
    return min(F(1), total)


def beta_allocation(beta: F, t: int) -> F:
    _budget(beta, "beta")
    if type(t) is not int or t < 1:
        raise ValueError("t must be an integer >= 1")
    return beta / (t * (t + 1))


def affine_interval(lo: F, hi: F, a: F, b: F, eps: F = F(0)) -> Tuple[F, F]:
    for value, name in ((lo, "lo"), (hi, "hi"), (a, "a"), (b, "b"), (eps, "eps")):
        _fraction(value, name)
    if lo > hi:
        raise ValueError("lo must not exceed hi")
    if eps < 0:
        raise ValueError("eps must be nonnegative")
    corners = (a * lo + b - eps, a * lo + b + eps, a * hi + b - eps, a * hi + b + eps)
    return min(corners), max(corners)


def identify_boolean(obj: ConfidenceObject, truth_table: Mapping[F, bool]) -> str:
    if set(truth_table) != set(obj.domain):
        raise ValueError("truth table must cover the object's full domain exactly")
    raw = [truth_table[x] for x in obj.values]
    if any(type(value) is not bool for value in raw):
        raise ValueError("truth table values must be exact bools")
    vals = set(raw)
    if vals == {True}:
        return "IDENTIFIED_TRUE"
    if vals == {False}:
        return "IDENTIFIED_FALSE"
    return "CANNOT_IDENTIFY"


class TransportCampaign:
    def __init__(self, source_version: int, source_domain: Tuple[F, ...], source_alpha: F):
        if type(source_version) is not int:
            raise ValueError("source_version must be integer")
        _domain(source_domain, "source_domain")
        _budget(source_alpha, "source_alpha")
        self.source_version = source_version
        self.source_domain = source_domain
        self.source_alpha = source_alpha
        self._tail_version = source_version
        self._tail_domain = source_domain
        self._contracts: List[TransportContract] = []
        self._locked = False
        self._source: Optional[ConfidenceObject] = None

    @property
    def locked(self) -> bool:
        return self._locked

    def register(self, contract: TransportContract) -> None:
        if self._locked:
            raise RuntimeError("transport contracts are locked after source activation")
        if not isinstance(contract, TransportContract):
            raise ValueError("contract must be TransportContract")
        if contract.from_version != self._tail_version:
            raise ValueError("contract does not continue the registered version chain")
        if contract.source_domain != self._tail_domain:
            raise ValueError("contract source domain does not match registered tail domain")
        self._contracts.append(contract)
        self._tail_version = contract.to_version
        self._tail_domain = contract.target_domain

    def activate_source(self, values: Tuple[F, ...], raw_evidence_count: int = 0) -> ConfidenceObject:
        if self._locked:
            raise RuntimeError("source already activated")
        self._locked = True
        self._source = ConfidenceObject(
            self.source_version,
            self.source_domain,
            tuple(sorted(set(values))),
            self.source_alpha,
            "SOURCE_ACTIVE",
            raw_evidence_count,
        )
        return self._source

    def _apply(self, obj: ConfidenceObject, contract: TransportContract) -> ConfidenceObject:
        if obj.version != contract.from_version or obj.domain != contract.source_domain:
            raise ValueError("object/contract mismatch")
        image = relational_image(obj.values, contract.relation)
        failure = cumulative_failure(obj.failure_budget, (contract.relation_failure_budget,))
        return ConfidenceObject(
            contract.to_version,
            contract.target_domain,
            image,
            failure,
            "TRANSPORTED",
            0,
        )

    def propagate_all(self) -> Tuple[ConfidenceObject, ...]:
        if self._source is None:
            raise RuntimeError("activate source before propagation")
        states = [self._source]
        current = self._source
        for contract in self._contracts:
            current = self._apply(current, contract)
            states.append(current)
        return tuple(states)

    def propagate_unknown(self, obj: ConfidenceObject, target_version: int, target_domain: Tuple[F, ...]) -> ConfidenceObject:
        if self._source is None:
            raise RuntimeError("activate source before unknown-relation propagation")
        registered_tail = self.propagate_all()[-1]
        if obj != registered_tail:
            raise ValueError("unknown transport must start from the campaign's registered chain tail")
        if type(target_version) is not int or target_version != obj.version + 1:
            raise ValueError("unknown transport still requires adjacent target version")
        _domain(target_domain, "target_domain")
        return ConfidenceObject(
            target_version,
            target_domain,
            target_domain,
            obj.failure_budget,
            "CANNOT_IDENTIFY_NO_RELATION",
            0,
        )


def relation_from_function(source_domain: Tuple[F, ...], fn: Callable[[F], F]) -> Tuple[Tuple[F, F], ...]:
    _domain(source_domain, "source_domain")
    pairs = []
    for x in source_domain:
        y = fn(x)
        _fraction(y, "function output")
        pairs.append((x, y))
    return tuple(pairs)


def relation_from_successors(source_domain: Tuple[F, ...], fn: Callable[[F], Iterable[F]]) -> Tuple[Tuple[F, F], ...]:
    _domain(source_domain, "source_domain")
    pairs = []
    for x in source_domain:
        ys = tuple(fn(x))
        if not ys:
            raise ValueError("successor function returned no targets")
        for y in ys:
            _fraction(y, "successor")
            pairs.append((x, y))
    return tuple(sorted(set(pairs)))


def _five_kind_contracts() -> Tuple[TransportContract, ...]:
    x0 = tuple(F(i) for i in range(-2, 3))
    x1 = tuple(F(i) for i in range(-1, 4))
    x2 = x1
    x3 = tuple(F(i) for i in range(-1, 5))
    x4 = tuple(F(i) for i in range(-2, 6))
    x5 = tuple(F(i) for i in (0, 1, 4, 9, 16, 25))
    return (
        TransportContract("info", 0, 1, "INFO", x0, x1, relation_from_function(x0, lambda x: x + 1)),
        TransportContract("recode", 1, 2, "RECODE", x1, x2, relation_from_function(x1, lambda x: x)),
        TransportContract("skill", 2, 3, "SKILL", x2, x3, relation_from_successors(x2, lambda x: (x, x + 1))),
        TransportContract("law", 3, 4, "LAW", x3, x4, relation_from_successors(x3, lambda x: (x - 1, x, x + 1))),
        TransportContract("morph", 4, 5, "MORPH", x4, x5, relation_from_function(x4, lambda x: x * x)),
    )


def build_receipt() -> Mapping[str, object]:
    alpha = F(1, 20)
    contracts = _five_kind_contracts()
    campaign = TransportCampaign(0, contracts[0].source_domain, alpha)
    for c in contracts:
        campaign.register(c)
    source = campaign.activate_source((F(-1), F(0), F(1)), raw_evidence_count=2048)
    chain = campaign.propagate_all()

    post_activation_blocked = False
    try:
        campaign.register(contracts[-1])
    except RuntimeError:
        post_activation_blocked = True

    unknown_domain = (F(0), F(1), F(2))
    unknown = campaign.propagate_unknown(chain[-1], 6, unknown_domain)
    mixed_query = {F(0): False, F(1): True, F(2): True}
    constant_query = {F(0): True, F(1): True, F(2): True}

    nonlinear_domain = tuple(F(i) for i in (-1, 0, 1, 2))
    nonlinear_relation = relation_from_successors((F(-1), F(0), F(1)), lambda x: (x*x - 1, x*x, x*x + 1))
    nonlinear = relational_image((F(-1), F(0), F(1)), nonlinear_relation)

    interval = affine_interval(F(1,4), F(3,4), F(-2), F(3), F(1,10))

    uncertain_failure = cumulative_failure(alpha, (F(1,100), F(1,200)))
    beta = F(1,20)
    allocation = {}
    for n in (1, 2, 5, 1000):
        partial = sum((beta_allocation(beta, t) for t in range(1, n+1)), F(0))
        allocation[str(n)] = {
            "partial": frac(partial),
            "closed_form": frac(beta * F(n, n+1)),
            "strictly_below_beta": partial < beta,
        }

    copy_counterexample = {
        "source_truth": "0",
        "source_set": ["0"],
        "target_truth": "1",
        "copied_set": ["0"],
        "copy_covers": False,
        "full_target_domain": ["0", "1"],
        "full_domain_covers": True,
    }

    return {
        "schema": "DevelopmentalUncertaintyTransportReceiptV1",
        "issue": 748,
        "parent_issue": 602,
        "freeze_commit": "041bb8950ebeed94b8b258e7ad23258df19eec1c",
        "claim_ceiling": "SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE",
        "five_kind_chain": [
            {
                "version": obj.version,
                "values": set_strings(obj.values),
                "failure_budget": frac(obj.failure_budget),
                "raw_evidence_count": obj.raw_evidence_count,
                "terminal": obj.terminal,
            }
            for obj in chain
        ],
        "five_kinds": [c.change_kind for c in contracts],
        "post_activation_registration_blocked": post_activation_blocked,
        "unknown_relation": {
            "values": set_strings(unknown.values),
            "terminal": unknown.terminal,
            "mixed_query": identify_boolean(unknown, mixed_query),
            "constant_query": identify_boolean(unknown, constant_query),
            "raw_evidence_count": unknown.raw_evidence_count,
        },
        "copy_counterexample": copy_counterexample,
        "interval_affine": {
            "result": [frac(interval[0]), frac(interval[1])],
            "expected": ["7/5", "13/5"],
        },
        "nonlinear_relation": {
            "result": set_strings(nonlinear),
            "expected": ["-1", "0", "1", "2"],
            "target_domain": set_strings(nonlinear_domain),
        },
        "uncertain_relation_budget": {
            "alpha": "1/20",
            "betas": ["1/100", "1/200"],
            "failure_budget": frac(uncertain_failure),
            "coverage_lower_bound": frac(F(1) - uncertain_failure),
        },
        "countable_allocation": {
            "beta": "1/20",
            "partials": allocation,
            "infinite_horizon_combined_lower_bound": frac(F(1) - alpha - beta),
        },
        "no_independence_assumption": True,
        "target_evidence_noninheritance": all(obj.raw_evidence_count == 0 for obj in chain[1:]),
        "source_raw_evidence_count": source.raw_evidence_count,
    }


def main() -> int:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
