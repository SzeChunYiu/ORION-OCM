"""CLI: selected retained fields only, with explicit missing/invalid/uninspected states."""
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from contract_v1 import AuditError, require, sha, strict_json
from consumer_structure_v1 import inspect
from source_contract_v1 import current_contract


def selections(record):
    schema = record.get("schema")
    if schema == "StageB6DevelopmentArmV1":
        best = record.get("final_best_genotypes")
        require(best is None or type(best) is dict, "archive-best container")
        if best is None:
            yield ["final_best_genotypes"], None
        else:
            for carrier, cell in sorted(best.items()):
                require(type(cell) is dict, "archive-best cell")
                yield ["final_best_genotypes", carrier, "genotype"], cell.get("genotype")
        first = record.get("first_admissible")
        require(first is None or type(first) is dict, "first-admissible container")
        for field in ("genotype", "atrophied_genotype"):
            yield ["first_admissible", field], None if first is None else first.get(field)
    elif schema == "StageB6DevelopmentSourceV1":
        cells = record.get("cells")
        require(cells is None or type(cells) is dict, "source-cell container")
        if cells is None:
            yield ["cells"], None
        else:
            for label, cell in sorted(cells.items()):
                require(type(cell) is dict, "source cell")
                yield ["cells", label, "genotype"], cell.get("genotype")
    elif schema == "StageB6DenseWitnessV1":
        for field in ("genotype_raw", "genotype_atrophied"):
            yield [field], record.get(field)
    else:
        raise AuditError("unsupported retained schema")


def scan_record(name, raw, kinds, roles):
    record = strict_json(raw)
    require(type(record) is dict, "record must be an object")
    rows = []
    for fields, text in selections(record):
        label = name + "/" + "/".join(fields)
        if text is None:
            row = {"label": label, "status": "NOT_RETAINED"}
        else:
            require(type(text) is str, "genotype must be serialized JSON")
            row = inspect(label, text, kinds, roles)
        row["source_fields"] = fields
        rows.append(row)
    return {"source": name, "source_sha256": sha(raw), "rows": rows,
            "other_fields_and_search_population": "UNINSPECTED"}


def scan_directory(directory):
    root = Path(directory)
    if not root.is_dir() or root.is_symlink():
        return {"status": "INPUT_UNAVAILABLE", "records": []}
    paths = sorted(set(root.glob("STAGE_B6_DEV_*.json")) |
                   set(root.glob("STAGE_B6_DENSE_WITNESS_*.json")))
    if not paths:
        return {"status": "NO_MATCHING_INPUTS", "records": []}
    kinds, roles = current_contract()
    records = []
    for path in paths:
        if path.is_symlink() or not path.is_file():
            records.append({"source": path.name, "status": "INPUT_UNAVAILABLE"})
            continue
        try:
            records.append(scan_record(path.name, path.read_bytes(), kinds, roles))
        except (AuditError, ValueError, KeyError, TypeError) as error:
            records.append({"source": path.name, "status": "INVALID_OR_UNSUPPORTED",
                            "reason": str(error)})
    missing = any("status" in r or any(x["status"] != "STRUCTURE_INSPECTED"
                  for x in r["rows"]) for r in records)
    return {"status": "PARTIAL" if missing else "COMPLETE_SELECTED_FIELD_INSPECTION",
            "records": records, "causal_or_campaign_coverage": "NOT_ESTABLISHED"}


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        raise SystemExit("usage: scan_retained_v1.py RETAINED_DIRECTORY")
    result = scan_directory(args[0])
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "COMPLETE_SELECTED_FIELD_INSPECTION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
