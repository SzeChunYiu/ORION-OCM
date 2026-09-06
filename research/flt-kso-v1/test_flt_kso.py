from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import pytest

from anthropic_dag import ExtractionError, active_imports, extract_node, extract_statement_source, theorem_imports
from flt_contract import EnvironmentIdentity, Terminal, statement_identity
from native_prop import Arrow, TyVar, emit_r1_lean, render_term, solve_r1
from sealer import LeakageError, audit_public_tree, build_packages, private_open_guard_capability, scan_generated_lean, sanitized_environment

def test_r1_native_search_constructs_proof_without_hidden_generator():
    result = solve_r1(max_expansions=64)
    assert result.terminal == "CANDIDATE_CONSTRUCTED"
    assert result.term is not None
    assert render_term(result.term) == "fun h0 h1 h2 => h1 (h0 h2)"
    assert result.expansions <= 64
    assert {e.operator_id for e in result.events} <= {
        "proof.intro", "proof.assumption", "proof.apply_local", "proof.deduplicate"
    }
    source = emit_r1_lean(result.term)
    scan_generated_lean(source)
    assert "sorry" not in source and "axiom bad" not in source and "native_decide" not in source


def test_r1_budget_failure_is_not_refutation():
    result = solve_r1(max_expansions=1)
    assert result.term is None
    assert result.terminal == "FAILED_UNDER_BUDGET"


def test_shortcut_and_hidden_import_hostiles():
    for text in (
        "axiom bad : False\n",
        "theorem bad : True := by sorry\n",
        "theorem bad : True := by native_decide\n",
        "import P2M.Sol.S_secret\ntheorem x : True := by trivial\n",
        "import Theorems.Thm_secret\ntheorem x : True := by trivial\n",
    ):
        with pytest.raises(LeakageError):
            scan_generated_lean(text)
    scan_generated_lean("import Mathlib\ntheorem x : True := by trivial\n")
    scan_generated_lean(
        "import Theorems.Thm_boundary\ntheorem x : True := by trivial\n",
        allowed_theorem_modules=("Theorems.Thm_boundary",),
    )


def test_import_scanner_ignores_comments_and_strings():
    text = '''
/- import P2M.Sol.S_fake
   /- import Theorems.Thm_nested -/
-/
-- import Theorems.Thm_line_fake
import Mathlib.NumberTheory.FLT.Basic
import Theorems.Thm_real
#check "import Theorems.Thm_string_fake"
'''
    assert active_imports(text) == ("Mathlib.NumberTheory.FLT.Basic", "Theorems.Thm_real")
    assert theorem_imports(text) == ("Theorems.Thm_real",)


def _fake_anthropic_tree(root: Path) -> None:
    (root / "Theorems").mkdir(parents=True)
    (root / "P2M" / "Sol").mkdir(parents=True)
    (root / "Theorems" / "Thm_target.lean").write_text(
        '''import Mathlib\nimport P2M.Util\nimport P2M.Sol.S_target\n\nattribute [-instance] Foo.bar\n\ntheorem target\n    (P Q : Prop)\n    (h : P → Q) : P → Q := by p2m_exact_reverting target\n''',
        encoding="utf-8",
    )
    (root / "P2M" / "Sol" / "S_target.lean").write_text(
        '''import Mathlib\nimport Theorems.Thm_dep_b\n-- import Theorems.Thm_fake\nimport Theorems.Thm_dep_a\n\nnamespace P2M\n-- hidden proof body\nend P2M\n''',
        encoding="utf-8",
    )


def test_wrapper_pair_and_statement_extraction_are_lexical_not_one_line_regex(tmp_path: Path):
    _fake_anthropic_tree(tmp_path)
    node = extract_node(tmp_path, "target")
    assert node.theorem_id == "Theorems.Thm_target"
    assert node.dependencies == ("Theorems.Thm_dep_a", "Theorems.Thm_dep_b")
    assert "theorem target" in node.statement_source
    assert "P2M.Sol" not in node.statement_source
    assert "p2m_exact_reverting" not in node.statement_source
    assert "(P Q : Prop)" in node.statement_source


def test_statement_extractor_fails_closed_without_generated_bridge_marker():
    with pytest.raises(ExtractionError):
        extract_statement_source("theorem x : True := by trivial\n")
    with pytest.raises(ExtractionError):
        extract_statement_source("theorem x : True := by p2m_exact_reverting x\ntheorem y : True := by p2m_exact_reverting y\n")


def test_statement_identity_is_environment_bound():
    env = EnvironmentIdentity()
    same = statement_identity("P → P", env)
    changed = EnvironmentIdentity(mathlib_commit="0" * 40)
    assert same == statement_identity("P → P", env)
    assert same != statement_identity("P → P", changed)


def test_sealer_hides_solution_and_r3_topology(tmp_path: Path):
    source = tmp_path / "source"
    _fake_anthropic_tree(source)
    node = extract_node(source, "target")
    public, private = build_packages(
        node=node,
        output_root=tmp_path / "sealed",
        regime="R3",
        boundary_statements={"Theorems.Thm_dep_a": "theorem dep_a : True"},
    )
    p = json.loads((public / "challenge.json").read_text())
    q = json.loads((private / "evaluator.json").read_text())
    assert p["hidden_solution_text"] is False
    assert p["hidden_dependency_topology"] is True
    assert "original_dependencies" not in p
    assert q["original_dependencies"] == ["Theorems.Thm_dep_a", "Theorems.Thm_dep_b"]
    public_text = "\n".join(x.read_text() for x in public.rglob("*") if x.is_file())
    assert "P2M/Sol" not in public_text and "P2M.Sol" not in public_text
    assert "original_dependencies" not in public_text
    audit_public_tree(public, private_root=private)


def test_sealer_rejects_symlink_and_private_path(tmp_path: Path):
    public = tmp_path / "public"; private = tmp_path / "private"
    public.mkdir(); private.mkdir()
    (public / "bad.txt").write_text(str(private.resolve()), encoding="utf-8")
    with pytest.raises(LeakageError):
        audit_public_tree(public, private_root=private)
    (public / "bad.txt").unlink()
    try:
        (public / "link").symlink_to(private)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(LeakageError):
        audit_public_tree(public, private_root=private)


def test_sanitized_environment_drops_model_and_path_overrides(monkeypatch):
    monkeypatch.setenv("LEAN_PATH", "/secret/lean")
    monkeypatch.setenv("PYTHONPATH", "/secret/python")
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    env = sanitized_environment()
    assert "LEAN_PATH" not in env and "PYTHONPATH" not in env and "OPENAI_API_KEY" not in env
    with pytest.raises(LeakageError):
        sanitized_environment({"LEAN_PATH": "/bad"})


def test_open_goal_planner_edge_failure_and_checker_lifecycle():
    from theorem_kso import (
        admit_checked_proof, compose_proof_candidate, empty_space, failed_attempt,
        open_obligation, proof_operator, proposed_reduction,
    )
    from ocm.kso.space import Atom
    from ocm.kso.warrant import Liveness, WarrantProfile
    env = EnvironmentIdentity()
    goal = open_obligation(theorem_name="demo", statement="P → P", environment=env)
    assert goal.liveness(()) is Liveness.UNKNOWN
    ks = empty_space().with_atoms(goal)

    failed = failed_attempt(attempt_id="a1", goal_atom_id=goal.atom_id, terminal="FAILED_UNDER_BUDGET", budget={"states": 1})
    ks_failed = ks.with_atoms(failed)
    assert ks_failed.atom_map()[goal.atom_id].liveness(()) is Liveness.UNKNOWN

    dep = Atom("dep:verified", "claim", WarrantProfile.of(("dep-evidence",), complete=True))
    ks_dep = ks_failed.with_atoms(dep)
    edge = proposed_reduction(edge_id="plan:1", dependencies=(dep.atom_id,), goal_atom_id=goal.atom_id, method_ref="planner:test")
    ks_plan = ks_dep.with_edges(edge)
    assert ks_plan.edge_map()[edge.edge_id].liveness(()) is Liveness.UNKNOWN
    assert edge.relation_type == "COMPOSITION"

    op = proof_operator(goal_atom_id=goal.atom_id, backend=lambda _ks, _ctx: {})
    pending = compose_proof_candidate(ks_plan, op, {"goal_atom_id": goal.atom_id, "source": "fun h => h"}, checker_evidence=None)
    assert pending.liveness(()) is Liveness.UNKNOWN

    exact = compose_proof_candidate(ks_plan, op, {"goal_atom_id": goal.atom_id, "source": "fun h => h"}, checker_evidence="lean-run:1")
    assert exact.liveness(()) is Liveness.LIVE
    admitted = admit_checked_proof(
        ks_plan, goal=goal, candidate=exact, proof_source_hash="1" * 64, checker_evidence="lean-run:1"
    )
    claim_id = goal.atom_id.replace("theorem-goal:", "theorem-claim:", 1)
    assert admitted.atom_map()[claim_id].liveness(()) is Liveness.LIVE
    assert admitted.atom_map()[claim_id].liveness({"lean-run:1"}) is Liveness.DEAD

    exact2 = compose_proof_candidate(ks_plan, op, {"goal_atom_id": goal.atom_id, "source": "fun h => h"}, checker_evidence="lean-run:2")
    admitted2 = admit_checked_proof(
        admitted, goal=goal, candidate=exact2, proof_source_hash="2" * 64, checker_evidence="lean-run:2"
    )
    assert admitted2.atom_map()[claim_id].liveness({"lean-run:1"}) is Liveness.LIVE
    assert admitted2.atom_map()[claim_id].liveness({"lean-run:1", "lean-run:2"}) is Liveness.DEAD


def test_private_open_guard_is_explicit_when_unavailable():
    assert private_open_guard_capability() in {"STRACE", Terminal.CANNOT_CHECK_PRIVATE_OPEN_GUARD.value}


def test_strace_guard_detects_private_open_when_available(tmp_path: Path):
    import sys
    from sealer import run_public_process

    if private_open_guard_capability() != "STRACE":
        pytest.skip("strace unavailable on this host")
    public = tmp_path / "public"; private = tmp_path / "private"
    public.mkdir(); private.mkdir()
    (private / "secret.txt").write_text("hidden", encoding="utf-8")
    (public / "ok.py").write_text("print('ok')\n", encoding="utf-8")
    clear = run_public_process([sys.executable, "ok.py"], public_root=public, private_root=private, timeout_s=5)
    assert clear["terminal"] == "PROCESS_GUARD_CLEAR"

    (public / "bad.py").write_text("open('../private/secret.txt').read()\n", encoding="utf-8")
    with pytest.raises(LeakageError, match="opened private tree"):
        run_public_process([sys.executable, "bad.py"], public_root=public, private_root=private, timeout_s=5)
