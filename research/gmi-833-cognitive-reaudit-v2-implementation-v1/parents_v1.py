"""Parent custody for the Section-M re-audit implementation.

CUSTODY requirement: this re-audit imports the upgraded #833 foundation and
axiom-core objects, and re-parents the three legacy packages to them.  Every
frozen parent blob is re-checked at run time (foundation result, axiom-core
result, the three legacy cores/executables, and the two legacy receipts),
and the legacy packages are replayed byte-exactly in isolation.

Blob identity uses the git blob sha (sha1("blob <len>\\0<bytes>")), which is
the same identity the freeze pins in FREEZE_V1.md, so a checkout of the same
bytes gives the same pin with no git history required.
"""

from __future__ import annotations

from hashlib import sha1
from fractions import Fraction as F
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # research/gmi-833-cognitive-reaudit-v2-implementation-v1
REPO = HERE.parent.parent                        # repo root
RESEARCH = REPO / "research"

FOUNDATION_PIN = "c0c574c4ec6e237d5fdafa694eac131399625a70"
AXIOM_CORE_PIN = "3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9"
HIERARCHY_CORE_PIN = "057ba5b705751d6fc2c6fc5f7571d78664a389a6"
HIERARCHY_EXE_PIN = "34266004877277de3e7c1faa377a462b383a4f56"
PLANNING_CORE_PIN = "42d5531cf2be37e2c08417c6c60a2b7621486308"
PLANNING_EXE_PIN = "7219b55a64d1baf5d9fe03a9b40f5c0bceec00b7"
CAUSAL_CORE_PIN = "8fca71ecdca2dec265460b8f27560f1957d779a5"
CAUSAL_EXE_PIN = "f0f80cd3c5377046d58b32019b69a9f92606d64b"

FOUNDATION_CLAIM = "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE"
AXIOM_CORE_CLAIM = "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE"

# (name, repo-root-relative path, expected blob, expected claim, claim field)
FREEZE_PINS = (
    ("foundation", "research/gmi-833-foundation-v1/RESULT_V1.json", FOUNDATION_PIN, FOUNDATION_CLAIM, "terminal"),
    ("axiom_core", "research/gmi-833-axiom-core-v1/RESULT_V1.json", AXIOM_CORE_PIN, AXIOM_CORE_CLAIM, "claim_ceiling"),
    ("hierarchy_core", "research/gmi-hierarchical-chunking-repair-v1/CORE.md", HIERARCHY_CORE_PIN, None, None),
    ("hierarchy_executable", "research/gmi-hierarchical-chunking-repair-v1/source_evidence_v1.py", HIERARCHY_EXE_PIN, None, None),
    ("planning_core", "research/gmi-planning-stopping-v1/CORE.md", PLANNING_CORE_PIN, None, None),
    ("planning_executable", "research/gmi-planning-stopping-v1/planning_stopping_v1.py", PLANNING_EXE_PIN, None, None),
    ("causal_core", "research/gmi-causal-rung-repair-v1/CORE.md", CAUSAL_CORE_PIN, None, None),
    ("causal_executable", "research/gmi-causal-rung-repair-v1/census_v1.py", CAUSAL_EXE_PIN, None, None),
)

# (name, repo-root-relative package dir, sha256 of the committed legacy receipt)
LEGACY_RECEIPTS = (
    ("hierarchy", "research/gmi-hierarchical-chunking-repair-v1",
     "c0e9ce918acc6b0eabbb06b137180b69c632dedad90f27c032c7ee3384b4eeb8"),
    ("causal", "research/gmi-causal-rung-repair-v1",
     "f5a489fe203babc5328a9758d541dec386e01fd501e0e461eadbc5a396ae91e4"),
)


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parent_pins() -> dict:
    """Re-check every frozen parent blob against the freeze pins."""
    rows = []
    for name, rel, expected_blob, expected_claim, field in FREEZE_PINS:
        path = REPO / rel
        if not path.is_file():
            rows.append({"name": name, "path": rel, "present": False,
                         "blob_ok": False, "claim_ok": False})
            continue
        data = path.read_bytes()
        blob = git_blob_sha(data)
        claim = None
        if expected_claim is not None:
            try:
                claim = json.loads(data).get(field)
            except Exception:
                claim = None
        rows.append({
            "name": name, "path": rel, "present": True,
            "actual_blob": blob, "blob_ok": blob == expected_blob,
            "claim_ok": expected_claim is None or claim == expected_claim,
        })
    return {
        "rows": rows,
        "all_pinned": all(r["present"] and r["blob_ok"] and r["claim_ok"] for r in rows),
    }


def legacy_replays() -> dict:
    """Byte-exact isolated replay of the two replayable legacy packages."""
    out = {}
    for name, rel, expected_sha256 in LEGACY_RECEIPTS:
        pkg = REPO / rel
        receipt_path = pkg / "RECEIPT_V1.json"
        committed = receipt_path.read_bytes()
        from hashlib import sha256 as sha256_mod
        ok_commit = sha256_mod(committed).hexdigest() == expected_sha256
        flags = ["-I", "-B"] + (["-O"] if sys.flags.optimize else [])
        p = subprocess.run(
            [sys.executable, *flags, str(pkg / "replay_v1.py")],
            cwd=str(pkg), capture_output=True, timeout=600,
        )
        ok = p.returncode == 0 and not p.stderr and p.stdout == committed
        out[name] = {
            "package": rel,
            "receipt_sha256_ok": ok_commit,
            "isolated_replay_byte_exact": bool(ok),
            "returncode": p.returncode,
            "stderr_empty": not p.stderr,
            "bytes": len(committed),
        }
        if not (ok_commit and ok):
            raise ValueError("legacy package %s failed byte-exact replay" % name)
    return out


def _import_from(pkg_dir: Path, module: str):
    """Load a package source file under a unique synthetic module name.

    Several legacy packages ship a module named ``witnesses_v1`` /
    ``source_evidence_v1``; a plain ``import witnesses_v1`` would resolve to
    whichever package imported it first (sys.modules cache), silently binding
    the wrong module.  Loading by explicit file location under a name derived
    from the package directory makes every import unambiguous.  The package
    directory is still inserted on ``sys.path`` first so the module's own
    absolute imports resolve inside its package.
    """
    path = pkg_dir / (module + ".py")
    if not path.is_file():
        raise ValueError("missing module file: %s" % path)
    if str(pkg_dir) not in sys.path:
        sys.path.insert(0, str(pkg_dir))
    name = "gmi833_%s_%s" % (pkg_dir.name, module)
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot build import spec for %s" % path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return mod


def exercise_parents() -> dict:
    """Actually import and exercise the upgraded foundation and axiom-core.

    Both receipts are regenerated from the imported source and compared
    against the committed (pinned) RESULT_V1.json files; the pinned blob and
    claim checks run separately in ``audit_parent_pins``.
    """
    foundation = _import_from(RESEARCH / "gmi-833-foundation-v1", "foundation_v1")
    axiom = _import_from(RESEARCH / "gmi-833-axiom-core-v1", "axiom_core_v1")

    foundation_result = json.loads((RESEARCH / "gmi-833-foundation-v1/RESULT_V1.json").read_bytes())
    axiom_result = json.loads((RESEARCH / "gmi-833-axiom-core-v1/RESULT_V1.json").read_bytes())

    # Regenerate each parent's own receipt from its imported source and
    # require byte-identical output to the committed (pinned) RESULT.
    # ``foundation_v1.main`` prints json.dumps(build_receipt(), indent=2,
    # sort_keys=True); ``axiom_core_v1`` prints canonical_json(...).  These
    # string forms are exactly what produced the committed files.
    rebuilt_foundation = foundation.build_receipt()
    rebuilt_axiom = axiom.build_receipt(axiom.audit_parents())
    foundation_ok = (json.dumps(rebuilt_foundation, indent=2, sort_keys=True) + "\n") \
        == (RESEARCH / "gmi-833-foundation-v1/RESULT_V1.json").read_text(encoding="utf-8")
    axiom_ok = axiom.canonical_json(rebuilt_axiom) \
        == (RESEARCH / "gmi-833-axiom-core-v1/RESULT_V1.json").read_text(encoding="utf-8")

    # Direct object exercises (beyond regeneration).
    forbidden = tuple(foundation.canonical_forbidden_promotions())
    if "COMPLETE_GMI" not in forbidden or not forbidden:
        raise ValueError("foundation forbidden-promotion registry not exercised")
    model = axiom.base_model()
    valid = axiom.validate_model(model)
    if not valid["satisfies"]:
        raise ValueError("axiom-core base model does not satisfy AX-1..AX-6")
    if not axiom.graph_is_acyclic(axiom.dependency_graph()):
        raise ValueError("axiom-core dependency graph is not acyclic")
    hyper = axiom.hostile_hypercube()
    if hyper["cases"] != 128 or hyper["satisfying_cases"] != 1 or hyper["failures"]:
        raise ValueError("axiom-core hostile hypercube did not reproduce")

    # A concrete foundation object: scalarization never reorders Pareto dominance.
    a, b = (F(1), F(2)), (F(1), F(1))
    if not foundation.pareto_strictly_dominates(b, a):
        raise ValueError("foundation pareto helper not exercised")

    return {
        "foundation": {
            "regenerated_matches_committed": foundation_ok,
            "canonical_forbidden_tokens": len(forbidden),
            "contains_COMPLETE_GMI": "COMPLETE_GMI" in forbidden,
        },
        "axiom_core": {
            "regenerated_matches_committed": axiom_ok,
            "base_model_satisfies_all_axioms": valid["satisfies"],
            "dependency_graph_acyclic": True,
            "hostile_hypercube_cases": hyper["cases"],
            "hostile_hypercube_satisfying_cases": hyper["satisfying_cases"],
        },
    }


def exercise_hierarchy() -> dict:
    """Import and exercise the frozen hierarchy repair content in-process."""
    pkg = RESEARCH / "gmi-hierarchical-chunking-repair-v1"
    hierarchy_v1 = _import_from(pkg, "hierarchy_v1")
    parsing_v1 = _import_from(pkg, "parsing_v1")
    witnesses_v1 = _import_from(pkg, "witnesses_v1")
    source_evidence_v1 = _import_from(pkg, "source_evidence_v1")

    witness = witnesses_v1.hierarchy_witness()
    runs = witness["runs"]
    if [runs[n]["cost"] for n in ("fresh", "lower_only", "both")] != [3060, 3032, 1233]:
        raise ValueError("hierarchy lifecycle 3060/3032/1233 not reproduced")
    controls = witnesses_v1.parsing_controls()
    if controls["greedy_countermodel"]["cost"] != 2:
        raise ValueError("greedy parsing countermodel not reproduced")
    source_ctrl = source_evidence_v1.source_controls()
    if source_ctrl["source_greedy"] != 3:
        raise ValueError("source greedy control not reproduced")
    policy = witnesses_v1.policy_census()
    parsing = witnesses_v1.parsing_census()

    # H_FREEZE_2: a workload where hierarchy loses after complete charges.
    reg = hierarchy_v1.Register(("a",), (1,), (("a",),), (0,), (9,), (0,))
    got = hierarchy_v1.solve(reg, (0, 0), (0,))
    if got["cost"] != 2:
        raise ValueError("H_FREEZE_2 hierarchy-loses workload not reproduced")

    return {
        "lifecycle": [runs[n]["cost"] for n in ("fresh", "lower_only", "both")],
        "first_gain": witness["first_gain"],
        "second_gain": witness["second_gain"],
        "greedy_exact_cost": controls["greedy_countermodel"]["cost"],
        "source_greedy_cost": source_ctrl["source_greedy"],
        "h_freezer_2_hierarchy_loses": {"retained_invocation_price": 9,
                                        "re_derivation_cost": 2,
                                        "solver_cost": got["cost"]},
        "policy_census_cases": policy["complete_register_class_cases"],
        "policy_census_executions": policy["complete_executions"],
        "parsing_census_cases": parsing["word_dictionary_cases"],
        "parsing_census_parses": parsing["complete_parses"],
    }


def exercise_causal() -> dict:
    """Import and exercise the frozen causal-rung repair content in-process."""
    pkg = RESEARCH / "gmi-causal-rung-repair-v1"
    scm_v1 = _import_from(pkg, "scm_v1")
    bounds_v1 = _import_from(pkg, "bounds_v1")
    fiber_v1 = _import_from(pkg, "fiber_v1")
    witnesses_v1 = _import_from(pkg, "witnesses_v1")
    census_v1 = _import_from(pkg, "census_v1")

    pairs = witnesses_v1.pair_results()
    orientation = witnesses_v1.orientation_result()
    census = census_v1.census()

    # C_FREEZE_1: observation-equivalent models, different counterfactual targets.
    six = pairs["six_original"]
    if not six["all_nine_joint_laws_equal"]:
        raise ValueError("C_FREEZE_1 joint laws not equal")
    if not (six["left_pn"] != six["right_pn"]):
        raise ValueError("C_FREEZE_1 counterfactual targets not different")
    if not (pairs["two_smaller"]["left_pn"] != pairs["two_smaller"]["right_pn"]):
        raise ValueError("C_FREEZE_1 two-smaller targets not different")
    if not pairs["three_treatment_supported"]["all_nine_joint_laws_equal"]:
        raise ValueError("C_FREEZE_1 three-treatment joint laws not equal")

    # C_FREEZE_2: incompatible evidence is refused, never an identified value.
    pn_bounds_refusal = False
    try:
        bounds_v1.pn_bounds((bounds_v1.F(1, 4),) * 4, bounds_v1.F(0), bounds_v1.F(1, 2))
    except ValueError:
        pn_bounds_refusal = True
    a = scm_v1.from_units(((1, 0, 1),))
    b = scm_v1.from_units(((1, 1, 1),))
    if fiber_v1.solve_fiber((a,), scm_v1.complete_laws(b))["status"] != "INCOMPATIBLE":
        raise ValueError("C_FREEZE_2 incompatible fiber not refused")

    # C_FREEZE_3: identified constant-on-fiber control (no alarm).
    w = scm_v1.from_units(((1, 0, 1),))
    r = fiber_v1.solve_fiber(fiber_v1.uniform_root_models(1), scm_v1.complete_laws(w))
    if (r["status"], r["lower"], r["upper"]) != ("IDENTIFIED", 1, 1):
        raise ValueError("C_FREEZE_3 identified control did not reproduce")
    r3 = bounds_v1.identified_or_bounds(*scm_v1.evidence(scm_v1.from_units(((0, 0, 0), (1, 0, 1)))))
    if (r3["status"], r3["lower"], r3["upper"]) != ("IDENTIFIED", 1, 1):
        raise ValueError("C_FREEZE_3 point-identification control did not reproduce")

    # C_FREEZE_4: faithfulness does not orient.
    if not orientation["same_full_support_observed"] or not orientation["dependent"]:
        raise ValueError("C_FREEZE_4 faithfulness counterexample not reproduced")
    if (orientation["forward_do1"], orientation["reverse_do1"]) != (F(3, 4), F(1, 2)):
        raise ValueError("C_FREEZE_4 orientation numbers wrong")

    # C_FREEZE_5: undefined conditioning is a distinct refusal from an empty fiber.
    undefined_refusal = False
    try:
        bounds_v1.pn_bounds((1, 0, 0, 0), 0, 0)
    except ValueError:
        undefined_refusal = True

    return {
        "c_freezer_1": {"six_original_all_nine_joint_laws_equal": six["all_nine_joint_laws_equal"],
                        "six_original_left_pn": str(six["left_pn"]), "six_original_right_pn": str(six["right_pn"]),
                        "two_smaller_left_pn": str(pairs["two_smaller"]["left_pn"]),
                        "two_smaller_right_pn": str(pairs["two_smaller"]["right_pn"]),
                        "three_treatment_supported": pairs["three_treatment_supported"]["all_nine_joint_laws_equal"]},
        "c_freezer_2": {"empty_compatible_class_refused": pn_bounds_refusal,
                        "disjoint_class_status": "INCOMPATIBLE"},
        "c_freezer_3": {"uniform_n1_status": r["status"], "lower": str(r["lower"]), "upper": str(r["upper"]),
                        "point_identification_status": r3["status"]},
        "c_freezer_4": {"same_full_support_observed": orientation["same_full_support_observed"],
                        "dependent": orientation["dependent"],
                        "forward_do1": str(orientation["forward_do1"]),
                        "reverse_do1": str(orientation["reverse_do1"])},
        "c_freezer_5": {"undefined_conditioning_refused": undefined_refusal},
        "census": census,
        "census_models_total": sum(rec["models"] for rec in census),
        "census_joint_law_comparisons_total": sum(rec["joint_law_comparisons"] for rec in census),
        "census_attainment_checks_total": sum(rec["constructive_attainment_checks"] for rec in census),
    }
