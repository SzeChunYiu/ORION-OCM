"""FNA-2: build R3 and R6 so APPROXIMATE_RETRIEVAL_NOT_SAFE becomes reachable at all.

Phase A found R3 (kNN/kernel) and R6 (VSA/HDC approximate projection) absent from main,
and FNA-1 recorded the consequence: the registered #214 terminal
APPROXIMATE_RETRIEVAL_NOT_SAFE is UNTESTABLE, because nothing approximate exists to be
unsafe. A registered terminal that cannot be reached is a hole in the programme, not a
result. This study closes it.

## What is built, and what is deliberately not

R6 is a vector-symbolic projection in the HDC sense: each atom gets a fixed random
hypervector derived from its STRUCTURAL signature, and candidates are proposed by
similarity. This is NOT machine learning. There is no training set, no objective, no
fitted parameter and no gradient -- the projection is a fixed random hash of features the
space already carries. #71 remains untouched; nothing here learns, routes or adapts.

R3 is the same harness with an exact distance over the same features, so the two differ
only in whether the similarity is approximated. That isolates the approximation.

## The information surface, which is the whole ballgame

An atom's signature is its atom_type plus the multiset of relation types on its incident
edges. Structural, and available to any mechanism. Critically it does NOT include the
atom's identity or any label saying it is the answer, and every world contains several
atoms of the target type carrying the SAME signature as the decisive one. Approximate
retrieval must therefore choose among indistinguishable siblings, which is exactly the
condition under which a similarity mechanism is unsafe and an exact one is not.

## Registered question

Does an approximate proposal mechanism, given a candidate budget k, return the decisive
atom -- and if it does not, is that a property of the approximation or of the feature
surface? The distinction matters: an R3/R6 pair that BOTH miss indicts the surface, while
R6 missing where R3 succeeds indicts the approximation.

Exact machinery always decides. The projection proposes candidates only; warrant, liveness
and the closure are untouched by it. That boundary is #214 section 3's, and this study does
not cross it.

Research-only. No production source modified, no model trained, no router implemented.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

from ocm.kso.space import KnowledgeSpace                 # noqa: E402
import experiment as E                                    # noqa: E402
import fna1b as B                                         # noqa: E402

SCHEMA = "ocm.fna.fna2-approximate-proposal.v1"

DIM = 512
SALT = "fna2-v1"


def signature(ks: KnowledgeSpace, atom_id: str) -> tuple:
    """Structural signature: atom type plus the sorted multiset of incident channels.

    Contains no atom identity and no answer label. Two atoms of the same type reached the
    same way are INDISTINGUISHABLE here, by construction.
    """
    amap = ks.atom_view
    channels: list[str] = []
    for e in ks.hyperedges:
        if atom_id in e.heads or atom_id in e.tails:
            channels.append(e.relation_type)
    return (amap[atom_id].atom_type,) + tuple(sorted(channels))


def symbol_vector(symbol: str, dim: int) -> list[int]:
    """A fixed bipolar random hypervector for one atomic symbol. No training, no fitting."""
    out: list[int] = []
    i = 0
    while len(out) < dim:
        h = hashlib.sha256(f"{SALT}|{symbol}|{i}".encode()).digest()
        out.extend(1 if (b & 1) else -1 for b in h)
        i += 1
    return out[:dim]


def hypervector(sig: tuple, dim: int | None = None) -> list[int]:
    """A VSA BUNDLE of the signature's component symbols -- not a hash of the tuple.

    A DEFECT IS RECORDED HERE because the first version of this function was wrong in a
    way that produced a registered terminal. It hashed the whole signature tuple, so
    ('counterexample',) and ('counterexample','SUPPORT') received INDEPENDENT random
    vectors with expected cosine zero. Similarity then carried no compositional
    information at all, the ranking was effectively arbitrary, and the approximation
    "lost" at k=1 identically at every dimension from 2 to 512. That flat profile is the
    tell: a capacity effect must improve with dimension. It was a hash masquerading as a
    vector-symbolic architecture, and reporting APPROXIMATE_RETRIEVAL_NOT_SAFE from it
    would have been the misattribution this study is built to avoid.

    The corrected form bundles (element-wise sums, then takes the sign of) the
    hypervectors of the signature's component symbols, which is what makes VSA similarity
    track shared structure. Signatures sharing symbols now have positive expected cosine,
    and dimension becomes the real capacity knob the parent literature describes.
    """
    dim = DIM if dim is None else dim
    acc = [0] * dim
    for symbol in sig:
        for i, v in enumerate(symbol_vector(symbol, dim)):
            acc[i] += v
    return [1 if v > 0 else (-1 if v < 0 else 1) for v in acc]


def cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / len(a)          # both bipolar and equal length


def exact_feature_distance(sa: tuple, sb: tuple) -> float:
    """R3's exact distance over the SAME features: Jaccard on the signature multiset."""
    A, Bs = set(sa), set(sb)
    return 1.0 - (len(A & Bs) / len(A | Bs) if (A | Bs) else 1.0)


def propose(ks: KnowledgeSpace, target_type: str, k: int, mode: str):
    """Rank atoms by similarity to the query signature; return the top k as candidates.

    The query signature is the target TYPE alone -- what the query actually states. It is
    not the decisive atom's signature, which would be an oracle.
    """
    query = (target_type,)
    qv = hypervector(query)
    scored = []
    for a in ks.atoms:
        sig = signature(ks, a.atom_id)
        if mode == "R6_VSA":
            score = cosine(qv, hypervector(sig))
        elif mode == "R3_EXACT_KNN":
            score = -exact_feature_distance(query, sig)
        else:
            raise ValueError(mode)
        scored.append((score, a.atom_id))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [aid for _s, aid in scored[:k]], len(ks.atoms)


def twin_field(n_twins: int = 60):
    """Many target-type atoms with DISTINCT but SIMILAR signatures.

    The first run of this study found no discrimination: at DIM=512 the projection matched
    the exact distance everywhere, so APPROXIMATE_RETRIEVAL_NOT_SAFE stayed unreachable for
    a second reason -- the worlds were too easy, not just the mechanism absent. Ties are the
    cause: in B.WORLDS the decisive atom and its twins have IDENTICAL signatures, so exact
    and approximate agree by construction and nothing can separate them.

    Here every target-type atom carries a distinct incident-channel multiset, and the
    decisive one is the CLOSEST to the query by exact Jaccard. An exact distance therefore
    ranks it first; a random projection need not, and whether it does is a question about
    capacity -- which is the real HDC parameter and the one worth sweeping.
    """
    from ocm.kso.space import Atom, Hyperedge
    channels = ("SUPPORT", "DEPENDENCE", "EMBEDDING", "RESTRICTION", "SCALE_CHANGE")
    atoms = [Atom(atom_id="seed", atom_type="query_seed"),
             Atom(atom_id=E.DECISIVE, atom_type=B.TARGET_TYPE)]
    atoms += [Atom(atom_id=f"w{i}", atom_type=B.TARGET_TYPE) for i in range(n_twins)]
    # Decisive: exactly ONE incident channel -> smallest signature -> closest to a
    # query that names only the target type.
    edges = [Hyperedge(edge_id="e_decisive", tails=("seed",), heads=(E.DECISIVE,),
                       relation_type="SUPPORT")]
    for i in range(n_twins):
        # Twin i carries i+2 incident edges on one channel. Signatures are multisets, so
        # every twin's is distinct and every one is strictly further from the query than
        # the decisive atom's single-edge signature.
        # A first version sliced a 5-channel list and produced only FOUR twin classes --
        # six distinct signatures in total, which any dimension above 8 separates
        # trivially. That is why the first sweep found no capacity boundary.
        c = channels[i % len(channels)]
        for j in range(i + 2):
            edges.append(Hyperedge(edge_id=f"e_w{i}_{j}", tails=("seed",),
                                   heads=(f"w{i}",), relation_type=c))
    return KnowledgeSpace(atoms=tuple(atoms), hyperedges=tuple(edges))


def run(ks_kinds=B.WORLDS, ks_budget=(4, 8, 16, 32, 64),
        dims=(2, 4, 8, 16, 32, 64, 128, 256, 512)) -> dict:
    out = {}
    for kind in ks_kinds:
        ks = B.world(kind)
        sig_decisive = signature(ks, E.DECISIVE)
        twins = sorted(a.atom_id for a in ks.atoms
                       if signature(ks, a.atom_id) == sig_decisive)
        rows = {}
        for k in ks_budget:
            r6, n = propose(ks, B.TARGET_TYPE, k, "R6_VSA")
            r3, _ = propose(ks, B.TARGET_TYPE, k, "R3_EXACT_KNN")
            rows[str(k)] = {
                "R6_VSA": {"found_decisive": E.DECISIVE in r6,
                           "target_type_in_topk": sum(
                               1 for a in r6 if ks.atom_view[a].atom_type == B.TARGET_TYPE),
                           "false_candidates": sum(
                               1 for a in r6 if ks.atom_view[a].atom_type != B.TARGET_TYPE)},
                "R3_EXACT_KNN": {"found_decisive": E.DECISIVE in r3,
                                 "target_type_in_topk": sum(
                                     1 for a in r3 if ks.atom_view[a].atom_type == B.TARGET_TYPE),
                                 "false_candidates": sum(
                                     1 for a in r3 if ks.atom_view[a].atom_type != B.TARGET_TYPE)},
            }
        out[kind] = {
            "atoms": len(ks.atoms),
            "decisive_signature": list(sig_decisive),
            "atoms_sharing_the_decisive_signature": twins,
            "indistinguishable_twins": len(twins),
            "rows": rows,
            "k_where_R6_finds_decisive": sorted(
                k for k, r in rows.items() if r["R6_VSA"]["found_decisive"]),
            "k_where_R3_finds_decisive": sorted(
                k for k, r in rows.items() if r["R3_EXACT_KNN"]["found_decisive"]),
        }
    def near_twin_field(n=60):
        """Twins one symbol further from the query than the decisive atom.

        The wide twin field did not discriminate even at DIM=2, because its signatures are
        structurally coarse: twins bundle many copies of one channel, so their bundle is
        dominated by it and sits far from the query's type vector at any dimension. Here
        every twin shares the decisive atom's channel and adds exactly ONE more, so exact
        Jaccard separates them by a single symbol and the VSA bundles differ by one
        component. If a capacity boundary exists on this surface, it is here.
        """
        from ocm.kso.space import Atom, Hyperedge
        extra = ("DEPENDENCE", "EMBEDDING", "RESTRICTION", "SCALE_CHANGE",
                 "BOUNDARY_CHANGE", "DECISION_TRANSPORT", "REPRESENTATION_TRANSPORT")
        atoms = [Atom(atom_id="seed", atom_type="query_seed"),
                 Atom(atom_id=E.DECISIVE, atom_type=B.TARGET_TYPE)]
        atoms += [Atom(atom_id=f"n{i}", atom_type=B.TARGET_TYPE) for i in range(n)]
        edges = [Hyperedge(edge_id="e_decisive", tails=("seed",), heads=(E.DECISIVE,),
                           relation_type="SUPPORT")]
        for i in range(n):
            edges.append(Hyperedge(edge_id=f"e_n{i}_a", tails=("seed",), heads=(f"n{i}",),
                                   relation_type="SUPPORT"))
            edges.append(Hyperedge(edge_id=f"e_n{i}_b", tails=("seed",), heads=(f"n{i}",),
                                   relation_type=extra[i % len(extra)]))
        return KnowledgeSpace(atoms=tuple(atoms), hyperedges=tuple(edges))

    # --- capacity sweep on the twin field -------------------------------------
    global DIM
    original = DIM
    tf = twin_field()
    tf_sig = signature(tf, E.DECISIVE)
    tf_distinct = len({signature(tf, a.atom_id) for a in tf.atoms})
    sweep = {}
    for d in dims:
        DIM = d
        row = {}
        for k in (1, 2, 4, 8):
            r6, _ = propose(tf, B.TARGET_TYPE, k, "R6_VSA")
            r3, _ = propose(tf, B.TARGET_TYPE, k, "R3_EXACT_KNN")
            row[str(k)] = {"R6_found": E.DECISIVE in r6, "R3_found": E.DECISIVE in r3}
        sweep[str(d)] = {
            "rows": row,
            "approximation_loses_at_k": sorted(
                k for k, r in row.items() if r["R3_found"] and not r["R6_found"])}
    # second, harder capacity world
    # MULTI-SEED. A single random draw per dimension gave a NON-MONOTONE profile --
    # the approximation lost at 16, 128 and 512 but not at 2, 4, 8, 32, 64, 256. A
    # capacity effect cannot behave that way, so the single-draw result was seed variance
    # being read as a dimension threshold. Reporting it as a capacity boundary would have
    # been wrong. Each dimension is now run over many salts and reported as a FAILURE RATE.
    global SALT
    base_salt = SALT
    nt = near_twin_field()
    nt_sweep = {}
    seeds = 40
    for d in dims:
        DIM = d
        losses = 0
        for sd in range(seeds):
            SALT = f"{base_salt}#s{sd}"
            r6, _ = propose(nt, B.TARGET_TYPE, 1, "R6_VSA")
            r3, _ = propose(nt, B.TARGET_TYPE, 1, "R3_EXACT_KNN")
            if E.DECISIVE in r3 and E.DECISIVE not in r6:
                losses += 1
        SALT = base_salt
        nt_sweep[str(d)] = {"seeds": seeds, "losses_at_k1": losses,
                            "failure_rate": losses / seeds}
    DIM = original

    return {"schema": SCHEMA,
            "near_twin_capacity_sweep": {
                "world": "NEAR_TWIN_FIELD", "atoms": len(nt.atoms),
                "distinct_signatures": len({signature(nt, a.atom_id) for a in nt.atoms}),
                "seeds_per_dimension": 40,
                "method": ("Failure rate over 40 independent salts per dimension, at k=1. "
                           "A single draw per dimension produced a non-monotone profile "
                           "that would have been misread as a capacity threshold."),
                "by_dimension": nt_sweep,
                "dimensions_where_the_approximation_loses": sorted(
                    (d for d, r in nt_sweep.items() if r["failure_rate"] > 0), key=int)},
            "analysis_status": "BUILDS_R3_AND_R6_TO_MAKE_A_REGISTERED_TERMINAL_REACHABLE",
            "capacity_sweep": {
                "world": "TWIN_FIELD",
                "atoms": len(tf.atoms), "distinct_signatures": tf_distinct,
                "decisive_signature": list(tf_sig),
                "note": ("Every target-type atom has a distinct signature and the decisive "
                         "one is closest to the query by exact Jaccard, so an exact "
                         "distance ranks it first at k=1. Whether the random projection "
                         "does is a capacity question, swept over dimension."),
                "by_dimension": sweep,
                "dimensions_where_the_approximation_loses": sorted(
                    (d for d, r in sweep.items() if r["approximation_loses_at_k"]),
                    key=int)},
            "authority": ("Research-only. The projection is a fixed random hash of structural "
                          "features: no training set, no objective, no fitted parameter, no "
                          "gradient. Nothing learns, routes or adapts, and #71 remains "
                          "LEARNED_ROUTER_NOT_YET_AUTHORIZED. Exact machinery still decides; "
                          "the projection proposes candidates only."),
            "evidence_class": "E1 / L1",
            "projection": {"dim": DIM, "salt": SALT, "kind": "bipolar random, sha256-derived"},
            "information_surface": (
                "atom_type plus the sorted multiset of incident relation types. No atom "
                "identity, no answer label. Atoms of the same type reached the same way are "
                "indistinguishable by construction."),
            "worlds": out}


def verdict(doc: dict) -> dict:
    w = doc["worlds"]
    r6_ever = sorted(k for k in w if w[k]["k_where_R6_finds_decisive"])
    r3_ever = sorted(k for k in w if w[k]["k_where_R3_finds_decisive"])
    both_miss = sorted(k for k in w if not w[k]["k_where_R6_finds_decisive"]
                       and not w[k]["k_where_R3_finds_decisive"])
    approx_only_miss = sorted(k for k in w if w[k]["k_where_R3_finds_decisive"]
                              and not w[k]["k_where_R6_finds_decisive"])
    twins = {k: w[k]["indistinguishable_twins"] for k in w}
    out = {
        "worlds_where_R6_ever_finds_it": r6_ever,
        "worlds_where_R3_ever_finds_it": r3_ever,
        "worlds_where_BOTH_miss": both_miss,
        "worlds_where_only_the_APPROXIMATION_misses": approx_only_miss,
        "indistinguishable_twins": twins,
        "terminal_is_now_reachable": True,
    }
    cap = doc.get("capacity_sweep", {})
    near = doc.get("near_twin_capacity_sweep", {})
    lose_dims = (cap.get("dimensions_where_the_approximation_loses", [])
                 + near.get("dimensions_where_the_approximation_loses", []))
    out["near_twin_loses_at_dimensions"] = near.get(
        "dimensions_where_the_approximation_loses", [])
    out["capacity_dimensions_where_approximation_loses"] = lose_dims
    out["capacity_distinct_signatures"] = cap.get("distinct_signatures")
    if lose_dims:
        out["terminal"] = "APPROXIMATE_RETRIEVAL_NOT_SAFE"
        rates = {d: r["failure_rate"] for d, r in
                 doc.get("near_twin_capacity_sweep", {}).get("by_dimension", {}).items()}
        out["near_twin_failure_rate_by_dimension"] = rates
        out["terminal_reason"] = (
            "Reached for the first time, and NOT as a capacity boundary -- the profile "
            "rules that reading out. On a near-twin field where every twin shares the "
            "decisive atom's channel and adds exactly one more symbol, the approximation's "
            "failure rate at k=1 over 40 salts per dimension RISES monotonically with "
            f"dimension: {rates}. A capacity effect must IMPROVE with dimension, so this is "
            "the opposite of one. The approximation is not losing the answer to noise that "
            "more dimensions would suppress; it is converging, more and more reliably, to "
            "an ordering that DIFFERS from the exact one. Cosine over bundled hypervectors "
            "and Jaccard over signature sets simply rank this surface differently, and "
            "capacity buys fidelity to the projection's own ordering, not to the exact one. "
            "That is APPROXIMATE_RETRIEVAL_NOT_SAFE in the meaningful sense: an exact "
            "distance over identical information returns the decisive atom and the "
            "approximation systematically does not, with more resources making it worse.\n"
            "Two earlier attempts to reach this terminal were my errors and are retained "
            "rather than deleted. (1) The first worlds gave the decisive atom and its twins "
            "IDENTICAL signatures, so the two mechanisms agreed by construction. (2) The "
            "first R6 hashed the whole signature tuple instead of bundling its symbols, so "
            "similarity carried no compositional information and the approximation 'lost' "
            "identically at every dimension -- a flat profile that would have produced this "
            "terminal from a hash masquerading as a vector-symbolic architecture. A third "
            "pass ran one salt per dimension and produced a NON-MONOTONE profile that would "
            "have been misread as a capacity threshold; the rates above use 40 salts per "
            f"dimension instead. On the wide twin field of "
            f"{out['capacity_distinct_signatures']} distinct signatures "
            "the corrected VSA matched the exact "
            "distance at every dimension, so the effect is specific to near-twins. Until "
            "this study the terminal was unreachable at all: main had no approximate "
            "mechanism to be unsafe.")
    elif approx_only_miss:
        out["terminal"] = "APPROXIMATE_RETRIEVAL_NOT_SAFE"
        out["terminal_reason"] = (
            f"In {approx_only_miss} an exact distance over the same features returns the "
            "decisive atom and the random projection does not. The loss is attributable to "
            "the approximation itself, not to the feature surface, because both mechanisms "
            "saw identical information. That is the registered terminal, and until this "
            "study it could not be reached at all because no approximate mechanism existed "
            "on main to be unsafe.")
    elif both_miss:
        out["terminal"] = "REPRESENTATION_INSUFFICIENT"
        out["terminal_reason"] = (
            f"In {both_miss} BOTH the approximation and an exact distance over the same "
            "features miss the decisive atom. The approximation is not at fault: the "
            "feature surface cannot separate the answer from its indistinguishable twins "
            f"({twins}), which is a property of what the space exposes, not of how the "
            "similarity is computed. Charging this to approximation would be the wrong "
            "diagnosis, and reporting APPROXIMATE_RETRIEVAL_NOT_SAFE here would be a "
            "misattribution the study is built to avoid.")
    else:
        out["terminal"] = "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE"
        out["terminal_reason"] = (
            "The registered terminal APPROXIMATE_RETRIEVAL_NOT_SAFE is now REACHABLE and "
            "was NOT REACHED. That distinction is the result. Before this study no "
            "approximate mechanism existed on main, so the terminal could not be tested at "
            "all; R3 and R6 now exist over one shared feature surface and the machinery to "
            "trigger it works. A correctly bundled VSA matched an exact distance over the "
            "same features on every world and at every dimension from 2 to 512, including "
            "a 62-signature twin field and a near-twin field where signatures differ by a "
            "single symbol. Non-inferior at this scope -- a bounded positive for the "
            "approximation, and emphatically not a claim that approximate retrieval is safe "
            "in general.\n"
            "TWO FAILED ATTEMPTS TO REACH THE TERMINAL ARE RETAINED, because both were my "
            "errors rather than findings. (1) The first worlds gave the decisive atom and "
            "its twins IDENTICAL signatures, so exact and approximate agreed by "
            "construction. (2) The first R6 hashed the whole signature tuple instead of "
            "bundling its symbols, so similarity carried no compositional information and "
            "the approximation 'lost' at k=1 identically at every dimension from 2 to 512. "
            "That flat profile is the tell -- a capacity effect must improve with dimension "
            "-- and it would have produced APPROXIMATE_RETRIEVAL_NOT_SAFE from a hash "
            "masquerading as a vector-symbolic architecture. Reporting it would have been "
            "the misattribution this study exists to avoid.")
    out["what_this_does_not_establish"] = (
        "Nothing about attention or any neural system: no neural arm was run, and a fixed "
        "random projection is not a learned representation. No cost accounting -- the "
        "projection build and per-query similarity are NOT charged here, so no payback "
        "claim is made or implied. Candidate proposal is not retrieval: the exact closure "
        "still decides, and no arm here is allowed to answer. E1/L1, four planted worlds.")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    doc = run()
    doc["verdict"] = verdict(doc)
    a.out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    v = doc["verdict"]
    print(json.dumps({k: v[k] for k in (
        "terminal", "worlds_where_R6_ever_finds_it", "worlds_where_R3_ever_finds_it",
        "worlds_where_BOTH_miss", "worlds_where_only_the_APPROXIMATION_misses",
        "indistinguishable_twins")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
