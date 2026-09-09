"""MATH-1 / N4 remaining-gate microscope: subgoal discovery + lemma introduction.

Successor to research/math-n4-lemma-reuse-v1/. Does not retune v1 salts, does not
overwrite that capsule's RESULT.json, does not close Metamath N4, and does not
touch FLT PRs 129-132. Invented intermediates are CUT_* names, never PREFIX/SWAP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "src"
V1 = REPO / "research" / "math-n4-lemma-reuse-v1"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

import kernel as K  # noqa: E402

SCHEMA = "math-n4-subgoal.result.v2"
V1_RESULT = V1 / "RESULT.json"
V1_RESULT_SHA256 = "cbcae02402fb7f73ec2f5cde25b4f922a141a8266f4ff603fc2d23c71aeb77cc"
V1_TERMINAL = "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED_AT_MINIATURE_SCOPE"
LIBRARY_SCHEMA = "math-n4-subgoal.library.v2"
PRIMITIVE_SIZE = 4
LIBRARY_SIZE = 2
FROZEN_NAMES = tuple(sorted(K.FROZEN_TRAINING_LEMMA_NAMES))
DISCOVERY_IDS = ("task:bb-sa-ta-wa-ya", "task:bb-sb-tb-wb-yb")
FRESH_ID = "task:bb-e-f-g-h"
TRAIN_ATOMS_1 = {"A": "sa", "B": "ta", "C": "wa", "D": "ya"}
TRAIN_ATOMS_2 = {"A": "sb", "B": "tb", "C": "wb", "D": "yb"}
FRESH_ATOMS = {"A": "e", "B": "f", "C": "g", "D": "h"}
SALT = "orion-ocm-math-n4-subgoal-v2"
LIBRARY_ARTIFACT = (
    REPO / "research" / "ordinary-goal-cohort-result-v1"
    / "records" / "qualification-01" / "LIBRARY-ARTIFACT.json"
)
NEURAL_CANNOT_CHECK = "CANNOT_CHECK_NO_NN_LIBRARY"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rss_kib() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def goal_compose(atoms: dict[str, str]) -> K.Formula:
    return K.instantiate_schema(K.COMPOSE_SECOND_SCHEMA, atoms)


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


def neural_status() -> str:
    return NEURAL_CANNOT_CHECK


def v1_result_custody() -> dict[str, Any]:
    present = V1_RESULT.is_file()
    digest = sha256_file(V1_RESULT) if present else None
    terminal = None
    if present:
        terminal = json.loads(V1_RESULT.read_text(encoding="utf-8")).get("terminal")
    return {
        "path": str(V1_RESULT.relative_to(REPO)),
        "present": present,
        "sha256": digest,
        "sha256_frozen": V1_RESULT_SHA256,
        "unchanged": digest == V1_RESULT_SHA256,
        "terminal": terminal,
        "terminal_frozen": V1_TERMINAL,
    }


def result_summary(row: K.SearchResult) -> dict[str, Any]:
    payload = row.as_dict()
    payload["conclusion"] = K.pretty(row.proof.conclusion) if row.proof is not None else None
    payload["subgoal_count"] = len(row.subgoals)
    payload["subgoals"] = [K.pretty(s) for s in row.subgoals[:8]]
    return payload


def persist_library(path: Path, lemmas: dict[str, K.Lemma]) -> int:
    payload = {
        "schema": LIBRARY_SCHEMA,
        "lemmas": [K.lemma_to_json(lemma) for lemma in lemmas.values()],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path.stat().st_size


def load_library(path: Path) -> dict[str, K.Lemma]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    lemmas = {}
    for row in payload["lemmas"]:
        lemma = K.lemma_from_json(row)
        lemmas[lemma.lemma_id] = lemma
    return lemmas


def revoke_support(lemmas: dict[str, K.Lemma], withdrawn: set[str]) -> dict[str, K.Lemma]:
    out = {}
    for lemma_id, lemma in lemmas.items():
        authorized = lemma.authorized and not (set(lemma.support_ids) & withdrawn)
        out[lemma_id] = K.Lemma(
            lemma_id=lemma.lemma_id,
            schema=lemma.schema,
            witness_term=lemma.witness_term,
            support_ids=lemma.support_ids,
            authorized=authorized,
        )
    return out


def authorized_only(lemmas: dict[str, K.Lemma]) -> dict[str, K.Lemma]:
    return {k: v for k, v in lemmas.items() if v.authorized}


def consume(goal: K.Formula, lemmas: dict[str, K.Lemma]) -> K.SearchResult:
    library = authorized_only(lemmas)
    constants = ("S", "K") + tuple(library.keys())
    return K.inhabit_well_typed(goal, constants, library, LIBRARY_SIZE)


def restart_consumer(library_path: Path, goal: K.Formula) -> dict[str, Any]:
    goal_path = library_path.parent / "goal.json"
    out_path = library_path.parent / "restart-result.json"
    goal_path.write_text(json.dumps(K.formula_to_json(goal)) + "\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [
            sys.executable, "-B", str(HERE / "experiment.py"),
            "--restart-consumer",
            "--library", str(library_path),
            "--goal", str(goal_path),
            "--out", str(out_path),
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO),
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"restart failed rc={proc.returncode}: {proc.stderr[-2000:]} {proc.stdout[-2000:]}"
        )
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    payload["returncode"] = proc.returncode
    payload["parent_pid"] = os.getpid()
    return payload


def run_restart_consumer(library: Path, goal_path: Path) -> dict[str, Any]:
    lemmas = load_library(library)
    goal = K.json_to_formula(json.loads(goal_path.read_text(encoding="utf-8")))
    row = consume(goal, lemmas)
    return {
        "pid": os.getpid(),
        "status": row.status,
        "lemmas_used": list(row.lemmas_used),
        "one_step_hits": list(row.one_step_hits),
        "proof_length": len(row.proof.steps) if row.proof else None,
        "mp_count": row.proof.mp_count() if row.proof else None,
        "term": K.term_pretty(row.term) if row.term is not None else None,
        "kernel_checks": row.costs.kernel_checks,
        "subgoals": [K.pretty(s) for s in K.intermediate_formulas(row.proof, goal)] if row.proof else [],
    }


def identity_distractor() -> K.Lemma:
    for ident in K.collect_primitive_identities(PRIMITIVE_SIZE):
        if K.unify_schema(K.IDENTITY_SCHEMA, ident.schema) is not None:
            return K.lemma_from_identity(ident, ("task:distractor-identity",))
    raise RuntimeError("IDENTITY-shaped primitive inhabitant missing")


def discover_on(task_id: str, atoms: dict[str, str]) -> dict[str, Any]:
    goal = goal_compose(atoms)
    started = time.perf_counter()
    row = K.subgoal_discover_and_finish(goal, (task_id,), PRIMITIVE_SIZE, LIBRARY_SIZE)
    if row.status != "FOUND" or row.invented_lemma is None or row.invented_identity is None:
        raise RuntimeError(f"discovery failed on {task_id}")
    lemma = row.invented_lemma
    if lemma.lemma_id in K.FROZEN_TRAINING_LEMMA_NAMES:
        raise RuntimeError("invented frozen training lemma name")
    if K.pretty(K.alpha_normalize(lemma.schema)) == K.pretty(K.alpha_normalize(goal)):
        raise RuntimeError("invented lemma is the goal")
    proof = row.finish.proof
    if proof is None:
        raise RuntimeError(f"discovery produced no proof on {task_id}")
    intermediates = K.intermediate_formulas(proof, goal)
    if not intermediates:
        raise RuntimeError(f"discovery proof has no intermediate on {task_id}")
    mapping = {var: f"h{i}" for i, var in enumerate(K.atoms_of(lemma.schema))}
    holdout = K.instantiate_schema(lemma.schema, mapping)
    holdout_proof = K.reconstruct_proof(lemma.witness_term, holdout)
    K.check_proof(holdout_proof)
    return {
        "task_id": task_id,
        "goal": K.pretty(goal),
        "atoms": atoms,
        "discovery": row.as_dict(),
        "lemma": lemma,
        "identity": row.invented_identity,
        "intermediates": [K.pretty(s) for s in intermediates],
        "term": K.term_pretty(row.finish.term) if row.finish.term is not None else None,
        "lemmas_used": list(row.finish.lemmas_used),
        "one_step_hits": list(row.one_step_hits),
        "holdout": {
            "goal": K.pretty(holdout),
            "proof_length": len(holdout_proof.steps),
            "kernel_ok": K.check_proof(holdout_proof) == holdout,
        },
        "wall_s": time.perf_counter() - started,
        "costs": row.costs.as_dict(),
        "finish_costs": row.finish.costs.as_dict(),
    }


def decide_terminal(payload: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    fresh = payload["fresh"]
    invented_id = payload["invented_lemma"]["lemma_id"]
    invoked = invented_id in set(fresh["with_cut"]["lemmas_used"])
    found = fresh["with_cut"]["status"] == "FOUND"
    one_step_zero = list(fresh["one_step_hits"]) == []
    primitive_fail = fresh["primitive"]["status"] != "FOUND"
    ablation_fail = fresh["ablation"]["status"] != "FOUND"
    discovery_ok = all(
        row["discovery"]["status"] == "FOUND"
        and row["discovery"]["invented_lemma_id"] == invented_id
        and row["discovery"]["invented_lemma_id"] not in FROZEN_NAMES
        and row["one_step_hits"] == []
        and row["intermediates"]
        for row in payload["discovery_tasks"]
    )
    schema_not_goal = (
        payload["invented_lemma"]["schema"] != payload["partition"]["fresh_goal"]
        and payload["invented_lemma"]["schema_alpha"] != payload["partition"]["fresh_goal_alpha"]
    )
    restart_ok = (
        payload["restart"]["status"] == "FOUND"
        and invented_id in set(payload["restart"]["lemmas_used"])
        and payload["restart"]["pid"] != os.getpid()
    )
    revoke_ok = payload["revocation"]["revoke_discovery_support"]["status"] != "FOUND"
    restore_ok = payload["revocation"]["restore"]["status"] == "FOUND"
    custody_ok = payload["v1_result_custody"]["unchanged"]
    not_frozen_name = invented_id not in FROZEN_NAMES
    representation_grew = invented_id in payload["acquisition"]["operators_after"]
    holdout_disjoint = payload["partition"]["fresh_atoms_disjoint_from_discovery"]
    criteria = {
        "discovery_invents_cut_not_frozen_name": discovery_ok and not_frozen_name,
        "invented_identity_is_not_the_goal": schema_not_goal,
        "fresh_found_with_invented_lemma": found and invoked,
        "one_step_zero_on_composition": one_step_zero,
        "primitive_cannot_at_library_size": primitive_fail,
        "ablation_loses_proof": ablation_fail,
        "os_process_restart": restart_ok,
        "revoke_support_restores_primitive": revoke_ok,
        "restore_returns_lemma_use": restore_ok,
        "representation_introduced_named_lemma": representation_grew,
        "fresh_atoms_held_out": holdout_disjoint,
        "v1_result_json_not_overwritten": custody_ok,
        "no_src_import_of_production_ocm": payload["src_custody"]["experiment_does_not_import_ocm"],
    }
    if all(criteria.values()):
        return "CAUSAL_SUBGOAL_LEMMA_INTRODUCTION_SUPPORTED_AT_MINIATURE_SCOPE", criteria
    return "NO_CAUSAL_REUSE", criteria


def render_core(payload: dict[str, Any]) -> str:
    invented = payload["invented_lemma"]
    boxes = payload["math1_boxes_at_miniature_scope"]
    cannot = payload["cannot_check"]
    supported = ", ".join(f"`{name}`" for name, ok in boxes.items() if ok)
    open_boxes = ", ".join(f"`{name}`" for name, ok in boxes.items() if not ok)
    cannot_lines = "\n".join(f"- `{row['id']}`: {row['reason']}" for row in cannot)
    return f"""# MATH-1 / N4 subgoal discovery and lemma introduction at miniature Hilbert scope

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) MATH-1, owner [#46](https://github.com/SzeChunYiu/ORION-OCM/issues/46).

**Successor** to [`research/math-n4-lemma-reuse-v1/`](../math-n4-lemma-reuse-v1/CORE.md)
(terminal `{payload['v1_result_custody']['terminal_frozen']}`). This capsule changes
**mechanism**, not v1 salts. Frozen v1 `RESULT.json` sha256
`{payload['v1_result_custody']['sha256_frozen']}` is custody-checked and must stay
unchanged. FLT PRs 129–132 are not touched. Production `src/` is not edited.

**This is a bounded MATH-1 microscope, not N4 completion of Metamath, and not
FLT.** There is no Metamath runtime here. The LIBRARY-ARTIFACT is an off-host
custody pointer.

## Mechanism change versus v1

v1 independently acquired frozen names `PREFIX` and `SWAP`, then composed them
on a held-out suffix. One-step hits were 0; revoke/ablation worked; neural was
`CANNOT_CHECK`.

v2 does **not** mint or consume `PREFIX`/`SWAP`. A registered kernel:

1. Enumerates primitive SK identities that are not K/S axiom schemas and not
   the goal.
2. Names a new lemma `CUT_*` from a proved identity (alpha-normalized schema).
3. Finishes the training goal by using that named lemma as an intermediate.
4. Reuses the same named lemma on a fresh theorem with held-out atoms.
5. Withdraws exact training-support IDs and restores primitive search.

## Domain

Positive implicational Hilbert calculus: axiom schemas K and S, rule MP.
Combinatory SK terms are Hilbert proofs. The v1 kernel checks every selected
proof. New population salt `{SALT}`.

| Object | Identity |
|---|---|
| Invented lemma | `{invented['lemma_id']}` |
| Invented schema | `{invented['schema']}` |
| Witness | `{invented['witness_term']}` (kernel-checked) |
| Discovery / reuse goal | `(A → (B → C)) → (A → ((D → B) → (D → C)))` (principal type of B B) |
| Frozen names refused | `PREFIX`, `SWAP` |
| Fresh atoms | `{', '.join(payload['partition']['fresh_atoms'])}` |

The invented schema is PREFIX-shaped, but the **lemma identity is not the
frozen name PREFIX**. That is the point of this successor.

## What is measured

- Subgoal discovery: intermediate lemma identity ≠ goal and ≠ frozen training
  lemma name, then the goal is finished
- Representation/lemma introduction: operators `{{K,S,MP}}` grow by `{invented['lemma_id']}`
- Fresh-theorem reuse of the introduced lemma
- Exact support revocation and restoration
- OS-process restart from a persisted library
- Retrieval parent: bag-of-symbols Jaccard after alpha-normalization
- Neural / Transformer parents: `{NEURAL_CANNOT_CHECK}`
- Windowed search / check / storage / acquisition costs on this microscope

## Terminal

Positive, if and only if every registered causal criterion holds **at this
scope**:

```text
{payload['terminal']}
```

This is **not** `CAUSAL_PROOF_METHOD_REUSE_SUPPORTED`. MATH-1 / N4 on Metamath
stays **OPEN**. MATH-2 / N5 and MATH-3 / N6 stay LOCKED.

## Issue #165 MATH-1 boxes this honestly supports

Supported **only** on this miniature Hilbert/SK microscope (not Metamath, not
FLT): {supported}.

Not supported here: {open_boxes or '(none at this scope besides Metamath/lifetime/neural)'}.

## What remains CANNOT_CHECK

{cannot_lines}

[Result](RESULT.json) · [kernel](kernel.py) · [experiment](experiment.py)
"""


def math1_boxes(payload: dict[str, Any]) -> dict[str, bool]:
    criteria = payload["criteria"]
    return {
        "subgoal_discovery": criteria["discovery_invents_cut_not_frozen_name"]
        and criteria["invented_identity_is_not_the_goal"],
        "representation_lemma_introduction": criteria["representation_introduced_named_lemma"]
        and criteria["fresh_found_with_invented_lemma"],
        "exact_support_revocation": criteria["revoke_support_restores_primitive"]
        and criteria["restore_returns_lemma_use"],
        "lemma_reuse": criteria["fresh_found_with_invented_lemma"],
        "unseen_composition": criteria["fresh_found_with_invented_lemma"]
        and criteria["one_step_zero_on_composition"],
        "fresh_theorem_family_reuse": criteria["fresh_atoms_held_out"]
        and criteria["fresh_found_with_invented_lemma"],
        "method_ablation": criteria["ablation_loses_proof"],
        "restart": criteria["os_process_restart"],
        "retrieval_prover": payload["retrieval_parent"]["method"].startswith("bag-of-symbols"),
        "symbolic_tactic_search_parent": True,
        "neural_guided_prover": False,
        "transformer_proof_reference_same_checker": False,
        "full_search_check_storage_acquisition_cost": False,
        "metamath_n4_close": False,
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
            "reason": "CANNOT_CHECK_NO_METAMATH_RUNTIME; LIBRARY-ARTIFACT is an off-host custody pointer. Unscoped CAUSAL_PROOF_METHOD_REUSE_SUPPORTED is not licensed.",
        },
        {
            "id": "full_search_check_storage_acquisition_cost",
            "reason": "CANNOT_CHECK_LIFETIME_ECONOMICS; only windowed microscope cost vectors are recorded.",
        },
        {
            "id": "flt_prs_129_132",
            "reason": "CANNOT_CHECK_FLT_BLOCKED; this capsule does not expand FLT.",
        },
    ]


def experiment_imports_ocm() -> bool:
    for line in (HERE / "experiment.py").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("from ocm") or stripped.startswith("import ocm"):
            return True
    return False


def run() -> dict[str, Any]:
    started = time.perf_counter()
    library_note = inspect_metamath_library()
    custody = v1_result_custody()
    if not custody["unchanged"]:
        raise RuntimeError(
            f"frozen v1 RESULT.json sha256 {custody['sha256']} != {V1_RESULT_SHA256}"
        )

    discovery_specs = (
        (DISCOVERY_IDS[0], TRAIN_ATOMS_1),
        (DISCOVERY_IDS[1], TRAIN_ATOMS_2),
    )
    discovery_rows = [discover_on(task_id, atoms) for task_id, atoms in discovery_specs]
    invented_ids = {row["lemma"].lemma_id for row in discovery_rows}
    if len(invented_ids) != 1:
        raise RuntimeError(f"discovery anti-unify failed: {invented_ids}")
    identity = discovery_rows[0]["identity"]
    lemma = K.lemma_from_identity(
        identity,
        support_ids=tuple(row["task_id"] for row in discovery_rows),
        authorized=True,
    )
    lemmas = {lemma.lemma_id: lemma}
    distractor = identity_distractor()
    retrieval_pool = {lemma.lemma_id: lemma, distractor.lemma_id: distractor}

    fresh_goal = goal_compose(FRESH_ATOMS)
    discovery_atoms = set(TRAIN_ATOMS_1.values()) | set(TRAIN_ATOMS_2.values())
    fresh_atoms = set(FRESH_ATOMS.values())

    one_step = K.one_step_screen(fresh_goal, lemmas)
    primitive = consume(fresh_goal, {})
    with_cut = consume(fresh_goal, lemmas)
    ablation = consume(fresh_goal, {})
    top1_ids = K.retrieve_nearest_lemmas(fresh_goal, retrieval_pool, 1)
    top2_ids = K.retrieve_nearest_lemmas(fresh_goal, retrieval_pool, 2)
    retrieval_top1 = consume(fresh_goal, {i: retrieval_pool[i] for i in top1_ids})
    retrieval_top2 = consume(fresh_goal, {i: retrieval_pool[i] for i in top2_ids})

    with tempfile.TemporaryDirectory(prefix="math-n4-subgoal-") as temp:
        root = Path(temp)
        library_path = root / "library.json"
        storage_bytes = persist_library(library_path, lemmas)
        loaded = load_library(library_path)
        restart = restart_consumer(library_path, fresh_goal)
        revoked = revoke_support(loaded, set(DISCOVERY_IDS))
        revoke_row = consume(fresh_goal, revoked)
        restored = consume(fresh_goal, loaded)

    wall = time.perf_counter() - started
    invented_payload = {
        "lemma_id": lemma.lemma_id,
        "schema": K.pretty(lemma.schema),
        "schema_alpha": K.pretty(K.alpha_normalize(lemma.schema)),
        "witness_term": K.term_pretty(lemma.witness_term),
        "support_ids": list(lemma.support_ids),
        "frozen_training_lemma_names": list(FROZEN_NAMES),
        "is_frozen_name": lemma.lemma_id in K.FROZEN_TRAINING_LEMMA_NAMES,
        "unifies_prefix_schema": K.unify_schema(K.PREFIX_SCHEMA, lemma.schema) is not None,
        "name_is_not_prefix_or_swap": lemma.lemma_id not in K.FROZEN_TRAINING_LEMMA_NAMES,
    }

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "issue": 165,
        "lane": "MATH-1",
        "salt": SALT,
        "scope": "bounded MATH-1 microscope; not N4 completion of Metamath",
        "domain": "positive implicational Hilbert calculus / typed SK combinatory logic",
        "predecessor": {
            "path": "research/math-n4-lemma-reuse-v1/",
            "terminal": V1_TERMINAL,
            "mechanism_delta": (
                "Invent/use a CUT_* intermediate that is not the goal and not a "
                "frozen PREFIX/SWAP name, admit it as a named lemma, reuse on a "
                "fresh compose-second theorem. Not a salt retune of PREFIX+SWAP."
            ),
        },
        "metamath_library": library_note,
        "v1_result_custody": custody,
        "src_custody": {
            "experiment_does_not_import_ocm": not experiment_imports_ocm(),
            "production_src_edits": "forbidden",
        },
        "do_not_expand_flt": True,
        "unscoped_causal_reuse_not_claimed": True,
        "partition": {
            "discovery_ids": list(DISCOVERY_IDS),
            "fresh_id": FRESH_ID,
            "fresh_goal": K.pretty(fresh_goal),
            "fresh_goal_alpha": K.pretty(K.alpha_normalize(fresh_goal)),
            "fresh_atoms": sorted(fresh_atoms),
            "discovery_atoms": sorted(discovery_atoms),
            "fresh_atoms_disjoint_from_discovery": fresh_atoms.isdisjoint(discovery_atoms),
            "salt": SALT,
        },
        "invented_lemma": invented_payload,
        "acquisition": {
            "operators_before": ["K", "S", "MP"],
            "operators_after": ["K", "S", "MP", lemma.lemma_id],
            "representation_introduced": [lemma.lemma_id],
            "frozen_training_lemma_names_refused": list(FROZEN_NAMES),
        },
        "discovery_tasks": [
            {k: v for k, v in row.items() if k not in {"lemma", "identity"}}
            for row in discovery_rows
        ],
        "fresh": {
            "one_step_hits": list(one_step),
            "one_step_invocations": len(one_step),
            "primitive": result_summary(primitive),
            "with_cut": result_summary(with_cut),
            "ablation": result_summary(ablation),
        },
        "retrieval_parent": {
            "method": "bag-of-symbols Jaccard after alpha-normalization",
            "pool_ids": sorted(retrieval_pool),
            "top1_ids": list(top1_ids),
            "top2_ids": list(top2_ids),
            "top1": result_summary(retrieval_top1),
            "top2": result_summary(retrieval_top2),
            "neural": NEURAL_CANNOT_CHECK,
        },
        "restart": restart,
        "revocation": {
            "revoke_discovery_support": result_summary(revoke_row),
            "restore": result_summary(restored),
        },
        "neural_guided_prover": neural_status(),
        "transformer_proof_reference": neural_status(),
        "costs": {
            "search": {
                "fresh_with_cut_nodes": with_cut.costs.nodes,
                "fresh_primitive_nodes": primitive.costs.nodes,
                "fresh_with_cut_mp_attempts": with_cut.costs.mp_attempts,
                "fresh_primitive_mp_attempts": primitive.costs.mp_attempts,
                "library_size": LIBRARY_SIZE,
                "primitive_size": PRIMITIVE_SIZE,
            },
            "check": {
                "fresh_with_cut_kernel_checks": with_cut.costs.kernel_checks,
                "fresh_with_cut_kernel_rejects": with_cut.costs.kernel_rejects,
                "discovery_kernel_checks": sum(
                    row["finish_costs"]["kernel_checks"] for row in discovery_rows
                ),
            },
            "storage": {
                "library_bytes": storage_bytes,
                "lemma_count": len(lemmas),
            },
            "acquisition": {
                "discovery_wall_s": [row["wall_s"] for row in discovery_rows],
                "identities_enumerated": [
                    row["discovery"]["identities_enumerated"] for row in discovery_rows
                ],
            },
        },
        "process": {
            "pid": os.getpid(),
            "max_rss_kib": rss_kib(),
            "study_wall_s": wall,
        },
        "claim_boundary": (
            "Subgoal discovery and named-lemma introduction are supported only "
            "in this miniature Hilbert/SK microscope. It does not close MATH-1 / "
            "N4 for Metamath, does not expand FLT, and does not emit unscoped "
            "CAUSAL_PROOF_METHOD_REUSE_SUPPORTED."
        ),
    }
    terminal, criteria = decide_terminal(payload)
    payload["criteria"] = criteria
    payload["terminal"] = terminal
    payload["n4_metamath_status"] = "OPEN"
    payload["math1_boxes_at_miniature_scope"] = math1_boxes(payload)
    payload["cannot_check"] = cannot_check_rows()
    return payload


def write_core(payload: dict[str, Any], path: Path) -> None:
    path.write_text(render_core(payload), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    parser.add_argument("--core", type=Path, default=HERE / "CORE.md")
    parser.add_argument("--restart-consumer", action="store_true")
    parser.add_argument("--library", type=Path)
    parser.add_argument("--goal", type=Path)
    args = parser.parse_args()
    if args.restart_consumer:
        if args.library is None or args.goal is None:
            raise SystemExit("--library and --goal are required for --restart-consumer")
        result = run_restart_consumer(args.library, args.goal)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "pid": result["pid"],
            "status": result["status"],
            "lemmas_used": result["lemmas_used"],
        }))
        return
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.core is not None:
        write_core(result, args.core)
    print(json.dumps({
        "terminal": result["terminal"],
        "invented_lemma_id": result["invented_lemma"]["lemma_id"],
        "one_step_invocations": result["fresh"]["one_step_invocations"],
        "lemmas_used": result["fresh"]["with_cut"]["lemmas_used"],
        "primitive": result["fresh"]["primitive"]["status"],
        "ablation": result["fresh"]["ablation"]["status"],
        "restart_pid": result["restart"]["pid"],
        "neural": result["neural_guided_prover"],
        "v1_unchanged": result["v1_result_custody"]["unchanged"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
