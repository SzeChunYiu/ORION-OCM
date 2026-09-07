"""Development fixture data transformations; never imported by the generic native checker."""
import copy
import hashlib
import json
from pathlib import Path


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def save(path, value):
    with path.open("x") as stream:
        stream.write(raw(value))


def packet(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def save_packet(path, rows):
    with path.open("x") as stream:
        stream.writelines(raw(row) for row in rows)


def names(rows):
    result = {0: ""}
    for row in rows:
        if "in" in row:
            kind = "str" if "str" in row else "num"
            part = row[kind]
            prefix = result[part["pre"]]
            result[row["in"]] = (prefix + "." if prefix else "") + str(part["str" if kind == "str" else "i"])
    return result


def declaration(rows, name):
    table = names(rows)
    for row in rows:
        for kind in ("thm", "def", "opaque", "axiom"):
            if kind in row and table[row[kind]["name"]] == name:
                return row[kind]
    raise ValueError(name)


def family(rows, name):
    table = names(rows)
    return next(row["inductive"] for row in rows if "inductive" in row
                and any(table[item["name"]] == name for item in row["inductive"]["types"]))


def root_const(rows, name):
    rows = copy.deepcopy(rows)
    table = names(rows)
    name_id = 0
    prefix = ""
    for segment in name.split("."):
        prefix = (prefix + "." if prefix else "") + segment
        found = next((key for key, value in table.items() if value == prefix), None)
        if found is None:
            found = len(table)
            rows.append({"in": found, "str": {"pre": name_id, "str": segment}})
            table[found] = prefix
        name_id = found
    root = sum("ie" in row for row in rows)
    rows.append({"ie": root, "const": {"name": name_id, "us": []}})
    return rows, root


def file_record(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
