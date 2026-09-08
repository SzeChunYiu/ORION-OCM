"""G4.2/G4.3 exact reusable-horizon toy. No ML. No scalarization.

PR #154 / residual-strategy-regime already sweeps horizon, query order, full
reset, and checkpoint/replay on the 142-target semantic-BFS vs inverse lifetime.
That branch is not merged here. This capsule cites it and fills the missing
independent axes (reuse density, drift ≠ reset, revision frequency) on a finite
noiseless cache/probe toy, while re-running horizon/reset/checkpoint so the
capsule is executable without that unmerged tree.

Integer cost vectors only. Pareto/price half-spaces are published raw.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
PR154_HEAD = "86a5ad1d0387d0ad0a7022d6385284229bc36f6e"
PR154_BRANCH = "codex/residual-strategy-regime-20260908"

ITEMS = (0, 1, 2)
RENT = 3
BUILD = 8
HIT = 1
PROBE = 2
ACT_OK = 1
ACT_WRONG = 9
CHECKPOINT_IO = 1
COORDINATES = (
    "rent",
    "build",
    "hit",
    "probe",
    "act",
    "checkpoint_write",
    "checkpoint_read",
    "replay",
    "invalidation",
)


def cost(**parts):
    row = {name: 0 for name in COORDINATES}
    row.update(parts)
    if any(row[name] < 0 for name in COORDINATES):
        raise ValueError("resource coordinates must be nonnegative")
    unknown = set(parts) - set(COORDINATES)
    if unknown:
        raise ValueError("unknown coordinates: " + ",".join(sorted(unknown)))
    return tuple(row[name] for name in COORDINATES)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def as_dict(vector):
    return {name: int(value) for name, value in zip(COORDINATES, vector)}


def weakly_dominates(a, b):
    return all(x <= y for x, y in zip(a, b))


def strictly_dominates(a, b):
    return weakly_dominates(a, b) and a != b


def pareto_insert(front, vector):
    kept = []
    for existing in front:
        if strictly_dominates(existing, vector):
            return front
        if not strictly_dominates(vector, existing):
            kept.append(existing)
    kept.append(vector)
    return tuple(sorted(kept))


def pareto_insert_payload(front, vector, payload):
    """Pareto-minimise cost vectors; on equal cost keep the richer payload."""
    kept = []
    for existing_v, existing_p in front:
        if strictly_dominates(existing_v, vector):
            return front
        if existing_v == vector:
            payload = max(existing_p, payload)
            continue
        if strictly_dominates(vector, existing_v):
            continue
        kept.append((existing_v, existing_p))
    kept.append((vector, payload))
    return tuple(kept)


def pareto_front(named_vectors):
    names = tuple(named_vectors)
    survivors = []
    for name in names:
        vector = named_vectors[name]
        if any(strictly_dominates(named_vectors[other], vector) for other in names if other != name):
            continue
        survivors.append(name)
    return tuple(survivors)


def price_halfspaces(a, b):
    """Nonnegative prices that strictly prefer A, B, or neither (incomparable)."""
    prefer_a = tuple(i for i, (x, y) in enumerate(zip(a, b)) if x < y)
    prefer_b = tuple(i for i, (x, y) in enumerate(zip(a, b)) if y < x)
    return {
        "a_strictly_cheaper_coordinates": [COORDINATES[i] for i in prefer_a],
        "b_strictly_cheaper_coordinates": [COORDINATES[i] for i in prefer_b],
        "componentwise_a_leq_b": weakly_dominates(a, b),
        "componentwise_b_leq_a": weakly_dominates(b, a),
        "pareto_incomparable": bool(prefer_a) and bool(prefer_b),
        "price_witness_prefer_a": (
            {COORDINATES[prefer_a[0]]: 1} if prefer_a else None
        ),
        "price_witness_prefer_b": (
            {COORDINATES[prefer_b[0]]: 1} if prefer_b else None
        ),
    }


@dataclass(frozen=True)
class Lifecycle:
    reset_every: int | None = None
    drift_every: int | None = None
    revision_every: int | None = None
    revision_item: int = 0
    checkpoint_every: int | None = None
    capacity: int | None = None


@dataclass(frozen=True)
class Outcome:
    vector: tuple
    h_eff: int
    peak_storage: int
    hits: int
    misses: int
    resets: int
    drifts: int
    revisions: int
    checkpoints: int


def remaining_count(sequence, start, item):
    return sum(1 for query in sequence[start:] if query == item)


def reuse_density(sequence):
    unique = len(set(sequence))
    horizon = len(sequence)
    unused = horizon - unique if horizon else 0
    return {"unused_queries": unused, "horizon": horizon, "unique": unique}


def analytic_should_buy(remaining, rent=RENT, hit=HIT, build=BUILD):
    return remaining * (rent - hit) > build


def _apply_lifecycle(cache_order, cache_set, t, life, vector, counts):
    previous = t  # events fire after completing query t, before t+1; caller uses t completed
    if life.reset_every and previous > 0 and previous % life.reset_every == 0:
        dropped = len(cache_set)
        cache_order.clear()
        cache_set.clear()
        vector = add(vector, cost(invalidation=dropped))
        counts["resets"] += 1
    if life.drift_every and previous > 0 and previous % life.drift_every == 0 and cache_order:
        stale = cache_order.popleft()
        cache_set.discard(stale)
        vector = add(vector, cost(invalidation=1))
        counts["drifts"] += 1
    if life.revision_every and previous > 0 and previous % life.revision_every == 0:
        item = life.revision_item
        counts["revisions"] += 1
        if item in cache_set:
            cache_set.discard(item)
            cache_order = deque(x for x in cache_order if x != item)
            vector = add(vector, cost(invalidation=1))
    if life.checkpoint_every and previous > 0 and previous % life.checkpoint_every == 0:
        snapshot = list(cache_order)
        vector = add(
            vector,
            cost(
                checkpoint_write=CHECKPOINT_IO,
                checkpoint_read=CHECKPOINT_IO,
                replay=len(snapshot),
            ),
        )
        cache_order.clear()
        cache_order.extend(snapshot)
        cache_set.clear()
        cache_set.update(snapshot)
        counts["checkpoints"] += 1
    return cache_order, cache_set, vector, counts


def _admit(cache_order, cache_set, item, capacity, evict, t):
    if item in cache_set:
        return cache_order, cache_set, cost()
    if capacity is not None and len(cache_set) >= capacity:
        victim = evict(cache_order, cache_set, t)
        cache_set.discard(victim)
        cache_order = deque(x for x in cache_order if x != victim)
    cache_set.add(item)
    cache_order.append(item)
    return cache_order, cache_set, cost(build=BUILD)


def simulate(sequence, decide, life=Lifecycle(), *, evict=None):
    """Run an exact cache strategy. `decide(t, item, cached, remaining)` -> 'hit'|'rent'|'buy'.

    Buy constructs the reusable entry and answers the current query (BUILD, no extra rent).
    Rent answers without retaining state.
    """
    cache_order = deque()
    cache_set = set()
    vector = cost()
    h_eff = 0
    peak = 0
    hits = 0
    misses = 0
    counts = {"resets": 0, "drifts": 0, "revisions": 0, "checkpoints": 0}
    if evict is None:
        evict = lru_evict

    for t, item in enumerate(sequence, start=1):
        cached = item in cache_set
        remaining = remaining_count(sequence, t - 1, item)
        action = decide(t, item, cached, remaining)
        if cached:
            if action != "hit":
                raise AssertionError("cached item must hit")
            vector = add(vector, cost(hit=HIT))
            h_eff += 1
            hits += 1
            cache_order = deque(x for x in cache_order if x != item)
            cache_order.append(item)
        elif action == "rent":
            vector = add(vector, cost(rent=RENT))
            misses += 1
        elif action == "buy":
            cache_order, cache_set, built = _admit(
                cache_order, cache_set, item, life.capacity, evict, t
            )
            vector = add(vector, built)
            misses += 1
        else:
            raise ValueError("action must be hit, rent, or buy")
        peak = max(peak, len(cache_set))
        cache_order, cache_set, vector, counts = _apply_lifecycle(
            cache_order, cache_set, t, life, vector, counts
        )
    return Outcome(
        vector=vector,
        h_eff=h_eff,
        peak_storage=peak,
        hits=hits,
        misses=misses,
        resets=counts["resets"],
        drifts=counts["drifts"],
        revisions=counts["revisions"],
        checkpoints=counts["checkpoints"],
    )


def always_rent(_t, _item, cached, _remaining):
    return "hit" if cached else "rent"


def always_buy(_t, _item, cached, _remaining):
    return "hit" if cached else "buy"


def analytic_threshold(_t, _item, cached, remaining):
    if cached:
        return "hit"
    return "buy" if analytic_should_buy(remaining) else "rent"


def ski_rental_factory():
    """Classic per-item deterministic ski rental: rent while paid + RENT < BUILD, then buy."""
    paid = {}

    def decide(_t, item, cached, _remaining):
        if cached:
            return "hit"
        if paid.get(item, 0) + RENT >= BUILD:
            return "buy"
        paid[item] = paid.get(item, 0) + RENT
        return "rent"

    return decide


def lru_evict(order, _cache_set, _t=None):
    return order[0]


def belady_evict_factory(sequence):
    def evict(order, cache_set, t):
        farthest, victim = -1, order[0]
        future = sequence[t:]
        for item in cache_set:
            nxt = next((i for i, query in enumerate(future) if query == item), 10**9)
            if nxt >= farthest:
                farthest, victim = nxt, item
        return victim
    return evict


def exact_dp_unlimited(sequence, life=Lifecycle()):
    """Exact known-sequence DP over cache subsets. Lifecycle events are applied after each query."""
    horizon = len(sequence)
    n = max(sequence) + 1 if sequence else 0
    all_masks = range(1 << n)

    def item_bit(item):
        return 1 << item

    def apply_mask_events(mask, t):
        vector = cost()
        events = {"resets": 0, "drifts": 0, "revisions": 0, "checkpoints": 0}
        if life.reset_every and t > 0 and t % life.reset_every == 0:
            dropped = bin(mask).count("1")
            mask = 0
            vector = add(vector, cost(invalidation=dropped))
            events["resets"] = 1
        if life.drift_every and t > 0 and t % life.drift_every == 0 and mask:
            # drop lowest-index cached item (deterministic analogue of oldest)
            bit = mask & -mask
            mask ^= bit
            vector = add(vector, cost(invalidation=1))
            events["drifts"] = 1
        if life.revision_every and t > 0 and t % life.revision_every == 0:
            events["revisions"] = 1
            bit = item_bit(life.revision_item)
            if mask & bit:
                mask ^= bit
                vector = add(vector, cost(invalidation=1))
        if life.checkpoint_every and t > 0 and t % life.checkpoint_every == 0:
            occupied = bin(mask).count("1")
            vector = add(
                vector,
                cost(
                    checkpoint_write=CHECKPOINT_IO,
                    checkpoint_read=CHECKPOINT_IO,
                    replay=occupied,
                ),
            )
            events["checkpoints"] = 1
        return mask, vector, events

    # Pareto sets of (cost_vector, (h_eff, peak)) at step t, mask.
    layer = {mask: ((cost(), (0, 0)),) for mask in all_masks}
    for t in range(horizon, 0, -1):
        item = sequence[t - 1]
        bit = item_bit(item)
        nxt = {}
        for mask in all_masks:
            options = ()
            if mask & bit:
                actions = (("hit", mask, cost(hit=HIT), 1),)
            else:
                buy_mask = mask | bit
                if life.capacity is not None and bin(buy_mask).count("1") > life.capacity:
                    actions = (("rent", mask, cost(rent=RENT), 0),)
                else:
                    actions = (
                        ("rent", mask, cost(rent=RENT), 0),
                        ("buy", buy_mask, cost(build=BUILD), 0),
                    )
            for _name, after, paid, reuse in actions:
                after_events, event_cost, _events = apply_mask_events(after, t)
                peak_now = bin(after).count("1")
                for future, payload in layer[after_events]:
                    future_h, future_peak = payload
                    total = add(add(paid, event_cost), future)
                    options = pareto_insert_payload(
                        options,
                        total,
                        (reuse + future_h, max(peak_now, future_peak)),
                    )
            nxt[mask] = options
        layer = nxt

    start = layer[0]
    if not start:
        raise AssertionError("DP produced an empty Pareto set")
    members = []
    for vector, payload in start:
        h_eff, peak = payload
        members.append(
            Outcome(
                vector=vector,
                h_eff=h_eff,
                peak_storage=peak,
                hits=h_eff,
                misses=horizon - h_eff,
                resets=0,
                drifts=0,
                revisions=0,
                checkpoints=0,
            )
        )
    return tuple(sorted(members, key=lambda row: (row.vector, -row.h_eff)))


def common_actions(version, good_actions):
    shared = set(good_actions[version[0]])
    for state in version[1:]:
        shared.intersection_update(good_actions[state])
    return frozenset(shared)


def decision_regions(states, actions, good_actions):
    return {
        action: frozenset(state for state in states if action in good_actions[state])
        for action in actions
    }


def contained_decision_actions(version, regions):
    version = frozenset(version)
    return frozenset(action for action, region in regions.items() if version <= region)


def probe_policy(version, good_actions, actions, probe_cost=PROBE):
    """Exact noiseless identification: stop if a common protected action exists."""
    gamma = common_actions(version, good_actions)
    regions = decision_regions(tuple(good_actions), actions, good_actions)
    contained = contained_decision_actions(version, regions)
    if gamma != contained:
        raise AssertionError("Gamma and contained decision-region actions must coincide")
    if gamma:
        action = sorted(gamma)[0]
        return {
            "stop": True,
            "action": action,
            "vector": cost(act=ACT_OK),
            "probes": 0,
        }
    # No common action: one noiseless probe identifies the state, then act.
    return {
        "stop": False,
        "action": None,
        "vector": cost(probe=probe_cost, act=ACT_OK),
        "probes": 1,
    }


def finite_probe_dp(stop_cost, probe_cost, identify_cost):
    """Budget-1 metareasoning: STOP vs one exact probe. Values are integer vectors' act/probe coords."""
    values = {0: stop_cost, 1: min(stop_cost, probe_cost + identify_cost)}
    policy = {0: None, 1: None if stop_cost <= probe_cost + identify_cost else "probe"}
    return values, policy


def frozen_sequences():
    """Exact frozen demand families. Density = (H - unique)/H."""
    families = {
        "constant": (0, 0, 0, 0, 0, 0, 0, 0),
        "unique_then_repeat": (0, 1, 2, 0, 1, 2, 0, 1),
        "all_unique_prefix": (0, 1, 2),
        "two_item_repeat": (0, 1, 0, 1, 0, 1, 0, 1),
        "late_reuse": (0, 1, 2, 0, 0, 0, 0, 0),
    }
    return families


def density_sequences(horizon=6):
    rows = []
    for unique in range(1, min(horizon, len(ITEMS)) + 1):
        items = ITEMS[:unique]
        seq = tuple(items[i % unique] for i in range(horizon))
        rows.append({"unique": unique, "unused_queries": horizon - unique, "horizon": horizon, "sequence": seq})
    return tuple(rows)


def order_permutations(multiset=(0, 0, 1, 1, 2, 2)):
    return tuple(sorted(set(permutations(multiset))))


def horizon_rows(sequence_prefix, strategy_name, decide, life=Lifecycle()):
    rows = []
    for horizon in range(1, len(sequence_prefix) + 1):
        seq = sequence_prefix[:horizon]
        policy = ski_rental_factory() if strategy_name == "ski_rental" else decide
        out = simulate(seq, policy, life)
        rows.append({
            "horizon": horizon,
            "h_eff": out.h_eff,
            "peak_storage": out.peak_storage,
            "vector": as_dict(out.vector),
            "reuse_density": reuse_density(seq),
        })
    return rows


def compare_parents(sequence, life=Lifecycle()):
    parents = {
        "always_rent": simulate(sequence, always_rent, life),
        "always_buy": simulate(sequence, always_buy, life),
        "analytic_threshold": simulate(sequence, analytic_threshold, life),
        "ski_rental": simulate(sequence, ski_rental_factory(), life),
    }
    if life.capacity is None and life.reset_every is None and life.drift_every is None and life.revision_every is None:
        dp_members = exact_dp_unlimited(sequence, life)
        parents["exact_dp_pareto"] = dp_members
        analytic_vec = parents["analytic_threshold"].vector
        match = next((m for m in dp_members if m.vector == analytic_vec), dp_members[0])
        parents["exact_dp"] = match
    named = {name: out.vector for name, out in parents.items() if name != "exact_dp_pareto"}
    return {
        "sequence": list(sequence),
        "reuse_density": reuse_density(sequence),
        "pareto": list(pareto_front(named)),
        "parents": {
            name: {
                "vector": as_dict(out.vector),
                "h_eff": out.h_eff,
                "peak_storage": out.peak_storage,
                "hits": out.hits,
                "misses": out.misses,
            }
            for name, out in parents.items()
            if name != "exact_dp_pareto"
        },
        "exact_dp_pareto": [
            {"vector": as_dict(out.vector), "h_eff": out.h_eff, "peak_storage": out.peak_storage}
            for out in parents.get("exact_dp_pareto", ())
        ],
        "rent_vs_buy_prices": price_halfspaces(
            parents["always_rent"].vector, parents["always_buy"].vector
        ),
    }


def cache_admission_rows(sequence, capacity=2):
    life = Lifecycle(capacity=capacity)
    lru = simulate(sequence, always_buy, life, evict=lru_evict)
    belady = simulate(sequence, always_buy, life, evict=belady_evict_factory(sequence))
    return {
        "capacity": capacity,
        "lru": {"vector": as_dict(lru.vector), "h_eff": lru.h_eff, "peak_storage": lru.peak_storage},
        "belady_opt": {"vector": as_dict(belady.vector), "h_eff": belady.h_eff, "peak_storage": belady.peak_storage},
        "belady_weakly_dominates_lru": weakly_dominates(belady.vector, lru.vector),
        "h_eff_belady_geq_lru": belady.h_eff >= lru.h_eff,
    }


def lifecycle_sweep(sequence):
    rows = []
    for kind, values in (
        ("reset", (1, 2, 4, 8)),
        ("drift", (1, 2, 4, 8)),
        ("revision", (1, 2, 4, 8)),
        ("checkpoint", (2, 4, 8)),
    ):
        for interval in values:
            life = Lifecycle(
                reset_every=interval if kind == "reset" else None,
                drift_every=interval if kind == "drift" else None,
                revision_every=interval if kind == "revision" else None,
                checkpoint_every=interval if kind == "checkpoint" else None,
            )
            buy = simulate(sequence, always_buy, life)
            rent = simulate(sequence, always_rent, life)
            rows.append({
                "kind": kind,
                "interval": interval,
                "buy": {
                    "vector": as_dict(buy.vector),
                    "h_eff": buy.h_eff,
                    "peak_storage": buy.peak_storage,
                    "resets": buy.resets,
                    "drifts": buy.drifts,
                    "revisions": buy.revisions,
                    "checkpoints": buy.checkpoints,
                },
                "rent": {"vector": as_dict(rent.vector), "h_eff": rent.h_eff},
                "prices": price_halfspaces(rent.vector, buy.vector),
            })
    return rows


def density_sweep():
    rows = []
    for spec in density_sequences():
        comparison = compare_parents(spec["sequence"])
        rows.append({
            "unique": spec["unique"],
            "unused_queries": spec["unused_queries"],
            "horizon": spec["horizon"],
            "h_eff_always_buy": comparison["parents"]["always_buy"]["h_eff"],
            "h_eff_always_rent": comparison["parents"]["always_rent"]["h_eff"],
            "h_eff_analytic": comparison["parents"]["analytic_threshold"]["h_eff"],
            "pareto": comparison["pareto"],
            "always_buy": comparison["parents"]["always_buy"],
            "always_rent": comparison["parents"]["always_rent"],
            "ski_rental": comparison["parents"]["ski_rental"],
            "analytic_threshold": comparison["parents"]["analytic_threshold"],
            "exact_dp": comparison["parents"].get("exact_dp"),
        })
    return rows


def order_sweep():
    unlimited = []
    capped = []
    for seq in order_permutations():
        buy = simulate(seq, always_buy)
        limited = simulate(seq, always_buy, Lifecycle(capacity=2), evict=lru_evict)
        unlimited.append({"sequence": list(seq), "h_eff": buy.h_eff, "vector": as_dict(buy.vector)})
        capped.append({"sequence": list(seq), "h_eff": limited.h_eff, "vector": as_dict(limited.vector)})
    u_h = {row["h_eff"] for row in unlimited}
    u_v = {tuple(row["vector"].values()) for row in unlimited}
    c_h = {row["h_eff"] for row in capped}
    return {
        "count": len(unlimited),
        "unlimited": {
            "h_eff_unique_values": sorted(u_h),
            "vector_unique_count": len(u_v),
            "order_invariant_h_eff": len(u_h) == 1,
            "order_invariant_vector": len(u_v) == 1,
        },
        "capacity_2_lru": {
            "h_eff_unique_values": sorted(c_h),
            "order_invariant_h_eff": len(c_h) == 1,
        },
        "rows": unlimited,
    }


def ski_rental_ratio_rows(build=BUILD, rent=RENT):
    """Classic unknown-horizon competitive ratios against clairvoyant buy-or-rent."""
    rows = []
    worst = 0
    for horizon in range(1, 13):
        seq = (0,) * horizon
        online = simulate(seq, ski_rental_factory())
        clairvoyant = simulate(seq, analytic_threshold)
        online_scalar = online.vector[0] + online.vector[1] + online.vector[2]
        off_scalar = clairvoyant.vector[0] + clairvoyant.vector[1] + clairvoyant.vector[2]
        # Competitive ratio is reported on the summed toy units only as a parent
        # diagnostic; the raw vectors remain the published object.
        ratio_num, ratio_den = online_scalar, off_scalar
        worst = max(worst, ratio_num / ratio_den if ratio_den else 0)
        rows.append({
            "horizon": horizon,
            "online": as_dict(online.vector),
            "clairvoyant": as_dict(clairvoyant.vector),
            "h_eff_online": online.h_eff,
            "h_eff_clairvoyant": clairvoyant.h_eff,
            "summed_unit_ratio_numerator": ratio_num,
            "summed_unit_ratio_denominator": ratio_den,
            "pareto": price_halfspaces(online.vector, clairvoyant.vector),
        })
    return {"rows": rows, "worst_summed_unit_ratio": worst, "classic_bound": 2.0}


def stopping_study():
    states = ("h0", "h1")
    actions = ("go", "wait")
    common = {"h0": frozenset({"go"}), "h1": frozenset({"go"})}
    split = {"h0": frozenset({"go"}), "h1": frozenset({"wait"})}
    common_policy = probe_policy(states, common, actions)
    split_policy = probe_policy(states, split, actions)
    identify_always_common = cost(probe=PROBE, act=ACT_OK)
    values_common, policy_common = finite_probe_dp(ACT_OK, PROBE, ACT_OK)
    values_split, policy_split = finite_probe_dp(ACT_WRONG, PROBE, ACT_OK)
    return {
        "common_action": {
            "gamma": sorted(common_actions(states, common)),
            "policy": {k: v for k, v in common_policy.items() if k != "vector"}
            | {"vector": as_dict(common_policy["vector"])},
            "identify_always": as_dict(identify_always_common),
            "early_exit_saves_probe": common_policy["vector"][3] < identify_always_common[3],
            "dp_policy_budget_1": policy_common[1],
            "dp_values": values_common,
        },
        "split_action": {
            "gamma": sorted(common_actions(states, split)),
            "policy": {k: v for k, v in split_policy.items() if k != "vector"}
            | {"vector": as_dict(split_policy["vector"])},
            "dp_policy_budget_1": policy_split[1],
            "dp_values": values_split,
        },
    }


def residual_after_exact_parents(sequence):
    comparison = compare_parents(sequence)
    dp_front = comparison.get("exact_dp_pareto") or []
    if not dp_front:
        return {"status": "CANNOT_CHECK_DP_WITH_LIFECYCLE"}
    analytic = comparison["parents"]["analytic_threshold"]
    on_front = any(row["vector"] == analytic["vector"] for row in dp_front)
    return {
        "analytic_on_dp_pareto": on_front,
        "dp_pareto_size": len(dp_front),
        "dp_matches_analytic_vector": on_front,
        "dp_matches_analytic_h_eff": any(
            row["vector"] == analytic["vector"] and row["h_eff"] == analytic["h_eff"]
            for row in dp_front
        ),
        "best_static_pareto": comparison["pareto"],
        "selector_residual_after_analytic": 0 if on_front else "NONEMPTY",
    }


def terminals(report):
    stopping = report["g4_3"]["common_action_stopping"]
    residual = report["g4_3"]["residual_known_sequence"]
    ski = report["g4_3"]["ski_rental"]
    prices = report["g4_2"]["parents_on_unique_then_repeat"]["rent_vs_buy_prices"]
    buy_h = [row["h_eff_always_buy"] for row in report["g4_2"]["reuse_density"]]
    declared = []
    if residual["dp_matches_analytic_vector"]:
        declared.append("EXACT_META_POLICY_SUFFICIENT")
        declared.append("LEARNED_ROUTER_NOT_NEEDED")
        declared.append("PARENT_SUFFICIENT")
    if stopping["common_action"]["early_exit_saves_probe"]:
        declared.append("EXACT_EARLY_EXIT_VALUE_SUPPORTED")
    if prices["pareto_incomparable"]:
        declared.append("PRICE_REGIME_ONLY")
    declared.append("CANNOT_CHECK_UNMERGED_PR154_SEMANTIC_LIFETIME")
    declared.append("CANNOT_CHECK_PRODUCTION_OCM_LIFETIME")
    if ski["worst_summed_unit_ratio"] > 2.0 + 1e-12:
        raise AssertionError("ski-rental exceeded classic competitive bound on summed units")
    if buy_h != sorted(buy_h, reverse=True):
        raise AssertionError("always-buy H_eff must not rise as unique demand rises")
    return declared


def build_report():
    families = frozen_sequences()
    mixed = families["unique_then_repeat"]
    constant = families["constant"]
    report = {
        "schema": "ocm.g4-horizon-exact.v1",
        "study": "G4.2/G4.3 effective reusable horizon; exact parents; no ML",
        "pr154_disposition": {
            "branch": PR154_BRANCH,
            "head": PR154_HEAD,
            "pr": 154,
            "merged": False,
            "covers": [
                "horizon 1..142 iid static semantic vs inverse",
                "query-order permutations (8 seeds)",
                "reset/restart intervals 1,2,4,8,16,32,64,142",
                "checkpoint/replay intervals 4,8,16,32,64,71",
                "raw phase coordinates and Pareto band H=4..8",
                "static exact strategies",
                "analytic expected-cost threshold",
                "finite DP oracle residual bound",
                "online switch / investment parents on that lifetime",
            ],
            "missing_independent_axes": [
                "reuse density as a swept coordinate",
                "drift/invalidation distinct from full reset",
                "revision frequency as a swept coordinate",
            ],
            "this_capsule": "fills missing axes on a finite noiseless toy; does not rerun the 142-target engines",
        },
        "model": {
            "items": list(ITEMS),
            "rent": RENT,
            "build": BUILD,
            "hit": HIT,
            "probe": PROBE,
            "coordinates": list(COORDINATES),
            "h_eff": "count of queries served from cache that survived since admission",
            "break_even_remaining_strict": 4,
            "analytic_buy_rule": "buy iff remaining*(rent-hit) > build",
        },
        "g4_2": {
            "horizon_constant_always_buy": horizon_rows(constant, "always_buy", always_buy),
            "horizon_constant_ski_rental": horizon_rows(constant, "ski_rental", ski_rental_factory),
            "reuse_density": density_sweep(),
            "query_order": {k: v for k, v in order_sweep().items() if k != "rows"},
            "lifecycle": lifecycle_sweep(mixed),
            "parents_on_unique_then_repeat": compare_parents(mixed),
            "parents_on_constant": compare_parents(constant),
        },
        "g4_3": {
            "static_and_analytic": compare_parents(mixed),
            "ski_rental": ski_rental_ratio_rows(),
            "cache_admission": cache_admission_rows(mixed, capacity=2),
            "common_action_stopping": stopping_study(),
            "residual_known_sequence": residual_after_exact_parents(mixed),
            "residual_constant": residual_after_exact_parents(constant),
        },
        "claim_boundary": {
            "ml_authorized": False,
            "scalarization": False,
            "production_ocm": False,
            "pr154_merged": False,
            "protected_143_run": False,
        },
    }
    report["terminals"] = terminals(report)
    report["g4_boxes"] = {
        "G4.2": {
            "sweep_horizon": "CHECKED_TOY_AND_CITED_PR154",
            "sweep_reuse_density": "CHECKED_TOY",
            "sweep_query_order": "CHECKED_TOY_AND_CITED_PR154",
            "sweep_drift": "CHECKED_TOY",
            "sweep_reset_restart": "CHECKED_TOY_AND_CITED_PR154",
            "sweep_revision_frequency": "CHECKED_TOY",
            "sweep_checkpoint_replay": "CHECKED_TOY_AND_CITED_PR154",
            "raw_cost_vector": "CHECKED",
        },
        "G4.3": {
            "static_exact_strategy": "CHECKED",
            "analytic_threshold": "CHECKED",
            "rent_vs_buy_ski_rental": "CHECKED",
            "cache_admission_parent": "CHECKED",
            "common_action_stopping": "CHECKED",
            "exact_decision_region": "CHECKED",
            "exact_finite_state_dp": "CHECKED",
            "cost_aware_probe_policy": "CHECKED",
            "price_regime_pareto": "CHECKED",
        },
        "G4.4_learned_routing": "NOT_UNLOCKED",
    }
    return report


def write_report(path=None):
    path = Path(path) if path else ROOT / "SUMMARY.json"
    report = build_report()
    path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report, path


def main():
    report, path = write_report()
    print(json.dumps({
        "path": str(path),
        "terminals": report["terminals"],
        "g4_boxes": report["g4_boxes"],
        "h_eff_constant_buy": [row["h_eff"] for row in report["g4_2"]["horizon_constant_always_buy"]],
        "pareto_mixed": report["g4_2"]["parents_on_unique_then_repeat"]["pareto"],
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
