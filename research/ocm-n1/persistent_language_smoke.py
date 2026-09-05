"""Run bounded supervised language reuse/revocation through fresh chat processes.

Development evidence for #43/#53/#62, not a protected or comparative result.
ADOPT ChatSession and its current seed inventory; no new runtime mechanism.
The worker sees only raw commands. Expected meanings stay in the controller.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


TARGET = "the cat the crate lifted"
KNOWN = "the cat the door lifted"
UNRELATED = "the robot lifted the gnome"


def worker(root: str) -> None:
    from ocm.chat.session import ChatSession

    session = ChatSession(Path(root))
    rows = []
    for text in json.load(sys.stdin):
        reply = session.say(text)
        rows.append({"text": text, "reply": reply, "trace": session.last_trace()})
    print(json.dumps({"pid": os.getpid(), "rows": rows,
                      "revoked": sorted(session.runtime.state.revoked)}))


def expected_digest(agent: str, patient: str) -> str:
    # Explicit evaluator oracle, not a second call to the learner/interpreter.
    from ocm.language.meaning import MEdge, MNode, MeaningGraph, canonical

    graph = MeaningGraph(
        (MNode("a", "entity", agent, (("definite", "yes"),)),
         MNode("e", "event", "lift"),
         MNode("p", "entity", patient, (("definite", "yes"),))),
        (MEdge("ROLE:agent", ("e",), ("a",)),
         MEdge("ROLE:patient", ("e",), ("p",)),
         MEdge("TENSE", ("e",), ("e",), "past")), root="e")
    # Public diagnostics currently expose the first 12 digest characters.
    return canonical(graph)[1][:12]


def run() -> dict:
    phases, checks = [], []

    def phase(root, *commands):
        completed = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--worker", str(root)],
            input=json.dumps(commands), text=True, capture_output=True, check=True,
            timeout=60)
        result = json.loads(completed.stdout)
        phases.append(result)
        return result["rows"]

    def check(name, row, verdict, *, patient=None, agent="cat", support=()):
        interpretation = row["trace"]["interpretation"]
        candidates = interpretation.get("candidates", [])
        ok = interpretation.get("verdict") == verdict
        if patient is not None:
            ok = ok and len(candidates) == 1 and candidates[0]["digest"] == expected_digest(agent, patient)
            ok = ok and set(support).issubset(candidates[0]["evidence"])
            ok = ok and row["reply"].startswith("Noted:")
        else:
            ok = ok and not candidates
        checks.append({"case": name, "passed": bool(ok), "actual": interpretation})

    def lesson(row):
        ids = row["trace"]["warrant_ids"]
        if len(ids) != 1:
            raise ValueError(f"expected one admitted lesson ID, got {ids}")
        return ids[0]

    with tempfile.TemporaryDirectory(prefix="ocm-persistent-language-") as directory:
        root = Path(directory) / "state"
        rows = phase(root, KNOWN)
        check("before_grammar_lesson", rows[0], "UNKNOWN_CONSTRUCTION")
        rows = phase(root,
            "teach: crate = parcel", "teach: crate = parcel",
            "teach: gnome = garden_statue", TARGET,
            "teach: construction the robot the door opened => robot open door", TARGET)
        first, alternate, unrelated = map(lesson, rows[:3])
        grammar = lesson(rows[4])
        checks.append({"case": "distinct_lexical_support", "passed": first != alternate})
        check("words_do_not_supply_grammar", rows[3], "UNKNOWN_CONSTRUCTION")
        check("learned_composition", rows[5], "INTERPRETED", patient="parcel", support=(grammar,))
        rows = phase(root, TARGET, KNOWN, UNRELATED, f"revoke {first}")
        check("fresh_process_reuse", rows[0], "INTERPRETED", patient="parcel", support=(grammar,))
        check("second_unseen_composition", rows[1], "INTERPRETED", patient="door", support=(grammar,))
        check("unrelated_capability_before_revocation", rows[2], "INTERPRETED", agent="robot", patient="garden_statue", support=(unrelated,))
        rows = phase(root, TARGET, f"revoke {alternate}")
        check("alternate_support_after_reload", rows[0], "INTERPRETED", patient="parcel", support=(alternate, grammar))
        rows = phase(root, TARGET, UNRELATED, f"reinstate {first}")
        check("last_lexical_support_revoked", rows[0], "UNKNOWN_LEXEME")
        check("unrelated_learned_word_retained", rows[1], "INTERPRETED", agent="robot", patient="garden_statue", support=(unrelated,))
        rows = phase(root, TARGET, f"revoke {grammar}")
        check("lexical_support_restored", rows[0], "INTERPRETED", patient="parcel", support=(first, grammar))
        rows = phase(root, TARGET, UNRELATED, f"reinstate {grammar}")
        check("grammar_revocation_survives_reload", rows[0], "UNKNOWN_CONSTRUCTION")
        check("unrelated_capability_survives_grammar_revoke", rows[1], "INTERPRETED", agent="robot", patient="garden_statue", support=(unrelated,))
        rows = phase(root, TARGET)
        check("grammar_support_restored", rows[0], "INTERPRETED", patient="parcel", support=(first, grammar))

    checks.append({"case": "fresh_worker_processes", "passed": len({p["pid"] for p in phases}) == len(phases)})
    return {
        "receipt": "N1_PERSISTENT_LANGUAGE_SMOKE_V1",
        "study_role": "DEVELOPMENT_SMOKE_ONLY", "protected_claim_authority": False,
        "bootstrap": "Current ChatSession seed lexicon, morphology, NP helper and transitive semantic template; six order hypotheses; one aligned grammar demonstration and three lexical lessons.",
        "scope": "Persisted supervised reuse and support revocation, not continued grammar acquisition after restart or packed-chart integration.",
        "comparator": "No comparative claim; persistent-parent calibrations remain separate.",
        "meaning_check": "Explicit role/tense oracle compared with the public 12-character canonical digest.",
        "checks": checks, "phases": phases,
        "passed": all(c["passed"] for c in checks),
        "terminal": "BOUNDED_PERSISTENT_CAPABILITY_DEMONSTRATED" if all(c["passed"] for c in checks) else "INTEGRATION_DEFECT",
    }


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        worker(sys.argv[2])
    else:
        receipt = run()
        print(json.dumps(receipt, indent=2, sort_keys=True))
        raise SystemExit(0 if receipt["passed"] else 1)
