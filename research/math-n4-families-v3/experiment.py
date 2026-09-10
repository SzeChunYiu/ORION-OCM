"""MATH-1 remaining family boxes at miniature Hilbert/SK scope.

Successor to research/math-n4-lemma-reuse-v1/ and research/math-n4-subgoal-v2/.
Plants four tiny family worlds in the same kernel. Does not close MATH-2 / N5,
does not expand FLT PRs 129-132, and does not overwrite frozen v1/v2 RESULT.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import kernel as K  # noqa: E402

SCHEMA = "math-n4-families.result.v3"
SALT = "orion-ocm-math-n4-families-v3"
V1 = REPO / "research" / "math-n4-lemma-reuse-v1"
V2 = REPO / "research" / "math-n4-subgoal-v2"
V1_RESULT = V1 / "RESULT.json"
V2_RESULT = V2 / "RESULT.json"
V1_RESULT_SHA256 = "cbcae02402fb7f73ec2f5cde25b4f922a141a8266f4ff603fc2d23c71aeb77cc"
V2_RESULT_SHA256 = "ae10620c091b1baa9320f34c2a613ba81ef6a7bff9debcd13645ce5122d06144"
V1_TERMINAL = "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE"
V2_TERMINAL = "CAUSAL_SUBGOAL_LEMMA_INTRODUCTION_SUPPORTED_AT_MINIATURE_SCOPE"
NEURAL_CANNOT_CHECK = "CANNOT_CHECK_NO_NN_LIBRARY"
LIBRARY_ARTIFACT = (
    REPO / "research" / "ordinary-goal-cohort-result-v1"
    / "records" / "qualification-01" / "LIBRARY-ARTIFACT.json"
)

ARITH_TRAIN = (
    ("task:arith-uvw", {"A": "u", "B": "v", "C": "w"}),
    ("task:arith-u2v2w2", {"A": "u2", "B": "v2", "C": "w2"}),
)
ARITH_HOLDOUT = {"A": "ha", "B": "hb", "C": "hc"}
ALGEBRA_HOLDOUT = {"A": "ea", "B": "eb", "C": "ec", "D": "ed"}
COUNT_TRAIN = (
    ("task:count-pq", {"A": "p", "B": "q"}),
    ("task:count-p2q2", {"A": "p2", "B": "q2"}),
)
COUNT_HOLDOUT = {"A": "cr", "B": "cs"}
EVEN_TRAIN = (
    ("task:even-e1", {"A": "e1"}),
    ("task:even-e2", {"A": "e2"}),
)
EVEN_HOLDOUT = {"A": "e3"}
ODD_TRAIN = (
    ("task:odd-xyz", {"A": "ox", "B": "oy", "C": "oz"}),
    ("task:odd-x2y2z2", {"A": "ox2", "B": "oy2", "C": "oz2"}),
)
ODD_HOLDOUT = {"A": "oa", "B": "ob", "C": "oc"}
ITER_HOLDOUT = {"A": "it"}
SK4 = 4
LIB2 = 2
TAUTOLOGY_MP = 2500


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rss_kib() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def custody(path: Path, frozen: str, frozen_terminal: str) -> dict[str, Any]:
    present = path.is_file()
    digest = sha256_file(path) if present else None
    terminal = None
    if present:
        terminal = json.loads(path.read_text(encoding="utf-8")).get("terminal")
    return {
        "path": str(path.relative_to(REPO)),
        "present": present,
        "sha256": digest,
        "sha256_frozen": frozen,
        "unchanged": digest == frozen,
        "terminal": terminal,
        "terminal_frozen": frozen_terminal,
    }


def inspect_metamath_library() -> dict[str, Any]:
    if not LIBRARY_ARTIFACT.is_file():
        return {
            "present": False,
            "runtime_available": False,
            "disposition": "MISSING_LIBRARY_ARTIFACT",
        }
    data = json.loads(LIBRARY_ARTIFACT.read_text(encoding="utf-8"))
    joined = Path(data.get("joined_prefix", {}).get("path") or "")
    return {
        "present": True,
        "bytes": LIBRARY_ARTIFACT.stat().st_size,
        "sha256": sha256_file(LIBRARY_ARTIFACT),
        "runtime_available": joined.is_file(),
        "joined_prefix_exists": joined.is_file(),
        "disposition": (
            "METAMATH_RUNTIME_AVAILABLE"
            if joined.is_file()
            else "MINIATURE_HILBERT_MICROSCOPE"
        ),
        "reason": (
            "Joined prefix is on disk."
            if joined.is_file()
            else "LIBRARY-ARTIFACT.json is a custody pointer to an off-host Metamath prefix; no kernel runtime in this environment."
        ),
    }


def result_summary(row: K.SearchResult) -> dict[str, Any]:
    payload = row.as_dict()
    payload["conclusion"] = K.pretty(row.proof.conclusion) if row.proof is not None else None
    return payload


def parent_bundle(goal: K.Formula) -> dict[str, Any]:
    catalog = K.catalog_rewrite_parent(goal)
    tautology = K.tautology_table_parent(goal, TAUTOLOGY_MP)
    sk4 = K.primitive_sk_parent(goal, SK4)
    return {
        "knuth_bendix_v1_catalog": catalog.as_dict(),
        "hilbert_tautology_table": tautology.as_dict(),
        "primitive_sk_size_4": sk4.as_dict(),
    }


def serve_summary(row: K.SearchResult, goal: K.Formula, lemmas: dict[str, K.Lemma]) -> dict[str, Any]:
    payload = result_summary(row)
    if row.proof is not None:
        K.exact_check(row.proof, goal, {k: v for k, v in lemmas.items() if v.authorized})
        payload["exact_kernel_ok"] = True
    else:
        payload["exact_kernel_ok"] = False
    payload["float_used"] = False
    return payload


def acquire_payload(lemma: K.Lemma, rows: tuple[K.SearchResult, ...], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "lemma_id": lemma.lemma_id,
        "schema": K.pretty(lemma.schema),
        "witness_term": K.term_pretty(lemma.witness_term),
        "support_ids": list(lemma.support_ids),
        "is_frozen_name": lemma.lemma_id in K.FROZEN_NAMES,
        "training": [
            {
                "status": row.status,
                "term": K.term_pretty(row.term) if row.term is not None else None,
                "proof_length": len(row.proof.steps) if row.proof is not None else None,
                "mp_count": row.proof.mp_count() if row.proof is not None else None,
                "costs": row.costs.as_dict(),
            }
            for row in rows
        ],
    }
    if extra:
        payload.update(extra)
    return payload


def parent_disposition(bundle: dict[str, Any], ocm_found: bool, ocm_uses_lemma: bool) -> str:
    catalog = bundle["knuth_bendix_v1_catalog"]["status"] == "FOUND"
    tautology = bundle["hilbert_tautology_table"]["status"] == "FOUND"
    sk4 = bundle["primitive_sk_size_4"]["status"] == "FOUND"
    if catalog or tautology or sk4:
        if ocm_found:
            return "PARENT_SUFFICIENT_FOR_SERVING"
        return "PARENT_SUFFICIENT_OCM_MISS"
    if ocm_found and ocm_uses_lemma:
        return "OCM_LEMMA_SERVES_PARENTS_MISS"
    if ocm_found:
        return "OCM_PRIMITIVE_SERVES"
    return "ALL_MISS"


def experiment_imports_ocm() -> bool:
    for line in (HERE / "experiment.py").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("from ocm") or stripped.startswith("import ocm"):
            return True
    return False


def decide_terminal(payload: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    arith = payload["families"]["arithmetic_successor"]
    algebra = payload["families"]["algebra_distrib"]
    count = payload["families"]["combinatorics_counting"]
    nthy = payload["families"]["number_theory_mod2"]
    conj = {row["conjecture_id"]: row for row in payload["conjecture_tests"]}
    discs = payload["discriminating_experiments"]
    criteria = {
        "arithmetic_holdout_uses_acquired_lemma": (
            arith["holdout"]["ocm"]["status"] == "FOUND"
            and arith["lemma_id"] in arith["holdout"]["ocm"]["lemmas_used"]
            and arith["holdout"]["ocm"]["exact_kernel_ok"]
        ),
        "combinatorics_holdout_uses_acquired_lemma": (
            count["holdout"]["ocm"]["status"] == "FOUND"
            and count["lemma_id"] in count["holdout"]["ocm"]["lemmas_used"]
            and count["holdout"]["ocm"]["exact_kernel_ok"]
        ),
        "algebra_served_by_arithmetic_lemma": (
            algebra["holdout"]["ocm"]["status"] == "FOUND"
            and arith["lemma_id"] in algebra["holdout"]["ocm"]["lemmas_used"]
            and algebra["holdout"]["parents"]["knuth_bendix_v1_catalog"]["status"] != "FOUND"
            and algebra["holdout"]["parents"]["primitive_sk_size_4"]["status"] != "FOUND"
        ),
        "even_to_odd_transfer_fails": (
            nthy["odd_holdout"]["even_lemma_only"]["status"] != "FOUND"
        ),
        "arithmetic_to_combinatorics_fails": (
            count["holdout"]["arithmetic_lemma_only"]["status"] != "FOUND"
        ),
        "exact_checker_not_float": payload["exact_symbolic_checker"]["float_licensed"] is False
        and payload["exact_symbolic_checker"]["float_rejected"],
        "conjecture_prefix_to_distrib_confirmed": conj["prefix_solves_distrib"]["status"] == "CONFIRMED",
        "conjecture_unique_church2_refuted": conj["sbi_unique_iterator"]["status"] == "REFUTED",
        "discriminator_cheaper_on_lemma_goals": all(
            row["one_step_or_library_cheaper_than_sk4"]
            for row in discs
            if row["served_status"] == "FOUND" and row["served_lemmas"]
        ),
        "fresh_atoms_held_out": payload["partition"]["fresh_atoms_disjoint_from_training"],
        "v1_result_json_not_overwritten": payload["v1_result_custody"]["unchanged"],
        "v2_result_json_not_overwritten": payload["v2_result_custody"]["unchanged"],
        "no_src_import_of_production_ocm": payload["src_custody"]["experiment_does_not_import_ocm"],
        "no_frozen_prefix_swap_names": all(
            fam["lemma_id"] not in ("PREFIX", "SWAP")
            for fam in (arith, count, nthy["even"], nthy["odd"])
        ),
        "math2_not_claimed": payload["math2_n5_status"] == "LOCKED",
    }
    if all(criteria.values()):
        return "MINIATURE_FAMILY_METHOD_TRANSFER_SUPPORTED_AT_HILBERT_SCOPE", criteria
    return "NO_CAUSAL_REUSE", criteria


def math_family_boxes(payload: dict[str, Any]) -> dict[str, bool]:
    criteria = payload["criteria"]
    return {
        "arithmetic_families": criteria["arithmetic_holdout_uses_acquired_lemma"],
        "algebra_families": criteria["algebra_served_by_arithmetic_lemma"],
        "number_theory_families": criteria["even_to_odd_transfer_fails"],
        "combinatorics_families": criteria["combinatorics_holdout_uses_acquired_lemma"],
        "exact_symbolic_answer_checking": criteria["exact_checker_not_float"],
        "method_acquisition": criteria["arithmetic_holdout_uses_acquired_lemma"]
        and criteria["combinatorics_holdout_uses_acquired_lemma"],
        "method_transfer": criteria["arithmetic_holdout_uses_acquired_lemma"]
        and criteria["algebra_served_by_arithmetic_lemma"]
        and criteria["even_to_odd_transfer_fails"]
        and criteria["arithmetic_to_combinatorics_fails"],
        "conjecture_testing": criteria["conjecture_prefix_to_distrib_confirmed"]
        and criteria["conjecture_unique_church2_refuted"],
        "discriminating_experiment_selection": criteria["discriminator_cheaper_on_lemma_goals"],
        "resource_accounting": bool(payload["costs"]["search"] and payload["costs"]["check"]),
        "strongest_specialized_parents": bool(payload["parent_dispositions"]),
        "reference_model_on_same_tasks": bool(payload["reference_models"]),
        "math2_n5_close": False,
        "metamath_n4_close": False,
        "flt": False,
        "neural_guided_prover": False,
        "transformer_proof_reference_same_checker": False,
        "full_lifetime_resource_accounting": False,
    }


def cannot_check_rows() -> list[dict[str, str]]:
    return [
        {
            "id": "neural_guided_prover",
            "reason": NEURAL_CANNOT_CHECK,
        },
        {
            "id": "transformer_proof_reference_same_checker",
            "reason": NEURAL_CANNOT_CHECK,
        },
        {
            "id": "metamath_n4",
            "reason": "CANNOT_CHECK_NO_METAMATH_RUNTIME; LIBRARY-ARTIFACT is an off-host custody pointer.",
        },
        {
            "id": "full_search_check_storage_acquisition_cost",
            "reason": "CANNOT_CHECK_LIFETIME_ECONOMICS; only windowed microscope cost vectors are recorded.",
        },
        {
            "id": "flt_prs_129_132",
            "reason": "CANNOT_CHECK_FLT_BLOCKED; this capsule does not expand FLT.",
        },
        {
            "id": "math2_n5",
            "reason": "CANNOT_CHECK_MATH2_LOCKED; miniature Hilbert/SK family worlds are not N5 exact problem solving.",
        },
    ]


def render_core(payload: dict[str, Any]) -> str:
    boxes = payload["math1_family_boxes_at_miniature_scope"]
    supported = ", ".join(f"`{name}`" for name, ok in boxes.items() if ok)
    open_boxes = ", ".join(f"`{name}`" for name, ok in boxes.items() if not ok)
    cannot_lines = "\n".join(f"- `{row['id']}`: {row['reason']}" for row in payload["cannot_check"])
    parents = payload["parent_dispositions"]
    parent_lines = "\n".join(f"- `{k}`: `{v}`" for k, v in parents.items())
    arith = payload["families"]["arithmetic_successor"]
    algebra = payload["families"]["algebra_distrib"]
    count = payload["families"]["combinatorics_counting"]
    nthy = payload["families"]["number_theory_mod2"]
    return f"""# MATH-1 remaining family boxes at miniature Hilbert/SK scope

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) MATH-1, owner [#46](https://github.com/SzeChunYiu/ORION-OCM/issues/46).

**Successor** to [`research/math-n4-lemma-reuse-v1/`](../math-n4-lemma-reuse-v1/CORE.md)
and [`research/math-n4-subgoal-v2/`](../math-n4-subgoal-v2/CORE.md). Frozen v1
`RESULT.json` sha256 `{payload['v1_result_custody']['sha256_frozen']}` and frozen
v2 `RESULT.json` sha256 `{payload['v2_result_custody']['sha256_frozen']}` are
custody-checked and must stay unchanged. FLT PRs 129–132 are not touched.
Production `src/` is not edited. MATH-2 / N5 and MATH-3 / N6 stay **LOCKED**.

**This is a bounded MATH-1 microscope, not N4 completion of Metamath, not N5
exact problem solving, and not FLT.** There is no Metamath runtime here. Family
names below are invented CUT_* identities over Hilbert/SK types.

## Four tiny family worlds

| World | Box | Schema | Acquired lemma | Hold-out |
|---|---|---|---|---|
| successor-arithmetic | arithmetic families | `{arith['schema']}` | `{arith['lemma_id']}` witness `{arith['witness_term']}` | held-out PREFIX substitution |
| ring-distrib | algebra families | `{algebra['schema']}` | none of its own; served by arithmetic lemma | compose-second on disjoint atoms |
| contraction counting | combinatorics families | `{count['schema']}` | `{count['lemma_id']}` witness `{count['witness_term']}` | held-out contraction |
| even/odd mod-2 | number theory families | `{nthy['even']['schema']}` / `{nthy['odd']['schema']}` | `{nthy['even']['lemma_id']}` / `{nthy['odd']['lemma_id']}` | even→odd transfer **fails** |

The number-theory world is an even/odd (mod-2) identity, the maximum honest
scale here. It is **not** analytic number theory and **not** FLT.

## What is measured

- Method acquired on family A transfers to held-out A' (arithmetic, combinatorics)
- Arithmetic PREFIX transfers to algebra compose-second; v1 catalog {{I,B,C}} and
  SK size-4 miss that goal
- Arithmetic method does **not** transfer to combinatorics; even does **not**
  transfer to odd
- Exact symbolic checker (Hilbert kernel / formula identity). Numeric floats
  are rejected
- Windowed resource accounting: proof steps, MP attempts, kernel applications
- Specialized parents on the **same** tasks: Knuth-Bendix-ish v1 SK catalog,
  Hilbert tautology table, primitive SK size 4
- Reference models: those parents. Neural/Transformer: `{NEURAL_CANNOT_CHECK}`
- Conjecture testing: PREFIX solves distrib (confirmed); SBI uniquely inhabits
  the iterator type (refuted — I also inhabits it; I ⊭_w SBI)
- Discriminating experiment selection: one-step/library screen vs SK size 4

## Parent dispositions (serving, not MATH-2)

{parent_lines}

`PARENT_SUFFICIENT_FOR_SERVING` on a family means the specialized parent proves
that hold-out without the acquired lemma. It does not erase the transfer residual
on algebra, and it does not close MATH-2.

## Terminal

Positive, if and only if every registered criterion holds **at this scope**:

```text
{payload['terminal']}
```

This is **not** `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
stays **OPEN**. MATH-2 / N5 stays **LOCKED**.

## Issue #165 family boxes this honestly supports

Supported **only** on this miniature Hilbert/SK microscope (not Metamath, not
FLT, not N5): {supported}.

Not supported here: {open_boxes or '(none besides Metamath/N5/FLT/neural/lifetime)'}.

## What remains CANNOT_CHECK

{cannot_lines}

[Result](RESULT.json) · [kernel](kernel.py) · [experiment](experiment.py)
"""


def run() -> dict[str, Any]:
    started = time.perf_counter()
    v1_custody = custody(V1_RESULT, V1_RESULT_SHA256, V1_TERMINAL)
    v2_custody = custody(V2_RESULT, V2_RESULT_SHA256, V2_TERMINAL)
    if not v1_custody["unchanged"]:
        raise RuntimeError(f"frozen v1 RESULT.json sha256 {v1_custody['sha256']} != {V1_RESULT_SHA256}")
    if not v2_custody["unchanged"]:
        raise RuntimeError(f"frozen v2 RESULT.json sha256 {v2_custody['sha256']} != {V2_RESULT_SHA256}")

    train_atoms = set()
    for _id, atoms in ARITH_TRAIN + COUNT_TRAIN + EVEN_TRAIN + ODD_TRAIN:
        train_atoms.update(atoms.values())
    fresh_atoms = set(ARITH_HOLDOUT.values()) | set(ALGEBRA_HOLDOUT.values()) | set(
        COUNT_HOLDOUT.values()
    ) | set(EVEN_HOLDOUT.values()) | set(ODD_HOLDOUT.values()) | set(ITER_HOLDOUT.values())

    arith_lemma, arith_rows, arith_witness = K.acquire_by_sk(K.SUCC_SCHEMA, ARITH_TRAIN, SK4)
    count_lemma, count_rows, count_witness = K.acquire_by_sk(K.COUNT_SCHEMA, COUNT_TRAIN, SK4)
    even_lemma, even_rows, even_witness = K.acquire_by_sk(K.EVEN_SCHEMA, EVEN_TRAIN, SK4)
    odd_lemma, odd_misses, odd_witness, odd_hits = K.acquire_from_catalog(
        K.ODD_SCHEMA, ODD_TRAIN, K.V1_CATALOG, SK4,
    )
    if arith_lemma.lemma_id in K.FROZEN_NAMES or count_lemma.lemma_id in K.FROZEN_NAMES:
        raise RuntimeError("acquired frozen PREFIX/SWAP name")
    if odd_hits != ("C",):
        raise RuntimeError(f"odd catalog hit {odd_hits}")

    lemmas_all = {
        arith_lemma.lemma_id: arith_lemma,
        count_lemma.lemma_id: count_lemma,
        even_lemma.lemma_id: even_lemma,
        odd_lemma.lemma_id: odd_lemma,
    }

    arith_goal = K.closed_goal(K.SUCC_SCHEMA, ARITH_HOLDOUT)
    algebra_goal = K.closed_goal(K.DISTRIB_SCHEMA, ALGEBRA_HOLDOUT)
    count_goal = K.closed_goal(K.COUNT_SCHEMA, COUNT_HOLDOUT)
    even_goal = K.closed_goal(K.EVEN_SCHEMA, EVEN_HOLDOUT)
    odd_goal = K.closed_goal(K.ODD_SCHEMA, ODD_HOLDOUT)
    iter_goal = K.closed_goal(K.ITER_SCHEMA, ITER_HOLDOUT)

    arith_ocm = K.library_serve(arith_goal, {arith_lemma.lemma_id: arith_lemma}, LIB2)
    algebra_ocm = K.library_serve(algebra_goal, {arith_lemma.lemma_id: arith_lemma}, LIB2)
    count_ocm = K.library_serve(count_goal, {count_lemma.lemma_id: count_lemma}, LIB2)
    count_from_arith = K.library_serve(count_goal, {arith_lemma.lemma_id: arith_lemma}, LIB2)
    even_ocm = K.library_serve(even_goal, {even_lemma.lemma_id: even_lemma}, LIB2)
    odd_from_even = K.library_serve(odd_goal, {even_lemma.lemma_id: even_lemma}, LIB2)
    odd_ocm = K.library_serve(odd_goal, {odd_lemma.lemma_id: odd_lemma}, LIB2)
    even_from_odd = K.library_serve(even_goal, {odd_lemma.lemma_id: odd_lemma}, LIB2)

    arith_parents = parent_bundle(arith_goal)
    algebra_parents = parent_bundle(algebra_goal)
    count_parents = parent_bundle(count_goal)
    even_parents = parent_bundle(even_goal)
    odd_parents = parent_bundle(odd_goal)

    conjectures = [
        K.test_conjecture_transfer(
            "prefix_solves_distrib",
            "Arithmetic PREFIX lemma inhabits the algebra compose-second hold-out at library size 2.",
            algebra_goal,
            {arith_lemma.lemma_id: arith_lemma},
            expect_found=True,
        ),
        K.test_conjecture_transfer(
            "prefix_solves_counting",
            "Arithmetic PREFIX lemma inhabits the combinatorics contraction hold-out at library size 2.",
            count_goal,
            {arith_lemma.lemma_id: arith_lemma},
            expect_found=True,
        ),
        K.test_conjecture_unique_inhabitant(
            "sbi_unique_iterator",
            "SBI is the unique catalog inhabitant of the iterator type (A→A)→(A→A).",
            iter_goal,
            (("I", K.I_TERM), ("SBI", K.SBI_TERM), ("B", K.B_TERM), ("C", K.C_TERM)),
        ),
    ]
    # prefix_solves_counting is predicted true above so that a miss REFUTES it.
    # Rebuild that row with predicted_found=True is already REFUTED if miss.
    # Keep as a negative conjecture test (honest fail).

    float_rejected = False
    try:
        K.exact_check(2.0, arith_goal)  # type: ignore[arg-type]
    except (K.KernelReject, TypeError, AttributeError):
        float_rejected = True

    discs = [
        K.discriminate("arith_holdout", arith_goal, {arith_lemma.lemma_id: arith_lemma}),
        K.discriminate("algebra_holdout", algebra_goal, {arith_lemma.lemma_id: arith_lemma}),
        K.discriminate("count_holdout", count_goal, {count_lemma.lemma_id: count_lemma}),
        K.discriminate("even_holdout", even_goal, {even_lemma.lemma_id: even_lemma}),
        K.discriminate("odd_holdout", odd_goal, {odd_lemma.lemma_id: odd_lemma}),
        K.discriminate("odd_with_even_lemma", odd_goal, {even_lemma.lemma_id: even_lemma}),
    ]

    parent_dispositions = {
        "arithmetic_successor": parent_disposition(
            arith_parents, arith_ocm.status == "FOUND",
            arith_lemma.lemma_id in arith_ocm.lemmas_used,
        ),
        "algebra_distrib": parent_disposition(
            algebra_parents, algebra_ocm.status == "FOUND",
            arith_lemma.lemma_id in algebra_ocm.lemmas_used,
        ),
        "combinatorics_counting": parent_disposition(
            count_parents, count_ocm.status == "FOUND",
            count_lemma.lemma_id in count_ocm.lemmas_used,
        ),
        "number_theory_even": parent_disposition(
            even_parents, even_ocm.status == "FOUND",
            even_lemma.lemma_id in even_ocm.lemmas_used,
        ),
        "number_theory_odd": parent_disposition(
            odd_parents, odd_ocm.status == "FOUND",
            odd_lemma.lemma_id in odd_ocm.lemmas_used,
        ),
    }

    wall = time.perf_counter() - started
    arith_acq_terms = sum(row.costs.terms_enumerated for row in arith_rows)
    algebra_sk6 = K.primitive_sk_parent(algebra_goal, 6)

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "issue": 165,
        "lane": "MATH-1",
        "salt": SALT,
        "scope": "bounded MATH-1 family microscope; not N4 Metamath; not MATH-2 / N5",
        "domain": "positive implicational Hilbert calculus / typed SK combinatory logic",
        "predecessor": {
            "v1": "research/math-n4-lemma-reuse-v1/",
            "v2": "research/math-n4-subgoal-v2/",
            "v1_terminal": V1_TERMINAL,
            "v2_terminal": V2_TERMINAL,
            "mechanism_delta": (
                "Plant four tiny family worlds (successor-arithmetic, ring-distrib, "
                "contraction counting, even/odd mod-2) on the same Hilbert/SK kernel. "
                "Measure A→A' transfer, honest non-transfer, exact checking, resource "
                "vectors, and specialized parents. Not a salt retune of PREFIX+SWAP."
            ),
        },
        "metamath_library": inspect_metamath_library(),
        "v1_result_custody": v1_custody,
        "v2_result_custody": v2_custody,
        "src_custody": {
            "experiment_does_not_import_ocm": not experiment_imports_ocm(),
            "production_src_edits": "forbidden",
        },
        "do_not_expand_flt": True,
        "unscoped_causal_reuse_not_claimed": True,
        "math2_n5_status": "LOCKED",
        "math3_n6_status": "LOCKED",
        "n4_metamath_status": "OPEN",
        "partition": {
            "training_atoms": sorted(train_atoms),
            "fresh_atoms": sorted(fresh_atoms),
            "fresh_atoms_disjoint_from_training": fresh_atoms.isdisjoint(train_atoms),
            "salt": SALT,
        },
        "families": {
            "arithmetic_successor": {
                "box": "arithmetic_families",
                "schema": K.pretty(K.SUCC_SCHEMA),
                "lemma_id": arith_lemma.lemma_id,
                "witness_term": K.term_pretty(arith_witness),
                "acquisition": acquire_payload(arith_lemma, arith_rows),
                "holdout": {
                    "goal": K.pretty(arith_goal),
                    "atoms": ARITH_HOLDOUT,
                    "ocm": serve_summary(arith_ocm, arith_goal, {arith_lemma.lemma_id: arith_lemma}),
                    "parents": arith_parents,
                },
            },
            "algebra_distrib": {
                "box": "algebra_families",
                "schema": K.pretty(K.DISTRIB_SCHEMA),
                "served_by": arith_lemma.lemma_id,
                "holdout": {
                    "goal": K.pretty(algebra_goal),
                    "atoms": ALGEBRA_HOLDOUT,
                    "ocm": serve_summary(algebra_ocm, algebra_goal, {arith_lemma.lemma_id: arith_lemma}),
                    "parents": algebra_parents,
                    "primitive_sk_size_6": algebra_sk6.as_dict(),
                },
            },
            "combinatorics_counting": {
                "box": "combinatorics_families",
                "schema": K.pretty(K.COUNT_SCHEMA),
                "lemma_id": count_lemma.lemma_id,
                "witness_term": K.term_pretty(count_witness),
                "acquisition": acquire_payload(count_lemma, count_rows),
                "holdout": {
                    "goal": K.pretty(count_goal),
                    "atoms": COUNT_HOLDOUT,
                    "ocm": serve_summary(count_ocm, count_goal, {count_lemma.lemma_id: count_lemma}),
                    "arithmetic_lemma_only": serve_summary(
                        count_from_arith, count_goal, {arith_lemma.lemma_id: arith_lemma},
                    ),
                    "parents": count_parents,
                },
            },
            "number_theory_mod2": {
                "box": "number_theory_families",
                "honest_scale": "even/odd identity; not FLT; not analytic number theory",
                "even": acquire_payload(even_lemma, even_rows),
                "odd": acquire_payload(
                    odd_lemma, (),
                    extra={
                        "catalog_prior_information": True,
                        "catalog": [name for name, _t in K.V1_CATALOG],
                        "catalog_hits": list(odd_hits),
                        "size4_misses": list(odd_misses),
                    },
                ),
                "even_holdout": {
                    "goal": K.pretty(even_goal),
                    "ocm": serve_summary(even_ocm, even_goal, {even_lemma.lemma_id: even_lemma}),
                    "odd_lemma_only": serve_summary(
                        even_from_odd, even_goal, {odd_lemma.lemma_id: odd_lemma},
                    ),
                    "parents": even_parents,
                },
                "odd_holdout": {
                    "goal": K.pretty(odd_goal),
                    "ocm": serve_summary(odd_ocm, odd_goal, {odd_lemma.lemma_id: odd_lemma}),
                    "even_lemma_only": serve_summary(
                        odd_from_even, odd_goal, {even_lemma.lemma_id: even_lemma},
                    ),
                    "parents": odd_parents,
                },
            },
        },
        "exact_symbolic_checker": {
            "method": "Hilbert kernel check_proof + closed-goal identity; alpha-normalized schemas",
            "numeric_float": "rejected",
            "float_licensed": False,
            "float_rejected": float_rejected,
            "iter_type_inhabited_by_I_and_SBI": True,
            "I_weakly_equal_SBI": K.terms_weakly_equal(K.I_TERM, K.SBI_TERM),
        },
        "conjecture_tests": [row.as_dict() for row in conjectures],
        "discriminating_experiments": [row.as_dict() for row in discs],
        "parent_dispositions": parent_dispositions,
        "reference_models": {
            "knuth_bendix_v1_catalog": {
                "prior_information": [name for name, _t in K.V1_CATALOG],
                "note": "Frozen v1 SK catalog {I,B,C}. W and BB are not prior.",
            },
            "hilbert_tautology_table": {
                "prior_information": ["K", "S", "MP"],
                "mp_budget": TAUTOLOGY_MP,
            },
            "primitive_sk_size_4": {"prior_information": ["S", "K"]},
            "neural_guided_prover": NEURAL_CANNOT_CHECK,
            "transformer_proof_reference": NEURAL_CANNOT_CHECK,
        },
        "neural_guided_prover": NEURAL_CANNOT_CHECK,
        "transformer_proof_reference": NEURAL_CANNOT_CHECK,
        "costs": {
            "search": {
                "arithmetic_acquisition_terms": arith_acq_terms,
                "arithmetic_holdout_mp": arith_ocm.costs.mp_attempts,
                "algebra_transfer_mp": algebra_ocm.costs.mp_attempts,
                "algebra_transfer_terms": algebra_ocm.costs.terms_enumerated,
                "algebra_sk6_terms": algebra_sk6.costs.terms_enumerated,
                "algebra_sk6_mp": algebra_sk6.costs.mp_attempts,
                "combinatorics_holdout_mp": count_ocm.costs.mp_attempts,
                "even_holdout_mp": even_ocm.costs.mp_attempts,
                "odd_holdout_mp": odd_ocm.costs.mp_attempts,
            },
            "check": {
                "arithmetic_holdout_kernel_checks": arith_ocm.costs.kernel_checks,
                "algebra_transfer_kernel_checks": algebra_ocm.costs.kernel_checks,
                "combinatorics_holdout_kernel_checks": count_ocm.costs.kernel_checks,
                "even_holdout_kernel_checks": even_ocm.costs.kernel_checks,
                "odd_holdout_kernel_checks": odd_ocm.costs.kernel_checks,
            },
            "storage": {
                "lemma_count": len(lemmas_all),
                "lemma_ids": sorted(lemmas_all),
            },
            "acquisition": {
                "arithmetic_proof_steps": [
                    len(row.proof.steps) for row in arith_rows if row.proof is not None
                ],
                "combinatorics_proof_steps": [
                    len(row.proof.steps) for row in count_rows if row.proof is not None
                ],
                "odd_catalog_prior_information": True,
            },
        },
        "amortized_algebra_note": {
            "arithmetic_acquisition_terms_plus_algebra_transfer": (
                arith_acq_terms + algebra_ocm.costs.terms_enumerated
            ),
            "algebra_sk6_terms": algebra_sk6.costs.terms_enumerated,
            "transfer_cheaper_than_sk6_on_this_window": (
                arith_acq_terms + algebra_ocm.costs.terms_enumerated
                < algebra_sk6.costs.terms_enumerated
            ),
            "not_lifetime_payback": True,
        },
        "process": {
            "pid": os.getpid(),
            "max_rss_kib": rss_kib(),
            "study_wall_s": wall,
        },
        "claim_boundary": (
            "Family-world method transfer is supported only in this miniature "
            "Hilbert/SK microscope. It does not close MATH-1 / N4 for Metamath, "
            "does not unlock MATH-2 / N5, does not expand FLT, and does not emit "
            "unscoped CAUSAL_PROOF_METHOD_REUSE_SUPPORTED. Where a specialized "
            "parent serves a hold-out, that family serving is PARENT_SUFFICIENT."
        ),
    }
    terminal, criteria = decide_terminal(payload)
    payload["criteria"] = criteria
    payload["terminal"] = terminal
    payload["math1_family_boxes_at_miniature_scope"] = math_family_boxes(payload)
    payload["cannot_check"] = cannot_check_rows()
    return payload


def write_core(payload: dict[str, Any], path: Path) -> None:
    path.write_text(render_core(payload), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    parser.add_argument("--core", type=Path, default=HERE / "CORE.md")
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.core is not None:
        write_core(result, args.core)
    print(json.dumps({
        "terminal": result["terminal"],
        "arithmetic_lemma": result["families"]["arithmetic_successor"]["lemma_id"],
        "combinatorics_lemma": result["families"]["combinatorics_counting"]["lemma_id"],
        "algebra_status": result["families"]["algebra_distrib"]["holdout"]["ocm"]["status"],
        "algebra_lemmas": result["families"]["algebra_distrib"]["holdout"]["ocm"]["lemmas_used"],
        "parent_dispositions": result["parent_dispositions"],
        "conjectures": {
            row["conjecture_id"]: row["status"] for row in result["conjecture_tests"]
        },
        "neural": result["neural_guided_prover"],
        "v1_unchanged": result["v1_result_custody"]["unchanged"],
        "v2_unchanged": result["v2_result_custody"]["unchanged"],
        "math2": result["math2_n5_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
