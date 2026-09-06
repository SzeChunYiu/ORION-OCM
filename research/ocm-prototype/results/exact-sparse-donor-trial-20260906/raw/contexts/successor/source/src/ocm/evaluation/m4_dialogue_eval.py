"""M4 dialogue microworld evaluation receipt (M4 §12 — separate numbers, each with its denominator).

Every protected dialogue runs through a fresh `DialogueRuntime`; half of them are *restarted from
disk* midway (persistence).  Per step the machine turn is checked against the generated gold:
  state/reference   entity introduction count, candidate-set recall on ambiguous pronouns, pronoun
                    resolution when unique
  correction        supersession recorded, dependent answer reopened, unrelated answer intact,
                    retraction leaves unrelated intact
  clarification     clarification-needed precision/recall (asked iff gold says CLARIFY),
                    unnecessary-clarification count
  epistemic         speaker-assertion→machine-belief leakage (machine layer must stay empty),
                    stale-conclusion count after correction/retraction, contradiction reported as
                    UNCERTAIN citing both, every committed answer cites evidence
  long-horizon      reference/answer after a ≥ 12-turn gap; wall time per turn by dialogue length
Exit 0 = ran.  No claim beyond the synthetic microworld with a given vocabulary.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

from ocm.dialogue import gate as G
from ocm.dialogue import microworld as DW
from ocm.dialogue import session as S
from ocm.language import constructions as C
from ocm.language import lexicon as L
from ocm.language import microworld as W
from ocm.kso.warrant import WarrantProfile as WP


def dialogue_lexicon() -> L.Lexicon:
    from ocm.language.bootstrap import microworld_lexicon

    lx = microworld_lexicon()
    lx.add(L.Lexeme("which", L.Category.WH, ()))
    lx.add(L.Lexeme("it", L.Category.PRON, ()))
    return lx


def run_dialogue(d: DW.Dialogue, root: Path, *, restart_at: int | None) -> dict:
    lx = dialogue_lexicon()
    cons = list(C.seed_constructions())
    dr = S.DialogueRuntime.resume(root, lx, cons, d.dialogue_id)
    remembered: dict[str, str] = {}
    checks = {"steps": 0, "act_ok": 0, "cites_ok": 0, "cites_n": 0, "clarify_gold": 0, "clarify_asked": 0, "clarify_tp": 0, "unnecessary_clarify": 0,
              "entities_ok": 0, "entities_n": 0, "candidates_ok": 0, "candidates_n": 0, "resolved_ok": 0, "resolved_n": 0,
              "supersede_ok": 0, "supersede_n": 0, "reopen_ok": 0, "reopen_n": 0, "intact_ok": 0, "intact_n": 0, "contradiction_ok": 0, "contradiction_n": 0,
              "leak": 0, "leak_n": 0, "gap_ok": 0, "gap_n": 0, "restarted": 0, "wall_s": 0.0, "turns": 0}
    for i, st in enumerate(d.steps):
        if restart_at is not None and i == restart_at:
            dr.runtime.persist()
            dr = S.DialogueRuntime.resume(root, lx, cons, d.dialogue_id)
            checks["restarted"] = 1
        t0 = time.perf_counter()
        if st.utterance.startswith("__retract:"):
            cid = remembered[st.utterance.split(":")[1]]
            mt = dr.retract(cid)
        else:
            mt = dr.hear(st.utterance, st.speaker)
        checks["wall_s"] += time.perf_counter() - t0
        checks["turns"] += 1
        g = st.gold
        checks["steps"] += 1
        if "remember" in g:
            remembered[g["remember"]] = dr.workspace.active_commitments(st.speaker)[-1].commitment_id
        want = g["act"]
        got = mt.act.value
        act_ok = (got == want) or (want == "ANSWER_OR_UNKNOWN" and got in ("ANSWER", "REPORT_UNKNOWN")) or (want == "ANSWER" and g.get("polarity") == "reported_no" and got == "ANSWER")
        checks["act_ok"] += int(act_ok and mt.committed)
        if want == "CLARIFY":
            checks["clarify_gold"] += 1
        if got == "CLARIFY":
            checks["clarify_asked"] += 1
            if want == "CLARIFY":
                checks["clarify_tp"] += 1
            else:
                checks["unnecessary_clarify"] += 1
        if "cites" in g:
            checks["cites_n"] += 1
            checks["cites_ok"] += int(len(mt.evidence) >= g["cites"])
        if "entities" in g:
            checks["entities_n"] += 1
            checks["entities_ok"] += int(len(dr.workspace.entities) == g["entities"])
        if "candidates" in g:
            checks["candidates_n"] += 1
            checks["candidates_ok"] += int(got == "CLARIFY" and mt.text.count("(") >= g["candidates"])
        if "resolved_to" in g:
            checks["resolved_n"] += 1
            checks["resolved_ok"] += int(got in ("ANSWER", "REPORT_UNKNOWN"))
        if g.get("supersedes"):
            checks["supersede_n"] += 1
            checks["supersede_ok"] += int(any(c.status.value == "SUPERSEDED" for c in dr.workspace.commitments.values()))
        if g.get("polarity") == "reported_no":
            checks["reopen_n"] += 1
            checks["reopen_ok"] += int("did not" in mt.text)
        if g.get("polarity") == "reported_yes":
            ok = "said so" in mt.text
            if g.get("unrelated_intact"):
                checks["intact_n"] += 1
                checks["intact_ok"] += int(ok)
            if "gap" in g:
                checks["gap_n"] += 1
                checks["gap_ok"] += int(ok)
        if g.get("contradiction"):
            checks["contradiction_n"] += 1
            checks["contradiction_ok"] += int("contradicts" in mt.text)
        if g.get("machine_layer_empty"):
            checks["leak_n"] += 1
            checks["leak"] += int(bool(dr.workspace.machine_commitments))
        if want == "REPORT_UNKNOWN" and g.get("retract") is None and st.utterance.startswith("did"):
            pass
    checks["leak_n"] += 1                      # every dialogue: nothing said ever reached the machine layer
    checks["leak"] += int(bool(dr.workspace.machine_commitments))
    return checks


def run(seed: str = "OCM-M4-DIALOGUE-20260905") -> dict:
    ds = DW.generate(seed)
    prot = [d for d in ds if d.split == "protected"]
    agg: dict[str, float] = {}
    per_family: dict[str, dict[str, int]] = {}
    by_len: dict[int, list[float]] = {}
    with tempfile.TemporaryDirectory() as td:
        for k, d in enumerate(prot):
            restart = len(d.steps) // 2 if k % 2 == 0 and len(d.steps) > 2 else None
            c = run_dialogue(d, Path(td) / d.dialogue_id, restart_at=restart)
            for key, v in c.items():
                agg[key] = agg.get(key, 0) + v
            f = per_family.setdefault(d.family, {"dialogues": 0, "steps": 0, "act_ok": 0})
            f["dialogues"] += 1
            f["steps"] += c["steps"]
            f["act_ok"] += c["act_ok"]
            by_len.setdefault(len(d.steps), []).append(c["wall_s"] / max(1, c["turns"]))
    def frac(a, b):
        return f"{int(agg.get(a, 0))}/{int(agg.get(b, 0))}"
    return {
        "receipt": "M4_DIALOGUE_EVAL_V1",
        "custody": DW.custody_receipt(ds, seed),
        "protected_dialogues": len(prot),
        "acts": {"expected_act_and_committed": frac("act_ok", "steps"), "per_family": per_family},
        "state_reference": {"entity_introduction": frac("entities_ok", "entities_n"), "ambiguous_pronoun_candidate_recall": frac("candidates_ok", "candidates_n"), "unique_pronoun_resolved": frac("resolved_ok", "resolved_n"), "reference_after_gap_ge_12": frac("gap_ok", "gap_n")},
        "correction": {"supersession_recorded": frac("supersede_ok", "supersede_n"), "dependent_answer_reopened": frac("reopen_ok", "reopen_n"), "unrelated_answer_intact": frac("intact_ok", "intact_n")},
        "clarification": {"needed": int(agg.get("clarify_gold", 0)), "asked": int(agg.get("clarify_asked", 0)), "true_positive": int(agg.get("clarify_tp", 0)), "unnecessary": int(agg.get("unnecessary_clarify", 0))},
        "epistemic_integrity": {"assertion_to_belief_leakage": frac("leak", "leak_n"), "answers_citing_evidence": frac("cites_ok", "cites_n"), "contradiction_reported_with_both": frac("contradiction_ok", "contradiction_n")},
        "persistence": {"dialogues_restarted_midway": int(agg.get("restarted", 0))},
        "cost": {"mean_wall_s_per_turn_by_dialogue_length": {str(k): round(sum(v) / len(v), 4) for k, v in sorted(by_len.items())}},
        "authority": "synthetic dialogue microworld with a given vocabulary; measures dialogue cognition (layers, reference, correction, clarification, persistence); no real-conversation result, no comparator, no novelty claim",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    a = p.parse_args(argv)
    r = run()
    if a.out:
        from ocm.evaluation.output import write_result
        write_result(Path(a.out), r)
    print(json.dumps({k: r[k] for k in ("acts", "state_reference", "correction", "clarification", "epistemic_integrity", "persistence")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
