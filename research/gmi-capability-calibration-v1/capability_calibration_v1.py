from __future__ import annotations

from fractions import Fraction as F
from hashlib import sha1, sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from json import dumps, loads
from math import comb
from pathlib import Path

N = 128
SAMPLE_N = 64
DELTA = F(1, 80)
DELTA_TOTAL = F(1, 20)
EPSILON = F(1, 20)
FREEZE_COMMIT = "f46d2b3930b980f85d2d0143cba20b39f396b396"
POPULATION_COMMIT = "68d5101b26bb095546030e1e37a994f74e62fe15"
SAMPLE_COMMIT = "f528ddcc183d28ae5cd91a98a9c1a860ddd3ba8d"
PINNED_PREDICTOR_BLOB = "937b91f6a3787ff04c2b5209c81d249518406859"
CLAIM = "EXACT_FINITE_POPULATION_CAPABILITY_ERROR_CALIBRATION_AT_REGISTERED_SCOPE"
PASS = "CALIBRATED_AT_REGISTERED_FINITE_POPULATION"
FAIL = "CANNOT_CERTIFY_ERROR_RATE"
NO_DETERMINATE = "CANNOT_CALIBRATE_NO_DETERMINATE_CELLS"
AXES = ("memory_margin", "planning_margin", "communication_margin", "routing_margin", "verification_margin")
TARGETS = ("memory_exact", "planning_exact", "coordination_exact", "verified_tool_exact")
FORBIDDEN_POPULATION_KEYS = {"oracle", "truth", "label", "error", "correct", "prediction", "predicted", "outcome", "capabilities"}
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
POPULATION_PATH = HERE / "POPULATION_MANIFEST_V1.json"
SAMPLE_PATH = HERE / "SAMPLE_MANIFEST_V1.json"
PREDICTOR_PATH = REPO / "research/gmi-capability-predictor-dev-v1/dev_predictor_v1.py"


def frac_text(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def git_blob_sha(data):
    return sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def canonical_point_json(point):
    return dumps({a: int(point[a]) for a in AXES}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def cell_id(target, point):
    return "cell_" + sha256((target + "\n" + canonical_point_json(point)).encode()).hexdigest()


def _load_json(path):
    return loads(path.read_text())


def _compact_json_digest(obj):
    return sha256(dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def reconstruct_population(manifest):
    if manifest.get("freeze_commit") != FREEZE_COMMIT:
        raise ValueError("population freeze authority mismatch")
    if manifest.get("population_size_per_coordinate") != N or manifest.get("selection_per_side") != 64:
        raise ValueError("population size contract mismatch")
    if tuple(manifest.get("axes", ())) != AXES or tuple(manifest.get("coordinates", ())) != TARGETS:
        raise ValueError("population registry mismatch")
    if manifest.get("oracle_fields_present") is not False:
        raise ValueError("population manifest must be result blind")
    keys = set()
    def collect(obj):
        if isinstance(obj, dict):
            keys.update(str(k).lower() for k in obj)
            for v in obj.values():
                collect(v)
        elif isinstance(obj, list):
            for v in obj:
                collect(v)
    collect(manifest)
    bad = keys & FORBIDDEN_POPULATION_KEYS
    if bad:
        raise ValueError(f"population manifest contains forbidden scored fields: {sorted(bad)}")
    result = {}
    generator = manifest["generator_spec"]
    for target in TARGETS:
        selected = []
        for side in ("positive_side", "negative_side"):
            spec = generator[target][side]
            candidates = [dict(zip(AXES, vals)) for vals in product(*(tuple(spec[a]) for a in AXES))]
            candidates.sort(key=lambda p: tuple(p[a] for a in AXES))
            selected.extend(candidates[:64])
        by_tuple = {tuple(p[a] for a in AXES): p for p in selected}
        if len(by_tuple) != N:
            raise ValueError(f"{target} population has duplicate points")
        points = [by_tuple[k] for k in sorted(by_tuple)]
        entries = tuple((cell_id(target, p), p) for p in points)
        ids = sorted(cid for cid, _ in entries)
        if _compact_json_digest(ids) != manifest["coordinate_population_id_digests_sha256"][target]:
            raise ValueError(f"{target} population ID digest mismatch")
        if any(all(p[a] in (-1, 0, 1) for a in AXES) for _, p in entries):
            raise ValueError("audit point leaked into development grid")
        result[target] = entries
    all_ids = sorted(cid for rows in result.values() for cid, _ in rows)
    if _compact_json_digest(all_ids) != manifest["all_sorted_population_ids_digest_sha256"]:
        raise ValueError("all-population ID digest mismatch")
    return result


def unrank_combination(items, k, rank):
    n = len(items)
    if not (0 <= rank < comb(n, k)):
        raise ValueError("combination rank out of range")
    out, start, left, r = [], 0, k, rank
    while left:
        for i in range(start, n - left + 1):
            count = comb(n - i - 1, left - 1) if left > 1 else 1
            if r < count:
                out.append(items[i]); start = i + 1; left -= 1; break
            r -= count
        else:
            raise RuntimeError("combination unranking failed")
    return tuple(out)


def validate_sample(populations, master):
    if master.get("freeze_commit") != FREEZE_COMMIT or master.get("population_commit") != POPULATION_COMMIT:
        raise ValueError("sample authority mismatch")
    if master.get("N") != N or master.get("n") != SAMPLE_N or tuple(master.get("coordinates", ())) != TARGETS:
        raise ValueError("sample registry mismatch")
    if master.get("scored_fields_present") is not False:
        raise ValueError("sample manifest contaminated by scored fields")
    M, B = comb(N, SAMPLE_N), 1 << 256
    q, L = B // M, (B // M) * M
    if int(master["combination_count_decimal"]) != M or int(master["entropy_space_decimal"]) != B:
        raise ValueError("sample combinatorics mismatch")
    if int(master["acceptance_quotient_decimal"]) != q or int(master["acceptance_limit_exclusive_decimal"]) != L:
        raise ValueError("sample rejection threshold mismatch")
    result = {}
    for target in TARGETS:
        meta = master["coordinate_sample_files"][target]
        raw = (REPO / meta["path"]).read_bytes()
        if sha256(raw).hexdigest() != meta["content_sha256"] or git_blob_sha(raw) != meta["git_blob_sha"]:
            raise ValueError(f"{target} sample digest mismatch")
        sample = loads(raw)
        if sample.get("coordinate") != target or sample.get("freeze_commit") != FREEZE_COMMIT or sample.get("population_commit") != POPULATION_COMMIT:
            raise ValueError(f"{target} sample metadata mismatch")
        blocks, idx = sample.get("entropy_blocks_hex"), sample.get("accepted_block_index")
        if not isinstance(blocks, list) or not isinstance(idx, int) or not (0 <= idx < len(blocks)):
            raise ValueError(f"{target} entropy transcript malformed")
        for i, block in enumerate(blocks):
            if not isinstance(block, str) or len(block) != 64:
                raise ValueError(f"{target} entropy block malformed")
            z_i = int(block, 16)
            if i < idx and z_i < L:
                raise ValueError(f"{target} rejected an acceptable block")
            if i == idx and z_i >= L:
                raise ValueError(f"{target} accepted an invalid block")
        z = int(blocks[idx], 16)
        if z != int(sample["accepted_integer_decimal"]):
            raise ValueError(f"{target} accepted integer mismatch")
        rank = z % M
        if rank != int(sample["combination_rank_decimal"]):
            raise ValueError(f"{target} rank mismatch")
        expected = unrank_combination(sorted(cid for cid, _ in populations[target]), SAMPLE_N, rank)
        observed = tuple(sample.get("sampled_cell_ids", ()))
        if len(observed) != SAMPLE_N or len(set(observed)) != SAMPLE_N or observed != expected:
            raise ValueError(f"{target} sample does not exactly replay")
        result[target] = observed
    return result


def hypergeom_pmf(N_, K, n, x):
    if N_ < 1 or not (0 <= K <= N_) or not (0 <= n <= N_):
        raise ValueError("invalid hypergeometric parameters")
    if x < 0 or x > n or x > K or n - x > N_ - K:
        return F(0)
    return F(comb(K, x) * comb(N_ - K, n - x), comb(N_, n))


def hypergeom_cdf(N_, K, n, x):
    if x < 0:
        return F(0)
    return sum((hypergeom_pmf(N_, K, n, i) for i in range(min(x, n) + 1)), F(0))


def upper_error_count(N_, n, x, delta):
    if not (F(0) < delta < F(1)):
        raise ValueError("delta must lie in (0,1)")
    admissible = [K for K in range(N_ + 1) if hypergeom_cdf(N_, K, n, x) > delta]
    if not admissible:
        raise RuntimeError("upper bound unexpectedly undefined")
    return max(admissible)


def _load_predictor():
    raw = PREDICTOR_PATH.read_bytes()
    if git_blob_sha(raw) != PINNED_PREDICTOR_BLOB:
        raise ValueError("pinned predictor source identity changed")
    spec = spec_from_file_location("gmi_dev_predictor_v1_pinned", PREDICTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load pinned predictor")
    mod = module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def score_coordinates(populations, samples):
    mod = _load_predictor(); predictor = mod.fit_registered_development_predictor(); results = {}
    for target in TARGETS:
        by_id = {cid: p for cid, p in populations[target]}
        sample_errors = sample_abstentions = 0
        for cid in samples[target]:
            p = by_id[cid]; pred = predictor.predict_one(p, target)
            if pred == mod.CANNOT_IDENTIFY:
                sample_abstentions += 1; continue
            sample_errors += int(pred != mod.capability_oracle(p)[target])
        full_errors = full_abstentions = 0
        for _, p in populations[target]:
            pred = predictor.predict_one(p, target)
            if pred == mod.CANNOT_IDENTIFY:
                full_abstentions += 1; continue
            full_errors += int(pred != mod.capability_oracle(p)[target])
        if full_abstentions or sample_abstentions:
            U = rate = None; terminal = NO_DETERMINATE
        else:
            U = upper_error_count(N, SAMPLE_N, sample_errors, DELTA); rate = F(U, N)
            terminal = PASS if rate <= EPSILON else FAIL
        corrupt_errors = SAMPLE_N - sample_errors if sample_abstentions == 0 else None
        corrupt_U = upper_error_count(N, SAMPLE_N, corrupt_errors, DELTA) if corrupt_errors is not None else None
        corrupt_rate = F(corrupt_U, N) if corrupt_U is not None else None
        results[target] = {
            "population_size": N, "sample_size": SAMPLE_N,
            "determinate_population_count": N - full_abstentions,
            "sample_abstentions": sample_abstentions, "sample_errors": sample_errors,
            "upper_error_count": U, "upper_error_rate": frac_text(rate) if rate is not None else None,
            "terminal": terminal,
            "corrupted_control": {
                "sample_errors": corrupt_errors, "upper_error_count": corrupt_U,
                "upper_error_rate": frac_text(corrupt_rate) if corrupt_rate is not None else None,
                "terminal": PASS if corrupt_rate is not None and corrupt_rate <= EPSILON else FAIL,
            },
            "census": {
                "fixed_population_errors": full_errors,
                "fixed_population_error_rate": frac_text(F(full_errors, N)),
                "abstentions": full_abstentions,
                "certificate_covers_fixed_truth": U is not None and full_errors <= U,
            },
        }
    return results


def dependence_hostile():
    atoms = range(4); A, B = {0}, {1}
    sa = F(sum(i not in A for i in atoms), 4); sb = F(sum(i not in B for i in atoms), 4)
    simultaneous = F(sum(i not in A and i not in B for i in atoms), 4)
    product_shortcut = sa * sb; union_lower = 1 - F(len(A), 4) - F(len(B), 4)
    overlap = F(sum(i not in A for i in atoms), 4)
    return {
        "individual_success": [frac_text(sa), frac_text(sb)],
        "true_simultaneous_success_disjoint_failures": frac_text(simultaneous),
        "unjustified_independence_product": frac_text(product_shortcut),
        "union_bound_lower": frac_text(union_lower), "product_is_unsound": product_shortcut > simultaneous,
        "overlap_control_true_simultaneous": frac_text(overlap),
        "union_bound_can_be_conservative": overlap > union_lower,
    }


def _enumerated_all_K(N_, n):
    counts = [[0] * (n + 1) for _ in range(N_ + 1)]
    mask, limit = (1 << n) - 1, 1 << N_
    while mask < limit:
        x = 0; counts[0][0] += 1
        for K in range(1, N_ + 1):
            x += (mask >> (K - 1)) & 1; counts[K][x] += 1
        c = mask & -mask; r = mask + c; mask = (((r ^ mask) >> 2) // c) | r
    return tuple(tuple(row) for row in counts)


def exhaustive_certificate(max_N=20):
    deltas = (F(1,2), F(1,3), F(1,4), F(1,5), F(1,10), F(1,20), F(1,80))
    pc = cc = mc = vc = ic = pf = cf = mf = vf = inf = 0
    for N_ in range(1, max_N + 1):
        for n in range(1, N_ + 1):
            enum = _enumerated_all_K(N_, n); den = sum(enum[0])
            if any(sum(row) != den for row in enum):
                raise RuntimeError("independent enumeration denominator mismatch")
            for K in range(N_ + 1):
                running = 0
                for x in range(n + 1):
                    observed = F(enum[K][x], den); expected = hypergeom_pmf(N_, K, n, x); pc += 1
                    if observed != expected: pf += 1
                    running += enum[K][x]; cc += 1
                    if F(running, den) != hypergeom_cdf(N_, K, n, x): cf += 1
                for delta in deltas:
                    vc += 1
                    prob = sum((hypergeom_pmf(N_, K, n, x) for x in range(n + 1) if K <= upper_error_count(N_, n, x, delta)), F(0))
                    if prob < 1 - delta: vf += 1
            for x in range(n + 1):
                cdfs = [hypergeom_cdf(N_, K, n, x) for K in range(N_ + 1)]
                for a, b in zip(cdfs, cdfs[1:]):
                    mc += 1
                    if b > a: mf += 1
                for delta in deltas:
                    ic += 1; U = upper_error_count(N_, n, x, delta)
                    if hypergeom_cdf(N_, U, n, x) <= delta: inf += 1
                    if U < N_ and hypergeom_cdf(N_, U + 1, n, x) > delta: inf += 1
    return {
        "max_N": max_N, "delta_grid": [frac_text(d) for d in deltas],
        "pmf_cases": pc, "pmf_failures": pf, "cdf_cases": cc, "cdf_failures": cf,
        "monotonicity_cases": mc, "monotonicity_failures": mf,
        "coverage_cases": vc, "coverage_failures": vf,
        "inversion_cases": ic, "inversion_failures": inf,
        "all_green": not any((pf, cf, mf, vf, inf)),
    }


def build_receipt(max_exact_N=20):
    population_manifest = _load_json(POPULATION_PATH); sample_master = _load_json(SAMPLE_PATH)
    populations = reconstruct_population(population_manifest); samples = validate_sample(populations, sample_master)
    scored = score_coordinates(populations, samples)
    U = upper_error_count(N, SAMPLE_N, 0, DELTA); f6 = hypergeom_cdf(N, 6, SAMPLE_N, 0); f7 = hypergeom_cdf(N, 7, SAMPLE_N, 0)
    return {
        "schema": "CapabilityCalibrationResultV1", "issue": 764, "parent_issue": 602,
        "freeze_commit": FREEZE_COMMIT, "population_commit": POPULATION_COMMIT, "sample_commit": SAMPLE_COMMIT,
        "claim_ceiling": CLAIM,
        "constants": {"N": N, "n": SAMPLE_N, "delta_total": frac_text(DELTA_TOTAL), "delta_per_coordinate": frac_text(DELTA), "epsilon": frac_text(EPSILON), "simultaneous_confidence_lower": frac_text(1 - 4 * DELTA)},
        "sample_custody": {"validated": True, "sampling_algorithm": sample_master["sampling_algorithm"], "population_digest": sample_master["all_sorted_population_ids_digest_sha256"], "coordinate_sample_content_sha256": {t: sample_master["coordinate_sample_files"][t]["content_sha256"] for t in TARGETS}},
        "coordinates": scored,
        "numerical_control": {"x": 0, "upper_error_count": U, "upper_rate": frac_text(F(U, N)), "F_6_at_0": frac_text(f6), "F_7_at_0": frac_text(f7), "F_6_gt_delta": f6 > DELTA, "F_7_le_delta": f7 <= DELTA},
        "dependence_hostile": dependence_hostile(), "exact_certificate": exhaustive_certificate(max_exact_N),
        "forbidden_claims": ["PER_EXAMPLE_PROBABILITIES_CALIBRATED", "IID_GENERALIZATION", "REAL_WORLD_CAPABILITY_CALIBRATION", "G6_UNIVERSAL", "COMPLETE_GMI"],
    }


def main():
    print(dumps(build_receipt(), sort_keys=True, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
