from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from anthropic_dag import extract_statement_source


def test_target_statement_is_nearest_declaration_before_unique_bridge():
    # Frozen Anthropic wrappers can carry a helper lemma before the generated target theorem.
    wrapper = '''
import Mathlib
import P2M.Util
import P2M.Sol.S_target

namespace Demo
lemma helper (P : Prop) : P → P := by
  intro h
  exact h
end Demo

theorem target
    (P Q : Prop)
    (h : P → Q) : P → Q := by p2m_exact_reverting @_root_.P2MW.S_target.solution
'''
    statement = extract_statement_source(wrapper)
    assert statement.startswith("theorem target")
    assert "lemma helper" not in statement
    assert "p2m_exact_reverting" not in statement
    assert "P2M.Sol" not in statement
