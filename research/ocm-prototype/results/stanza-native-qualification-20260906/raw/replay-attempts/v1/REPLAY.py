"""Regrade retained predictions with exact archived source; never run a donor."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def replay(repo, packet, output, gold, train):
    if output.exists():
        raise ValueError("fresh replay directory required")
    raw = packet/"raw"
    run = raw/"native-prediction-v1"
    launch = json.loads((run/"launch-manifest.json").read_text())
    custody = json.loads((raw/"source-custody.json").read_text())
    # The frozen grader also verifies this exact actor-stage pathname.
    stage = Path(launch["actor_stage_path"])
    for name, expected in launch["actor_stage_files"].items():
        if digest(stage/name) != expected:
            raise ValueError("restore raw/actor-inputs at the recorded actor_stage_path first")
    output.mkdir(parents=True)
    tree = output/"source-tree"; tree.mkdir()
    files = dict(launch["source_files"])
    files.update(launch["external_baseline_artifacts"])
    files["research/ocm-prototype/results/g1-matched-plan-v1/public-items.json"] = launch["public_sha256"]
    for name, expected in files.items():
        archived = raw/"executed-source"/Path(name).name
        if name in launch["source_files"] and Path(name).name in custody["archived_new_source_files"]:
            data = archived.read_bytes()
        else:
            data = subprocess.check_output(["/usr/bin/git", "show", custody["base_commit"]+":"+name], cwd=repo)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("frozen source/artifact drift: "+name)
        target=tree/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    rerun=output/"run";rerun.mkdir()
    for path in run.iterdir():
        if path.is_file() and path.name != "grade.json":
            shutil.copyfile(path,rerun/path.name)
    argv=[sys.executable,str(tree/"research/ocm-prototype/stanza_qualification_grade.py"),
          "--run",str(rerun),"--gold",str(gold),"--train",str(train)]
    env=dict(os.environ,PYTHONPATH=str(tree/"src"))
    with (output/"regrade.log").open("x") as log:
        result=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        raise ValueError("frozen-source grading refused; retain regrade.log")
    original=json.loads((run/"grade.json").read_text())
    reproduced=json.loads((rerun/"grade.json").read_text())
    cost_fields=("external_grading_wall_s","external_grading_cpu_s","grader_peak_rss_kib")
    equivalent=all(original[k]==reproduced[k] for k in original if k not in cost_fields)
    receipt={"status":"FROZEN_GRADE_REPRODUCED" if equivalent else "GRADING_MISMATCH",
             "original_grade_sha256":digest(run/"grade.json"),"replayed_grade_sha256":digest(rerun/"grade.json"),
             "semantic_fields_identical":equivalent,"only_uncompared_fields":list(cost_fields),
             "base_commit":custody["base_commit"],"source_files_verified":len(launch["source_files"]),
             "donor_inference":"NOT_RUN","argv":argv}
    (output/"replay-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt))
    return 0 if equivalent else 2

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for name in ("repo","out","gold","train"):
        parser.add_argument("--"+name,type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(replay(args.repo,Path(__file__).resolve().parent,args.out,args.gold,args.train))
