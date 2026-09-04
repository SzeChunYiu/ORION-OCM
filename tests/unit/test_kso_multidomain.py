from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_multidomain_v1.py"


def load():
    name = "kso_multidomain_v1"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_one_knowledge_space_holds_procedure_and_formal_math_domains():
    m = load()
    r = m.run_multidomain()
    assert r["terminal"] == "CONTROLLED_MULTIDOMAIN_KSO_GREEN"
    s = r["space"]
    assert s["learned_procedures"] == 1
    assert s["verified_math_proofs"] == 20
    assert s["registered_bad_proofs_excluded"] == 20
    assert s["root_reaches_procedure_region"] is True
    assert s["root_reaches_math_region"] is True
    assert s["root_activates_both"] is True


def test_cross_domain_revocation_does_not_launder_or_overretract():
    m = load()
    r = m.run_multidomain()
    n = r["noninterference"]
    assert n["procedure_revocation_leaves_math_proof_live"] is True
    assert n["proof_revocation_leaves_procedure_executable"] is True
    assert n["global_evidence_ids_unique"] is True


def test_feedback_does_not_create_cross_domain_procedure_warrant():
    m = load()
    r = m.run_multidomain()
    assert r["feedback"] == {
        "status": "FEEDBACK_RECORDED_UNWARRANTED",
        "created_procedure_atom": False,
    }


def test_global_evidence_namespace_is_domain_sensitive_and_deterministic():
    m = load()
    a = m.global_evidence_id("procedure-lesson", "same")
    b = m.global_evidence_id("lean-proof", "same")
    assert a != b
    assert a == m.global_evidence_id("procedure-lesson", "same")


def test_multidomain_boundary_is_not_scalability_claim():
    m = load()
    r = m.run_multidomain()
    assert r["boundary"] == {
        "domains": ["learned_boolean_procedures", "Lean_verified_formal_math"],
        "scalability_established": False,
        "automatic_domain_router": False,
        "open_domain_language": False,
        "novelty": False,
    }


def test_multidomain_main():
    m = load()
    assert m.main([]) == 0
