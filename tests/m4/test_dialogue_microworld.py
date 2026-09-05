"""M4 §11–§12: the frozen dialogue microworld and the evaluation on its dev split (the protected
split is consulted only by the receipt script)."""
from __future__ import annotations

from pathlib import Path

from ocm.dialogue import microworld as DW
from ocm.evaluation import m4_dialogue_eval as E


def test_dialogue_corpus_is_deterministic_and_frozen():
    a, b = DW.generate(), DW.generate()
    assert [d.dialogue_id for d in a] == [d.dialogue_id for d in b]
    rec = DW.custody_receipt(a, "OCM-M4-DIALOGUE-20260905")
    assert rec["n"] == 120 and rec["dev"] + rec["protected"] == 120 and len(rec["families"]) == 8
    assert 0.25 < rec["protected"] / rec["n"] < 0.6


def test_every_family_runs_clean_on_dev_with_a_midway_restart(tmp_path):
    ds = DW.generate()
    seen = set()
    for d in ds:
        if d.split != "dev" or d.family in seen:
            continue
        seen.add(d.family)
        c = E.run_dialogue(d, tmp_path / d.dialogue_id, restart_at=len(d.steps) // 2 if len(d.steps) > 2 else None)
        assert c["act_ok"] == c["steps"], (d.family, c)
        assert c["leak"] == 0 and c["unnecessary_clarify"] == 0
    assert len(seen) == 8
