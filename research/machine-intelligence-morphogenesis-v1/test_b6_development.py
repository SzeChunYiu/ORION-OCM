"""RV-377-180 (B6): the two additive parameters of b1.search leave the committed default path byte-identical, and the
seeding/matching machinery of b6_development does what the freeze says."""
import hashlib
import json

from gmi_microscope import b1, b6_development as b6, ecology, morph

# hash of the archive produced by the COMMITTED b1.search (origin/main at 99e4db13, before the seed_population/trace
# parameters existed) on E_smooth3, seed 0, 200 evaluations, computed on billy-old with the committed file; see the
# freeze document. If this changes, the default path is no longer the committed search.
PINNED_DEFAULT_200 = "11f0c9cd24b7b674"


def archive_digest(archive, n, failed, tries):
    rows = sorted((list(k), v[0], morph.fingerprint(v[1]), v[3]) for k, v in archive.items())
    return hashlib.sha256(json.dumps({"rows": rows, "n": n, "failed": failed, "tries": tries}, sort_keys=True).encode()).hexdigest()[:16]


def _run(**kw):
    target = ecology.target_of(ecology.REGISTRY["E_smooth3"])
    archive, n, failed, tries, hist = b1.search(target, 0, 200, **kw)
    return archive_digest(archive, n, failed, tries), archive, n


def test_default_search_path_is_byte_identical():
    assert _run()[0] == PINNED_DEFAULT_200


def test_trace_does_not_change_the_search():
    tr = []
    d, archive, n = _run(trace=tr)
    assert d == PINNED_DEFAULT_200
    assert all(r["capability"] >= b1.THETA for r in tr)
    assert all(1 <= r["n_eval"] <= n for r in tr)


def test_seed_population_is_placed_first_and_charged():
    target = ecology.target_of(ecology.REGISTRY["E_smooth3"])
    seeds = [b6.zoo.hamming_knn(3), b6.zoo.exemplar_table(4)]
    tr = []
    archive, n, failed, tries, _ = b1.search(target, 0, len(seeds), seed_population=seeds, trace=tr)
    assert n == len(seeds)
    fps = {morph.fingerprint(v[1]) for v in archive.values()}
    assert morph.fingerprint(seeds[0]) in fps or morph.fingerprint(seeds[1]) in fps
    assert all(r["origin"][0] == "seed" for r in tr)


def test_matched_populations_have_identical_carrier_histograms():
    mk = lambda caps: {"cells": {f"c{i}": {"capability": c, "carrier_raw": k, "fingerprint": f"f{i}", "genotype": "{}", "n_nodes": 5}
                                 for i, (k, c) in enumerate(caps)}}
    a = mk([("TABLE", 0.9), ("TABLE", 0.8), ("DENSE", 0.7), ("KVSTORE", 0.6)])
    t = mk([("TABLE", 0.5), ("DENSE", 0.4), ("DENSE", 0.3), ("PROGRAM", 0.2)])
    cont, twin, k, sizes = b6.matched_populations(a, t)
    assert k == {"NONE": 0, "DENSE": 1, "TABLE": 1, "KVSTORE": 0, "PROGRAM": 0}
    assert [v["carrier_raw"] for v in cont] == [v["carrier_raw"] for v in twin] == ["DENSE", "TABLE"]
    assert cont[1]["capability"] == 0.9 and twin[1]["capability"] == 0.5   # top by capability


def test_random_table_specs_are_deterministic_and_structure_free():
    a, b = b6.spec_of("E_rnd0"), b6.spec_of("E_rnd0")
    assert a == b and a["family"] == "table" and len(a["table"]) == 16
    assert b6.spec_of("E_rnd1") != a and b6.spec_of("E_twin0") != a


def test_rule42_extractor_validates_on_known_rows():
    assert b6.validate_extractor()["valid"]
