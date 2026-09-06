"""External-only, bound G1 development grading; never imported by actors."""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import sys
from vendor import conll18_ud_eval as official
from syntax_contract import validate
import clia_checker

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ocm-n1"))
from ud_induction import load_split

GOLD_SHA = "dd514122385fd3374dd10051ddaf477c957d3da0bba48931d6f969820ece233f"
PUBLIC_SHA = "7ece4dd05bdc5c07caa88213fb5952b75f8a22e26bdc4a379bb83644cfaa48d0"
ARMS = ("native", "ocm")
METRICS = ("UAS", "LAS_base", "LAS_full", "UPOS")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def gold_words(sentence):
    mapping = {t.token_id: i for i, t in enumerate(sentence.tokens, 1)} | {0: 0}
    return [dict(id=i, form=t.form, head=mapping[t.head], deprel=t.deprel, upos=t.upos)
            for i, t in enumerate(sentence.tokens, 1)]


def conllu(words):
    return "\n".join("\t".join([str(w["id"]), w["form"], "_", w["upos"], "_", "_",
                                str(w["head"]), w["deprel"], "_", "_"]) for w in words) + "\n\n"


def syntax_score(words, gold):
    reason = validate(words, [w["form"] for w in gold])
    zero = {m: 0 for m in METRICS}
    if reason:
        return dict(correct=zero, exact_tree=False, exact_typed=False, valid=False, reason=reason)
    score = official.evaluate(official.load_conllu(io.StringIO(conllu(gold))),
                              official.load_conllu(io.StringIO(conllu(words))))
    full = sum(p["head"] == g["head"] and p["deprel"] == g["deprel"] for p, g in zip(words, gold))
    counts = dict(UAS=score["UAS"].correct, LAS_base=score["LAS"].correct,
                  LAS_full=full, UPOS=score["UPOS"].correct)
    return dict(correct=counts, exact_tree=full == len(gold),
                exact_typed=full == len(gold) and counts["UPOS"] == len(gold), valid=True,
                tree_sha256=hashlib.sha256(json.dumps(words, sort_keys=True).encode()).hexdigest())


def grade_row(item, result, arm, model_sha, gold):
    require(isinstance(result, dict), "result schema")
    require(result.get("status") in (("ADMITTED", "NOT_ADMITTED", "CANNOT_CHECK", "INPUT_REFUSED") if arm == "ocm" else ("ACCEPTED_PARENT", "NOT_ACCEPTED")), "unknown response status")
    syntax = item["request"]["kind"] == "syntax"
    claimed = result.get("status") == ("ADMITTED" if arm == "ocm" else "ACCEPTED_PARENT")
    accepted = claimed and ((isinstance(result.get("admitted_id"), str) and bool(result["admitted_id"])) if arm == "ocm" else result.get("accepted") is True)
    require(not claimed or accepted, "inconsistent acceptance record: " + item["id"])
    row = dict(id=item["id"], arm=arm, domain="syntax" if syntax else "clia", completed=True,
               accepted=accepted, scored=True, terminal="COMPLETED_REFUSAL", correct_program=False)
    if syntax:
        row.update(tokens=len(gold), correct={m: 0 for m in METRICS}, exact_tree=False, exact_typed=False)
    if not accepted:
        require(result.get("answer") is None, "unaccepted result exposes an answer")
        row["response_status"] = result.get("status")
        return row
    expected = "MODEL_SUPPORTED_SYNTAX_OBSERVATION" if syntax else "SPECIFICATION_VERIFIED_PROGRAM"
    require(result.get("claim") == expected and isinstance(result.get("answer"), dict), "claim/output mismatch")
    answer = result["answer"]
    if syntax:
        require(answer.get("status") == "PREDICTED" and answer.get("model_sha256") == model_sha, "model output binding")
        row.update(syntax_score(answer.get("words"), gold))
        row["terminal"] = "GRADED_SYNTAX" if row["valid"] else "INVALID_ACCEPTED_SYNTAX"
    else:
        checked = clia_checker.check(item["request"]["task"], answer)
        row.update(external_check=checked, correct_program=checked["status"] == "PASS",
                   scored=checked["status"] != "CANNOT_CHECK", terminal="PROGRAM_" + checked["status"])
    return row


def summarize(rows):
    out = {"assigned": len(rows), "completed": sum(r["completed"] for r in rows),
           "accepted": sum(r["accepted"] for r in rows), "terminals": dict(Counter(r["terminal"] for r in rows))}
    scored = [r for r in rows if r["scored"]]
    complete = len(scored) == len(rows)
    out["all_assigned_scored"] = complete
    if rows[0]["domain"] == "syntax":
        total = sum(r["tokens"] for r in rows); observed = sum(r["tokens"] for r in scored)
        out["tokens_assigned"] = total; out["tokens_scored"] = observed
        out["valid_output_count"] = sum(r.get("valid", False) for r in rows)
        for m in METRICS:
            n = sum(r["correct"][m] for r in scored)
            out[m] = {"correct": n, "assigned_rate": n / total if complete else None,
                      "completed_scored_rate": n / observed if observed else None}
        for m in ("exact_tree", "exact_typed"):
            n = sum(r[m] for r in scored)
            out[m] = {"correct": n, "assigned_rate": n / len(rows) if complete else None,
                      "completed_scored_rate": n / len(scored) if scored else None}
    else:
        n = sum(r["correct_program"] for r in scored)
        out["verified_programs"] = {"correct": n, "assigned_rate": n / len(rows) if complete else None}
    return out


def resources(chunks, arm):
    selected = [c for c in chunks if c["arm"] == arm]
    workers = [c["worker"] for c in selected if "worker" in c]
    return {"observed_outer_wall_s": sum(c["wall_s"] for c in selected),
            "observed_reaped_cpu_s": sum(c["reaped_process_tree_cpu_s"] for c in selected),
            "complete_cpu_custody": bool(selected) and all(c.get("complete_cpu_custody") is True for c in selected),
            "last_reported_state_bytes": workers[-1]["durable_state_bytes"] if workers else None,
            "state_report_is_final": bool(selected) and len(selected) == 5 and selected[-1].get("source_stable") is True}


def grade(plan_dir, run_dir, gold_path):
    require(sha(gold_path) == GOLD_SHA, "gold DEV custody mismatch; gold not loaded")
    plan = read(plan_dir / "plan.json"); items = read(plan_dir / "public-items.json")
    require(sha(plan_dir / "public-items.json") == plan["public_items_sha256"] == PUBLIC_SHA, "public input binding")
    ids = [i["id"] for i in items]
    require(len(ids) == len(set(ids)) == 105, "assigned item inventory")
    receipt = read(run_dir / "receipt.json"); initial = read(run_dir / "run-binding.json")
    require(receipt.get("status") == "EXECUTED_NOT_GRADED" or receipt.get("status", "").startswith("CANNOT_CHECK"), "run not sealed")
    require(all(receipt.get(k) == v for k, v in initial.items() if k != "chunks"), "initial run binding changed")
    require(receipt["plan"] == plan and receipt["plan_sha256"] == sha(plan_dir / "plan.json"), "plan receipt binding")
    require(receipt["assigned_ids_by_arm"] == {a: ids for a in ARMS}, "assigned arm inventory")
    require(receipt["model_sha256"] == receipt["training_manifest"]["model_sha256"], "training/model identity")
    dependencies = [*HERE.glob("clia_*.py"), HERE / "syntax_contract.py", HERE / "vendor/conll18_ud_eval.py"]
    require(all(receipt["source_files"].get(str(p.relative_to(HERE.parents[1]))) == sha(p) for p in dependencies), "checker source changed")
    dev = load_split(gold_path, "dev"); gold = {}
    for item in items:
        if item["request"]["kind"] == "syntax":
            require(item["id"].startswith("all_tokens:"), "wrong syntax input contract")
            gold[item["id"]] = gold_words(dev[int(item["id"].split(":")[1])])
            require([w["form"] for w in gold[item["id"]]] == item["request"]["tokens"], "forms/gold identity mismatch")
    require(len(gold) == 100, "syntax count mismatch")
    rows = {(a, i["id"]): dict(id=i["id"], arm=a, domain="syntax" if i["id"] in gold else "clia",
            completed=False, accepted=False, scored=False, terminal="CANNOT_CHECK_MISSING_EXECUTION",
            tokens=len(gold.get(i["id"], []))) for a in ARMS for i in items}
    seen = set()
    for chunk in receipt["chunks"]:
        arm, index = chunk["arm"], chunk["chunk"]; key = (arm, index)
        require(arm in ARMS and type(index) is int and 0 <= index < 5 and key not in seen, "chunk inventory")
        seen.add(key); assigned = items[index * 21:(index + 1) * 21]
        prefix = run_dir / f"{index:02d}-{arm}"; config = read(prefix.with_suffix(".input.json"))
        require(config["items"] == assigned and config["arm"] == arm and config["chunk"] == index, "chunk input binding")
        require(config["model_sha256"] == receipt["model_sha256"] and config["training_manifest"] == receipt["training_manifest"], "chunk model binding")
        worker = chunk.get("worker", {}); path = prefix.with_suffix(".rows.jsonl")
        usable = chunk.get("exit_code") == 0 and chunk.get("source_stable") is True and not chunk.get("outer_timeout")
        if not usable:
            for item in assigned:
                rows[(arm, item["id"])]["terminal"] = "CANNOT_CHECK_CHUNK_EXECUTION"
            continue
        require(worker.get("source_files") == receipt["source_files"] and worker.get("rows_sha256") == sha(path), "row/source SHA binding")
        actual = [json.loads(line) for line in path.read_text().splitlines()]
        if len(actual) != 21 or chunk["rows_written"] != 21 or worker.get("rows") != 21:
            for item in assigned:
                rows[(arm, item["id"])]["terminal"] = "CANNOT_CHECK_ROW_INVENTORY"
            continue
        require([r["id"] for r in actual] == [i["id"] for i in assigned] and all(r["arm"] == arm for r in actual), "row identity/order mismatch")
        for item, row in zip(assigned, actual):
            if arm == "ocm" and row["result"].get("admitted_id"):
                require(row["result"].get("source_identity") == receipt["source_identity"], "OCM row source binding")
            rows[(arm, item["id"])] = grade_row(item, row["result"], arm, receipt["model_sha256"], gold.get(item["id"]))
    values = list(rows.values())
    paired = [(rows[("native", i)], rows[("ocm", i)]) for i in gold]
    comparable = [(a, b) for a, b in paired if a.get("valid") and b.get("valid")]
    return {"status": "GRADED_DEVELOPMENT" if all(r["completed"] and r["scored"] for r in values) else "CANNOT_CHECK_COMPLETE_COMPARISON",
            "scope": "Balanced genre/length development panel; supplied tokens including punctuation. No population EWT, NI, global parity or efficiency claim. Shared-host timings descriptive.",
            "gold_sha256": GOLD_SHA, "public_items_sha256": PUBLIC_SHA, "receipt_sha256": sha(run_dir / "receipt.json"),
            "grader_sha256": sha(Path(__file__)), "gold_loader_sha256": sha(HERE.parent / "ocm-n1/ud_induction.py"),
            "summaries": {a: {d: summarize([r for r in values if r["arm"] == a and r["domain"] == d]) for d in ("syntax", "clia")} for a in ARMS},
            "syntax_agreement": {"assigned": 100, "both_valid": len(comparable), "equal_trees": sum(a["tree_sha256"] == b["tree_sha256"] for a, b in comparable)},
            "resources": {a: resources(receipt["chunks"], a) for a in ARMS}, "external_rechecks": "Grader work is additional evaluation cost, excluded from actor process totals.",
            "rows": values}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("plan", "run", "gold", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(); require(not args.out.exists(), "refuse to overwrite a grading receipt")
    try:
        result = grade(args.plan, args.run, args.gold)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        result = {"status": "CANNOT_CHECK_BINDING_OR_GRADING", "reason": f"{type(exc).__name__}: {exc}"}
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, sort_keys=True))
    raise SystemExit(0 if result["status"] == "GRADED_DEVELOPMENT" else 2)
