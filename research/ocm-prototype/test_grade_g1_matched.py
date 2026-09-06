"""External scorer controls; real DEV gold is never sent to an actor."""
from copy import deepcopy
import json
import os
from pathlib import Path
import pytest
import grade_g1_matched as G

HERE = Path(__file__).resolve().parent
PLAN = HERE / "results/g1-matched-plan-v1"


def write(path, data):
    path.write_text(json.dumps(data, sort_keys=True) + "\n")


@pytest.fixture(scope="module")
def dev():
    path = os.environ.get("OCM_G1_DEV_PATH")
    if not path:
        pytest.skip("set OCM_G1_DEV_PATH for actual custody-bound DEV controls")
    path = Path(path)
    assert G.sha(path) == G.GOLD_SHA
    return path, G.load_split(path, "dev")


def fixture_run(tmp_path, dev):
    """Explicit gold-output test fixture, not a donor or capability receipt."""
    gold_path, sentences = dev
    items = G.read(PLAN / "public-items.json"); plan = G.read(PLAN / "plan.json")
    proposals = {r["task"]["task_id"]: r["proposal"] for r in
                 G.read(HERE / "results/g1-20260906/clia-direct-development.json")["rows"]}
    deps = [*HERE.glob("clia_*.py"), HERE / "syntax_contract.py", HERE / "vendor/conll18_ud_eval.py"]
    sources = {str(p.relative_to(HERE.parents[1])): G.sha(p) for p in deps}
    model_sha = "d" * 64; training = {"model_sha256": model_sha, "role": "ORACLE_FIXTURE_TEST_ONLY"}
    record = dict(role="ORACLE_FIXTURE_TEST_ONLY", plan=plan, plan_sha256=G.sha(PLAN / "plan.json"),
                  assigned_ids_by_arm={a: [i["id"] for i in items] for a in G.ARMS}, chunks=[],
                  model_sha256=model_sha, training_manifest=training, source_files=sources, source_identity="fixture-only")
    write(tmp_path / "run-binding.json", record)
    for chunk in range(5):
        for arm in G.ARMS:
            prefix = tmp_path / f"{chunk:02d}-{arm}"; subset = items[chunk * 21:(chunk + 1) * 21]
            write(prefix.with_suffix(".input.json"), dict(arm=arm, chunk=chunk, items=subset,
                  model_sha256=model_sha, training_manifest=training))
            rows = []
            for item in subset:
                if item["request"]["kind"] == "syntax":
                    gold = G.gold_words(sentences[int(item["id"].split(":")[1])])
                    answer = dict(status="PREDICTED", words=gold, model_sha256=model_sha)
                    claim = "MODEL_SUPPORTED_SYNTAX_OBSERVATION"
                else:
                    answer = proposals[item["request"]["task"]["task_id"]]
                    claim = "SPECIFICATION_VERIFIED_PROGRAM"
                result = dict(answer=answer, claim=claim, source_identity="fixture-only")
                result.update(dict(status="ADMITTED", admitted_id="fixture:" + item["id"]) if arm == "ocm"
                              else dict(status="ACCEPTED_PARENT", accepted=True))
                rows.append(dict(id=item["id"], arm=arm, result=result))
            path = prefix.with_suffix(".rows.jsonl")
            path.write_text("".join(json.dumps(r) + "\n" for r in rows))
            record["chunks"].append(dict(arm=arm, chunk=chunk, exit_code=0, outer_timeout=False, source_stable=True,
                rows_written=21, wall_s=1, reaped_process_tree_cpu_s=0.5, complete_cpu_custody=True,
                worker=dict(rows=21, rows_sha256=G.sha(path), source_files=sources, durable_state_bytes=100)))
    record["status"] = "EXECUTED_NOT_GRADED"; write(tmp_path / "receipt.json", record)
    return gold_path


def test_actual_gold_perfect_no_alarm_and_real_programs(tmp_path, dev):
    gold = fixture_run(tmp_path, dev); report = G.grade(PLAN, tmp_path, gold)
    assert report["status"] == "GRADED_DEVELOPMENT" and len(report["rows"]) == 210
    assert report["syntax_agreement"]["equal_trees"] == 100
    for arm in G.ARMS:
        s = report["summaries"][arm]
        assert s["syntax"]["tokens_assigned"] == 1584
        assert all(s["syntax"][m]["assigned_rate"] == 1 for m in G.METRICS)
        assert s["syntax"]["exact_typed"]["correct"] == 100
        assert s["clia"]["verified_programs"]["correct"] == 5


def test_wrong_label_is_valid_but_not_gold_correct(dev):
    _, sentences = dev
    item = next(i for i in G.read(PLAN / "public-items.json") if i["request"]["kind"] == "syntax" and len(i["request"]["tokens"]) > 3)
    gold = G.gold_words(sentences[int(item["id"].split(":")[1])]); words = deepcopy(gold)
    word = next(w for w in words if w["head"] != 0); word["deprel"] = "dep" if word["deprel"] != "dep" else "obj"
    score = G.syntax_score(words, gold)
    assert score["valid"] and score["correct"]["UAS"] == len(gold)
    assert score["correct"]["LAS_base"] == len(gold) - 1 and not score["exact_typed"]


def test_crashed_partial_chunk_preserves_assigned_unknowns(tmp_path, dev):
    gold = fixture_run(tmp_path, dev); record = G.read(tmp_path / "receipt.json")
    first = record["chunks"][0]; first.update(exit_code=-9, source_stable=False, complete_cpu_custody=False)
    first.pop("worker"); record["status"] = "CANNOT_CHECK_INCOMPLETE_EXECUTION"; write(tmp_path / "receipt.json", record)
    report = G.grade(PLAN, tmp_path, gold)
    assert report["status"] == "CANNOT_CHECK_COMPLETE_COMPARISON" and len(report["rows"]) == 210
    summary = report["summaries"]["native"]["syntax"]
    assert summary["assigned"] == 100 and summary["completed"] == 80 and summary["UAS"]["assigned_rate"] is None
    assert summary["terminals"]["CANNOT_CHECK_CHUNK_EXECUTION"] == 20


def test_changed_rows_fail_sha_binding(tmp_path, dev):
    gold = fixture_run(tmp_path, dev); path = tmp_path / "00-native.rows.jsonl"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="SHA binding"):
        G.grade(PLAN, tmp_path, gold)


def test_false_admission_and_completed_refusal_remain_distinct():
    gold = [dict(id=1, form="Runs", head=0, deprel="root", upos="VERB")]
    item = dict(id="all_tokens:fixture", request=dict(kind="syntax", tokens=["Runs"]))
    with pytest.raises(ValueError, match="inconsistent acceptance"):
        G.grade_row(item, dict(status="ADMITTED", admitted_id=None), "ocm", "d" * 64, gold)
    row = G.grade_row(item, dict(status="CANNOT_CHECK", answer=None), "ocm", "d" * 64, gold)
    assert row["completed"] and row["scored"] and row["terminal"] == "COMPLETED_REFUSAL"
    assert row["correct"]["UAS"] == 0


def test_gold_hash_checked_before_loading(tmp_path, monkeypatch):
    wrong = tmp_path / "wrong-dev.conllu"; wrong.write_text("unbound data")
    monkeypatch.setattr(G, "load_split", lambda *a: pytest.fail("gold was loaded before custody check"))
    with pytest.raises(ValueError, match="gold DEV custody"):
        G.grade(PLAN, tmp_path, wrong)


def test_bound_missing_row_is_incomplete_not_a_smaller_denominator(tmp_path, dev):
    gold = fixture_run(tmp_path, dev); path = tmp_path / "00-native.rows.jsonl"
    path.write_text("\n".join(path.read_text().splitlines()[:-1]) + "\n")
    record = G.read(tmp_path / "receipt.json"); chunk = record["chunks"][0]
    chunk["worker"].update(rows=20, rows_sha256=G.sha(path)); chunk["rows_written"] = 20
    record["status"] = "CANNOT_CHECK_INCOMPLETE_EXECUTION"; write(tmp_path / "receipt.json", record)
    report = G.grade(PLAN, tmp_path, gold)
    assert report["status"] == "CANNOT_CHECK_COMPLETE_COMPARISON"
    assert len(report["rows"]) == 210 and report["summaries"]["native"]["syntax"]["assigned"] == 100
    assert report["summaries"]["native"]["clia"]["verified_programs"]["assigned_rate"] is None


def test_program_rechecked_by_behavior_not_output_string():
    original = G.read(HERE / "results/g1-20260906/clia-direct-development.json")["rows"][0]
    item = next(i for i in G.read(PLAN / "public-items.json") if i["id"] == "clia:" + original["task"]["task_id"])
    answer = deepcopy(original["proposal"]); answer["candidate"] = "\n  " + answer["candidate"] + "  \n"
    result = dict(status="ACCEPTED_PARENT", accepted=True, claim="SPECIFICATION_VERIFIED_PROGRAM", answer=answer)
    row = G.grade_row(item, result, "native", "d" * 64, None)
    assert row["correct_program"] and row["external_check"]["solver_result"] == "unsat"
