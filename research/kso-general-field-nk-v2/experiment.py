"""Issue #165 §8 remaining GEF boxes: N / k / indexes / parent federation.

Uses production ``ocm.kso`` plus the G5.2 packed field parent. Two typed
domains (language ``lexeme``, mathematics ``theorem``) on one local registry.
Does not edit ``src/``. Does not overwrite ``research/kso-general-field-v1/``.
Does not mint a second truth store.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
G5 = REPO / "research" / "g5-packed-field-v1"
SRC = REPO / "src"


def _prefer(path: Path) -> None:
    p = str(path)
    while p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)


_prefer(SRC)
_prefer(G5)
_prefer(ROOT)

from ocm.kso.admission import compose
from ocm.kso.space import Atom, Hyperedge, KnowledgeSpace, TypedRejection
from ocm.kso.types import CORE_ATOM_TYPES, DEFAULT_REGISTRY, Authority, TypeRegistry
from ocm.kso.warrant import WarrantProfile
from packed_space import PackedKnowledgeSpace

import indexes as I

SCHEMA = "ocm.kso.general-field-nk.v2"
DEFAULT_NS = (64, 256, 1024)
EV_LANG = "ev:lang"
EV_MATH = "ev:math"
EV_UNREL_LANG = "ev:unrel-lang"
EV_UNREL_MATH = "ev:unrel-math"
V1_DIR = REPO / "research" / "kso-general-field-v1"


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def production_src_edited() -> bool:
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--", "src"], cwd=REPO, text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return True
    return bool(diff.strip())


def v1_capsule_overwritten() -> bool:
    if not V1_DIR.is_dir():
        return False
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--", str(V1_DIR.relative_to(REPO))],
            cwd=REPO,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return True
    return bool(diff.strip())


def snapshot_default_registry() -> dict[str, list[str]]:
    return {
        "atom_types": sorted(DEFAULT_REGISTRY.atom_types),
        "relation_types": sorted(DEFAULT_REGISTRY.relation_types),
    }


def fresh_registry() -> TypeRegistry:
    """Local registry. Never mutate ``DEFAULT_REGISTRY``."""
    reg = TypeRegistry()
    reg.register_atom_type(I.LANG_TYPE)
    reg.register_atom_type(I.MATH_TYPE)
    return reg


def _ring_edges(ids: list[str], prefix: str) -> list[Hyperedge]:
    edges: list[Hyperedge] = []
    n = len(ids)
    if n == 0:
        return edges
    for i, atom_id in enumerate(ids):
        head = ids[(i + 1) % n]
        if head == atom_id and n > 1:
            head = ids[(i + 2) % n]
        if head == atom_id:
            continue
        edges.append(
            Hyperedge(
                f"{prefix}-{i}",
                (atom_id,),
                (head,),
                "DEPENDENCE",
                warrant=WarrantProfile.of({i % 5}),
            )
        )
    return edges


def plant_world(n: int) -> KnowledgeSpace:
    """One field, two typed domains. Unrelated other-domain atoms grow N; planted k stays 8+8."""
    if n < I.K_LANG + I.K_MATH:
        raise ValueError("n must cover planted language and mathematics targets")
    extra = n - I.K_LANG - I.K_MATH
    extra_lang = extra // 2
    extra_math = extra - extra_lang
    atoms: list[Atom] = []
    lang_ids: list[str] = []
    math_ids: list[str] = []
    for i in range(I.K_LANG):
        atom_id = f"lang_t{i}"
        lang_ids.append(atom_id)
        atoms.append(
            Atom(
                atom_id,
                I.LANG_TYPE,
                WarrantProfile.of({EV_LANG}),
                Authority.of(speaker=1),
                content_ref=f"{I.LANG_PREFIX}{i}",
            )
        )
    for i in range(I.K_MATH):
        atom_id = f"math_t{i}"
        math_ids.append(atom_id)
        atoms.append(
            Atom(
                atom_id,
                I.MATH_TYPE,
                WarrantProfile.of({EV_MATH}),
                Authority.of(formal_proof=1),
                content_ref=f"{I.MATH_PREFIX}{i}",
            )
        )
    for i in range(extra_lang):
        atom_id = f"lang_u{i}"
        lang_ids.append(atom_id)
        atoms.append(
            Atom(
                atom_id,
                I.LANG_TYPE,
                WarrantProfile.of({EV_UNREL_LANG}),
                Authority.of(speaker=1),
                content_ref=f"{I.UNREL_LANG_PREFIX}{i}",
            )
        )
    for i in range(extra_math):
        atom_id = f"math_u{i}"
        math_ids.append(atom_id)
        atoms.append(
            Atom(
                atom_id,
                I.MATH_TYPE,
                WarrantProfile.of({EV_UNREL_MATH}),
                Authority.of(formal_proof=1),
                content_ref=f"{I.UNREL_MATH_PREFIX}{i}",
            )
        )
    edges = _ring_edges(lang_ids, "lang-e") + _ring_edges(math_ids, "math-e")
    return KnowledgeSpace(tuple(atoms), tuple(edges), fresh_registry())


def isolated_domain(ks: KnowledgeSpace, atom_type: str) -> KnowledgeSpace:
    keep = {atom.atom_id for atom in ks.atoms if atom.atom_type == atom_type}
    atoms = tuple(atom for atom in ks.atoms if atom.atom_id in keep)
    edges = tuple(
        edge
        for edge in ks.hyperedges
        if set(edge.tails) | set(edge.heads) <= keep
    )
    return KnowledgeSpace(atoms, edges, ks.registry)


def try_compose(ks: KnowledgeSpace, tails: list[str], head_id: str, head_type: str) -> dict[str, Any]:
    try:
        new_ks, rec = compose(ks, tails, head_id, head_type=head_type)
    except TypedRejection as exc:
        return {
            "ok": False,
            "error": str(exc),
            "n_atoms": len(ks.atoms),
        }
    return {
        "ok": True,
        "head": rec.head_id if hasattr(rec, "head_id") else head_id,
        "n_atoms": len(new_ks.atoms),
        "one_store": True,
    }


def federation_copy_math_into_lang(lang_ks: KnowledgeSpace, math_ks: KnowledgeSpace, math_id: str) -> dict[str, Any]:
    """Hostile parent: copy a math atom into the language store to compose. Duplicates identity."""
    copied = math_ks.atom(math_id)
    if copied.atom_id in lang_ks.ids:
        return {"ok": False, "duplicated_identity": False, "reason": "already_present"}
    merged = KnowledgeSpace(lang_ks.atoms + (copied,), lang_ks.hyperedges, lang_ks.registry)
    composed = try_compose(merged, ["lang_t0", math_id], "fed_bridge", "claim")
    return {
        "ok": bool(composed["ok"]),
        "duplicated_identity": True,
        "copied_atom": math_id,
        "lang_store_n_after_copy": len(merged.atoms),
        "compose": composed,
        "second_copy_not_correspondence": True,
    }


def measure_n(n: int) -> dict[str, Any]:
    ks = plant_world(n)
    packed = PackedKnowledgeSpace.from_reference(ks)
    identity = I.identity_N(ks)
    index = I.CrossDomainIndex.build(packed)

    lang_tag = index.retrieve_tag(I.LANG_TAG, relevant_k=I.K_LANG)
    math_tag = index.retrieve_tag(I.MATH_TAG, relevant_k=I.K_MATH)
    lang_type = index.retrieve_type(I.LANG_TYPE)
    math_type = index.retrieve_type(I.MATH_TYPE)
    lang_linear = I.g5_linear_query(index, prefix=I.LANG_PREFIX, relevant_k=I.K_LANG)
    math_linear = I.g5_linear_query(index, prefix=I.MATH_PREFIX, relevant_k=I.K_MATH)
    lang_bitmap = I.g5_bitmap_type_query(index, I.LANG_TYPE)
    mutant = I.mutant_uninstrumented_linear(packed, prefix=I.LANG_PREFIX)

    extra = Atom(
        f"math_u_extra_{n}",
        I.MATH_TYPE,
        WarrantProfile.of({EV_UNREL_MATH}),
        Authority.of(formal_proof=1),
        content_ref=f"{I.UNREL_MATH_PREFIX}extra-{n}",
    )
    incremental = index.incremental_update(extra)
    rebuilt = index.rebuild_update(extra)
    lang_after_math_append = incremental.retrieve_tag(I.LANG_TAG, relevant_k=I.K_LANG)

    lang_ks = isolated_domain(ks, I.LANG_TYPE)
    math_ks = isolated_domain(ks, I.MATH_TYPE)
    lang_packed = PackedKnowledgeSpace.from_reference(lang_ks)
    math_packed = PackedKnowledgeSpace.from_reference(math_ks)
    lang_index = I.CrossDomainIndex.build(lang_packed)
    math_index = I.CrossDomainIndex.build(math_packed)
    routed_lang = lang_index.retrieve_tag(I.LANG_TAG, relevant_k=I.K_LANG)
    routed_math = math_index.retrieve_tag(I.MATH_TAG, relevant_k=I.K_MATH)
    naive_federation_work = lang_ks.resource_counts()["object_count"] + math_ks.resource_counts()["object_count"]

    unified_compose = try_compose(ks, ["lang_t0", "math_t0"], "bridge", "claim")
    isolated_compose = try_compose(lang_ks, ["lang_t0", "math_t0"], "bridge", "claim")
    copied = federation_copy_math_into_lang(lang_ks, math_ks, "math_t0")

    n_lang = len(lang_ks.atoms)
    n_math = len(math_ks.atoms)
    expected_lang = tuple(f"lang_t{i}" for i in range(I.K_LANG))
    expected_math = tuple(f"math_t{i}" for i in range(I.K_MATH))
    hit_parity = (
        tuple(lang_tag["hits"]) == expected_lang
        and tuple(math_tag["hits"]) == expected_math
        and lang_linear["hit_count"] == I.K_LANG
        and math_linear["hit_count"] == I.K_MATH
    )
    return {
        "n": n,
        "n_atoms": identity["n_atoms"],
        "n_edges": identity["n_edges"],
        "N_t": identity["N_t"],
        "n_language_atoms": n_lang,
        "n_mathematics_atoms": n_math,
        "unrelated_language_atoms": n_lang - I.K_LANG,
        "unrelated_mathematics_atoms": n_math - I.K_MATH,
        "warrant_size_auxiliary": identity["warrant_size_auxiliary"],
        "k_lang_planted": I.K_LANG,
        "k_math_planted": I.K_MATH,
        "digest_parity": packed.digest() == ks.digest(),
        "hit_parity": hit_parity,
        "one_field": True,
        "second_truth_store": False,
        "lang_tag": lang_tag,
        "math_tag": math_tag,
        "lang_type": {
            "hit_count": lang_type["hit_count"],
            "retrieval_units": lang_type["retrieval_units"],
            "query_work_units": lang_type["query_work_units"],
        },
        "math_type": {
            "hit_count": math_type["hit_count"],
            "retrieval_units": math_type["retrieval_units"],
            "query_work_units": math_type["query_work_units"],
        },
        "lang_linear": lang_linear,
        "math_linear": math_linear,
        "lang_bitmap": {
            "retrieval_units": lang_bitmap["retrieval_units"],
            "hit_count": lang_bitmap["hit_count"],
            "query_work_units": lang_bitmap["query_work_units"],
        },
        "mutant_uninstrumented_linear": mutant,
        "index_construction": {
            "posting_construction_units": index.construction_units,
            "packed_index_build_touches": index.packed_index_build_touches,
            "charged": index.construction_units == n and index.packed_index_build_touches > 0,
        },
        "index_update": {
            "incremental_posting_units": incremental.update_units,
            "rebuild_posting_units": rebuilt.update_units,
            "packed_rebuild_touches_after_append": incremental.packed_index_build_touches,
            "incremental_lt_rebuild": incremental.update_units < rebuilt.update_units,
            "lang_k_after_unrelated_math_append": lang_after_math_append["relevant_k"],
            "lang_hits_after_unrelated_math_append": lang_after_math_append["hit_count"],
            "charged": incremental.update_units == 1 and rebuilt.update_units == n + 1,
        },
        "federation": {
            "routed_lang_work": routed_lang["query_work_units"],
            "routed_math_work": routed_math["query_work_units"],
            "unified_lang_work": lang_tag["query_work_units"],
            "unified_math_work": math_tag["query_work_units"],
            "naive_scan_both_stores": naive_federation_work,
            "unified_linear_work": lang_linear["query_work_units"],
            "routed_ties_unified": routed_lang["query_work_units"] == lang_tag["query_work_units"] == 2 * I.K_LANG,
            "naive_tracks_n": naive_federation_work == n,
            "isolated_lang_n": n_lang,
            "isolated_math_n": n_math,
            "unified_compose": unified_compose,
            "isolated_compose": isolated_compose,
            "federation_copy": copied,
        },
        "hidden_scan_classification": {
            "lang_tag": I.classify_hidden_scan(lang_tag),
            "lang_linear": I.classify_hidden_scan(lang_linear),
            "mutant": I.classify_hidden_scan(mutant),
        },
    }


def _boxes(rows: list[dict[str, Any]], scaling: dict[str, Any], src_edited: bool, v1_overwritten: bool) -> dict[str, Any]:
    n_grew = [row["N_t"] for row in rows]
    unrelated_math = [row["unrelated_mathematics_atoms"] for row in rows]
    unrelated_lang = [row["unrelated_language_atoms"] for row in rows]
    one_field = all(row["one_field"] and not row["second_truth_store"] for row in rows)
    grow_ok = (
        one_field
        and not src_edited
        and not v1_overwritten
        and n_grew[0] < n_grew[-1]
        and unrelated_math[0] < unrelated_math[-1]
        and unrelated_lang[0] < unrelated_lang[-1]
        and all(row["n_language_atoms"] + row["n_mathematics_atoms"] == row["n_atoms"] for row in rows)
        and all(row["digest_parity"] for row in rows)
    )
    k_ok = (
        all(row["lang_tag"]["relevant_k"] == I.K_LANG for row in rows)
        and all(row["math_tag"]["relevant_k"] == I.K_MATH for row in rows)
        and all(row["lang_tag"]["hit_count"] == I.K_LANG for row in rows)
        and all(row["math_tag"]["hit_count"] == I.K_MATH for row in rows)
        and all(row["lang_linear"]["relevant_k"] == I.K_LANG for row in rows)
        and all(row["lang_linear"]["touched"] == row["n_atoms"] for row in rows)
        and all(row["lang_type"]["hit_count"] == row["n_language_atoms"] for row in rows)
        and scaling["status"] == "MEASURED"
        and all(row["hit_parity"] for row in rows)
    )
    charge_ok = all(
        row["index_construction"]["charged"]
        and row["index_update"]["charged"]
        and row["index_update"]["incremental_lt_rebuild"]
        and row["index_update"]["lang_k_after_unrelated_math_append"] == I.K_LANG
        and row["lang_tag"]["hidden_scan_units"] == 0
        and row["lang_linear"]["hidden_scan_units"] == row["n_atoms"]
        and row["lang_tag"]["materialization_units"] == I.K_LANG
        and row["hidden_scan_classification"]["mutant"] == "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
        and row["mutant_uninstrumented_linear"]["status"] == "CANNOT_CHECK_UNINSTRUMENTED_GLOBAL_SCAN"
        for row in rows
    )
    fed_ok = all(
        row["federation"]["routed_ties_unified"]
        and row["federation"]["naive_tracks_n"]
        and row["federation"]["unified_linear_work"] == row["n_atoms"] + I.K_LANG
        and row["federation"]["unified_compose"]["ok"]
        and not row["federation"]["isolated_compose"]["ok"]
        and row["federation"]["federation_copy"]["duplicated_identity"]
        and row["federation"]["federation_copy"]["ok"]
        for row in rows
    )

    def status(ok: bool) -> str:
        return "EARNED_AT_SCOPE" if ok else "OPEN"

    return {
        "GEF/010-grow_unrelated_cross_domain_n": {
            "text": "grow unrelated cross-domain N",
            "status": status(grow_ok),
            "N_t": n_grew,
            "n_atoms": [row["n_atoms"] for row in rows],
            "unrelated_language_atoms": unrelated_lang,
            "unrelated_mathematics_atoms": unrelated_math,
            "one_field": one_field,
            "digest_parity": [row["digest_parity"] for row in rows],
            "note": "Language and mathematics share one packed KSO. Unrelated other-domain atoms grow N; planted targets stay 8+8.",
        },
        "GEF/011-measure_relevant_k": {
            "text": "measure relevant k",
            "status": status(k_ok),
            "k_lang": [row["lang_tag"]["relevant_k"] for row in rows],
            "k_math": [row["math_tag"]["relevant_k"] for row in rows],
            "k_over_N": [row["lang_tag"]["k_over_N"] for row in rows],
            "type_index_lang_hits": [row["lang_type"]["hit_count"] for row in rows],
            "linear_touched": [row["lang_linear"]["touched"] for row in rows],
            "scaling": scaling,
            "note": "Relevant k is the planted domain query (8), not type-index size and not N. Type postings grow with extra same-type atoms; tag postings do not.",
        },
        "GEF/012-charge_cross_domain_indexes": {
            "text": "charge cross-domain indexes",
            "status": status(charge_ok),
            "posting_construction_units": [row["index_construction"]["posting_construction_units"] for row in rows],
            "packed_index_build_touches": [row["index_construction"]["packed_index_build_touches"] for row in rows],
            "incremental_posting_units": [row["index_update"]["incremental_posting_units"] for row in rows],
            "rebuild_posting_units": [row["index_update"]["rebuild_posting_units"] for row in rows],
            "lang_tag_retrieval_units": [row["lang_tag"]["retrieval_units"] for row in rows],
            "lang_tag_materialization_units": [row["lang_tag"]["materialization_units"] for row in rows],
            "lang_linear_hidden_scan_units": [row["lang_linear"]["hidden_scan_units"] for row in rows],
            "mutant_status": rows[-1]["mutant_uninstrumented_linear"]["status"],
            "note": "Construction scans N once. Incremental unrelated-math append is 1; rebuild is N+1. Language tag retrieval does not hide a math scan. Uninstrumented linear is CANNOT_CHECK.",
        },
        "GEF/013-compare_parent_federation": {
            "text": "compare parent federation",
            "status": status(fed_ok),
            "unified_lang_work": [row["federation"]["unified_lang_work"] for row in rows],
            "routed_federation_lang_work": [row["federation"]["routed_lang_work"] for row in rows],
            "naive_scan_both_stores": [row["federation"]["naive_scan_both_stores"] for row in rows],
            "unified_linear_work": [row["federation"]["unified_linear_work"] for row in rows],
            "unified_compose_ok": [row["federation"]["unified_compose"]["ok"] for row in rows],
            "isolated_compose_ok": [row["federation"]["isolated_compose"]["ok"] for row in rows],
            "federation_copy_duplicates_identity": [
                row["federation"]["federation_copy"]["duplicated_identity"] for row in rows
            ],
            "note": (
                "Routed isolated typed indexes tie unified tag postings on in-domain query work (k). "
                "Naive federation and unified linear track N. Isolated stores cannot compose across "
                "domains without copying, which duplicates identity. One packed KSO composes in place."
            ),
        },
    }


def choose_terminal(boxes: dict[str, Any], src_edited: bool, v1_overwritten: bool) -> str:
    if src_edited:
        return "GEF_NK_GATE_FAILED_PRODUCTION_SRC_EDITED"
    if v1_overwritten:
        return "GEF_NK_GATE_FAILED_V1_OVERWRITE"
    earned = [v["status"] == "EARNED_AT_SCOPE" for v in boxes.values()]
    if all(earned):
        return "CURRENT_KSO_ALREADY_GENERAL_ENOUGH"
    if any(earned):
        return "GEF_NK_PARTIAL_AT_PLANTED_SCOPE"
    return "GEF_NK_GATE_FAILED"


def run_study(ns: tuple[int, ...] = DEFAULT_NS) -> dict[str, Any]:
    default_before = snapshot_default_registry()
    src_edited = production_src_edited()
    v1_overwritten = v1_capsule_overwritten()
    rows = [measure_n(n) for n in ns]
    scaling = I.tracks_k_better_than_n(rows)
    boxes = _boxes(rows, scaling, src_edited, v1_overwritten)
    terminal = choose_terminal(boxes, src_edited, v1_overwritten)
    default_after = snapshot_default_registry()
    default_untouched = default_before == default_after
    default_is_core = set(default_after["atom_types"]) == set(CORE_ATOM_TYPES)
    if not default_untouched or not default_is_core:
        for box in boxes.values():
            box["status"] = "OPEN"
        terminal = "GEF_NK_GATE_FAILED_DEFAULT_REGISTRY"
    fed_ties = all(row["federation"]["routed_ties_unified"] for row in rows)
    return {
        "schema": SCHEMA,
        "issue": 165,
        "section": 8,
        "head": git_head(),
        "terminal": terminal,
        "programme_wide_close": False,
        "production_src_edited": src_edited,
        "v1_capsule_overwritten": v1_overwritten,
        "default_registry_untouched": default_untouched,
        "default_registry_is_core": default_is_core,
        "second_truth_store": False,
        "parent": (
            "G5.2 packed physical field (interned identifiers, type bitmaps, version-bound "
            "CSR indexes) plus inverted type/tag postings; isolated typed-store federation "
            "as the in-domain k parent; production ocm.kso compose for cross-domain identity"
        ),
        "parent_sufficient": fed_ties and terminal == "CURRENT_KSO_ALREADY_GENERAL_ENOUGH",
        "index_parent_ties_in_domain_k": fed_ties,
        "claim_ceiling": (
            "Planted-oracle §8 GEF N/k/index/federation boxes on one packed KSO with two "
            "typed domains (lexeme, theorem). Unrelated other-domain N grows; relevant k "
            "stays planted. Indexes are charged. Routed isolated indexes tie unified tag "
            "postings on in-domain work; federation copy duplicates identity. Not programme-"
            "wide GEF close. Not #73 prototype. Not language fluency. Does not re-issue v1 type/"
            "warrant boxes."
        ),
        "ns": list(ns),
        "k_lang": I.K_LANG,
        "k_math": I.K_MATH,
        "language_type": I.LANG_TYPE,
        "mathematics_type": I.MATH_TYPE,
        "boxes": boxes,
        "earned": sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_SCOPE"),
        "open": sorted(k for k, v in boxes.items() if v["status"] == "OPEN"),
        "cannot_check": [],
        "scaling": scaling,
        "rows": rows,
        "not_issued": [
            "PROGRAMME_WIDE_GEF_CLOSE",
            "GENERAL_EPISTEMIC_FIELD_SUPPORTED_AT_REGISTERED_SCOPE",
            "LANGUAGE_FLUENCY_BOUNDARY_MEASURED",
            "DOMAIN_CORE_FORK_REQUIRED",
            "PARENT_PRODUCT_SUFFICIENT",
            "PROTOTYPE_73",
            "GEF/001",
            "GEF/002",
            "GEF/003",
            "GEF/004",
            "GEF/005",
            "GEF/006",
            "GEF/007",
            "GEF/008",
            "GEF/009",
        ],
    }


def main(out: Path | None = None) -> dict[str, Any]:
    target = out if out is not None else ROOT / "RESULT.json"
    result = run_study()
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    target.write_text(text)
    print(json.dumps({"terminal": result["terminal"], "earned": result["earned"]}, indent=2))
    return result


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "RESULT.json"
    main(dest)
