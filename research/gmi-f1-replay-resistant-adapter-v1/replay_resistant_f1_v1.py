"""Replay-resistant operational adapter from the F1 paired-difference assay to ARC-6.

Statistical validity is conditional on ARC-6's conditional-mean premise. Declared
origin IDs and tokens enforce bookkeeping invariants only; they do not authenticate
physical sample freshness.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
from typing import Dict, Iterable, Mapping, Optional, Tuple

F = Fraction


def _load_arc6():
    path = Path(__file__).resolve().parents[1] / "gmi-countable-row-corrigendum-v1" / "countable_rows_v1.py"
    spec = importlib.util.spec_from_file_location("gmi_arc6_countable_rows_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load ARC-6 parent module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ARC6 = _load_arc6()


def _fraction(value, name: str) -> F:
    if not isinstance(value, F):
        raise ValueError(f"{name} must be an exact Fraction")
    return value


def _text(value, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


@dataclass(frozen=True)
class ComparisonContract:
    comparison_id: str
    capability_id: str
    developmental_version: int
    system_digest: str
    parent_digest: str
    twin_digest: str
    tau_parent: F
    tau_twin: F

    def __post_init__(self):
        for value, name in (
            (self.comparison_id, "comparison_id"),
            (self.capability_id, "capability_id"),
            (self.system_digest, "system_digest"),
            (self.parent_digest, "parent_digest"),
            (self.twin_digest, "twin_digest"),
        ):
            _text(value, name)
        if type(self.developmental_version) is not int or self.developmental_version < 1:
            raise ValueError("developmental_version must be an integer >= 1")
        _fraction(self.tau_parent, "tau_parent")
        _fraction(self.tau_twin, "tau_twin")
        if not F(-1) <= self.tau_parent <= F(1):
            raise ValueError("tau_parent must lie in [-1,1]")
        if not F(0) <= self.tau_twin <= F(1):
            raise ValueError("tau_twin must lie in [0,1]")


@dataclass(frozen=True)
class DerivedAffineContract:
    name: str
    terms: Tuple[Tuple[str, F], ...]
    bias: F = F(0)

    def __post_init__(self):
        _text(self.name, "name")
        _fraction(self.bias, "bias")
        if not isinstance(self.terms, tuple) or not self.terms:
            raise ValueError("terms must be a nonempty tuple")
        seen = set()
        for row_id, weight in self.terms:
            _text(row_id, "row_id")
            _fraction(weight, "weight")
            if row_id in seen:
                raise ValueError("derived contract cannot repeat a row_id")
            seen.add(row_id)


@dataclass(frozen=True)
class Reservation:
    origin_id: str
    token: str


@dataclass
class _RowState:
    row_id: str
    row_index: int
    comparison_key: Tuple[str, int]
    role: str
    mapped_sum: F = F(0)
    visits: int = 0
    acquisition_charges: int = 0
    pending: Dict[str, Reservation] = field(default_factory=dict)
    retired: bool = False
    retirement_reason: Optional[str] = None


class Campaign:
    """One ARC-6 alpha campaign with adaptive, never-reused row indices."""

    def __init__(self, alpha: F):
        ARC6.probability(alpha)
        self.alpha = alpha
        self._next_row = 1
        self._comparisons: Dict[Tuple[str, int], ComparisonContract] = {}
        self._comparison_rows: Dict[Tuple[str, int], Tuple[str, str]] = {}
        self._rows: Dict[str, _RowState] = {}
        self._origins_seen = set()
        self._tokens_seen = set()
        self._derived: Dict[str, DerivedAffineContract] = {}

    def register_comparison(self, contract: ComparisonContract) -> Tuple[str, str]:
        if not isinstance(contract, ComparisonContract):
            raise ValueError("contract must be ComparisonContract")
        key = (contract.comparison_id, contract.developmental_version)
        if key in self._comparisons:
            raise ValueError("comparison/version already registered")
        row_ids = []
        for role in ("positive", "twin"):
            row_id = f"{contract.comparison_id}@v{contract.developmental_version}:{role}"
            if row_id in self._rows:
                raise ValueError("row identity collision")
            self._rows[row_id] = _RowState(row_id, self._next_row, key, role)
            row_ids.append(row_id)
            self._next_row += 1
        self._comparisons[key] = contract
        self._comparison_rows[key] = (row_ids[0], row_ids[1])
        return row_ids[0], row_ids[1]

    def _row(self, row_id: str) -> _RowState:
        if row_id not in self._rows:
            raise KeyError(f"unknown row {row_id}")
        return self._rows[row_id]

    def row_ids(self, comparison_id: str, developmental_version: int) -> Tuple[str, str]:
        key = (comparison_id, developmental_version)
        if key not in self._comparison_rows:
            raise KeyError("unknown comparison/version")
        return self._comparison_rows[key]

    def reserve(self, row_id: str, origin_id: str, token: str) -> None:
        row = self._row(row_id)
        if row.retired:
            raise RuntimeError("row is retired")
        _text(origin_id, "origin_id")
        _text(token, "token")
        if origin_id in self._origins_seen:
            raise ValueError("origin_id already used in campaign")
        if token in self._tokens_seen:
            raise ValueError("token already used in campaign")
        self._origins_seen.add(origin_id)
        self._tokens_seen.add(token)
        row.acquisition_charges += 1
        row.pending[token] = Reservation(origin_id, token)

    def _consume(self, row: _RowState, origin_id: str, token: str) -> Reservation:
        if row.retired:
            raise RuntimeError("row is retired")
        if token not in row.pending:
            raise ValueError("observation has no live prior reservation")
        reservation = row.pending[token]
        if reservation.origin_id != origin_id:
            raise ValueError("origin_id does not match reservation")
        del row.pending[token]
        return reservation

    def _retire(self, row: _RowState, reason: str) -> None:
        row.retired = True
        row.retirement_reason = reason
        row.pending.clear()  # reservations remain charged and globally spent

    def observe(self, row_id: str, origin_id: str, token: str, paired_difference) -> str:
        row = self._row(row_id)
        self._consume(row, origin_id, token)
        if not isinstance(paired_difference, F) or not F(-1) <= paired_difference <= F(1):
            self._retire(row, "MALFORMED_OUTCOME")
            return "RETIRED_MALFORMED"
        mapped = (paired_difference + 1) / 2
        row.mapped_sum += mapped
        row.visits += 1
        return "ACCEPTED"

    def mark_missing(self, row_id: str, origin_id: str, token: str) -> str:
        row = self._row(row_id)
        self._consume(row, origin_id, token)
        self._retire(row, "MISSING_OUTCOME")
        return "RETIRED_MISSING"

    def row_stats(self, row_id: str) -> Mapping[str, object]:
        row = self._row(row_id)
        return {
            "row_id": row.row_id,
            "row_index": row.row_index,
            "role": row.role,
            "visits": row.visits,
            "acquisition_charges": row.acquisition_charges,
            "pending": len(row.pending),
            "retired": row.retired,
            "retirement_reason": row.retirement_reason,
            "mapped_sum": row.mapped_sum,
        }

    def row_interval(self, row_id: str) -> Tuple[F, F]:
        row = self._row(row_id)
        if row.retired:
            raise RuntimeError("retired row has no admissible inferential interval")
        lo_y, hi_y = ARC6.interval_from_sum(row.mapped_sum, self.alpha, row.row_index, row.visits)
        return 2 * lo_y - 1, 2 * hi_y - 1

    def decision(self, comparison_id: str, developmental_version: int) -> str:
        key = (comparison_id, developmental_version)
        if key not in self._comparisons:
            raise KeyError("unknown comparison/version")
        contract = self._comparisons[key]
        positive_id, twin_id = self._comparison_rows[key]
        positive = self._row(positive_id)
        twin = self._row(twin_id)
        if positive.retired or twin.retired:
            return "CANNOT_IDENTIFY_RETIRED"
        lp, up = self.row_interval(positive_id)
        lt, ut = self.row_interval(twin_id)
        if lp > contract.tau_parent and lt >= -contract.tau_twin and ut <= contract.tau_twin:
            return "SUPPORTED"
        if up <= contract.tau_parent:
            return "PARENT_NOT_SEPARATED"
        if ut < -contract.tau_twin or lt > contract.tau_twin:
            return "TWIN_NOT_COLLAPSED"
        return "CANNOT_IDENTIFY"

    def register_derived(self, contract: DerivedAffineContract) -> None:
        if not isinstance(contract, DerivedAffineContract):
            raise ValueError("contract must be DerivedAffineContract")
        if contract.name in self._derived:
            raise ValueError("derived contract already registered")
        for row_id, _weight in contract.terms:
            row = self._row(row_id)
            if row.acquisition_charges != 0 or row.visits != 0:
                raise ValueError("derived weights must be frozen before referenced acquisition")
        self._derived[contract.name] = contract

    def derived_interval(self, name: str) -> Tuple[F, F]:
        if name not in self._derived:
            raise KeyError("unknown derived contract")
        contract = self._derived[name]
        terms = []
        for row_id, weight in contract.terms:
            row = self._row(row_id)
            if row.retired:
                raise RuntimeError("derived interval references a retired row")
            terms.append((weight, self.row_interval(row_id)))
        return affine_interval(terms, contract.bias)


def affine_interval(terms: Iterable[Tuple[F, Tuple[F, F]]], bias: F = F(0)) -> Tuple[F, F]:
    _fraction(bias, "bias")
    lo = hi = bias
    any_term = False
    for weight, interval in terms:
        any_term = True
        _fraction(weight, "weight")
        if not isinstance(interval, tuple) or len(interval) != 2:
            raise ValueError("interval must be a (low, high) tuple")
        left, right = interval
        _fraction(left, "interval lower")
        _fraction(right, "interval upper")
        if left > right:
            raise ValueError("interval lower must not exceed upper")
        a, b = weight * left, weight * right
        lo += min(a, b)
        hi += max(a, b)
    if not any_term:
        raise ValueError("at least one affine term is required")
    return lo, hi


def frac(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _contract(version: int = 1) -> ComparisonContract:
    return ComparisonContract(
        comparison_id="f1-demo",
        capability_id="verification_reliability",
        developmental_version=version,
        system_digest=f"system-v{version}",
        parent_digest="parent-v1",
        twin_digest="twin-v1",
        tau_parent=F(1, 2),
        tau_twin=F(1, 4),
    )


def _feed_constant(campaign: Campaign, row_id: str, value: F, n: int, prefix: str) -> None:
    for i in range(n):
        origin = f"{prefix}-origin-{i}"
        token = f"{prefix}-token-{i}"
        campaign.reserve(row_id, origin, token)
        status = campaign.observe(row_id, origin, token, value)
        if status != "ACCEPTED":
            raise RuntimeError("unexpected feed failure")


def build_receipt() -> Mapping[str, object]:
    alpha = F(1, 20)
    campaign = Campaign(alpha)
    positive, twin = campaign.register_comparison(_contract(1))
    campaign.register_derived(DerivedAffineContract("contrast", ((positive, F(1)), (twin, F(-1)))))
    _feed_constant(campaign, positive, F(1), 1024, "pos")
    _feed_constant(campaign, twin, F(0), 1024, "twin")
    positive_interval = campaign.row_interval(positive)
    twin_interval = campaign.row_interval(twin)
    contrast_interval = campaign.derived_interval("contrast")

    small = Campaign(alpha)
    small_positive, small_twin = small.register_comparison(_contract(1))
    _feed_constant(small, small_positive, F(1), 64, "small-pos")
    _feed_constant(small, small_twin, F(0), 64, "small-twin")

    replay_blocked = False
    try:
        campaign.observe(positive, "pos-origin-0", "pos-token-0", F(1))
    except ValueError:
        replay_blocked = True
    duplicate_origin_blocked = False
    try:
        campaign.reserve(positive, "pos-origin-0", "fresh-token")
    except ValueError:
        duplicate_origin_blocked = True

    posthoc_derived_blocked = False
    try:
        campaign.register_derived(DerivedAffineContract("posthoc", ((positive, F(1)),)))
    except ValueError:
        posthoc_derived_blocked = True

    v2_positive, v2_twin = campaign.register_comparison(_contract(2))

    bad_contract = ComparisonContract(
        "bad", "verification_reliability", 1, "bad-system", "parent-v1", "twin-v1", F(1, 2), F(1, 4)
    )
    bad_positive, bad_twin = campaign.register_comparison(bad_contract)
    campaign.reserve(bad_positive, "bad-origin", "bad-token")
    malformed_status = campaign.observe(bad_positive, "bad-origin", "bad-token", F(2))
    campaign.reserve(bad_twin, "missing-origin", "missing-token")
    missing_status = campaign.mark_missing(bad_twin, "missing-origin", "missing-token")

    cache_contract = ComparisonContract(
        "cache-control", "verification_reliability", 1, "cache-system", "parent-v1", "twin-v1", F(1, 2), F(1, 4)
    )
    cache_positive, _cache_twin = campaign.register_comparison(cache_contract)
    _feed_constant(campaign, cache_positive, F(1), 4, "declared-distinct-cached")

    return {
        "schema": "ReplayResistantF1ARC6AdapterReceiptV1",
        "issue": 657,
        "parent_issue": 602,
        "alpha": frac(alpha),
        "claim_ceiling": "CONDITIONAL_FINITE_RECORD_ADAPTER_NOT_G6",
        "full_control": {
            "visits_per_row": 1024,
            "positive_interval": [frac(x) for x in positive_interval],
            "twin_interval": [frac(x) for x in twin_interval],
            "decision": campaign.decision("f1-demo", 1),
            "contrast_interval": [frac(x) for x in contrast_interval],
            "contrast_contains_one": contrast_interval[0] <= F(1) <= contrast_interval[1],
        },
        "small_prefix_control": {
            "visits_per_row": 64,
            "decision": small.decision("f1-demo", 1),
        },
        "provenance_controls": {
            "replay_blocked": replay_blocked,
            "duplicate_origin_blocked": duplicate_origin_blocked,
            "posthoc_derived_blocked": posthoc_derived_blocked,
            "v2_positive_row_index": campaign.row_stats(v2_positive)["row_index"],
            "v2_twin_row_index": campaign.row_stats(v2_twin)["row_index"],
            "v2_visits": [campaign.row_stats(v2_positive)["visits"], campaign.row_stats(v2_twin)["visits"]],
            "malformed_status": malformed_status,
            "malformed_visits": campaign.row_stats(bad_positive)["visits"],
            "malformed_acquisition_charges": campaign.row_stats(bad_positive)["acquisition_charges"],
            "missing_status": missing_status,
            "missing_visits": campaign.row_stats(bad_twin)["visits"],
            "missing_acquisition_charges": campaign.row_stats(bad_twin)["acquisition_charges"],
            "distinct_metadata_cached_draws_accepted": campaign.row_stats(cache_positive)["visits"],
            "metadata_is_not_physical_freshness_proof": True,
        },
        "marginal_joint_counterexample": {
            "each_marginal_coverage": "19/20",
            "joint_coverage_with_disjoint_failures": "9/10",
        },
    }


def main() -> int:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
