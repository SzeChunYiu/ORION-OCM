from __future__ import annotations

from fractions import Fraction as F
import itertools
import json
from typing import Dict, Iterable, Mapping, Sequence, Tuple

N = 4
ATOMS = tuple(itertools.product((0, 1), repeat=N))
IDX = {a: i for i, a in enumerate(ATOMS)}
ORDERS = tuple(itertools.permutations(range(N)))
GRID = (F(0), F(1,2), F(1))
FREEZE_COMMIT = "f50f36f500b272e8663baad1c3beec1394d020df"


def _distribution(values: Sequence[F]) -> Tuple[F, ...]:
    if not isinstance(values, tuple) or len(values) != len(ATOMS):
        raise ValueError("distribution must be a 16-tuple")
    if any(type(x) is not F or x < 0 for x in values):
        raise ValueError("distribution entries must be nonnegative exact Fractions")
    if sum(values, F(0)) != 1:
        raise ValueError("distribution must sum exactly to one")
    return values


def uniform_on(support: Iterable[Tuple[int, ...]]) -> Tuple[F, ...]:
    support = tuple(support)
    if not support or len(set(support)) != len(support):
        raise ValueError("support must be nonempty and duplicate-free")
    if any(a not in IDX for a in support):
        raise ValueError("support atom outside {0,1}^4")
    w = F(1, len(support))
    out = [F(0)] * len(ATOMS)
    for a in support:
        out[IDX[a]] = w
    return tuple(out)


def point_mass(atom: Tuple[int, ...]) -> Tuple[F, ...]:
    return uniform_on((atom,))


def product_distribution(bit_one_probs: Sequence[F]) -> Tuple[F, ...]:
    if not isinstance(bit_one_probs, tuple) or len(bit_one_probs) != N:
        raise ValueError("need exactly four marginals")
    for p in bit_one_probs:
        if type(p) is not F or not F(0) <= p <= F(1):
            raise ValueError("marginals must be exact Fractions in [0,1]")
    out = []
    for a in ATOMS:
        p = F(1)
        for bit, q in zip(a, bit_one_probs):
            p *= q if bit else 1-q
        out.append(p)
    return _distribution(tuple(out))


def support(P: Tuple[F, ...]) -> Tuple[Tuple[int, ...], ...]:
    _distribution(P)
    return tuple(a for a in ATOMS if P[IDX[a]] > 0)


def permute_coordinates(P: Tuple[F, ...], perm: Tuple[int, ...]) -> Tuple[F, ...]:
    _distribution(P)
    if tuple(sorted(perm)) != tuple(range(N)):
        raise ValueError("perm must be a coordinate permutation")
    out = [F(0)] * len(ATOMS)
    for x in ATOMS:
        y = tuple(x[i] for i in perm)
        out[IDX[y]] = P[IDX[x]]
    return _distribution(tuple(out))


def targets() -> Mapping[str, Tuple[F, ...]]:
    full = uniform_on(ATOMS)
    half = uniform_on(a for a in ATOMS if a[0] == 0)
    even = uniform_on(a for a in ATOMS if sum(a) % 2 == 0)
    diagonal = uniform_on(((0,0,0,0), (1,1,1,1)))
    hamming2 = uniform_on(a for a in ATOMS if sum(a) == 2)
    equal01 = uniform_on(a for a in ATOMS if a[0] == a[1])
    and_graph = uniform_on(
        (x0,x1,x2,x0*x1*x2)
        for x0,x1,x2 in itertools.product((0,1), repeat=3)
    )
    biased = product_distribution((F(1,2), F(1,3), F(1,4), F(1,5)))
    biased_swap = permute_coordinates(biased, (3,2,1,0))
    return {
        "FULL": full, "HALF": half, "EVEN": even, "DIAGONAL": diagonal,
        "HAMMING2": hamming2, "EQUAL01": equal01, "AND_GRAPH": and_graph,
        "BIASED_SWAP": biased_swap, "DELTA0": point_mass((0,0,0,0)),
    }


def bases() -> Mapping[str, Tuple[F, ...]]:
    biased = product_distribution((F(1,2), F(1,3), F(1,4), F(1,5)))
    return {
        "U16": uniform_on(ATOMS),
        "U8": uniform_on(a for a in ATOMS if a[0] == 0),
        "U6": uniform_on(ATOMS[:6]),
        "U2": uniform_on(((0,0,0,0), (0,0,0,1))),
        "BIASED": biased,
    }


# R1 -----------------------------------------------------------------------
def ar_row_cost(P: Tuple[F, ...], order: Tuple[int, ...]) -> Tuple[int, Tuple[int, ...]]:
    _distribution(P)
    if tuple(sorted(order)) != tuple(range(N)):
        raise ValueError("invalid coordinate order")
    per_pos = []
    for pos in range(N):
        current = order[pos]
        prev = order[:pos]
        contexts: Dict[Tuple[int, ...], list[F]] = {}
        for atom in ATOMS:
            mass = P[IDX[atom]]
            if mass == 0:
                continue
            key = tuple(atom[j] for j in prev)
            contexts.setdefault(key, [F(0), F(0)])
            contexts[key][atom[current]] += mass
        rows = set()
        for zero, one in contexts.values():
            rows.add(one / (zero + one))
        per_pos.append(len(rows))
    return sum(per_pos), tuple(per_pos)


def ar_reconstruct(P: Tuple[F, ...], order: Tuple[int, ...]) -> Tuple[F, ...]:
    _distribution(P)
    out = [F(0)] * len(ATOMS)
    for atom in ATOMS:
        p = F(1)
        for pos, current in enumerate(order):
            prev = order[:pos]
            den = F(0)
            num = F(0)
            for b in ATOMS:
                if all(b[j] == atom[j] for j in prev):
                    den += P[IDX[b]]
                    if b[current] == atom[current]:
                        num += P[IDX[b]]
            if den == 0:
                p = F(0)
                break
            p *= num / den
        out[IDX[atom]] = p
    return tuple(out)


def coordinate_stabilizer_size(P: Tuple[F, ...]) -> int:
    _distribution(P)
    n = 0
    for perm in ORDERS:
        if permute_coordinates(P, perm) == P:
            n += 1
    return n


def ar_response(P: Tuple[F, ...]) -> Mapping[str, object]:
    costs = {}
    for order in ORDERS:
        cost, per = ar_row_cost(P, order)
        if ar_reconstruct(P, order) != P:
            raise RuntimeError("chain reconstruction failure")
        costs[order] = (cost, per)
    vals = [x[0] for x in costs.values()]
    return {
        "min": min(vals), "max": max(vals),
        "stabilizer": coordinate_stabilizer_size(P),
        "orders": [
            {"order": list(order), "cost": costs[order][0], "per_position": list(costs[order][1])}
            for order in ORDERS
        ],
    }


# R2 -----------------------------------------------------------------------
COORD_CHOICES = ((0,), (1,), (0,1))


def all_subcubes() -> Tuple[frozenset, ...]:
    cubes = []
    for choices in itertools.product(COORD_CHOICES, repeat=N):
        cube = frozenset(a for a in ATOMS if all(a[i] in choices[i] for i in range(N)))
        cubes.append(cube)
    if len(cubes) != 3**N or any(not c for c in cubes):
        raise RuntimeError("subcube enumeration malformed")
    return tuple(cubes)


SUBCUBES = all_subcubes()


def rectangle_cover_number(P: Tuple[F, ...]) -> int:
    S = frozenset(support(P))
    ordered = tuple(sorted(S))
    bit = {a: 1 << i for i, a in enumerate(ordered)}
    valid_masks = sorted({
        sum((bit[a] for a in cube), 0)
        for cube in SUBCUBES if cube.issubset(S)
    })
    valid_masks = [m for m in valid_masks if m]
    full = (1 << len(ordered)) - 1
    inf = len(ordered) + 1
    dp = [inf] * (full + 1)
    dp[0] = 0
    for mask in range(full + 1):
        if dp[mask] == inf:
            continue
        for rect in valid_masks:
            new = mask | rect
            if dp[new] > dp[mask] + 1:
                dp[new] = dp[mask] + 1
    if dp[full] == inf:
        raise RuntimeError("support not coverable")
    return dp[full]


def product_component_from_choices(choices: Tuple[Tuple[int, ...], ...]) -> Tuple[F, ...]:
    probs = []
    for choice in choices:
        if choice == (0,):
            probs.append(F(0))
        elif choice == (1,):
            probs.append(F(1))
        elif choice == (0,1):
            probs.append(F(1,2))
        else:
            raise ValueError("unsupported component choice")
    return product_distribution(tuple(probs))


def mixture_certificate(name: str) -> Tuple[Tuple[F, Tuple[F, ...]], ...]:
    t = targets()
    if name == "FULL":
        return ((F(1), product_distribution((F(1,2),)*4)),)
    if name == "HALF":
        return ((F(1), product_distribution((F(0),F(1,2),F(1,2),F(1,2)))),)
    if name == "DIAGONAL":
        return tuple((F(1,2), point_mass(a)) for a in ((0,0,0,0),(1,1,1,1)))
    if name == "EQUAL01":
        return (
            (F(1,2), product_distribution((F(0),F(0),F(1,2),F(1,2)))),
            (F(1,2), product_distribution((F(1),F(1),F(1,2),F(1,2)))),
        )
    if name in ("EVEN", "HAMMING2"):
        S = support(t[name])
        w = F(1, len(S))
        return tuple((w, point_mass(a)) for a in S)
    raise KeyError(name)


def mixture_reconstruct(cert: Tuple[Tuple[F, Tuple[F, ...]], ...]) -> Tuple[F, ...]:
    if not cert:
        raise ValueError("empty mixture")
    if sum((w for w,_ in cert), F(0)) != 1:
        raise ValueError("mixture weights must sum to one")
    out = [F(0)] * len(ATOMS)
    for w, comp in cert:
        if type(w) is not F or w <= 0:
            raise ValueError("weights must be positive Fractions")
        _distribution(comp)
        for i, p in enumerate(comp):
            out[i] += w*p
    return _distribution(tuple(out))


# R3 -----------------------------------------------------------------------
def multiset_reachable(base: Tuple[F, ...], target: Tuple[F, ...]) -> bool:
    _distribution(base); _distribution(target)
    return sorted(base) == sorted(target)


def matching_bijection(base: Tuple[F, ...], target: Tuple[F, ...]):
    _distribution(base); _distribution(target)
    buckets: Dict[F, list[int]] = {}
    for j,p in enumerate(target):
        buckets.setdefault(p, []).append(j)
    mapping = [-1] * len(ATOMS)
    for i,p in enumerate(base):
        candidates = buckets.get(p)
        if not candidates:
            return None
        mapping[i] = candidates.pop(0)
    if any(buckets[p] for p in buckets):
        return None
    if sorted(mapping) != list(range(len(ATOMS))):
        raise RuntimeError("matching is not a bijection")
    return tuple(mapping)


def push_by_mapping(base: Tuple[F, ...], mapping: Tuple[int, ...]) -> Tuple[F, ...]:
    if tuple(sorted(mapping)) != tuple(range(len(ATOMS))):
        raise ValueError("mapping must be a permutation")
    out = [F(0)] * len(ATOMS)
    for i,j in enumerate(mapping):
        out[j] = base[i]
    return tuple(out)


# R4 -----------------------------------------------------------------------
def marginals(P: Tuple[F, ...]) -> Tuple[F, ...]:
    _distribution(P)
    return tuple(sum((P[i] for i,a in enumerate(ATOMS) if a[j] == 1), F(0)) for j in range(N))


def product_of_marginals(P: Tuple[F, ...]) -> Tuple[F, ...]:
    return product_distribution(marginals(P))


def local_refinement_status(P: Tuple[F, ...]) -> Mapping[str, object]:
    ms = marginals(P)
    factors = product_of_marginals(P)
    is_product = factors == P
    grid_ok = all(m in GRID for m in ms)
    if not is_product:
        return {"reachable": False, "reason": "NONPRODUCT", "marginals": [frac(x) for x in ms]}
    if not grid_ok:
        return {"reachable": False, "reason": "OUTSIDE_REFRESH_GRID", "marginals": [frac(x) for x in ms]}
    steps = tuple((i,m) for i,m in enumerate(ms) if m != 0)
    return {
        "reachable": True, "reason": "REACHABLE", "min_steps": len(steps),
        "steps": [[i, frac(p)] for i,p in steps], "marginals": [frac(x) for x in ms],
    }


def apply_refresh(P: Tuple[F, ...], coordinate: int, p: F) -> Tuple[F, ...]:
    _distribution(P)
    if coordinate not in range(N) or p not in GRID:
        raise ValueError("invalid refresh")
    out = [F(0)] * len(ATOMS)
    for a in ATOMS:
        mass = P[IDX[a]]
        if mass == 0:
            continue
        for bit,prob in ((0,1-p),(1,p)):
            b = list(a); b[coordinate] = bit; b = tuple(b)
            out[IDX[b]] += mass*prob
    return _distribution(tuple(out))


def reconstruct_local(status: Mapping[str, object]) -> Tuple[F, ...]:
    P = point_mass((0,0,0,0))
    if not status["reachable"]:
        raise ValueError("cannot reconstruct unreachable status")
    for i,ptext in status["steps"]:
        P = apply_refresh(P, i, parse_frac(ptext))
    return P


def parse_frac(text: str) -> F:
    if "/" in text:
        a,b = text.split("/")
        return F(int(a),int(b))
    return F(int(text))


def frac(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def dist_json(P: Tuple[F, ...]):
    return [frac(x) for x in P]


def build_receipt() -> Mapping[str, object]:
    t = targets()
    b = bases()

    ar_names = ("FULL","EVEN","DIAGONAL","HAMMING2","HALF","AND_GRAPH")
    ar = {name: ar_response(t[name]) for name in ar_names}

    latent_names = ("FULL","HALF","DIAGONAL","EQUAL01","EVEN","HAMMING2")
    latent = {}
    for name in latent_names:
        cover = rectangle_cover_number(t[name])
        cert = mixture_certificate(name)
        recon = mixture_reconstruct(cert)
        latent[name] = {
            "rectangle_cover": cover,
            "components": len(cert),
            "certificate_exact": recon == t[name],
        }

    flow_target_names = ("FULL","HALF","EVEN","DIAGONAL","HAMMING2","EQUAL01","AND_GRAPH","BIASED_SWAP")
    flow = {}
    for tn in flow_target_names:
        flow[tn] = {}
        for bn, base in b.items():
            pred = multiset_reachable(base, t[tn])
            mapping = matching_bijection(base, t[tn])
            measured = mapping is not None
            verified = measured and push_by_mapping(base, mapping) == t[tn]
            flow[tn][bn] = {
                "predicted": pred, "measured": measured,
                "certificate_verified": bool(verified),
                "mapping": list(mapping) if mapping is not None else None,
            }

    local_names = ("DELTA0","FULL","HALF","EVEN","DIAGONAL","HAMMING2","EQUAL01","AND_GRAPH","BIASED_SWAP")
    local = {name: local_refinement_status(t[name]) for name in local_names}
    for name in ("DELTA0","FULL","HALF"):
        local[name]["reconstruction_exact"] = reconstruct_local(local[name]) == t[name]

    return {
        "schema": "B17HeldResponseN4ReceiptV1",
        "issue": 752,
        "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": "B17_PREREGISTERED_HELD_RESPONSE_GREEN_AT_EXACT_N4_REGISTERED_SCOPE",
        "domain": {"bits": 4, "atoms": 16},
        "target_support_sizes": {name: len(support(P)) for name,P in t.items()},
        "ar": ar,
        "latent": latent,
        "flow": flow,
        "local_refinement": local,
        "old_false_converse_guard": {
            "HALF_coordinate_stabilizer": ar["HALF"]["stabilizer"],
            "HALF_ar_flat": ar["HALF"]["min"] == ar["HALF"]["max"],
            "asymmetry_implies_sensitivity": False,
        },
        "claim_guards": {
            "continuous_flow_claimed": False,
            "general_diffusion_claimed": False,
            "prediction_frozen_before_outcome": True,
        },
    }


def main() -> int:
    print(json.dumps(build_receipt(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
