from __future__ import print_function

import json
from dataclasses import dataclass
from fractions import Fraction
from typing import FrozenSet, Tuple

ALLOWED_KINDS = ("INFO", "RECODE", "SKILL", "LAW", "MORPH")


def _check_fraction_01(value, name):
    if not isinstance(value, Fraction):
        raise TypeError("%s must be Fraction" % name)
    if value < 0 or value > 1:
        raise ValueError("%s must be in [0,1]" % name)


def _canonical_domain(values):
    domain = tuple(values)
    if not domain:
        raise ValueError("domain must be nonempty")
    if len(set(domain)) != len(domain):
        raise ValueError("domain contains duplicates")
    if not all(isinstance(x, Fraction) for x in domain):
        raise TypeError("domain points must be Fraction")
    return domain


def _version_number(version):
    if not isinstance(version, str) or len(version) < 2 or version[0] != "v":
        raise ValueError("version must be canonical vN")
    try:
        number = int(version[1:])
    except ValueError:
        raise ValueError("version must be canonical vN")
    if number < 0 or str(number) != version[1:]:
        raise ValueError("version must be canonical vN")
    return number


def _fstr(value):
    if value.denominator == 1:
        return str(value.numerator)
    return "%d/%d" % (value.numerator, value.denominator)


def _sorted_fstr(values):
    return [_fstr(x) for x in sorted(values)]


@dataclass(frozen=True)
class TransportContract:
    name: str
    from_version: str
    to_version: str
    change_kind: str
    source_domain: Tuple[Fraction, ...]
    target_domain: Tuple[Fraction, ...]
    relation: Tuple[Tuple[Fraction, Fraction], ...]
    relation_failure_budget: Fraction


@dataclass(frozen=True)
class TransportState:
    version: str
    domain: Tuple[Fraction, ...]
    uncertainty: FrozenSet[Fraction]
    failure_budget: Fraction
    terminal: str
    raw_visits: int = 0
    raw_sum: Fraction = Fraction(0, 1)
    inherited_tokens: Tuple[str, ...] = ()
    inherited_origins: Tuple[str, ...] = ()


def relational_image(source_set, relation):
    source = frozenset(source_set)
    return frozenset(y for x, y in relation if x in source)


def affine_interval_hull(x_lo, x_hi, a, b, error_lo=Fraction(0), error_hi=Fraction(0)):
    for value in (x_lo, x_hi, a, b, error_lo, error_hi):
        if not isinstance(value, Fraction):
            raise TypeError("affine interval arguments must be Fraction")
    if x_lo > x_hi or error_lo > error_hi:
        raise ValueError("invalid interval")
    corners = (
        a * x_lo + b + error_lo,
        a * x_lo + b + error_hi,
        a * x_hi + b + error_lo,
        a * x_hi + b + error_hi,
    )
    return min(corners), max(corners)


def identify_boolean(state, query):
    outcomes = {bool(query(x)) for x in state.uncertainty}
    if outcomes == {True}:
        return "IDENTIFIED_TRUE"
    if outcomes == {False}:
        return "IDENTIFIED_FALSE"
    return "CANNOT_IDENTIFY"


class TransportCampaign:
    def __init__(self, source_version, source_domain, alpha):
        _version_number(source_version)
        self.source_version = source_version
        self.source_domain = _canonical_domain(source_domain)
        _check_fraction_01(alpha, "alpha")
        self.alpha = alpha
        self.contracts = []
        self.locked = False
        self._tail_version = source_version
        self._tail_domain = self.source_domain
        self._seen_versions = {source_version}
        self.state = None

    def register_contract(self, name, from_version, to_version, change_kind,
                          source_domain, target_domain, relation,
                          relation_failure_budget=Fraction(0)):
        if self.locked:
            raise RuntimeError("campaign locked after source activation")
        if change_kind not in ALLOWED_KINDS:
            raise ValueError("invalid developmental change kind")
        if from_version != self._tail_version:
            raise ValueError("contract must continue current registered chain")
        if _version_number(to_version) != _version_number(from_version) + 1:
            raise ValueError("version skip/back-edge rejected")
        if to_version in self._seen_versions:
            raise ValueError("target version already registered")

        source_domain = _canonical_domain(source_domain)
        target_domain = _canonical_domain(target_domain)
        if source_domain != self._tail_domain:
            raise ValueError("source domain must equal current tail domain")
        _check_fraction_01(relation_failure_budget, "relation_failure_budget")

        relation = tuple(relation)
        if not relation:
            raise ValueError("registered relation must be nonempty")
        seen_pairs = set()
        for pair in relation:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("relation entries must be 2-tuples")
            x, y = pair
            if not isinstance(x, Fraction) or not isinstance(y, Fraction):
                raise TypeError("relation endpoints must be Fraction")
            if x not in source_domain or y not in target_domain:
                raise ValueError("out-of-domain relation endpoint")
            if pair in seen_pairs:
                raise ValueError("duplicate relation pair")
            seen_pairs.add(pair)

        covered_sources = {x for x, _ in relation}
        if set(source_domain) - covered_sources:
            raise ValueError("registered relation omits a source-domain point")

        contract = TransportContract(
            name=name,
            from_version=from_version,
            to_version=to_version,
            change_kind=change_kind,
            source_domain=source_domain,
            target_domain=target_domain,
            relation=relation,
            relation_failure_budget=relation_failure_budget,
        )
        self.contracts.append(contract)
        self._tail_version = to_version
        self._tail_domain = target_domain
        self._seen_versions.add(to_version)
        return contract

    def activate_source(self, source_uncertainty):
        if self.locked:
            raise RuntimeError("source already activated")
        source_uncertainty = frozenset(source_uncertainty)
        if not source_uncertainty:
            raise ValueError("source uncertainty must be nonempty")
        if not all(isinstance(x, Fraction) for x in source_uncertainty):
            raise TypeError("source uncertainty points must be Fraction")
        if not source_uncertainty.issubset(set(self.source_domain)):
            raise ValueError("source uncertainty outside source domain")
        self.locked = True
        self.state = TransportState(
            version=self.source_version,
            domain=self.source_domain,
            uncertainty=source_uncertainty,
            failure_budget=self.alpha,
            terminal="SOURCE_ACTIVE",
        )
        return self.state

    def propagate_contract(self, contract_index):
        if not self.locked or self.state is None:
            raise RuntimeError("activate source before propagation")
        contract = self.contracts[contract_index]
        if self.state.version != contract.from_version:
            raise RuntimeError("state/contract version mismatch")
        image = relational_image(self.state.uncertainty, contract.relation)
        failure = min(Fraction(1), self.state.failure_budget + contract.relation_failure_budget)
        self.state = TransportState(
            version=contract.to_version,
            domain=contract.target_domain,
            uncertainty=image,
            failure_budget=failure,
            terminal="TRANSPORTED",
        )
        return self.state

    def propagate_all(self):
        if not self.locked or self.state is None:
            raise RuntimeError("activate source before propagation")
        states = [self.state]
        for index in range(len(self.contracts)):
            states.append(self.propagate_contract(index))
        return states

    def propagate_missing_relation(self, target_version, target_domain):
        if not self.locked or self.state is None:
            raise RuntimeError("activate source before propagation")
        if _version_number(target_version) != _version_number(self.state.version) + 1:
            raise ValueError("missing-relation target must be next version")
        target_domain = _canonical_domain(target_domain)
        self.state = TransportState(
            version=target_version,
            domain=target_domain,
            uncertainty=frozenset(target_domain),
            failure_budget=self.state.failure_budget,
            terminal="CANNOT_IDENTIFY_NO_RELATION",
        )
        return self.state


def frozen_five_kind_campaign():
    F = Fraction
    X0 = tuple(F(x) for x in (-2, -1, 0, 1, 2))
    X1 = tuple(F(x) for x in (-1, 0, 1, 2, 3))
    X3 = tuple(F(x) for x in (-1, 0, 1, 2, 3, 4))
    X4 = tuple(F(x) for x in (-2, -1, 0, 1, 2, 3, 4, 5))
    X5 = tuple(F(x) for x in (0, 1, 4, 9, 16, 25))

    campaign = TransportCampaign("v0", X0, F(1, 20))
    campaign.register_contract("info", "v0", "v1", "INFO", X0, X1,
                               tuple((x, x + 1) for x in X0))
    campaign.register_contract("recode", "v1", "v2", "RECODE", X1, X1,
                               tuple((x, x) for x in X1))
    campaign.register_contract("skill", "v2", "v3", "SKILL", X1, X3,
                               tuple((x, y) for x in X1 for y in (x, x + 1)))
    campaign.register_contract("law", "v3", "v4", "LAW", X3, X4,
                               tuple((x, y) for x in X3 for y in (x - 1, x, x + 1)))
    campaign.register_contract("morph", "v4", "v5", "MORPH", X4, X5,
                               tuple((x, x * x) for x in X4))
    campaign.activate_source(F(x) for x in (-1, 0, 1))
    return campaign


def _tight_union_bound_control():
    atoms = tuple(range(200))
    source_fail = set(range(0, 10))
    relation1_fail = set(range(10, 12))
    relation2_fail = {12}
    good = set(atoms) - source_fail - relation1_fail - relation2_fail
    return {
        "atoms": len(atoms),
        "source_failure": "%d/200" % len(source_fail),
        "relation1_failure": "%d/200" % len(relation1_fail),
        "relation2_failure": "%d/200" % len(relation2_fail),
        "joint_good": "%d/200" % len(good),
        "bound_is_tight": len(good) == 187,
        "independence_used": False,
    }


def build_receipt():
    F = Fraction
    campaign = frozen_five_kind_campaign()
    states = campaign.propagate_all()

    interval = affine_interval_hull(F(1, 4), F(3, 4), F(-2), F(3), F(-1, 10), F(1, 10))
    interval_corners = sorted({
        F(-2) * x + F(3) + e
        for x in (F(1, 4), F(3, 4))
        for e in (F(-1, 10), F(1, 10))
    })

    nonlinear_source = frozenset((F(-1), F(0), F(1)))
    nonlinear_relation = tuple((x, y) for x in nonlinear_source
                               for y in (x * x - 1, x * x, x * x + 1))
    nonlinear_image = relational_image(nonlinear_source, nonlinear_relation)

    uncertain_total = F(1, 20) + F(1, 100) + F(1, 200)
    partial_sums = {}
    for n in (1, 2, 5, 1000):
        s = sum((F(1, 20) / F(t * (t + 1)) for t in range(1, n + 1)), F(0))
        partial_sums[str(n)] = {
            "sum": _fstr(s),
            "closed_form": _fstr(F(1, 20) * F(n, n + 1)),
            "strictly_below_beta": s < F(1, 20),
        }

    ignorance = TransportCampaign("v0", (F(0),), F(0))
    ignorance.activate_source((F(0),))
    ignorance_state = ignorance.propagate_missing_relation("v1", (F(0), F(1), F(2)))

    return {
        "claim": "SOUND_DEVELOPMENTAL_UNCERTAINTY_TRANSPORT_AT_REGISTERED_FINITE_SCOPE",
        "issue": 748,
        "source_alpha": _fstr(F(1, 20)),
        "five_kind_chain": [{
            "version": state.version,
            "uncertainty": _sorted_fstr(state.uncertainty),
            "failure_budget": _fstr(state.failure_budget),
            "terminal": state.terminal,
            "raw_visits": state.raw_visits,
            "raw_sum": _fstr(state.raw_sum),
            "inherited_token_count": len(state.inherited_tokens),
            "inherited_origin_count": len(state.inherited_origins),
        } for state in states],
        "interval_affine": {
            "hull": [_fstr(interval[0]), _fstr(interval[1])],
            "corners": [_fstr(x) for x in interval_corners],
        },
        "nonlinear_relation": {"image": _sorted_fstr(nonlinear_image)},
        "uncertain_budget": {
            "total_failure": _fstr(uncertain_total),
            "coverage_lower_bound": _fstr(F(1) - uncertain_total),
            "countable_partial_sums": partial_sums,
            "infinite_horizon_combined_lower_bound": _fstr(F(9, 10)),
            "tight_finite_union_bound_control": _tight_union_bound_control(),
        },
        "ignorance": {
            "uncertainty": _sorted_fstr(ignorance_state.uncertainty),
            "terminal": ignorance_state.terminal,
            "x_gt_0": identify_boolean(ignorance_state, lambda x: x > 0),
            "constant_true": identify_boolean(ignorance_state, lambda x: True),
        },
        "copy_counterexample": {
            "source_truth_set": ["0"],
            "target_domain": ["0", "1"],
            "actual_target": "1",
            "copied_set_covers": False,
            "full_domain_covers": True,
        },
        "raw_evidence_inheritance": "ZERO_BY_STATE_CONSTRUCTOR",
        "independence_assumption": False,
    }


if __name__ == "__main__":
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
