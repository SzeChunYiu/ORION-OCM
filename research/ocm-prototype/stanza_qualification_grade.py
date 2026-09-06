"""External-only Stanza grading: unchanged selected-tree scorer, fixed public panel."""
from pathlib import Path
import argparse
import json
import resource
import time
from collections import Counter
import grade_g1_matched as G
from stanza_donor import PUBLIC_SHA, require_hash, sha, syntax_items
from stanza_qualification_capture import HERE, REPO, BASE, PUBLIC, source_files, write_new

def read_rows(version):
    rows={}
    for i in range(5):
        for line in (BASE/version/f"{i:02d}-native.rows.jsonl").read_text().splitlines():
            row=json.loads(line)
            if row["id"].startswith("all_tokens:"):
                if row["id"] in rows: raise ValueError("duplicate baseline ID")
                rows[row["id"]]=row["result"]["answer"]["words"]
    return rows

def summarize(rows):
    return G.summarize(rows) if rows else {"assigned":0}


def checked_predictions(path, ids):
    predictions = {}
    if path.exists():
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if (not isinstance(row, dict) or row.get("id") not in ids
                    or row["id"] in predictions or row.get("completed") is not True):
                raise ValueError("prediction identity/completion binding")
            if row.get("status") == "PREDICTED":
                if not isinstance(row.get("words"), list):
                    raise ValueError("predicted row missing words")
            elif row.get("status") in ("INPUT_CONTRACT_MISMATCH", "CANNOT_CHECK"):
                if row.get("words") is not None or not isinstance(row.get("reason"), str) or not row["reason"]:
                    raise ValueError("refusal row exposes words or lacks reason")
            else:
                raise ValueError("unknown prediction status")
            predictions[row["id"]] = row
    if list(predictions) != ids[:len(predictions)]:
        raise ValueError("prediction order changed")
    return predictions


def decision(sealed, completed, valid, nondecrease, improvement):
    if sealed.get("outer_timeout"):
        return "EXECUTION_DEADLINE_EXCEEDED"
    if sealed.get("status") != "ACTOR_SEALED" or sealed.get("exit_code") != 0 or completed != 100:
        return "CANNOT_CHECK_EXECUTION_OR_BINDING"
    if valid != 100:
        return "INPUT_CONTRACT_MISMATCH"
    return "DONOR_QUALITY_PROGRESSION_ONLY" if nondecrease and improvement else "NO_DOMINANT_DEVELOPMENT_GAIN"

def grade(run, gold, train):
    wall=time.perf_counter(); cpu=time.process_time()
    sealed=json.loads((run/"sealed-receipt.json").read_text())
    launch=json.loads((run/"launch-manifest.json").read_text())
    require_hash(run/"launch-manifest.json",sealed["launch_sha256"])
    if not sealed["source_and_model_stable"]:
        raise ValueError("unstable actor source/model binding")
    for name,digest in sealed["artifacts"].items(): require_hash(run/name,digest)
    for name,digest in launch["actor_stage_files"].items(): require_hash(Path(launch["actor_stage_path"])/name,digest)
    if launch["source_files"] != {str(p.relative_to(REPO)):sha(p) for p in source_files()}:
        raise ValueError("external source closure changed")
    for name,digest in launch["external_baseline_artifacts"].items(): require_hash(REPO/name,digest)
    require_hash(PUBLIC,PUBLIC_SHA)
    require_hash(gold,launch["external_gold_sha256"]); require_hash(train,launch["external_train_sha256"])
    items=syntax_items(json.loads(PUBLIC.read_text()))
    if [i["id"] for i in items] != launch["assigned_ids"]:
        raise ValueError("assigned input IDs changed")
    # Gold and TRAIN are first opened as annotated data AFTER sealed actor verification.
    dev=G.load_split(gold,"dev"); training=G.load_split(train,"train")
    train_surfaces={tuple(t.form for t in sentence.tokens) for sentence in training}
    metadata=json.loads((HERE/"results/g1-20260906/language-evaluation-manifest.json").read_text())
    meta={r["dev_index"]:r for r in metadata["rows"]}
    baseline=read_rows("revised"); original=read_rows("original")
    ids=[i["id"] for i in items]
    if set(baseline)!=set(ids) or original!=baseline:
        raise ValueError("original/revised baseline selected trees differ")
    path=run/"predictions.jsonl"
    predictions=checked_predictions(path, ids)
    rows=[]; baseline_rows=[]; first_sequences=set(); unique=[]; no_detected=[]
    for item in items:
        iid=item["id"]; index=int(iid.split(":")[1]); forms=item["request"]["tokens"]
        gold_words=G.gold_words(dev[index])
        if [w["form"] for w in gold_words]!=forms: raise ValueError("word/gold binding")
        prediction=predictions.get(iid); words=prediction.get("words") if prediction else None
        score=G.syntax_score(words,gold_words)
        row={"id":iid,"domain":"syntax","completed":prediction is not None,
             "scored":prediction is not None and prediction["status"]!="CANNOT_CHECK","accepted":score["valid"],"tokens":len(forms),
             "terminal":"GRADED_SYNTAX" if score["valid"] else "CANNOT_CHECK_DONOR" if prediction and prediction["status"]=="CANNOT_CHECK" else "INVALID_OUTPUT" if prediction else "CANNOT_CHECK_MISSING_EXECUTION",
             **score,"genre":meta[index]["genre"],"band":meta[index]["band"],
             "normalized_train_surface_duplicate":meta[index]["normalized_train_surface_duplicate"],
             "exact_train_surface_duplicate":tuple(forms) in train_surfaces}
        b={**row,**G.syntax_score(baseline[iid],gold_words),"completed":True,"scored":True,"accepted":True,"terminal":"GRADED_SYNTAX"}
        rows.append(row);baseline_rows.append(b)
        row["delta"]={m:row["correct"][m]-b["correct"][m] for m in G.METRICS}
        row["delta"].update({m:int(row[m])-int(b[m]) for m in ("exact_tree","exact_typed")})
        if tuple(forms) not in first_sequences:
            unique.append(row);first_sequences.add(tuple(forms))
        if not row["normalized_train_surface_duplicate"]: no_detected.append(row)
    summary=summarize(rows); reference=summarize(baseline_rows)
    recorded=json.loads((BASE/"revised/grade.json").read_text())["summaries"]["native"]["syntax"]
    for m in (*G.METRICS,"exact_tree","exact_typed"):
        if reference[m]["correct"]!=recorded[m]["correct"]:
            raise ValueError("baseline scorer cross-check")
    endpoints=("LAS_base","LAS_full","exact_tree","exact_typed")
    nondecrease=all(summary[m]["correct"]>=reference[m]["correct"] for m in endpoints)
    improvement=any(summary[m]["correct"]>reference[m]["correct"] for m in ("LAS_base","exact_tree"))
    terminal=decision(sealed, sum(r["completed"] and r["scored"] for r in rows), summary["valid_output_count"], nondecrease, improvement)
    out={"status":"GRADED_PUBLIC_DEVELOPMENT","terminal":terminal,"stanza":summary,"udpipe":reference,
         "selected_endpoints":list(endpoints),"nondecrease":nondecrease,"strict_base_las_or_exact_tree":improvement,
         "original_revised_native_selected_trees_equal":True,"all_baseline_scores_reproduced":True,
         "prediction_sha256":sha(path) if path.exists() else None,"sealed_receipt_sha256":sha(run/"sealed-receipt.json"),
         "launch_sha256":sha(run/"launch-manifest.json"),"gold_sha256":sha(gold),"train_sha256":sha(train),
         "unique_input_first_in_fixed_order_diagnostic":summarize(unique),
         "no_detected_normalized_overlap_with_custody_ewt_train_diagnostic":summarize(no_detected),
         "normalized_overlap_rows":sum(r["normalized_train_surface_duplicate"] for r in rows),
         "exact_overlap_rows":sum(r["exact_train_surface_duplicate"] for r in rows),
         "genre_length_diagnostic":{g+"|"+b:summarize([r for r in rows if r["genre"]==g and r["band"]==b])
             for g,b in sorted({(r["genre"],r["band"]) for r in rows})},
         "rows":rows,"external_grading_wall_s":time.perf_counter()-wall,"external_grading_cpu_s":time.process_time()-cpu,
         "grader_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
         "scope":"Four-endpoint finite-panel donor selection only. Imported training partly unknown; no protected, useful-language, OCM, parity or efficiency claim."}
    write_new(run/"grade.json",out)
    print(json.dumps({k:out[k] for k in ("status","terminal","stanza","udpipe","normalized_overlap_rows","exact_overlap_rows")}))
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("run","gold","train"):p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    try: grade(a.run,a.gold,a.train)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        result={"status":"CANNOT_CHECK_EXECUTION_OR_BINDING","terminal":"CANNOT_CHECK_EXECUTION_OR_BINDING",
                "reason":type(exc).__name__+": "+str(exc)}
        write_new(a.run/"grade.json",result)
        print(json.dumps(result));raise SystemExit(2)
