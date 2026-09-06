"""Freeze the existing public development panel/order without reading outcomes."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from clia_tasks import load_task

SELECTION_SHA = "880d696abb2ac2397658beed9bff3f9829e785dd7fe0c609c91593d682f16c47"
CLIA_IDS = ("jmbl_fg_max3", "jmbl_fg_max10", "jmbl_fg_array_search_4",
            "jmbl_fg_array_search_10", "jmbl_fg_mpg_guard2")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(selection, requests, output):
    if output.exists():
        raise ValueError("refuse to overwrite a frozen stream")
    assert sha(selection) == SELECTION_SHA
    manifest = json.loads(selection.read_text())
    raw = [json.loads(line) for line in requests.read_text().splitlines()]
    assert all(set(row) == {"id", "tokens"} for row in raw)
    by_id = {row["id"]: row for row in raw}
    assert len(by_id) == len(raw)
    ids = [f"all_tokens:{i:04d}" for i in manifest["genre_length100"]]
    assert len(set(ids)) == 100 and all(i in by_id for i in ids)
    ids.sort(key=lambda i: hashlib.sha256(("G1-STREAM-V1|" + i).encode()).hexdigest())
    items = []
    for index, task_id in enumerate(ids, 1):
        row = by_id[task_id]
        items.append({"id": task_id, "request": {"kind": "syntax", "tokens": row["tokens"]}})
        if index % 20 == 0:
            name = CLIA_IDS[index // 20 - 1]
            items.append({"id": "clia:" + name, "request": {"kind": "clia", "task": load_task(name)}})
    assert len(items) == 105 and len({i["id"] for i in items}) == 105
    output.mkdir(parents=True)
    public = output / "public-items.json"
    public.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    plan = {"classification": "PUBLIC_DEVELOPMENT_NOT_PROTECTED", "registered_utc": datetime.now(timezone.utc).isoformat(),
            "public_items_sha256": sha(public), "selection_sha256": sha(selection),
            "forms_only_source_sha256": sha(requests), "freeze_source_sha256": sha(Path(__file__)),
            "syntax_count": 100, "clia_count": 5, "order": "SHA256(G1-STREAM-V1|id), CLIA after each20 syntax",
            "restart_after_every_items": 21, "chunks": 5, "outer_seconds_per_chunk": 600,
            "native_bounds": {"synthesis_timeout_ms": 5000, "synthesis_outer_s": 15,
                              "check_timeout_ms": 5000, "check_outer_s": 10},
            "arm_order": "even chunks native then OCM; odd chunks OCM then native",
            "retries": "one default proposal per item in native/OCM; hosted allowances separately frozen before calls",
            "metrics": "per-domain external gold scoring and native/shared agreement; no pooled quality or efficiency claim",
            "cost_scope": "all observed process work, model copies/reloads, training/failed attempts separately charged",
            "required_model": "completed checkpointed TRAIN-only UDPipe repeat; identity bound before inference"}
    (output / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(freeze(args.selection, args.requests, args.out), sort_keys=True))
